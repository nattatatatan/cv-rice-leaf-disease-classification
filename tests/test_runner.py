"""Tests of the platform-aware runner notebook (notebooks/runner.ipynb).

The helpers live in notebook cells whose first line is `#| lib`: plain functions with no side effects. These tests
load exactly those cells (the notebook is the single source, nothing to keep in sync), then exercise platform detection,
path resolution, the Kaggle input discovery, dataset copy and restore on fake /kaggle trees in tmp_path, the GPU and torch
decisions with mocked subprocess calls, and the two-GPU orchestration with a real subprocess that stands in for the
generated script. Kaggle and Colab themselves cannot run here.
"""

import json
import os
import shutil
import stat
import sys
import textwrap
import time
import types
import zipfile
from pathlib import Path

import pytest

from conftest import REPO_ROOT

NOTEBOOK = REPO_ROOT / "notebooks" / "runner.ipynb"
LIB_MARKER = "#| lib"


def load_cells(marker=LIB_MARKER):
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    return [(c["id"], "".join(c["source"])) for c in nb["cells"] if c["cell_type"] == "code" and "".join(c["source"]).startswith(marker)]


@pytest.fixture(scope="module")
def lib():
    module = types.ModuleType("runner_lib")
    sys.modules["runner_lib"] = module
    for cell_id, source in load_cells():
        exec(compile(source, f"<runner cell {cell_id}>", "exec"), module.__dict__)
    return module


@pytest.fixture(autouse=True)
def quiet_log(lib):
    lib.set_log_path(None)
    yield
    lib.set_log_path(None)


# ---------------------------------------------------------------------------
# Notebook structure
# ---------------------------------------------------------------------------


def test_notebook_has_lib_cells_and_no_notebook_only_syntax_in_them():
    cells = load_cells()
    assert len(cells) >= 6
    for cell_id, source in cells:
        for line in source.splitlines():
            assert not line.lstrip().startswith(("!", "%")), f"{cell_id}: notebook-only syntax {line!r}"
        compile(source, cell_id, "exec")


def test_no_em_dash_in_notebook():
    assert chr(0x2014) not in NOTEBOOK.read_text(encoding="utf-8")


def test_batch_cells_follow_the_documented_order():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    ids = [c["id"] for c in nb["cells"]]
    order = ["settings", "setup-config", "setup-inputs", "setup-install", "setup-dataset", "setup-restore", "setup-env", "smoke",
             "setup-restore-caches", "batch2", "batch3-sweeps", "batch3-core", "batch3-wf", "batch4", "batch4-wf", "batch-generic",
             "finish"]
    assert [i for i in ids if i in order] == order
    assert ids[0] == "runner-intro" and ids.index("settings") == 1  # BATCHES_TO_RUN is the first thing in the notebook


def test_every_batch_cell_name_is_a_known_plan(lib):
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    import re

    called = set()
    for cell in nb["cells"]:
        called.update(re.findall(r'^batch\("([^"]+)"\)$', "".join(cell["source"]), flags=re.M))
    assert called and called <= set(lib.BATCH_PLANS)


# ---------------------------------------------------------------------------
# Platform detection and paths
# ---------------------------------------------------------------------------


def test_detect_platform_uses_machine_markers(lib):
    detect = lib.detect_platform
    none = lambda p: False  # noqa: E731
    assert detect(env={}, exists=none) == "local"
    # Kaggle: either marker
    assert detect(env={"KAGGLE_KERNEL_RUN_TYPE": "Batch"}, exists=none) == "kaggle"
    assert detect(env={}, exists=lambda p: p == "/kaggle/input") == "kaggle"
    # Colab: /var/colab/hostname or its environment variables
    assert detect(env={}, exists=lambda p: p == "/var/colab/hostname") == "colab"
    assert detect(env={"COLAB_RELEASE_TAG": "release-colab_20260101"}, exists=none) == "colab"
    assert detect(env={"COLAB_GPU": "1"}, exists=none) == "colab"
    # /kaggle alone (no input mount, no run type) is not enough, and nothing about importability matters
    assert detect(env={}, exists=lambda p: p == "/kaggle") == "local"
    # overrides
    assert detect(env={"RUNNER_PLATFORM": "local"}, exists=lambda p: True) == "local"
    assert detect(env={"RUNNER_PLATFORM": " Colab "}, exists=none) == "colab"
    with pytest.raises(AssertionError):
        detect(env={"RUNNER_PLATFORM": "mars"})


def test_kaggle_wins_even_when_colab_markers_and_google_colab_exist(lib, monkeypatch):
    """Kaggle images ship the google.colab package (and may carry COLAB_* variables): that must not make them 'colab'
    (it made the Drive mount raise 'Mounting drive is unsupported in this environment')."""
    import importlib.machinery
    import importlib.util

    fake_colab = types.ModuleType("google.colab")
    fake_colab.__spec__ = importlib.machinery.ModuleSpec("google.colab", None)
    fake_google = types.ModuleType("google")
    fake_google.__spec__ = importlib.machinery.ModuleSpec("google", None)
    fake_google.colab = fake_colab
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.colab", fake_colab)
    assert importlib.util.find_spec("google.colab") is not None  # importable, as on Kaggle
    env = {"KAGGLE_KERNEL_RUN_TYPE": "Interactive", "COLAB_RELEASE_TAG": "x", "COLAB_GPU": "1"}
    assert lib.detect_platform(env=env, exists=lambda p: p in ("/kaggle/input", "/var/colab/hostname")) == "kaggle"
    assert lib.detect_platform(env={}, exists=lambda p: p == "/kaggle/input") == "kaggle"
    # importable google.colab and no machine marker at all: local, not colab
    assert lib.detect_platform(env={}, exists=lambda p: False) == "local"


def test_google_colab_is_imported_only_inside_the_colab_branch():
    import ast

    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    found = 0
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        tree = ast.parse("".join(cell["source"]))
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.Import, ast.ImportFrom)):
                    names = [child.module] if isinstance(child, ast.ImportFrom) else [a.name for a in child.names]
                    if any(n and n.startswith("google.colab") for n in names):
                        found += 1
                        assert isinstance(node, ast.If) and ast.unparse(node.test) == "PLATFORM == 'colab'", ast.unparse(node.test)
    assert found == 1


def test_kaggle_config_keeps_data_out_of_the_saved_output(lib, tmp_path):
    cfg = lib.resolve_config("kaggle", "group3-starvenus", kaggle_root=tmp_path / "kaggle", min_free_gb=0)
    working = tmp_path / "kaggle" / "working"
    assert cfg.persist == "outdir" and cfg.device == "cuda" and cfg.require_gpu
    assert cfg.out_dir == working / "out" and cfg.out_zip == working / "out.zip" and cfg.input_root == tmp_path / "kaggle" / "input"
    for path in (cfg.data_root, cfg.work, cfg.scratch, cfg.script_path):
        assert working not in path.parents, f"{path} would be saved as notebook output"
    assert cfg.data_root == tmp_path / "kaggle" / "tmp" / "Dhan-Shomadhan"
    assert cfg.runs_dir == cfg.data_root / "_work" / "runs" and cfg.choices_path == cfg.data_root / "_work" / "results" / "choices.json"
    assert cfg.env_json_path == cfg.out_dir / "env.json" and cfg.log_path == cfg.out_dir / "runner_log.txt"


