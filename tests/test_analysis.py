"""Phase 04/07: aggregation over splits, gates G0 and G1, result tables, figures, cases and findings.

Most tests build a synthetic data root (committed-split stand-ins, a choices.json and metrics.json files whose
fingerprints are the ones the registry produces), so G1, which needs E2 runs that do not exist yet, is covered too.
The last tests read the committed E0 runs and pin the numbers that gate G0 decided on.
"""

import csv
import json
import math
import shutil
from collections import Counter

import numpy as np
import pytest

from conftest import REPO_ROOT

SPREAD = np.array([-0.02, -0.01, 0.0, 0.01, 0.02])  # sample std (ddof=1) = 0.01581
STD = float(np.std(SPREAD, ddof=1))
ALL_LRS = {"resnet50": 1e-4, "convnext_tiny": 1e-4, "swin_t": 3e-4}
CLASSES = ("Brown Spot", "Leaf Scald", "Rice Blast", "Rice Tungro", "Sheath Blight")
KAGGLE_ENV = {"device": "cuda", "gpu": "Tesla T4", "torch": "2.11.0+cu128", "python": "3.13.15", "torch_home": "/kaggle/tmp/x/_work/weights",
              "platform": "Linux-6.18-x86_64"}
MAC_ENV = {"device": "mps", "gpu": "Apple MPS", "torch": "2.11.0", "python": "3.12.13", "torch_home": "Dhan-Shomadhan/_work/weights",
           "platform": "macOS-26.5-arm64-arm-64bit"}


def synthetic_confusion(n_per_class: int) -> list:
    """Every class right except class 0 (Brown Spot), whose first image is taken for class 1 (Leaf Scald)."""
    matrix = np.eye(5, dtype=int) * n_per_class
    matrix[0, 0] -= 1
    matrix[0, 1] += 1
    return matrix.tolist()


def per_class_block(f1, support):
    """Class i has F1 f1 + 0.01 * (i - 2) (so their mean is f1), precision 0.02 above and recall 0.02 below it."""
    return {cls: {"precision": f1 + 0.01 * (i - 2) + 0.02, "recall": f1 + 0.01 * (i - 2) - 0.02, "f1": f1 + 0.01 * (i - 2), "support": support}
            for i, cls in enumerate(CLASSES)}


def subset_block(mixed, field):
    white = mixed + 0.05
    return {
        "mixed": {"n": 10, "accuracy": mixed + 0.02, "macro_f1": mixed, "per_class": per_class_block(mixed, 2), "confusion_matrix": synthetic_confusion(2)},
        "field": {"n": 5, "accuracy": field + 0.02, "macro_f1": field, "per_class": per_class_block(field, 1), "confusion_matrix": synthetic_confusion(1)},
        "white": {"n": 5, "accuracy": white + 0.02, "macro_f1": white, "per_class": per_class_block(white, 1), "confusion_matrix": synthetic_confusion(1)},
        "domain_balanced": {"accuracy": (field + white) / 2 + 0.02, "macro_f1": (field + white) / 2},
    }


@pytest.fixture
def root(gs, tmp_path):
    """A data root with 5 splits and a choices.json holding input_mode rect and all three learning rates."""
    root = tmp_path / "Dhan-Shomadhan"
    for seed in range(5):
        parts = {"train": [f"a{seed}.jpg"], "val": [f"b{seed}.jpg"], "test": [f"c{seed}.jpg"]}
        sha = gs.split_sha256(seed, parts["train"], parts["val"], parts["test"])
        gs.write_json(gs.split_path(root, seed), {"seed": seed, **parts, "sha256": sha})
    gs.write_json(gs.choices_path(root), {
        "input_mode": {"value": "rect", "evidence": {}},
        "lr": {name: {"value": lr, "evidence": {}} for name, lr in ALL_LRS.items()},
    }, indent=2)
    return root


def write_predictions(gs, folder, split_seed, rows):
    """predictions_test.csv of one split. ``rows``: (filename, domain, true class, predicted class, top probability); the rest of
    the probability goes to the next class."""
    lines = []
    for name, domain, true, pred, top in rows:
        probs = [(1 - top) / 4] * 5
        probs[CLASSES.index(pred)] = top
        lines.append([name, domain, true, pred, *[f"{p:.6f}" for p in probs]])
    gs.write_text_atomic(gs.split_dir(folder, split_seed) / "predictions_test.csv",
                         gs.csv_text(["filename", "domain", "true", "pred", *[f"p{i}" for i in range(5)]], lines))


def add_run(gs, root, exp_id, mixed, field=None, env=None, **tweaks):
    """Write complete synthetic runs for an experiment. ``mixed`` / ``field`` are the mean val mixed / field F1
    (per-split values are mean + SPREAD); test values are val - 0.03. Besides metrics.json each split gets the config.json,
    env.json (``env`` overrides KAGGLE_ENV), history.csv and predictions_test.csv that a real run writes."""
    import dataclasses

    field = mixed - 0.08 if field is None else field
    choices = gs.load_choices(root)
    resolved = gs.resolve_experiment(exp_id, choices)
    folder = gs.runs_dir(root) / gs.run_folder_name(exp_id, choices)
    for seed in range(5):
        metrics = {
            "split": seed, "exp_id": resolved.config.exp_id, "split_sha256": gs.load_split(root, seed)["sha256"],
            "config_fingerprint": gs.expected_fingerprint(resolved.config), "fast": False, "overrides": {},
            "train_time_s": 120.0 * (seed + 1), "seconds_per_epoch": 10.0 + seed, "epochs_run": 20 + seed, "parameters": 25_000_000,
            "val": subset_block(mixed + SPREAD[seed], field + SPREAD[seed]),
            "test": subset_block(mixed + SPREAD[seed] - 0.03, field + SPREAD[seed] - 0.03),
        }
        metrics.update(tweaks)
        gs.write_json(gs.split_dir(folder, seed) / "metrics.json", metrics)
        config = {"format": 1, "requested_exp_id": exp_id, "experiment": dataclasses.asdict(resolved.config), "split": seed, "seed": seed,
                  "seed_offset": 0, "limit": None, "choices_used": resolved.choices_used, "notes": [], "overrides": {},
                  "weights": gs.BACKBONE_SPECS[resolved.config.backbone].weights,
                  "input_size": list(gs.input_size(resolved.config.input_mode)), "config_fingerprint": metrics["config_fingerprint"]}
        gs.write_json(gs.split_dir(folder, seed) / "config.json", config)
        gs.write_json(gs.split_dir(folder, seed) / "env.json", {**KAGGLE_ENV, **(env or {})})
        history = [{"epoch": e, "stage": "lp" if e <= 2 else "ft", "lr": 1e-3, "train_loss": 1.5 / e, "val_loss": 1.0, "val_macro_f1": 0.4 + 0.1 * e + 0.01 * seed,
                    "val_accuracy": 0.5, "val_f1_white": 0.5, "val_f1_field": 0.4, "val_f1_mixed": 0.45, "best": int(e == 4), "seconds": 10.0}
                   for e in range(1, 6)]
        gs.write_text_atomic(gs.split_dir(folder, seed) / "history.csv", gs.history_csv(history))
        write_predictions(gs, folder, seed, [(f"w{seed}.jpg", "white", "Brown Spot", "Brown Spot", 0.9), (f"f{seed}.jpg", "field", "Leaf Scald", "Rice Blast", 0.6)])
    return folder


def add_e0(gs, root, squash, pad, rect, fields=(None, None, None)):
    for mode, mixed, field in zip(("squash", "pad", "rect"), (squash, pad, rect), fields):
        add_run(gs, root, f"E0-{mode}", mixed, field)


def add_g1_candidates(gs, root, resnet, cnx, swin, fields=(None, None, None)):
    for exp_id, mixed, field in zip(("E1-U", "E2-cnx-U", "E2-swin-U"), (resnet, cnx, swin), fields):
        add_run(gs, root, exp_id, mixed, field)


# ---------------------------------------------------------------------------- aggregation


def test_aggregate_mean_std_ddof1_and_per_split_list(gs, root):
    add_run(gs, root, "E0-rect", 0.80)
    exp, problems = gs.load_experiment(root, "E0-rect", gs.load_choices(root))
    assert problems == [] and exp.splits == (0, 1, 2, 3, 4)
    agg = gs.aggregate(exp, "mixed", "macro_f1", "val")
    assert agg.values == pytest.approx(list(0.80 + SPREAD))
    assert agg.mean == pytest.approx(0.80)
    assert agg.std == pytest.approx(STD) and agg.std == pytest.approx(np.std(agg.values, ddof=1))
    assert gs.aggregate(exp, "mixed", "macro_f1").mean == pytest.approx(0.77)  # default part is test
    with pytest.raises(ValueError):
        gs.aggregate(exp, "mixed", "recall", "val")


def test_paired_difference_is_per_split(gs, root):
    add_run(gs, root, "E0-squash", 0.80)
    add_run(gs, root, "E0-rect", 0.78)
    choices = gs.load_choices(root)
    a, b = (gs.load_experiment(root, f"E0-{m}", choices)[0] for m in ("squash", "rect"))
    diff = gs.paired_difference(a, b, "mixed", "macro_f1", "val")
    assert diff.values == pytest.approx([0.02] * 5)
    assert diff.mean == pytest.approx(0.02) and diff.std == pytest.approx(0.0, abs=1e-12)
    assert diff.ahead == 5
    assert gs.paired_difference(b, a, "mixed", "macro_f1", "val").ahead == 0


