"""Step 1: RootSIFT features of every cached image.

Run (about 2 minutes on 8 cores)::

    python tools/dup_audit/features.py [--workers 8]

Writes ``Dhan-Shomadhan/_work/dup_audit/feats.pkl``: {filename: (keypoints (K, 2) float32, descriptors (K, 128) float32)}.

Design notes (details and evidence in results/summary.md):

* Images are resized to a long side of 800 px; up to 1500 keypoints; ``contrastThreshold`` is 0.005
  because white-background leaves are texture-poor (the 0.04 default gave a median of 25 keypoints).
* RootSIFT: L1-normalise, then square root.
* White-background images: keypoints are restricted to a leaf mask. Without it the wall (sensor noise,
  smudges at the same position in every shot) produced hundreds of false "identical" pairs.
"""

from __future__ import annotations

import argparse
import pickle
import time
from multiprocessing import Pool

import cv2
import numpy as np

from common import AUDIT_DIR, cache_path, load_records

LONG_SIDE = 800
MAX_KEYPOINTS = 1500
CONTRAST_THRESHOLD = 0.005


def leaf_mask(bgr: np.ndarray) -> np.ndarray:
    """uint8 mask, 255 on the leaf plus a margin, for a white-background image at long side 800.

    Saturation (Otsu) separates the coloured leaf from the grey wall; the mask is closed with a
    large ellipse and filled so that pale lesions inside the leaf stay in, then dilated by 10 px."""
    hsv = cv2.cvtColor(cv2.GaussianBlur(bgr, (0, 0), 2), cv2.COLOR_BGR2HSV)
    _, mask = cv2.threshold(hsv[..., 1], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = np.zeros_like(mask)
    big = [c for c in contours if cv2.contourArea(c) > 0.003 * mask.size]
    cv2.drawContours(out, big if big else contours, -1, 255, -1)
    return cv2.dilate(out, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))


def extract(bgr: np.ndarray, domain: str) -> tuple[np.ndarray, np.ndarray]:
    """(keypoint coordinates, RootSIFT descriptors) of one BGR image."""
    scale = LONG_SIDE / max(bgr.shape[:2])
    if scale < 1:
        bgr = cv2.resize(bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    mask = leaf_mask(bgr) if domain == "white" else None
    sift = cv2.SIFT_create(nfeatures=MAX_KEYPOINTS, contrastThreshold=CONTRAST_THRESHOLD)
    keypoints, desc = sift.detectAndCompute(gray, mask)
    if desc is None:
        return np.zeros((0, 2), np.float32), np.zeros((0, 128), np.float32)
    desc = desc / (np.abs(desc).sum(1, keepdims=True) + 1e-7)
    return np.array([k.pt for k in keypoints], np.float32), np.sqrt(desc).astype(np.float32)


def _work(item: tuple[str, str]):
    filename, domain = item
    return filename, extract(cv2.imread(str(cache_path(filename))), domain)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    cv2.setNumThreads(1)
    records = load_records()
    start = time.time()
    with Pool(args.workers) as pool:
        feats = dict(pool.map(_work, [(r["filename"], r["domain"]) for r in records], chunksize=8))
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_DIR / "feats.pkl", "wb") as f:
        pickle.dump(feats, f)
    for domain in ("white", "field"):
        counts = np.array([len(feats[r["filename"]][0]) for r in records if r["domain"] == domain])
        print(domain, "keypoints per image, percentiles 0/5/25/50/75/95/100:", np.percentile(counts, [0, 5, 25, 50, 75, 95, 100]))
    print(f"done in {time.time() - start:.0f} s")


if __name__ == "__main__":
    main()
