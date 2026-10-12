"""Guard against silently invalidating Colab results.

`run` skips a split only when the split sha256 AND the config fingerprint of the stored metrics.json match the
registry. If a change to ExperimentConfig, the registry or the fingerprint recipe alters a fingerprint, every
finished run counts as stale and Colab retrains it (E0 is about 45 minutes per input mode). These tests pin the
fingerprints of the committed runs and of the rows that are not run yet.
"""

from pathlib import Path

import pytest

from conftest import REPO_ROOT

DATA_ROOT = REPO_ROOT / "Dhan-Shomadhan"
RUNS = DATA_ROOT / "_work" / "runs"
E0_MODES = ("squash", "pad", "rect")


def committed_choices(gs):
    return gs.load_choices(DATA_ROOT)


@pytest.mark.parametrize("mode", E0_MODES)
@pytest.mark.parametrize("split", range(5))
def test_registry_reproduces_the_fingerprint_of_every_committed_e0_run(gs, mode, split):
    run_dir = RUNS / f"E0-{mode}" / f"split_{split}"
    config = gs.json.loads((run_dir / "config.json").read_text())
    metrics = gs.json.loads((run_dir / "metrics.json").read_text())
    resolved = gs.resolve_experiment(f"E0-{mode}", committed_choices(gs))
    fingerprint = gs.expected_fingerprint(resolved.config)
    assert gs.json.loads(gs.json.dumps(gs.asdict(resolved.config))) == config["experiment"], "the registry row no longer equals the config that was trained"
    assert fingerprint == config["config_fingerprint"] == metrics["config_fingerprint"], (
        "the config fingerprint changed: `run` would treat the committed Colab results as stale and retrain them"
    )
    assert metrics["split_sha256"] == gs.load_split(DATA_ROOT, split)["sha256"]
    state, _ = gs.result_state(run_dir, metrics["split_sha256"], fingerprint)
    assert state == "fresh"


@pytest.mark.parametrize("split", range(5))
def test_e1_u_resolves_to_the_committed_winning_e0_folder_and_is_skipped(gs, split):
    choices = committed_choices(gs)
    assert choices.get("input_mode") == "rect"
    resolved = gs.resolve_experiment("E1-U", choices)
    assert resolved.config.exp_id == "E0-rect" and resolved.requested == "E1-U"
    assert gs.run_folder_name("E1-U", choices) == "E0-rect"
    run_dir = RUNS / "E0-rect" / f"split_{split}"
    state, _ = gs.result_state(run_dir, gs.load_split(DATA_ROOT, split)["sha256"], gs.expected_fingerprint(resolved.config))
    assert state == "fresh"


def test_committed_sweep_runs_keep_their_fingerprints(gs):
    for lr_tag in ("1e-4", "3e-4"):
        run_dir = RUNS / "sweep" / f"E0-rect_lr{lr_tag}" / "split_0"
        metrics = gs.json.loads((run_dir / "metrics.json").read_text())
        resolved = gs.resolve_experiment("E0-rect", committed_choices(gs), lr=float(lr_tag))
        assert gs.expected_fingerprint(resolved.config) == metrics["config_fingerprint"], lr_tag


# Fingerprints of the rows that Colab runs next, at input_mode rect and lr 1e-4 (the ResNet50 choice; the
# ConvNeXt-T / Swin-T learning rates are not chosen yet, so 1e-4 stands in and only the rest of the definition is pinned).
# If a deliberate change to the recipe or the registry alters these, update them knowing that every Colab run of
# the affected rows must be redone.
GOLDEN = {
    "E1-WW": "7c673c5a2f3387787042151c4929a771790c6e115a4f59b7256257192c421233",
    "E1-FF": "dcc03eb7a5ea856dc444bcf41f4a8678501a975982f4d6b6eb2e6330451cf8da",
    "E1-WF": "e0e8fa18dd6850f30f10db39e171eb3a2c8fc62c9e7a1ee54f05a177b37e09c5",
    "E2-cnx-U": "7b328a708c2d9e7b15ff63e7088b996d9cee0f44d3cbaff03280ed28512b283e",
    "E2-cnx-WF": "fff71012fbb040c0615a9143e1f0cb4fe1ea82d575b513a4d11f258527bb51ef",
    "E2-swin-U": "9276bc924783bb2609617ac26f9612086c1cccbbec1e1d8c821d4b886c732d40",
    "E2-swin-WF": "75a697fad318447a63a4bae165f0e0f4cce1c0e8441bed04440ba00d203294fe",
}


@pytest.mark.parametrize("exp_id", sorted(GOLDEN))
def test_fingerprints_of_the_rows_that_are_not_run_yet_are_pinned(gs, exp_id):
    lrs = {name: 1e-4 for name in gs.BACKBONES}
    choices = gs.Choices(Path("choices.json"), {"input_mode": "rect", "lr": lrs})
    resolved = gs.resolve_experiment(exp_id, choices)
    assert gs.expected_fingerprint(resolved.config) == GOLDEN[exp_id]
