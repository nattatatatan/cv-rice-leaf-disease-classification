"""Tests for tools/export_py.py using throwaway fixture notebooks in a temp dir."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import EXPORT_TOOL_PATH, REPO_ROOT

MAIN = "def main():\n    print('hi')\n"


def make_notebook(path: Path, cells: list[tuple[str, str]]) -> Path:
    """Write a minimal nbformat 4 notebook. ``cells`` is a list of (cell_type, source)."""
    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {},
        "cells": [
            {"cell_type": kind, "metadata": {}, "source": source.splitlines(keepends=True)}
            | ({"execution_count": None, "outputs": []} if kind == "code" else {})
            for kind, source in cells
        ],
    }
    path.write_text(json.dumps(nb), encoding="utf-8")
    return path


def export(export_tool, tmp_path: Path, notebooks: dict[str, list[tuple[str, str]]]) -> Path:
    nb_dir = tmp_path / "notebooks"
    nb_dir.mkdir(exist_ok=True)
    for name, cells in notebooks.items():
        make_notebook(nb_dir / name, cells)
    out = tmp_path / "out.py"
    export_tool.export(nb_dir, out, repo_root=tmp_path)
    return out


def exported(source: str) -> tuple[str, str]:
    return ("code", "#| export\n" + source)


def test_happy_path_order_header_and_guard(export_tool, tmp_path):
    out = export(
        export_tool,
        tmp_path,
        {
            "20_b.ipynb": [("markdown", "# notes"), exported("import json\n\nB = 2")],
            "10_a.ipynb": [exported("import numpy as np\n\nA = 1"), ("code", "not_exported = 1")],
            "90_cli.ipynb": [exported(MAIN)],
        },
    )
    text = out.read_text()
    assert text.startswith('"""')
    assert "GENERATED FILE - DO NOT EDIT" in text
    assert text.index("from 10_a.ipynb") < text.index("from 20_b.ipynb") < text.index("from 90_cli.ipynb")
    assert "#| export" not in text
    assert "not_exported" not in text
    assert text.rstrip().endswith('if __name__ == "__main__":\n    main()')
    # The result actually runs.
    run = subprocess.run([sys.executable, str(out)], capture_output=True, text=True)
    assert run.returncode == 0 and run.stdout.strip() == "hi"


def test_skips_audit_and_runner_notebooks(export_tool, tmp_path):
    out = export(
        export_tool,
        tmp_path,
        {
            "00_audit.ipynb": [exported("import pandas as pd")],
            "colab_runner.ipynb": [exported("import google.colab")],
            "90_cli.ipynb": [exported(MAIN)],
        },
    )
    assert "pandas" not in out.read_text()
    assert "colab" not in out.read_text()


@pytest.mark.parametrize(
    "bad_import",
    [
        "import pandas",
        "import pandas as pd",
        "from PIL import Image",
        "import timm",
        "from torch.nn import Module\nimport PIL.Image",
        "def f():\n    import pandas",  # nested imports count too
        "from . import sibling",
    ],
)
def test_import_guard_rejects_forbidden_imports(export_tool, tmp_path, bad_import):
    with pytest.raises(export_tool.ExportError) as excinfo:
        export(export_tool, tmp_path, {"10_data.ipynb": [exported(bad_import)], "90_cli.ipynb": [exported(MAIN)]})
    message = str(excinfo.value)
    assert "10_data.ipynb" in message and "cell 0" in message
    assert not (tmp_path / "out.py").exists(), "nothing may be written when a check fails"


def test_import_guard_message_names_package_and_cell_index(export_tool, tmp_path):
    cells = [("markdown", "intro"), exported("x = 1"), exported("import pandas as pd")]
    with pytest.raises(export_tool.ExportError) as excinfo:
        export(export_tool, tmp_path, {"20_classifier.ipynb": cells, "90_cli.ipynb": [exported(MAIN)]})
    message = str(excinfo.value)
    assert "20_classifier.ipynb, cell 2" in message
    assert "'pandas'" in message


@pytest.mark.parametrize(
    "good_import",
    [
        "import numpy",
        "import numpy as np\nimport matplotlib.pyplot as plt\nimport cv2",
        "from sklearn.metrics import f1_score\nfrom skimage import measure",
        "import torch\nimport torch.nn as nn\nfrom torchvision import models",
        "import os, sys, json, argparse, importlib, __future__",
        "from concurrent.futures import ProcessPoolExecutor",
    ],
)
def test_import_guard_accepts_allowed_imports(export_tool, tmp_path, good_import):
    export(export_tool, tmp_path, {"10_data.ipynb": [exported(good_import)], "90_cli.ipynb": [exported(MAIN)]})


