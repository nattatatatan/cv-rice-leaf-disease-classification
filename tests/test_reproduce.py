"""`reproduce`: the chain, `--recommended`, `--splits` / `--fast` pass-through, failure and resume messages. The steps are replaced by
recorders (nothing trains); one test runs `--recommended --fast` for real on the tiny synthetic data."""

import json
import re

import pytest

from test_run import prepared  # noqa: F401  (fixture: a tiny data root with index, cache and split 0)

EXPECTED_CHAIN = [
    "download-weights",
    "prepare",
    "run --exp E0-rect --sweep-lr",
    "choose-lr --backbone resnet50",
    "run --exp E0",
    "gate g0",
    "run --exp E1",
    "run --exp E2-cnx-U --sweep-lr",
    "run --exp E2-swin-U --sweep-lr",
    "choose-lr --backbone convnext_tiny",
    "choose-lr --backbone swin_t",
    "run --exp E2",
    "gate g1",
    "run --exp E3-A --sweep-composites",
    "choose-composites",
    "run --exp E3-A,E3-A-WF",
    "gate g2 --cut B",
    "benchmark",
    "gradcam",
    "summarize",
]


class Calls(list):
    outcomes: dict  # what a gate or chooser reports, by step label (default: matches)


@pytest.fixture
def calls(gs, monkeypatch):
    """Replace every function a step calls with a recorder. ``calls`` lists (step, details) in call order; ``outcomes`` sets what a gate
    or chooser reports (default: matches)."""
    log = Calls()
    log.outcomes = {}

    def outcome(name):
        return {"outcome": log.outcomes.get(name, "matches")}

    monkeypatch.setattr(gs, "download_weights", lambda root: log.append(("download-weights", str(root))))
    monkeypatch.setattr(gs, "run_prepare", lambda root, workers=None, out=print: log.append(("prepare", str(root))))
    monkeypatch.setattr(gs, "run_command", lambda args: log.append(("run", args.exp, args.sweep_lr, args.sweep_composites, tuple(args.splits),
                                                                    args.fast, args.device, str(args.data_root), args.seed_offset)))
    monkeypatch.setattr(gs, "choose_lr", lambda root, backbone, out=print, *, force=False: log.append(("choose-lr", backbone, force)) or outcome(f"choose-lr {backbone}"))
    monkeypatch.setattr(gs, "choose_composites", lambda root, out=print, *, force=False: log.append(("choose-composites", force)) or outcome("choose-composites"))
    monkeypatch.setattr(gs, "run_gate", lambda root, gate, out=print, *, cut=(), force=False, strict=True: log.append(("gate", gate, tuple(cut), force, strict)) or outcome(f"gate {gate}"))
    monkeypatch.setattr(gs, "resolve_device", lambda requested="auto": "cpu")
    monkeypatch.setattr(gs, "run_benchmark", lambda root, device: log.append(("benchmark", device)))
    monkeypatch.setattr(gs, "run_gradcam", lambda root, exp, compare, device, split, runs: log.append(("gradcam", exp, compare, device, split)))
    monkeypatch.setattr(gs, "summarize", lambda root: log.append(("summarize", str(root))))
    return log


def reproduce(gs, root, *flags):
    return gs.run_cli(["reproduce", "--data-root", str(root), *flags])


def test_reproduce_is_a_registered_command_with_a_description(gs, capsys):
    with pytest.raises(SystemExit):
        gs.run_cli(["reproduce", "--help"])
    out = capsys.readouterr().out
    assert "--recommended" in out and "--splits" in out and "about 10 hours on one T4" in out and "about 40 minutes on one T4" in out
    assert all(f". {label}\n" in out for label in EXPECTED_CHAIN)


def test_the_chain_is_the_documented_list(gs):
    assert [step.label for step in gs.REPRODUCE_CHAIN] == EXPECTED_CHAIN
    assert [step.label for step in gs.REPRODUCE_CHAIN if step.needs_all_splits] == ["gate g0", "gate g1", "gate g2 --cut B", "gradcam"]


def test_the_chain_produces_every_reported_run_and_nothing_that_was_cut(gs):
    """Every run folder the tables read is trained by a real `run` step (aliases included); Method B and the X-domain rows are not."""
    trained = []
    for step in gs.REPRODUCE_CHAIN:
        if step.argv[0] == "run" and not {"--sweep-lr", "--sweep-composites"} & set(step.argv):
            trained += gs.expand_experiment_ids(step.argv[2])
    assert set(trained) == {*gs.REPORTED_EXPERIMENTS} and len(trained) == len(set(trained))
    everything = " ".join(step.label for step in gs.REPRODUCE_CHAIN)
    assert not any(word in everything for word in ("E4-B", "S-seg", "X-domain", "seg-eval"))


