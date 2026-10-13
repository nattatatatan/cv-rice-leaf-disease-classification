"""Phase 05 T5.1: HSV pseudo-masks of the white-background images, reject list, area table and QC sheets."""

import json

import cv2
import numpy as np
import pytest

from conftest import make_cache


def synthetic_leaf(height=640, width=300, *, paper=(205, 207, 212), seed=0):
    """Grey paper with a light gradient, a green ellipse (the leaf) with brown spots, as (image, truth mask)."""
    rng = np.random.default_rng(seed)
    image = np.empty((height, width, 3), np.uint8)
    image[:] = paper
    image = np.clip(image.astype(np.float32) * np.linspace(1.0, 0.85, height)[:, None, None], 0, 255).astype(np.uint8)
    truth = np.zeros((height, width), np.uint8)
    cv2.ellipse(truth, (width // 2 + 20, height // 2), (60, 270), 8, 0, 360, 255, -1)
    leaf = np.empty_like(image)
    leaf[:] = (50, 130, 40)
    leaf = np.clip(leaf.astype(np.int16) + rng.integers(-8, 9, leaf.shape), 0, 255).astype(np.uint8)
    image[truth > 0] = leaf[truth > 0]
    for _ in range(12):  # brown lesions, fully inside the leaf
        x, y = int(rng.integers(width // 2 - 20, width // 2 + 60)), int(rng.integers(150, 500))
        cv2.circle(image, (x, y), int(rng.integers(5, 11)), (150, 100, 60), -1)
    image = cv2.GaussianBlur(image, (3, 3), 0)
    return image, truth


def iou(a, b):
    a, b = a > 0, b > 0
    return (a & b).sum() / (a | b).sum()


def test_synthetic_leaf_on_grey_paper_has_iou_above_095(gs):
    image, truth = synthetic_leaf()
    mask = gs.white_pseudo_mask(image)
    assert mask.dtype == np.uint8 and mask.shape == truth.shape and set(np.unique(mask)) <= {0, 255}
    assert iou(mask, truth) > 0.95


@pytest.mark.parametrize("paper", [(205, 207, 212), (222, 224, 226), (170, 174, 182)])
def test_mask_is_robust_to_the_paper_brightness_and_dark_leaves(gs, paper):
    image, truth = synthetic_leaf(paper=paper, seed=3)
    assert iou(gs.white_pseudo_mask(image), truth) > 0.95
    dark = image.copy()
    dark[truth > 0] = (dark[truth > 0] * 0.28).astype(np.uint8)  # a dark leaf: V around 30, must not be cut by V > v_min
    assert iou(gs.white_pseudo_mask(dark), truth) > 0.9


def test_fill_holes_fills_enclosed_background_only(gs):
    mask = np.zeros((40, 40), np.uint8)
    cv2.rectangle(mask, (5, 5), (34, 34), 255, -1)
    mask[15:25, 15:25] = 0  # enclosed hole
    mask[:, 0:3] = 0
    filled = gs.fill_holes(mask)
    assert filled[20, 20] == 255 and filled[2, 2] == 0 and filled[20, 1] == 0
    notch = np.zeros((40, 40), np.uint8)
    notch[5:35, 5:35] = 255
    notch[5:15, 18:22] = 0  # open to the outside: not a hole
    assert gs.fill_holes(notch)[8, 20] == 0


def test_a_leaf_touching_the_image_border_keeps_its_enclosed_lesion_filled(gs):
    mask = np.zeros((60, 30), np.uint8)
    mask[:, 8:22] = 255  # crosses the top and the bottom border
    mask[25:35, 12:18] = 0
    assert gs.fill_holes(mask)[30, 15] == 255


def test_largest_component_keeps_one_blob_and_survives_an_empty_mask(gs):
    mask = np.zeros((50, 50), np.uint8)
    mask[5:30, 5:30] = 255
    mask[40:44, 40:44] = 255
    out = gs.largest_component(mask)
    assert out[10, 10] == 255 and out[41, 41] == 0
    assert not gs.largest_component(np.zeros((8, 8), np.uint8)).any()


def test_named_constants_are_part_of_the_recipe_hash(gs):
    assert {"blur", "v_min", "close", "open", "version"} == set(gs.MASK_CONSTANTS)
    assert gs.MASK_V_MIN == 20 and gs.MASK_CLOSE_KSIZE == 45
    assert len(gs.MASK_RECIPE) == 12


# ---------------------------------------------------------------------- files, idempotence, rejects


@pytest.fixture
def white_root(gs, tmp_path):
    """10 cached synthetic white leaves of 5 classes (make_cache alternates classes) plus the matching index."""
    root = tmp_path / "root"
    records = []
    prefixes = {c: p for p, c, d, _ in gs.LABEL_TABLE if d == "white"}
    for i in range(10):
        cls = gs.CLASS_NAMES[i % 5]
        image, _ = synthetic_leaf(seed=i)
        name = f"{prefixes[cls]}{i}.jpg"
        gs.write_bytes_atomic(gs.cache_dir(root) / name, gs.encode_jpeg(image, 95))
        records.append(gs.Record(name, f"x/{name}", cls, gs.CLASS_NAMES.index(cls), "white", 1, f"sha{i}"))
    return root, records


def test_build_masks_writes_one_png_per_white_image_and_is_idempotent(gs, white_root):
    root, records = white_root
    stats = gs.build_white_masks(root, records, workers=1)
    assert (stats.total, stats.built, stats.reused) == (10, 10, 0)
    for record in records:
        path = gs.white_mask_path(root, record.filename)
        assert path.name == f"{record.filename}.png"
        mask = gs.read_white_mask(root, record.filename)
        assert mask.shape == (640, 300) and set(np.unique(mask)) == {0, 255}
    manifest = json.loads(gs.white_masks_manifest_path(root).read_text())
    assert manifest["recipe"] == gs.MASK_RECIPE and 0.05 < manifest["files"][records[0].filename]["area"] < 0.3
    stamp = gs.white_mask_path(root, records[0].filename).stat().st_mtime_ns
    again = gs.build_white_masks(root, records, workers=1)
    assert (again.built, again.reused) == (0, 10)
    assert gs.white_mask_path(root, records[0].filename).stat().st_mtime_ns == stamp


def test_masks_are_rebuilt_when_an_image_or_the_recipe_changes(gs, white_root, monkeypatch):
    root, records = white_root
    gs.build_white_masks(root, records, workers=1)
    changed = [gs.replace(records[0], sha1="other"), *records[1:]]
    assert gs.build_white_masks(root, changed, workers=1).built == 1
    gs.white_mask_path(root, records[2].filename).unlink()
    assert gs.build_white_masks(root, changed, workers=1).built == 1
    monkeypatch.setattr(gs, "MASK_RECIPE", "0" * 12)
    assert gs.build_white_masks(root, changed, workers=1).built == 10, "a changed recipe rebuilds every mask"


def test_masks_ignore_field_images_and_name_missing_cache_files(gs, white_root):
    root, records = white_root
    field = gs.Record("bsf_1.jpg", "x/bsf_1.jpg", "Brown Spot", 0, "field", 1, "")
    assert gs.build_white_masks(root, [field, *records], workers=1).total == 10
    ghost = gs.Record("bs_wb_999.jpg", "x/bs_wb_999.jpg", "Brown Spot", 0, "white", 1, "g")
    with pytest.raises(gs.DatasetError, match="bs_wb_999.jpg is missing; run `prepare`"):
        gs.build_white_masks(root, [ghost], workers=1)
    with pytest.raises(gs.DatasetError, match="does not exist"):
        gs.read_white_mask(root, "nope.jpg")


def test_reject_list_ignores_comments_and_blank_lines_and_validates_names(gs, white_root):
    root, records = white_root
    assert gs.load_white_rejects(root) == set(), "no file, no rejects"
    path = gs.white_rejects_path(root)
    assert path == root / "_work" / "masks" / "white_rejects.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    first, second = records[0].filename, records[1].filename
    path.write_text(f"# reviewed by Nattan\n\n{first}   # shadow included\n  {second}\n#{records[2].filename}\n")
    assert gs.load_white_rejects(root, records) == {first, second}
    path.write_text(f"{first}\nbsf_1.jpg\n")
    with pytest.raises(gs.DatasetError, match=r"line 2: 'bsf_1.jpg' is not a white-background image"):
        gs.load_white_rejects(root, records)


def test_the_full_dataset_uses_the_embedded_reject_list_and_checks_it(gs, white_root, monkeypatch):
    """On the real dataset the list comes from WHITE_REJECTS (it travels in the .py); a local file is then ignored.
    A tiny tree stands in for the full dataset by declaring its own counts the expected ones."""
    root, records = white_root
    gs.white_rejects_path(root).parent.mkdir(parents=True, exist_ok=True)
    gs.white_rejects_path(root).write_text(f"{records[2].filename}\n")
    monkeypatch.setattr(gs, "EXPECTED_COUNTS", gs.class_domain_counts(records))
    monkeypatch.setattr(gs, "WHITE_REJECTS", {"note": "test", "rejects": {records[0].filename: "shadow"}})
    assert gs.load_white_rejects(root, records) == {records[0].filename}
    assert gs.white_rejects_source(records) == "embedded WHITE_REJECTS"
    monkeypatch.setattr(gs, "WHITE_REJECTS", {"note": "test", "rejects": {"bs_wb_999.jpg": "typo"}})
    with pytest.raises(gs.DatasetError, match=r"WHITE_REJECTS .* not white images of the index: \['bs_wb_999.jpg'\]"):
        gs.load_white_rejects(root, records)


def test_the_embedded_reject_list_is_the_reviewed_one(gs):
    assert len(gs.WHITE_REJECTS["rejects"]) == 33
    assert all(name.endswith(".jpg") and "_wb_" in name for name in gs.WHITE_REJECTS["rejects"])


def test_area_table_is_per_class_over_accepted_leaves(gs, white_root):
    root, records = white_root
    areas = {r.filename: 0.05 * (1 + i % 5) for i, r in enumerate(records)}
    rows = gs.mask_area_rows(records, areas, {records[0].filename})
    assert [r[0] for r in rows] == [*gs.CLASS_NAMES, "all"]
    assert [r[1] for r in rows] == [1, 2, 2, 2, 2, 9], "one leaf of the first class is rejected"
    assert rows[1][2] == pytest.approx(10.0)  # two leaves of 10%
    text = gs.white_mask_area_markdown(records, areas, {records[0].filename})
    assert text.startswith("| Class | Leaves | Mean area (%)") and "| **All** | 9 |" in text and "rejected: 1)" in text
    gs.build_white_masks(root, records, workers=1)
    path = gs.write_white_mask_area(root, records, set())
    assert path == root / "_work" / "results" / "white_mask_area.md" and "| Brown Spot | 2 |" in path.read_text()


# ------------------------------------------------------------------------------------- QC sheets


def test_sheets_cover_all_images_with_at_most_48_each(gs):
    groups = gs.qc_sheet_groups(769)
    sizes = [stop - start for start, stop in groups]
    assert len(groups) == 17 and sum(sizes) == 769 and max(sizes) <= 48 and max(sizes) - min(sizes) <= 1
    assert groups[0][0] == 0 and groups[-1][1] == 769 and all(a[1] == b[0] for a, b in zip(groups, groups[1:]))
    assert gs.qc_sheet_groups(48) == [(0, 48)] and gs.qc_sheet_groups(49) == [(0, 25), (25, 49)] and gs.qc_sheet_groups(0) == [(0, 0)]


def test_qc_sheet_draws_the_outline_and_marks_rejects(gs, white_root):
    root, records = white_root
    gs.build_white_masks(root, records, workers=1)
    paths = gs.save_mask_qc_sheets(root, records, rejects={records[1].filename})
    assert [p.name for p in paths] == ["pseudo_mask_qc_01.png"] and paths[0].parent == root / "_work" / "figures"
    sheet = cv2.imread(str(paths[0]))
    tile_w, tile_h = gs.QC_TILE[0], gs.QC_TILE[1] + gs.QC_LABEL_HEIGHT
    assert sheet.shape == (gs.QC_ROWS * (tile_h + gs.QC_GAP) + gs.QC_GAP, gs.QC_COLUMNS * (tile_w + gs.QC_GAP) + gs.QC_GAP, 3)

    def near(image, rgb, tolerance=30):
        return int(np.all(np.abs(image.astype(int) - np.array(rgb[::-1])) < tolerance, axis=2).sum())

    first = sheet[gs.QC_GAP : gs.QC_GAP + gs.QC_TILE[1], gs.QC_GAP : gs.QC_GAP + tile_w]
    second = sheet[gs.QC_GAP : gs.QC_GAP + gs.QC_TILE[1], 2 * gs.QC_GAP + tile_w : 2 * gs.QC_GAP + 2 * tile_w]
    assert near(first, (255, 255, 0)) > 300, "the outline is drawn in yellow, 1 px wide"
    assert near(first, (213, 94, 0)) == 0 and near(second, (213, 94, 0)) > 1000, "only the rejected tile has the vermilion frame"
    outline = near(first, (255, 255, 0))
    assert outline < 0.02 * first.shape[0] * first.shape[1], "thin: a line, not a fill"
    again = gs.save_mask_qc_sheets(root, records, rejects={records[1].filename})
    assert cv2.imread(str(again[0])).tobytes() == sheet.tobytes(), "deterministic"


def test_old_sheets_are_removed_and_prepare_reports(gs, white_root):
    root, records = white_root
    stale = gs.figures_dir(root) / "pseudo_mask_qc_09.png"
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_bytes(b"old")
    lines = []
    result = gs.prepare_pseudo_masks(root, records, workers=1, out=lines.append)
    assert not stale.exists() and result["built"] == 10 and len(result["sheets"]) == 1
    assert "10 white pseudo-masks: built 10" in lines[0] and "0 rejected (_work/masks/white_rejects.txt)" in lines[0]
    lines.clear()
    assert gs.prepare_pseudo_masks(root, records, workers=1, out=lines.append)["built"] == 0
    assert "up to date 10" in lines[0]
    assert gs.prepare_pseudo_masks(root, [], out=lines.append) == {"built": 0}
