"""Phase 05 T5.2 / T5.3: the composite generator, its sources, `CompositeSource`, and the Method A plumbing
(fingerprints, choices, sweep and `choose-composites`)."""

import json
import pickle

import cv2
import numpy as np
import pytest

from argparse import Namespace

from test_pseudo_masks import synthetic_leaf

H, W = 640, 300


def field_image(seed, height=H, width=W):
    rng = np.random.default_rng(seed)
    base = rng.integers(60, 200, size=(height // 20, width // 20, 3), dtype=np.uint8)
    base[..., 1] = np.clip(base[..., 1].astype(int) + 40, 0, 255)
    return cv2.resize(base, (width, height), interpolation=cv2.INTER_LINEAR)


@pytest.fixture(scope="module")
def method_base(tmp_path_factory):
    """Built once per module (see `method_root`): 12 white and 12 field images per class (synthetic leaves on grey paper,
    random green fields), their cache, the index, split 0 and the pseudo-masks of the white images."""
    from conftest import REPO_ROOT, load_module

    gs = load_module("group3_starvenus_composites", REPO_ROOT / "group3-starvenus.py")
    root = tmp_path_factory.mktemp("method") / "root"
    prefix = {(c, d): p for p, c, d, _ in gs.LABEL_TABLE}
    records = []
    for cls in gs.CLASS_NAMES:
        for domain in gs.DOMAINS:
            for i in range(12):
                name = f"{prefix[(cls, domain)]}{i}.jpg"
                seed = len(records)
                image = synthetic_leaf(seed=seed)[0] if domain == "white" else field_image(seed)
                gs.write_bytes_atomic(gs.cache_dir(root) / name, gs.encode_jpeg(image, 95))
                records.append(gs.Record(name, f"x/{name}", cls, gs.CLASS_NAMES.index(cls), domain, 1, f"sha{seed}"))
    gs.write_index(root, records)
    gs.write_json(gs.split_path(root, 0), gs.make_split(records, [], 0))
    gs.build_white_masks(root, records, workers=1)
    return root, [(r.filename, r.rel_path, r.cls, r.domain, r.sha1) for r in records]


@pytest.fixture
def method_root(gs, method_base, tmp_path):
    """A private copy of `method_base` for one test (tests write reject lists, runs and choices into it)."""
    import shutil

    base, _ = method_base
    root = tmp_path / "root"
    shutil.copytree(base, root)
    return root, gs.load_index(root)


# -------------------------------------------------------------------------------------- composite_arrays


def sample_arrays(seed=0, **kwargs):
    leaf, truth = synthetic_leaf(seed=seed)
    return leaf, truth, field_image(100 + seed, **kwargs)


def test_composite_shapes_dtypes_and_non_empty_mask(gs):
    leaf, mask, bg = sample_arrays()
    image, out_mask = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0))
    assert image.shape == bg.shape and image.dtype == np.uint8
    assert out_mask.shape == bg.shape[:2] and out_mask.dtype == np.uint8 and set(np.unique(out_mask)) <= {0, 255}
    assert 0.01 < (out_mask > 0).mean() < 0.4
    assert np.abs(image.astype(int) - bg.astype(int)).max() > 20, "the leaf changed pixels"


def test_the_same_seed_gives_the_same_composite_and_another_seed_a_different_one(gs):
    leaf, mask, bg = sample_arrays()
    first = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(5))
    again = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(5))
    other = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(6))
    assert all(np.array_equal(a, b) for a, b in zip(first, again))
    assert not np.array_equal(first[0], other[0])


def test_all_randomness_comes_from_the_generator(gs):
    """Global numpy / random state must not matter (workers are seeded differently)."""
    leaf, mask, bg = sample_arrays()
    first = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(1))
    np.random.seed(123)
    import random

    random.seed(456)
    second = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(1))
    assert np.array_equal(first[0], second[0])


def test_params_follow_the_documented_ranges(gs):
    rng = np.random.default_rng(0)
    draws = [gs.draw_composite_params(rng) for _ in range(500)]
    assert all(0.6 <= p.length_fraction <= 1.0 and 0.2 <= p.base[0] <= 0.8 and 1.0 <= p.base[1] <= 1.12 for p in draws)
    assert all(abs(p.lean_jitter) <= 6 and abs(p.lean_fallback) <= 35 and abs(p.bend) <= 0.08 for p in draws)
    assert all(0 <= p.blur_sigma <= 4 and 0.4 <= p.leaf_sigma <= 1.4 and 1.5 <= p.feather_sigma <= 3 for p in draws)
    assert all(0.7 <= p.l_blend <= 1.0 and 0.65 <= p.contrast <= 0.9 and 0.4 <= p.ab_blend <= 0.7 for p in draws)
    assert all(all(0.97 <= g <= 1.03 for g in p.gains) for p in draws)
    assert 0.2 < np.mean([p.shadow for p in draws]) < 0.4, "shadow with p = 0.3"
    assert gs.draw_composite_params(np.random.default_rng(3)) == gs.draw_composite_params(np.random.default_rng(3))


def fixed_params(gs, **changes):
    base = gs.CompositeParams(length_fraction=0.8, base=(0.5, 1.0), lean_jitter=0.0, lean_fallback=0.0, bend=0.0,
                              blur_sigma=0.0, leaf_sigma=0.0, l_blend=0.7, contrast=1.0, ab_blend=0.5, gains=(1.0, 1.0, 1.0),
                              feather_sigma=2.0, shadow=False, shadow_angle=0.0, shadow_offset=10.0, shadow_sigma=6.0,
                              shadow_strength=0.4)
    return gs.replace(base, **changes)


