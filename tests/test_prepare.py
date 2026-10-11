"""Phase 02 T2.7: `prepare` end to end on a tiny synthetic tree."""

import json
import os
import shutil
from pathlib import Path

import pytest

from conftest import FIELD_DIR

TINY_COUNTS = {
    ("Brown Spot", "white"): 3,
    ("Sheath Blight", "white"): 3,
    ("Brown Spot", "field"): 3,
    ("Sheath Blight", "field"): 3,
}


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted((root / "_work").rglob("*"))
        if p.is_file()
    }


def test_prepare_writes_everything_and_warns_about_unconfirmed_duplicates(gs, tiny_tree):
    lines = []
    summary = gs.prepare_data(tiny_tree, expected_counts=TINY_COUNTS, workers=1, out=lines.append)
    text = "\n".join(lines)
    assert summary["records"] == 12 and summary["cache"].built == 12
    assert "WARNING" in text and "UNCONFIRMED" in text
    assert "index       12 images" in text and "exif" in text and "splits" in text
    assert len(lines) <= 20, "one-screen summary"

    work = tiny_tree / "_work"
    assert (work / "index.json").is_file()
    assert len(list((work / "cache").glob("*.jpg"))) == 12
    assert (work / "results" / "near_duplicates.csv").is_file()
    assert (work / "results" / "dataset_counts.md").is_file()
    assert (work / "figures" / "dataset_grid.png").is_file()
    assert (work / "figures" / "class_domain_counts.png").is_file()
    assert sorted(p.name for p in (work / "splits").glob("*.json")) == [f"split_{k}.json" for k in range(5)]
    assert not (work / "duplicate_groups.json").exists(), "prepare never invents duplicate groups"
    for seed in range(5):
        assert gs.load_split(tiny_tree, seed)["seed"] == seed
    assert len(gs.load_index(tiny_tree)) == 12


def test_prepare_is_idempotent(gs, tiny_tree):
    gs.prepare_data(tiny_tree, expected_counts=TINY_COUNTS, workers=1, out=lambda _: None)
    first = snapshot(tiny_tree)
    lines = []
    summary = gs.prepare_data(tiny_tree, expected_counts=TINY_COUNTS, workers=1, out=lines.append)
    assert summary["cache"].built == 0 and summary["cache"].reused == 12
    assert set(summary["splits"].values()) == {"unchanged"}
    assert snapshot(tiny_tree) == first, "second run reproduces every output byte for byte"


def test_prepare_uses_confirmed_duplicate_groups(gs, tiny_tree):
    (tiny_tree / "_work").mkdir()
    (tiny_tree / "_work" / "duplicate_groups.json").write_text(json.dumps([["bsf_0.jpg", "bsf_1.jpg"]]))
    lines = []
    summary = gs.prepare_data(tiny_tree, expected_counts=TINY_COUNTS, workers=1, out=lines.append)
    assert summary["duplicate_groups"] == [["bsf_0.jpg", "bsf_1.jpg"]]
    assert "UNCONFIRMED" not in "\n".join(lines)
    assert "1 confirmed groups" in "\n".join(lines)


def test_prepare_rejects_groups_with_unknown_files(gs, tiny_tree):
    (tiny_tree / "_work").mkdir()
    (tiny_tree / "_work" / "duplicate_groups.json").write_text(json.dumps([["bsf_0.jpg", "ghost.jpg"]]))
    with pytest.raises(gs.DatasetError, match="ghost.jpg"):
        gs.prepare_data(tiny_tree, expected_counts=TINY_COUNTS, workers=1, out=lambda _: None)


def test_prepare_with_default_counts_rejects_a_different_dataset(gs, tiny_tree):
    with pytest.raises(gs.DatasetError, match="not the expected dataset"):
        gs.prepare_data(tiny_tree, workers=1, out=lambda _: None)


def test_prepare_works_from_any_working_directory(gs, tiny_tree, tmp_path, monkeypatch):
    elsewhere = tmp_path / "somewhere" / "else"
    elsewhere.mkdir(parents=True)
    monkeypatch.chdir(elsewhere)
    relative = os.path.relpath(tiny_tree, elsewhere)
    gs.prepare_data(relative, expected_counts=TINY_COUNTS, workers=1, out=lambda _: None)
    assert (tiny_tree / "_work" / "index.json").is_file()
    assert not (elsewhere / "_work").exists()


def test_prepare_does_not_modify_the_dataset(gs, tiny_tree):
    def tree(root):
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file() and "_work" not in p.parts}

    before = tree(tiny_tree)
    gs.prepare_data(tiny_tree, expected_counts=TINY_COUNTS, workers=1, out=lambda _: None)
    assert tree(tiny_tree) == before


def test_prepare_survives_renamed_class_folders(gs, tiny_tree, tmp_path):
    root = tmp_path / "renamed"
    shutil.copytree(tiny_tree, root)
    (root / FIELD_DIR / "Browon Spot").rename(root / FIELD_DIR / "Brown Spot Field")
    gs.prepare_data(root, expected_counts=TINY_COUNTS, workers=1, out=lambda _: None)
    assert len(gs.load_index(root)) == 12


def test_pick_smoke_records_covers_orientations_and_strata(gs):
    records = [
        gs.Record(r.filename, r.rel_path, r.cls, r.cls_idx, r.domain, {5: 3, 6: 6, 7: 8}.get(i, 1), "")
        for i, r in enumerate(gs.synthetic_records(5))
    ]
    chosen = gs.pick_smoke_records(records, 20)
    assert len(chosen) == 20 == len({r.filename for r in chosen})
    assert {3, 6, 8} <= {r.exif_orientation for r in chosen}
    assert len({r.stratum for r in chosen}) == 10
    assert len(gs.pick_smoke_records(records[:4], 20)) == 4
    assert gs.pick_smoke_records([], 20) == []
