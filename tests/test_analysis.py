"""Phase 04/07: aggregation over splits, gates G0 and G1, result tables and findings.

Most tests build a synthetic data root (committed-split stand-ins, a choices.json and metrics.json files whose
fingerprints are the ones the registry produces), so G1, which needs E2 runs that do not exist yet, is covered too.
The last tests read the committed E0 runs and pin the numbers that gate G0 decided on.
"""

import json
import math
import shutil

import numpy as np
import pytest

from conftest import REPO_ROOT

SPREAD = np.array([-0.02, -0.01, 0.0, 0.01, 0.02])  # sample std (ddof=1) = 0.01581
STD = float(np.std(SPREAD, ddof=1))
ALL_LRS = {"resnet50": 1e-4, "convnext_tiny": 1e-4, "swin_t": 3e-4}


def subset_block(mixed, field):
    white = mixed + 0.05
    return {
        "mixed": {"n": 10, "accuracy": mixed + 0.02, "macro_f1": mixed},
        "field": {"n": 5, "accuracy": field + 0.02, "macro_f1": field},
        "white": {"n": 5, "accuracy": white + 0.02, "macro_f1": white},
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


def add_run(gs, root, exp_id, mixed, field=None, **tweaks):
    """Write complete synthetic runs for an experiment. ``mixed`` / ``field`` are the mean val mixed / field F1
    (per-split values are mean + SPREAD); test values are val - 0.03."""
    field = mixed - 0.08 if field is None else field
    choices = gs.load_choices(root)
    resolved = gs.resolve_experiment(exp_id, choices)
    folder = gs.runs_dir(root) / gs.run_folder_name(exp_id, choices)
    for seed in range(5):
        metrics = {
            "split": seed, "exp_id": resolved.config.exp_id, "split_sha256": gs.load_split(root, seed)["sha256"],
            "config_fingerprint": gs.expected_fingerprint(resolved.config), "fast": False, "overrides": {},
            "val": subset_block(mixed + SPREAD[seed], field + SPREAD[seed]),
            "test": subset_block(mixed + SPREAD[seed] - 0.03, field + SPREAD[seed] - 0.03),
        }
        metrics.update(tweaks)
        gs.write_json(gs.split_dir(folder, seed) / "metrics.json", metrics)
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


def test_load_ignores_env_json_sweep_and_scratch_but_flags_unknown_folders(gs, root, capsys):
    choices = gs.load_choices(root)
    add_run(gs, root, "E0-rect", 0.8)
    runs = gs.runs_dir(root)
    (runs / "env.json").write_text("{}")
    (runs / "sweep" / "E0-rect_lr1e-4" / "split_0").mkdir(parents=True)
    (runs / "scratch" / "E0-rect_fast" / "split_0").mkdir(parents=True)
    (runs / "mystery" / "split_0").mkdir(parents=True)
    capsys.readouterr()
    results = gs.load_experiments(root, ["E0-rect"], choices)
    err = capsys.readouterr().err
    assert list(results) == ["E0-rect"]
    assert "mystery" in err and "env.json" not in err and "sweep" not in err and "scratch" not in err


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
    gs.summarize(scratch, out=lambda text: None)
    for name in ("table_input_mode.csv", "table_input_mode.md", "table_required.csv", "table_required.md",
                 "table_domains.csv", "table_domains.md", "table_methods.csv", "table_methods.md", "table_segmenter.csv",
                 "table_segmenter.md", "findings.md"):
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
