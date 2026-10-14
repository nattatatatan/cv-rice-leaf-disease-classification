"""The decisions frozen at results-freeze are embedded in the .py (`FROZEN_CHOICES`), `prepare` seeds `choices.json` from them, and the
seeded choices resolve every committed experiment to the fingerprint of its committed run. The gates and choosers that verify once a
decision exists are tested next to the code they change (test_analysis, test_aliases_and_reuse, test_composites)."""

import json
import shutil

import pytest

from conftest import REPO_ROOT

DATA_ROOT = REPO_ROOT / "Dhan-Shomadhan"
RUNS = DATA_ROOT / "_work" / "runs"
COMMITTED_CHOICES = DATA_ROOT / "_work" / "results" / "choices.json"
# every run folder the report draws on (the aliases E1-U, E1-WW and X-domain-WW resolve to one of them)
COMMITTED_EXPERIMENTS = (
    "E0-squash", "E0-pad", "E0-rect", "E1-U", "E1-WW", "E1-FF", "E1-WF", "E2-cnx-U", "E2-cnx-WF", "E2-swin-U", "E2-swin-WF",
    "E3-A", "E3-A-WF", "X-domain-WW",
)


def seeded(gs, tmp_path):
    """A data root whose choices.json `prepare` seeded, and its choices."""
    root = tmp_path / "Dhan-Shomadhan"
    assert gs.seed_choices(root, out=lambda text: None)
    return root, gs.load_choices(root)


def test_the_embedded_constant_is_the_committed_choices_file(gs):
    assert gs.FROZEN_CHOICES == json.loads(COMMITTED_CHOICES.read_text())
    assert set(gs.FROZEN_CHOICES) == {"input_mode", "lr", "backbone", "composite_n_factor", "recommended"}
    assert all("evidence" in entry for key, entry in gs.FROZEN_CHOICES.items() if key != "lr")


def test_seed_choices_writes_the_frozen_decisions_once(gs, tmp_path):
    root = tmp_path / "Dhan-Shomadhan"
    lines = []
    assert gs.seed_choices(root, out=lines.append) is True
    assert len(lines) == 1 and "seeded" in lines[0] and "frozen at results-freeze" in lines[0] and "embedded in this file" in lines[0]
    assert gs.choices_path(root).read_bytes() == COMMITTED_CHOICES.read_bytes(), "byte-identical to the committed file"
    gs.choices_path(root).write_text('{"input_mode": "pad"}')
    assert gs.seed_choices(root, out=lines.append) is False and len(lines) == 1
    assert gs.choices_path(root).read_text() == '{"input_mode": "pad"}', "an existing choices.json is left alone"


def test_load_choices_has_no_side_effects(gs, tmp_path):
    root = tmp_path / "Dhan-Shomadhan"
    assert gs.load_choices(root).data == {}
    assert not root.exists()


def test_prepare_seeds_choices_json_and_leaves_an_existing_one(gs, tmp_path, monkeypatch, capsys):
    root = tmp_path / "Dhan-Shomadhan"
    for name in ("prepare_pseudo_masks", "prepare_composites", "prepare_annotations"):
        monkeypatch.setattr(gs, name, lambda *args, **kwargs: None)
    monkeypatch.setattr(gs, "prepare_data", lambda data_root, workers=None: None)
    monkeypatch.setattr(gs, "load_index", lambda data_root: [])
    assert gs.run_cli(["prepare", "--data-root", str(root)]) == 0
    out = capsys.readouterr().out
    assert out.count("seeded") == 1 and out.strip().splitlines()[-1].startswith("prepare: done in")
    assert gs.load_choices(root).get("backbone") == "swin_t" and gs.load_choices(root).get("recommended") == "E2-swin-U"
    gs.write_choice(root, "input_mode", "pad")
    before = gs.choices_path(root).read_bytes()
    assert gs.run_cli(["prepare", "--data-root", str(root)]) == 0
    assert "seeded" not in capsys.readouterr().out and gs.choices_path(root).read_bytes() == before