def test_number_formats(gs):
    f1 = gs.Aggregate(0.9123, 0.0141, [])
    assert gs.format_mean_std(f1, "macro_f1") == "0.912 +- 0.014"
    assert gs.format_mean_std(f1, "accuracy") == "91.2 +- 1.4"
    diff = gs.PairedDifference(0.0129, 0.0186, [], 4)
    assert gs.format_mean_std(diff, "macro_f1", signed=True) == "+0.013 +- 0.019"
    assert gs.format_mean_std(gs.PairedDifference(-0.0129, 0.0186, [], 1), "accuracy", signed=True) == "-1.3 +- 1.9"
    assert gs.format_mean_std(gs.Aggregate(float("nan"), float("nan"), []), "macro_f1") == "n/a"
    mean, std = gs.mean_std([0.5])
    assert mean == 0.5 and math.isnan(std)


def test_load_skips_incomplete_and_mismatched_runs_with_a_warning(gs, root, capsys):
    choices = gs.load_choices(root)
    folder = add_run(gs, root, "E0-rect", 0.8)
    assert gs.load_experiment(root, "E0-rect", choices)[0] is not None

    (folder / "split_3" / "metrics.json").unlink()
    exp, problems = gs.load_experiment(root, "E0-rect", choices)
    assert exp is None and any("split 3" in p and "incomplete" in p for p in problems)

    add_run(gs, root, "E0-rect", 0.8, split_sha256="0" * 64)
    exp, problems = gs.load_experiment(root, "E0-rect", choices)
    assert exp is None and len(problems) == 5 and all("sha256" in p for p in problems)

    add_run(gs, root, "E0-rect", 0.8, config_fingerprint="f" * 64)
    exp, problems = gs.load_experiment(root, "E0-rect", choices)
    assert exp is None and all("fingerprint" in p for p in problems)

    add_run(gs, root, "E0-rect", 0.8, fast=True)
    assert "--fast" in gs.load_experiment(root, "E0-rect", choices)[1][0]

    exp, problems = gs.load_experiment(root, "E0-pad", choices)
    assert exp is None and "pending" in problems[0]

    capsys.readouterr()
    assert gs.load_experiments(root, ["E0-rect", "E0-pad"], choices) == {}
    err = capsys.readouterr().err
    assert "E0-rect: skipped" in err and "E0-pad: skipped" in err


def test_load_ignores_env_json_sweep_scratch_and_retrain_but_flags_unknown_folders(gs, root, capsys):
    choices = gs.load_choices(root)
    add_run(gs, root, "E0-rect", 0.8)
    runs = gs.runs_dir(root)
    (runs / "env.json").write_text("{}")
    (runs / "sweep" / "E0-rect_lr1e-4" / "split_0").mkdir(parents=True)
    (runs / "scratch" / "E0-rect_fast" / "split_0").mkdir(parents=True)
    (runs / "retrain" / "E0-rect" / "split_0").mkdir(parents=True)
    (runs / "mystery" / "split_0").mkdir(parents=True)
    capsys.readouterr()
    results = gs.load_experiments(root, ["E0-rect"], choices)
    err = capsys.readouterr().err
    assert list(results) == ["E0-rect"]
    assert "mystery" in err and "env.json" not in err and "sweep" not in err and "scratch" not in err and "retrain" not in err


def test_unresolvable_experiment_is_reported_not_raised(gs, root):
    data = json.loads(gs.choices_path(root).read_text())
    del data["lr"]["swin_t"]
    gs.choices_path(root).write_text(json.dumps(data))
    exp, problems = gs.load_experiment(root, "E2-swin-U", gs.load_choices(root))
    assert exp is None and "lr[swin_t]" in problems[0]
    exp, problems = gs.load_experiment(root, "E3-A", gs.load_choices(root))
    assert exp is None and "not ready" in problems[0]


def test_e1_u_is_read_from_the_winning_e0_folder(gs, root):
    add_run(gs, root, "E0-rect", 0.8)
    exp, problems = gs.load_experiment(root, "E1-U", gs.load_choices(root))
    assert problems == [] and exp.run_name == "E0-rect" and exp.exp_id == "E1-U" and exp.config.exp_id == "E0-rect"


# ---------------------------------------------------------------------------- gate rules


def aggs(gs, **means):
    return {name: gs.Aggregate(mean, STD, []) for name, mean in means.items()}


def test_g0_prefers_rect_when_the_top_two_are_within_one_std(gs):
    decision = gs.decide_g0(aggs(gs, squash=0.780, pad=0.741, rect=0.767))
    assert decision["value"] == "rect" and decision["decided_by"] == "within one std -> rect"
    assert decision["ranking"] == ["squash", "rect", "pad"]
    assert decision["top_two_gap"] == pytest.approx(0.013)


def test_g0_picks_the_leader_when_it_is_clearly_ahead(gs):
    decision = gs.decide_g0(aggs(gs, squash=0.80, pad=0.70, rect=0.75))
    assert (decision["value"], decision["decided_by"]) == ("squash", "highest mean")
    decision = gs.decide_g0(aggs(gs, squash=0.70, pad=0.60, rect=0.80))
    assert (decision["value"], decision["decided_by"]) == ("rect", "highest mean")


def test_g0_tie_that_does_not_involve_rect_goes_to_the_leader(gs):
    decision = gs.decide_g0(aggs(gs, squash=0.80, pad=0.795, rect=0.70))
    assert decision["value"] == "squash" and "rect is not one of them" in decision["decided_by"]


def test_g0_gap_is_compared_with_the_larger_std_of_the_pair(gs):
    mixed = {"squash": gs.Aggregate(0.80, 0.005, []), "pad": gs.Aggregate(0.70, 0.01, []), "rect": gs.Aggregate(0.78, 0.03, [])}
    assert gs.decide_g0(mixed)["value"] == "rect"  # gap 0.02 <= max(0.005, 0.03)
    mixed["rect"] = gs.Aggregate(0.78, 0.01, [])
    assert gs.decide_g0(mixed)["value"] == "squash"  # gap 0.02 > 0.01


def test_g1_clear_winner_by_mean(gs):
    names = ("resnet50", "convnext_tiny", "swin_t")
    mixed = aggs(gs, resnet50=0.77, convnext_tiny=0.85, swin_t=0.80)
    field = aggs(gs, resnet50=0.9, convnext_tiny=0.5, swin_t=0.6)  # field must not matter when the gap is clear
    decision = gs.decide_g1(mixed, field)
    assert (decision["value"], decision["decided_by"]) == ("convnext_tiny", "highest mean")
    assert set(decision["ranking"]) == set(names)


def test_g1_tie_goes_to_the_higher_field_f1(gs):
    mixed = aggs(gs, resnet50=0.77, convnext_tiny=0.80, swin_t=0.795)
    field = aggs(gs, resnet50=0.60, convnext_tiny=0.60, swin_t=0.70)
    decision = gs.decide_g1(mixed, field)
    assert decision["value"] == "swin_t" and decision["decided_by"] == "within one std -> higher val field macro-F1"
    field = aggs(gs, resnet50=0.60, convnext_tiny=0.72, swin_t=0.70)
    assert gs.decide_g1(mixed, field)["value"] == "convnext_tiny"


def test_g1_tie_only_looks_at_the_top_two(gs):
    mixed = aggs(gs, resnet50=0.80, convnext_tiny=0.795, swin_t=0.70)
    field = aggs(gs, resnet50=0.50, convnext_tiny=0.55, swin_t=0.90)  # swin has the best field F1 but is not in the top two
    assert gs.decide_g1(mixed, field)["value"] == "convnext_tiny"


# ---------------------------------------------------------------------------- gates end to end


def test_gate_g0_writes_choice_with_evidence_and_keeps_other_keys(gs, root):
    add_e0(gs, root, squash=0.80, pad=0.74, rect=0.79, fields=(0.72, 0.60, 0.68))
    before = json.loads(gs.choices_path(root).read_text())
    lines = []
    result = gs.run_gate(root, "g0", out=lines.append)
    after = json.loads(gs.choices_path(root).read_text())
    assert after["input_mode"]["value"] == "rect" == result["value"]
    assert after["lr"] == before["lr"]
    ev = after["input_mode"]["evidence"]
    assert ev["decided_by"] == "within one std -> rect" and ev["ranking"] == ["squash", "rect", "pad"]
    assert "highest validation mixed macro-F1" in ev["rule"] and "prefer rect" in ev["rule"]
    assert set(ev["candidates"]) == {"squash", "pad", "rect"}
    rect = ev["candidates"]["rect"]
    assert rect["val_mixed_macro_f1"]["per_split"] == pytest.approx(list(0.79 + SPREAD))
    assert rect["val_mixed_macro_f1"]["std"] == pytest.approx(STD) and rect["val_field_macro_f1"]["mean"] == pytest.approx(0.68)
    diff = ev["paired_differences"]["squash_minus_rect"]
    assert diff["val_mixed_macro_f1"]["mean"] == pytest.approx(0.01) and diff["val_field_macro_f1"]["splits_ahead"] == 5
    assert set(ev["paired_differences"]) == {"squash_minus_rect", "pad_minus_rect"}
    assert "decision: rect" in "\n".join(lines) and "within one std -> rect" in "\n".join(lines)
    # deterministic: a second run rewrites byte-identical content
    first = gs.choices_path(root).read_bytes()
    gs.run_gate(root, "g0", out=lambda text: None)
    assert gs.choices_path(root).read_bytes() == first


