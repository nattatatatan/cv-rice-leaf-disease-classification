"""Phase 02 T2.1: dataset index."""

import shutil
from pathlib import Path

import pytest

from conftest import FIELD_DIR, REPO_ROOT, WHITE_DIR, make_jpeg

DATASET = REPO_ROOT / "Dhan-Shomadhan"


# ------------------------------------------------------------------ constants


def test_expected_counts_match_the_audit(gs):
    counts = gs.EXPECTED_COUNTS
    assert sum(counts.values()) == gs.EXPECTED_TOTAL == 1106
    assert sum(n for (_, domain), n in counts.items() if domain == "white") == 769
    assert sum(n for (_, domain), n in counts.items() if domain == "field") == 337
    assert min(counts.values()) == 49 and max(counts.values()) == 219
    assert set(counts) == {(c, d) for c in gs.CLASS_NAMES for d in gs.DOMAINS}


def test_class_order_is_fixed(gs):
    assert gs.CLASS_NAMES == ("Brown Spot", "Leaf Scald", "Rice Blast", "Rice Tungro", "Sheath Blight")


def test_csv_strings_are_the_exact_dataset_strings(gs):
    assert gs.CSV_LABELS["Shath Blight(white Background)"] == ("Sheath Blight", "white")
    assert gs.CSV_LABELS["Browon Spot(Feild Background)"] == ("Brown Spot", "field")
    assert gs.CSV_LABELS["Rice Turgro(Feild Background)"] == ("Rice Tungro", "field")
    assert gs.CSV_LABELS["Leaf Scaled(white Background)"] == ("Leaf Scald", "white")
    assert len(gs.CSV_LABELS) == 10


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("bs_wb_12.jpg", ("Brown Spot", "white")),
        ("bsf_3.jpg", ("Brown Spot", "field")),
        ("sb_wb_1.jpg", ("Sheath Blight", "white")),
        ("sbf_30.jpg", ("Sheath Blight", "field")),
        ("RTF_5.JPG", ("Rice Tungro", "field")),
        ("rt_wb_95.jpg", ("Rice Tungro", "white")),
    ],
)
def test_classify_filename(gs, name, expected):
    assert gs.classify_filename(name) == expected


def test_longest_prefix_wins(gs, monkeypatch):
    table = gs.LABEL_TABLE + (("bsf_wb_", "Leaf Scald", "white", "x"),)
    monkeypatch.setattr(gs, "PREFIXES_LONGEST_FIRST", tuple(sorted(table, key=lambda row: -len(row[0]))))
    assert gs.classify_filename("bsf_wb_1.jpg") == ("Leaf Scald", "white")
    assert gs.classify_filename("bsf_1.jpg") == ("Brown Spot", "field")


# ------------------------------------------------------------------ build_index


def test_index_of_tiny_tree(gs, tiny_tree):
    records = gs.build_index(tiny_tree, expected_counts=None)
    assert [r.filename for r in records] == sorted(r.filename for r in records)
    assert len(records) == 12
    by_name = {r.filename: r for r in records}
    first = by_name["sbf_1.jpg"]
    assert (first.cls, first.cls_idx, first.domain) == ("Sheath Blight", 4, "field")
    assert first.rel_path == f"{FIELD_DIR}/Sheath Blight/sbf_1.jpg"
    assert first.exif_orientation == 6 and by_name["sbf_2.jpg"].exif_orientation == 8
    assert by_name["sbf_0.jpg"].exif_orientation == 1
    assert len(first.sha1) == 40
    assert by_name["bs_wb_0.jpg"].domain == "white"


def test_index_does_not_depend_on_folder_names(gs, tiny_tree, tmp_path):
    """The folder `Shath Blight` and its renamed variant `Sheath Blight` give the same labels."""
    before = gs.build_index(tiny_tree, expected_counts=None)
    renamed = tmp_path / "renamed"
    shutil.copytree(tiny_tree, renamed)
    (renamed / WHITE_DIR / "Shath Blight").rename(renamed / WHITE_DIR / "Sheath Blight")
    (renamed / FIELD_DIR / "Sheath Blight").rename(renamed / FIELD_DIR / "Shath Blight")
    after = gs.build_index(renamed, expected_counts=None)
    key = lambda r: (r.filename, r.cls, r.domain, r.sha1, r.exif_orientation)  # noqa: E731
    assert [key(r) for r in before] == [key(r) for r in after]
    assert {r.rel_path for r in before} != {r.rel_path for r in after}


def test_work_folder_is_skipped(gs, tiny_tree):
    make_jpeg(tiny_tree / "_work" / "cache" / "sbf_9.jpg")
    assert len(gs.build_index(tiny_tree, expected_counts=None)) == 12


def test_unknown_prefix_raises_with_the_path(gs, tiny_tree):
    make_jpeg(tiny_tree / FIELD_DIR / "Sheath Blight" / "xyz_1.jpg")
    with pytest.raises(gs.DatasetError, match="xyz_1.jpg"):
        gs.build_index(tiny_tree, expected_counts=None)


def test_duplicate_filename_raises(gs, tiny_tree):
    make_jpeg(tiny_tree / FIELD_DIR / "Other" / "sbf_1.jpg")
    with pytest.raises(gs.DatasetError, match="duplicate filename"):
        gs.build_index(tiny_tree, expected_counts=None)


def test_missing_data_root_raises(gs, tmp_path):
    with pytest.raises(gs.DatasetError, match="not a directory"):
        gs.build_index(tmp_path / "nope")


def test_expected_counts_fail_loudly_by_default(gs, tiny_tree):
    with pytest.raises(gs.DatasetError, match="not the expected dataset") as excinfo:
        gs.build_index(tiny_tree)
    assert "total: expected 1106, found 12" in str(excinfo.value)
    assert "Brown Spot / white: expected 90, found 3" in str(excinfo.value)