@pytest.mark.parametrize("exp_id", COMMITTED_EXPERIMENTS)
def test_seeded_choices_resolve_to_the_fingerprint_of_every_committed_run(gs, tmp_path, exp_id):
    """The proof that the embedding is right: a re-run after `prepare` has the config of the reported run, so it lands in the same
    run folder (layout) and `run` treats the committed splits as current."""
    root, choices = seeded(gs, tmp_path)
    resolved = gs.resolve_experiment(exp_id, choices)
    expected = gs.expected_fingerprint(resolved.config, resolved.composite_factor, root)
    folder = RUNS / gs.run_folder_name(exp_id, choices)
    assert folder.is_dir(), folder
    for split in range(5):
        run_dir = folder / f"split_{split}"
        config = json.loads((run_dir / "config.json").read_text())
        metrics = json.loads((run_dir / "metrics.json").read_text())
        assert expected == config["config_fingerprint"] == metrics["config_fingerprint"], (exp_id, split)
        assert json.loads(json.dumps(gs.asdict(resolved.config))) == config["experiment"], (exp_id, split)
        # the older runs recorded fewer choices (the lr was added later), but every one they did record is the seeded value
        assert config["choices_used"].items() <= resolved.choices_used.items() or resolved.requested != resolved.config.exp_id, (exp_id, split)
        assert gs.result_state(run_dir, gs.load_split(DATA_ROOT, split)["sha256"], expected)[0] == "fresh", (exp_id, split)
    assert gs.run_folder_name(exp_id, choices) == gs.run_folder_name(exp_id, gs.load_choices(DATA_ROOT))


@pytest.mark.parametrize("exp_id", ["E0-rect", "E2-cnx-U", "E2-swin-U"])
@pytest.mark.parametrize("lr", [1e-4, 3e-4])
def test_seeded_choices_resolve_the_sweep_runs_to_their_fingerprints(gs, tmp_path, exp_id, lr):
    root, choices = seeded(gs, tmp_path)
    metrics = json.loads((RUNS / "sweep" / f"{exp_id}_lr{gs.lr_tag(lr)}" / "split_0" / "metrics.json").read_text())
    assert gs.expected_fingerprint(gs.resolve_experiment(exp_id, choices, lr=lr).config) == metrics["config_fingerprint"]


@pytest.mark.parametrize("factor", [0.5, 1.0])
def test_seeded_choices_resolve_the_composite_sweep_runs_to_their_fingerprints(gs, tmp_path, factor):
    root, choices = seeded(gs, tmp_path)
    metrics = json.loads((RUNS / "sweep" / f"E3-A_n{gs.composite_factor_tag(factor)}" / "split_0" / "metrics.json").read_text())
    resolved = gs.resolve_experiment("E3-A", choices, composite_factor=factor)
    assert gs.expected_fingerprint(resolved.config, factor, root) == metrics["config_fingerprint"]


@pytest.mark.parametrize("backbone", ["resnet50", "convnext_tiny", "swin_t"])
def test_choose_lr_on_the_committed_sweeps_matches_the_frozen_lr_and_reuses_the_winner(gs, tmp_path, backbone):
    """Real committed sweep runs, seeded choices: the recomputed lr equals the frozen one, so the marker's `choose-lr` verifies and the
    sweep run is copied to split 0 of the real run folder (provenance.json), which `run` then skips."""
    root, choices = seeded(gs, tmp_path)
    exp_id = gs.SWEEP_EXPERIMENT[backbone]
    for lr in gs.SWEEP_LRS:
        name = f"{exp_id}_lr{gs.lr_tag(lr)}"
        shutil.copytree(RUNS / "sweep" / name, root / "_work" / "runs" / "sweep" / name)
    shutil.copytree(DATA_ROOT / "_work" / "splits", root / "_work" / "splits")
    before = gs.choices_path(root).read_bytes()
    result = gs.choose_lr(root, backbone, out=lambda text: None)
    assert result["outcome"] == "matches" and result["lr"] == choices.get("lr", backbone) and result["split_0"] == "copied"
    assert gs.choices_path(root).read_bytes() == before
    real = gs.split_dir(root / "_work" / "runs" / exp_id, 0)
    expected = gs.expected_fingerprint(gs.resolve_experiment(exp_id, choices).config)
    assert gs.result_state(real, gs.load_split(root, 0)["sha256"], expected)[0] == "fresh"


def test_choose_composites_on_the_committed_sweeps_matches_the_frozen_factor(gs, tmp_path):
    root, choices = seeded(gs, tmp_path)
    for name in ("E3-A_n0.5", "E3-A_n1"):
        shutil.copytree(RUNS / "sweep" / name, root / "_work" / "runs" / "sweep" / name)
    shutil.copytree(DATA_ROOT / "_work" / "splits", root / "_work" / "splits")
    before = gs.choices_path(root).read_bytes()
    result = gs.choose_composites(root, out=lambda text: None)
    assert result["outcome"] == "matches" and result["n_factor"] == 0.5 == choices.get("composite_n_factor") and result["split_0"] == "copied"
    assert gs.choices_path(root).read_bytes() == before
    real = gs.split_dir(root / "_work" / "runs" / "E3-A", 0)
    resolved = gs.resolve_experiment("E3-A", choices)
    expected = gs.expected_fingerprint(resolved.config, resolved.composite_factor, root)
    assert gs.result_state(real, gs.load_split(root, 0)["sha256"], expected)[0] == "fresh"