def test_gate_g0_refuses_incomplete_experiments_and_leaves_choices_alone(gs, root):
    add_run(gs, root, "E0-squash", 0.8)
    add_run(gs, root, "E0-rect", 0.79)  # E0-pad missing
    before = gs.choices_path(root).read_bytes()
    with pytest.raises(gs.ExperimentError, match="E0-pad cannot be used"):
        gs.run_gate(root, "g0", out=lambda text: None)
    assert gs.choices_path(root).read_bytes() == before


def test_gate_g1_picks_by_field_f1_in_a_tie_and_records_backbone_and_lr(gs, root):
    add_g1_candidates(gs, root, resnet=0.77, cnx=0.80, swin=0.795, fields=(0.60, 0.62, 0.70))
    gs.run_gate(root, "g1", out=lambda text: None)
    data = json.loads(gs.choices_path(root).read_text())
    assert data["backbone"]["value"] == "swin_t"
    ev = data["backbone"]["evidence"]
    assert ev["decided_by"] == "within one std -> higher val field macro-F1"
    assert ev["lr"]["backbone"] == "swin_t" and ev["lr"]["value"] == 3e-4
    assert gs.load_choices(root).get("lr", "swin_t") == 3e-4  # lr[backbone] stays where the resolver reads it
    assert set(ev["candidates"]) == {"resnet50", "convnext_tiny", "swin_t"}
    assert ev["candidates"]["resnet50"]["experiment"] == "E1-U"
    assert set(ev["paired_differences"]) == {"convnext_tiny_minus_resnet50", "swin_t_minus_resnet50", "swin_t_minus_convnext_tiny"}
    pair = ev["paired_differences"]["convnext_tiny_minus_resnet50"]["val_mixed_macro_f1"]
    assert pair["mean"] == pytest.approx(0.03) and pair["splits_ahead"] == 5
    assert data["input_mode"]["value"] == "rect"


def test_gate_g1_clear_winner_and_missing_candidates(gs, root):
    add_run(gs, root, "E0-rect", 0.77)
    add_run(gs, root, "E2-cnx-U", 0.85)  # swin missing
    before = gs.choices_path(root).read_bytes()
    with pytest.raises(gs.ExperimentError, match="E2-swin-U cannot be used"):
        gs.run_gate(root, "g1", out=lambda text: None)
    assert gs.choices_path(root).read_bytes() == before
    add_run(gs, root, "E2-swin-U", 0.80)
    result = gs.run_gate(root, "g1", out=lambda text: None)
    assert result["value"] == "convnext_tiny" and result["evidence"]["decided_by"] == "highest mean"


def test_gate_command_exit_codes(gs, root, capsys):
    add_e0(gs, root, 0.80, 0.74, 0.79)
    assert gs.run_cli(["--data-root", str(root), "gate", "g0"]) == 0
    assert json.loads(gs.choices_path(root).read_text())["input_mode"]["value"] == "rect"
    assert gs.run_cli(["--data-root", str(root), "gate", "g1"]) == 1  # no E2 runs yet
    assert "gate g1: FAIL" in capsys.readouterr().err
    assert gs.run_cli(["--data-root", str(root), "gate", "g2"]) == 1  # no backbone chosen yet
    err = capsys.readouterr().err
    assert "gate g2: FAIL" in err and "backbone" in err
    assert gs.run_cli(["--data-root", str(root), "gate", "g0", "--cut", "A"]) == 1
    assert "belong to gate g2" in capsys.readouterr().err
    with pytest.raises(SystemExit):
        gs.run_cli(["--data-root", str(root), "gate", "g3"])


# ---------------------------------------------------------------------------- summarize


def read_results(gs, root, name):
    return (gs.results_dir(root) / name).read_text()


def test_summarize_fills_tables_and_marks_missing_rows_pending(gs, root, capsys):
    add_e0(gs, root, squash=0.80, pad=0.74, rect=0.79, fields=(0.72, 0.60, 0.68))
    gs.run_gate(root, "g0", out=lambda text: None)
    capsys.readouterr()
    gs.summarize(root, out=lambda text: None)
    err = capsys.readouterr().err
    for pending in ("E1-WW", "E1-FF", "E1-WF", "E2-cnx-U", "E2-swin-U", "E2-cnx-WF", "E2-swin-WF"):
        assert f"{pending}: skipped" in err
    for stem in ("table_input_mode", "table_required", "table_domains"):
        assert (gs.results_dir(root) / f"{stem}.csv").is_file() and (gs.results_dir(root) / f"{stem}.md").is_file()
    md = read_results(gs, root, "table_input_mode.md")
    assert "| val | rect | 448x224 | 0.840 +- 0.016 |" in md  # white = mixed + 0.05
    assert "| val | squash - rect (paired) | - |" in md and "+0.010 +- 0.000" in md
    required = read_results(gs, root, "table_required.md")
    assert "| E1-U | resnet50 | 0.810 +- 0.016 |" in required  # E1-U resolves to the E0-rect folder
    assert "| E2-cnx-U | convnext_tiny | pending |" in required
    domains = read_results(gs, root, "table_domains.md")
    assert "| E1-WW | resnet50 | white | pending |" in domains and "| E2-swin-WF | swin_t | white | pending |" in domains
    header, first = read_results(gs, root, "table_input_mode.csv").splitlines()[:2]
    assert header.split(",")[:3] == ["Part", "Input mode", "Input HxW"] and first.startswith("val,squash,320x320,")


def test_summarize_fills_in_e1_and_e2_rows_when_they_arrive(gs, root):
    add_e0(gs, root, 0.80, 0.74, 0.79)
    add_g1_candidates(gs, root, 0.79, 0.85, 0.82)
    add_run(gs, root, "E1-WF", 0.60, 0.50)
    gs.summarize(root, out=lambda text: None)
    required = read_results(gs, root, "table_required.md")
    rows = [line for line in required.splitlines() if line.startswith(("| E1-U", "| E2"))]
    assert len(rows) == 3 and not any("pending" in row for row in rows)
    assert "0.820 +- 0.016" in rows[1]  # E2-cnx-U: test mixed = val 0.85 - 0.03
    domains = read_results(gs, root, "table_domains.md")
    wf_row = next(line for line in domains.splitlines() if line.startswith("| E1-WF"))
    assert "pending" not in wf_row
    assert "| - | - |" in wf_row.replace("0.5", "")  # W->F row reports field and white only, mixed and balanced are '-'


def test_findings_g0_section_and_preservation_of_hand_written_text(gs, root):
    add_e0(gs, root, squash=0.80, pad=0.74, rect=0.79, fields=(0.72, 0.60, 0.68))
    gs.run_gate(root, "g0", out=lambda text: None)
    gs.summarize(root, out=lambda text: None)
    path = gs.results_dir(root) / "findings.md"
    text = path.read_text()
    assert "<!-- auto:g0:begin -->\n## G0 input mode" in text
    assert "Gate G0 picked the rect input (448x224)" in text
    assert "Squash leads rect by 0.010, less than one std (0.016)" in text
    assert "ahead on field in 5 of 5 splits" in text
    assert "squash 0.800 +- 0.016, rect 0.790 +- 0.016 and pad 0.740 +- 0.016" in text
    path.write_text(text + "\n## Failure modes\n\nMy own notes.\n")
    gs.summarize(root, out=lambda text: None)
    again = path.read_text()
    assert again == text + "\n## Failure modes\n\nMy own notes.\n"  # regenerated block identical, notes untouched
    # a changed run changes the auto block but still not the notes
    add_e0(gs, root, squash=0.80, pad=0.74, rect=0.81)
    gs.run_gate(root, "g0", out=lambda text: None)
    gs.summarize(root, out=lambda text: None)
    changed = path.read_text()
    assert "rect has the highest mean" in changed and changed.endswith("## Failure modes\n\nMy own notes.\n")


def test_summarize_warns_when_choices_json_disagrees_with_the_runs(gs, root, capsys):
    add_e0(gs, root, squash=0.90, pad=0.74, rect=0.70)
    capsys.readouterr()
    gs.summarize(root, out=lambda text: None)  # choices.json says rect, the runs say squash
    assert "run `gate g0`" in capsys.readouterr().err


def test_summarize_command_runs_on_an_empty_root(gs, tmp_path, capsys):
    root = tmp_path / "Dhan-Shomadhan"
    (root / "_work").mkdir(parents=True)
    assert gs.run_cli(["--data-root", str(root), "summarize"]) == 0
    assert (gs.results_dir(root) / "table_input_mode.md").is_file()
    assert "G0 section skipped" in capsys.readouterr().err


# ---------------------------------------------------------------------------- the committed E0 runs


@pytest.fixture(scope="module")
def committed(gs):
    root = REPO_ROOT / "Dhan-Shomadhan"
    choices = gs.load_choices(root)
    exps = {m: gs.load_experiment(root, f"E0-{m}", choices) for m in ("squash", "pad", "rect")}
    for mode, (exp, problems) in exps.items():
        assert exp is not None, f"E0-{mode}: {problems}"
    return root, {m: exp for m, (exp, _) in exps.items()}


