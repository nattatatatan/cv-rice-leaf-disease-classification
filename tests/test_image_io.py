"""Phase 02 T2.2: EXIF-correct image IO."""

from pathlib import Path

import numpy as np
import pytest

from conftest import REPO_ROOT, make_jpeg

DATASET = REPO_ROOT / "Dhan-Shomadhan"


def pil_reference(path: Path) -> np.ndarray:
    """PIL's answer: EXIF applied, then landscape turned clockwise."""
    from PIL import Image, ImageOps

    with Image.open(path) as image:
        rgb = np.asarray(ImageOps.exif_transpose(image).convert("RGB"))
    return np.rot90(rgb, -1) if rgb.shape[1] > rgb.shape[0] else rgb


@pytest.mark.parametrize("orientation", range(1, 9))
@pytest.mark.parametrize("shape", [(40, 90), (90, 40)])
def test_read_rgb_matches_pil_for_every_orientation(gs, tmp_path, orientation, shape):
    path = make_jpeg(tmp_path / "a.jpg", *shape, orientation=orientation, seed=orientation)
    ours = gs.read_rgb(path)
    assert ours.dtype == np.uint8 and ours.ndim == 3 and ours.shape[2] == 3
    assert ours.shape[0] >= ours.shape[1], "always portrait"
    np.testing.assert_array_equal(ours, pil_reference(path))


def test_landscape_is_rotated_clockwise(gs, tmp_path):
    from PIL import Image

    pixels = np.zeros((40, 90, 3), dtype=np.uint8)
    pixels[:, :10] = 255  # white block at the LEFT edge of a landscape image
    Image.fromarray(pixels).save(tmp_path / "l.jpg", quality=100)
    out = gs.read_rgb(tmp_path / "l.jpg")
    assert out.shape[:2] == (90, 40)
    assert out[:10].mean() > 200 and out[10:].mean() < 60, "after a clockwise turn the left edge is on top"


def test_read_rgb_through_trailing_space_folders(gs, tiny_tree):
    record = next(r for r in gs.build_index(tiny_tree, expected_counts=None) if r.filename == "sbf_1.jpg")
    assert " " in record.rel_path.split("/")[0][-1:]
    assert gs.read_rgb(tiny_tree / record.rel_path).shape == (90, 40, 3)


def test_read_rgb_non_ascii_path(gs, tmp_path):
    path = make_jpeg(tmp_path / "caf\u00e9 \u30c6\u30b9\u30c8" / "a.jpg")
    assert gs.read_rgb(path).shape == (90, 40, 3)


def test_read_rgb_undecodable_file_raises(gs, tmp_path):
    (tmp_path / "bad.jpg").write_bytes(b"\xff\xd8garbage")
    with pytest.raises(gs.DatasetError, match="bad.jpg"):
        gs.read_rgb(tmp_path / "bad.jpg")


@pytest.mark.skipif(not DATASET.is_dir(), reason="dataset not present")
@pytest.mark.parametrize(("name", "orientation", "portrait_shape"), [
    ("sbf_30.jpg", 6, (3264, 1536)),
    ("bsf_0.jpg", 8, (4160, 1952)),
    ("rt_wb_95.jpg", 3, (4160, 1952)),
])
def test_real_images_match_pil_and_opencv_default(gs, name, orientation, portrait_shape):
    import cv2

    path = next((p for p in gs.find_images(DATASET) if p.name == name), None)
    if path is None:
        pytest.skip(f"{name} not in this copy of the dataset")
    assert gs.parse_exif_orientation(path.read_bytes()[:131072]) == orientation
    ours = gs.read_rgb(path)
    assert ours.shape[:2] == portrait_shape
    np.testing.assert_array_equal(ours, pil_reference(path))
    # OpenCV 4.12 honours EXIF by default for imread and imdecode: same pixels as our explicit transpose.
    default = cv2.cvtColor(cv2.imread(str(path), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    np.testing.assert_array_equal(ours, np.rot90(default, -1) if default.shape[1] > default.shape[0] else default)
