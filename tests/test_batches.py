"""Batch 2 (E1) and Batch 3 (E2) readiness: every row resolves from the committed choices.json, the E2 sweeps do not
need their own learning rate, and what `run --sweep-lr` writes is what `choose-lr` reads (for every backbone)."""

import json
from argparse import Namespace

import pytest

from conftest import REPO_ROOT

DATA_ROOT = REPO_ROOT / "Dhan-Shomadhan"


def test_e1_rows_resolve_from_the_committed_choices(gs):
    choices = gs.load_choices(DATA_ROOT)
    alias = gs.resolve_experiment("E1-U", choices)
    assert alias.config.exp_id == "E0-rect" and gs.run_folder_name("E1-U", choices) == "E0-rect"
    for exp_id, train in (("E1-WW", ("white",)), ("E1-FF", ("field",)), ("E1-WF", ("white",))):
        config = gs.resolve_experiment(exp_id, choices).config
        assert (config.backbone, config.input_mode, config.lr, config.train_domains) == ("resnet50", "rect", 1e-4, train)


@pytest.mark.parametrize("exp_id, backbone", [("E2-cnx-U", "convnext_tiny"), ("E2-swin-U", "swin_t")])
def test_e2_sweeps_use_rect_and_do_not_need_their_own_lr(gs, exp_id, backbone):
    # the state before Batch 3: input mode and the ResNet50 lr are chosen, the E2 learning rates are not
    committed = gs.load_choices(DATA_ROOT)
    choices = gs.Choices(committed.path, {"input_mode": committed.data["input_mode"], "lr": {"resnet50": committed.data["lr"]["resnet50"]}})
    for lr in gs.SWEEP_LRS:
        config = gs.resolve_experiment(exp_id, choices, lr=lr).config
        assert (config.backbone, config.input_mode, config.lr) == (backbone, "rect", lr)
    with pytest.raises(gs.ChoicesError, match=rf"lr\[{backbone}\]"):  # a plain run waits for choose-lr
        gs.resolve_experiment(exp_id, choices)
    with pytest.raises(gs.ChoicesError, match=rf"lr\[{backbone}\]"):
        gs.resolve_experiment(exp_id.replace("-U", "-WF"), choices)


@pytest.mark.parametrize("exp_id, backbone", [("E2-cnx-U", "convnext_tiny"), ("E2-swin-U", "swin_t")])
def test_sweep_output_is_what_choose_lr_reads_and_unlocks_the_e2_rows(gs, tmp_path, exp_id, backbone):
    root = tmp_path / "root"
    gs.write_json(gs.choices_path(root), {"input_mode": {"value": "rect", "evidence": {}}}, indent=2)
    choices = gs.load_choices(root)
    args = Namespace(out_dir=None, sweep_lr=True, fast=False)
    for lr, score in zip(gs.SWEEP_LRS, (0.6, 0.7)):
        config = gs.resolve_experiment(exp_id, choices, lr=lr).config
        folder, name = gs.run_destination(root, args, config, dev=False)
        metrics = {"backbone": backbone, "lr": lr, "split_sha256": "abc", "fast": False, "overrides": {},
                   "val": {"mixed": {"macro_f1": score}}}
        gs.write_json(gs.split_dir(folder / name, 0) / "metrics.json", metrics)
    assert gs.run_cli(["--data-root", str(root), "choose-lr", "--backbone", backbone]) == 0
    choices = gs.load_choices(root)
    assert choices.get("lr", backbone) == 3e-4
    assert json.loads(choices.path.read_text())["lr"][backbone]["evidence"]["experiment"] == exp_id
    for row in (exp_id, exp_id.replace("-U", "-WF")):
        config = gs.resolve_experiment(row, choices).config
        assert (config.backbone, config.input_mode, config.lr) == (backbone, "rect", 3e-4)