def test_the_leaf_grows_up_from_its_base_on_the_bottom_edge(gs):
    """v2 step 3: the base sits on (or below) the bottom edge at the drawn x, the leaf rises length x frame height."""
    leaf, mask, bg = sample_arrays()
    bg = np.full_like(bg, 120)  # no texture: the background gives no direction, the fallback lean (0) is used
    for length, base_x in ((0.6, 0.3), (0.8, 0.5), (1.0, 0.7)):
        _, out = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0), fixed_params(gs, length_fraction=length, base=(base_x, 1.0)))
        ys, xs = np.nonzero(out)
        assert ys.max() >= H - 3, "the base touches the bottom edge"
        assert ys.max() - ys.min() + 1 == pytest.approx(min(length, 1.0) * H, rel=0.08), "leaf length is a fraction of the frame height"
        assert xs[ys >= H - 6].mean() == pytest.approx(base_x * W, abs=0.06 * W)
    _, low = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0), fixed_params(gs, length_fraction=0.6, base=(0.5, 1.12)))
    assert np.nonzero(low)[0].min() > H - 0.6 * H, "a base below the frame shows less of the leaf"


def test_the_lean_follows_the_background_leaves(gs):
    """Diagonal stripes leaning 20 degrees left (or right) from the bottom: the straight path along them wins. The base
    sits near the side the stripes lean away from, because a lean that would put the tip outside the frame is never used."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for true, base_x in ((20.0, 0.85), (-20.0, 0.15)):
        lean = np.deg2rad(true)
        phase = (xx * np.cos(lean) - yy * np.sin(lean)) / 14.0  # constant along (-sin, -cos): up and to the left for a positive lean
        bg = np.stack([60 + 50 * (np.sin(phase) > 0)] * 3, axis=-1).astype(np.uint8)
        found, score = gs.follow_background_lean(bg, (base_x * W, H), 0.5 * H, 35.0)
        assert found == pytest.approx(true, abs=5.0) and score > 0.6
    flat, flat_score = gs.follow_background_lean(np.full_like(bg, 120), (0.5 * W, H), 0.8 * H, 35.0)
    assert flat_score < gs.COMPOSITE_LEAN_MIN_SCORE, "a plain background gives no direction"


def test_the_fallback_lean_turns_the_leaf(gs):
    leaf, mask, bg = sample_arrays()
    bg = np.full_like(bg, 120)
    straight = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0), fixed_params(gs, lean_fallback=0.0))[1]
    leaning = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0), fixed_params(gs, lean_fallback=20.0))[1]

    def slope(m):  # dx/dy of the leaf axis; positive lean (counter-clockwise) moves the tip left, i.e. x grows with y
        ys, xs = np.nonzero(m)
        return np.polyfit(ys, xs, 1)[0]

    assert abs(slope(straight)) < 0.1 and slope(leaning) == pytest.approx(np.tan(np.deg2rad(20.0)), abs=0.12)


def test_bend_moves_the_tip_sideways_and_keeps_the_base(gs):
    leaf, mask, bg = sample_arrays()
    bg = np.full_like(bg, 120)
    straight = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0), fixed_params(gs))[1]
    bent = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0), fixed_params(gs, bend=0.08))[1]

    def centre(m, rows):
        ys, xs = np.nonzero(m)
        top = ys.min()
        pick = (ys >= top + rows[0]) & (ys < top + rows[1])
        return xs[pick].mean()

    assert centre(bent, (60, 90)) - centre(straight, (60, 90)) > 0.04 * H, "the upper leaf moves right"
    assert abs(np.nonzero(bent)[1][np.nonzero(bent)[0] >= H - 6].mean() - np.nonzero(straight)[1][np.nonzero(straight)[0] >= H - 6].mean()) < 3


def test_background_outside_the_leaf_is_only_defocused(gs):
    leaf, mask, bg = sample_arrays()
    image, out = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0), fixed_params(gs, blur_sigma=0.0))
    far = cv2.dilate(out, np.ones((61, 61), np.uint8)) == 0
    assert far.any() and np.array_equal(image[far], bg[far]), "step 4 with sigma 0 and no shadow: nothing changes away from the leaf"
    blurred, _ = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0), fixed_params(gs, blur_sigma=4.0))
    assert cv2.Laplacian(blurred[far.astype(bool)].reshape(-1, 1, 3), cv2.CV_64F).var() < cv2.Laplacian(bg[far].reshape(-1, 1, 3), cv2.CV_64F).var()


def test_leaf_brightness_moves_toward_the_background_and_hue_survives(gs):
    leaf, mask, _ = sample_arrays()
    bright = np.full((H, W, 3), (200, 215, 190), np.uint8)

    def mean_l(image, m):
        lab = cv2.cvtColor(image.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
        return float(lab[..., 0][m > 0].mean())

    inner = cv2.erode(mask, np.ones((9, 9), np.uint8))
    before = mean_l(leaf, inner)
    image, out = gs.composite_arrays(leaf, mask, bright, np.random.default_rng(0), fixed_params(gs, l_blend=0.7))
    after = mean_l(image, cv2.erode(out, np.ones((9, 9), np.uint8)))
    background_l = mean_l(bright, np.ones((H, W)))
    assert before < after < background_l, "brighter than the white-photo leaf, still darker than the background"
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)[..., 0][cv2.erode(out, np.ones((9, 9), np.uint8)) > 0]
    assert 25 < np.median(hsv) < 70, "the leaf stays green (OpenCV hue 25-70)"


def test_the_leaf_follows_the_local_light_of_the_vegetation(gs):
    """Left half of the field in shade, right half in sun: the same leaf is darker on the left."""
    leaf, mask, _ = sample_arrays()
    bg = np.empty((H, W, 3), np.uint8)
    bg[:, : W // 2] = (40, 80, 30)
    bg[:, W // 2 :] = (120, 200, 90)

    def leaf_l(base_x):
        image, out = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0), fixed_params(gs, base=(base_x, 1.0), l_blend=1.0))
        lab = cv2.cvtColor(image.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
        return float(lab[..., 0][cv2.erode(out, np.ones((9, 9), np.uint8)) > 0].mean())

    assert leaf_l(0.25) + 15 < leaf_l(0.75)


def test_contrast_softens_the_leaf_detail(gs):
    leaf, mask, bg = sample_arrays()
    bg = np.full_like(bg, 120)

    def detail(contrast):
        image, out = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0), fixed_params(gs, contrast=contrast))
        lab = cv2.cvtColor(image.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
        return float(lab[..., 0][cv2.erode(out, np.ones((15, 15), np.uint8)) > 0].std())

    assert detail(0.65) < 0.8 * detail(1.0)


def test_feathered_edge_is_soft_and_has_no_paper_fringe(gs):
    leaf, mask, _ = sample_arrays()
    bg = np.full((H, W, 3), (90, 60, 40), np.uint8)  # dark brown, so that a light paper fringe would stand out
    image, out = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0), fixed_params(gs, feather_sigma=2.0))
    ring = (cv2.dilate(out, np.ones((9, 9), np.uint8)) > 0) & (cv2.erode(out, np.ones((9, 9), np.uint8)) == 0)
    assert image[ring].max() < 215 and image[ring][:, 0].mean() < 140, "no light paper pixels at the edge"
    grad = np.abs(np.diff(image[H // 2, :, 1].astype(int)))
    assert grad.max() < 60, "an edge ramp, not a step"


def test_paper_inside_a_sloppy_mask_is_cut_away(gs):
    """A mask 10 px too wide on one side (the paper strip v1 pasted, realism check image 14) loses that strip."""
    leaf, mask, _ = sample_arrays()
    sloppy = cv2.dilate(mask, np.ones((1, 21), np.uint8))
    bg = np.full((H, W, 3), (90, 60, 40), np.uint8)
    image, out = gs.composite_arrays(leaf, sloppy, bg, np.random.default_rng(0), fixed_params(gs))
    lab = cv2.cvtColor(image.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
    paper = cv2.cvtColor(np.float32([[[205, 207, 212]]]) / 255, cv2.COLOR_RGB2LAB)[0, 0]
    near_paper = np.linalg.norm(lab - paper, axis=2) < 15
    assert (near_paper & (out > 0)).sum() < 0.002 * (out > 0).sum(), "no paper-coloured pixels inside the pasted leaf"


def test_edge_colours_come_from_inside_the_leaf(gs):
    rgb = np.full((40, 40, 3), 230, np.uint8)
    alpha = np.zeros((40, 40), np.float32)
    alpha[5:35, 10:30] = 1.0
    rgb[8:32, 13:27] = (40, 140, 50)  # the inside (more than 3 px from the edge) is green, the 3 px rim is paper-light
    out = gs.decontaminate_edge(rgb, alpha, 3)
    assert np.array_equal(out[alpha > 0.5].reshape(-1, 3).max(axis=0), [40, 140, 50])
    assert np.array_equal(gs.decontaminate_edge(rgb, alpha, 0), rgb)


def test_the_tip_tapers_and_the_base_runs_out_of_the_frame(gs):
    """A strip cut off at both ends by the white photo (the common case in the dataset)."""
    mask = np.zeros((H, W), np.uint8)
    mask[:, 120:180] = 255
    leaf = np.full((H, W, 3), 205, np.uint8)
    leaf[mask > 0] = (50, 130, 40)
    bg = np.full((H, W, 3), 120, np.uint8)
    _, out = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0), fixed_params(gs, length_fraction=0.7))
    ys, _ = np.nonzero(out)
    widths = [(out[y] > 0).sum() for y in range(ys.min(), ys.max() + 1)]
    assert widths[0] < 0.4 * max(widths), "the tip narrows instead of ending flat"
    assert widths[-1] > 0.5 * max(widths), "the base is not tapered: it continues below the frame"


def test_the_wider_end_becomes_the_base(gs):
    """A wedge (wide at the top of the white photo) is turned so that its wide end is at the bottom of the composite."""
    mask = np.zeros((H, W), np.uint8)
    cv2.fillPoly(mask, [np.array([[100, 40], [200, 40], [152, 600], [148, 600]], np.int32)], 255)
    leaf = np.full((H, W, 3), 205, np.uint8)
    leaf[mask > 0] = (50, 130, 40)
    _, out = gs.composite_arrays(leaf, mask, np.full((H, W, 3), 120, np.uint8), np.random.default_rng(0), fixed_params(gs))
    ys, _ = np.nonzero(out)
    top, bottom = (out[ys.min() + 20] > 0).sum(), (out[ys.max() - 5] > 0).sum()
    assert bottom > 2 * top


def test_shadow_darkens_the_background_next_to_the_leaf_only_when_asked(gs):
    leaf, mask, _ = sample_arrays()
    bg = np.full((H, W, 3), 150, np.uint8)
    off, mask_off = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0), fixed_params(gs, shadow=False))
    on, mask_on = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0), fixed_params(gs, shadow=True, shadow_strength=0.5))
    assert np.array_equal(mask_off, mask_on)
    near = (cv2.dilate(mask_on, np.ones((25, 25), np.uint8)) > 0) & (mask_on == 0)
    assert on[near].mean() < off[near].mean() - 1


def test_half_resolution_composites_are_the_same_picture_at_half_the_size(gs):
    leaf, mask, bg = sample_arrays()
    half = lambda x, flag: cv2.resize(x, None, fx=0.5, fy=0.5, interpolation=flag)  # noqa: E731
    params = gs.draw_composite_params(np.random.default_rng(2))
    full, full_mask = gs.composite_arrays(leaf, mask, bg, np.random.default_rng(0), params)
    small, small_mask = gs.composite_arrays(half(leaf, cv2.INTER_AREA), (half(mask, cv2.INTER_AREA) > 127).astype(np.uint8) * 255,
                                            half(bg, cv2.INTER_AREA), np.random.default_rng(0), params, scale=0.5)
    assert small.shape[:2] == (H // 2, W // 2)
    both = half(full_mask, cv2.INTER_AREA) > 127
    assert (both & (small_mask > 0)).sum() / (both | (small_mask > 0)).sum() > 0.9
    assert np.abs(half(full, cv2.INTER_AREA).astype(int) - small.astype(int)).mean() < 12


def test_an_empty_mask_is_an_error(gs):
    leaf, _, bg = sample_arrays()
    with pytest.raises(gs.DatasetError, match="mask is empty"):
        gs.composite_arrays(leaf, np.zeros((H, W), np.uint8), bg, np.random.default_rng(0))


# ----------------------------------------------------------------------------------------------- pool


def test_pool_uses_only_train_images_of_the_same_class(gs, method_root):
    root, records = method_root
    split = gs.load_split(root, 0)
    pool = gs.CompositePool(root, 0, records, exclusions=set())
    held_out = set(split["val"]) | set(split["test"])
    assert len(pool.white_train) == 40 and len(pool.leaves) == 40
    assert all(r.filename in split["train"] and r.domain == "white" for r in pool.leaves)
    assert all(b.filename in split["train"] and b.domain == "field" and b.cls_idx == cls for cls, group in pool.backgrounds.items() for b in group)
    rng = np.random.default_rng(0)
    for _ in range(600):
        leaf, background = pool.sample(rng)
        assert leaf.filename not in held_out and background.filename not in held_out
        assert leaf.cls == background.cls and leaf.domain == "white" and background.domain == "field"


def test_a_validation_or_test_image_can_never_be_sampled(gs, method_root):
    root, records = method_root
    split = gs.load_split(root, 0)
    pool = gs.CompositePool(root, 0, records, exclusions=set())
    by_name = {r.filename: r for r in records}
    for part in ("val", "test"):
        for name in split[part]:
            record = by_name[name]
            assert name not in {r.filename for r in pool.leaves} and name not in {b.filename for g in pool.backgrounds.values() for b in g}
            with pytest.raises(gs.CompositeLeakError, match="no validation or test image"):
                pool.check_name(record)
    white_val = next(by_name[n] for n in split["val"] if by_name[n].domain == "white")
    field_train = next(b for b in pool.backgrounds[white_val.cls_idx])
    with pytest.raises(gs.CompositeLeakError):
        pool.check_pair(white_val, field_train)
    # even if a held-out image is smuggled into the lists, construction refuses
    class Leaky(gs.CompositePool):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.leaves.append(white_val)
            self.check_name(white_val)

    with pytest.raises(gs.CompositeLeakError):
        Leaky(root, 0, records, exclusions=set())


def test_pairs_must_match_in_class_and_domain_and_skip_rejects_and_annotated_images(gs, method_root):
    root, records = method_root
    pool0 = gs.CompositePool(root, 0, records, exclusions=set())
    leaf = pool0.leaves[0]
    other = next(b for c, g in pool0.backgrounds.items() if c != leaf.cls_idx for b in g)
    with pytest.raises(gs.CompositeLeakError, match="classes differ"):
        pool0.check_pair(leaf, other)
    with pytest.raises(gs.CompositeLeakError, match="differ in class"):
        gs.make_composite(leaf, other, np.random.default_rng(0), data_root=root)
    with pytest.raises(gs.CompositeLeakError, match="white leaf on a field background"):
        pool0.check_pair(pool0.backgrounds[leaf.cls_idx][0], pool0.backgrounds[leaf.cls_idx][1])
    banned = pool0.backgrounds[leaf.cls_idx][0].filename
    pool = gs.CompositePool(root, 0, records, rejects={leaf.filename}, exclusions={banned})
    assert leaf.filename not in {r.filename for r in pool.leaves}, "rejected leaves are never paste sources"
    assert banned not in {b.filename for b in pool.backgrounds[leaf.cls_idx]}, "annotated images are never backgrounds"
    with pytest.raises(gs.CompositeLeakError, match="rejected or annotated"):
        pool.check_pair(leaf, next(b for b in pool0.backgrounds[leaf.cls_idx] if b.filename == banned))


def test_the_pool_reads_the_reject_file_and_excludes_the_annotated_images_and_their_duplicates(gs, method_root, monkeypatch):
    root, records = method_root
    victim = next(r for r in records if r.domain == "white" and r.filename in gs.load_split(root, 0)["train"])
    gs.white_rejects_path(root).write_text(f"{victim.filename}  # shadow\n")
    assert victim.filename not in {r.filename for r in gs.CompositePool(root, 0, records).leaves}
    # the 30 annotated images and their duplicate-group partners come from the real selection on a real-sized index
    real = gs.load_index(gs.Path(__file__).resolve().parent.parent / "Dhan-Shomadhan")
    excluded = gs.annotation_exclusion_set(real)
    selection = {row["filename"] for row in gs.annotation_selection(real)}
    assert selection <= excluded and {"bsf_4.jpg", "rtf_11.jpg"} <= excluded and len(excluded) == 32
    few = [r for r in records if r.domain == "white" or int(r.filename[:-4].split("_")[-1]) < 4]
    assert gs.annotation_exclusion_set(few) == set(), "too few field images to select from: nothing excluded"


def test_a_pool_without_any_leaf_is_an_error(gs, method_root):
    root, records = method_root
    pool = gs.CompositePool(root, 0, records, rejects={r.filename for r in records if r.domain == "white"})
    with pytest.raises(gs.ExperimentError, match="no white leaves"):
        pool.sample(np.random.default_rng(0))
    with pytest.raises(gs.ExperimentError, match="no white training leaf"):
        gs.CompositeSource(root, 0, pool=pool)


def test_make_composite_returns_image_mask_and_the_class_label(gs, method_root):
    root, records = method_root
    pool = gs.CompositePool(root, 0, records, exclusions=set())
    leaf, background = pool.sample(np.random.default_rng(4), 2)
    image, mask, label = gs.make_composite(leaf, background, np.random.default_rng(1), data_root=root)
    assert image.shape == (H, W, 3) and mask.shape == (H, W) and mask.any() and label == 2 == leaf.cls_idx == background.cls_idx
    again = gs.make_composite(leaf, background, np.random.default_rng(1), data_root=root)
    assert np.array_equal(again[0], image) and np.array_equal(again[1], mask)
    small, small_mask, _ = gs.make_composite(leaf, background, np.random.default_rng(1), data_root=root, scale=0.5)
    assert small.shape == (H // 2, W // 2, 3)


# ---------------------------------------------------------------------------------------- CompositeSource


def test_default_length_is_the_white_train_count_and_the_factor_scales_it(gs, method_root):
    root, records = method_root
    assert len(gs.CompositeSource(root, 0)) == 40
    assert len(gs.build_composite_source(root, 0, 0)) == 40
    assert len(gs.build_composite_source(root, 0, 0, n_factor=0.5)) == 20
    assert len(gs.build_composite_source(root, 0, 0, n_factor=1.0, limit=7)) == 7


def test_samples_are_a_function_of_seed_epoch_and_index_only(gs, method_root):
    root, _ = method_root
    a, b = gs.CompositeSource(root, 0, 12, seed=3), gs.CompositeSource(root, 0, 12, seed=3)  # two "workers"
    first = a.load(4, epoch=2)
    assert first[1] in range(5) and first[2].startswith("composite:") and first[0].shape == (H // 2, W // 2, 3)
    for worker in (a, b):
        again = worker.load(4, epoch=2)
        assert np.array_equal(again[0], first[0]) and again[1:] == first[1:]
    assert not np.array_equal(a.load(4, epoch=3)[0], first[0]), "a new epoch brings new variations"
    assert not np.array_equal(a.load(5, epoch=2)[0], first[0])
    assert not np.array_equal(gs.CompositeSource(root, 0, 12, seed=4).load(4, epoch=2)[0], first[0])
    assert a.epoch_seed(2) == 3 * 1000 + 2, "rng seeded with seed * 1000 + epoch"
    with pytest.raises(IndexError):
        a.load(12)


def test_each_leaf_is_used_once_per_epoch_with_a_background_of_its_class(gs, method_root):
    root, _ = method_root
    source = gs.CompositeSource(root, 0, 40, seed=1, pool=gs.CompositePool(root, 0, exclusions=set()))
    pairs = [source.pair(i, 0) for i in range(40)]
    assert sorted(leaf.filename for leaf, _ in pairs) == sorted(r.filename for r in source.pool.leaves)
    assert all(leaf.cls == bg.cls for leaf, bg in pairs)
    assert [p[0].filename for p in pairs] != [source.pair(i, 1)[0].filename for i in range(40)], "the order changes per epoch"
    held_out = set(gs.load_split(root, 0)["val"]) | set(gs.load_split(root, 0)["test"])
    for epoch in range(20):
        for i in range(40):
            leaf, bg = source.pair(i, epoch)
            assert leaf.filename not in held_out and bg.filename not in held_out


def test_the_source_pickles_for_dataloader_workers_and_drops_its_cache(gs, method_root):
    root, _ = method_root
    source = gs.CompositeSource(root, 0, 6, seed=0)
    first = source.load(1, 0)
    assert source._cached > 0
    clone = pickle.loads(pickle.dumps(source))
    assert clone._cached == 0 and clone._leaf_cache == {} and np.array_equal(clone.load(1, 0)[0], first[0])
    tiny = gs.CompositeSource(root, 0, 6, seed=0, cache_mb=0.0)
    tiny.load(1, 0)
    assert tiny._cached == 0, "a full cache stops growing"
    assert np.array_equal(tiny.load(1, 0)[0], first[0]), "the cache is only a speed-up"


def test_composites_pass_through_the_same_training_augmentation_as_real_images(gs, method_root):
    root, records = method_root
    train = gs.select_records(records, gs.load_split(root, 0)["train"])
    source = gs.CompositeSource(root, 0, 10, seed=0)
    transform = gs.ImageTransform("rect", train=True, size_div=4)
    dataset = gs.LeafDataset(root, train, transform, seed=0, extra_sources=(source,))
    assert len(dataset) == len(train) + 10
    image, label, index = dataset[(len(train) + 3, 1)]
    assert tuple(image.shape) == (3, 112, 56) and image.dtype == gs.torch.uint8 and label in range(5) and index == len(train) + 3
    again = dataset[(len(train) + 3, 1)][0]
    assert gs.torch.equal(image, again), "deterministic augmentation"
    assert not gs.torch.equal(image, dataset[(len(train) + 3, 2)][0])


def test_the_cost_of_a_composite_at_half_resolution_is_small(gs, method_root):
    import time

    root, _ = method_root
    source = gs.CompositeSource(root, 0, 30, seed=0)
    for i in range(30):
        source.load(i, 0)  # warm the cache
    start = time.perf_counter()
    for i in range(30):
        source.load(i, 1)
    assert (time.perf_counter() - start) / 30 < 0.5, "far below the budget of a training step"


# ------------------------------------------------------------------------ fingerprints, choices, run


def test_fingerprints_of_non_composite_rows_do_not_change_and_composite_rows_carry_factor_and_recipe(gs):
    choices = gs.Choices(gs.Path("c.json"), {"input_mode": "rect", "backbone": "convnext_tiny", "lr": {"convnext_tiny": 1e-4}})
    plain = gs.resolve_experiment("E2-cnx-U", choices)
    assert gs.composite_fingerprint_extra(plain.config, None) == {} and plain.composite_factor is None
    assert gs.expected_fingerprint(plain.config) == gs.config_fingerprint(plain.config, {"seed_offset": 0, "limit": None})
    a = gs.resolve_experiment("E3-A", choices)
    assert a.composite_factor == 1.0 and any("not chosen yet" in n for n in a.notes) and a.choices_used["composite_n_factor"] == 1.0
    half = gs.resolve_experiment("E3-A", choices, composite_factor=0.5)
    assert half.composite_factor == 0.5 and half.config == a.config
    fingerprints = {gs.expected_fingerprint(r.config, r.composite_factor) for r in (a, half)}
    assert len(fingerprints) == 2, "the factor is part of the fingerprint"
    assert gs.expected_fingerprint(a.config, 1.0) == gs.expected_fingerprint(a.config) == gs.expected_fingerprint(a.config, None)
    extra = gs.composite_fingerprint_extra(a.config, 0.5)["composites"]
    assert extra == {"n_factor": 0.5, "recipe": gs.COMPOSITE_RECIPE}
    wf = gs.resolve_experiment("E3-A-WF", choices)
    assert wf.config.train_domains == ("white",) and wf.composite_factor == 1.0


def test_the_recipe_hash_covers_the_constants(gs, monkeypatch):
    assert len(gs.COMPOSITE_RECIPE) == 12 and gs.COMPOSITE_CONSTANTS["masks"] == gs.MASK_RECIPE
    import hashlib

    changed = dict(gs.COMPOSITE_CONSTANTS, feather=(1.0, 3.0))
    assert hashlib.sha1(json.dumps(changed, sort_keys=True).encode()).hexdigest()[:12] != gs.COMPOSITE_RECIPE


def test_the_chosen_factor_comes_from_choices_json_and_invalid_ones_are_refused(gs):
    base = {"input_mode": "rect", "backbone": "swin_t", "lr": {"swin_t": 3e-4}}
    chosen = gs.Choices(gs.Path("c.json"), {**base, "composite_n_factor": {"value": 0.5, "evidence": {}}})
    resolved = gs.resolve_experiment("E3-A", chosen)
    assert resolved.composite_factor == 0.5 and not resolved.notes and resolved.config.backbone == "swin_t"
    assert gs.resolve_experiment("E3-A", chosen, composite_factor=1.0).composite_factor == 1.0, "the sweep overrides"
    with pytest.raises(gs.ChoicesError, match="composite_n_factor"):
        gs.resolve_experiment("E3-A", gs.Choices(gs.Path("c.json"), {**base, "composite_n_factor": 0.75}))


def run_cli(gs, root, *args):
    return gs.run_cli(["run", "--data-root", str(root), "--device", "cpu", "--num-workers", "0", *args])


@pytest.fixture
def method_run_root(gs, method_root):
    root, records = method_root
    gs.write_json(gs.choices_path(root), {"input_mode": "rect", "backbone": "resnet50", "lr": {"resnet50": 1e-4}}, indent=2)
    return root


def test_fast_run_of_e3_a_trains_on_composites_and_writes_only_to_scratch(gs, method_run_root, capsys):
    root = method_run_root
    assert run_cli(gs, root, "--exp", "E3-A", "--splits", "0", "--fast") == 0
    out = capsys.readouterr().out
    assert "not chosen yet" in out and "never a result" in out
    scratch = root / "_work" / "runs" / "scratch" / "E3-A_fast" / "split_0"
    metrics = json.loads((scratch / "metrics.json").read_text())
    assert metrics["fast"] is True and metrics["composites"]["n_factor"] == 1.0 and metrics["composites"]["scale"] == 0.5
    assert metrics["composites"]["n_per_epoch"] == 24 and metrics["n_train"] == 24 + 24, "24 real images (limit) + 24 composites"
    assert not (root / "_work" / "runs" / "E3-A").exists()
    config = json.loads((scratch / "config.json").read_text())
    assert config["choices_used"]["composite_n_factor"] == 1.0
    assert run_cli(gs, root, "--exp", "E3-A", "--splits", "0", "--fast") == 0
    assert "skipped" in capsys.readouterr().out
    assert run_cli(gs, root, "--exp", "E3-A-WF", "--splits", "0", "--fast") == 0
    assert (root / "_work" / "runs" / "scratch" / "E3-A-WF_fast" / "split_0" / "metrics.json").is_file()


def test_a_real_run_of_e3_a_waits_for_the_backbone_gate(gs, method_root, capsys):
    root, _ = method_root
    assert run_cli(gs, root, "--exp", "E3-A", "--splits", "0") == 1
    err = capsys.readouterr().err
    assert "backbone" in err and "G1" in err


def test_composite_sweep_runs_split_zero_at_both_factors(gs, method_run_root, capsys):
    root = method_run_root
    assert run_cli(gs, root, "--exp", "E3-A", "--sweep-composites", "--splits", "3", "--fast") == 0
    assert "split 0 only" in capsys.readouterr().out
    scratch = root / "_work" / "runs" / "scratch"
    assert sorted(p.name for p in scratch.iterdir()) == ["E3-A_n0.5", "E3-A_n1"]
    half = json.loads((scratch / "E3-A_n0.5" / "split_0" / "metrics.json").read_text())
    assert half["composites"]["n_factor"] == 0.5
    assert run_cli(gs, root, "--exp", "E3-A-WF", "--sweep-composites") == 1
    assert "use --exp E3-A" in capsys.readouterr().err
    assert run_cli(gs, root, "--exp", "E3-A", "--sweep-composites", "--sweep-lr") == 1
    assert "one at a time" in capsys.readouterr().err
    assert gs.run_destination(root, Namespace(out_dir=None, sweep_lr=False, sweep_composites=True, fast=False),
                              gs.resolve_experiment("E3-A", gs.load_choices(root)).config, False, 0.5) == (
        root / "_work" / "runs" / "sweep", "E3-A_n0.5")
    assert gs.run_destination(root, Namespace(out_dir=None, sweep_lr=False, sweep_composites=False, fast=False),
                              gs.resolve_experiment("E3-A", gs.load_choices(root)).config, False) == (root / "_work" / "runs", "E3-A")


def fake_composite_sweep(gs, root, scores=(0.6, 0.7), **overrides):
    """Sweep runs shaped like the real ones, with the fingerprint a real run would write."""
    choices = gs.load_choices(root)
    for factor, score in zip(gs.COMPOSITE_N_FACTORS, scores):
        resolved = gs.resolve_experiment("E3-A", choices, composite_factor=factor)
        fingerprint = gs.expected_fingerprint(resolved.config, factor)
        folder = gs.split_dir(gs.sweep_dir(root) / gs.composite_sweep_run_name("E3-A", factor), 0)
        metrics = {"backbone": "resnet50", "lr": 1e-4, "split_sha256": gs.load_split(root, 0)["sha256"], "fast": False, "overrides": {},
                   "config_fingerprint": fingerprint, "composites": {"n_factor": factor, "n_per_epoch": int(30 * factor)},
                   "val": {"mixed": {"macro_f1": score}}, **overrides}
        gs.write_json(folder / "metrics.json", metrics)
        (folder / "best.pt").write_bytes(b"x")


def test_choose_composites_records_the_better_validation_factor_and_reuses_the_sweep_run(gs, method_run_root, capsys):
    root = method_run_root
    fake_composite_sweep(gs, root, scores=(0.6, 0.7))
    assert gs.run_cli(["choose-composites", "--data-root", str(root)]) == 0
    out = capsys.readouterr().out
    assert "0.5x -> val mixed F1 0.600" in out and "=>  1x" in out and "copied to split 0 of E3-A" in out
    choices = gs.load_choices(root)
    assert choices.get("composite_n_factor") == 1.0
    entry = json.loads(choices.path.read_text())["composite_n_factor"]
    assert entry["evidence"]["val_mixed_macro_f1"] == {"0.5": 0.6, "1": 0.7} and entry["evidence"]["n_per_epoch"] == {"0.5": 15, "1": 30}
    assert "backbone" in json.loads(choices.path.read_text()), "other choices are kept"
    real = root / "_work" / "runs" / "E3-A" / "split_0"
    provenance = json.loads((real / "provenance.json").read_text())
    assert provenance["n_factor"] == 1.0 and provenance["copied_from"] == "sweep/E3-A_n1/split_0"
    resolved = gs.resolve_experiment("E3-A", choices)
    state, _ = gs.result_state(real, gs.load_split(root, 0)["sha256"], gs.expected_fingerprint(resolved.config, resolved.composite_factor))
    assert state == "fresh", "the real run skips split 0"
    # the other way round: 0.5x wins, the factor is recorded and used by every composites experiment
    for run in (gs.runs_dir(root) / "E3-A",):
        import shutil

        shutil.rmtree(run)
    fake_composite_sweep(gs, root, scores=(0.8, 0.7))
    gs.choose_composites(root, out=lambda _: None, force=True)
    choices = gs.load_choices(root)
    assert choices.get("composite_n_factor") == 0.5 and gs.resolve_experiment("E3-A-WF", choices).composite_factor == 0.5
    assert (gs.runs_dir(root) / "E3-A" / "split_0" / "provenance.json").is_file()


def test_choose_composites_with_the_same_factor_as_recorded_keeps_the_entry_and_still_reuses_the_sweep_run(gs, method_run_root):
    root = method_run_root
    gs.write_choice(root, "composite_n_factor", 1.0)
    fake_composite_sweep(gs, root, scores=(0.6, 0.7))
    before = gs.choices_path(root).read_bytes()
    lines = []
    result = gs.choose_composites(root, out=lines.append)
    assert result["outcome"] == "matches" and result["n_factor"] == 1.0 and result["split_0"] == "copied"
    assert gs.choices_path(root).read_bytes() == before
    text = "\n".join(lines)
    assert "matches the recorded one" in text and "written to" not in text and "recorded not recorded" in text and "recomputed 0.700" in text
    assert json.loads((gs.split_dir(gs.runs_dir(root) / "E3-A", 0) / "provenance.json").read_text())["n_factor"] == 1.0


def test_choose_composites_with_another_factor_keeps_the_recorded_one_and_copies_only_its_sweep_run(gs, method_run_root, capsys):
    root = method_run_root
    gs.write_choice(root, "composite_n_factor", 0.5)
    fake_composite_sweep(gs, root, scores=(0.6, 0.7))  # 1x wins, 0.5x is recorded
    for factor in gs.COMPOSITE_N_FACTORS:
        (gs.split_dir(gs.sweep_dir(root) / gs.composite_sweep_run_name("E3-A", factor), 0) / "best.pt").write_bytes(b"x%g" % factor)
    before = gs.choices_path(root).read_bytes()
    lines = []
    result = gs.choose_composites(root, out=lines.append)
    assert result["outcome"] == "differs" and result["n_factor"] == 0.5 and result["recomputed_n_factor"] == 1.0
    assert gs.choices_path(root).read_bytes() == before and gs.load_choices(root).get("composite_n_factor") == 0.5
    text = "\n".join(lines)
    assert "WARNING - the recomputed composite_n_factor = 1.0 differs from the recorded 0.5" in text and "--force overwrites" in text
    real = gs.split_dir(gs.runs_dir(root) / "E3-A", 0)
    assert result["split_0"] == "copied" and (real / "best.pt").read_bytes() == b"x0.5" and "the recorded factor" in lines[-1]
    assert json.loads((real / "provenance.json").read_text())["n_factor"] == 0.5
    resolved = gs.resolve_experiment("E3-A", gs.load_choices(root))
    assert gs.result_state(real, gs.load_split(root, 0)["sha256"], gs.expected_fingerprint(resolved.config, resolved.composite_factor))[0] == "fresh"
    assert gs.run_cli(["choose-composites", "--data-root", str(root)]) == 0, "exit status 0, so that `reproduce` goes on"
    assert "differs from the recorded" in capsys.readouterr().out
    assert gs.run_cli(["choose-composites", "--data-root", str(root), "--force"]) == 0
    assert gs.load_choices(root).get("composite_n_factor") == 1.0


def test_choose_composites_ties_go_to_the_default_and_bad_sweeps_are_refused(gs, method_run_root, capsys):
    root = method_run_root
    with pytest.raises(gs.ExperimentError, match="--sweep-composites"):
        gs.choose_composites(root)
    fake_composite_sweep(gs, root, scores=(0.7, 0.7))
    gs.choose_composites(root, out=lambda _: None)
    assert gs.load_choices(root).get("composite_n_factor") == 1.0
    fake_composite_sweep(gs, root, fast=True)
    with pytest.raises(gs.ExperimentError, match="not a real sweep run"):
        gs.choose_composites(root)
    fake_composite_sweep(gs, root)
    broken = gs.split_dir(gs.sweep_dir(root) / "E3-A_n0.5", 0) / "metrics.json"
    metrics = json.loads(broken.read_text())
    metrics["composites"]["n_factor"] = 1.0
    broken.write_text(json.dumps(metrics))
    with pytest.raises(gs.ExperimentError, match="expected composites per epoch factor 0.5"):
        gs.choose_composites(root)
    assert gs.run_cli(["choose-composites", "--data-root", str(root)]) == 1
    assert "choose-composites: FAIL" in capsys.readouterr().err


def test_a_stale_sweep_run_is_not_reused_and_a_real_split_zero_is_left_alone(gs, method_run_root, capsys):
    root = method_run_root
    fake_composite_sweep(gs, root, scores=(0.6, 0.7), config_fingerprint="0" * 64)
    lines = []
    gs.choose_composites(root, out=lines.append)
    assert "not reused" in lines[-1] and "fingerprint" in lines[-1] and not (gs.runs_dir(root) / "E3-A").exists()
    fake_composite_sweep(gs, root, scores=(0.6, 0.7))
    real = gs.split_dir(gs.runs_dir(root) / "E3-A", 0)
    real.mkdir(parents=True)
    (real / "metrics.json").write_text("{}")
    lines.clear()
    gs.choose_composites(root, out=lines.append)
    assert "already exists" in lines[-1] and (real / "metrics.json").read_text() == "{}"


def test_prepare_composites_writes_both_figures_and_the_key(gs, method_root, monkeypatch):
    root, records = method_root
    monkeypatch.setattr(gs, "annotation_exclusion_set", lambda _records: set())  # the fixture is too small to spare 30 images
    lines = []
    result = gs.prepare_composites(root, records, out=lines.append)
    assert result["examples"].is_file() and result["realism"].is_file() and result["key"].is_file()
    assert "40 usable white leaves" in lines[0]
    skipped = []
    gs.white_masks_manifest_path(root).unlink()
    assert gs.prepare_composites(root, records, out=skipped.append) == {} and "skipped" in skipped[0]


def test_realism_check_mixes_20_composites_with_20_real_images_and_keeps_the_key_out_of_the_figure(gs, method_root, tmp_path):
    root, records = method_root
    pool = gs.CompositePool(root, 0, records, exclusions=set())
    items = gs.realism_items(pool)
    kinds = [i["kind"] for i in items]
    assert len(items) == 40 and kinds.count("composite") == 20 and kinds.count("real") == 20
    assert kinds != sorted(kinds) and kinds != sorted(kinds, reverse=True), "shuffled"
    for cls in gs.CLASS_NAMES:
        assert [i["cls"] for i in items if i["kind"] == "composite"].count(cls) == 4 == [i["cls"] for i in items if i["kind"] == "real"].count(cls)
    used = {i["background"] for i in items if i["kind"] == "composite"}
    assert not used & {i["filename"] for i in items if i["kind"] == "real"}, "a real image is never also a composite background"
    held_out = set(gs.load_split(root, 0)["val"]) | set(gs.load_split(root, 0)["test"])
    assert not held_out & ({i["filename"] for i in items if i["kind"] == "real"} | used | {i["leaf"] for i in items if i["kind"] == "composite"})
    path, key_path = gs.save_realism_check(root, 0, tmp_path / "check.png", tmp_path / "key.json", pool=pool)
    key = json.loads(key_path.read_text())
    assert [e["kind"] for e in key["items"]] == kinds and key["composites"] == 20 and "Do not open" in key["note"]
    assert [e["position"] for e in key["items"]] == list(range(1, 41)) and key["items"][8]["row"] == 2 and key["items"][8]["column"] == 1
    image = cv2.imread(str(path))
    assert image.shape[1] == round(6.4 * 300) and image.shape[0] == round(8.35 * 300)
    text = path.read_bytes()
    for word in (b"composite", b"real", b"Composite"):
        assert word not in text, "no label in the figure file"
    again = gs.save_realism_check(root, 0, tmp_path / "check2.png", tmp_path / "key2.json", pool=pool)
    assert cv2.imread(str(again[0])).tobytes() == image.tobytes() and again[1].read_text() == key_path.read_text()


def test_examples_figure_has_two_composites_per_class(gs, method_root, tmp_path):
    root, records = method_root
    pool = gs.CompositePool(root, 0, records, exclusions=set())
    rows = gs.composite_examples(pool)
    assert [r["cls_idx"] for r in rows] == [c for c in range(5) for _ in range(2)]
    assert all(r["leaf"].cls_idx == r["background"].cls_idx == r["cls_idx"] and r["mask"].any() for r in rows)
    assert all(a["leaf"].filename != b["leaf"].filename for a, b in zip(rows[::2], rows[1::2]))
    path = gs.save_composites_examples(root, 0, tmp_path / "examples.png", pool=pool)
    image = cv2.imread(str(path))
    assert image.shape[1] == round(5.8 * 300) and image.shape[0] == round((1.78 * 5 + 0.3) * 300)
