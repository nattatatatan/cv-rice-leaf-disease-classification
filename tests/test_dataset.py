"""Phase 03 T3.2: LeafDataset, input modes, augmentation, determinism, hooks."""

import multiprocessing

import numpy as np
import pytest
import torch

from conftest import make_cache


@pytest.fixture
def cached(gs, tmp_path):
    root = tmp_path / "root"
    return root, make_cache(gs, root)


@pytest.mark.parametrize("mode,shape", [("squash", (320, 320)), ("pad", (320, 320)), ("rect", (448, 224))])
@pytest.mark.parametrize("train", [False, True])
def test_output_shape_dtype_for_all_modes(gs, cached, mode, shape, train):
    root, records = cached
    ds = gs.LeafDataset(root, records, gs.ImageTransform(mode, train=train), seed=3)
    image, label, index = ds[1]
    assert image.shape == (3, *shape) and image.dtype == torch.uint8
    assert label == records[1].cls_idx and index == 1


def test_size_div_shrinks_every_mode(gs):
    assert gs.input_size("rect", 4) == (112, 56)
    assert gs.input_size("squash", 4) == (80, 80)


def test_pad_mode_keeps_aspect_and_uses_the_imagenet_mean(gs):
    white = np.full((200, 90, 3), 255, dtype=np.uint8)  # tall leaf-like image, aspect 0.45
    out = gs.ImageTransform("pad")(white)
    assert out.shape == (320, 320, 3)
    inside = np.all(out == 255, axis=(0, 2))  # columns that carry image content
    columns = np.flatnonzero(inside)
    width = columns[-1] - columns[0] + 1
    assert columns[0] == (320 - width) // 2 and abs(width - 144) <= 1  # 90 * 320/200
    assert np.all(out[:, 0] == gs.PAD_COLOR) and np.all(out[:, -1] == gs.PAD_COLOR)
    rows = np.flatnonzero(np.any(out == 255, axis=(1, 2)))
    assert rows[0] == 0 and rows[-1] == 319, "the image fills the box vertically"


def test_squash_and_rect_are_plain_resizes_at_eval(gs):
    import cv2

    big = np.random.default_rng(0).integers(0, 256, size=(600, 280, 3), dtype=np.uint8)
    assert np.array_equal(gs.ImageTransform("squash")(big), cv2.resize(big, (320, 320), interpolation=cv2.INTER_AREA))
    assert np.array_equal(gs.ImageTransform("rect")(big), cv2.resize(big, (224, 448), interpolation=cv2.INTER_AREA))
    small = big[:300, :140]  # enlarging uses bilinear interpolation
    assert np.array_equal(gs.ImageTransform("rect")(small), cv2.resize(small, (224, 448), interpolation=cv2.INTER_LINEAR))


def test_eval_transform_is_deterministic_and_needs_no_rng(gs, cached):
    root, records = cached
    ds = gs.LeafDataset(root, records, gs.ImageTransform("rect"), seed=1)
    assert torch.equal(ds[2][0], ds[(2, 7)][0])


def test_train_augmentation_is_a_pure_function_of_seed_epoch_index(gs, cached):
    root, records = cached
    make = lambda seed: gs.LeafDataset(root, records, gs.ImageTransform("rect", train=True), seed=seed)
    a, b = make(5), make(5)
    first = a[(3, 0)][0]
    _ = [a[(i, 0)] for i in (7, 1, 0)]  # access order and other samples do not matter
    assert torch.equal(first, b[(3, 0)][0])
    assert torch.equal(first, a[(3, 0)][0])
    assert not torch.equal(first, a[(3, 1)][0]), "a new epoch draws new augmentation"
    assert not torch.equal(first, make(6)[(3, 0)][0]), "a new seed draws new augmentation"
    assert not torch.equal(first, a[(4, 0)][0])


def test_random_crop_covers_60_to_100_percent_at_the_images_aspect(gs):
    rgb = np.zeros((400, 180, 3), dtype=np.uint8)
    areas = []
    for i in range(300):
        crop = gs.random_crop(rgb, np.random.default_rng(i))
        areas.append(crop.shape[0] * crop.shape[1] / (400 * 180))
        assert abs(crop.shape[1] / crop.shape[0] - 180 / 400) < 0.02
    assert 0.595 <= min(areas) and max(areas) <= 1.0 and max(areas) - min(areas) > 0.2


def test_flips_are_half_and_half_and_independent(gs):
    ramp = np.arange(12, dtype=np.uint8).reshape(3, 4, 1).repeat(3, axis=2)
    seen = {(False, False): 0, (True, False): 0, (False, True): 0, (True, True): 0}
    for i in range(2000):
        out = gs.random_flips(ramp, np.random.default_rng([7, 0, i]))
        corner = out[0, 0, 0]  # 0 untouched, 3 mirrored left-right, 8 mirrored top-bottom, 11 both
        seen[(corner in (3, 11), corner in (8, 11))] += 1
    assert all(420 <= count <= 580 for count in seen.values()), seen


def test_rotation_stays_within_15_degrees_and_reflects_borders(gs):
    rgb = np.random.default_rng(0).integers(0, 256, size=(120, 60, 3), dtype=np.uint8)
    out = gs.random_rotation(rgb, np.random.default_rng(4))
    assert out.shape == rgb.shape
    assert not np.any(np.all(out == 0, axis=2)), "reflected borders, no black corners"


