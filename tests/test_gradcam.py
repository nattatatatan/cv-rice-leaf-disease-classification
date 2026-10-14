"""Phase 07 T7.5: Grad-CAM (hooks, maps, geometry), the shortcut check on the annotated field images, the figures and the command.

The geometry tests use a tiny network whose map is known (it measures the brightness of the network input), so they prove that a
map lands on the right pixels of the ORIGINAL image under every input mode. One test reads a real retrained checkpoint and is
skipped where the (gitignored) `best.pt` is absent.
"""

import math

import numpy as np
import pytest
import torch
import torchvision
from torch import nn

from conftest import REPO_ROOT

CLASSES = ("Brown Spot", "Leaf Scald", "Rice Blast", "Rice Tungro", "Sheath Blight")


class BrightnessNet(torchvision.models.ResNet):
    """A ResNet by type (so `gradcam_target_layer` picks `layer4`) whose forward is: average-pool the normalised input by 32,
    one 1x1 'layer4' conv that sums the channels, a linear layer that reads that channel for every class. Its Grad-CAM map is
    therefore the brightness of the network input on a 32-pixel grid (ReLU-ed): black is negative, the letterbox colour is 0."""

    def __init__(self):
        super().__init__(torchvision.models.resnet.Bottleneck, [1, 1, 1, 1], num_classes=5)
        self.pool = nn.AvgPool2d(32)
        self.layer4 = nn.Conv2d(3, 4, 1, bias=False)
        self.fc = nn.Linear(4, 5)
        with torch.no_grad():
            self.layer4.weight.zero_()
            self.layer4.weight[0, :, 0, 0] = 1.0
            self.fc.weight.zero_()
            self.fc.weight[:, 0] = 1.0
            self.fc.bias.zero_()

    def forward(self, x):
        return self.fc(self.layer4(self.pool(x)).mean(dim=(2, 3)))


def checkpoint_for(mode: str, size_div: int = 1) -> dict:
    return {"input_mode": mode, "size_div": size_div, "config": {}, "exp_id": "T"}


def bright_square_image(height=300, width=150, top=150, bottom=270, left=100, right=145) -> np.ndarray:
    rgb = np.full((height, width, 3), 20, np.uint8)
    rgb[top:bottom, left:right] = 255
    return rgb


# ---------------------------------------------------------------------------------------------------------- the maps


def test_cam_from_gradients_is_relu_of_the_weighted_activation_sum(gs):
    activation = torch.tensor([[[[1.0, -2.0]], [[3.0, 4.0]]]])  # [1, 2 channels, 1, 2]
    gradient = torch.tensor([[[[1.0, 3.0]], [[-1.0, -1.0]]]])  # channel weights: 2.0 and -1.0
    cam = gs.cam_from_gradients(activation, gradient)
    assert cam.shape == (1, 1, 2)
    assert cam[0, 0].tolist() == [max(0.0, 2 * 1.0 - 3.0), max(0.0, 2 * -2.0 - 4.0)] == [0.0, 0.0]
    cam = gs.cam_from_gradients(activation * torch.tensor([[[[1.0]], [[-1.0]]]]), gradient)  # flip the sign of channel 1
    assert cam[0, 0].tolist() == [5.0, 0.0]


@pytest.mark.parametrize("backbone", ["resnet50", "swin_t"])
def test_grad_cam_matches_an_independent_backward_pass_and_removes_its_hook(gs, backbone):
    torch.manual_seed(0)
    model = gs.build_model(backbone, pretrained=False).eval()
    images = torch.randn(2, 3, 224, 224)
    result = gs.grad_cam(model, images)
    layer = gs.gradcam_target_layer(model)
    assert not layer._forward_hooks and not layer._backward_hooks, "the hook is removed afterwards"
    assert result.cams.shape == (2, 7, 7) and (result.cams >= 0).all()
    assert result.targets.tolist() == result.probs.argmax(axis=1).tolist(), "the predicted class is explained by default"
    assert np.allclose(result.probs.sum(axis=1), 1.0, atol=1e-5)
    # The same thing the textbook way: retain_grad on the layer output, backward on the class logit, per image.
    for i in range(2):
        kept = []
        handle = layer.register_forward_hook(lambda m, inp, out: kept.append(out))
        logits = model(images[i : i + 1])
        handle.remove()
        kept[0].retain_grad()
        logits[0, result.targets[i]].backward()
        activation, gradient = gs.cam_to_nchw(kept[0].detach(), model), gs.cam_to_nchw(kept[0].grad, model)
        expected = torch.relu((gradient.mean(dim=(2, 3), keepdim=True) * activation).sum(dim=1))[0]
        assert np.allclose(result.cams[i], expected.numpy(), rtol=1e-4, atol=1e-6)
    other = (result.targets + 1) % 5
    assert gs.grad_cam(model, images, other).targets.tolist() == other.tolist(), "an explicit class is explained instead"


