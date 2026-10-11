"""Phase 03 T3.3 and download-weights: model builders, parameter groups, Grad-CAM layer, weights enums."""

import pytest
import torch

BACKBONES = ("resnet50", "convnext_tiny", "swin_t")
MODES = ("squash", "pad", "rect")


@pytest.mark.parametrize("backbone", BACKBONES)
@pytest.mark.parametrize("mode", MODES)
def test_forward_pass_for_every_backbone_and_input_mode(gs, backbone, mode):
    model = gs.build_model(backbone, pretrained=False).eval()
    height, width = gs.INPUT_SIZES[mode]
    with torch.no_grad():
        out = model(torch.zeros(2, 3, height, width))
    assert out.shape == (2, 5)


def test_weights_enums_resolve_to_the_documented_members(gs):
    expected = {
        "resnet50": "ResNet50_Weights.IMAGENET1K_V2",
        "convnext_tiny": "ConvNeXt_Tiny_Weights.IMAGENET1K_V1",
        "swin_t": "Swin_T_Weights.IMAGENET1K_V1",
    }
    for backbone, name in expected.items():
        weights = gs.backbone_weights(backbone)
        assert f"{type(weights).__name__}.{weights.name}" == name
        assert weights.url.endswith(".pth")
    seg = gs.torchvision.models.get_weight(gs.SEGMENTER_WEIGHTS)
    assert seg.name == "COCO_WITH_VOC_LABELS_V1"
    assert [row[0] for row in gs.WEIGHT_TABLE] == [*BACKBONES, "lraspp_mobilenet_v3_large"]


@pytest.mark.parametrize("backbone", BACKBONES)
def test_head_is_dropout_plus_linear_and_parameter_groups_partition(gs, backbone):
    model = gs.build_model(backbone, pretrained=False, dropout=0.2)
    head = gs.head_module(model)
    assert isinstance(head[0], torch.nn.Dropout) and head[0].p == 0.2
    assert isinstance(head[1], torch.nn.Linear) and head[1].out_features == 5
    head_ids = {id(p) for p in gs.head_parameters(model)}
    back_ids = {id(p) for p in gs.backbone_parameters(model)}
    assert head_ids and back_ids and not head_ids & back_ids
    assert head_ids | back_ids == {id(p) for p in model.parameters()}


def test_unknown_backbone_is_rejected(gs):
    with pytest.raises(ValueError, match="unknown backbone"):
        gs.build_model("vgg16", pretrained=False)


@pytest.mark.parametrize("backbone", BACKBONES)
def test_gradcam_target_layer_gives_nchw_activations(gs, backbone):
    model = gs.build_model(backbone, pretrained=False).eval()
    captured = []
    handle = gs.gradcam_target_layer(model).register_forward_hook(lambda m, i, o: captured.append(o))
    with torch.no_grad():
        model(torch.zeros(1, 3, 224, 224))
    handle.remove()
    activation = captured[0]
    channels = {"resnet50": 2048, "convnext_tiny": 768, "swin_t": 768}[backbone]
    if backbone == "swin_t":
        assert activation.shape[-1] == channels, "Swin returns NHWC"
    assert gs.cam_to_nchw(activation, model).shape[1] == channels


def test_weight_file_check_uses_the_sha256_prefix_in_the_name(gs, tmp_path):
    import hashlib

    data = b"pretend weights"
    good = tmp_path / f"net-{hashlib.sha256(data).hexdigest()[:8]}.pth"
    good.write_bytes(data)
    bad = tmp_path / "net-00000000.pth"
    bad.write_bytes(data)
    unhashed = tmp_path / "net.pth"
    unhashed.write_bytes(data)
    empty = tmp_path / "empty-12345678.pth"
    empty.write_bytes(b"")
    assert gs.weight_file_ok(good) and gs.weight_file_ok(unhashed)
    assert not gs.weight_file_ok(bad) and not gs.weight_file_ok(empty) and not gs.weight_file_ok(tmp_path / "none.pth")


def test_torch_home_points_into_the_data_root_and_download_is_idempotent(gs, tmp_path, monkeypatch):
    monkeypatch.setenv("TORCH_HOME", "/somewhere/else")
    root = tmp_path / "data"
    calls = []

    class FakeWeights:
        url = "https://example.org/models/fake-net.pth"

        def get_state_dict(self, progress=True, check_hash=True):
            calls.append(1)
            path = gs.weight_checkpoint_path(self)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"weights")

    monkeypatch.setattr(gs, "WEIGHT_TABLE", (("fake", "Fake.V1", "test"),))
    monkeypatch.setattr(gs.torchvision.models, "get_weight", lambda name: FakeWeights())
    lines = []
    first = gs.download_weights(root, out=lines.append)
    again = gs.download_weights(root, out=lines.append)
    assert len(calls) == 1, "the second call must not download again"
    expected = root / "_work" / "weights" / "hub" / "checkpoints" / "fake-net.pth"
    assert first[0]["path"] == again[0]["path"] == str(expected)
    assert first[0]["state"] == "downloaded" and again[0]["state"] == "already present"
    text = "\n".join(lines)
    assert "https://example.org/models/fake-net.pth" in text and str(expected) in text
    assert gs.os.environ["TORCH_HOME"] == str(root / "_work" / "weights")
