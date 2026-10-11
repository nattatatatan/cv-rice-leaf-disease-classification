"""Phase 03 T3.4 and metrics: schedule, checkpoint selection, LP-FT behaviour, determinism, OOM fallback."""

import math

import numpy as np
import pytest
import torch

from conftest import make_cache


def test_lr_schedule_warms_up_then_decays_to_zero(gs):
    kw = dict(base_lr=3e-4, warmup_steps=10, total_steps=100)
    lrs = [gs.lr_at_step(s, **kw) for s in range(100)]
    assert lrs[0] == pytest.approx(3e-5) and lrs[9] == pytest.approx(3e-4)
    assert all(a < b for a, b in zip(lrs[:9], lrs[1:10])), "linear warmup"
    assert all(a >= b for a, b in zip(lrs[10:], lrs[11:])), "cosine decay"
    assert 0 <= lrs[-1] < 1e-3 * 3e-4, "cosine reaches ~0 at the last step"
    assert gs.lr_at_step(0, base_lr=1.0, warmup_steps=0, total_steps=4) == pytest.approx(1.0)


def test_patience_counts_only_stage_two_epochs(gs):
    selector = gs.CheckpointSelector(patience=3)
    snap = lambda: {"w": 1}
    assert selector.update(0.5, 1, snap, counts_for_patience=False)
    assert not selector.update(0.4, 2, snap, counts_for_patience=False)  # stage 1 never runs patience out
    assert selector.stale == 0 and not selector.should_stop
    assert selector.update(0.6, 3, snap, counts_for_patience=True)
    for epoch in (4, 5):
        assert not selector.update(0.6, epoch, snap, counts_for_patience=True)  # ties are not improvements
        assert not selector.should_stop
    assert not selector.update(0.1, 6, snap, counts_for_patience=True)
    assert selector.should_stop and selector.best_epoch == 3 and selector.best_score == 0.6
    selector2 = gs.CheckpointSelector(patience=2)
    selector2.update(0.5, 1, snap, counts_for_patience=True)
    selector2.update(0.4, 2, snap, counts_for_patience=True)
    selector2.update(0.7, 3, snap, counts_for_patience=True)  # an improvement resets the counter
    assert selector2.stale == 0


def test_classification_metrics_match_hand_computation(gs):
    y_true = [0, 0, 1, 1, 2, 2, 3, 4]
    y_pred = [0, 1, 1, 1, 2, 0, 3, 4]
    m = gs.classification_metrics(y_true, y_pred)
    assert m["n"] == 8 and m["accuracy"] == pytest.approx(6 / 8)
    f1 = [m["per_class"][c]["f1"] for c in gs.CLASS_NAMES]
    assert f1 == pytest.approx([0.5, 0.8, 2 / 3, 1.0, 1.0])
    assert m["macro_f1"] == pytest.approx(np.mean(f1))
    assert np.array(m["confusion_matrix"]).shape == (5, 5) and np.trace(np.array(m["confusion_matrix"])) == 6
    assert m["per_class"]["Brown Spot"]["support"] == 2
    assert gs.classification_metrics([], [])["macro_f1"] is None


def test_subset_metrics_has_white_field_mixed_and_domain_balanced(gs):
    labels = np.array([0, 1, 2, 3, 0, 1, 2, 3])
    domains = ["white"] * 4 + ["field"] * 4
    probs = np.eye(5)[[0, 1, 2, 3, 1, 1, 2, 0]]  # white perfect, field 2 of 4 right
    m = gs.subset_metrics(probs, labels, domains)
    assert m["white"]["accuracy"] == 1.0 and m["field"]["accuracy"] == 0.5 and m["mixed"]["accuracy"] == 0.75
    assert m["domain_balanced"]["macro_f1"] == pytest.approx((m["white"]["macro_f1"] + m["field"]["macro_f1"]) / 2)
    only_white = gs.subset_metrics(probs[:4], labels[:4], domains[:4])
    assert only_white["field"]["n"] == 0 and only_white["domain_balanced"]["macro_f1"] is None


def tiny_setup(gs, tmp_path, n=10):
    root = tmp_path / "root"
    records = make_cache(gs, root, n=n)
    tf_train = gs.ImageTransform("rect", train=True, size_div=4)
    tf_eval = gs.ImageTransform("rect", train=False, size_div=4)
    train_ds = gs.LeafDataset(root, records, tf_train, seed=1)
    val_set = gs.materialize(gs.LeafDataset(root, records[:6], tf_eval))
    return root, train_ds, val_set


def fast_cfg(gs, **kw):
    base = gs.replace(gs.EXPERIMENTS["E0-rect"], backbone="resnet50", lr=3e-4, pretrained=False, size_div=4,
                      batch_size=4, stage1_epochs=1, epochs=2, patience=5)
    return gs.replace(base, **kw)


