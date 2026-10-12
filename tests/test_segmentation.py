"""Phase 06 T6.2-T6.3: the leaf segmenter, mask -> crop box, the Method B crop hook and E4-B plumbing, the segmenter
metrics on annotated images and the leakage rule (dev any time, eval once and only with --final)."""

import json
import os

import cv2
import numpy as np
import pytest
import torch

from conftest import REPO_ROOT, make_cache
from test_composites import method_base, method_root, run_cli  # noqa: F401 (fixtures)

DATA_ROOT = REPO_ROOT / "Dhan-Shomadhan"
TINY = (64, 32)  # segmenter input of the tests (H, W)


# ---------------------------------------------------------------------------------------------- model


@pytest.mark.parametrize("arch", ["lraspp_mobilenet_v3_large", "deeplabv3_mobilenet_v3_large"])
def test_segmenter_outputs_one_leaf_logit_per_pixel(gs, arch):
    model = gs.build_segmenter(arch, pretrained=False).eval()
    with torch.no_grad():
        logits = gs.seg_logits(model, torch.zeros(2, 3, *TINY))
    assert logits.shape == (2, *TINY)


def test_unknown_segmenter_and_the_input_size(gs):
    with pytest.raises(ValueError, match="unknown segmenter"):
        gs.build_segmenter("unet")
    assert gs.seg_size() == (512, 256) and gs.seg_size(4) == (128, 64)
    row = gs.EXPERIMENTS["S-seg"]
    assert (row.backbone, row.epochs, row.lr, row.weight_decay, row.batch_size) == ("lraspp_mobilenet_v3_large", 40, 3e-4, 1e-4, 16)
    assert gs.SEG_SAMPLES_PER_EPOCH == 1000 and gs.SEG_COMPOSITE_SHARE == 0.5 and gs.SEG_VAL_COMPOSITES == 200


@pytest.mark.skipif(not (DATA_ROOT / "_work" / "weights" / "hub" / "checkpoints" / "lraspp_mobilenet_v3_large-d234d4ea.pth").is_file(),
                    reason="the COCO_WITH_VOC_LABELS_V1 weights are not downloaded")
def test_pretrained_segmenter_keeps_the_coco_weights_and_replaces_both_heads(gs):
    previous = os.environ.get("TORCH_HOME")
    try:
        model = gs.build_segmenter("lraspp_mobilenet_v3_large", data_root=DATA_ROOT)
        reference = gs.build_segmenter("lraspp_mobilenet_v3_large", data_root=DATA_ROOT)
    finally:
        os.environ.pop("TORCH_HOME", None) if previous is None else os.environ.__setitem__("TORCH_HOME", previous)
    assert model.classifier.low_classifier.out_channels == 1 and model.classifier.high_classifier.out_channels == 1
    a, b = model.state_dict(), reference.state_dict()
    backbone = [k for k in a if k.startswith("backbone.")]
    assert backbone and all(torch.equal(a[k], b[k]) for k in backbone), "the backbone is the pretrained one, not random"


# ---------------------------------------------------------------------------------------------- loss


def test_seg_loss_is_low_for_the_right_mask_and_high_for_the_wrong_one(gs):
    target = torch.zeros(2, 32, 16)
    target[:, 8:24, 4:12] = 1
    good = (target * 2 - 1) * 10
    assert gs.seg_loss(good, target).item() < 0.01
    assert gs.seg_loss(-good, target).item() > 5
    empty = torch.zeros(1, 8, 8)
    assert gs.seg_loss(torch.full((1, 8, 8), -10.0), empty).item() < 0.01, "an empty target with an empty prediction is fine"


def test_mask_iou_per_image(gs):
    pred = np.zeros((2, 4, 4), bool)
    truth = np.zeros((2, 4, 4), bool)
    pred[0, :2], truth[0, :, :2] = True, True
    assert gs.mask_iou(pred, truth) == pytest.approx([4 / 12, 1.0])


# ------------------------------------------------------------------------------------- post-processing