@pytest.mark.parametrize(
    ("bad_source", "needle"),
    [
        ("!pip install numpy", "notebook-only syntax"),
        ("%matplotlib inline", "notebook-only syntax"),
        ("x = 1\n%timeit x", "notebook-only syntax"),
        ("display(1)", "display"),
        ("def f():\n    display(df)", "display"),
        ("get_ipython().run_line_magic('x', '')", "get_ipython"),
        ("def broken(:\n    pass", "syntax error"),
    ],
)
def test_notebook_only_syntax_is_rejected(export_tool, tmp_path, bad_source, needle):
    with pytest.raises(export_tool.ExportError) as excinfo:
        export(export_tool, tmp_path, {"10_data.ipynb": [exported(bad_source)], "90_cli.ipynb": [exported(MAIN)]})
    assert needle in str(excinfo.value)
    assert "10_data.ipynb" in str(excinfo.value)


def test_valid_python_that_merely_looks_like_magic_is_accepted(export_tool, tmp_path):
    source = "total = (1\n% 2)\nnot_equal = (1\n!= 2)\ntext = '''\n!not a shell command\n%nor a magic\n'''\nclass V:\n    def display(self): ...\nV().display()"
    export(export_tool, tmp_path, {"10_data.ipynb": [exported(source)], "90_cli.ipynb": [exported(MAIN)]})


def test_only_notebook_cells_with_exact_marker_are_exported(export_tool, tmp_path):
    out = export(
        export_tool,
        tmp_path,
        {
            "10_data.ipynb": [
                ("code", "# #| export\nSKIPPED_COMMENTED = 1"),
                ("markdown", "#| export\nSKIPPED_MARKDOWN = 1"),
                ("code", "x = 1\n#| export\nSKIPPED_NOT_FIRST_LINE = 1"),
                exported("KEPT = 1"),
            ],
            "90_cli.ipynb": [exported(MAIN)],
        },
    )
    text = out.read_text()
    assert "KEPT" in text
    assert "SKIPPED" not in text


@pytest.mark.parametrize("marker", ["#|export", "# | export", "#| Export", "#|  export"])
def test_near_miss_marker_is_an_error_not_a_silent_skip(export_tool, tmp_path, marker):
    cells = [("code", f"{marker}\nX = 1")]
    with pytest.raises(export_tool.ExportError, match="export marker"):
        export(export_tool, tmp_path, {"10_data.ipynb": cells, "90_cli.ipynb": [exported(MAIN)]})


def test_missing_main_is_an_error(export_tool, tmp_path):
    with pytest.raises(export_tool.ExportError, match="main"):
        export(export_tool, tmp_path, {"10_data.ipynb": [exported("X = 1")]})


def test_no_notebooks_is_an_error(export_tool, tmp_path):
    (tmp_path / "notebooks").mkdir()
    with pytest.raises(export_tool.ExportError, match="no notebooks"):
        export_tool.export(tmp_path / "notebooks", tmp_path / "out.py", repo_root=tmp_path)


def test_source_as_plain_string_is_supported(export_tool, tmp_path):
    nb_dir = tmp_path / "notebooks"
    nb_dir.mkdir()
    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {},
        "cells": [{"cell_type": "code", "metadata": {}, "outputs": [], "source": "#| export\ndef main(): ..."}],
    }
    (nb_dir / "90_cli.ipynb").write_text(json.dumps(nb))
    export_tool.export(nb_dir, tmp_path / "out.py", repo_root=tmp_path)
    assert "def main()" in (tmp_path / "out.py").read_text()


def test_export_is_deterministic(export_tool, tmp_path):
    notebooks = {"10_data.ipynb": [exported("import json")], "90_cli.ipynb": [exported(MAIN)]}
    first = export(export_tool, tmp_path, notebooks).read_text()
    second = export(export_tool, tmp_path, notebooks).read_text()
    assert first == second


def test_embedded_sections_extension_point_is_empty_but_validated(export_tool, tmp_path):
    assert export_tool.embedded_sections(tmp_path) == []
    # Anything returned from the extension point goes through the same import guard.
    bad = export_tool.Section("embedded:data.json", "import pandas")
    with pytest.raises(export_tool.ExportError, match="embedded:data.json"):
        export_tool.build_module([], [bad])


def test_command_line_failure_exit_code_and_message(tmp_path):
    nb_dir = tmp_path / "notebooks"
    nb_dir.mkdir()
    make_notebook(nb_dir / "10_data.ipynb", [exported("import pandas")])
    result = subprocess.run(
        [sys.executable, str(EXPORT_TOOL_PATH), "--notebooks-dir", str(nb_dir), "--out", str(tmp_path / "o.py")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "10_data.ipynb, cell 0" in result.stderr and "'pandas'" in result.stderr
    assert not (tmp_path / "o.py").exists()