def test_hook_is_removed_when_the_forward_pass_fails(gs):
    model = gs.build_model("resnet50", pretrained=False).eval()
    with pytest.raises(RuntimeError):
        gs.grad_cam(model, torch.zeros(1, 1, 64, 64))  # one channel: the stem conv rejects it
    assert not gs.gradcam_target_layer(model)._forward_hooks


def test_normalise_cam(gs):
    assert gs.normalise_cam(np.array([[2.0, 4.0], [6.0, 4.0]])).tolist() == [[0.0, 0.5], [1.0, 0.5]]
    assert gs.normalise_cam(np.full((2, 2), 3.0)).sum() == 0.0


# ---------------------------------------------------------------------------------------------------------- geometry


@pytest.mark.parametrize("mode", ["squash", "pad", "rect"])
def test_content_box_is_where_the_transform_puts_the_photo(gs, mode):
    rng = np.random.default_rng(0)
    for shape in ((123, 77, 3), (60, 200, 3), (101, 101, 3)):
        rgb = rng.integers(0, 256, shape, dtype=np.uint8)
        transform = gs.ImageTransform(mode, train=False)
        out = transform(rgb)
        top, left, height, width = gs.content_box(mode, transform.size, shape)
        assert np.array_equal(out[top : top + height, left : left + width], gs.resize_content(rgb, mode, transform.size))
        if mode == "pad":
            covered = np.zeros(out.shape[:2], bool)
            covered[top : top + height, left : left + width] = True
            assert (out[~covered] == np.array(gs.PAD_COLOR)).all(), "everything outside the box is letterbox"
        else:
            assert (top, left, height, width) == (0, 0, *transform.size)


@pytest.mark.parametrize("mode", ["squash", "pad", "rect"])
def test_the_map_lands_on_the_bright_square_of_the_original_image(gs, mode):
    """A 300 x 150 photo with a bright rectangle in the lower right: under every input mode the map's mass must sit on that
    rectangle in the photo's own pixels (`pad` letterboxes the photo, so a map that was not un-done would shift sideways)."""
    rgb = bright_square_image()
    (explanation,) = gs.explain_images(BrightnessNet().eval(), checkpoint_for(mode), [rgb], "cpu")
    cam = explanation.cam
    assert cam.shape == rgb.shape[:2] and (cam >= 0).all() and cam.sum() > 0
    ys, xs = np.mgrid[0 : cam.shape[0], 0 : cam.shape[1]]
    centre_y, centre_x = (cam * ys).sum() / cam.sum(), (cam * xs).sum() / cam.sum()
    assert abs(centre_y - 210) < 8 and abs(centre_x - 122.5) < 8, (centre_y, centre_x)
    near = np.zeros(cam.shape, bool)
    near[150 - 35 : 270 + 35, 100 - 35 : 145 + 35] = True  # the square and one coarse cell around it
    assert cam[near].sum() / cam.sum() > 0.85
    assert near.mean() < 0.5, "chance level is far below the measured share"


def test_a_uniform_image_gives_no_spatial_preference_under_squash(gs):
    (explanation,) = gs.explain_images(BrightnessNet().eval(), checkpoint_for("squash"), [np.full((120, 60, 3), 255, np.uint8)], "cpu")
    assert explanation.cam.std() / explanation.cam.mean() < 0.01