def test_postprocess_keeps_the_component_with_the_largest_area_times_centrality(gs):
    prob = np.zeros((512, 256), np.float32)
    prob[0:200, 0:100] = 0.9  # 15% of the image, in the corner: centrality 0.39
    prob[206:306, 78:178] = 0.9  # 7.6% of the image, at the centre: centrality 1
    post = gs.postprocess_probability(prob)
    assert not post.fallback and post.mask[256, 128] and not post.mask[10, 10]
    assert post.tight == pytest.approx((78 / 256, 206 / 512, 178 / 256, 306 / 512))
    w, h = 100 / 256, 100 / 512
    assert post.box == pytest.approx((78 / 256 - 0.15 * w, 206 / 512 - 0.15 * h, 178 / 256 + 0.15 * w, 306 / 512 + 0.15 * h))
    assert post.area == pytest.approx(10000 / (512 * 256))
    prob[0:400, 0:100] = 0.9  # now the corner one is so large that it wins anyway
    assert gs.postprocess_probability(prob).mask[10, 10]


def test_postprocess_falls_back_to_the_full_image_below_two_percent(gs):
    prob = np.zeros((512, 256), np.float32)
    prob[250:300, 100:150] = 0.9  # 1.9% of the image
    prob[0:200, 0:100] = 0.5  # not above the threshold
    post = gs.postprocess_probability(prob)
    assert post.fallback and post.tight is None and post.box == (0.0, 0.0, 1.0, 1.0) and not post.mask.any() and post.area == 0.0
    prob[250:310, 100:160] = 0.9  # 2.7%
    assert not gs.postprocess_probability(prob).fallback


def test_crop_box_is_grown_to_the_classifier_aspect_shifted_inside_and_clamped(gs):
    width, height = 600, 1280
    assert gs.classifier_aspect("rect") == 2.0 and gs.classifier_aspect("pad") == 1.0
    # 120 x 128 px -> grown in height to 240 around the same centre
    assert gs.crop_box_pixels((0.4, 0.4, 0.6, 0.5), 2.0, width, height) == (240, 456, 360, 696)
    # at the top edge: grown to 60 x 120 and shifted down into the image (the aspect is kept)
    assert gs.crop_box_pixels((0.0, 0.0, 0.1, 0.05), 2.0, width, height) == (0, 0, 60, 120)
    # a tall box at square aspect is widened
    assert gs.crop_box_pixels((0.45, 0.25, 0.55, 0.75), 1.0, width, height) == (0, 320, 600, 960)
    # larger than the image: clamped to the whole image
    assert gs.crop_box_pixels((-0.15, -0.15, 1.15, 1.15), 2.0, width, height) == (0, 0, width, height)


def test_jitter_crop_is_seeded_bounded_and_keeps_the_aspect(gs):
    crop = (200, 400, 400, 800)
    rng = lambda: np.random.default_rng(3)  # noqa: E731
    first = gs.jitter_crop(crop, rng(), 600, 1280)
    assert first == gs.jitter_crop(crop, rng(), 600, 1280)
    for seed in range(50):
        x0, y0, x1, y1 = gs.jitter_crop(crop, np.random.default_rng(seed), 600, 1280)
        assert 190 - 1 <= x1 - x0 <= 210 + 1 and abs((y1 - y0) / (x1 - x0) - 2.0) < 0.03
        assert abs((x0 + x1) / 2 - 300) <= 0.05 * 200 + 1 and abs((y0 + y1) / 2 - 600) <= 0.05 * 400 + 1


# ------------------------------------------------------------------------------------- Method B hook


def boxes_for(records, box=(0.25, 0.25, 0.75, 0.5), fallback=()):
    return {r.filename: {"domain": r.domain, "fallback": r.filename in fallback, "area": 0.1,
                         "tight": None if r.filename in fallback else list(box), "box": [0, 0, 1, 1] if r.filename in fallback else list(box)}
            for r in records}