def test_reproduce_runs_the_chain_in_order_with_the_right_arguments(gs, calls, tmp_path, capsys):
    assert reproduce(gs, tmp_path, "--device", "cuda", "--seed-offset", "3") == 0
    names = [call[0] if call[0] != "run" else f"run {call[1]}{' sweep-lr' if call[2] else ' sweep-composites' if call[3] else ''}" for call in calls]
    assert names == ["download-weights", "prepare", "run E0-rect sweep-lr", "choose-lr", "run E0", "gate", "run E1", "run E2-cnx-U sweep-lr",
                     "run E2-swin-U sweep-lr", "choose-lr", "choose-lr", "run E2", "gate", "run E3-A sweep-composites", "choose-composites",
                     "run E3-A,E3-A-WF", "gate", "benchmark", "gradcam", "summarize"]
    assert [c[1] for c in calls if c[0] == "choose-lr"] == ["resnet50", "convnext_tiny", "swin_t"]
    assert [c[1:] for c in calls if c[0] == "gate"] == [("g0", (), False, False), ("g1", (), False, False), ("g2", ("B",), False, False)], \
        "gates run non-strict (a different outcome warns and the chain goes on)"
    real = [c for c in calls if c[0] == "run" and not c[2] and not c[3]]
    assert [c[1] for c in real] == ["E0", "E1", "E2", "E3-A,E3-A-WF"] and all(c[4] == (0, 1, 2, 3, 4) for c in real)
    assert all(c[6] == "cuda" and c[8] == 3 and c[5] is False and c[7] == str(tmp_path) for c in calls if c[0] == "run")
    assert [c for c in calls if c[0] == "gradcam"] == [("gradcam", None, "E3-A", "cpu", None)]
    out = capsys.readouterr().out
    for number, label in enumerate(EXPECTED_CHAIN, 1):
        assert f"reproduce: [{number}/20] {label}\n" in out
    assert len(re.findall(r"^reproduce: \[\d+/20\] .* done in .*\(total ", out, flags=re.M)) == 20
    assert "summary - 20 of 20 steps done" in out and "gate g0: matches" in out and "choose-composites: matches" in out
    assert f"tables and findings: {tmp_path / '_work' / 'results'}" in out and "figures:" in out


def test_splits_go_to_every_real_run_but_not_to_the_sweeps_and_the_gates_that_need_five_are_skipped(gs, calls, tmp_path, capsys):
    assert reproduce(gs, tmp_path, "--splits", "0") == 0
    runs = [c for c in calls if c[0] == "run"]
    assert [c[4] for c in runs if not c[2] and not c[3]] == [(0,)] * 4
    assert [c[4] for c in runs if c[2] or c[3]] == [(0, 1, 2, 3, 4)] * 4, "the sweeps are split 0 anyway: --splits is not passed to them"
    assert [c[0] for c in calls].count("gate") == 0 and "gradcam" not in [c[0] for c in calls]
    assert [c[0] for c in calls].count("choose-lr") == 3 and "choose-composites" in [c[0] for c in calls]
    out = capsys.readouterr().out
    assert out.count("skipped - it needs all five splits (--splits 0)") == 4
    assert "summary - 16 of 20 steps done, 4 skipped" in out
    calls.clear()
    assert reproduce(gs, tmp_path, "--splits", "4,3,2,1,0") == 0 and [c[0] for c in calls].count("gate") == 3, "all five splits in any order"
    calls.clear()
    assert reproduce(gs, tmp_path, "--splits", "1,2") == 0
    assert [c[4] for c in calls if c[0] == "run" and not c[2] and not c[3]] == [(1, 2)] * 4


