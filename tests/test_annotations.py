"""Phase 06 T6.1: the 30-image selection, the labelme converter and the annotation overview figure."""

import json
from collections import Counter

import cv2
import numpy as np
import pytest

from conftest import EXPORT_TOOL_PATH, REPO_ROOT, load_module, make_cache

DATA_ROOT = REPO_ROOT / "Dhan-Shomadhan"
CONVERTER_PATH = REPO_ROOT / "tools" / "labelme_to_annotations.py"


@pytest.fixture(scope="module")
def converter():
    return load_module("labelme_to_annotations", CONVERTER_PATH)


@pytest.fixture
def field_rich_root(gs, tmp_path):
    """A data root with 6 white and 6 field cached images in each class (cache, index and manifest)."""
    root = tmp_path / "root"
    records = make_cache(gs, root, n=60)
    gs.write_index(root, records)
    return root, records


# ------------------------------------------------------------------------------------------- selection


def test_selection_is_six_field_images_per_class_two_dev_four_eval(gs):
    selection = gs.annotation_selection(gs.synthetic_records(20))
    assert len(selection) == 30
    assert [r["cls"] for r in selection] == [c for c in gs.CLASS_NAMES for _ in range(6)]
    assert all(gs.classify_filename(r["filename"]) == (r["cls"], "field") for r in selection)
    for cls in gs.CLASS_NAMES:
        rows = [r for r in selection if r["cls"] == cls]
        assert Counter(r["set"] for r in rows) == {"dev": 2, "eval": 4} and len({r["filename"] for r in rows}) == 6
        assert [r["set"] for r in rows] == ["dev"] * 2 + ["eval"] * 4, "dev first"


def test_selection_is_deterministic_and_independent_of_record_order(gs):
    records = gs.synthetic_records(20)
    first = gs.annotation_selection(records)
    assert gs.annotation_selection(records) == first
    assert gs.annotation_selection(list(reversed(records))) == first, "candidates are sorted by filename first"


def test_selection_follows_the_documented_recipe(gs):
    """default_rng(2026) permutes the sorted candidates of each class in CLASS_NAMES order (one shared stream)."""
    records = gs.synthetic_records(20)
    rng = np.random.default_rng(2026)
    for cls in gs.CLASS_NAMES:
        names = sorted(r.filename for r in records if r.cls == cls and r.domain == "field")
        expected = sorted(names[i] for i in rng.permutation(len(names))[:6])
        assert sorted(r["filename"] for r in gs.annotation_selection(records) if r["cls"] == cls) == expected


def test_selection_needs_six_field_images_per_class(gs):
    few = [r for r in gs.synthetic_records(20) if not (r.cls == "Rice Blast" and r.domain == "field" and int(r.filename[4:-4]) >= 5)]
    with pytest.raises(gs.DatasetError, match="Rice Blast: 5 field images"):
        gs.annotation_selection(few)


def test_exclusions_add_the_duplicate_partners_of_annotated_images(gs):
    selection = [{"filename": "bsf_5.jpg"}, {"filename": "rtf_12.jpg"}]
    groups = [["bsf_4.jpg", "bsf_5.jpg"], ["rtf_11.jpg", "rtf_12.jpg"], ["lsf_1.jpg", "lsf_2.jpg"]]
    assert gs.annotation_exclusions(selection, groups) == {"bsf_4.jpg", "bsf_5.jpg", "rtf_11.jpg", "rtf_12.jpg"}


def test_committed_selection_json_is_what_the_code_selects_from_the_committed_index(gs):
    document = json.loads(gs.selection_path(DATA_ROOT).read_text())
    records = gs.load_index(DATA_ROOT)
    expected = gs.annotation_selection(records)
    assert [(e["filename"], e["cls"], e["set"]) for e in document["images"]] == [(r["filename"], r["cls"], r["set"]) for r in expected]
    assert document["seed"] == 2026 and document["per_class"] == 6 and document["dev_per_class"] == 2
    assert all(e["image"] == f"_work/cache/{e['filename']}" and e["width"] > 0 and e["height"] > 0 for e in document["images"])


def test_prepare_annotations_writes_the_selection_and_copies_the_cached_images_idempotently(gs, field_rich_root):
    root, records = field_rich_root
    lines = []
    result = gs.prepare_annotations(root, records, out=lines.append)
    assert result["selected"] == 30 and result["copied"] == 30
    assert "30 field images selected (10 dev, 20 eval)" in lines[0] and "not the full dataset" in lines[1]
    selection = gs.load_selection(root)
    assert len(selection) == 30
    for row in selection:
        copy = gs.annotation_images_dir(root) / row["filename"]
        assert copy.read_bytes() == (gs.cache_dir(root) / row["filename"]).read_bytes(), "annotate the cached pixels"
    before = gs.selection_path(root).read_bytes()
    assert gs.prepare_annotations(root, records, out=lambda _: None)["copied"] == 0
    assert gs.selection_path(root).read_bytes() == before