def test_seg_crop_hook_crops_exactly_at_eval_and_jitters_at_train(gs, tmp_path):
    records = make_cache(gs, tmp_path, n=4)
    rgb = gs.read_cached_rgb(tmp_path, records[0].filename)
    height, width = rgb.shape[:2]
    boxes = boxes_for(records, fallback={records[1].filename})
    exact = gs.SegCropHook(boxes, 2.0)
    assert not exact.stochastic
    x0, y0, x1, y1 = gs.crop_box_pixels(boxes[records[0].filename]["box"], 2.0, width, height)
    assert np.array_equal(exact(rgb, records[0]), rgb[y0:y1, x0:x1])
    assert exact(rgb, records[1]).shape == rgb.shape, "a fallback crops nothing"
    jitter = gs.SegCropHook(boxes, 2.0, gs.SEG_JITTER)
    assert jitter.stochastic
    a = jitter(rgb, records[0], np.random.default_rng(1))
    assert np.array_equal(a, jitter(rgb, records[0], np.random.default_rng(1)))
    assert any(jitter(rgb, records[0], np.random.default_rng(s)).shape != a.shape for s in range(2, 10))
    with pytest.raises(gs.ExperimentError, match="no box"):
        exact(rgb, gs.replace(records[0], filename="other.jpg"))
    with pytest.raises(gs.ExperimentError, match="LiveCropHook"):
        exact(rgb, None)


def test_leaf_dataset_gives_a_stochastic_hook_its_own_stream_per_sample(gs, tmp_path):
    records = make_cache(gs, tmp_path, n=4)
    hook = gs.SegCropHook(boxes_for(records), 2.0, gs.SEG_JITTER)
    ds = gs.LeafDataset(tmp_path, records, gs.ImageTransform("rect", train=False, size_div=8), seed=0, input_hook=hook)
    raw = lambda i, e: ds.load_raw(i, e)[0]  # noqa: E731
    assert np.array_equal(raw(0, 0), raw(0, 0)), "a sample is a function of (seed, epoch, index)"
    assert any(raw(0, e).shape != raw(0, 0).shape or not np.array_equal(raw(0, e), raw(0, 0)) for e in range(1, 8)), "epochs differ"


def test_make_input_hook_reads_the_split_boxes_and_fails_clearly_without_them(gs, tmp_path):
    cfg = gs.replace(gs.EXPERIMENTS["E4-B"], backbone="resnet50", input_mode="rect", lr=1e-4)
    assert gs.make_input_hook(gs.EXPERIMENTS["E0-rect"], tmp_path, 0) is None
    with pytest.raises(gs.ExperimentError, match=r"run --exp S-seg --splits 2"):
        gs.make_input_hook(cfg, tmp_path, 2)
    records = make_cache(gs, tmp_path, n=2)
    path = gs.boxes_path(tmp_path, 2)
    path.parent.mkdir(parents=True)
    gs.write_boxes(path, 2, boxes_for(records), {"white": {"n": 1, "fallback": 0}, "field": {"n": 1, "fallback": 0}}, "S-seg")
    assert gs.make_input_hook(cfg, tmp_path, 2).jitter == 0.0
    assert gs.make_input_hook(cfg, tmp_path, 2, train=True).jitter == gs.SEG_JITTER
    assert gs.load_boxes(tmp_path, 2) == json.loads(path.read_text())["images"]


# ----------------------------------------------------------------------------------- training samples


def test_seg_augment_moves_image_and_mask_together(gs):
    mask = np.zeros((400, 200), np.uint8)
    cv2.ellipse(mask, (90, 210), (40, 150), 15, 0, 360, 255, -1)
    rgb = np.dstack([mask, np.zeros_like(mask), 255 - mask])  # red leaf on blue
    for seed in range(5):
        image, target = gs.seg_augment(rgb, mask, np.random.default_rng(seed), (128, 64))
        assert image.shape == (128, 64, 3) and target.shape == (128, 64) and set(np.unique(target)) <= {0, 1}
        agree = ((image[..., 0] > image[..., 2]) == target.astype(bool)).mean()
        assert agree > 0.97, f"seed {seed}: the mask no longer covers the leaf ({agree:.3f})"


