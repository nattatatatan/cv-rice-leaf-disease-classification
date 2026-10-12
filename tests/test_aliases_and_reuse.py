"""One training, several names (E1-WW = E1-WF, X-domain-WW = W->F row of the winning backbone) and choose-lr reusing
the winning sweep run as split 0 of the real run."""

import dataclasses
import json

import pytest

from test_analysis import add_run, root  # noqa: F401  (fixtures and helpers of the synthetic data root)


# ---------------------------------------------------------------------------- aliases


def test_e1_ww_is_the_same_training_as_e1_wf(gs, root):
    choices = gs.load_choices(root)
    alias, target = gs.resolve_experiment("E1-WW", choices), gs.resolve_experiment("E1-WF", choices)
    assert alias.config == target.config and alias.requested == "E1-WW"
    assert any("alias of E1-WF" in note for note in alias.notes)
    assert gs.run_folder_name("E1-WW", choices) == "E1-WF"
    assert gs.expected_fingerprint(alias.config) == gs.expected_fingerprint(target.config)
    # the premise of the alias: nothing that defines the training differs between the two registry rows
    ww, wf = gs.EXPERIMENTS["E1-WW"], gs.EXPERIMENTS["E1-WF"]
    ignore = {"exp_id", "note", "test_subsets"}
    differing = {k for k, v in dataclasses.asdict(ww).items() if dataclasses.asdict(wf)[k] != v}
    assert differing <= ignore, differing


@pytest.mark.parametrize("backbone, target", [("resnet50", "E1-WF"), ("convnext_tiny", "E2-cnx-WF"), ("swin_t", "E2-swin-WF")])
def test_x_domain_ww_is_the_w_to_f_row_of_the_winning_backbone(gs, root, backbone, target):
    gs.write_choice(root, "backbone", backbone)
    choices = gs.load_choices(root)
    alias, row = gs.resolve_experiment("X-domain-WW", choices), gs.resolve_experiment(target, choices)
    assert alias.config == row.config and gs.run_folder_name("X-domain-WW", choices) == target
    own = dataclasses.asdict(dataclasses.replace(
        gs.EXPERIMENTS["X-domain-WW"], backbone=backbone, input_mode=row.config.input_mode, lr=row.config.lr))
    other = dataclasses.asdict(row.config)
    assert {k for k in own if own[k] != other[k]} <= {"exp_id", "note", "test_subsets"}


def test_x_domain_ww_needs_the_backbone_choice_and_x_domain_ff_is_not_aliased(gs, root):
    data = json.loads(gs.choices_path(root).read_text())
    gs.choices_path(root).write_text(json.dumps(data))  # no backbone yet
    with pytest.raises(gs.ChoicesError, match="backbone"):
        gs.resolve_experiment("X-domain-WW", gs.load_choices(root))
    gs.write_choice(root, "backbone", "swin_t")
    ff = gs.resolve_experiment("X-domain-FF", gs.load_choices(root))
    assert ff.config.exp_id == "X-domain-FF" and not any("alias" in n for n in ff.notes)


def test_summarize_still_has_an_e1_ww_row_with_the_white_test_of_the_e1_wf_runs(gs, root):
    add_run(gs, root, "E0-rect", 0.8)
    add_run(gs, root, "E1-WF", 0.7, 0.5)
    exp, problems = gs.load_experiment(root, "E1-WW", gs.load_choices(root))
    assert problems == [] and exp.exp_id == "E1-WW" and exp.run_name == "E1-WF"
    gs.summarize(root, out=lambda text: None)
    rows = {line.split(" | ")[0].lstrip("| "): line for line in (gs.results_dir(root) / "table_domains.md").read_text().splitlines()
            if line.startswith("| E")}
    ww, wf = rows["E1-WW"].split(" | "), rows["E1-WF"].split(" | ")
    assert ww[3:5] == wf[3:5] and "pending" not in rows["E1-WW"]  # white macro-F1 and accuracy are the E1-WF numbers
    assert ww[5:7] == ["-", "-"]  # E1-WW is about the white test only


def test_run_of_e1_ww_trains_nothing_once_e1_wf_is_done(gs, root, capsys):
    add_run(gs, root, "E1-WF", 0.7, 0.5)
    code = gs.run_cli(["run", "--data-root", str(root), "--device", "cpu", "--exp", "E1-WW"])
    out = capsys.readouterr().out
    assert code == 0 and out.count("] skipped:") == 5 and "alias of E1-WF" in out
    assert not (gs.runs_dir(root) / "E1-WW").exists()


# ---------------------------------------------------------------------------- choose-lr reuses the sweep run


def make_sweep_runs(gs, root, scores=(0.60, 0.70), exp_id="E2-cnx-U", backbone="convnext_tiny", **tweaks):
    """Sweep runs for both learning rates with the fingerprints a real sweep writes, plus dummy extra files."""
    choices = gs.load_choices(root)
    for lr, score in zip(gs.SWEEP_LRS, scores):
        resolved = gs.resolve_experiment(exp_id, choices, lr=lr)
        folder = gs.split_dir(gs.sweep_dir(root) / gs.sweep_run_name(exp_id, lr), 0)
        metrics = {
            "exp_id": exp_id, "backbone": backbone, "lr": lr, "split": 0, "fast": False, "overrides": {},
            "split_sha256": gs.load_split(root, 0)["sha256"], "config_fingerprint": gs.expected_fingerprint(resolved.config),
            "val": {"mixed": {"macro_f1": score}}, "test": {"mixed": {"macro_f1": 0.5}}, **tweaks,
        }
        gs.write_json(folder / "metrics.json", metrics, indent=1)
        gs.write_json(folder / "config.json", {"experiment": exp_id, "lr": lr})
        (folder / "best.pt").write_bytes(b"checkpoint-%d" % round(lr * 1e6))
        (folder / "history.csv").write_text("epoch\n1\n")


