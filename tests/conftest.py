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