def test_segmenter_dataset_mixes_composites_and_white_masks_reproducibly(gs, method_root):
    root, records = method_root
    pool = gs.CompositePool(root, 0, records, rejects=set(), exclusions=set())
    split = gs.load_split(root, 0)
    whites = gs.white_mask_records(root, records, split["train"], rejects=set())
    assert whites and all(r.domain == "white" and r.filename in split["train"] for r in whites)
    composites = gs.CompositeSource(root, 0, 5, 0, pool=pool)
    ds = gs.SegmenterDataset(root, whites, composites, size=TINY, n_samples=10, seed=0)
    assert len(ds) == 10 and ds.n_composites == 5
    for i in (0, 7):
        image, mask, index = ds[(i, 0)]
        assert image.shape == (3, *TINY) and image.dtype == torch.uint8 and mask.shape == (1, *TINY) and index == i
        assert 0 < mask.float().mean() < 1, "the target is neither empty nor everything"
        again, mask_again, _ = ds[(i, 0)]
        assert torch.equal(image, again) and torch.equal(mask, mask_again)
        assert not torch.equal(image, ds[(i, 1)][0]), "every epoch is new"
    rejects = {whites[0].filename}
    assert whites[0] not in gs.white_mask_records(root, records, split["train"], rejects=rejects), "a rejected mask is never a target"
    with pytest.raises(gs.ExperimentError, match="no training data"):
        gs.SegmenterDataset(root, [], None, size=TINY, n_samples=10)


def test_validation_sets_use_only_val_images(gs, method_root):
    root, records = method_root
    composites, white = gs.build_seg_val_sets(root, 0, records, TINY, n_composites=6)
    val = set(gs.load_split(root, 0)["val"])
    assert len(composites) == 6 and len(white) > 0
    assert set(white.names) <= val
    for name in composites.names:
        leaf, background = name.removeprefix("composite:").split("+")
        assert leaf in val and background in val
    assert composites.images.shape[1:] == (3, *TINY) and composites.masks.any()
    with pytest.raises(gs.CompositeLeakError):
        gs.CompositePool(root, 0, records, part="val").check_name(next(r for r in records if r.filename in gs.load_split(root, 0)["train"]))


# ----------------------------------------------------------------------------- S-seg runs and E4-B


CHOICES = {"input_mode": "rect", "backbone": "resnet50", "lr": {"resnet50": 1e-4}}


@pytest.fixture
def chosen_root(gs, method_root):
    root, records = method_root
    gs.write_json(gs.choices_path(root), CHOICES, indent=2)
    return root, records


@pytest.fixture(scope="module")
def seg_fast_base(method_base, tmp_path_factory):
    """method_base plus choices.json and one finished `run --exp S-seg --splits 0 --fast` (built once per module; it is the
    slowest step of these tests). Returns (root, the captured stdout of that run)."""
    import contextlib
    import io
    import shutil

    from conftest import load_module

    gs = load_module("group3_starvenus_segmentation", REPO_ROOT / "group3-starvenus.py")
    root = tmp_path_factory.mktemp("seg") / "root"
    shutil.copytree(method_base[0], root)
    gs.write_json(gs.choices_path(root), CHOICES, indent=2)
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        assert run_cli(gs, root, "--exp", "S-seg", "--splits", "0", "--fast") == 0
    return root, stdout.getvalue()


@pytest.fixture
def seg_fast_root(gs, seg_fast_base, tmp_path):
    """A private copy of `seg_fast_base`."""
    import shutil

    root = tmp_path / "root"
    shutil.copytree(seg_fast_base[0], root)
    return root, gs.load_index(root)