def test_committed_e0_numbers_and_decision(gs, committed):
    root, exps = committed
    expected = {  # val mixed, val field: mean, std (ddof=1)
        "squash": ((0.780, 0.017), (0.708, 0.018)),
        "rect": ((0.767, 0.021), (0.683, 0.027)),
        "pad": ((0.741, 0.027), (0.657, 0.060)),
    }
    for mode, (mixed, field) in expected.items():
        for subset, (mean, std) in (("mixed", mixed), ("field", field)):
            stat = gs.aggregate(exps[mode], subset, "macro_f1", "val")
            assert (round(stat.mean, 3), round(stat.std, 3)) == (mean, std), (mode, subset)
    mixed = gs.paired_difference(exps["squash"], exps["rect"], "mixed", "macro_f1", "val")
    field = gs.paired_difference(exps["squash"], exps["rect"], "field", "macro_f1", "val")
    assert (round(mixed.mean, 3), round(mixed.std, 3)) == (0.013, 0.019)
    assert (round(field.mean, 3), round(field.std, 3), field.ahead) == (0.025, 0.021, 5)
    result = gs.evaluate_g0(exps)
    assert result["value"] == "rect" and result["evidence"]["decided_by"] == "within one std -> rect"
    recorded = gs.load_choices(root).raw("input_mode")
    assert recorded == "rect"
    assert gs.load_choices(root).data["input_mode"]["evidence"] == json.loads(json.dumps(result["evidence"]))


def test_committed_results_files_are_current(gs, committed, tmp_path):
    """The committed tables and findings equal what `summarize` regenerates from the committed runs."""
    root, _ = committed
    scratch = tmp_path / "Dhan-Shomadhan"
    shutil.copytree(root / "_work" / "runs", scratch / "_work" / "runs", ignore=shutil.ignore_patterns("scratch"))
    shutil.copytree(root / "_work" / "splits", scratch / "_work" / "splits")
    (scratch / "_work" / "annotations").mkdir()
    shutil.copy(root / "_work" / "annotations" / "selection.json", scratch / "_work" / "annotations" / "selection.json")
    (scratch / "_work" / "results").mkdir()
    shutil.copy(root / "_work" / "results" / "choices.json", scratch / "_work" / "results" / "choices.json")
    shutil.copy(root / "_work" / "results" / "findings.md", scratch / "_work" / "results" / "findings.md")
    shutil.copy(root / "_work" / "results" / "inference_benchmark.json", scratch / "_work" / "results" / "inference_benchmark.json")
    gs.summarize(scratch, out=lambda text: None)  # no image cache in the scratch root: the contact sheets are skipped
    for name in ("table_input_mode.csv", "table_input_mode.md", "table_required.csv", "table_required.md",
                 "table_domains.csv", "table_domains.md", "table_methods.csv", "table_methods.md", "table_segmenter.csv",
                 "table_segmenter.md", "table_per_class.csv", "table_per_class.md", "table_hparams.csv", "table_hparams.md",
                 "table_runtime.csv", "table_runtime.md", "cases.csv", "findings.md"):
        assert (scratch / "_work" / "results" / name).read_text() == (root / "_work" / "results" / name).read_text(), name


# ---------------------------------------------------------------------------- gate G2 and the phase 06 tables (synthetic)


@pytest.fixture
def g2_root(gs, root):
    """``root`` after gate G1 chose ResNet50, so the plain G2 candidate is E1-U (the E0-rect folder)."""
    data = json.loads(gs.choices_path(root).read_text())
    data["backbone"] = {"value": "resnet50", "evidence": {}}
    gs.write_json(gs.choices_path(root), data, indent=2)
    return root


def add_method_b(gs, root, mixed, field=None):
    """Synthetic E4-B runs plus the S-seg boxes.json they cropped by (the same file in every split)."""
    for seed in range(5):
        path = gs.boxes_path(root, seed)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{"images": {}}\n')
    return add_run(gs, root, "E4-B", mixed, field, seg_boxes_sha256=gs.file_sha256(gs.boxes_path(root, 0)))


def aggregates(gs, **means):
    return {name: gs.Aggregate(mean, std, []) for name, (mean, std) in means.items()}


def test_g2_rule_mixed_then_field_then_simpler(gs):
    clear = gs.decide_g2(aggregates(gs, plain=(0.80, 0.01), A=(0.85, 0.01), B=(0.82, 0.01)),
                         aggregates(gs, plain=(0.7, 0.01), A=(0.6, 0.01), B=(0.9, 0.01)))
    assert clear["value"] == "A" and clear["decided_by"] == "highest mean" and clear["ranking"] == ["A", "B", "plain"]
    by_field = gs.decide_g2(aggregates(gs, plain=(0.80, 0.02), A=(0.81, 0.02), B=(0.79, 0.02)),
                            aggregates(gs, plain=(0.70, 0.01), A=(0.60, 0.01), B=(0.95, 0.01)))
    assert by_field["value"] == "plain" and by_field["decided_by"] == "within one std -> higher val field macro-F1", "only the top two count"
    simpler = gs.decide_g2(aggregates(gs, plain=(0.80, 0.02), A=(0.79, 0.02), B=(0.81, 0.02)),
                           aggregates(gs, plain=(0.70, 0.03), A=(0.60, 0.01), B=(0.72, 0.03)))
    assert simpler["value"] == "plain" and simpler["decided_by"] == "within one std on mixed and on field -> simpler method"
    assert simpler["ranking"][:2] == ["B", "plain"] and simpler["field_gap"] == pytest.approx(0.02)
    a_over_b = gs.decide_g2(aggregates(gs, A=(0.80, 0.02), B=(0.81, 0.02), plain=(0.5, 0.01)),
                            aggregates(gs, A=(0.70, 0.03), B=(0.71, 0.03), plain=(0.5, 0.01)))
    assert a_over_b["value"] == "A"
    tie = gs.decide_g2(aggregates(gs, B=(0.8, 0.0), plain=(0.8, 0.0)), aggregates(gs, B=(0.7, 0.0), plain=(0.7, 0.0)))
    assert tie["ranking"] == ["plain", "B"] and tie["value"] == "plain"
    alone = gs.decide_g2(aggregates(gs, plain=(0.8, 0.01)), aggregates(gs, plain=(0.7, 0.01)))
    assert alone["value"] == "plain" and alone["top_two_gap"] is None


def test_gate_g2_writes_the_recommended_experiment_with_evidence(gs, g2_root):
    root = g2_root
    add_run(gs, root, "E0-rect", 0.78)
    add_run(gs, root, "E3-A", 0.84, 0.76)
    add_method_b(gs, root, 0.80, 0.70)
    lines = []
    result = gs.run_gate(root, "g2", out=lines.append)
    data = json.loads(gs.choices_path(root).read_text())
    assert data["recommended"]["value"] == "E3-A" == result["value"] and data["backbone"]["value"] == "resnet50"
    assert gs.load_choices(root).get("recommended") == "E3-A"
    ev = data["recommended"]["evidence"]
    assert ev["method"] == "A" and ev["decided_by"] == "highest mean" and ev["ranking"] == ["A", "B", "plain"] and ev["cut"] == []
    assert ev["candidates"]["plain"]["experiment"] == "E1-U" and ev["candidates"]["plain"]["run_folder"] == "E0-rect"
    assert ev["candidates"]["B"]["val_mixed_macro_f1"]["mean"] == pytest.approx(0.80)
    assert set(ev["paired_differences"]) == {"A_minus_plain", "B_minus_plain", "B_minus_A"}
    assert ev["paired_differences"]["A_minus_plain"]["val_mixed_macro_f1"]["mean"] == pytest.approx(0.06)
    assert "simpler method (plain < A < B)" in ev["rule"]
    text = "\n".join(lines)
    assert "decision: E3-A = Method A (composites)" in text
    first = gs.choices_path(root).read_bytes()
    gs.run_gate(root, "g2", out=lambda _: None)
    assert gs.choices_path(root).read_bytes() == first, "deterministic"


def test_gate_g2_refuses_incomplete_candidates_unless_cut(gs, g2_root):
    root = g2_root
    add_run(gs, root, "E0-rect", 0.78)
    add_run(gs, root, "E3-A", 0.84)
    before = gs.choices_path(root).read_bytes()
    with pytest.raises(gs.ExperimentError, match="E4-B cannot be used"):
        gs.run_gate(root, "g2", out=lambda _: None)
    assert gs.choices_path(root).read_bytes() == before
    result = gs.run_gate(root, "g2", out=lambda _: None, cut=("B",))
    assert result["value"] == "E3-A" and result["evidence"]["cut"] == ["B"] and set(result["evidence"]["candidates"]) == {"plain", "A"}
    with pytest.raises(gs.ExperimentError, match="only Method A or B can be cut"):
        gs.run_gate(root, "g2", out=lambda _: None, cut=("plain",))


def test_gate_g2_refuses_a_stale_method_b_run(gs, g2_root):
    root = g2_root
    add_run(gs, root, "E0-rect", 0.78)
    add_run(gs, root, "E3-A", 0.84)
    add_method_b(gs, root, 0.80)
    gs.boxes_path(root, 2).write_text('{"images": {"changed": 1}}\n')
    with pytest.raises(gs.ExperimentError, match="split 2: the S-seg boxes changed"):
        gs.run_gate(root, "g2", out=lambda _: None)


