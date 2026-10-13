"""CLI skeleton tests (phase 01). Later phases add their own test files."""

import subprocess
import sys
from pathlib import Path

import pytest

NOT_IMPLEMENTED = {
    "gradcam": ["--exp", "E1-U", "--split", "0"],
    "reproduce": [],
}


def test_help_exits_zero(gs, capsys):
    with pytest.raises(SystemExit) as excinfo:
        gs.run_cli(["--help"])
    assert excinfo.value.code == 0
    out = capsys.readouterr().out
    for command in [*NOT_IMPLEMENTED, "smoke", "download-weights", "run", "choose-lr", "predict", "benchmark"]:
        assert command in out


def test_help_as_subprocess(group_file):
    result = subprocess.run(
        [sys.executable, str(group_file), "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "--data-root" in result.stdout


@pytest.mark.parametrize("command", sorted(NOT_IMPLEMENTED))
def test_stub_commands_fail_with_clear_message(gs, capsys, command):
    code = gs.run_cli([command, *NOT_IMPLEMENTED[command]])
    assert code != 0
    assert "not implemented yet (phase" in capsys.readouterr().err


def test_global_flags_before_and_after_command(gs):
    parser = gs.build_parser()
    before = parser.parse_args(["--data-root", "A", "--device", "cpu", "--fast", "smoke"])
    after = parser.parse_args(["smoke", "--data-root", "A", "--device", "cpu", "--fast"])
    for args in (before, after):
        assert args.data_root == Path("A")
        assert args.device == "cpu"
        assert args.fast is True
    defaults = parser.parse_args(["smoke"])
    assert defaults.data_root == Path("Dhan-Shomadhan")
    assert defaults.device == "auto"
    assert defaults.seed_offset == 0
    assert defaults.fast is False


def test_flag_before_command_survives_subparser_defaults(gs):
    args = gs.build_parser().parse_args(["--seed-offset", "7", "run", "--exp", "E1-U"])
    assert args.seed_offset == 7
    assert args.splits == (0, 1, 2, 3, 4)


def test_parse_splits(gs):
    assert gs.parse_splits("0,2,2,1") == (0, 2, 1)
    with pytest.raises(Exception):
        gs.parse_splits("a,b")
    with pytest.raises(Exception):
        gs.parse_splits("-1")


def test_smoke_succeeds_on_data_root_with_images(gs, tiny_tree, capsys):
    (tiny_tree / "_work").mkdir()
    (tiny_tree / "_work" / "ignored.jpg").write_bytes(b"")
    before = sorted(p.relative_to(tiny_tree) for p in tiny_tree.rglob("*"))
    code = gs.run_cli(["smoke", "--data-root", str(tiny_tree), "--device", "cpu"])
    out = capsys.readouterr().out
    assert code == 0
    assert "found 12 JPEG images" in out
    assert "read and cached 12 images" in out and "idempotent" in out
    assert "smoke: PASSED" in out
    assert sorted(p.relative_to(tiny_tree) for p in tiny_tree.rglob("*")) == before, "smoke must not write into the data root"


def test_smoke_as_script_uses_the_process_pool(group_file, tiny_tree):
    """Run the exported file as a script, so that spawned workers can re-import it (macOS/Windows)."""
    result = subprocess.run(
        [sys.executable, str(group_file), "smoke", "--data-root", str(tiny_tree), "--device", "cpu"],
        capture_output=True,
        text=True,
        timeout=240,  # ~15 s on an idle machine; a heavily loaded one (torch is imported twice) needs ~100 s
    )
    assert result.returncode == 0, result.stderr
    assert "smoke: PASSED" in result.stdout


def test_smoke_fails_on_unlabelled_image(gs, tiny_tree, capsys):
    from conftest import make_jpeg

    make_jpeg(tiny_tree / "oops_1.jpg")
    assert gs.run_cli(["smoke", "--data-root", str(tiny_tree), "--device", "cpu"]) == 1
    assert "oops_1.jpg" in capsys.readouterr().err


def test_prepare_fails_cleanly_on_the_wrong_dataset(gs, tiny_tree, capsys):
    assert gs.run_cli(["prepare", "--data-root", str(tiny_tree)]) == 1
    err = capsys.readouterr().err
    assert "prepare: FAIL" in err and "not the expected dataset" in err
    assert not (tiny_tree / "_work" / "index.json").exists()


def test_prepare_has_a_workers_flag(gs):
    assert gs.build_parser().parse_args(["prepare", "--workers", "3"]).workers == 3
    assert gs.build_parser().parse_args(["prepare"]).workers is None


def test_smoke_fails_without_data_root(gs, tmp_path, capsys):
    assert gs.run_cli(["smoke", "--data-root", str(tmp_path / "missing")]) != 0
    assert "not a directory" in capsys.readouterr().err


def test_smoke_fails_on_empty_data_root(gs, tmp_path, capsys):
    assert gs.run_cli(["smoke", "--data-root", str(tmp_path)]) != 0
    assert "no JPEG images" in capsys.readouterr().err
