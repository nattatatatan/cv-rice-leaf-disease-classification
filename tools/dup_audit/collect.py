"""Step 3: gather chunk files into one table and write the candidate list.

Run::

    python tools/dup_audit/collect.py [--min-score 15] [--out tools/dup_audit/results/pairs_sift.csv]

Score of a pair (the quantity every threshold in this audit refers to):

* field vs field: ``max(H inliers, F inliers)``. Canopy scenes are not planar, so the fundamental
  matrix often finds more inliers than the homography (rbf_13 / rbf_14: H 129, F 196).
* any pair involving a white image: ``H inliers`` only. F on a few matches over a narrow leaf is
  under-constrained and produced "all matches are inliers" artefacts in the null.

Also prints, per pair group, how many pairs were evaluated and a histogram of scores. That table is
the evidence for the thresholds in ``build_groups.py``: the null (cross-class pairs) tops out at 16
for field and 36 for white.
"""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from common import AUDIT_DIR, REPO_ROOT, load_records
from run_pairs import CHUNKS_ROOT

COLUMNS = ["i", "j", "n_good", "H", "F", "Hraw"]
BINS = [0, 1, 8, 10, 12, 15, 20, 25, 30, 40, 60, 100, 200, 10**9]


def load_pairs() -> pd.DataFrame:
    files = sorted(f for folder in CHUNKS_ROOT.glob("t[0-9]") for f in folder.glob("c*.npy") if "tmp" not in f.name)
    if not files:
        raise SystemExit(f"no chunk files under {CHUNKS_ROOT}; run run_pairs.py first")
    pairs = pd.DataFrame(np.concatenate([np.load(f) for f in files]), columns=COLUMNS).drop_duplicates(["i", "j"])
    records = load_records()
    name = np.array([r["filename"] for r in records])
    cls = np.array([r["cls"] for r in records])
    domain = np.array([r["domain"] for r in records])
    with open(AUDIT_DIR / "feats.pkl", "rb") as f:
        feats = pickle.load(f)
    keypoints = np.array([len(feats[n][0]) for n in name])

    pairs["file_a"], pairs["file_b"] = name[pairs.i], name[pairs.j]
    pairs["class_a"], pairs["class_b"] = cls[pairs.i], cls[pairs.j]
    pairs["domain_a"], pairs["domain_b"] = domain[pairs.i], domain[pairs.j]
    pairs["kpmin"] = np.minimum(keypoints[pairs.i], keypoints[pairs.j])
    pairs["inliers"] = pairs[["H", "F"]].max(axis=1)
    both_field = (pairs.domain_a == "field") & (pairs.domain_b == "field")
    pairs["score"] = np.where(both_field, pairs.inliers, pairs.H)
    pairs["match_ratio"] = (pairs.score / pairs.kpmin).round(4)
    same_class = (pairs.class_a == pairs.class_b).to_numpy()
    cross_domain = (pairs.domain_a != pairs.domain_b).to_numpy()
    white = (pairs.domain_a == "white").to_numpy()
    pairs["group"] = np.where(
        cross_domain,
        "field-white same-class",
        np.where(white, np.where(same_class, "white same-class", "white cross-class"),
                 np.where(same_class, "field same-class", "field cross-class")),
    )
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--min-score", type=int, default=15)
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "tools" / "dup_audit" / "results" / "pairs_sift.csv")
    args = parser.parse_args()
    pairs = load_pairs()

    for group, rows in pairs.groupby("group"):
        histogram = np.histogram(rows.score, bins=BINS)[0]
        print(f"{group}: {len(rows)} pairs, max score {rows.score.max()}")
        print("   bins", BINS[:-1], "\n   pairs", histogram.tolist())

    top = pairs[pairs.score >= args.min_score].sort_values(["score", "inliers"], ascending=False)
    top = top.assign(inliers=top.score, inliers_H=top.H, inliers_F=top.F)  # "inliers" in the CSV is the score
    columns = ["file_a", "file_b", "class_a", "class_b", "domain_a", "domain_b", "inliers", "match_ratio",
               "inliers_H", "inliers_F", "n_good", "group"]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    top[columns].to_csv(args.out, index=False)
    print(f"wrote {len(top)} pairs with score >= {args.min_score} to {args.out}")


if __name__ == "__main__":
    main()
