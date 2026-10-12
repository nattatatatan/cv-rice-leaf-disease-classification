"""Phase 03 T3.1: experiment registry, choices.json resolution, aliases."""

import json
import re

import pytest

from conftest import REPO_ROOT


def readme_experiment_ids():
    """The IDs in the first column of the matrix in docs/instructions/README.md (section 5)."""
    text = (REPO_ROOT / "docs" / "instructions" / "README.md").read_text()
    section = text.split("## 5. Experiment matrix", 1)[1].split("## 6.", 1)[0]
    return re.findall(r"^\| ((?:E|S|X)[\w-]+) \|", section, flags=re.MULTILINE)


def test_registry_covers_every_row_of_the_readme_matrix(gs):
    ids = readme_experiment_ids()
    assert len(ids) >= 16
    for exp_id in ids:
        if exp_id == "X-domain":  # two runs: W->W and F->F
            assert {"X-domain-WW", "X-domain-FF"} <= set(gs.EXPERIMENTS)
        else:
            assert exp_id in gs.EXPERIMENTS, exp_id


def test_select_domains_equal_train_domains_for_every_row(gs):
    for cfg in gs.EXPERIMENTS.values():
        assert set(cfg.select_domains) == set(cfg.train_domains), cfg.exp_id
    wf = gs.EXPERIMENTS["E1-WF"]
    assert wf.train_domains == ("white",) and wf.select_domains == ("white",)
    assert wf.test_subsets[0] == "field"


def test_config_rejects_selecting_on_other_domains(gs):
    with pytest.raises(ValueError, match="select_domains must equal train_domains"):
        gs.ExperimentConfig(
            exp_id="bad", backbone="resnet50", train_domains=("white",), select_domains=("white", "field"),
            test_subsets=("field",), input_mode="rect",
        )


def test_recipe_defaults_match_the_report_table(gs):
    cfg = gs.EXPERIMENTS["E0-rect"]
    assert (cfg.stage1_epochs, cfg.stage1_lr, cfg.epochs) == (2, 1e-3, 30)
    assert (cfg.weight_decay, cfg.warmup_epochs, cfg.label_smoothing) == (0.05, 1, 0.1)
    assert (cfg.batch_size, cfg.grad_accum, cfg.clip_norm, cfg.patience, cfg.dropout) == (32, 1, 1.0, 10, 0.2)
    assert cfg.lr is None, "lr comes from the split-0 sweep recorded in choices.json"


def test_input_sizes_have_an_equal_pixel_budget(gs):
    budgets = {mode: h * w for mode, (h, w) in gs.INPUT_SIZES.items()}
    assert budgets["squash"] == budgets["pad"] == 320 * 320
    assert gs.INPUT_SIZES["rect"] == (448, 224)
    assert abs(budgets["rect"] / budgets["squash"] - 1) < 0.03


@pytest.fixture
def choices_in(gs, tmp_path):
    def make(data=None):
        root = tmp_path / "root"
        (root / "_work" / "results").mkdir(parents=True, exist_ok=True)
        if data is not None:
            (root / "_work" / "results" / "choices.json").write_text(json.dumps(data))
        return gs.load_choices(root)

    return make


def test_fixed_rows_resolve_with_only_the_learning_rate(gs, choices_in):
    choices = choices_in({"lr": {"resnet50": 3e-4}})
    resolved = gs.resolve_experiment("E0-pad", choices)
    assert resolved.config.lr == 3e-4 and resolved.config.input_mode == "pad" and resolved.config.backbone == "resnet50"
    assert resolved.choices_used == {"lr[resnet50]": 3e-4}


def test_missing_choices_file_gives_a_clear_error(gs, choices_in):
    choices = choices_in(None)
    with pytest.raises(gs.ChoicesError) as excinfo:
        gs.resolve_experiment("E1-FF", choices)
    message = str(excinfo.value)
    assert "E1-FF" in message and "choices.json does not exist" in message and "input_mode" in message
    assert "gate G0" in message


