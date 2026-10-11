"""Step 2: match image pairs. Resumable, writes one small ``.npy`` per chunk of 100 pairs.

Run (hours; see README.md for the cost per tier)::

    python tools/dup_audit/run_pairs.py --tiers 1,2,3        # what the decision needs
    python tools/dup_audit/run_pairs.py --tiers 1,2,3,4      # plus the white cross-class null

Tiers:

    1  same class, same domain      (the candidates: where duplicates can be)
    2  same class, different domain (white vs field of one disease)
    3  field vs field, different class   (null reference: no scene should carry two diseases)
    4  white vs white, different class   (null reference: different leaves, vein texture still matches)

Each tier has its own folder ``chunks/t<tier>/``. Interrupt and re-run at any time: finished chunks are
skipped. Each chunk row is
(i, j, n_good, H inliers, F inliers, unvalidated H inliers); i, j index ``index.json``.
"""

from __future__ import annotations

import argparse
import itertools
import os
import pickle
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cv2
import numpy as np

from common import AUDIT_DIR, load_records
from matching import match_pair

CHUNK = 100
CHUNKS_ROOT = AUDIT_DIR / "chunks"


def tier(a: dict, b: dict) -> int:
    same_class = a["cls"] == b["cls"]
    if a["domain"] == b["domain"]:
        if same_class:
            return 1
        return 3 if a["domain"] == "field" else 4
    return 2 if same_class else 5  # 5 (cross-domain, cross-class) is never run


_feats: dict | None = None
_names: list[str] | None = None


def _init(feats_path: str, names: list[str]) -> None:
    global _feats, _names
    cv2.setNumThreads(1)
    with open(feats_path, "rb") as f:
        _feats = pickle.load(f)
    _names = names


def _run_chunk(job: tuple[str, int, list[tuple[int, int]]]) -> int:
    folder, number, pairs = job
    path = Path(folder) / f"c{number}.npy"
    if path.exists():
        return number
    bf = cv2.BFMatcher(cv2.NORM_L2)
    rows = [(i, j, *match_pair(_feats[_names[i]], _feats[_names[j]], bf)) for i, j in pairs]
    tmp = path.with_suffix(".tmp.npy")
    np.save(tmp, np.array(rows, dtype=np.int32))
    os.replace(tmp, path)
    return number


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--tiers", default="1,2,3", help="comma-separated tiers to run (default 1,2,3)")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int, default=None, help="only N pairs per tier, into separate folders (testing)")
    args = parser.parse_args()
    wanted = {int(t) for t in args.tiers.split(",")}

    records = load_records()
    names = [r["filename"] for r in records]
    by_tier: dict[int, list[tuple[int, int]]] = {t: [] for t in sorted(wanted)}
    for i, j in itertools.combinations(range(len(records)), 2):
        t = tier(records[i], records[j])
        if t in by_tier:
            by_tier[t].append((i, j))
    jobs = []
    for t, pairs in by_tier.items():
        np.random.default_rng(0).shuffle(pairs)  # spreads cheap (white) and costly (field) pairs over all chunks
        folder = CHUNKS_ROOT / (f"t{t}" if not args.limit else f"t{t}_limit{args.limit}")
        folder.mkdir(parents=True, exist_ok=True)
        pairs = pairs[: args.limit] if args.limit else pairs
        chunks = [(str(folder), k // CHUNK, pairs[k : k + CHUNK]) for k in range(0, len(pairs), CHUNK)]
        todo = [job for job in chunks if not (Path(job[0]) / f"c{job[1]}.npy").exists()]
        print(f"tier {t}: {len(pairs)} pairs, {len(chunks)} chunks, {len(todo)} still to do", flush=True)
        jobs += todo
    start = time.time()
    with ProcessPoolExecutor(args.workers, initializer=_init, initargs=(str(AUDIT_DIR / "feats.pkl"), names)) as pool:
        for n, _ in enumerate(pool.map(_run_chunk, jobs)):
            if n % 25 == 0:
                print(f"{n}/{len(jobs)} chunks, {time.time() - start:.0f} s", flush=True)
    print(f"done in {time.time() - start:.0f} s")


if __name__ == "__main__":
    main()