@pytest.fixture
def without_e2_lrs(gs, root):
    """choices.json as it is before Batch 3: input mode and the ResNet50 lr only."""
    data = json.loads(gs.choices_path(root).read_text())
    data["lr"] = {"resnet50": data["lr"]["resnet50"]}
    gs.choices_path(root).write_text(json.dumps(data))
    return root


def test_choose_lr_copies_the_winning_sweep_run_to_split_0_and_run_skips_it(gs, without_e2_lrs, capsys):
    root = without_e2_lrs
    make_sweep_runs(gs, root, scores=(0.60, 0.70))
    lines = []
    result = gs.choose_lr(root, "convnext_tiny", out=lines.append)
    assert result["lr"] == 3e-4 and result["split_0"] == "copied"
    sweep = gs.split_dir(gs.sweep_dir(root) / "E2-cnx-U_lr3e-4", 0)
    real = gs.split_dir(gs.runs_dir(root) / "E2-cnx-U", 0)
    assert sorted(p.name for p in real.iterdir()) == sorted([*(p.name for p in sweep.iterdir()), "provenance.json"])
    for path in sweep.iterdir():  # byte-identical copies, the sweep copy stays for the evidence trail
        assert (real / path.name).read_bytes() == path.read_bytes()
    provenance = json.loads((real / "provenance.json").read_text())
    assert provenance["copied_from"] == "sweep/E2-cnx-U_lr3e-4/split_0" and provenance["lr"] == 3e-4
    assert "copied to split 0 of E2-cnx-U" in lines[-1]
    assert not list(real.parent.glob("*.tmp*"))
    # the other sweep run is not copied, and the real run now skips split 0
    choices = gs.load_choices(root)
    fingerprint = gs.expected_fingerprint(gs.resolve_experiment("E2-cnx-U", choices).config)
    assert gs.result_state(real, gs.load_split(root, 0)["sha256"], fingerprint)[0] == "fresh"
    code = gs.run_cli(["run", "--data-root", str(root), "--device", "cpu", "--exp", "E2-cnx-U", "--splits", "0"])
    assert code == 0 and "skipped" in capsys.readouterr().out
    # the summary of the T3.4 rule is unchanged
    assert choices.get("lr", "convnext_tiny") == 3e-4


def test_choose_lr_picks_the_other_sweep_run_when_it_wins(gs, without_e2_lrs):
    root = without_e2_lrs
    make_sweep_runs(gs, root, scores=(0.80, 0.70))
    assert gs.choose_lr(root, "convnext_tiny", out=lambda text: None)["split_0"] == "copied"
    assert (gs.split_dir(gs.runs_dir(root) / "E2-cnx-U", 0) / "best.pt").read_bytes() == b"checkpoint-100"


def test_an_existing_real_split_0_is_never_overwritten(gs, without_e2_lrs):
    root = without_e2_lrs
    make_sweep_runs(gs, root)
    real = gs.split_dir(gs.runs_dir(root) / "E2-cnx-U", 0)
    gs.write_json(real / "metrics.json", {"marker": "earlier real run"})
    lines = []
    assert gs.choose_lr(root, "convnext_tiny", out=lines.append)["split_0"] == "exists"
    assert json.loads((real / "metrics.json").read_text()) == {"marker": "earlier real run"}
    assert not (real / "provenance.json").exists() and "left untouched" in lines[-1]


def test_reuse_is_refused_when_the_fingerprint_differs(gs, without_e2_lrs):
    root = without_e2_lrs
    make_sweep_runs(gs, root, config_fingerprint="0" * 64)
    lines = []
    result = gs.choose_lr(root, "convnext_tiny", out=lines.append)
    assert result["lr"] == 3e-4 and result["split_0"] == "not reused"  # the lr choice itself still succeeds
    assert "not reused" in lines[-1] and "fingerprint" in lines[-1]
    assert not (gs.runs_dir(root) / "E2-cnx-U").exists()


def test_reuse_is_refused_when_the_split_differs(gs, without_e2_lrs):
    root = without_e2_lrs
    make_sweep_runs(gs, root, split_sha256="f" * 64)
    lines = []
    assert gs.choose_lr(root, "convnext_tiny", out=lines.append)["split_0"] == "not reused"
    assert "split sha256" in lines[-1] and not (gs.runs_dir(root) / "E2-cnx-U").exists()


def test_reuse_is_refused_for_the_lr_that_lost_and_for_dev_runs(gs, without_e2_lrs):
    root = without_e2_lrs
    make_sweep_runs(gs, root, scores=(0.60, 0.70))
    gs.choose_lr(root, "convnext_tiny", out=lambda text: None)
    real = gs.split_dir(gs.runs_dir(root) / "E2-cnx-U", 0)
    for path in sorted(real.rglob("*"), reverse=True):
        path.unlink() if path.is_file() else path.rmdir()
    real.rmdir()
    with pytest.raises(gs.ExperimentError, match="fingerprint"):  # choices.json says 3e-4, this sweep run used 1e-4
        gs.reuse_sweep_run(root, "convnext_tiny", 1e-4)
    make_sweep_runs(gs, root, scores=(0.60, 0.70), fast=True)
    with pytest.raises(gs.ExperimentError, match="fast"):
        gs.reuse_sweep_run(root, "convnext_tiny", 3e-4)
    assert not real.exists()


def test_choose_lr_for_resnet50_leaves_the_committed_e0_rect_split_0_alone(gs):
    from conftest import REPO_ROOT

    data_root = REPO_ROOT / "Dhan-Shomadhan"
    assert gs.reuse_sweep_run(data_root, "resnet50", 1e-4) == "exists"