def test_expected_counts_can_be_overridden_for_tiny_trees(gs, tiny_tree):
    expected = {("Brown Spot", "white"): 3, ("Sheath Blight", "white"): 3, ("Brown Spot", "field"): 3, ("Sheath Blight", "field"): 3}
    assert len(gs.build_index(tiny_tree, expected_counts=expected)) == 12
    expected[("Brown Spot", "field")] = 4
    with pytest.raises(gs.DatasetError, match="Brown Spot / field: expected 4, found 3"):
        gs.build_index(tiny_tree, expected_counts=expected)


def write_csv(gs, path: Path, records, *, bom: bool = False, overrides=None):
    csv_for = {(cls, domain): csv_label for _, cls, domain, csv_label in gs.LABEL_TABLE}
    lines = [",pictureName,Diseases"]
    for i, r in enumerate(records):
        label = (overrides or {}).get(r.filename) or csv_for[(r.cls, r.domain)]
        lines.append(f"{i},{r.filename},{label}")
    path.write_bytes((("\ufeff" if bom else "") + "\r\n".join(lines) + "\r\n").encode("utf-8"))


@pytest.mark.parametrize("bom", [False, True])
def test_csv_cross_check_passes(gs, tiny_tree, bom):
    records = gs.build_index(tiny_tree, expected_counts=None)
    write_csv(gs, tiny_tree / gs.CSV_FILENAME, records, bom=bom)
    assert len(gs.build_index(tiny_tree, expected_counts=None)) == 12


def test_csv_label_mismatch_raises(gs, tiny_tree):
    records = gs.build_index(tiny_tree, expected_counts=None)
    write_csv(gs, tiny_tree / gs.CSV_FILENAME, records, overrides={"bsf_1.jpg": "Rice Blast(Feild Background)"})
    with pytest.raises(gs.DatasetError, match="bsf_1.jpg"):
        gs.build_index(tiny_tree, expected_counts=None)


def test_csv_missing_row_and_unknown_string_raise(gs, tiny_tree):
    records = gs.build_index(tiny_tree, expected_counts=None)
    write_csv(gs, tiny_tree / gs.CSV_FILENAME, records[:-1])
    with pytest.raises(gs.DatasetError, match="not listed"):
        gs.build_index(tiny_tree, expected_counts=None)
    write_csv(gs, tiny_tree / gs.CSV_FILENAME, records, overrides={"bsf_1.jpg": "Brown Spot(Field Background)"})
    with pytest.raises(gs.DatasetError, match="unknown Diseases string"):
        gs.build_index(tiny_tree, expected_counts=None)


def test_csv_missing_only_warns(gs, tiny_tree, capsys):
    assert len(gs.build_index(tiny_tree, expected_counts=None)) == 12
    assert "no label CSV" in capsys.readouterr().err


def test_csv_with_wrong_columns_raises(gs, tiny_tree):
    (tiny_tree / gs.CSV_FILENAME).write_text("a,b\n1,2\n")
    with pytest.raises(gs.DatasetError, match="pictureName"):
        gs.build_index(tiny_tree, expected_counts=None)


def test_index_round_trip(gs, tiny_tree):
    records = gs.build_index(tiny_tree, expected_counts=None)
    path = gs.write_index(tiny_tree, records)
    assert path == tiny_tree / "_work" / "index.json"
    assert gs.load_index(tiny_tree) == records
    assert gs.write_index(tiny_tree, records).read_bytes() == path.read_bytes()


def test_load_index_without_prepare_is_a_clear_error(gs, tmp_path):
    with pytest.raises(gs.DatasetError, match="prepare"):
        gs.load_index(tmp_path)


def test_hashing_can_be_skipped(gs, tiny_tree):
    records = gs.build_index(tiny_tree, expected_counts=None, with_sha1=False)
    assert {r.sha1 for r in records} == {""}
    assert sorted(r.exif_orientation for r in records) == [1] * 4 + [6] * 4 + [8] * 4


# ------------------------------------------------------------------ real dataset


@pytest.mark.skipif(not DATASET.is_dir(), reason="dataset not present")
def test_real_dataset_index(gs):
    records = gs.build_index(DATASET, with_sha1=False)
    assert len(records) == 1106
    assert sum(r.exif_orientation != 1 for r in records) == 381
    assert {r.exif_orientation for r in records} == {1, 3, 6, 8}


# ------------------------------------------------------------------ Windows paths


def test_extended_path_prefix(gs):
    f = gs.extended_path
    assert f("C:\\data\\Field Background  \\x.jpg", True) == "\\\\?\\C:\\data\\Field Background  \\x.jpg"
    assert f("\\\\server\\share\\x.jpg", True) == "\\\\?\\UNC\\server\\share\\x.jpg"
    assert f("\\\\?\\C:\\x.jpg", True) == "\\\\?\\C:\\x.jpg"
    assert f("/data/x.jpg", False) == "/data/x.jpg"


# ------------------------------------------------------------------ EXIF parsing


@pytest.mark.parametrize("orientation", range(1, 9))
def test_exif_orientation_is_parsed(gs, tmp_path, orientation):
    path = make_jpeg(tmp_path / "a.jpg", orientation=orientation)
    assert gs.parse_exif_orientation(path.read_bytes()) == orientation


def test_exif_parser_is_robust(gs):
    assert gs.parse_exif_orientation(b"") == 1
    assert gs.parse_exif_orientation(b"not a jpeg") == 1
    assert gs.parse_exif_orientation(b"\xff\xd8\xff\xe1\x00\x08Exif\x00\x00") == 1  # truncated EXIF
    assert gs.parse_exif_orientation(b"\xff\xd8\xff\xd9") == 1