def test_s_seg_fast_run_writes_the_run_folder_and_boxes_for_every_image(gs, seg_fast_base, seg_fast_root, capsys):
    root, records = seg_fast_root
    out = seg_fast_base[1]
    assert "never a result" in out and "summary (segmenter" in out
    run = root / "_work" / "runs" / "scratch" / "S-seg_fast" / "split_0"
    for name in ("config.json", "env.json", "history.csv", "metrics.json", "best.pt", "boxes.json", "seg_metrics.json"):
        assert (run / name).is_file(), name
    metrics = json.loads((run / "metrics.json").read_text())
    assert metrics["kind"] == "segmenter" and metrics["fast"] is True and metrics["n_boxes"] == len(records)
    assert metrics["n_composites_per_epoch"] == 12 and metrics["n_train_per_epoch"] == 24
    boxes = json.loads((run / "boxes.json").read_text())
    assert set(boxes["images"]) == {r.filename for r in records} and boxes["box_recipe"] == gs.BOX_RECIPE
    assert metrics["boxes_sha256"] == gs.file_sha256(run / "boxes.json")
    assert {d: c["n"] for d, c in boxes["fallbacks"].items()} == {"white": 60, "field": 60}
    seg_metrics = json.loads((run / "seg_metrics.json").read_text())
    assert "dev" not in seg_metrics and "eval" not in seg_metrics, "training never looks at the annotations"
    checkpoint = torch.load(run / "best.pt", map_location="cpu", weights_only=True)
    assert checkpoint["arch"] == "lraspp_mobilenet_v3_large" and checkpoint["size_div"] == 4
    assert not (root / "_work" / "runs" / "S-seg").exists()
    assert run_cli(gs, root, "--exp", "S-seg", "--splits", "0", "--fast") == 0
    assert "skipped" in capsys.readouterr().out


def test_s_seg_fingerprint_follows_the_reject_list_and_only_changes_segmenter_and_method_b_rows(gs, chosen_root):
    root, _ = chosen_root
    seg = gs.EXPERIMENTS["S-seg"]
    before = gs.expected_fingerprint(seg, None, root)
    gs.write_text_atomic(gs.white_rejects_path(root), "bs_wb_0.jpg\n")
    assert gs.expected_fingerprint(seg, None, root) != before, "a rejected leaf is no longer a target: retrain"
    plain = gs.resolve_experiment("E0-rect", gs.load_choices(root)).config
    assert gs.seg_fingerprint_extra(plain, root) == {}
    b = gs.resolve_experiment("E4-B", gs.load_choices(root)).config
    assert gs.seg_fingerprint_extra(b, root) == {"seg_crop": {"recipe": gs.BOX_RECIPE}}


def test_e4_b_crops_by_the_stored_boxes_and_goes_stale_when_they_change(gs, seg_fast_root, capsys):
    root, records = seg_fast_root
    assert run_cli(gs, root, "--exp", "E4-B", "--splits", "0", "--fast") == 1
    err = capsys.readouterr().err
    assert "boxes.json does not exist" in err and "run --exp S-seg --splits 0" in err
    seg_dir = root / "_work" / "runs" / "scratch" / "S-seg_fast"
    assert run_cli(gs, root, "--exp", "E4-B", "--splits", "0", "--fast", "--seg-dir", str(seg_dir)) == 0
    run = root / "_work" / "runs" / "scratch" / "E4-B_fast" / "split_0"
    metrics = json.loads((run / "metrics.json").read_text())
    boxes_file = seg_dir / "split_0" / "boxes.json"
    assert metrics["seg_boxes_sha256"] == gs.file_sha256(boxes_file) and "composites" not in metrics
    capsys.readouterr()
    assert run_cli(gs, root, "--exp", "E4-B", "--splits", "0", "--fast", "--seg-dir", str(seg_dir)) == 0
    assert "skipped" in capsys.readouterr().out
    document = json.loads(boxes_file.read_text())
    first = sorted(document["images"])[0]
    document["images"][first]["box"] = [0.1, 0.1, 0.9, 0.9]
    boxes_file.write_text(json.dumps(document))
    assert run_cli(gs, root, "--exp", "E4-B", "--splits", "0", "--fast", "--seg-dir", str(seg_dir)) == 0
    assert "boxes of this split changed" in capsys.readouterr().out
    # predict: segment, crop, classify
    lines = []
    image = gs.cache_dir(root) / records[0].filename
    probs = gs.predict_image(run, image, "cpu", root, out=lines.append, seg_dir=seg_dir)
    assert probs.shape == (5,) and abs(float(probs.sum()) - 1) < 1e-4
    assert any(line.startswith("segmenter   crop box") for line in lines)
    with pytest.raises(gs.ExperimentError, match="best.pt does not exist"):
        gs.predict_image(run, image, "cpu", root, out=lines.append, seg_dir=root / "nowhere")