def test_cam_on_image_crops_the_letterbox_bars(gs):
    cam = np.full((20, 20), 2.0, np.float32)  # 16 px cells on a 320 px canvas
    cam[:, :5] = 1.0  # five cells = the 80 px bar on the left of a 320 x 160 photo in a square canvas
    cam[:, 15:] = 1.0  # and on the right
    mapped = gs.cam_on_image(cam, "pad", (320, 320), (320, 160, 3))
    assert mapped.shape == (320, 160) and mapped.max() <= 2.0 + 1e-6
    assert (mapped[:, 8:-8] > 1.99).all(), "the bars are cut away"
    assert mapped.min() >= 1.49, "only the bilinear half-cell at the cut can see a bar"


def test_explain_images_on_swin_agrees_with_classify_rgb_and_batches(gs):
    torch.manual_seed(1)
    model = gs.build_model("swin_t", pretrained=False).eval()
    checkpoint = checkpoint_for("rect", size_div=4)
    rng = np.random.default_rng(2)
    rgbs = [rng.integers(0, 256, (90, 45, 3), dtype=np.uint8), rng.integers(0, 256, (70, 70, 3), dtype=np.uint8), rng.integers(0, 256, (80, 50, 3), dtype=np.uint8)]
    explained = gs.explain_images(model, checkpoint, rgbs, "cpu", batch_size=2)
    for rgb, explanation in zip(rgbs, explained):
        assert explanation.cam.shape == rgb.shape[:2]
        assert np.allclose(explanation.probs, gs.classify_rgb(model, checkpoint, rgb, "cpu"), atol=1e-5)
        assert explanation.target == explanation.predicted
    single = gs.explain_images(model, checkpoint, rgbs[2:], "cpu")[0]
    assert np.allclose(single.cam, explained[2].cam, rtol=1e-4, atol=1e-6), "batching does not change a map"


def test_method_b_models_are_refused(gs):
    with pytest.raises(gs.ExperimentError, match="Method B"):
        gs.explain_images(BrightnessNet().eval(), {**checkpoint_for("rect"), "config": {"seg_crop": True}}, [np.zeros((40, 40, 3), np.uint8)], "cpu")


# ---------------------------------------------------------------------------------------------------------- energy


def test_cam_energy_share(gs):
    cam = np.array([[1.0, 1.0], [2.0, 4.0]], np.float32)
    assert gs.cam_energy_share(cam, np.array([[False, False], [False, True]])) == pytest.approx(0.5)
    assert gs.cam_energy_share(cam, np.ones((2, 2), bool)) == pytest.approx(1.0)
    assert math.isnan(gs.cam_energy_share(np.zeros((2, 2), np.float32), np.ones((2, 2), bool)))
    uniform = np.ones((40, 20), np.float32)
    mask = gs.rasterize_polygon(np.array([[0.25, 0.25], [0.75, 0.25], [0.75, 0.75], [0.25, 0.75]]), (40, 20))
    assert gs.cam_energy_share(uniform, mask) == pytest.approx(mask.mean()), "a uniform map scores exactly the area share"


def make_measurement(gs, pred=0, p=0.9, energy=0.3, area=0.1, reported=True):
    probs = np.full(5, (1 - p) / 4, np.float32)
    probs[pred] = p
    return gs.Measurement(probs, pred, np.ones((4, 4), np.float32), energy, energy, area, reported)


def make_rows(gs, plain_energy, other_energy, parts=None, ambiguous=None, names=("P", "O")):
    rows = []
    for i, (a, b) in enumerate(zip(plain_energy, other_energy)):
        rows.append({"filename": f"img{i // 2}.jpg", "cls": CLASSES[i % 5], "set": "eval", "ambiguous": bool(ambiguous[i]) if ambiguous else False,
                     "split": i % 2, "part": parts[i] if parts else ("test" if i % 2 == 0 else "val"), "area": 0.1,
                     names[0]: make_measurement(gs, energy=a), names[1]: make_measurement(gs, energy=b)})
    return rows