def test_embedded_annotations_are_not_validated_against_a_synthetic_selection(gs, field_rich_root, monkeypatch):
    """The embedded real polygons describe the real selection: on a tiny tree they are ignored (like DUPLICATE_GROUPS)."""
    root, records = field_rich_root
    monkeypatch.setattr(gs, "FIELD_ANNOTATIONS", {"bsf_1.jpg": {}}, raising=False)
    lines = []
    result = gs.prepare_annotations(root, records, out=lines.append)
    assert result["figure"] is None and "not the full dataset" in lines[-1]


def test_embedded_annotations_are_validated_when_the_index_is_the_full_dataset(gs, field_rich_root, monkeypatch):
    root, records = field_rich_root
    monkeypatch.setattr(gs, "class_domain_counts", lambda _: gs.EXPECTED_COUNTS)
    monkeypatch.setattr(gs, "FIELD_ANNOTATIONS", {"bsf_1.jpg": {}}, raising=False)
    with pytest.raises(gs.DatasetError, match="do not match the selection"):
        gs.prepare_annotations(root, records, out=lambda _: None)


def test_committed_annotations_validate_against_the_committed_selection(gs):
    selection = gs.load_selection(DATA_ROOT)
    annotations = gs.embedded_field_annotations()
    assert annotations is not None, "annotations/field_salient_leaf.json is embedded"
    assert gs.validate_field_annotations(annotations, selection) is annotations
    assert len(annotations) == 30 and sum(a["ambiguous"] for a in annotations.values()) == 6


def test_prepare_annotations_skips_data_with_too_few_field_images(gs, tiny_tree):
    records = gs.build_index(tiny_tree, expected_counts=None)
    lines = []
    assert gs.prepare_annotations(tiny_tree, records, out=lines.append) == {"selected": 0}
    assert "skipped" in lines[0] and not gs.selection_path(tiny_tree).exists()


# ------------------------------------------------------------------------------------ validation + figure


def synthetic_annotations(gs, selection):
    """One triangle-ish polygon per selected image; every fifth is ambiguous."""
    return {
        row["filename"]: {"polygon": [[0.2, 0.15], [0.8, 0.3], [0.7, 0.9], [0.25, 0.8]], "ambiguous": i % 5 == 0}
        for i, row in enumerate(selection)
    }


def test_validate_field_annotations_accepts_good_and_names_the_problem_in_bad(gs):
    selection = gs.annotation_selection(gs.synthetic_records(20))
    good = synthetic_annotations(gs, selection)
    assert gs.validate_field_annotations(good, selection) is good
    first = selection[0]["filename"]
    missing = {k: v for k, v in good.items() if k != first}
    with pytest.raises(gs.DatasetError, match=f"missing.*{first}"):
        gs.validate_field_annotations(missing, selection)
    with pytest.raises(gs.DatasetError, match="unexpected.*ghost.jpg"):
        gs.validate_field_annotations({**good, "ghost.jpg": good[first]}, selection)
    for bad, message in (
        ({"polygon": [[0, 0], [1, 1]], "ambiguous": False}, "3 to 60 vertices"),
        ({"polygon": [[0, 0], [1, 0], [1.2, 1]], "ambiguous": False}, "normalised to"),
        ({"polygon": [[0, 0], [0.5, 0.5], [1, 1]], "ambiguous": False}, "no area"),
        ({"polygon": [[0, 0], [1, 0], [1, 1]], "ambiguous": "yes"}, "'ambiguous'"),
        ({"polygon": [[0.1, 0.1]] * 61, "ambiguous": False}, "3 to 60 vertices"),
    ):
        with pytest.raises(gs.DatasetError, match=message):
            gs.validate_field_annotations({**good, first: bad}, selection)