# ------------------------------------------------------------------------ metrics and the leakage rule


def test_polygon_metrics(gs):
    square = [[0.25, 0.25], [0.75, 0.25], [0.75, 0.75], [0.25, 0.75]]
    truth = gs.rasterize_polygon(square, (40, 20))
    assert truth.sum() == pytest.approx(20 * 10, abs=40)
    assert gs.iou_dice(truth, truth) == (1.0, 1.0)
    half = truth.copy()
    half[:, :10] = False
    iou, dice = gs.iou_dice(half, truth)
    assert iou == pytest.approx(half.sum() / truth.sum()) and dice == pytest.approx(2 * half.sum() / (half.sum() + truth.sum()))
    assert gs.box_fraction((0, 0, 1, 1), truth) == 1.0 and gs.box_fraction((0, 0, 0.5, 1), truth) == pytest.approx(0.5, abs=0.06)
    results = [{"iou": 0.8, "dice": 0.9, "hit": True, "fallback": False, "ambiguous": False, "crop": [0, 0, 0.5, 0.5]},
               {"iou": 0.0, "dice": 0.0, "hit": True, "fallback": True, "ambiguous": True, "crop": [0, 0, 1, 1]}]
    summary = gs.summarize_annotation_results(results)
    assert summary["all"] == {"n": 2, "iou": 0.4, "dice": 0.45, "hit_rate": 1.0, "box_area": 0.625}
    assert summary["excluding_ambiguous"]["n"] == 1 and summary["fallbacks"] == 1


def test_example_order_shows_the_worst_last(gs):
    results = [{"iou": v, "filename": f"f{i}"} for i, v in enumerate([0.9, 0.1, 0.5, 0.7, 0.0, 0.3, 0.8, 0.6, 0.2, 0.4, 0.95, 0.05])]
    order = gs.example_order(results, n=10, failures=2)
    assert len(order) == 10 == len(set(order)) and [results[i]["iou"] for i in order[-2:]] == [0.05, 0.0]
    assert results[order[0]]["iou"] == 0.95


@pytest.fixture
def annotated_root(gs, method_root, tmp_path):
    """method_root with a 6-image annotation selection (2 dev, 4 eval), polygons, and a finished tiny S-seg split 0."""
    root, records = method_root
    fields = [r for r in records if r.domain == "field"][:6]
    selection = [{"filename": r.filename, "cls": r.cls, "set": "dev" if i < 2 else "eval"} for i, r in enumerate(fields)]
    gs.write_json(gs.selection_path(root), {"format": 1, "images": selection})
    polygon = [[0.35, 0.2], [0.65, 0.2], [0.6, 0.8], [0.4, 0.8]]
    annotations = {r.filename: {"polygon": polygon, "ambiguous": i == 3} for i, r in enumerate(fields)}
    run = gs.split_dir(gs.runs_dir(root) / "S-seg", 0)
    torch.manual_seed(0)
    model = gs.build_segmenter(pretrained=False)
    gs.save_torch_atomic({"state_dict": model.state_dict(), "arch": "lraspp_mobilenet_v3_large", "size_div": 8}, run / "best.pt")
    gs.write_json(run / "metrics.json", {"boxes_sha256": "a" * 64, "config_fingerprint": "f", "best_epoch": 1})
    return root, annotations, tmp_path / "figures"


