"""Phase 02 T2.3: resolution cache."""

import json
import sys
import time

import numpy as np
import pytest

from conftest import make_jpeg

LINUX = sys.platform.startswith("linux")


@pytest.fixture
def indexed(gs, tiny_tree):
    return tiny_tree, gs.build_index(tiny_tree, expected_counts=None)


def test_cache_files_and_manifest(gs, indexed):
    from PIL import Image

    root, records = indexed
    make_jpeg(root / "extra" / "sbf_wide.jpg", 200, 100, seed=99)  # landscape source
    records = gs.build_index(root, expected_counts=None)
    stats = gs.build_cache(root, records, workers=1, long_side=64)
    assert (stats.total, stats.built, stats.reused, stats.rotated_landscape) == (13, 13, 0, 9)  # 8 via EXIF 6/8 (stored 40x90 -> upright 90x40), 1 natively
    manifest = json.loads((root / "_work/cache/manifest.json").read_text())
    assert set(manifest) == {r.filename for r in records}
    for record in records:
        path = root / "_work" / "cache" / record.filename
        with Image.open(path) as image:
            assert image.format == "JPEG"
            assert image.getexif().get(274) is None, "the cached pixels are already upright"
            width, height = image.size
        assert height >= width, "cache is portrait"
        assert max(width, height) <= 64
        assert (manifest[record.filename]["width"], manifest[record.filename]["height"]) == (width, height)
        assert manifest[record.filename]["sha1"] == record.sha1
        assert len(manifest[record.filename]["dhash"]) == 16
    wide = manifest["sbf_wide.jpg"]
    assert wide["rotated_landscape"] is True and (wide["width"], wide["height"]) == (32, 64)


def test_cache_never_upscales_and_preserves_pixels_when_small(gs, indexed):
    root, records = indexed
    gs.build_cache(root, records, workers=1)  # default long side 1280 > 90
    assert gs.read_cached_rgb(root, "sbf_0.jpg").shape == (90, 40, 3)


def test_cache_matches_read_rgb_after_resize(gs, indexed):
    root, records = indexed
    gs.build_cache(root, records, workers=1, long_side=45)
    cached = gs.read_cached_rgb(root, "sbf_1.jpg")  # source has EXIF 6
    expected = gs.resize_long_side(gs.read_rgb(root / next(r.rel_path for r in records if r.filename == "sbf_1.jpg")), 45)
    assert cached.shape == expected.shape == (45, 20, 3)
    assert np.abs(cached.astype(int) - expected.astype(int)).mean() < 30  # JPEG round trip only


def test_cache_is_idempotent(gs, indexed):
    root, records = indexed
    gs.build_cache(root, records, workers=1)
    files = sorted((root / "_work/cache").glob("*.jpg"))
    stamps = {p: p.stat().st_mtime_ns for p in files}
    time.sleep(0.02)
    stats = gs.build_cache(root, records, workers=1)
    assert (stats.built, stats.reused) == (0, 12)
    assert {p: p.stat().st_mtime_ns for p in files} == stamps


def test_cache_rebuilds_only_what_changed(gs, indexed):
    root, records = indexed
    gs.build_cache(root, records, workers=1)
    # source file content changes -> new sha1 in the index -> that image is rebuilt
    make_jpeg(root / next(r.rel_path for r in records if r.filename == "bsf_0.jpg"), seed=1234)
    # a cache file disappears -> rebuilt
    (root / "_work/cache/bs_wb_1.jpg").unlink()
    stats = gs.build_cache(root, gs.build_index(root, expected_counts=None), workers=1)
    assert (stats.built, stats.reused) == (2, 10)


def test_manifest_entry_without_dhash_is_rebuilt(gs, indexed):
    root, records = indexed
    gs.build_cache(root, records, workers=1)
    path = root / "_work/cache/manifest.json"
    manifest = json.loads(path.read_text())
    del manifest["sbf_0.jpg"]["dhash"]
    path.write_text(json.dumps(manifest))
    assert gs.build_cache(root, records, workers=1).built == 1


def test_damaged_manifest_means_rebuild(gs, indexed):
    root, records = indexed
    gs.build_cache(root, records, workers=1)
    (root / "_work/cache/manifest.json").write_text("{not json")
    assert gs.build_cache(root, records, workers=1).built == 12


def test_cache_needs_sha1(gs, tiny_tree):
    records = gs.build_index(tiny_tree, expected_counts=None, with_sha1=False)
    with pytest.raises(gs.DatasetError, match="sha1"):
        gs.build_cache(tiny_tree, records, workers=1)


def test_undecodable_source_names_the_file(gs, indexed):
    root, records = indexed
    bad = next(r for r in records if r.filename == "sbf_0.jpg")
    (root / bad.rel_path).write_bytes(b"\xff\xd8garbage")
    records = gs.build_index(root, expected_counts=None)
    with pytest.raises(gs.DatasetError, match="sbf_0.jpg"):
        gs.build_cache(root, records, workers=1)


def test_run_parallel_falls_back_inline_when_pool_is_unsafe(gs, monkeypatch):
    monkeypatch.setattr(gs, "pool_is_safe", lambda: False)
    assert list(gs.run_parallel(abs, [-1, -2, 3], workers=4)) == [1, 2, 3]


@pytest.mark.skipif(not LINUX, reason="fork-based pool test; the spawn path is covered by the smoke test")
def test_process_pool_with_fork(gs, indexed):
    import multiprocessing

    root, records = indexed
    stats = gs.build_cache(root, records, workers=3, mp_context=multiprocessing.get_context("fork"))
    assert stats.built == 12
    assert len(list((root / "_work/cache").glob("*.jpg"))) == 12
