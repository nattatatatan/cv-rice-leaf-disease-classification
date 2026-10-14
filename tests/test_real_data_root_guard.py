"""The session guard in conftest.py notices a write to the committed results."""

import conftest


def test_the_snapshot_covers_the_frozen_results_and_notices_changes(monkeypatch, tmp_path):
    snapshot = conftest.snapshot_real_results()
    assert "results/choices.json" in snapshot and "results/inference_benchmark.json" in snapshot and "runs/E2-swin-U/split_0/metrics.json" in snapshot
    assert not any("scratch" in name for name in snapshot)
    fake = tmp_path / "Dhan-Shomadhan"
    (fake / "_work" / "results").mkdir(parents=True)
    (fake / "_work" / "results" / "choices.json").write_text("{}")
    monkeypatch.setattr(conftest, "REAL_DATA_ROOT", fake)
    before = conftest.snapshot_real_results()
    assert list(before) == ["results/choices.json"]
    (fake / "_work" / "results" / "choices.json").write_text('{"a": 1}')
    (fake / "_work" / "results" / "inference_benchmark.json").write_text("{}")
    after = conftest.snapshot_real_results()
    assert before != after and set(after) - set(before) == {"results/inference_benchmark.json"}