def test_recommended_runs_weights_prepare_the_recommended_model_and_summarize(gs, calls, tmp_path, capsys):
    assert reproduce(gs, tmp_path, "--recommended") == 0
    assert [c[0] for c in calls] == ["download-weights", "prepare", "run", "summarize"]
    assert calls[2][1:5] == ("E2-swin-U", False, False, (0, 1, 2, 3, 4)), "the frozen recommendation, before prepare seeded choices.json"
    out = capsys.readouterr().out
    assert "reproduce: [3/4] run --exp E2-swin-U\n" in out and "summary - 4 of 4 steps done" in out and "decisions recomputed" not in out
    calls.clear()
    gs.write_choice(tmp_path, "recommended", "E3-A")
    assert reproduce(gs, tmp_path, "--recommended", "--splits", "0,1", "--device", "cpu") == 0
    assert calls[2][1:5] == ("E3-A", False, False, (0, 1)), "the recommendation of choices.json when there is one"


def test_fast_is_passed_on_skips_the_download_and_needs_recommended(gs, calls, tmp_path, capsys):
    assert reproduce(gs, tmp_path, "--recommended", "--fast", "--splits", "0") == 0
    assert [c[0] for c in calls] == ["prepare", "run", "summarize"] and calls[1][4:6] == ((0,), True)
    assert "skipped - --fast uses the pretrained weights only if they are already downloaded" in capsys.readouterr().out
    calls.clear()
    assert reproduce(gs, tmp_path, "--fast") == 1 and not calls
    assert "--fast only works with --recommended" in capsys.readouterr().err


def test_a_failing_step_stops_the_chain_and_says_how_to_resume(gs, calls, monkeypatch, tmp_path, capsys):
    def failing(args):
        calls.append(("run", args.exp))
        if args.exp == "E0":
            raise gs.ExperimentError("out of patience")

    monkeypatch.setattr(gs, "run_command", failing)
    assert reproduce(gs, tmp_path) == 1
    captured = capsys.readouterr()
    assert [c[0] for c in calls] == ["download-weights", "prepare", "run", "choose-lr", "run"] and calls[-1] == ("run", "E0")
    assert "FAIL at step [5/20] run --exp E0" in captured.err and "out of patience" in captured.err
    assert "the 4 step(s) before it are done" in captured.err and "run the same command again" in captured.err
    assert "summary" not in captured.out
    monkeypatch.setattr(gs, "run_command", lambda args: (_ for _ in ()).throw(KeyboardInterrupt()))
    calls.clear()
    assert reproduce(gs, tmp_path, "--recommended") == 130
    assert "interrupted at step [3/4] run --exp E2-swin-U" in capsys.readouterr().err


def test_a_differing_decision_is_reported_and_the_chain_continues(gs, calls, tmp_path, capsys):
    calls.outcomes["choose-lr swin_t"] = "differs"
    calls.outcomes["gate g1"] = "written"
    assert reproduce(gs, tmp_path) == 0
    out = capsys.readouterr().out
    assert "choose-lr --backbone swin_t: DIFFERS (kept the frozen one, see the warning above)" in out
    assert "gate g1: no frozen decision, recorded" in out and "1 decision(s) differ from the frozen ones" in out
    assert [c[0] for c in calls][-1] == "summarize"


def test_a_choices_file_that_cannot_be_read_stops_before_any_step(gs, calls, tmp_path, capsys):
    gs.choices_path(tmp_path).parent.mkdir(parents=True)
    gs.choices_path(tmp_path).write_text("{not json")
    assert reproduce(gs, tmp_path, "--recommended") == 1 and not calls
    assert "reproduce: FAIL" in capsys.readouterr().err


def test_reproduce_recommended_fast_end_to_end_on_tiny_data(gs, prepared, monkeypatch, capsys):  # noqa: F811
    """No stubs for the run and summarize steps: seeded choices.json -> a real tiny run of E2-swin-U into scratch -> the tables."""
    monkeypatch.setattr(gs, "run_prepare", lambda root, workers=None, out=print: gs.seed_choices(root, out=out))
    assert reproduce(gs, prepared, "--recommended", "--fast", "--splits", "0", "--device", "cpu") == 0
    out = capsys.readouterr().out
    assert "seeded" in out and "[3/4] run --exp E2-swin-U" in out and "summary - 3 of 4 steps done, 0 skipped" not in out
    assert "summary - 3 of 4 steps done, 1 skipped" in out
    metrics = json.loads((prepared / "_work" / "runs" / "scratch" / "E2-swin-U_fast" / "split_0" / "metrics.json").read_text())
    assert metrics["fast"] is True and metrics["backbone"] == "swin_t" and metrics["lr"] == 3e-4
    assert not (prepared / "_work" / "runs" / "E2-swin-U").exists(), "a fast run is never a result"
    assert (prepared / "_work" / "results" / "table_required.md").is_file()