def test_gate_g2_is_frozen_once_written(gs, g2_root, capsys):
    root = g2_root
    add_run(gs, root, "E0-rect", 0.78)
    add_run(gs, root, "E3-A", 0.84)
    assert gs.run_cli(["--data-root", str(root), "gate", "g2", "--cut", "B"]) == 0
    add_run(gs, root, "E3-A", 0.70)  # the runs change and would now pick plain
    frozen = gs.choices_path(root).read_bytes()
    assert gs.run_cli(["--data-root", str(root), "gate", "g2", "--cut", "B"]) == 1
    assert "frozen" in capsys.readouterr().err and gs.choices_path(root).read_bytes() == frozen
    assert gs.run_cli(["--data-root", str(root), "gate", "g2", "--cut", "B", "--force"]) == 0
    assert gs.load_choices(root).raw("recommended") == "E1-U"


def test_table_methods_shows_test_numbers_only_after_g2(gs, g2_root):
    root = g2_root
    add_run(gs, root, "E0-rect", 0.78)
    add_run(gs, root, "E3-A", 0.84)
    gs.summarize(root, out=lambda _: None)
    md = read_results(gs, root, "table_methods.md")
    assert "| val | plain unified model | E1-U | 0.830 +- 0.016 |" in md  # white = mixed + 0.05
    assert "| val | Method B (segment, crop) | E4-B | pending |" in md
    assert "| val | A - plain (paired) | E3-A - E1-U | +0.060 +- 0.000 |" in md
    test_rows = [line for line in md.splitlines() if line.startswith("| test")]
    assert len(test_rows) == 5 and all("hidden until gate g2" in row and "0." not in row for row in test_rows)
    assert "auto:g2" not in read_results(gs, root, "findings.md")
    gs.run_gate(root, "g2", out=lambda _: None, cut=("B",))
    gs.summarize(root, out=lambda _: None)
    md = read_results(gs, root, "table_methods.md")
    assert "| test | Method A (composites) (recommended) | E3-A | 0.860 +- 0.016 |" in md and "hidden" not in md
    findings = read_results(gs, root, "findings.md")
    assert "## G2 recommended method" in findings and "Gate G2 recommends Method A (composites) (E3-A)" in findings
    assert "Left out because of a cut line: Method B." in findings


def test_g2_findings_reads_the_plain_method_with_an_article(gs, g2_root):
    root = g2_root
    add_run(gs, root, "E0-rect", 0.84)
    add_run(gs, root, "E3-A", 0.84)
    gs.run_gate(root, "g2", out=lambda _: None, cut=("B",))
    gs.summarize(root, out=lambda _: None)
    assert "Gate G2 recommends the plain unified model (E1-U)," in read_results(gs, root, "findings.md")


def test_table_domains_adds_e3_a_wf_once_run_and_hides_its_test_numbers_until_g2(gs, g2_root):
    root = g2_root
    add_run(gs, root, "E0-rect", 0.78)
    add_run(gs, root, "E3-A", 0.84)
    gs.summarize(root, out=lambda _: None)
    assert "| E3-A-WF" not in read_results(gs, root, "table_domains.md")  # optional row, not run yet
    add_run(gs, root, "E3-A-WF", 0.70, 0.55)
    gs.summarize(root, out=lambda _: None)
    row = next(line for line in read_results(gs, root, "table_domains.md").splitlines() if line.startswith("| E3-A-WF"))
    assert row.startswith("| E3-A-WF | resnet50 | white + composites | hidden until gate g2 |")
    assert row.endswith("| - | - | - | - |")  # mixed and balanced are not what a W->F row is about
    gs.run_gate(root, "g2", out=lambda _: None, cut=("B",))
    gs.summarize(root, out=lambda _: None)
    row = next(line for line in read_results(gs, root, "table_domains.md").splitlines() if line.startswith("| E3-A-WF"))
    assert "hidden" not in row and "| 0.520 +- 0.016 |" in row  # test field = val 0.55 - 0.03


def add_segmenter(gs, root, *, eval_sections=True, stale_split=None):
    """Synthetic S-seg runs (metrics.json as `run_seg_split` writes it) and, optionally, their eval sections."""
    config = gs.EXPERIMENTS["S-seg"]
    for seed in range(5):
        run = gs.split_dir(gs.runs_dir(root) / "S-seg", seed)
        metrics = {
            "split": seed, "kind": "segmenter", "split_sha256": gs.load_split(root, seed)["sha256"],
            "config_fingerprint": gs.expected_fingerprint(config, None, root), "fast": False, "overrides": {},
            "val_iou_white": 0.90 + 0.01 * seed, "val_iou_composite": 0.70, "n_val_white": 116, "n_val_composites": 200,
            "boxes_sha256": f"{seed}" * 64,
            "fallbacks": {"white": {"n": 769, "fallback": 0, "rate": 0.0}, "field": {"n": 337, "fallback": seed, "rate": seed / 337}},
        }
        gs.write_json(run / "metrics.json", metrics)
        if eval_sections:
            summary = {"all": {"n": 20, "iou": 0.5 + 0.01 * seed, "dice": 0.6, "hit_rate": 0.8, "box_area": 0.3},
                       "excluding_ambiguous": {"n": 15, "iou": 0.55, "dice": 0.65, "hit_rate": 0.9, "box_area": 0.3}, "fallbacks": 1}
            sha = "x" * 64 if seed == stale_split else metrics["boxes_sha256"]
            gs.write_json(run / "seg_metrics.json", {"eval": {"boxes_sha256": sha, "summary": summary}})


def test_table_segmenter_reads_the_eval_sections_and_marks_what_is_missing(gs, root):
    gs.summarize(root, out=lambda _: None)
    md = read_results(gs, root, "table_segmenter.md")
    assert "| IoU, eval annotations | - | pending | pending |" in md
    add_segmenter(gs, root, eval_sections=False)
    gs.summarize(root, out=lambda _: None)
    md = read_results(gs, root, "table_segmenter.md")
    assert "| IoU, eval annotations | - | pending (seg-eval --set eval --final) | pending |" in md
    assert "| IoU, white val pseudo-masks (checkpoint data) | 116 | 0.920 +- 0.016 | 0.900; 0.910; 0.920; 0.930; 0.940 |" in md
    assert "| Fallbacks, all cached field images (%) | 337 | 0.6 +- 0.5 |" in md
    add_segmenter(gs, root, stale_split=3)
    gs.summarize(root, out=lambda _: None)
    assert "pending (seg-eval --set eval --final)" in read_results(gs, root, "table_segmenter.md"), "an eval of other boxes is stale"
    add_segmenter(gs, root)
    gs.summarize(root, out=lambda _: None)
    md = read_results(gs, root, "table_segmenter.md")
    assert "| IoU, eval annotations | 20 | 0.520 +- 0.016 | 0.500; 0.510; 0.520; 0.530; 0.540 |" in md
    assert "| Salient-leaf hit rate (%), eval annotations without the ambiguous ones | 15 | 90.0 +- 0.0 |" in md
    assert "| Fallbacks on the eval annotations (%) | 20 | 5.0 +- 0.0 |" in md


# ---------------------------------------------------------------------------- phase 07: tables, figures, cases, findings (synthetic)


def quiet(_text):
    pass


@pytest.fixture
def rich_root(gs, g2_root):
    """The plain, domain-wise, cross-domain and Method A rows all complete, E1-FF / E1-WF on the Mac, gate G2 run with B cut
    (E3-A, the Method A run, is recommended). Per-class F1 of class i is the subset macro-F1 + 0.01 * (i - 2)."""
    root = g2_root
    add_run(gs, root, "E0-rect", 0.78, 0.70)
    for exp_id, mixed, field, env in (
        ("E1-FF", 0.60, 0.50, MAC_ENV), ("E1-WF", 0.50, 0.30, MAC_ENV), ("E2-cnx-U", 0.80, 0.71, None), ("E2-swin-U", 0.79, 0.69, None),
        ("E2-cnx-WF", 0.40, 0.10, None), ("E2-swin-WF", 0.45, 0.25, None), ("E3-A", 0.84, 0.76, None), ("E3-A-WF", 0.70, 0.55, None),
    ):
        add_run(gs, root, exp_id, mixed, field, env=env)
    gs.run_gate(root, "g2", out=quiet, cut=("B",))
    return root


def test_table_required_marks_the_recommended_row_and_adds_it(gs, rich_root):
    gs.summarize(rich_root, out=quiet)
    rows = [line for line in read_results(gs, rich_root, "table_required.md").splitlines() if line.startswith(("| E1", "| E2", "| E3"))]
    assert [row.split("|")[1].strip() for row in rows] == ["E1-U", "E2-cnx-U", "E2-swin-U", "E3-A (recommended)"]
    assert "| E3-A (recommended) | resnet50 | 0.860 +- 0.016 |" in rows[3]  # white test = val mixed 0.84 + 0.05 - 0.03