def test_annotation_overview_draws_every_polygon_on_a_300_dpi_figure(gs, field_rich_root, tmp_path):
    root, records = field_rich_root
    gs.prepare_annotations(root, records, out=lambda _: None)
    selection = gs.load_selection(root)
    annotations = synthetic_annotations(gs, selection)
    path = gs.save_annotation_overview(root, selection, annotations)
    assert path == root / "_work/figures/annotations_overview.png"
    plain = gs.save_annotation_overview(root, selection, {}, tmp_path / "plain.png")
    drawn, bare = (cv2.imread(str(p)) for p in (path, plain))
    assert drawn.shape == bare.shape and drawn.shape[1] == round(5.8 * 300)
    def count(image, bgr, tolerance):
        return int(np.all(np.abs(image.astype(int) - np.array(bgr)) < tolerance, axis=2).sum())

    # the cached test images are random blocks, so compare against the same figure without polygons
    assert count(drawn, [66, 228, 240], 40) - count(bare, [66, 228, 240], 40) > 1000, "yellow outlines are drawn"
    assert count(drawn, [0, 94, 213], 25) - count(bare, [0, 94, 213], 25) > 100, "ambiguous marker (vermilion)"


def test_annotation_overview_keeps_smooth_gradients_smooth(gs, field_rich_root):
    """The photos are downsampled with an area filter and drawn 1:1: a smooth ramp stays a smooth ramp (no palette, no flat bands)."""
    root, records = field_rich_root
    gs.prepare_annotations(root, records, out=lambda _: None)
    ramp = np.dstack([np.tile(np.linspace(20, 235, 1280)[:, None], (1, 600))] * 3).astype(np.uint8)
    ramp[..., 1] = np.clip(ramp[..., 1].astype(int) + 15, 0, 255)
    for row in gs.load_selection(root):
        gs.write_bytes_atomic(gs.cache_dir(root) / row["filename"], gs.encode_jpeg(ramp, 95))
    path = gs.save_annotation_overview(root, gs.load_selection(root), {})
    image = cv2.imread(str(path))
    column = image[:, image.shape[1] // 2 - 40 : image.shape[1] // 2 - 30, 1].mean(axis=1)
    run = column[(column > 40) & (column < 220)]
    assert len(np.unique(np.round(run))) > 150, "the green ramp keeps (nearly) every grey level"
    assert np.abs(np.diff(run))[np.abs(np.diff(run)) < 5].size > 0.9 * (run.size - 1), "no jumps inside a tile"


def test_prepare_annotations_draws_the_overview_for_the_given_annotations(gs, field_rich_root):
    root, records = field_rich_root
    gs.prepare_annotations(root, records, out=lambda _: None)
    lines = []
    result = gs.prepare_annotations(root, records, out=lines.append, annotations=synthetic_annotations(gs, gs.load_selection(root)))
    assert result["figure"] == root / "_work/figures/annotations_overview.png" and result["figure"].is_file()
    assert "6 ambiguous" in lines[-1]
    with pytest.raises(gs.DatasetError, match="do not match the selection"):
        gs.prepare_annotations(root, records, out=lambda _: None, annotations={"bsf_1.jpg": {}})


# ------------------------------------------------------------------------------------------ the converter


def labelme_file(name, polygon, *, size=(601, 1280), label="leaf", shape_type="polygon", flags=None, extra_shapes=()):
    return {
        "version": "7.8.1", "flags": flags or {},
        "shapes": [{"label": label, "points": polygon, "group_id": None, "shape_type": shape_type, "flags": {}}, *extra_shapes],
        "imagePath": f"../../Dhan-Shomadhan/_work/annotations/images/{name}", "imageData": None,
        "imageHeight": size[1], "imageWidth": size[0],
    }


def circle(center=(300, 640), radius=250, n=200):
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return [[float(center[0] + radius * np.cos(a)), float(center[1] + radius * np.sin(a))] for a in angles]


@pytest.fixture
def labelme_setup(gs, tmp_path):
    """A selection.json for the 30 real selected names (601x1280) and a labelme folder with all 30 good files."""
    root = tmp_path / "data"
    selection = json.loads(gs.selection_path(DATA_ROOT).read_text())
    path = root / "_work" / "annotations" / "selection.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(selection))
    folder = tmp_path / "labelme"
    folder.mkdir()
    for i, entry in enumerate(selection["images"]):
        stem = entry["filename"].rsplit(".", 1)[0]
        flags = {"ambiguous": True} if i == 3 else {}
        size = (entry["width"], entry["height"])
        (folder / f"{stem}.json").write_text(json.dumps(labelme_file(entry["filename"], circle((size[0] / 2, size[1] / 2), 200), size=size, flags=flags)))
    return root, folder, selection["images"], tmp_path / "out.json"


def test_converter_normalises_simplifies_and_keeps_the_ambiguous_flag(converter, labelme_setup, capsys):
    root, folder, images, out = labelme_setup
    assert converter.main(["--labelme-dir", str(folder), "--data-root", str(root), "--out", str(out)]) == 0
    result = json.loads(out.read_text())
    assert sorted(result) == sorted(e["filename"] for e in images)
    for entry in images:
        item = result[entry["filename"]]
        polygon = np.asarray(item["polygon"])
        assert 3 <= len(polygon) <= 60 and polygon.min() >= 0 and polygon.max() <= 1
        assert np.allclose(polygon.mean(axis=0), 0.5, atol=0.02), "vertices are normalised by the cached width and height"
        assert set(item) == {"polygon", "ambiguous"}
    assert [n for n, v in result.items() if v["ambiguous"]] == [images[3]["filename"]]
    text = capsys.readouterr().out
    assert "30 converted" in text and "200 ->" in text and "ambiguous" in text and "wrote" in text


def test_converted_circle_keeps_its_area(converter, labelme_setup):
    root, folder, images, out = labelme_setup
    converter.main(["--labelme-dir", str(folder), "--data-root", str(root), "--out", str(out)])
    entry = images[0]
    polygon = np.asarray(json.loads(out.read_text())[entry["filename"]]["polygon"]) * (entry["width"], entry["height"])
    assert converter.polygon_area(polygon) == pytest.approx(np.pi * 200**2, rel=0.02)


def test_converter_reports_missing_and_extra_files_and_writes_nothing(converter, labelme_setup, capsys):
    root, folder, images, out = labelme_setup
    (folder / f"{images[0]['filename'].rsplit('.', 1)[0]}.json").unlink()
    (folder / "zzz_1.json").write_text("{}")
    assert converter.main(["--labelme-dir", str(folder), "--data-root", str(root), "--out", str(out)]) == 1
    err = capsys.readouterr().err
    assert images[0]["filename"] in err and "no labelme file" in err and "zzz_1" in err and "not in the selection" in err
    assert not out.exists()


@pytest.mark.parametrize("breakage, message", [
    ("two", "found 2"),
    ("none", "found 0"),
    ("label", "found 0"),
    ("rectangle", "found 0"),
    ("extra", "unexpected extra shapes: point 'dot'"),
    ("size", "differs from the cached image"),
    ("tiny", "fewer than 3 vertices"),
])
def test_converter_rejects_wrong_shapes_labels_and_sizes(converter, labelme_setup, capsys, breakage, message):
    root, folder, images, out = labelme_setup
    entry = images[1]
    file = folder / f"{entry['filename'].rsplit('.', 1)[0]}.json"
    data = json.loads(file.read_text())
    shape = data["shapes"][0]
    if breakage == "two":
        data["shapes"].append(dict(shape))
    elif breakage == "none":
        data["shapes"] = []
    elif breakage == "label":
        shape["label"] = "Leaf"
    elif breakage == "rectangle":
        shape.update(shape_type="rectangle", points=[[10, 10], [200, 300]])
    elif breakage == "extra":
        data["shapes"].append({"label": "dot", "points": [[5, 5]], "shape_type": "point", "flags": {}})
    elif breakage == "size":
        data["imageWidth"], data["imageHeight"] = 4000, 3000
    elif breakage == "tiny":
        shape["points"] = [[10, 10], [200, 300]]
    file.write_text(json.dumps(data))
    assert converter.main(["--labelme-dir", str(folder), "--data-root", str(root), "--out", str(out)]) == 1
    err = capsys.readouterr().err
    assert file.name in err and message in err
    assert not out.exists(), "nothing is written unless all 30 images are fine"


def test_converter_needs_the_selection_and_the_labelme_folder(converter, tmp_path, capsys):
    assert converter.main(["--labelme-dir", str(tmp_path), "--data-root", str(tmp_path), "--out", str(tmp_path / "o.json")]) == 1
    assert "prepare" in capsys.readouterr().err


def test_converted_file_embeds_as_field_annotations_in_the_generated_module(converter, labelme_setup, gs, tmp_path):
    root, folder, images, out = labelme_setup
    converter.main(["--labelme-dir", str(folder), "--data-root", str(root), "--out", str(out)])
    export_tool = load_module("export_py_for_annotations", EXPORT_TOOL_PATH)
    repo = tmp_path / "repo"
    (repo / "annotations").mkdir(parents=True)
    (repo / "annotations" / "field_salient_leaf.json").write_text(out.read_text())
    sections = export_tool.embedded_sections(repo, (export_tool.EmbeddedFile("annotations/field_salient_leaf.json", "FIELD_ANNOTATIONS", required=False),))
    namespace = {}
    exec(sections[0].source, namespace)
    selection = gs.annotation_selection(gs.load_index(DATA_ROOT))
    assert gs.validate_field_annotations(namespace["FIELD_ANNOTATIONS"], selection)
