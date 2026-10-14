"""Shared pytest fixtures.

The deliverable ``group3-starvenus.py`` has a hyphen in its name, so it cannot be imported
with a plain ``import``. We load it by path instead, which also guarantees that the tests
exercise the GENERATED file and not the notebooks.
"""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_TOOL_PATH = REPO_ROOT / "tools" / "export_py.py"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None, f"cannot load {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # needed by dataclasses and pickling inside the module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def export_tool() -> ModuleType:
    """The export tool module (tools/ is not a package)."""
    return load_module("export_py", EXPORT_TOOL_PATH)


@pytest.fixture(scope="session")
def group_file(export_tool: ModuleType) -> Path:
    path = REPO_ROOT / f"{export_tool.GROUP_NAME}.py"
    if not path.exists():
        pytest.fail(f"{path.name} is missing; run `python tools/export_py.py` first")
    return path


@pytest.fixture(scope="session")
def gs(group_file: Path) -> ModuleType:
    """The exported module, importable under the valid name ``group3_starvenus``."""
    return load_module("group3_starvenus", group_file)


# ---------------------------------------------------------------------------
# Synthetic dataset helpers (tests only; PIL is allowed here, not in the exported file)
# ---------------------------------------------------------------------------

WHITE_DIR = "White Background "  # sic: trailing space, like the real dataset
FIELD_DIR = "Field Background  "  # sic: two trailing spaces


def make_jpeg(path: Path, width: int = 40, height: int = 90, *, orientation: int = 1, seed: int = 0) -> Path:
    """Write a small random-but-structured JPEG. ``orientation`` is written as the EXIF tag
    (pixels are NOT rotated, exactly like a camera that stores the sensor orientation in EXIF)."""
    import numpy as np
    from PIL import Image

    rng = np.random.default_rng(seed)
    base = rng.integers(0, 256, size=(height // 10 + 1, width // 10 + 1, 3), dtype=np.uint8)
    pixels = np.kron(base, np.ones((10, 10, 1), dtype=np.uint8))[:height, :width]  # blocky: survives JPEG
    image = Image.fromarray(pixels)
    exif = Image.Exif()
    if orientation != 1:
        exif[274] = orientation
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "JPEG", quality=95, exif=exif)
    return path


@pytest.fixture
def tiny_tree(tmp_path: Path) -> Path:
    """A 3-image-per-class tree in the real layout, with the real folder-name typos."""
    root = tmp_path / "Dhan-Shomadhan"
    layout = [
        (WHITE_DIR, "Brown Spot", ["bs_wb_"]),
        (WHITE_DIR, "Shath Blight", ["sb_wb_"]),
        (FIELD_DIR, "Browon Spot", ["bsf_"]),
        (FIELD_DIR, "Sheath Blight", ["sbf_"]),
    ]
    seed = 0
    for top, folder, prefixes in layout:
        for prefix in prefixes:
            for i in range(3):
                seed += 1
                make_jpeg(root / top / folder / f"{prefix}{i}.jpg", orientation=[1, 6, 8][i], seed=seed)
    return root


def make_cache(gs, root, n=8, size=(260, 120)):
    """Write ``n`` random blocky portrait JPEGs into <root>/_work/cache and return matching Records."""
    import numpy as np

    records = []
    prefixes = {(c, d): p for p, c, d, _ in gs.LABEL_TABLE}
    for i in range(n):
        cls, domain = gs.CLASS_NAMES[i % 5], gs.DOMAINS[i % 2]
        name = f"{prefixes[(cls, domain)]}{i}.jpg"
        rng = np.random.default_rng(i)
        blocks = rng.integers(0, 256, size=(size[0] // 20, size[1] // 20, 3), dtype=np.uint8)
        rgb = np.kron(blocks, np.ones((20, 20, 1), dtype=np.uint8))
        gs.write_bytes_atomic(gs.cache_dir(root) / name, gs.encode_jpeg(rgb, 95))
        records.append(gs.Record(name, f"x/{name}", cls, gs.CLASS_NAMES.index(cls), domain, 1, ""))
    return records


# ---------------------------------------------------------------------------
# Guard: no test may write to the real data root (the committed results are frozen)
# ---------------------------------------------------------------------------

REAL_DATA_ROOT = REPO_ROOT / "Dhan-Shomadhan"
GUARDED_PATHS = ("index.json", "splits", "results", "runs", "figures", "annotations/selection.json")


def snapshot_real_results() -> dict:
    """(size, mtime) of every committed result file under the real data root (scratch runs are not results)."""
    work = REAL_DATA_ROOT / "_work"
    state = {}
    for name in GUARDED_PATHS:
        base = work / name
        for path in ([base] if base.is_file() else sorted(base.rglob("*")) if base.is_dir() else []):
            if path.is_file() and "scratch" not in path.relative_to(work).parts:
                stat = path.stat()
                state[str(path.relative_to(work))] = (stat.st_size, stat.st_mtime_ns)
    return state


@pytest.fixture(scope="session", autouse=True)
def real_data_root_is_not_written():
    """Fails the session if any test (or the code under test) created, changed or deleted a file of the frozen results."""
    before = snapshot_real_results()
    yield
    after = snapshot_real_results()
    changed = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
    assert not changed, f"the tests wrote to the real data root {REAL_DATA_ROOT}: {changed[:10]}"