def test_energy_stats_paired_difference_and_nan_handling(gs):
    rows = make_rows(gs, [0.2, 0.4, 0.3, 0.5], [0.3, 0.3, 0.6, float("nan")])
    stats = gs.energy_stats(rows, "P", "O", "energy_pred")
    assert stats["n"] == 3 and stats["images"] == 2, "a pair with a NaN map is left out of every statistic"
    assert stats["diff"][0] == pytest.approx(np.mean([0.1, -0.1, 0.3]))
    assert stats["diff"][1] == pytest.approx(np.std([0.1, -0.1, 0.3], ddof=1))
    assert stats["ahead"] == 2 and stats["area"] == pytest.approx(0.1)
    assert stats["P"][0] == pytest.approx(0.3) and stats["O"][0] == pytest.approx(0.4)


def test_per_image_rows_average_the_splits_of_an_image(gs):
    rows = make_rows(gs, [0.2, 0.4, 0.3, 0.5], [0.3, 0.3, 0.6, 0.5])
    merged = gs.per_image_rows(rows, ("P", "O"))
    assert [r["filename"] for r in merged] == ["img0.jpg", "img1.jpg"]
    assert merged[0]["P"].energy_pred == pytest.approx(0.3) and merged[1]["O"].energy_pred == pytest.approx(0.55)


def test_table_and_csv_have_one_row_per_subset_and_per_pair(gs):
    rows = make_rows(gs, [0.2, 0.4, 0.3, 0.5, 0.1, 0.2], [0.3, 0.3, 0.6, 0.5, 0.1, 0.3], ambiguous=[0, 0, 1, 0, 0, 0])
    table = gs.table_gradcam(rows, "P", "O")
    assert len(table.rows) == 2 * (len(gs.ENERGY_SUBSETS) + 1)
    all_pairs = table.rows[0]
    assert all_pairs[:3] == ["predicted class", "all pairs", "6 (3 images)"] and all_pairs[3] == "0.100"
    without = next(r for r in table.rows if r[1] == "all pairs, without the ambiguous images")
    assert without[2] == "5 (3 images)"
    assert "O - P (paired)" in table.header and "+- " in all_pairs[4]
    csv_lines = gs.energy_csv(rows, ("P", "O")).strip().split("\n")
    assert len(csv_lines) == 7 and csv_lines[0].startswith("filename,class,set,ambiguous,split,part,leaf_area_share,P_pred,")
    assert csv_lines[1].split(",")[3] == "false" and csv_lines[3].split(",")[3] == "true"


def reading_rows(gs, diffs, names=("P", "O")):
    return make_rows(gs, [0.3] * len(diffs), [0.3 + d for d in diffs], names=names)


def test_the_reading_follows_its_fixed_rule(gs):
    base = [0.02, -0.03, 0.04, -0.01] * 6
    better = gs.gradcam_reading(reading_rows(gs, [d + 0.1 for d in base]), "P", "O")
    worse = gs.gradcam_reading(reading_rows(gs, [d - 0.1 for d in base]), "P", "O")
    same = gs.gradcam_reading(reading_rows(gs, base), "P", "O")
    assert "puts more of its map on the annotated leaf" in better and "motivation of Method A predicts" in better
    assert "puts less of its map" in worse and "does not support it" in worse
    assert "about the same share" in same and "no effect" in same
    assert "same in all five subsets" in better and "proof" in same


def test_findings_block_names_every_number_and_the_device(gs):
    rows = reading_rows(gs, [0.02, -0.03, 0.04, -0.01] * 6, ("E2-swin-U", "E3-A"))
    text = gs.gradcam_findings(rows, "E2-swin-U", "E3-A", "mps")
    for needle in ("24 (image, split) pairs", "mps", "Leaf area share (chance): 0.100", "Plain (E2-swin-U): energy inside 0.300", "Method A (E3-A) ahead in",
                   "Reading:", "48 of 48 pairs checked"):
        assert needle in text, needle
    assert "—" not in text


# ---------------------------------------------------------------------------------------------------------- pairs and picks


@pytest.fixture(scope="module")
def committed_root():
    return REPO_ROOT / "Dhan-Shomadhan"