def test_linear_probe_updates_only_the_head_and_freezes_batchnorm(gs, tmp_path):
    _, train_ds, val_set = tiny_setup(gs, tmp_path)
    cfg = fast_cfg(gs, stage1_epochs=2, epochs=0)
    gs.seed_everything(0)
    model = gs.build_model("resnet50", pretrained=False)
    head_ids = {id(p) for p in gs.head_parameters(model)}
    head_keys = {k for k, v in model.state_dict().items() if k.startswith("fc.")}
    before = {k: v.clone() for k, v in model.state_dict().items()}
    outcome = gs.train_classifier(cfg, model, train_ds, val_set, "cpu", seed=0, log=lambda _: None)
    after = model.state_dict()
    assert [r["stage"] for r in outcome.history] == ["lp", "lp"]
    assert all(r["lr"] == 1e-3 for r in outcome.history), "stage 1 uses lr 1e-3 on the head"
    for key, value in before.items():
        if key.endswith("num_batches_tracked"):
            continue
        same = torch.equal(value, after[key])
        assert same == (key not in head_keys), f"{key}: frozen backbone (incl. BatchNorm stats) must not change"
    assert head_ids


def test_two_stage_training_history_and_determinism(gs, tmp_path):
    _, train_ds, val_set = tiny_setup(gs, tmp_path)
    cfg = fast_cfg(gs)

    def run():
        gs.seed_everything(5)
        model = gs.build_model("resnet50", pretrained=False)
        return gs.train_classifier(cfg, model, train_ds, val_set, "cpu", seed=5, log=lambda _: None)

    a, b = run(), run()
    assert [r["stage"] for r in a.history] == ["lp", "ft", "ft"]
    assert [r["epoch"] for r in a.history] == [1, 2, 3]
    assert a.history[1]["lr"] <= 3e-4 and a.history[2]["lr"] < a.history[1]["lr"], "warmup epoch then cosine"
    assert a.history[2]["lr"] >= 0 and all(math.isfinite(r["train_loss"]) for r in a.history)
    assert [r["train_loss"] for r in a.history] == pytest.approx([r["train_loss"] for r in b.history])
    assert a.best_epoch == b.best_epoch and set(a.best_state) == set(b.best_state)
    assert a.best_score == max(r["val_macro_f1"] for r in a.history)


def test_select_domains_decide_the_checkpoint_metric(gs, tmp_path):
    _, train_ds, val_set = tiny_setup(gs, tmp_path)
    cfg = fast_cfg(gs, train_domains=("white",), select_domains=("white",), stage1_epochs=1, epochs=1)
    gs.seed_everything(0)
    outcome = gs.train_classifier(cfg, gs.build_model("resnet50", pretrained=False), train_ds, val_set, "cpu",
                                  seed=0, log=lambda _: None)
    assert all(r["val_macro_f1"] == r["val_f1_white"] for r in outcome.history)


def test_out_of_memory_retries_with_batch_16_and_accumulation_2(gs, monkeypatch):
    seen = []

    def fake_train(cfg, model, train_ds, val_set, device, **kw):
        seen.append((cfg.batch_size, cfg.grad_accum))
        if cfg.batch_size == 32:
            raise RuntimeError("CUDA out of memory. Tried to allocate 2.00 GiB")
        return "outcome"

    monkeypatch.setattr(gs, "train_classifier", fake_train)
    cfg = gs.replace(gs.EXPERIMENTS["E0-rect"], lr=3e-4, pretrained=False)
    model, outcome, used = gs.train_with_fallback(cfg, None, None, gs.RunOptions(device="cpu", num_workers=0), 0, lambda _: None)
    assert seen == [(32, 1), (16, 2)] and outcome == "outcome" and (used.batch_size, used.grad_accum) == (16, 2)
    monkeypatch.setattr(gs, "train_classifier", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("something else")))
    with pytest.raises(RuntimeError, match="something else"):
        gs.train_with_fallback(cfg, None, None, gs.RunOptions(device="cpu", num_workers=0), 0, lambda _: None)


def test_gradient_accumulation_runs_and_counts_steps(gs, tmp_path):
    _, train_ds, val_set = tiny_setup(gs, tmp_path)
    cfg = fast_cfg(gs, batch_size=2, grad_accum=2, stage1_epochs=0, epochs=1)
    outcome = gs.train_classifier(cfg, gs.build_model("resnet50", pretrained=False), train_ds, val_set, "cpu", seed=0,
                                  log=lambda _: None)
    assert len(outcome.history) == 1 and math.isfinite(outcome.history[0]["train_loss"])
