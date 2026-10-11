"""Checks on the committed, generated deliverable."""

from conftest import REPO_ROOT


def test_committed_generated_file_is_up_to_date(export_tool, group_file, tmp_path):
    """Guards against editing a notebook and forgetting to re-export."""
    fresh = tmp_path / "fresh.py"
    export_tool.export(REPO_ROOT / "notebooks", fresh)
    assert fresh.read_text() == group_file.read_text(), "run `python tools/export_py.py`"