def test_table_per_class_reads_the_recommended_method(gs, rich_root, root):
    gs.summarize(rich_root, out=quiet)
    md = read_results(gs, rich_root, "table_per_class.md")
    assert md.splitlines()[0] == "# Per-class results of the recommended method (E3-A), test split"
    assert "| field | Rice Blast | 5 | 0.750 +- 0.016 | 0.710 +- 0.016 | 0.730 +- 0.016 |" in md  # support 1 per split, F1 = test field 0.73
    assert "| white | Brown Spot | 5 | 0.860 +- 0.016 | 0.820 +- 0.016 | 0.840 +- 0.016 |" in md  # F1 = test white 0.86 - 0.02
    assert "| field | macro-F1 | 25 | - | - | 0.730 +- 0.016 |" in md
    assert len([line for line in md.splitlines() if line.startswith(("| white", "| field"))]) == 12
    header = read_results(gs, rich_root, "table_per_class.csv").splitlines()[0]
    assert header == "Domain,Class,Support (5 splits),Precision,Recall,F1"


def test_table_per_class_is_pending_until_the_recommendation_exists(gs, root):
    add_run(gs, root, "E0-rect", 0.78)
    gs.summarize(root, out=quiet)
    md = read_results(gs, root, "table_per_class.md")
    assert "not chosen yet" in md and "| white | Brown Spot | pending | pending | pending | pending |" in md


def test_table_hparams_is_read_from_config_json_and_flags_differences(gs, rich_root):
    gs.summarize(rich_root, out=quiet)
    md = read_results(gs, rich_root, "table_hparams.md")
    assert "Values are identical across the 5 splits of every experiment." in md
    rows = {line.split("|")[1].strip(): [c.strip() for c in line.split("|")[1:-1]] for line in md.splitlines() if line.startswith("| E")}
    header = [c.strip() for c in next(line for line in md.splitlines() if line.startswith("| Experiment")).split("|")[1:-1]]
    cell = lambda exp, column: rows[exp][header.index(column)]  # noqa: E731
    assert cell("E1-U", "Run folder") == "E0-rect" and cell("E1-WW", "Run folder") == "E1-WF"
    assert cell("E2-swin-U", "Backbone") == "swin_t" and cell("E2-swin-U", "Learning rate") == "0.0003"
    assert cell("E0-rect", "Input HxW") == "448x224" and cell("E3-A", "Train on") == "white + field + composites"
    assert cell("E3-A-WF", "Checkpoint chosen on (val)") == "white"
    assert cell("E2-cnx-U", "Batch size x accumulation") == "32 x 1" and cell("E0-squash", "Learning rate") == "pending"
    assert "random crop of 60%-100% of the area" in md and "AdamW" in md
    # a split whose config.json differs is shown and named, never averaged away
    path = gs.split_dir(gs.runs_dir(rich_root) / "E2-cnx-U", 3) / "config.json"
    data = json.loads(path.read_text())
    data["experiment"]["lr"] = 0.005
    gs.write_json(path, data)
    gs.summarize(rich_root, out=quiet)
    md = read_results(gs, rich_root, "table_hparams.md")
    assert "varies: 0.0001 / 0.005" in md and "Not identical across the splits: E2-cnx-U (Learning rate)." in md
    path.unlink()
    gs.summarize(rich_root, out=quiet)
    assert "config.json is missing for: E2-cnx-U." in read_results(gs, rich_root, "table_hparams.md")


def benchmark_record(device, resnet, convnext, swin, **extra):
    record = {"device": device, "precision": "fp32", "input_mode": "rect", "input_size": [448, 224], "batch_size": 1, "warmup": 10, "repeats": 50,
              "platform": "macOS-26.5-arm64-arm-64bit", "cpu_count": 8, "gpu": None, "torch": "2.11.0", **extra,
              "backbones": {name: {"median_ms": median, "q1_ms": median - 1.0, "q3_ms": median + 1.0, "parameters": 1}
                            for name, median in (("resnet50", resnet), ("convnext_tiny", convnext), ("swin_t", swin))}}
    return record


def test_table_runtime_reads_metrics_env_and_the_benchmark_file(gs, rich_root):
    gs.summarize(rich_root, out=quiet)
    md = read_results(gs, rich_root, "table_runtime.md")
    row = next(line for line in md.splitlines() if line.startswith("| E1-FF "))
    assert row.startswith("| E1-FF | E1-FF | local macOS, mps (Apple MPS) | 6.0 +- 3.2 | 12.0 +- 1.6 | 22.0 +- 1.6 | 25.0 | not measured (run benchmark) |")
    assert "| E2-swin-U | E2-swin-U | Kaggle, cuda (Tesla T4) | 6.0 +- 3.2 |" in md
    assert "| E1-U | E0-rect | Kaggle, cuda (Tesla T4) |" in md and "| E0-squash | - | pending |" in md
    assert "No benchmark file yet" in md
    gs.write_json(gs.benchmark_path(rich_root), {"format": 1, "devices": {
        "mps": benchmark_record("mps", 20.0, 50.0, 60.0), "cpu": benchmark_record("cpu", 63.24, 857.36, 78.28)}}, indent=2)
    gs.summarize(rich_root, out=quiet)
    md = read_results(gs, rich_root, "table_runtime.md")
    assert "Inference ms/image, median (quartiles), cpu | Inference ms/image, median (quartiles), mps |" in md  # fixed device order
    assert "| 25.0 | 63.2 (62.2-64.2) | 20.0 (19.0-21.0) |" in next(line for line in md.splitlines() if line.startswith("| E1-FF "))
    assert "| 78.3 (77.3-79.3) | 60.0 (59.0-61.0) |" in next(line for line in md.splitlines() if line.startswith("| E2-swin-U "))
    assert "Measured on - cpu: macOS-26.5-arm64-arm-64bit, 8 cores, no GPU, torch 2.11.0, rect input 448x224, fp32, median of 50 after 10 warm-up passes" in md


def test_read_benchmark_handles_a_missing_or_unusable_file(gs, root, capsys):
    assert gs.read_benchmark(root) == {}
    path = gs.benchmark_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    for bad in ("{not json", json.dumps({"format": 2, "devices": {}}), json.dumps({"format": 1}), json.dumps({"format": 1, "devices": {"cpu": 3}})):
        path.write_text(bad)
        assert gs.read_benchmark(root) == {}
        assert "unusable" in capsys.readouterr().err
    gs.write_json(path, {"format": 1, "devices": {"cuda": benchmark_record("cuda", 1, 2, 3), "cpu": benchmark_record("cpu", 4, 5, 6)}})
    assert list(gs.read_benchmark(root)) == ["cpu", "cuda"]


def test_run_benchmark_times_the_three_backbones_and_keeps_other_devices(gs, root):
    other = benchmark_record("mps", 20.0, 50.0, 60.0)
    gs.write_json(gs.benchmark_path(root), {"format": 1, "devices": {"mps": other}}, indent=2)
    record = gs.run_benchmark(root, "cpu", out=quiet, warmup=1, repeats=3)
    assert record["device"] == "cpu" and record["input_size"] == [448, 224] and record["input_mode"] == "rect" and record["batch_size"] == 1
    assert record["precision"] == "fp32" and (record["warmup"], record["repeats"]) == (1, 3)
    assert set(record["backbones"]) == set(gs.BACKBONES)
    for entry in record["backbones"].values():
        assert 0 < entry["q1_ms"] <= entry["median_ms"] <= entry["q3_ms"] and entry["parameters"] > 1e7
    saved = json.loads(gs.benchmark_path(root).read_text())
    assert list(saved["devices"]) == ["cpu", "mps"] and saved["devices"]["mps"] == other
    assert gs.hardware_text((("Colab", "cuda", "Tesla T4", "2.11.0", "3.13.15"),), full=False) == "Colab, cuda (Tesla T4)"
    assert gs.precision_of("cuda") != gs.precision_of("mps") == gs.precision_of("cpu") == "fp32"
    assert gs.host_label({"torch_home": "/kaggle/tmp/w"}) == "Kaggle" and gs.host_label({"torch_home": "/content/w"}) == "Colab"
    assert gs.host_label({"torch_home": "w", "platform": "macOS-26.5-arm64"}) == "local macOS"


