"""Shared paths and helpers of the one-off near-duplicate audit (see README.md)."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPO_ROOT / "Dhan-Shomadhan"
WORK = DATA_ROOT / "_work"  # written by `group3-starvenus.py prepare`: index.json and cache/
AUDIT_DIR = WORK / "dup_audit"  # large intermediate files (features, pair chunks); git-ignored


def load_records(work: Path = WORK) -> list[dict]:
    """The dataset index written by `prepare`: filename, cls, domain, ... in a fixed order."""
    return json.loads((work / "index.json").read_text(encoding="utf-8"))["records"]


def cache_path(filename: str, work: Path = WORK) -> Path:
    return work / "cache" / filename