def test_missing_lr_names_the_command_that_writes_it(gs, choices_in):
    choices = choices_in({"input_mode": "rect"})
    with pytest.raises(gs.ChoicesError, match=r"lr\[resnet50\].*choose-lr"):
        gs.resolve_experiment("E1-FF", choices)


def test_best_of_rows_read_the_winners(gs, choices_in):
    choices = choices_in({
        "input_mode": {"value": "pad", "evidence": {}},
        "backbone": {"value": "swin_t"},
        "lr": {"resnet50": {"value": 1e-4}, "convnext_tiny": 1e-4, "swin_t": {"value": 3e-4, "evidence": {"1e-4": 0.8}}},
    })
    one = gs.resolve_experiment("E1-FF", choices).config
    assert (one.backbone, one.input_mode, one.lr) == ("resnet50", "pad", 1e-4)
    two = gs.resolve_experiment("E2-cnx-U", choices)
    assert two.config.input_mode == "pad" and two.config.backbone == "convnext_tiny"
    best = gs.resolve_experiment("E4-B", choices).config
    assert (best.backbone, best.input_mode, best.lr, best.seg_crop) == ("swin_t", "pad", 3e-4, True)


def test_invalid_choice_values_are_rejected(gs, choices_in):
    with pytest.raises(gs.ChoicesError, match="invalid input_mode"):
        gs.resolve_experiment("E1-FF", choices_in({"input_mode": "round", "lr": {"resnet50": 3e-4}}))
    with pytest.raises(gs.ChoicesError, match="invalid lr"):
        gs.resolve_experiment("E0-rect", choices_in({"lr": {"resnet50": 5}}))


def test_e1_u_is_an_alias_of_the_winning_e0_row(gs, choices_in):
    choices = choices_in({"input_mode": "pad", "lr": {"resnet50": 3e-4}})
    resolved = gs.resolve_experiment("E1-U", choices)
    assert resolved.requested == "E1-U" and resolved.config.exp_id == "E0-pad"
    assert resolved.config == gs.resolve_experiment("E0-pad", choices).config
    assert any("alias" in note for note in resolved.notes)


def test_fast_placeholders_stand_in_for_missing_choices_and_say_so(gs, choices_in):
    resolved = gs.resolve_experiment("E1-FF", choices_in(None), placeholders=True)
    assert resolved.config.input_mode == "rect" and resolved.config.lr == 3e-4
    assert len(resolved.notes) == 2 and all("--fast" in note for note in resolved.notes)


def test_lr_override_beats_choices(gs, choices_in):
    resolved = gs.resolve_experiment("E0-rect", choices_in({"lr": {"resnet50": 3e-4}}), lr=1e-4)
    assert resolved.config.lr == 1e-4


def test_non_classifier_rows_are_registered_but_not_runnable(gs, choices_in):
    for exp_id, phase in (("S-seg", "phase 06"), ("X-gradcam", "phase 07")):
        with pytest.raises(gs.NotReadyError, match=phase):
            gs.resolve_experiment(exp_id, choices_in({}))


def test_groups_and_unknown_ids(gs):
    assert gs.expand_experiment_ids("E0") == ["E0-squash", "E0-pad", "E0-rect"]
    assert gs.expand_experiment_ids("E1-U, E1-U,E1-WW") == ["E1-U", "E1-WW"]
    assert gs.expand_experiment_ids("X-domain") == ["X-domain-WW", "X-domain-FF"]
    with pytest.raises(gs.UnknownExperimentError, match="Did you mean: E0-rect"):
        gs.expand_experiment_ids("E0-rec")


def test_write_choice_keeps_other_keys(gs, choices_in, tmp_path):
    choices = choices_in({"input_mode": "rect"})
    root = choices.path.parents[2]
    gs.write_choice(root, "lr", 3e-4, {"1e-4": 0.8, "3e-4": 0.9}, sub="resnet50")
    gs.write_choice(root, "lr", 1e-4, sub="swin_t")
    data = json.loads(choices.path.read_text())
    assert data["input_mode"] == "rect"
    assert data["lr"]["resnet50"] == {"value": 3e-4, "evidence": {"1e-4": 0.8, "3e-4": 0.9}}
    assert gs.load_choices(root).get("lr", "swin_t") == 1e-4