def test_benchmark_command_calls_run_benchmark_and_reports_failures(gs, root, monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(gs, "run_benchmark", lambda data_root, device, **kwargs: calls.append((data_root, device)))
    assert gs.run_cli(["--data-root", str(root), "benchmark", "--device", "cpu"]) == 0 and calls == [(root, "cpu")]

    def fail(data_root, device, **kwargs):
        raise gs.ExperimentError("no input_mode yet")

    monkeypatch.setattr(gs, "run_benchmark", fail)
    assert gs.run_cli(["--data-root", str(root), "benchmark", "--device", "cpu"]) == 1
    assert "benchmark: FAIL - no input_mode yet" in capsys.readouterr().err


# ---- figures


def png_size_and_dpi(path):
    from PIL import Image

    with Image.open(path) as image:
        return image.size, image.info.get("dpi")


def test_summarize_writes_every_figure_at_300_dpi(gs, rich_root):
    gs.summarize(rich_root, out=quiet)
    figures = gs.figures_dir(rich_root)
    expected = {"confusion_E3-A_white.png": 3.9, "confusion_E3-A_field.png": 3.9, "confusion_E1-WF_field.png": 3.9, "confusion_E2-swin-WF_field.png": 3.9,
                "confusion_E3-A-WF_field.png": 3.9, "scenario_bars.png": 4.4, "domain_gap.png": 4.4, "training_curves_E3-A.png": 4.4}
    for name, width in expected.items():
        size, dpi = png_size_and_dpi(figures / name)
        assert round(dpi[0]) == 300 and size[0] == round(width * 300), name
    assert png_size_and_dpi(figures / "domain_gap.png")[0][1] < 4.5 * 300  # compact: well under a page
    first = (figures / "confusion_E3-A_field.png").read_bytes()
    gs.summarize(rich_root, out=quiet)
    assert (figures / "confusion_E3-A_field.png").read_bytes() == first, "figures are reproducible"


def test_figures_only_draw_what_the_runs_support(gs, g2_root):
    add_run(gs, g2_root, "E0-rect", 0.78)
    gs.summarize(g2_root, out=quiet)
    names = sorted(p.name for p in gs.figures_dir(g2_root).glob("*.png"))
    assert names == ["domain_gap.png", "scenario_bars.png"]  # E1-U is the only main model; no recommendation yet, no W->F rows


def test_confusion_figure_sums_the_splits_and_shows_counts(gs, rich_root):
    exp, _ = gs.load_experiment(rich_root, "E1-WF", gs.load_choices(rich_root))
    matrix = gs.summed_confusion(exp, "field")
    assert matrix.sum() == 25 and matrix[0].tolist() == [0, 5, 0, 0, 0] and matrix[3, 3] == 5
    assert gs.largest_confusions(exp, "field") == "Brown Spot taken for Leaf Scald in 5 of 5 images (100%)"
    path = gs.save_confusion(rich_root, exp, "white", rich_root / "x" / "c.png")
    assert path.is_file()
    assert gs.per_class_support(exp, "test", "white", "Rice Blast") == 5


def test_training_curves_skip_a_missing_history(gs, rich_root):
    exp, _ = gs.load_experiment(rich_root, "E3-A", gs.load_choices(rich_root))
    (gs.split_dir(gs.runs_dir(rich_root) / "E3-A", 2) / "history.csv").unlink()
    assert gs.read_history(rich_root, exp, 2) is None
    history = gs.read_history(rich_root, exp, 1)
    assert [row["stage"] for row in history] == ["lp", "lp", "ft", "ft", "ft"] and history[3]["best"] == 1.0
    assert gs.save_training_curves(rich_root, exp, rich_root / "x" / "t.png").is_file()
    for k in (0, 1, 3, 4):
        (gs.split_dir(gs.runs_dir(rich_root) / "E3-A", k) / "history.csv").unlink()
    assert gs.save_training_curves(rich_root, exp, rich_root / "x" / "none.png") is None


# ---- cases


def pooled_example():
    return {
        "a.jpg": {"domain": "white", "true": "Brown Spot", "tests": {0: (0, [0.90, 0.05, 0.02, 0.02, 0.01]), 2: (0, [0.80, 0.10, 0.05, 0.03, 0.02])}},
        "b.jpg": {"domain": "field", "true": "Leaf Scald", "tests": {1: (2, [0.10, 0.20, 0.60, 0.05, 0.05]), 3: (2, [0.10, 0.10, 0.70, 0.05, 0.05])}},
        "c.jpg": {"domain": "field", "true": "Rice Blast", "tests": {0: (2, [0.10, 0.10, 0.55, 0.10, 0.15]), 1: (1, [0.10, 0.60, 0.20, 0.05, 0.05]),
                                                                     4: (2, [0.05, 0.10, 0.65, 0.10, 0.10])}},
        "d.jpg": {"domain": "white", "true": "Rice Tungro", "tests": {2: (3, [0.10, 0.10, 0.10, 0.45, 0.25])}},
    }


@pytest.mark.parametrize("correct, confidence, expected", [
    ([True], [0.95], "success"), ([True, True], [0.9, 0.5], "success"), ([True, True], [0.9, 0.49], "challenging"),
    ([True, False], [0.9, 0.9], "challenging"), ([False, False], [0.9, 0.9], "failure"), ([False], [0.2], "failure"),
    ([False, True, False], [0.9, 0.9, 0.9], "challenging"),
])
def test_classify_case(gs, correct, confidence, expected):
    assert gs.classify_case(correct, confidence) == expected


def test_case_rows_pool_the_splits(gs):
    rows = {r["filename"]: r for r in gs.case_rows(pooled_example())}
    assert list(rows) == ["a.jpg", "b.jpg", "c.jpg", "d.jpg"]
    assert [rows[n]["category"] for n in rows] == ["success", "failure", "challenging", "challenging"]
    assert (rows["a.jpg"]["tested"], rows["a.jpg"]["correct"]) == (2, 2) and rows["a.jpg"]["preds"] == ["Brown Spot", "", "Brown Spot", "", ""]
    assert rows["b.jpg"]["modal_pred"] == "Rice Blast" and rows["b.jpg"]["wrong_pred"] == "Rice Blast"
    assert rows["b.jpg"]["mean_p_modal"] == pytest.approx(0.65) and rows["b.jpg"]["mean_p_true"] == pytest.approx(0.15)
    c = rows["c.jpg"]
    assert (c["tested"], c["correct"], c["modal_pred"], c["wrong_pred"]) == (3, 2, "Rice Blast", "Leaf Scald")
    assert c["preds"] == ["Rice Blast", "Leaf Scald", "", "", "Rice Blast"]
    assert c["mean_p_modal"] == pytest.approx((0.55 + 0.20 + 0.65) / 3) and c["min_top_p"] == pytest.approx(0.55)
    d = rows["d.jpg"]
    assert d["category"] == "challenging" and d["correct"] == 1 and d["wrong_pred"] == "" and d["min_top_p"] == pytest.approx(0.45)
    parsed = list(csv.DictReader(gs.cases_csv(list(rows.values())).splitlines()))
    assert list(parsed[2]) == ["filename", "domain", "true", "tested", "correct", "category", "pred_split0", "pred_split1", "pred_split2", "pred_split3",
                               "pred_split4", "modal_pred", "wrong_pred", "mean_p_modal", "mean_p_true", "min_top_p"]
    assert parsed[2]["pred_split1"] == "Leaf Scald" and parsed[2]["pred_split2"] == "" and parsed[2]["mean_p_modal"] == "0.467"


def case_row(name, domain, true, category, tested=1, correct=0, p=0.5):
    return {"filename": name, "domain": domain, "true": true, "category": category, "tested": tested, "correct": correct, "mean_p_modal": p}


def test_select_cases_is_balanced_deterministic_and_ordered(gs):
    rows = [case_row(f"{d[0]}{c}_{i}.jpg", d, cls, "failure", tested=1 + (i % 3), p=0.5 + 0.01 * i)
            for d in gs.DOMAINS for c, cls in enumerate(gs.CLASS_NAMES) if not (d == "field" and c == 4) for i in range(4)]
    rows.append(case_row("other.jpg", "white", "Brown Spot", "success"))
    picked = gs.select_cases(rows, "failure")
    assert len(picked) == 10 and picked == gs.select_cases(list(reversed(rows)), "failure")
    groups = [(r["domain"], r["true"]) for r in picked]
    assert len(set(groups)) == 9 and ("field", "Sheath Blight") not in groups  # field has no Sheath Blight failures: that group is skipped
    assert [g[0] for g in groups] == sorted((g[0] for g in groups), key=gs.DOMAINS.index), "white first, then field"
    white = [r for r in picked if r["domain"] == "white"]
    assert [r["true"] for r in white] == sorted((r["true"] for r in white), key=gs.CLASS_NAMES.index)
    best = next(r for r in picked if (r["domain"], r["true"]) == ("white", "Leaf Scald"))
    assert best["filename"] == "w1_2.jpg"  # failures: the group's most often tested image first
    assert not [r for r in picked if r["category"] != "failure"]
    assert len(gs.select_cases(rows, "failure", 12)) == 12 and len(gs.select_cases(rows, "challenging")) == 0


def test_select_cases_orders_each_category_by_its_own_key(gs):
    group = [case_row("a.jpg", "white", "Rice Blast", "success", 1, 1, 0.90), case_row("b.jpg", "white", "Rice Blast", "success", 3, 3, 0.80),
             case_row("c.jpg", "white", "Rice Blast", "success", 3, 3, 0.95)]
    assert gs.select_cases(group, "success", 1)[0]["filename"] == "c.jpg"  # most confident
    group = [case_row("a.jpg", "white", "Rice Blast", "failure", 1, 0, 0.99), case_row("b.jpg", "white", "Rice Blast", "failure", 3, 0, 0.60),
             case_row("c.jpg", "white", "Rice Blast", "failure", 3, 0, 0.80)]
    assert gs.select_cases(group, "failure", 1)[0]["filename"] == "c.jpg"  # most tested, then most confidently wrong
    group = [case_row("a.jpg", "white", "Rice Blast", "challenging", 3, 3, 0.4), case_row("b.jpg", "white", "Rice Blast", "challenging", 4, 3, 0.4),
             case_row("c.jpg", "white", "Rice Blast", "challenging", 4, 2, 0.4)]
    assert gs.select_cases(group, "challenging", 1)[0]["filename"] == "c.jpg"  # most tested, outcomes closest to half


def test_case_label_reads_true_to_predicted(gs):
    row = {"true": "Rice Blast", "modal_pred": "Leaf Scald", "mean_p_modal": 0.4667, "filename": "rbf_9.jpg", "correct": 1, "tested": 3, "wrong_pred": "Leaf Scald"}
    assert gs.case_label(row) == "Rice Blast ->\nLeaf Scald (0.47)\nrbf_9.jpg  1/3 correct"
    assert gs.case_label({**row, "modal_pred": "Rice Blast", "wrong_pred": "Leaf Scald"}).endswith("\nalso taken for Leaf Scald")


def test_write_cases_reads_the_recommended_runs_and_draws_three_sheets(gs, rich_root, capsys):
    from conftest import make_jpeg

    gs.summarize(rich_root, out=quiet)
    err = capsys.readouterr().err
    assert "contact sheets skipped" in err  # no image cache in the synthetic root
    rows = list(csv.DictReader(read_results(gs, rich_root, "cases.csv").splitlines()))
    assert len(rows) == 10 and Counter(r["category"] for r in rows) == {"success": 5, "failure": 5}
    failure = next(r for r in rows if r["filename"] == "f3.jpg")
    assert (failure["domain"], failure["true"], failure["modal_pred"], failure["tested"], failure["correct"]) == ("field", "Leaf Scald", "Rice Blast", "1", "0")
    assert failure["pred_split3"] == "Rice Blast" and failure["pred_split0"] == "" and failure["mean_p_modal"] == "0.600"
    for name in [r["filename"] for r in rows]:
        make_jpeg(gs.cache_dir(rich_root) / name, 40, 90, seed=len(name))
    gs.summarize(rich_root, out=quiet)
    for category in ("success", "failure", "challenging"):
        size, dpi = png_size_and_dpi(gs.figures_dir(rich_root) / f"cases_{category}.png")
        assert round(dpi[0]) == 300 and size[0] == round(5.8 * 300)
    assert "contact sheets skipped" not in capsys.readouterr().err


def test_write_cases_is_skipped_until_the_recommendation_exists(gs, root, capsys):
    add_run(gs, root, "E0-rect", 0.78)
    gs.summarize(root, out=quiet)
    assert "cases: skipped" in capsys.readouterr().err
    assert not (gs.results_dir(root) / "cases.csv").exists() and "auto:cases" not in read_results(gs, root, "findings.md")


# ---- findings


def test_domain_questions_findings_answer_each_question_with_numbers(gs, rich_root):
    gs.summarize(rich_root, out=quiet)
    text = read_results(gs, rich_root, "findings.md")
    assert "<!-- auto:questions:begin -->\n## Domain transfer questions (phase 04)" in text
    assert ("**1. Domain gap.** Field test macro-F1 is 0.470 +- 0.016 for E1-FF (ResNet50 trained on field images) and 0.270 +- 0.016 for E1-WF "
            "(trained on white images only), so training on white alone lowers field macro-F1 by 0.200 "
            "(paired E1-WF - E1-FF: -0.200 +- 0.000; E1-WF ahead in 0 of 5 splits).") in text
    assert "E2-cnx-WF (white only, ConvNeXt-T) reaches 0.070 +- 0.016." in text and "With composites E3-A-WF reaches 0.520 +- 0.016" in text
    assert "(paired E3-A-WF - E2-swin-WF: +0.300 +- 0.000; E3-A-WF ahead in 5 of 5 splits)" in text
    assert "**2. Does white data help field?** Field test macro-F1 is 0.670 +- 0.016 for E1-U (white + field) and 0.470 +- 0.016 for E1-FF" in text
    assert "the unified model is ahead by 0.200 (paired E1-U - E1-FF: +0.200 +- 0.000; E1-U ahead in 5 of 5 splits)." in text
    assert "**3. Does field data hurt white?** White test macro-F1 is 0.800 +- 0.016 for E1-U (white + field) and 0.520 +- 0.016 for E1-WW" in text
    assert "**4. Which classes collapse under W->F?**" in text and "below 50% of E1-FF's for that class" in text
    assert "- E1-FF (field only, reference): per-class field F1 Brown Spot 0.450, Leaf Scald 0.460, Rice Blast 0.470, Rice Tungro 0.480, Sheath Blight 0.490." in text
    wf = next(line for line in text.splitlines() if line.startswith("- E1-WF:"))
    assert "Collapsed: none." in wf and "Largest change against E1-FF: Brown Spot (-0.200)." in wf
    assert "Most frequent mistakes: Brown Spot taken for Leaf Scald in 5 of 5 images (100%)." in wf
    assert "Collapsed: Brown Spot, Leaf Scald, Rice Blast, Rice Tungro, Sheath Blight." in next(line for line in text.splitlines() if line.startswith("- E2-cnx-WF:"))


def test_domain_questions_say_what_is_not_available_yet(gs, root):
    add_run(gs, root, "E0-rect", 0.78)
    gs.summarize(root, out=quiet)
    text = read_results(gs, root, "findings.md")
    assert "**1. Domain gap.** Not available yet: E1-FF, E1-WF is not complete." in text
    assert "**3. Does field data hurt white?** Not available yet: E1-U, E1-WW is not complete." in text
    assert "**4. Which classes collapse under W->F?** Not available yet" in text


def test_hardware_findings_group_the_runs_and_name_the_comparisons_that_cross(gs, rich_root):
    gs.summarize(rich_root, out=quiet)
    text = read_results(gs, rich_root, "findings.md")
    assert "<!-- auto:hardware:begin -->\n## Hardware" in text
    assert "- E1-WF (also E1-WW), E1-FF: local macOS, mps (Apple MPS), torch 2.11.0, Python 3.12.13, fp32" in text
    assert "- E0-rect (also E1-U), E2-cnx-U, E2-cnx-WF, E2-swin-U, E2-swin-WF, E3-A, E3-A-WF: Kaggle, cuda (Tesla T4), torch 2.11.0+cu128, Python 3.13.15, " \
           "mixed precision (fp16 autocast)" in text
    assert "can include hardware and numerics effects" in text
    assert "cross groups: E1-U vs E1-FF, E1-U vs E1-WW, E2-swin-WF vs E1-WF. Read those" in text


def test_hardware_findings_for_one_group_and_for_none(gs, root):
    add_run(gs, root, "E0-rect", 0.78)
    gs.summarize(root, out=quiet)
    assert "All runs share the same hardware, torch build and precision" in read_results(gs, root, "findings.md")
    assert gs.hardware_findings({}, root) == ""  # nothing complete: no section


def test_cases_findings_count_the_categories(gs, rich_root):
    gs.summarize(rich_root, out=quiet)
    text = read_results(gs, rich_root, "findings.md")
    assert "<!-- auto:cases:begin -->\n## Success, failure and challenging cases (T7.4)" in text
    assert "Pooled test predictions of E3-A over the 5 splits cover 10 distinct images; 10 of them were in the test part of only one split." in text
    assert "5 consistent successes (right in every split they were tested in, top probability never below 0.5): 5 white, 0 field." in text
    assert "5 consistent failures (wrong in every split they were tested in): 0 white, 5 field." in text
    assert "0 challenging cases" in text and "Leaf Scald -> Rice Blast (5)" in text
    assert "5 of the 5 failures were tested in one split only" in text


def test_findings_keep_hand_written_failure_hypotheses(gs, rich_root):
    gs.summarize(rich_root, out=quiet)
    path = gs.results_dir(rich_root) / "findings.md"
    notes = "\n## Failure hypotheses (Nattan)\n\n- f3.jpg: leaf is small in the frame\n"
    path.write_text(path.read_text() + notes)
    before = path.read_text()
    gs.summarize(rich_root, out=quiet)
    assert path.read_text() == before and path.read_text().endswith(notes)


# ---- the committed runs


def test_committed_phase_07_numbers(gs, committed):
    root, _ = committed
    rows = list(csv.DictReader((root / "_work" / "results" / "cases.csv").read_text().splitlines()))
    assert len(rows) == 607 and Counter(r["category"] for r in rows) == {"success": 428, "failure": 119, "challenging": 60}
    findings = (root / "_work" / "results" / "findings.md").read_text()
    assert "Field test macro-F1 is 0.539 +- 0.128 for E1-FF" in findings and "0.141 +- 0.039 for E1-WF" in findings
    per_class = (root / "_work" / "results" / "table_per_class.md").read_text()
    assert "| field | Leaf Scald | 51 | 0.503 +- 0.065 | 0.511 +- 0.134 | 0.501 +- 0.083 |" in per_class
    assert "(recommended)" in (root / "_work" / "results" / "table_required.md").read_text()
    benchmark = gs.read_benchmark(root)
    assert set(benchmark) <= {"cpu", "mps", "cuda"} and benchmark
    for record in benchmark.values():
        assert record["input_size"] == [448, 224] and set(record["backbones"]) == set(gs.BACKBONES)
    figures = root / "_work" / "figures"
    for name in ("confusion_E2-swin-U_white.png", "confusion_E2-swin-U_field.png", "confusion_E2-swin-WF_field.png", "confusion_E3-A-WF_field.png",
                 "scenario_bars.png", "domain_gap.png", "training_curves_E2-swin-U.png", "cases_success.png", "cases_failure.png", "cases_challenging.png"):
        size, dpi = png_size_and_dpi(figures / name)
        assert round(dpi[0]) == 300 and size[0] <= round(5.8 * 300), name
