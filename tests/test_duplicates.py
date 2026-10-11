"""Phase 02 T2.4: near-duplicate audit."""

import shutil

import numpy as np
import pytest

from conftest import FIELD_DIR, make_jpeg


def textured(seed: int, h: int = 240, w: int = 120) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = rng.integers(0, 256, size=(h // 8 + 1, w // 8 + 1, 3), dtype=np.uint8)
    return np.kron(base, np.ones((8, 8, 1), dtype=np.uint8))[:h, :w]


# ------------------------------------------------------------------ dHash


def test_dhash_is_64_bits_and_deterministic(gs):
    image = textured(1)
    bits = gs.dhash_bits(image)
    assert bits.shape == (64,) and set(np.unique(bits)) <= {0, 1}
    assert np.array_equal(bits, gs.dhash_bits(image.copy()))
    assert len(gs.dhash_hex(bits)) == 16
    assert np.array_equal(gs.hex_to_bits(gs.dhash_hex(bits)), bits)


def test_dhash_is_robust_to_brightness_and_noise_but_not_to_other_images(gs):
    image = textured(1)
    brighter = np.clip(image.astype(np.int16) * 0.9 + 10, 0, 255).astype(np.uint8)
    noisy = np.clip(image + np.random.default_rng(0).integers(-3, 4, image.shape), 0, 255).astype(np.uint8)
    base = gs.dhash_bits(image)
    assert (gs.dhash_bits(brighter) != base).sum() <= 6
    assert (gs.dhash_bits(noisy) != base).sum() <= 6
    others = [(gs.dhash_bits(textured(s)) != base).sum() for s in range(2, 12)]
    assert np.median(others) > 15


def test_hamming_matrix_matches_brute_force(gs):
    bits = np.random.default_rng(0).integers(0, 2, size=(12, 64), dtype=np.uint8)
    dist = gs.hamming_matrix(bits)
    for i in range(12):
        for j in range(12):
            assert dist[i, j] == (bits[i] != bits[j]).sum()


def test_find_near_duplicates_threshold_and_order(gs):
    bits = np.zeros((4, 64), dtype=np.uint8)
    bits[1, :3] = 1  # distance 3 from row 0
    bits[2, :6] = 1  # distance 6 from row 0, 3 from row 1
    bits[3, :7] = 1  # distance 7 from row 0
    assert gs.find_near_duplicates(bits, 6) == [(2, 3, 1), (0, 1, 3), (1, 2, 3), (1, 3, 4), (0, 2, 6)]
    assert gs.find_near_duplicates(bits, 2) == [(2, 3, 1)]


# ------------------------------------------------------------------ feature verification


def test_feature_inliers_separates_shifted_copy_from_unrelated_image(gs):
    import cv2

    image = textured(5, 400, 200)
    shifted = np.ascontiguousarray(image[12:, 8:])
    shifted = cv2.copyMakeBorder(shifted, 0, 12, 0, 8, cv2.BORDER_REFLECT)
    same = gs.feature_inliers(gs.sift_features(image), gs.sift_features(shifted))
    other = gs.feature_inliers(gs.sift_features(image), gs.sift_features(textured(6, 400, 200)))
    assert same >= 30 and other <= 10


def test_feature_inliers_without_keypoints_is_zero(gs):
    flat = np.full((100, 50, 3), 128, dtype=np.uint8)
    assert gs.feature_inliers(gs.sift_features(flat), gs.sift_features(flat)) == 0


# ------------------------------------------------------------------ pairs on a tiny dataset


@pytest.fixture
def cached(gs, tiny_tree):
    """Tiny tree plus an exact copy of bsf_0 (-> distance 0) and a field duplicate of a white image."""
    shutil.copy(tiny_tree / FIELD_DIR / "Browon Spot" / "bsf_0.jpg", tiny_tree / FIELD_DIR / "Browon Spot" / "bsf_copy.jpg")
    records = gs.build_index(tiny_tree, expected_counts=None)
    gs.build_cache(tiny_tree, records, workers=1)
    return tiny_tree, records


def test_duplicate_pairs_finds_the_copy_and_ranks_it_first(gs, cached):
    root, records = cached
    pairs = gs.duplicate_pairs(root, records, gs.load_dhashes(root, records))
    assert pairs[0].pair_id == 1 and pairs[0].hamming == 0
    assert {pairs[0].a.filename, pairs[0].b.filename} == {"bsf_0.jpg", "bsf_copy.jpg"}
    assert [p.pair_id for p in pairs] == list(range(1, len(pairs) + 1))
    keys = [(-p.feature_inliers, p.hamming, p.a.filename, p.b.filename) for p in pairs]
    assert keys == sorted(keys), "review order: most feature inliers first"
    assert all(p.hamming <= 6 for p in pairs)
    stats = gs.duplicate_stats(pairs)
    assert stats["total"] == len(pairs) and stats["by_distance"][0] >= 1
    assert stats["within_domain"] + stats["across_domains"] == stats["total"]


def test_load_dhashes_requires_the_cache(gs, tiny_tree):
    records = gs.build_index(tiny_tree, expected_counts=None)
    with pytest.raises(gs.DatasetError, match="prepare"):
        gs.load_dhashes(tiny_tree, records)


def test_report_csv_and_sheets(gs, cached):
    root, records = cached
    pairs = gs.duplicate_pairs(root, records, gs.load_dhashes(root, records))
    csv_path = gs.write_duplicate_report(root, pairs)
    assert csv_path == root / "_work/results/near_duplicates.csv"
    lines = csv_path.read_text().splitlines()
    assert lines[0].split(",")[:4] == ["pair_id", "hamming", "feature_inliers", "scope"]
    assert len(lines) == len(pairs) + 1
    assert lines[1].split(",")[0] == "1" and "bsf_copy.jpg" in lines[1]

    stale = root / "_work/figures/near_duplicates_99.png"
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_bytes(b"old")
    paths = gs.save_duplicate_sheets(root, pairs, max_pairs=10, per_page=4)
    assert not stale.exists()
    assert [p.name for p in paths] == [f"near_duplicates_{i:02d}.png" for i in range(1, len(paths) + 1)]
    assert len(paths) == -(-min(10, len(pairs)) // 4)
    assert all(p.stat().st_size > 5000 for p in paths)
    assert gs.save_duplicate_sheets(root, [], max_pairs=10) == []