def test_scratch_falls_back_when_a_candidate_is_unusable(lib, tmp_path):
    blocked = tmp_path / "blocked"
    blocked.write_text("a file, so mkdir fails")
    good = tmp_path / "good"
    assert lib.pick_scratch_dir([blocked / "tmp", good], min_free_gb=0) == good
    with pytest.raises(lib.RunnerError, match="not writable") as info:
        lib.pick_scratch_dir([blocked / "tmp"], min_free_gb=0)
    assert str(blocked) in str(info.value)
    with pytest.raises(lib.RunnerError, match="GB free"):
        lib.pick_scratch_dir([good], min_free_gb=10**9)


def test_colab_and_local_config(lib, tmp_path):
    cfg = lib.resolve_config("colab", "group3-starvenus")
    assert cfg.persist == "drive" and cfg.data_root == Path("/content/Dhan-Shomadhan")
    assert cfg.drive == Path("/content/drive/MyDrive/csci935") and cfg.drive_runs == cfg.drive / "_work" / "runs"
    assert cfg.env_json_path == cfg.drive_runs / "env.json" and cfg.script_path == Path("/content/group3-starvenus.py")
    local = lib.resolve_config("local", "group3-starvenus", env={"RUNNER_REPO": str(tmp_path), "RUNNER_OUT_BASE": str(tmp_path / "o")})
    assert local.device == "auto" and not local.require_gpu and local.data_root == tmp_path.resolve() / "Dhan-Shomadhan"
    assert local.out_zip == tmp_path / "o" / "out.zip"


def test_python_and_internet_checks(lib):
    lib.check_python((3, 12, 1))
    lib.check_python((3, 13, 0))
    with pytest.raises(lib.RunnerError, match="3.12"):
        lib.check_python((3, 11, 9))

    class Response:
        def close(self):
            pass

    lib.ensure_internet(urlopen=lambda url, timeout: Response())

    def offline(url, timeout):
        raise OSError("name resolution failed")

    with pytest.raises(lib.RunnerError, match="Internet > On"):
        lib.ensure_internet(urlopen=offline)


# ---------------------------------------------------------------------------
# GPUs and torch
# ---------------------------------------------------------------------------

T4_X2 = "0, Tesla T4, 7.5, 560.35.03, 15360\n1, Tesla T4, 7.5, 560.35.03, 15360\n"
P100 = "0, Tesla P100-PCIE-16GB, 6.0, 560.35.03, 16384\n"


def test_parse_and_check_gpus(lib, capsys):
    gpus = lib.parse_gpus(T4_X2)
    assert [g["name"] for g in gpus] == ["Tesla T4", "Tesla T4"] and gpus[0]["capability"] == (7, 5) and gpus[1]["index"] == 1
    assert lib.check_gpus(gpus, "kaggle") == ["Tesla T4", "Tesla T4"]
    assert "GPU 1: Tesla T4" in capsys.readouterr().out


def test_p100_fails_early_and_says_what_to_select(lib):
    with pytest.raises(lib.RunnerError) as info:
        lib.check_gpus(lib.parse_gpus(P100), "kaggle")
    message = str(info.value)
    assert "P100" in message and "GPU T4 x2" in message and "sm_60" in message
    with pytest.raises(lib.RunnerError, match="no GPU"):
        lib.check_gpus([], "kaggle")
    with pytest.raises(lib.RunnerError, match="T4 GPU"):
        lib.check_gpus([], "colab")


def test_gpu_warnings(lib, capsys):
    lib.check_gpus(lib.parse_gpus("0, NVIDIA L4, 8.9, 580.1, 23034\n"), "colab")
    assert "not a T4" in capsys.readouterr().out
    lib.check_gpus(lib.parse_gpus("0, Tesla T4, 7.5, 560, 15360\n"), "kaggle")
    assert "only one GPU" in capsys.readouterr().out
    lib.check_gpus(lib.parse_gpus("0, Tesla T4, 7.5, 560, 15360\n1, NVIDIA L4, 8.9, 560, 23034\n"), "kaggle")
    assert "different models" in capsys.readouterr().out


def test_query_gpus_handles_missing_nvidia_smi(lib):
    def missing(*args, **kwargs):
        raise FileNotFoundError("nvidia-smi")

    assert lib.query_gpus(run=missing) == []
    ok = types.SimpleNamespace(returncode=0, stdout=T4_X2)
    assert len(lib.query_gpus(run=lambda *a, **k: ok)) == 2
    assert lib.query_gpus(run=lambda *a, **k: types.SimpleNamespace(returncode=9, stdout="x")) == []


def test_requirements_parsing_and_filtering(lib):
    text = (REPO_ROOT / "requirements.txt").read_text()
    pins = lib.parse_requirements(text)
    assert pins["torch"] == "2.11.0" and pins["torchvision"] == "0.26.0" and pins["opencv-python-headless"].startswith("4.12.")
    filtered = lib.filter_requirements(text, {"torch", "torchvision"})
    assert "torch" not in lib.parse_requirements(filtered) and "numpy" in lib.parse_requirements(filtered)


PINS = {"torch": "2.11.0", "torchvision": "0.26.0"}


def good_info(torch="2.11.0+cu130", n=2):
    return {"torch": torch, "torchvision": "0.26.0+" + torch.split("+")[-1], "cuda_available": True,
            "devices": [{"index": i, "name": "Tesla T4", "op_ok": True} for i in range(n)], "python": "3.13.1", "opencv": "4.12.0"}


def test_torch_candidates_follow_the_driver(lib):
    new = lib.torch_candidates("580.65.06", PINS, python="py")
    assert "cu130" in new[0]["label"] or "13.0" in new[0]["label"]
    assert new[0]["cmd"] == ["py", "-m", "pip", "install", "-q", "--disable-pip-version-check", "torch==2.11.0", "torchvision==0.26.0"]
    assert "cu128" in new[1]["label"]
    old = lib.torch_candidates("560.35.03", PINS, python="py")
    assert old[0]["cmd"][-4:] == ["torch==2.11.0+cu128", "torchvision==0.26.0+cu128", "--extra-index-url", "https://download.pytorch.org/whl/cu128"]
    assert "cu126" in old[1]["label"]


def test_matching_torch_is_kept_without_downloading(lib):
    calls = []
    result = lib.ensure_torch(lambda cmd: calls.append(cmd), PINS, "560.1", 2, probe=lambda: good_info())
    assert calls == [] and result["honoured"] and result["how"] == "preinstalled"


def test_wrong_torch_is_replaced_by_the_pin_for_the_driver(lib):
    probes = iter([good_info("2.6.0+cu124"), good_info("2.11.0+cu128")])
    calls = []
    result = lib.ensure_torch(lambda cmd: calls.append(cmd), PINS, "560.1", 2, probe=lambda: next(probes))
    assert len(calls) == 1 and "torch==2.11.0+cu128" in calls[0] and result["honoured"] and "cu128" in result["how"]


def test_install_fallback_to_the_next_candidate(lib):
    attempts = []

    def stream(cmd):
        attempts.append(cmd)
        if len(attempts) == 1:
            raise lib.RunnerError("pip failed")

    probes = iter([good_info("2.6.0"), good_info("2.11.0+cu126")])
    result = lib.ensure_torch(stream, PINS, "560.1", 1, probe=lambda: next(probes))
    assert len(attempts) == 2 and "cu126" in result["how"]


