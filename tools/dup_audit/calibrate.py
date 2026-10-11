"""Calibration: how many inliers does a KNOWN duplicate score?

Run (about 1 minute)::

    python tools/dup_audit/calibrate.py

For 40 random images per domain a synthetic "next shot" is made (crop, scale, rotation, brightness,
JPEG), then pushed through exactly the same pipeline (leaf mask, RootSIFT, matching) against the
original. Two difficulty levels:

* ``spec``: crop 70-95 % of the area, scale 0.8-1.2, rotation +-5 deg, brightness +-10 %, JPEG 70-95
* ``hard``: crop 35-60 %, scale 0.6-1.4, rotation +-10 deg

The percentiles printed here are the "true duplicate" side of the threshold decision in
``results/summary.md`` (field: min 213 even for ``hard``; white: p5 about 22 for ``spec``).
"""

from __future__ import annotations

import csv
import pickle
import random

import cv2
import numpy as np

from common import AUDIT_DIR, cache_path, load_records
from features import extract
from matching import match_pair

SETS = {"spec": (0.70, 0.95, 5, 0.8, 1.2), "hard": (0.35, 0.60, 10, 0.6, 1.4)}  # area min/max, rot, scale min/max
PER_DOMAIN = 40


def synthetic_next_shot(img: np.ndarray, rng: np.random.RandomState, area_min, area_max, rot, scale_min, scale_max):
    h, w = img.shape[:2]
    side = np.sqrt(rng.uniform(area_min, area_max))
    ch, cw = int(h * side), int(w * side)
    y, x = rng.randint(0, h - ch + 1), rng.randint(0, w - cw + 1)
    out = img[y : y + ch, x : x + cw]
    scale = rng.uniform(scale_min, scale_max)
    out = cv2.resize(out, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    oh, ow = out.shape[:2]
    matrix = cv2.getRotationMatrix2D((ow / 2, oh / 2), rng.uniform(-rot, rot), 1.0)
    out = cv2.warpAffine(out, matrix, (ow, oh), borderMode=cv2.BORDER_REFLECT)
    out = np.clip(out.astype(np.float32) * rng.uniform(0.9, 1.1), 0, 255).astype(np.uint8)
    _, encoded = cv2.imencode(".jpg", out, [cv2.IMWRITE_JPEG_QUALITY, int(rng.randint(70, 95))])
    return cv2.imdecode(encoded, 1)


def main() -> None:
    cv2.setNumThreads(1)
    records = load_records()
    with open(AUDIT_DIR / "feats.pkl", "rb") as f:
        feats = pickle.load(f)
    rng = np.random.RandomState(1)
    random.seed(1)
    rows = []
    for domain in ("white", "field"):
        names = [r["filename"] for r in records if r["domain"] == domain]
        for set_name, params in SETS.items():
            for name in random.sample(names, PER_DOMAIN):
                shot = synthetic_next_shot(cv2.imread(str(cache_path(name))), rng, *params)
                n_good, h, f, h_raw = match_pair(feats[name], extract(shot, domain))
                rows.append((domain, set_name, name, n_good, h, f, h_raw))
    out = AUDIT_DIR / "calibration_bursts.csv"
    with open(out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["domain", "set", "file", "n_good", "H", "F", "Hraw"])
        writer.writerows(rows)
    for domain in ("white", "field"):
        for set_name in SETS:
            h = np.array([r[4] for r in rows if r[0] == domain and r[1] == set_name])
            f = np.array([r[5] for r in rows if r[0] == domain and r[1] == set_name])
            print(f"{domain:5s} {set_name:4s} H inliers min/p5/p25/median {np.percentile(h, [0, 5, 25, 50])}  F {np.percentile(f, [0, 5, 25, 50])}")
    print(f"per-image rows in {out}")


if __name__ == "__main__":
    main()