def test_dev_annotations_can_be_measured_any_time(gs, annotated_root):
    root, annotations, figures = annotated_root
    lines = []
    summaries = gs.run_seg_eval(root, "dev", [0], annotations=annotations, figure=figures / "dev.png", out=lines.append)
    assert summaries[0]["all"]["n"] == 2 and 0 <= summaries[0]["all"]["iou"] <= 1
    record = json.loads((gs.runs_dir(root) / "S-seg" / "split_0" / "seg_metrics.json").read_text())
    assert set(record) == {"dev"} and len(record["dev"]["images"]) == 2 and record["dev"]["input_mode"] == "rect"
    assert (figures / "dev.png").is_file()
    assert any("box has" in line for line in lines), "dev prints per-image results"
    gs.run_seg_eval(root, "dev", [0], annotations=annotations, figure=figures / "dev.png", out=lines.append)  # again: allowed


def test_eval_annotations_need_final_and_are_measured_once(gs, annotated_root, capsys):
    root, annotations, figures = annotated_root
    with pytest.raises(gs.ExperimentError, match="--final"):
        gs.run_seg_eval(root, "eval", [0], annotations=annotations)
    assert not (gs.runs_dir(root) / "S-seg" / "split_0" / "seg_metrics.json").exists()
    summaries = gs.run_seg_eval(root, "eval", [0], final=True, annotations=annotations, figure=figures / "eval.png", out=lambda _: None)
    assert summaries[0]["all"]["n"] == 4 and summaries[0]["excluding_ambiguous"]["n"] == 3
    assert (figures / "eval.png").is_file()
    with pytest.raises(gs.ExperimentError, match="already measured"):
        gs.run_seg_eval(root, "eval", [0], final=True, annotations=annotations)
    gs.run_seg_eval(root, "eval", [0], final=True, again=True, annotations=annotations, figure=figures / "eval.png", out=lambda _: None)
    record = json.loads((gs.runs_dir(root) / "S-seg" / "split_0" / "seg_metrics.json").read_text())
    assert record["eval"]["boxes_sha256"] == "a" * 64 and record["eval"]["summary"]["all"]["n"] == 4
    assert gs.run_cli(["seg-eval", "--data-root", str(root), "--set", "eval", "--splits", "0"]) == 1
    assert "--final" in capsys.readouterr().err


def test_seg_eval_needs_a_trained_segmenter_and_annotations(gs, annotated_root, method_root):
    root, annotations, _ = annotated_root
    with pytest.raises(gs.ExperimentError, match="metrics.json is missing"):
        gs.run_seg_eval(root, "dev", [3], annotations=annotations)
    with pytest.raises(gs.DatasetError, match="annotations do not match the selection"):
        gs.run_seg_eval(root, "dev", [0], annotations={})


def test_seg_arch_is_a_dev_override_of_the_segmenter_only(gs, chosen_root, capsys):
    root, _ = chosen_root
    assert run_cli(gs, root, "--exp", "E0-rect", "--splits", "0", "--fast", "--seg-arch", "deeplabv3_mobilenet_v3_large") == 1
    assert "only applies to the segmenter" in capsys.readouterr().err
    args = gs.build_parser().parse_args(["run", "--data-root", str(root), "--exp", "S-seg", "--seg-arch", "deeplabv3_mobilenet_v3_large", "--epochs", "1"])
    resolved, overrides, limit = gs.apply_run_flags(args, gs.resolve_experiment("S-seg", gs.load_choices(root)), root)
    assert resolved.config.backbone == "deeplabv3_mobilenet_v3_large" and overrides == {"epochs": 1, "seg_arch": "deeplabv3_mobilenet_v3_large"}
    root_dir, name = gs.run_destination(root, args, resolved.config, True)
    assert root_dir == gs.scratch_dir(root) and name == "S-seg_dev"