def test_unhonoured_pin_warns_loudly_and_is_recorded(lib, capsys):
    result = lib.ensure_torch(lambda cmd: (_ for _ in ()).throw(lib.RunnerError("offline")), PINS, "560.1", 2,
                              probe=lambda: good_info("2.6.0+cu124"))
    out = capsys.readouterr().out
    assert not result["honoured"] and "THE TORCH PIN COULD NOT BE HONOURED" in out and "2.6.0+cu124" in out
    record = lib.build_env_record(types.SimpleNamespace(platform="kaggle"), [{"name": "Tesla T4", "driver": "560"}],
                                  result["info"], result)
    assert record["torch_pin_honoured"] is False and record["torch"] == "2.6.0+cu124" and record["gpu"] == "Tesla T4"


def test_no_working_torch_raises(lib):
    broken = {"torch": "2.11.0+cu130", "torchvision": "0.26.0", "cuda_available": True,
              "devices": [{"index": 0, "op_ok": False, "error": "no kernel image is available"}]}
    with pytest.raises(lib.RunnerError, match="no torch build can use the GPU"):
        lib.ensure_torch(lambda cmd: None, PINS, "580.1", 1, probe=lambda: broken)


def test_install_requirements_single_opencv_and_filtered_torch(lib, tmp_path):
    requirements = tmp_path / "requirements.txt"
    requirements.write_text((REPO_ROOT / "requirements.txt").read_text())
    calls = []
    info = lib.install_requirements(lambda cmd: calls.append([str(c) for c in cmd]), requirements, True, tmp_path,
                                    probe=lambda: {"opencv": "4.12.0"}, python="py")
    assert calls[0][:6] == ["py", "-m", "pip", "uninstall", "-y", "-q"] and "opencv-contrib-python-headless" in calls[0]
    assert calls[1][-1] == str(requirements) and info["opencv"] == "4.12.0"
    calls.clear()
    lib.install_requirements(lambda cmd: calls.append([str(c) for c in cmd]), requirements, False, tmp_path,
                             probe=lambda: {"opencv": "4.12.0"}, python="py")
    filtered = Path(calls[1][-1])
    assert filtered.name == "requirements.filtered.txt" and "torch" not in lib.parse_requirements(filtered.read_text())
    with pytest.raises(lib.RunnerError, match="OpenCV 4.12"):
        lib.install_requirements(lambda cmd: None, requirements, True, tmp_path, probe=lambda: {"opencv": "5.0.0"}, python="py")


def test_probe_environment_parses_the_marker_line(lib):
    payload = json.dumps({"torch": "2.11.0"})
    fake = lambda *a, **k: types.SimpleNamespace(stdout=f"noise\nPROBE_JSON {payload}\n", stderr="")  # noqa: E731
    assert lib.probe_environment(run=fake) == {"torch": "2.11.0"}
    assert "probe_error" in lib.probe_environment(run=lambda *a, **k: types.SimpleNamespace(stdout="", stderr="boom"))


def test_probe_code_runs_for_real(lib):
    info = lib.probe_environment()
    assert info["python"].startswith("3.") and ("torch" in info or "torch_error" in info)


# ---------------------------------------------------------------------------
# Kaggle inputs, dataset copy, restore (fake /kaggle trees)
# ---------------------------------------------------------------------------

DOMAINS = ("White Background ", "Field Background  ")


def make_dataset(top: Path, domains=DOMAINS, per_domain=3):
    for d, domain in enumerate(domains):
        for i in range(per_domain):
            path = top / domain / "Brown Spot" / f"img_{d}_{i}.jpg"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"\xff\xd8 fake jpeg %d %d" % (d, i))
    (top / "Dhan-Shomadhan_picture_Information.csv").write_text("pictureName,Diseases\n")
    return top


def make_zip(zip_path: Path, tree: Path, prefix="Dhan-Shomadhan", junk=True):
    with zipfile.ZipFile(zip_path, "w") as archive:
        for path in sorted(tree.rglob("*")):
            if path.is_file():
                archive.write(path, f"{prefix}/{path.relative_to(tree).as_posix()}")
        if junk:
            archive.writestr("__MACOSX/Dhan-Shomadhan/._img.jpg", b"junk")
            archive.writestr(f"{prefix}/.DS_Store", b"junk")


def make_code_dataset(code: Path, runs=False, choices=True):
    code.mkdir(parents=True, exist_ok=True)
    (code / "group3-starvenus.py").write_text("print('script')\n")
    (code / "requirements.txt").write_text((REPO_ROOT / "requirements.txt").read_text())
    if choices:
        (code / "choices.json").write_text(json.dumps({"input_mode": {"value": "rect", "evidence": {}}}))
    return code


N = 6  # images in the fake dataset


def test_discover_with_an_uploaded_zip(lib, tmp_path):
    inp = tmp_path / "input"
    make_code_dataset(inp / "csci935-code")
    src = make_dataset(tmp_path / "src")
    (inp / "csci935-dhan-shomadhan").mkdir(parents=True)
    make_zip(inp / "csci935-dhan-shomadhan" / "Dhan-Shomadhan.zip", src)
    found = lib.discover_kaggle_inputs(inp, "group3-starvenus.py", expected_images=N)
    assert found["data_kind"] == "zip" and found["data_source"].name == "Dhan-Shomadhan.zip"
    assert found["code_dir"] == inp / "csci935-code" and found["choices"] and not found["runs_zip"]


def test_discover_with_an_extracted_tree_and_altered_folder_names(lib, tmp_path):
    inp = tmp_path / "input"
    make_code_dataset(inp / "datasets" / "someone" / "csci935-code")  # newer mounts add owner folders
    make_dataset(inp / "datasets" / "someone" / "csci935-dhan-shomadhan" / "Dhan-Shomadhan", domains=("White Background", "Field Background"))
    found = lib.discover_kaggle_inputs(inp, "group3-starvenus.py", expected_images=N)
    assert found["data_kind"] == "tree" and found["data_source"].name == "Dhan-Shomadhan"
    assert found["code_dir"].name == "csci935-code"


def test_discover_failures_list_what_is_mounted(lib, tmp_path):
    inp = tmp_path / "input"
    (inp / "something-else").mkdir(parents=True)
    (inp / "something-else" / "notes.txt").write_text("x")
    with pytest.raises(lib.RunnerError) as info:
        lib.discover_kaggle_inputs(inp, "group3-starvenus.py", expected_images=N)
    assert "csci935-code" in str(info.value) and "something-else" in str(info.value) and "notes.txt" in str(info.value)
    make_code_dataset(inp / "csci935-code")
    with pytest.raises(lib.RunnerError, match="images were not found"):
        lib.discover_kaggle_inputs(inp, "group3-starvenus.py", expected_images=N)
    make_dataset(inp / "d")
    with pytest.raises(lib.RunnerError, match="expected 1106"):
        lib.discover_kaggle_inputs(inp, "group3-starvenus.py", expected_images=1106)
    with pytest.raises(lib.RunnerError, match="does not exist"):
        lib.discover_kaggle_inputs(tmp_path / "nope", "group3-starvenus.py")
    (inp / "csci935-code" / "requirements.txt").unlink()
    with pytest.raises(lib.RunnerError, match="no requirements.txt"):
        lib.discover_kaggle_inputs(inp, "group3-starvenus.py", expected_images=N)


