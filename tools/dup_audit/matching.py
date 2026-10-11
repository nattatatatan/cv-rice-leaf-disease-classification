"""Pair matching: Lowe-ratio kNN matches verified by RANSAC (homography and fundamental matrix).

``match_pair`` returns ``(n_good, h_inliers, f_inliers, h_raw)``. A fit counts only when it is not
degenerate: the homography must be well conditioned and the inlier cloud must span at least
``MIN_EXTENT`` px (principal axis, 5-95 percentile, long side 800) in BOTH images. Without these
guards matches on a single point or a wall smudge give "perfect" fits.
"""

from __future__ import annotations

import cv2
import numpy as np

MIN_EXTENT = 40.0
RATIO = 0.75  # Lowe ratio test
H_RANSAC_PX = 6.0
F_RANSAC_PX = 1.5


def extent(points: np.ndarray) -> float:
    """Spread of a point cloud along its principal axis (5th to 95th percentile), in px."""
    centred = points - points.mean(0)
    _, _, vt = np.linalg.svd(centred, full_matrices=False)
    z = centred @ vt[0]
    return float(np.percentile(z, 95) - np.percentile(z, 5))


def homography_ok(H: np.ndarray | None) -> bool:
    """Reject collapsing, exploding or strongly projective homographies."""
    if H is None or not np.all(np.isfinite(H)):
        return False
    H = H / H[2, 2]
    sv = np.linalg.svd(H[:2, :2], compute_uv=False)
    return bool(sv[1] > 0.33 and sv[0] < 3.0 and abs(H[2, 0]) < 2e-3 and abs(H[2, 1]) < 2e-3)


def match_pair(a, b, bf: cv2.BFMatcher | None = None) -> tuple[int, int, int, int]:
    """a, b = (keypoints, descriptors). Returns (n_good, H inliers, F inliers, unvalidated H inliers)."""
    pa, da = a
    pb, db = b
    if len(da) < 8 or len(db) < 8:
        return 0, 0, 0, 0
    bf = bf or cv2.BFMatcher(cv2.NORM_L2)
    good = [m[0] for m in bf.knnMatch(da, db, k=2) if len(m) == 2 and m[0].distance < RATIO * m[1].distance]
    n_good = len(good)
    if n_good < 8:
        return n_good, 0, 0, 0
    src = pa[[g.queryIdx for g in good]]
    dst = pb[[g.trainIdx for g in good]]
    h_inliers = f_inliers = h_raw = 0
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, H_RANSAC_PX, maxIters=2000, confidence=0.99)
    if mask is not None:
        keep = mask.ravel() != 0
        h_raw = int(keep.sum())
        if h_raw >= 4 and homography_ok(H) and extent(src[keep]) >= MIN_EXTENT and extent(dst[keep]) >= MIN_EXTENT:
            h_inliers = h_raw
    if n_good >= 12:
        _, mask = cv2.findFundamentalMat(src, dst, cv2.FM_RANSAC, F_RANSAC_PX, 0.99, 2000)
        if mask is not None and mask.shape[0] == n_good:
            keep = mask.ravel() != 0
            if keep.sum() >= 8 and extent(src[keep]) >= MIN_EXTENT and extent(dst[keep]) >= MIN_EXTENT:
                f_inliers = int(keep.sum())
    return n_good, h_inliers, f_inliers, h_raw
