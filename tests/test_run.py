"""Phase 03 T3.4-T3.6: run folders, idempotence, sweep + choose-lr, dev routing, predict."""

import csv
import json

import pytest
import torch

from conftest import make_cache


@pytest.fixture
def prepared(gs, tmp_path):
    """A tiny data root with index, cache and split 0 (no dataset images needed)."""
    root = tmp_path / "root"
    records = make_cache(gs, root, n=20)
    gs.write_index(root, records)
    gs.write_json(gs.split_path(root, 0), gs.smoke_split(records))
    return root


def tiny_resolved(gs, lr=3e-4, **changes):
    resolved = gs.resolve_experiment("E0-rect", gs.Choices(gs.Path("none.json"), {}), lr=lr)
    config = gs.replace(resolved.config, pretrained=False, **{**gs.FAST_CONFIG, **changes})
    return gs.replace(resolved, config=config)


OPTIONS = dict(device="cpu", num_workers=0)


def test_run_split_writes_the_complete_run_folder(gs, prepared):
    out = prepared / "_work" / "runs" / "E0-rect" / "split_0"
    lines = []
    result = gs.run_split(tiny_resolved(gs), 0, data_root=prepared, out_dir=out, options=gs.RunOptions(**OPTIONS), log=lines.append)
    assert result["status"] == "done"
    for name in (*gs.RUN_FILES, "best.pt"):
        assert (out / name).is_file(), name
    assert not list(out.glob("*.tmp*")), "atomic writes leave no temporary files"

    metrics = json.loads((out / "metrics.json").read_text())
    split = gs.load_split(prepared, 0)
    assert metrics["split_sha256"] == split["sha256"] and metrics["wall_time_s"] > 0
    assert metrics["exp_id"] == "E0-rect" and metrics["n_test"] == len(split["test"])
    for part in ("val", "test"):
        assert set(metrics[part]) == {"white", "field", "mixed", "domain_balanced"}
        mixed = metrics[part]["mixed"]
        assert {"accuracy", "macro_f1", "per_class", "confusion_matrix"} <= set(mixed)
        assert len(mixed["confusion_matrix"]) == 5 and set(mixed["per_class"]) == set(gs.CLASS_NAMES)
    bal = metrics["test"]["domain_balanced"]["macro_f1"]
    assert bal == pytest.approx((metrics["test"]["white"]["macro_f1"] + metrics["test"]["field"]["macro_f1"]) / 2)

    with open(out / "predictions_test.csv", newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == ["filename", "domain", "true", "pred", "p0", "p1", "p2", "p3", "p4"]
    assert len(rows) - 1 == len(split["test"])
    assert all(abs(sum(map(float, r[4:])) - 1) < 1e-4 and r[2] in gs.CLASS_NAMES and r[3] in gs.CLASS_NAMES for r in rows[1:])
    with open(out / "history.csv", newline="") as handle:
        history = list(csv.DictReader(handle))
    assert [h["stage"] for h in history] == ["lp", "ft"] and set(gs.HISTORY_COLUMNS) == set(history[0])

    config = json.loads((out / "config.json").read_text())
    assert config["experiment"]["exp_id"] == "E0-rect" and config["split"] == 0
    env = json.loads((out / "env.json").read_text())
    assert {"python", "torch", "torchvision", "opencv", "device", "gpu"} <= set(env)
    checkpoint = torch.load(out / "best.pt", map_location="cpu", weights_only=True)
    assert checkpoint["backbone"] == "resnet50" and checkpoint["class_names"] == list(gs.CLASS_NAMES)


def test_finished_splits_are_skipped_stale_ones_retrained_and_force_retrains(gs, prepared):
    out = prepared / "_work" / "runs" / "E0-rect" / "split_0"
    options = gs.RunOptions(**OPTIONS)
    gs.run_split(tiny_resolved(gs), 0, data_root=prepared, out_dir=out, options=options, log=lambda _: None)
    stamp = (out / "metrics.json").stat().st_mtime_ns

    lines = []
    again = gs.run_split(tiny_resolved(gs), 0, data_root=prepared, out_dir=out, options=options, log=lines.append)
    assert again["status"] == "skipped" and (out / "metrics.json").stat().st_mtime_ns == stamp and "skipped" in lines[0]

    # a different batch size is a system setting, not a different experiment
    other = tiny_resolved(gs, batch_size=4)
    assert gs.run_split(other, 0, data_root=prepared, out_dir=out, options=options, log=lambda _: None)["status"] == "skipped"

    lines = []
    changed = gs.run_split(tiny_resolved(gs, lr=1e-4), 0, data_root=prepared, out_dir=out, options=options, log=lines.append)
    assert changed["status"] == "done" and any("stale" in line and "config" in line for line in lines)

    forced = gs.run_split(tiny_resolved(gs, lr=1e-4), 0, data_root=prepared, out_dir=out,
                          options=gs.RunOptions(force=True, **OPTIONS), log=lambda _: None)
    assert forced["status"] == "done"

    split = gs.load_split(prepared, 0)
    metrics = json.loads((out / "metrics.json").read_text())
    metrics["split_sha256"] = "0" * 64
    (out / "metrics.json").write_text(json.dumps(metrics))
    state, reason = gs.result_state(out, split["sha256"], metrics["config_fingerprint"])
    assert state == "stale" and "split" in reason


def test_missing_cache_and_unprepared_data_give_clear_errors(gs, prepared, tmp_path):
    (gs.cache_dir(prepared) / gs.load_index(prepared)[0].filename).unlink()
    with pytest.raises(gs.DatasetError, match="run `prepare`"):
        gs.run_split(tiny_resolved(gs), 0, data_root=prepared, out_dir=tmp_path / "o", options=gs.RunOptions(**OPTIONS), log=lambda _: None)
    with pytest.raises(gs.DatasetError, match="prepare"):
        gs.run_split(tiny_resolved(gs), 0, data_root=tmp_path / "empty", out_dir=tmp_path / "o2", options=gs.RunOptions(**OPTIONS), log=lambda _: None)


def run_cli(gs, root, *args):
    return gs.run_cli(["run", "--data-root", str(root), "--device", "cpu", "--num-workers", "0", *args])


def test_fast_run_works_for_any_experiment_id_and_writes_to_scratch(gs, prepared, capsys):
    assert run_cli(gs, prepared, "--exp", "E1-FF", "--splits", "0", "--fast") == 0
    out = capsys.readouterr().out
    assert "placeholder" in out and "never a result" in out
    scratch = prepared / "_work" / "runs" / "scratch" / "E1-FF_fast" / "split_0"
    assert (scratch / "metrics.json").is_file()
    assert not (prepared / "_work" / "runs" / "E1-FF").exists()
    assert json.loads((scratch / "metrics.json").read_text())["fast"] is True
    assert run_cli(gs, prepared, "--exp", "E1-FF", "--splits", "0", "--fast") == 0
    assert "skipped" in capsys.readouterr().out


def test_real_run_needs_a_chosen_lr_and_says_how_to_get_one(gs, prepared, capsys):
    assert run_cli(gs, prepared, "--exp", "E0-rect", "--splits", "0") == 1
    err = capsys.readouterr().err
    assert "run: FAIL" in err and "choose-lr" in err and "lr[resnet50]" in err


def test_later_phase_rows_fail_cleanly(gs, prepared, capsys):
    assert run_cli(gs, prepared, "--exp", "E4-B", "--fast", "--splits", "0") == 1
    err = capsys.readouterr().err
    assert "boxes.json does not exist" in err and "run --exp S-seg --splits 0" in err
    assert run_cli(gs, prepared, "--exp", "nope") == 1
    assert "unknown experiment" in capsys.readouterr().err


def test_dev_overrides_never_write_to_the_results_folder(gs, prepared, capsys):
    args = ("--exp", "E0-rect", "--splits", "0", "--lr", "3e-4", "--epochs", "1", "--stage1-epochs", "1", "--fast")
    assert run_cli(gs, prepared, *args) == 0
    runs = prepared / "_work" / "runs"
    assert sorted(p.name for p in runs.iterdir()) == ["scratch"]
    config = json.loads((runs / "scratch" / "E0-rect_fast" / "split_0" / "config.json").read_text())
    assert config["overrides"]["lr"] == 3e-4 and config["overrides"]["fast"] is True


def test_sweep_runs_split_zero_at_both_learning_rates(gs, prepared, capsys):
    assert run_cli(gs, prepared, "--exp", "E0-rect", "--sweep-lr", "--splits", "3", "--fast") == 0
    out = capsys.readouterr().out
    assert "split 0 only" in out
    scratch = prepared / "_work" / "runs" / "scratch"
    assert sorted(p.name for p in scratch.iterdir()) == ["E0-rect_lr1e-4", "E0-rect_lr3e-4"]
    assert all((scratch / name / "split_0" / "metrics.json").is_file() for name in ("E0-rect_lr1e-4", "E0-rect_lr3e-4"))
    assert run_cli(gs, prepared, "--exp", "E0-rect", "--sweep-lr", "--lr", "1e-4") == 1


def make_sweep(gs, root, backbone="resnet50", scores=(0.5, 0.7), **metric_overrides):
    exp = gs.SWEEP_EXPERIMENT[backbone]
    for lr, score in zip(gs.SWEEP_LRS, scores):
        folder = gs.split_dir(gs.sweep_dir(root) / gs.sweep_run_name(exp, lr), 0)
        metrics = {"backbone": backbone, "lr": lr, "split_sha256": "abc", "fast": False, "overrides": {},
                   "val": {"mixed": {"macro_f1": score}}, **metric_overrides}
        gs.write_json(folder / "metrics.json", metrics)


def test_choose_lr_records_the_better_validation_lr(gs, tmp_path):
    root = tmp_path / "r"
    make_sweep(gs, root, scores=(0.5, 0.7))
    lines = []
    gs.choose_lr(root, "resnet50", out=lines.append)
    choices = gs.load_choices(root)
    assert choices.get("lr", "resnet50") == 3e-4
    entry = json.loads(choices.path.read_text())["lr"]["resnet50"]
    assert entry["evidence"]["val_mixed_macro_f1"] == {"1e-4": 0.5, "3e-4": 0.7} and entry["evidence"]["experiment"] == "E0-rect"
    assert "3e-4" in lines[0]
    make_sweep(gs, root, scores=(0.8, 0.7))
    gs.choose_lr(root, "resnet50", out=lambda _: None)
    assert gs.load_choices(root).get("lr", "resnet50") == 1e-4
    make_sweep(gs, root, scores=(0.7, 0.7))
    gs.choose_lr(root, "resnet50", out=lambda _: None)
    assert gs.load_choices(root).get("lr", "resnet50") == 1e-4, "ties go to the smaller lr"


def test_choose_lr_refuses_missing_fast_and_dev_runs(gs, tmp_path, capsys):
    root = tmp_path / "r"
    with pytest.raises(gs.ExperimentError, match=r"run --exp E0-rect --sweep-lr"):
        gs.choose_lr(root, "resnet50")
    make_sweep(gs, root, fast=True)
    with pytest.raises(gs.ExperimentError, match="not a real sweep run"):
        gs.choose_lr(root, "resnet50")
    make_sweep(gs, root, overrides={"epochs": 1})
    with pytest.raises(gs.ExperimentError, match="not a real sweep run"):
        gs.choose_lr(root, "resnet50")
    assert gs.run_cli(["choose-lr", "--backbone", "swin_t", "--data-root", str(root)]) == 1
    assert "choose-lr: FAIL" in capsys.readouterr().err


def test_predict_prints_probabilities_from_a_run_folder(gs, prepared, capsys):
    out = prepared / "_work" / "runs" / "E0-rect" / "split_0"
    gs.run_split(tiny_resolved(gs), 0, data_root=prepared, out_dir=out, options=gs.RunOptions(**OPTIONS), log=lambda _: None)
    image = gs.cache_dir(prepared) / gs.load_index(prepared)[0].filename
    capsys.readouterr()
    assert gs.run_cli(["predict", "--data-root", str(prepared), "--device", "cpu", "--exp", "E0-rect", "--image", str(image)]) == 0
    text = capsys.readouterr().out
    assert "prediction" in text and all(name in text for name in gs.CLASS_NAMES)
    percentages = [float(line.split()[-2].rstrip("%")) if line.rstrip().endswith("#") else float(line.split()[-1].rstrip("%"))
                   for line in text.splitlines() if line.startswith("  ") and any(n in line for n in gs.CLASS_NAMES)]
    assert abs(sum(percentages) - 100) < 1
    assert gs.run_cli(["predict", "--data-root", str(prepared), "--device", "cpu", "--run-dir", str(out), "--image", str(image)]) == 0


def test_predict_errors_are_clear(gs, prepared, capsys):
    image = gs.cache_dir(prepared) / gs.load_index(prepared)[0].filename
    base = ["predict", "--data-root", str(prepared), "--device", "cpu", "--image", str(image)]
    assert gs.run_cli(base) == 1
    assert "recommended" in capsys.readouterr().err
    assert gs.run_cli([*base, "--exp", "E0-rect"]) == 1
    assert "best.pt" in capsys.readouterr().err
    assert gs.run_cli(["predict", "--data-root", str(prepared), "--exp", "E0-rect", "--image", "missing.jpg"]) == 1
    assert "does not exist" in capsys.readouterr().err


def test_alias_resolves_to_the_winning_e0_run_folder(gs, tmp_path):
    root = tmp_path / "r"
    gs.write_choice(root, "input_mode", "pad")
    choices = gs.load_choices(root)
    assert gs.run_folder_name("E1-U", choices) == "E0-pad" and gs.run_folder_name("E1-WW", choices) == "E1-WF"
