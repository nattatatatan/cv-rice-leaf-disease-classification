"""Step 4: turn the scored pairs into duplicate groups (connected components).

Run::

    python tools/dup_audit/build_groups.py                  # print and compare
    python tools/dup_audit/build_groups.py --write          # write annotations/duplicate_groups.json

Reads ``results/pairs_sift.csv`` (every pair with score >= 15). The rule, chosen after looking at
every candidate by eye and at the null distributions (see results/summary.md):

* only pairs of the same class AND the same domain are edges (no cross-class or cross-domain
  pair came near a threshold: field cross-class max 16, field-white same-class max 9);
* field: score >= 20 (null max 16, simulated hard bursts >= 213, wide empty gap in between);
* white: score >= 40, or score >= 20 together with file numbers at most 3 apart. Scores of 20-36 occur
  by chance for different leaves (vein texture is nearly periodic), but every true white burst in the
  data is consecutive files, and no non-consecutive pair reached 10.

The rule is deliberately inclusive: a wrongly grouped pair only costs a little split flexibility, a
missed duplicate inflates test scores. Groups are the connected components of the edges, so
rtf_7 / 8 / 9 / 10 form one group of four.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]

FIELD_MIN_SCORE = 20
WHITE_MIN_SCORE = 40
WHITE_MIN_SCORE_CONSECUTIVE = 20
CONSECUTIVE_GAP = 3


def file_number(name: str) -> int:
    return int(re.search(r"_(\d+)\.jpg$", name).group(1))


def sort_key(name: str) -> tuple[str, int]:
    return re.sub(r"\d+\.jpg$", "", name), file_number(name)


def is_edge(row: dict) -> bool:
    if row["class_a"] != row["class_b"] or row["domain_a"] != row["domain_b"]:
        return False
    score = int(row["inliers"])
    if row["domain_a"] == "field":
        return score >= FIELD_MIN_SCORE
    gap = abs(file_number(row["file_a"]) - file_number(row["file_b"]))
    return score >= WHITE_MIN_SCORE or (score >= WHITE_MIN_SCORE_CONSECUTIVE and gap <= CONSECUTIVE_GAP)


def connected_components(edges: list[tuple[str, str]]) -> list[list[str]]:
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        parent[find(a)] = find(b)
    groups: dict[str, list[str]] = {}
    for name in parent:
        groups.setdefault(find(name), []).append(name)
    return sorted((sorted(g, key=sort_key) for g in groups.values()), key=lambda g: sort_key(g[0]))


def to_json(groups: list[list[str]]) -> str:
    """One group per line: small, diff-friendly."""
    return "[\n" + ",\n".join(" " + json.dumps(g) for g in groups) + "\n]\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--pairs", type=Path, default=HERE / "results" / "pairs_sift.csv")
    parser.add_argument("--write", action="store_true", help="write annotations/duplicate_groups.json")
    args = parser.parse_args()
    with open(args.pairs, newline="", encoding="utf-8") as f:
        edges = [(r["file_a"], r["file_b"]) for r in csv.DictReader(f) if is_edge(r)]
    groups = connected_components(edges)
    text = to_json(groups)
    print(f"{len(edges)} edges, {len(groups)} groups, {sum(map(len, groups))} images")
    target = REPO_ROOT / "annotations" / "duplicate_groups.json"
    if args.write:
        target.write_text(text, encoding="utf-8")
        print(f"wrote {target}")
    elif target.is_file():
        print("identical to annotations/duplicate_groups.json" if target.read_text(encoding="utf-8") == text
              else "DIFFERS from annotations/duplicate_groups.json")
    else:
        print(text)


if __name__ == "__main__":
    main()