def test_annotated_pairs_are_the_43_pairs_of_24_images_and_never_training(gs, committed_root):
    pairs = gs.annotated_pairs(committed_root)
    assert len(pairs) == 43 and len({p["filename"] for p in pairs}) == 24
    assert {p["set"] for p in pairs} == {"dev", "eval"}, "both annotation sets count"
    assert {p["part"] for p in pairs} == {"test", "val"}
    for pair in pairs:
        split = gs.load_split(committed_root, pair["split"])
        assert pair["filename"] not in split["train"] and pair["filename"] in split[pair["part"]]
    assert sum(p["part"] == "test" for p in pairs) == 22
    restricted = gs.annotated_pairs(committed_root, splits=(2,))
    assert restricted and {p["split"] for p in restricted} == {2}


def test_select_annotated_examples_is_balanced_and_skips_ambiguous(gs):
    rows = []
    for k, cls in enumerate(CLASSES * 3):
        rows.append({"filename": f"f{k:02d}.jpg", "cls": cls, "set": "eval", "ambiguous": k == 0, "split": 1, "part": "test", "area": 0.1})
    rows.append({"filename": "f99.jpg", "cls": CLASSES[0], "set": "eval", "ambiguous": False, "split": 0, "part": "val", "area": 0.1})
    picked = gs.select_annotated_examples(rows, 7)
    assert [r["cls"] for r in picked] == list(CLASSES) + [CLASSES[0], CLASSES[1]]
    assert all(r["part"] == "test" and not r["ambiguous"] for r in picked) and len({r["filename"] for r in picked}) == 7


def pooled_case(true, tests):
    return {"domain": "field", "true": true, "tests": {k: (CLASSES.index(pred), [0.9 if i == CLASSES.index(pred) else 0.025 for i in range(5)]) for k, pred in tests.items()}}


def test_case_picks_use_the_contact_sheet_selection_and_one_test_split(gs):
    pooled = {"a.jpg": pooled_case("Brown Spot", {2: "Brown Spot", 4: "Brown Spot"}),
              "b.jpg": pooled_case("Leaf Scald", {1: "Rice Blast", 3: "Rice Blast"}),
              "c.jpg": pooled_case("Rice Blast", {0: "Rice Blast"})}
    rows = gs.case_rows(pooled)
    picks = gs.gradcam_case_picks(rows, None)
    assert [(r["filename"], k) for r, k in picks["success"]] == [("a.jpg", 2), ("c.jpg", 0)], "first split where the image was a test image"
    assert [(r["filename"], k) for r, k in picks["failure"]] == [("b.jpg", 1)]
    assert [r["filename"] for r, _ in picks["success"]] == [r["filename"] for r in gs.select_cases(rows, "success")]
    only_4 = gs.gradcam_case_picks(rows, 4)
    assert [(r["filename"], k) for r, k in only_4["success"]] == [("a.jpg", 4)] and only_4["failure"] == []
    tasks = gs.gradcam_tasks(picks, [{"split": 2, "filename": "a.jpg", "cls": "Brown Spot", "part": "test", "polygon": np.zeros((3, 2))}])
    assert tasks[(2, "a.jpg")]["polygon"] is not None and tasks[(1, "b.jpg")]["polygon"] is None and tasks[(1, "b.jpg")]["true"] == 1


# ---------------------------------------------------------------------------------------------------------- checkpoints and command


def test_checkpoint_run_dir_prefers_the_reported_folder_then_retrain_then_override(gs, tmp_path):
    root = tmp_path / "Dhan-Shomadhan"
    choices = gs.Choices(root / "choices.json", {})
    runs = gs.runs_dir(root)
    retrain = gs.split_dir(runs / "retrain" / "E2-swin-U", 3)
    retrain.mkdir(parents=True)
    (retrain / "best.pt").write_bytes(b"x")
    assert gs.checkpoint_run_dir(root, "E2-swin-U", choices, 3) == retrain
    reported = gs.split_dir(runs / "E2-swin-U", 3)
    reported.mkdir(parents=True)
    (reported / "best.pt").write_bytes(b"x")
    assert gs.checkpoint_run_dir(root, "E2-swin-U", choices, 3) == reported
    elsewhere = gs.split_dir(tmp_path / "ckpt" / "E2-swin-U", 3)
    elsewhere.mkdir(parents=True)
    (elsewhere / "best.pt").write_bytes(b"x")
    assert gs.checkpoint_run_dir(root, "E2-swin-U", choices, 3, tmp_path / "ckpt") == elsewhere
    with pytest.raises(gs.ExperimentError, match="no best.pt.*--runs-dir"):
        gs.checkpoint_run_dir(root, "E2-swin-U", choices, 0)
    with pytest.raises(gs.ExperimentError, match="no best.pt"):
        gs.checkpoint_run_dir(root, "E2-swin-U", choices, 3, tmp_path / "nowhere")