def test_colour_jitter_changes_hue_only_slightly(gs):
    import cv2

    patch = np.zeros((16, 16, 3), dtype=np.uint8)
    patch[:] = (200, 120, 40)  # orange, like a Tungro leaf
    base_hue = int(cv2.cvtColor(patch, cv2.COLOR_RGB2HSV_FULL)[0, 0, 0]) * 360 / 256
    for i in range(60):
        out = gs.color_jitter(patch, np.random.default_rng(i))
        hue = int(cv2.cvtColor(out, cv2.COLOR_RGB2HSV_FULL)[0, 0, 0]) * 360 / 256
        delta = abs((hue - base_hue + 180) % 360 - 180)
        assert delta < 8.5, f"hue moved by {delta} degrees"  # 0.02 * 360 = 7.2 plus rounding
        assert out.dtype == np.uint8


def test_normalize_batch_maps_the_pad_colour_to_zero_and_uses_imagenet_stats(gs):
    batch = torch.zeros(2, 3, 4, 4, dtype=torch.uint8)
    for c, value in enumerate(gs.PAD_COLOR):
        batch[:, c] = value
    assert torch.allclose(gs.normalize_batch(batch, "cpu"), torch.zeros(2, 3, 4, 4), atol=0.01)
    ones = torch.full((1, 3, 2, 2), 255, dtype=torch.uint8)
    expected = torch.tensor([(1 - m) / s for m, s in zip(gs.IMAGENET_MEAN, gs.IMAGENET_STD)]).view(1, 3, 1, 1)
    assert torch.allclose(gs.normalize_batch(ones, "cpu"), expected.expand(1, 3, 2, 2))


def test_epoch_sampler_is_a_function_of_seed_and_epoch(gs):
    s1, s2 = gs.EpochSampler(20, 3), gs.EpochSampler(20, 3)
    assert list(s1) == list(s2) and sorted(i for i, _ in s1) == list(range(20))
    s2.set_epoch(1)
    assert list(s1) != list(s2) and {e for _, e in s2} == {1}


@pytest.mark.skipif("fork" not in multiprocessing.get_all_start_methods(), reason="needs the fork start method")
@pytest.mark.filterwarnings("ignore:This process.*fork")
def test_workers_give_the_same_batches_as_the_main_process(gs, cached):
    root, records = cached
    ds = gs.LeafDataset(root, records, gs.ImageTransform("rect", train=True, size_div=4), seed=9)

    def epoch_batches(workers, sampler, loader, epoch):
        sampler.set_epoch(epoch)
        return [x for x, _, _ in loader]

    sampler0 = gs.EpochSampler(len(ds), 9)
    inline = gs.make_loader(ds, 3, sampler=sampler0, num_workers=0)
    sampler2 = gs.EpochSampler(len(ds), 9)
    pooled = gs.make_loader(ds, 3, sampler=sampler2, num_workers=2, mp_context="fork")
    for epoch in (0, 1):  # persistent workers must see the new epoch through the sampler
        a = epoch_batches(0, sampler0, inline, epoch)
        b = epoch_batches(2, sampler2, pooled, epoch)
        assert len(a) == len(b) == 3 and all(torch.equal(x, y) for x, y in zip(a, b))
    assert not torch.equal(epoch_batches(0, sampler0, inline, 0)[0], epoch_batches(0, sampler0, inline, 1)[0])


class DummySource:
    def __init__(self, n):
        self.n = n

    def __len__(self):
        return self.n

    def load(self, index, epoch):
        return np.full((100, 50, 3), 10 * index + epoch, dtype=np.uint8), 4, f"composite-{index}"


def test_extra_sources_are_appended_and_augmented(gs, cached):
    root, records = cached
    ds = gs.LeafDataset(root, records, gs.ImageTransform("squash", train=True, size_div=4), seed=1,
                        extra_sources=(DummySource(3), DummySource(2)))
    assert len(ds) == len(records) + 5
    image, label, index = ds[len(records) + 1]
    assert label == 4 and image.shape == (3, 80, 80)
    assert ds.load_raw(len(records) + 3, epoch=2)[2] == "composite-0"  # second source starts at its own 0
    assert ds.load_raw(len(records) + 4, epoch=2)[0][0, 0, 0] == 12
    with pytest.raises(IndexError):
        ds[len(ds)]


def test_input_hook_sees_real_images_and_records_only(gs, cached):
    root, records = cached
    calls = []

    def hook(image, record):
        calls.append(record.filename)
        return image[:100]  # e.g. a crop

    ds = gs.LeafDataset(root, records, gs.ImageTransform("pad", size_div=4), input_hook=hook,
                        extra_sources=(DummySource(1),))
    ds[0], ds[len(records)]
    assert calls == [records[0].filename]
    assert ds.load_raw(0)[0].shape[0] == 100


def test_select_and_subsample_records(gs):
    records = gs.synthetic_records(per_stratum=6)
    names = [r.filename for r in records]
    white = gs.select_records(records, names[::-1], domains=("white",))
    assert [r.filename for r in white] == [n for n in names[::-1] if gs.classify_filename(n)[1] == "white"]
    small = gs.subsample_records(records, 20)
    assert len(small) == 20 and len({r.stratum for r in small}) == 10
    assert [r.filename for r in small] == [r.filename for r in gs.subsample_records(records, 20)]
    with pytest.raises(gs.DatasetError, match="not in the index"):
        gs.select_records(records, ["nope.jpg"])


@pytest.mark.parametrize("cores,expected", [(1, 1), (2, 2), (3, 2), (4, 3), (8, 4), (64, 4)])
def test_default_workers_use_every_core_on_small_machines(gs, monkeypatch, cores, expected):
    monkeypatch.delattr(gs.os, "sched_getaffinity", raising=False)
    monkeypatch.setattr(gs.os, "cpu_count", lambda: cores)
    assert gs.default_num_workers() == expected