def test_discover_rejects_two_code_datasets(lib, tmp_path):
    inp = tmp_path / "input"
    make_code_dataset(inp / "a")
    make_code_dataset(inp / "b")
    with pytest.raises(lib.RunnerError, match="several attached datasets"):
        lib.discover_kaggle_inputs(inp, "group3-starvenus.py", expected_images=N)


def test_materialise_from_zip_ignores_junk_and_keeps_names(lib, tmp_path, capsys):
    src = make_dataset(tmp_path / "src")
    make_zip(tmp_path / "ds.zip", src)
    root, scratch = tmp_path / "scratch" / "Dhan-Shomadhan", tmp_path / "scratch"
    layout = lib.materialise_dataset("zip", tmp_path / "ds.zip", root, scratch, expected_images=N)
    assert lib.count_images(root) == N and (root / "White Background " / "Brown Spot" / "img_0_0.jpg").is_file()
    assert not (scratch / "_dataset_stage").exists() and not (root / ".DS_Store").exists()
    assert "'White Background '" in layout["source_top_level"] and layout["differs_from_original_names"] == []
    assert "'Field Background  '" in capsys.readouterr().out  # repr shows the trailing spaces


def test_materialise_from_a_read_only_tree_with_altered_names(lib, tmp_path, capsys):
    src = make_dataset(tmp_path / "ro" / "Dhan-Shomadhan", domains=("White Background", "Field Background"))
    for path in [*src.rglob("*"), src]:  # what /kaggle/input looks like
        path.chmod(path.stat().st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    try:
        root = tmp_path / "scratch" / "Dhan-Shomadhan"
        layout = lib.materialise_dataset("tree", src, root, tmp_path / "scratch", expected_images=N)
        (root / "_work").mkdir()  # the copy must be writable
        (root / "_work" / "x").write_text("ok")
        assert lib.count_images(root) == N
        assert layout["differs_from_original_names"] == ["'Field Background'", "'White Background'"]
        assert "differ from the original" in capsys.readouterr().out
    finally:
        for path in [*src.rglob("*"), src]:
            path.chmod(0o755)


def test_materialise_wrong_count_and_repair_and_existing(lib, tmp_path):
    src = make_dataset(tmp_path / "src")
    root = tmp_path / "scratch" / "Dhan-Shomadhan"
    with pytest.raises(lib.RunnerError, match="expected 99 images"):
        lib.materialise_dataset("tree", src, root, tmp_path / "scratch", expected_images=99)
    (root / "_work").mkdir(exist_ok=True)
    (root / "_work" / "keep").write_text("unsynced run")
    victim = next(root.rglob("img_1_2.jpg"))
    victim.unlink()  # an interrupted copy
    assert lib.count_images(root) == N - 1
    lib.materialise_dataset("tree", src, root, tmp_path / "scratch", expected_images=N)
    assert lib.count_images(root) == N and (root / "_work" / "keep").read_text() == "unsynced run"
    assert lib.materialise_dataset("tree", src, root, tmp_path / "scratch", expected_images=N)["kind"] == "existing"


def test_map_member(lib):
    m = lib.map_member
    assert m(("runs", "E0-rect", "split_0", "metrics.json")) == Path("runs/E0-rect/split_0/metrics.json")
    assert m(("results", "choices.json")) == Path("results/choices.json")
    assert m(("_work", "runs", "E1-FF", "split_1", "x")) == Path("runs/E1-FF/split_1/x")
    assert m(("E1-FF", "split_1", "metrics.json")) == Path("runs/E1-FF/split_1/metrics.json")
    assert m(("env.json",)) is None and m(("pip_freeze.txt",)) is None and m(("runner_log.txt",)) is None
    assert m(("runs", "..", "..", "evil")) is None and m(("__MACOSX", "runs", "x")) is None and m(()) is None


def write_run(runs: Path, exp, split, gpu="Tesla T4", requested=None):
    d = runs / exp / f"split_{split}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "metrics.json").write_text("{}")
    (d / "env.json").write_text(json.dumps({"gpu": gpu}))
    (d / "config.json").write_text(json.dumps({"requested_exp_id": requested or exp, "experiment": {"exp_id": exp}}))


def test_restore_from_runs_zip_applies_choices_last(lib, tmp_path, capsys):
    prior = tmp_path / "prior" / "out"
    write_run(prior / "runs", "E0-rect", 0)
    write_run(prior / "runs", "E2-cnx-U", 0)
    (prior / "results").mkdir()
    (prior / "results" / "choices.json").write_text('{"old": true}')
    (prior / "env.json").write_text("{}")
    code = make_code_dataset(tmp_path / "input" / "csci935-code")
    zip_path = lib.make_zip(prior, code / "runs.zip")
    with zipfile.ZipFile(zip_path, "a") as archive:
        archive.writestr("../../evil.txt", "no")
    inputs = {"runs_zip": zip_path, "runs_dir": None, "choices": code / "choices.json"}
    work = tmp_path / "scratch" / "Dhan-Shomadhan" / "_work"
    assert lib.restore_from_code_dataset(inputs, work) == 7  # 2 runs x 3 files + results/choices.json; the '../' member is skipped
    assert lib.finished_splits(work / "runs") == {"E0-rect": [0], "E2-cnx-U": [0]}
    assert json.loads((work / "results" / "choices.json").read_text())["input_mode"]["value"] == "rect"  # the code dataset wins
    assert not (tmp_path / "evil.txt").exists() and not (work / "env.json").exists()


def test_restore_from_extracted_runs_folder_and_nothing(lib, tmp_path, capsys):
    code = make_code_dataset(tmp_path / "code", choices=False)
    write_run(code / "runs", "E1-FF", 2)
    work = tmp_path / "work"
    lib.restore_from_code_dataset({"runs_zip": None, "runs_dir": code / "runs", "choices": None}, work)
    assert lib.finished_splits(work / "runs") == {"E1-FF": [2]} and not (work / "results").exists()
    assert "no choices.json" in capsys.readouterr().out
    lib.restore_from_code_dataset({"runs_zip": None, "runs_dir": None, "choices": None}, tmp_path / "empty")
    assert "no runs.zip" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Sync and zip
# ---------------------------------------------------------------------------


def test_sync_tree_skips_checkpoints_scratch_temp_and_unchanged(lib, tmp_path):
    src, dst = tmp_path / "runs", tmp_path / "out"
    write_run(src, "E0-rect", 0)
    (src / "E0-rect" / "split_0" / "best.pt").write_bytes(b"weights")
    (src / "E0-rect" / "split_0" / "x.json.tmp123").write_text("half")
    write_run(src, "scratch", 0)
    write_run(src, "E1-FF", 0)
    assert lib.sync_tree(src, dst, keep_checkpoints=False, skip=("scratch",), say=lambda *_: None) == 6
    assert not (dst / "E0-rect" / "split_0" / "best.pt").exists() and not list(dst.rglob("*.tmp*")) and not (dst / "scratch").exists()
    assert lib.sync_tree(src, dst, keep_checkpoints=False, skip=("scratch",), say=lambda *_: None) == 0  # nothing changed
    (src / "E0-rect" / "split_0" / "metrics.json").write_text('{"changed": 1}')
    assert lib.sync_tree(src, dst, keep_checkpoints=True, skip=("scratch",), say=lambda *_: None) == 2  # metrics + best.pt
    assert (dst / "E0-rect" / "split_0" / "best.pt").is_file()


def test_make_zip_is_atomic_and_complete(lib, tmp_path):
    out = tmp_path / "out"
    (out / "runs" / "E0").mkdir(parents=True)
    (out / "runs" / "E0" / "m.json").write_text("{}")
    (out / "env.json").write_text("{}")
    zip_path = tmp_path / "out.zip"
    lib.make_zip(out, zip_path)
    with zipfile.ZipFile(zip_path) as archive:
        assert sorted(archive.namelist()) == ["env.json", "runs/E0/m.json"]
    (out / "runs" / "E0" / "m2.json").write_text("{}")
    lib.make_zip(out, zip_path)
    assert not list(tmp_path.glob("*.tmp")) and len(zipfile.ZipFile(zip_path).namelist()) == 3


def make_runner(lib, tmp_path, gpus=2, script_body=None, workers=2, keep=False):
    cfg = lib.resolve_config("kaggle", "group3-starvenus", kaggle_root=tmp_path / "kaggle", min_free_gb=0)
    if script_body is not None:
        cfg.script_path.parent.mkdir(parents=True, exist_ok=True)
        cfg.script_path.write_text(script_body)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    lib.set_log_path(cfg.log_path)
    gpu_list = [{"index": i, "name": "Tesla T4", "driver": "560", "capability": (7, 5)} for i in range(gpus)]
    return lib.Runner(cfg, gpu_list, keep_checkpoints=keep, workers_parallel=workers)


def test_kaggle_sync_writes_out_dir_and_zip_after_each_call(lib, tmp_path):
    runner = make_runner(lib, tmp_path)
    cfg = runner.cfg
    write_run(cfg.runs_dir, "E0-rect", 0)
    (cfg.runs_dir / "E0-rect" / "split_0" / "best.pt").write_bytes(b"w")
    write_run(cfg.runs_dir, "scratch", 0)
    cfg.choices_path.parent.mkdir(parents=True)
    cfg.choices_path.write_text('{"input_mode": {"value": "rect"}}')
    runner.sync_runs()
    names = sorted(zipfile.ZipFile(cfg.out_zip).namelist())
    assert "runs/E0-rect/split_0/metrics.json" in names and "results/choices.json" in names
    assert not any(n.endswith(".pt") or "scratch" in n for n in names)
    write_run(cfg.runs_dir, "E0-rect", 1)
    runner.sync_runs()
    assert "runs/E0-rect/split_1/metrics.json" in zipfile.ZipFile(cfg.out_zip).namelist()
    runner.sync_runs(keep_checkpoints=True)
    assert "runs/E0-rect/split_0/best.pt" in zipfile.ZipFile(cfg.out_zip).namelist()
    assert cfg.out_zip.parent == tmp_path / "kaggle" / "working" and cfg.data_root not in cfg.out_zip.parents


# ---------------------------------------------------------------------------
# Hardware rule
# ---------------------------------------------------------------------------


def test_prior_gpu_names_follow_aliases(lib, tmp_path):
    runs = tmp_path / "runs"
    write_run(runs, "E0-rect", 0, gpu="Tesla T4", requested="E1-U")  # E1-U is the E0-rect folder
    write_run(runs, "E0-rect", 1, gpu="NVIDIA L4", requested="E0-rect")
    write_run(runs, "E2-cnx-U", 3, gpu="Tesla T4")
    (runs / "E2-cnx-U" / "split_4").mkdir()  # unfinished: no metrics.json
    write_run(runs / "sweep", "E2-cnx-U_lr1e-4", 0, gpu="Tesla P4")
    assert lib.prior_gpu_names(runs, "E1-U") == {"Tesla T4": ["0"]}
    assert lib.prior_gpu_names(runs, "E0-rect") == {"Tesla T4": ["0"], "NVIDIA L4": ["1"]}
    assert lib.prior_gpu_names(runs, "E2") == {"Tesla T4": ["3"]}
    assert lib.prior_gpu_names(runs, "E9-none") == {} and lib.prior_gpu_names(tmp_path / "missing", "E0") == {}


def test_hardware_warnings(lib):
    assert lib.hardware_warnings("E2-cnx-U", {"Tesla T4": ["0"]}, ["Tesla T4", "Tesla T4"]) == []
    msgs = lib.hardware_warnings("E2-cnx-U", {"Tesla T4": ["0", "1"]}, ["NVIDIA A100"])
    assert len(msgs) == 1 and "'Tesla T4'" in msgs[0] and "0, 1" in msgs[0] and "same GPU type" in msgs[0]
    assert len(lib.hardware_warnings("X", {"Tesla T4": ["0"], "NVIDIA L4": ["1"]}, ["Tesla T4"])) == 2  # a mix, and L4 differs


def test_check_hardware_prints_a_loud_warning(lib, tmp_path, capsys):
    runner = make_runner(lib, tmp_path, gpus=1)
    write_run(runner.cfg.runs_dir, "E2-cnx-U", 0, gpu="NVIDIA L4")
    assert len(runner.check_hardware("E2-cnx-U")) == 1
    out = capsys.readouterr().out
    assert "!!!!" in out and "WARNING" in out and "NVIDIA L4" in out
    assert runner.check_hardware("E2-swin-U") == []


# ---------------------------------------------------------------------------
# Runner against a stand-in script (real subprocesses, real threads)
# ---------------------------------------------------------------------------

FAKE_SCRIPT = textwrap.dedent('''
    import json, os, sys, time
    from pathlib import Path

    args = sys.argv[1:]
    data_root, device, cmd, rest = Path(args[1]), args[3], args[4], args[5:]
    def opt(name, default=None):
        return rest[rest.index(name) + 1] if name in rest else default
    started = time.time()
    work = data_root / "_work"
    gpu = os.environ.get("FAKE_GPU", "Tesla T4")
    BACKBONES = {"E2-cnx-U": "convnext_tiny", "E2-swin-U": "swin_t", "E0-rect": "resnet50"}
    def write_split(folder, split, lr=None):
        d = folder / f"split_{split}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "env.json").write_text(json.dumps({"gpu": gpu}))
        (d / "config.json").write_text(json.dumps({"requested_exp_id": opt("--exp")}))
        (d / "best.pt").write_bytes(b"w")
        (d / "metrics.json").write_text(json.dumps({"lr": lr, "val": {"mixed": {"macro_f1": 0.5 + (lr or 0)}}}))
    if cmd == "run":
        exp = opt("--exp")
        time.sleep(float(os.environ.get("FAKE_SLEEP", "0.2")))
        if opt("--sweep-lr"):  # a flag without a value: opt() returns the next token, so test membership instead
            pass
        if "--sweep-lr" in rest:
            for lr in ("1e-4", "3e-4"):
                write_split(work / "runs" / "sweep" / f"{exp}_lr{lr}", 0, float(lr))
            print(f"sweep {exp} done")
        elif "--sweep-composites" in rest:
            for factor in ("0.5", "1"):
                write_split(work / "runs" / "sweep" / f"{exp}_n{factor}", 0)
            print(f"composite sweep {exp} done")
        else:
            split = int(opt("--splits"))
            fail = os.environ.get("FAKE_FAIL", "")
            if fail == f"{exp}:{split}":
                print("boom", file=sys.stderr)
                sys.exit(1)
            if (work / "runs" / exp / f"split_{split}" / "metrics.json").exists():
                print(f"[{exp} split {split}] skipped")
            else:
                write_split(work / "runs" / exp, split)
                print(f"[{exp} split {split}] done on {os.environ.get('CUDA_VISIBLE_DEVICES')}")
    elif cmd == "choose-lr":
        backbone = opt("--backbone")
        path = work / "results" / "choices.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        data = json.loads(path.read_text()) if path.exists() else {}
        time.sleep(0.2)
        data.setdefault("lr", {})[backbone] = {"value": 3e-4, "evidence": {}}
        path.write_text(json.dumps(data))
        print(f"choose-lr: {backbone} ok")
    elif cmd == "choose-composites":
        path = work / "results" / "choices.json"
        data = json.loads(path.read_text())
        data["composite_n_factor"] = {"value": 1.0, "evidence": {}}
        path.write_text(json.dumps(data))
        write_split(work / "runs" / "E3-A", 0)  # the winning sweep run becomes split 0
        print("choose-composites: 1x")
    with open(data_root.parent / "calls.jsonl", "a") as log:
        log.write(json.dumps({"cmd": cmd, "args": rest, "device": device, "cvd": os.environ.get("CUDA_VISIBLE_DEVICES"),
                              "order": os.environ.get("CUDA_DEVICE_ORDER"), "start": started, "end": time.time()}) + "\\n")
''')


def calls(runner):
    path = runner.cfg.data_root.parent / "calls.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


@pytest.fixture
def fake_env(monkeypatch):
    monkeypatch.setenv("FAKE_SLEEP", "0.15")
    monkeypatch.delenv("FAKE_FAIL", raising=False)
    monkeypatch.delenv("FAKE_GPU", raising=False)


def test_stream_prefixes_and_fails_loudly(lib, tmp_path, capsys):
    runner = make_runner(lib, tmp_path, gpus=1)
    runner.stream([sys.executable, "-c", "print('a'); print('b')"], prefix="[X] ")
    out = capsys.readouterr().out
    assert "[X] a" in out and "[X] b" in out
    assert "[X] a" in runner.cfg.log_path.read_text()
    with pytest.raises(lib.RunnerError, match="exit code 3"):
        runner.stream([sys.executable, "-c", "import sys; sys.exit(3)"])


@pytest.mark.skipif(not hasattr(os, "killpg"), reason="process groups are POSIX only")
def test_stream_ends_when_the_command_exits_even_if_a_leftover_child_holds_the_pipe(lib, tmp_path, capsys):
    """The 2026-10-13 Kaggle hang: the command was finished but a deadlocked worker kept stdout open, so a loop over the
    pipe never ended. `stream` must return soon after the command exits and kill the leftover."""
    runner = make_runner(lib, tmp_path, gpus=1)
    leftover = "import subprocess, sys; p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)']); print('child', p.pid)"
    started = time.monotonic()
    runner.stream([sys.executable, "-c", leftover], prefix="[L] ")
    assert time.monotonic() - started < 30
    out = capsys.readouterr().out
    assert "left processes holding its output; stopping them" in out
    pid = int(next(line for line in out.splitlines() if line.startswith("[L] child")).split()[-1])
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline and pid_alive(pid):
        time.sleep(0.1)
    assert not pid_alive(pid), "the leftover child was killed"


def pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    try:  # a killed child that nobody reaped yet is a zombie: dead for our purpose
        with open(f"/proc/{pid}/stat") as handle:
            return handle.read().split()[2] != "Z"
    except OSError:
        return True


def test_script_command_line_and_gpu_pinning(lib, tmp_path):
    seen = []

    class FakePopen:
        def __init__(self, cmd, **kwargs):
            seen.append((cmd, kwargs["env"]))
            self.stdout = iter(["ok\n"])

        def wait(self):
            return 0

    runner = make_runner(lib, tmp_path, gpus=2)
    runner.popen = FakePopen
    runner.script("run", "--exp", "E1-FF", "--splits", "2")
    runner.script("run", "--exp", "E1-FF", gpu=1, num_workers=2)
    (cmd0, env0), (cmd1, env1) = seen
    assert cmd0[1:5] == [str(runner.cfg.script_path), "--data-root", str(runner.cfg.data_root), "--device"] and cmd0[5] == "cuda"
    assert "CUDA_VISIBLE_DEVICES" not in env0 or env0["CUDA_VISIBLE_DEVICES"] == os.environ.get("CUDA_VISIBLE_DEVICES")
    assert env1["CUDA_VISIBLE_DEVICES"] == "1" and env1["CUDA_DEVICE_ORDER"] == "PCI_BUS_ID" and cmd1[-2:] == ["--num-workers", "2"]


def test_run_batch_syncs_after_every_split(lib, tmp_path, fake_env):
    runner = make_runner(lib, tmp_path, gpus=2, script_body=FAKE_SCRIPT)
    synced = []
    real_sync = runner.sync_runs
    runner.sync_runs = lambda keep=None: (synced.append(sorted(p.name for p in (runner.cfg.runs_dir / "E1-FF").glob("split_*"))), real_sync(keep))
    runner.run_batch("E1-FF", splits=(0, 1, 2))
    assert synced == [["split_0"], ["split_0", "split_1"], ["split_0", "split_1", "split_2"]]
    assert "runs/E1-FF/split_2/metrics.json" in zipfile.ZipFile(runner.cfg.out_zip).namelist()
    assert all(c["cvd"] is None or c["cvd"] == os.environ.get("CUDA_VISIBLE_DEVICES") for c in calls(runner))
    runner.run_batch("E1-FF", splits=(0, 1, 2))  # a rerun skips finished splits
    assert sum(1 for c in calls(runner)) == 6


def test_run_parallel_uses_one_gpu_per_experiment_and_syncs_per_split(lib, tmp_path, fake_env, capsys):
    runner = make_runner(lib, tmp_path, gpus=2, script_body=FAKE_SCRIPT)
    synced = []
    real_sync = runner.sync_runs
    runner.sync_runs = lambda keep=None: (synced.append(1), real_sync(keep))
    runner.run_parallel(["E2-cnx-U", "E2-swin-U"], splits=(0, 1, 2))
    made = calls(runner)
    by_exp = {}
    for c in made:
        by_exp.setdefault(c["args"][c["args"].index("--exp") + 1], set()).add(c["cvd"])
    assert by_exp == {"E2-cnx-U": {"0"}, "E2-swin-U": {"1"}} or by_exp == {"E2-cnx-U": {"1"}, "E2-swin-U": {"0"}}
    assert all(c["order"] == "PCI_BUS_ID" and c["args"][-2:] == ["--num-workers", "2"] and c["device"] == "cuda" for c in made)
    assert len(synced) == 6  # after each completed split of either experiment
    out = capsys.readouterr().out
    assert "[E2-cnx-U|gpu" in out and "[E2-swin-U|gpu" in out
    # the two experiments really overlapped in time
    cnx = [c for c in made if "E2-cnx-U" in c["args"]]
    swin = [c for c in made if "E2-swin-U" in c["args"]]
    assert min(c["start"] for c in swin) < max(c["end"] for c in cnx) and min(c["start"] for c in cnx) < max(c["end"] for c in swin)
    names = zipfile.ZipFile(runner.cfg.out_zip).namelist()
    assert all(f"runs/{e}/split_{s}/metrics.json" in names for e in ("E2-cnx-U", "E2-swin-U") for s in (0, 1, 2))


def test_run_parallel_falls_back_to_sequential_with_one_gpu(lib, tmp_path, fake_env, capsys):
    runner = make_runner(lib, tmp_path, gpus=1, script_body=FAKE_SCRIPT)
    runner.run_parallel(["E2-cnx-U", "E2-swin-U"], splits=(0, 1))
    assert "one after the other" in capsys.readouterr().out
    made = calls(runner)
    assert len(made) == 4 and all(c["cvd"] is None for c in made)
    assert all(a["end"] <= b["start"] + 0.01 for a, b in zip(made, made[1:]))  # strictly sequential


def test_run_parallel_failure_of_one_experiment_does_not_stop_the_other(lib, tmp_path, fake_env, monkeypatch):
    monkeypatch.setenv("FAKE_FAIL", "E2-swin-U:1")
    runner = make_runner(lib, tmp_path, gpus=2, script_body=FAKE_SCRIPT)
    with pytest.raises(lib.RunnerError, match="E2-swin-U"):
        runner.run_parallel(["E2-cnx-U", "E2-swin-U"], splits=(0, 1, 2))
    names = zipfile.ZipFile(runner.cfg.out_zip).namelist()
    assert all(f"runs/E2-cnx-U/split_{s}/metrics.json" in names for s in (0, 1, 2))  # the other GPU finished everything
    assert "runs/E2-swin-U/split_0/metrics.json" in names and "runs/E2-swin-U/split_2/metrics.json" not in names


def test_more_experiments_than_gpus_reuse_the_free_gpu(lib, tmp_path, fake_env):
    runner = make_runner(lib, tmp_path, gpus=2, script_body=FAKE_SCRIPT)
    runner.run_parallel(["E1-WF", "E1-FF", "E3-A"], splits=(0,))
    assert len(calls(runner)) == 3 and {c["cvd"] for c in calls(runner)} <= {"0", "1"}


def test_batch3_core_runs_sweeps_in_parallel_then_choose_lr_one_by_one_then_the_runs(lib, tmp_path, fake_env):
    runner = make_runner(lib, tmp_path, gpus=2, script_body=FAKE_SCRIPT)
    runner.cfg.choices_path.parent.mkdir(parents=True, exist_ok=True)
    runner.cfg.choices_path.write_text(json.dumps({"input_mode": {"value": "rect"}, "lr": {"resnet50": {"value": 1e-4}}}))
    assert lib.run_selected(runner, "batch3-core", ["batch3-core"]) is True
    made = calls(runner)
    kinds = [("sweep" if "--sweep-lr" in c["args"] else c["cmd"]) for c in made]
    first_run = next(i for i, k in enumerate(kinds) if k == "run")
    assert sorted(kinds[:2]) == ["sweep", "sweep"] and kinds[2:4] == ["choose-lr", "choose-lr"] and first_run == 4
    sweeps, chooses = made[:2], made[2:4]
    assert {c["cvd"] for c in sweeps} == {"0", "1"}
    # the race by construction: choose-lr (the only writer of choices.json) starts after both sweeps ended and never overlaps itself
    assert max(c["end"] for c in sweeps) <= min(c["start"] for c in chooses)
    assert chooses[0]["end"] <= chooses[1]["start"] + 0.01
    assert all(c["cvd"] is None for c in chooses)
    assert len(made) == 2 + 2 + 10  # 2 sweeps, 2 choose-lr, then 2 experiments x 5 splits
    choices = json.loads(runner.cfg.choices_path.read_text())
    assert set(choices["lr"]) == {"resnet50", "convnext_tiny", "swin_t"}
    with zipfile.ZipFile(runner.cfg.out_zip) as archive:
        names = archive.namelist()
    assert "results/choices.json" in names and "runs/sweep/E2-cnx-U_lr1e-4/split_0/metrics.json" in names
    assert "runs/E2-swin-U/split_4/metrics.json" in names


def test_batch3_core_skips_sweeps_whose_lr_is_known_and_needs_the_resnet_choice(lib, tmp_path, fake_env):
    runner = make_runner(lib, tmp_path, gpus=2, script_body=FAKE_SCRIPT)
    runner.cfg.choices_path.parent.mkdir(parents=True, exist_ok=True)
    full = {"input_mode": {"value": "rect"}, "lr": {n: {"value": 1e-4} for n in ("resnet50", "convnext_tiny", "swin_t")}}
    runner.cfg.choices_path.write_text(json.dumps(full))
    lib.plan_batch3_core(runner)
    assert not [c for c in calls(runner) if "--sweep-lr" in c["args"] or c["cmd"] == "choose-lr"]
    runner.cfg.choices_path.write_text(json.dumps({"input_mode": {"value": "rect"}}))
    with pytest.raises(lib.RunnerError, match="lr.resnet50"):
        runner.show_choices("input_mode", "lr.resnet50")


BATCH4_CHOICES = {"input_mode": {"value": "rect"}, "backbone": {"value": "swin_t"},
                  "lr": {n: {"value": 1e-4} for n in ("resnet50", "convnext_tiny", "swin_t")}}


def test_batch4_sweeps_composites_then_chooses_then_spreads_the_splits_over_both_gpus(lib, tmp_path, fake_env):
    runner = make_runner(lib, tmp_path, gpus=2, script_body=FAKE_SCRIPT)
    runner.cfg.choices_path.parent.mkdir(parents=True, exist_ok=True)
    runner.cfg.choices_path.write_text(json.dumps(BATCH4_CHOICES))
    assert lib.run_selected(runner, "batch4", ["batch4"]) is True
    made = calls(runner)
    kinds = [("sweep" if "--sweep-composites" in c["args"] else c["cmd"]) for c in made]
    assert kinds[:2] == ["sweep", "choose-composites"] and kinds[2:] == ["run"] * 5
    runs = made[2:]
    assert {c["cvd"] for c in runs} == {"0", "1"}, "splits are spread over both GPUs"
    assert sorted(int(c["args"][c["args"].index("--splits") + 1]) for c in runs) == [0, 1, 2, 3, 4]
    assert json.loads(runner.cfg.choices_path.read_text())["composite_n_factor"]["value"] == 1.0
    names = zipfile.ZipFile(runner.cfg.out_zip).namelist()
    assert "runs/sweep/E3-A_n0.5/split_0/metrics.json" in names and "results/choices.json" in names
    assert all(f"runs/E3-A/split_{s}/metrics.json" in names for s in range(5))


def test_batch4_skips_the_sweep_once_the_factor_is_chosen_and_batch4_wf_needs_it(lib, tmp_path, fake_env):
    runner = make_runner(lib, tmp_path, gpus=2, script_body=FAKE_SCRIPT)
    runner.cfg.choices_path.parent.mkdir(parents=True, exist_ok=True)
    runner.cfg.choices_path.write_text(json.dumps(BATCH4_CHOICES))
    with pytest.raises(lib.RunnerError, match="composite_n_factor"):
        lib.plan_batch4_wf(runner)
    runner.cfg.choices_path.write_text(json.dumps({**BATCH4_CHOICES, "composite_n_factor": {"value": 0.5}}))
    lib.plan_batch4(runner)
    lib.plan_batch4_wf(runner)
    made = calls(runner)
    assert not [c for c in made if "--sweep-composites" in c["args"] or c["cmd"] == "choose-composites"]
    assert sorted({c["args"][c["args"].index("--exp") + 1] for c in made}) == ["E3-A", "E3-A-WF"] and len(made) == 10


def test_run_splits_parallel_with_one_gpu_is_run_batch(lib, tmp_path, fake_env):
    runner = make_runner(lib, tmp_path, gpus=1, script_body=FAKE_SCRIPT)
    runner.run_splits_parallel("E3-A", (0, 1))
    made = calls(runner)
    assert len(made) == 2 and all(c["cvd"] is None for c in made)


def test_run_selected_skips_unlisted_and_syncs_even_when_the_batch_fails(lib, tmp_path, fake_env, monkeypatch, capsys):
    runner = make_runner(lib, tmp_path, gpus=2, script_body=FAKE_SCRIPT)
    assert lib.run_selected(runner, "batch2", ["batch3-core"]) is False
    assert "not in BATCHES_TO_RUN" in capsys.readouterr().out and calls(runner) == []
    monkeypatch.setenv("FAKE_FAIL", "E7-X:1")
    with pytest.raises(lib.RunnerError, match="exit code 1"):
        lib.run_selected(runner, "run:E7-X", ["run:E7-X"])
    names = zipfile.ZipFile(runner.cfg.out_zip).namelist()  # split 0 finished before the failure and is in the zip
    assert "runs/E7-X/split_0/metrics.json" in names and "runs/E7-X/split_1/metrics.json" not in names
    lib.run_generic(runner, ["batch3", "parallel:E8-A,E8-B"])  # only the generic entries run here


def test_batch_names(lib):
    lib.validate_batches(["batch3-core", "batch3", "run:E3-A", "parallel:E3-A,E3-A-WF", "sanity"])
    with pytest.raises(lib.RunnerError, match="unknown entries"):
        lib.validate_batches(["batch3-core", "batch33"])
    with pytest.raises(lib.RunnerError, match="at least two"):
        lib.validate_batches(["parallel:E3-A"])
    with pytest.raises(lib.RunnerError, match="needs an experiment"):
        lib.validate_batches(["run:"])
    assert lib.expand_batches(["batch3", "batch3-core"]) == ["batch3-core", "batch3-wf"]


# ---------------------------------------------------------------------------
# Contract with the generated script
# ---------------------------------------------------------------------------


def test_script_selects_gpus_only_through_cuda_visible_devices(gs_text):
    """`--device cuda` must mean 'the visible GPU 0'; an explicit cuda:N anywhere would defeat CUDA_VISIBLE_DEVICES."""
    assert "cuda:" not in gs_text.replace("device_type=", "")
    assert "set_device" not in gs_text and "device_count" not in gs_text and "DataParallel" not in gs_text


def test_run_never_writes_choices(gs_text):
    """Two concurrent `run` processes must not race on choices.json: write_choice is called by the choose-* and gate commands only."""
    import re

    writers = re.findall(r"^def (\w+)\(.*\n(?:(?:    .*|)\n)*?    .*write_choice\(", gs_text, flags=re.M)
    assert writers and not set(writers) & {"run_command", "cmd_run", "run_split", "train_with_fallback"}, writers


@pytest.fixture(scope="module")
def gs_text():
    return (REPO_ROOT / "group3-starvenus.py").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# The whole notebook in local mode
# ---------------------------------------------------------------------------


def run_notebook_cells(namespace):
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            exec(compile("".join(cell["source"]), f"<cell {cell['id']}>", "exec"), namespace)


@pytest.mark.skipif(not (REPO_ROOT / "Dhan-Shomadhan" / "Dhan-Shomadhan_picture_Information.csv").is_file(), reason="dataset not in the checkout")
def test_notebook_runs_end_to_end_in_local_mode(tmp_path, monkeypatch):
    monkeypatch.setenv("RUNNER_PLATFORM", "local")
    monkeypatch.setenv("RUNNER_REPO", str(REPO_ROOT))
    monkeypatch.setenv("RUNNER_OUT_BASE", str(tmp_path))
    monkeypatch.setenv("RUNNER_BATCHES", "")
    monkeypatch.setenv("RUNNER_SKIP", "smoke,prepare")
    namespace = {"__name__": "runner_e2e"}
    sys.modules["runner_e2e"] = types.ModuleType("runner_e2e")
    try:
        run_notebook_cells(namespace)
    finally:
        sys.modules.pop("runner_e2e", None)
    assert namespace["PLATFORM"] == "local" and namespace["BATCHES_TO_RUN"] == []
    env = json.loads((tmp_path / "out" / "env.json").read_text())
    assert env["platform"] == "local" and env["python"] and env["torch_pin_honoured"] is None
    assert env["dataset_layout"]["kind"] == "local"
    with zipfile.ZipFile(tmp_path / "out.zip") as archive:
        assert "env.json" in archive.namelist() and "runner_log.txt" in archive.namelist()
    # the helpers drive the real generated script with the right global flags
    namespace["R"].script("--help")
    log = (tmp_path / "out" / "runner_log.txt").read_text()
    assert "--data-root" in log and "--device auto" in log and "usage:" in log


def test_cells_run_on_a_fake_kaggle_session_up_to_the_dataset(lib, tmp_path, monkeypatch):
    """The Kaggle code path of the setup cells (inputs, copy, restore, env.json, out.zip) on a fake /kaggle tree."""
    kaggle = tmp_path / "kaggle"
    code = make_code_dataset(kaggle / "input" / "csci935-code")
    prior = tmp_path / "prior"
    write_run(prior / "runs", "E0-rect", 0)
    lib.make_zip(prior, code / "runs.zip")
    src = make_dataset(tmp_path / "src")
    (kaggle / "input" / "csci935-dhan-shomadhan").mkdir(parents=True)
    make_zip(kaggle / "input" / "csci935-dhan-shomadhan" / "Dhan-Shomadhan.zip", src)

    cfg = lib.resolve_config("kaggle", "group3-starvenus", kaggle_root=kaggle, min_free_gb=0)
    inputs = lib.discover_kaggle_inputs(cfg.input_root, cfg.script_name, N)
    cfg.script_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(inputs["script"], cfg.script_path)
    layout = lib.materialise_dataset(inputs["data_kind"], inputs["data_source"], cfg.data_root, cfg.scratch, N)
    lib.restore_from_code_dataset(inputs, cfg.work)
    record = lib.build_env_record(cfg, lib.parse_gpus(T4_X2), good_info(), {"honoured": True, "how": "preinstalled"}, layout)
    cfg.env_json_path.parent.mkdir(parents=True, exist_ok=True)
    cfg.env_json_path.write_text(json.dumps(record))
    runner = lib.Runner(cfg, lib.parse_gpus(T4_X2))
    runner.refresh_zip()
    assert lib.finished_splits(cfg.runs_dir) == {"E0-rect": [0]} and runner.has_choice("input_mode")
    assert cfg.out_dir.parent not in cfg.data_root.parents  # the dataset copy is not part of the saved output
    assert "env.json" in zipfile.ZipFile(cfg.out_zip).namelist() and record["dataset_layout"]["kind"] == "zip"