def test_gradcam_command_is_wired_and_fails_cleanly(gs, tmp_path, capsys):
    parser = gs.build_parser()
    args = parser.parse_args(["gradcam", "--split", "2", "--runs-dir", "ckpt", "--compare", "E3-A"])
    assert args.exp is None and args.split == 2 and str(args.runs_dir) == "ckpt" and args.compare == "E3-A" and args.handler is gs.cmd_gradcam
    assert parser.parse_args(["gradcam"]).split is None
    code = gs.run_cli(["--data-root", str(tmp_path / "empty"), "gradcam"])
    assert code == gs.EXIT_FAILURE and "gradcam: FAIL" in capsys.readouterr().err
    code = gs.run_cli(["--data-root", str(tmp_path / "empty"), "gradcam", "--exp", "E2-swin-U"])
    assert code == gs.EXIT_FAILURE and "gradcam: FAIL" in capsys.readouterr().err


def test_cam_sheet_is_a_300_dpi_png_of_the_expected_width(gs, tmp_path):
    rng = np.random.default_rng(0)
    cam = rng.random((12, 6)).astype(np.float32)
    items = [{"rgb": rng.integers(0, 256, (200, 100, 3), dtype=np.uint8), "domain": domain, "caption": "x.jpg\nsplit 0", "cams": [cam, cam],
              "labels": ["Brown Spot ->\nBrown Spot (0.90)", "Brown Spot ->\nLeaf Scald (0.50)"], "wrong": [False, True],
              "polygon": np.array([[0.2, 0.2], [0.8, 0.2], [0.5, 0.9]]) if domain == "field" else None} for domain in ("white", "field", "field")]
    path = gs.save_cam_sheet(tmp_path / "sheet.png", items, ["Photo", "A", "B"], "title", "footer " * 40)
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    assert int.from_bytes(data[16:20], "big") == round(5.8 * gs.FIGURE_DPI), "5.8 inch wide at 300 dpi"
    assert gs.blend_cam(items[0]["rgb"], cam, (40, 80)).shape == (80, 40, 3)


# ---------------------------------------------------------------------------------------------------------- a real checkpoint


REAL_CHECKPOINT = REPO_ROOT / "Dhan-Shomadhan" / "_work" / "runs" / "retrain" / "E2-swin-U" / "split_0" / "best.pt"


@pytest.mark.skipif(not REAL_CHECKPOINT.is_file(), reason="the retrained checkpoint (gitignored best.pt) is not here")
def test_real_checkpoint_reproduces_the_reported_predictions_and_the_energy_is_a_share(gs):
    root = REPO_ROOT / "Dhan-Shomadhan"
    choices = gs.load_choices(root)
    entries = [e for e in gs.annotation_entries(root, "eval") if e["filename"] in gs.load_split(root, 0)["test"]][:2]
    assert entries
    tasks = {(0, e["filename"]): {"true": gs.CLASS_NAMES.index(e["cls"]), "part": "test", "polygon": e["polygon"]} for e in entries}
    measured = gs.measure_model(root, choices, "E2-swin-U", tasks, "cpu", out=lambda text: None)
    for key, m in measured.items():
        assert m.reported is True, "the retrained model predicts what the reported run predicted"
        assert 0.0 <= m.energy_pred <= 1.0 and 0.0 <= m.energy_true <= 1.0 and 0.0 < m.area < 0.5
        assert max(m.cam.shape) <= gs.GRADCAM_KEEP_PX and (m.cam >= 0).all()
