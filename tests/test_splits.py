"""Phase 02 T2.5: stratified, group-aware splits (run on a synthetic index: no image files needed)."""

import json
import re

import numpy as np
import pytest


@pytest.fixture(scope="module")
def records(gs):
    """1106 fake records with the real class x domain counts."""
    prefix = {(cls, domain): p for p, cls, domain, _ in gs.LABEL_TABLE}
    out = []
    for (cls, domain), n in gs.EXPECTED_COUNTS.items():
        for i in range(n):
            name = f"{prefix[(cls, domain)]}{i}.jpg"
            out.append(gs.Record(name, f"x/{name}", cls, gs.CLASS_NAMES.index(cls), domain, 1, "0" * 40))
    return sorted(out, key=lambda r: r.filename)


def target(n: int, pct: int = 15) -> int:
    return int(n * pct / 100 + 0.5)


def test_split_size_rounds_half_up(gs):
    assert [gs.split_size(n) for n in (0, 1, 3, 4, 10, 49, 64, 74, 90)] == [0, 0, 0, 1, 2, 7, 10, 11, 14]
    assert gs.split_size(90) == 14  # 13.5 -> 14, exactly half
    assert gs.split_size(30) == 5 and gs.split_size(50) == 8  # 4.5 -> 5 and 7.5 -> 8


def test_partition_is_disjoint_and_complete(gs, records):
    names = {r.filename for r in records}
    for seed in gs.SPLIT_SEEDS:
        split = gs.make_split(records, [], seed)
        parts = [set(split[k]) for k in ("train", "val", "test")]
        assert parts[0].isdisjoint(parts[1]) and parts[0].isdisjoint(parts[2]) and parts[1].isdisjoint(parts[2])
        assert parts[0] | parts[1] | parts[2] == names
        assert sum(len(p) for p in parts) == 1106
        for key in ("train", "val", "test"):
            assert split[key] == sorted(split[key])


def test_every_stratum_is_within_one_of_the_target(gs, records):
    by_stratum = {}
    for r in records:
        by_stratum.setdefault(r.stratum, []).append(r.filename)
    for seed in gs.SPLIT_SEEDS:
        split = gs.make_split(records, [], seed)
        for stratum, names in by_stratum.items():
            n = len(names)
            test = sum(x in set(names) for x in split["test"])
            val = sum(x in set(names) for x in split["val"])
            assert abs(test - 0.15 * n) <= 1 and abs(val - 0.15 * n) <= 1, (stratum, test, val, n)
            assert test == target(n) == val


def test_expected_split_sizes(gs, records):
    split = gs.make_split(records, [], 0)
    counts = gs.split_counts(split, records)
    assert counts["train"]["all"] + counts["val"]["all"] + counts["test"]["all"] == 1106
    assert 770 <= counts["train"]["all"] <= 780
    assert 160 <= counts["val"]["all"] <= 170 and 160 <= counts["test"]["all"] <= 170
    assert 45 <= counts["test"]["field"] <= 55
    assert counts["test"]["white"] + counts["test"]["field"] == counts["test"]["all"]


def test_same_seed_same_sha_different_seeds_differ(gs, records):
    first = gs.make_split(records, [], 3)
    assert gs.make_split(records, [], 3) == first
    assert gs.make_split(list(reversed(records)), [], 3) == first, "input order does not matter"
    shas = {gs.make_split(records, [], s)["sha256"] for s in gs.SPLIT_SEEDS}
    assert len(shas) == 5
    assert re.fullmatch(r"[0-9a-f]{64}", first["sha256"])
    assert len({tuple(gs.make_split(records, [], s)["test"]) for s in gs.SPLIT_SEEDS}) == 5


def test_sha256_serialisation_is_what_the_docs_say(gs):
    import hashlib

    expected = hashlib.sha256(
        b'{"seed":2,"test":["c.jpg"],"train":["a.jpg","b.jpg"],"val":["d.jpg"]}'
    ).hexdigest()
    assert gs.split_sha256(2, ["b.jpg", "a.jpg"], ["d.jpg"], ["c.jpg"]) == expected


def test_golden_value_for_seed_0_is_stable(gs, records):
    """Guards against an accidental change of the algorithm (and so of every committed split)."""
    split = gs.make_split(records, [], 0)
    assert split["sha256"] == gs.split_sha256(0, split["train"], split["val"], split["test"])
    # Pinned on purpose: if this changes, every committed split_*.json (and every run's recorded sha) changes.
    assert split["sha256"] == "a1547a447e3b1341c71d47d5744846b3b3e73fb6156c742c4ea0a14ac176aa64"
    assert gs.make_split(records, [], 4)["sha256"] == "88b056b603e75b6d3d7cc451fe4837d17c87ef3b45070d0e60baa603d8262167"
    assert (len(split["train"]), len(split["val"]), len(split["test"])) == (774, 166, 166)


def random_groups(records, rng, n=25):
    """Random groups of 2-3 images, each inside one class x domain stratum (the only valid kind)."""
    by_stratum = {}
    for r in records:
        by_stratum.setdefault(r.stratum, []).append(r.filename)
    strata = sorted(by_stratum)
    used, groups = set(), []
    while len(groups) < n:
        names = by_stratum[strata[int(rng.integers(len(strata)))]]
        group = [names[i] for i in rng.choice(len(names), size=int(rng.integers(2, 4)), replace=False)]
        if used.isdisjoint(group):
            used.update(group)
            groups.append(group)
    return groups


def test_duplicate_groups_never_straddle_splits(gs, records):
    groups = random_groups(records, np.random.default_rng(0), 40)
    for seed in gs.SPLIT_SEEDS:
        split = gs.make_split(records, groups, seed)
        where = {n: part for part in ("train", "val", "test") for n in split[part]}
        assert len(where) == 1106
        for group in groups:
            assert len({where[n] for n in group}) == 1, group


def test_embedded_groups_are_valid_and_never_straddle_splits_for_any_seed(gs, records):
    """The real embedded list against an index with the real filenames (synthetic file contents)."""
    groups = gs.validate_duplicate_groups(gs.DUPLICATE_GROUPS, records)
    assert (len(groups), sum(len(g) for g in groups)) == (36, 77)
    for seed in gs.SPLIT_SEEDS:
        split = gs.make_split(records, gs.DUPLICATE_GROUPS, seed)
        where = {n: part for part in ("train", "val", "test") for n in split[part]}
        assert all(len({where[n] for n in g}) == 1 for g in groups), seed
        counts = gs.split_counts(split, records)
        assert counts["train"]["all"] + counts["val"]["all"] + counts["test"]["all"] == 1106


def test_group_units_count_as_one_in_the_stratum_arithmetic(gs, records):
    first = [r.filename for r in records if r.stratum == ("Brown Spot", "white")][:2]
    units = gs.build_units(records, [first])
    assert tuple(sorted(first)) in units[("Brown Spot", "white")]
    assert sum(len(u) for us in units.values() for u in us) == 1106
    assert len(units[("Brown Spot", "white")]) == gs.EXPECTED_COUNTS[("Brown Spot", "white")] - 1


def test_invalid_groups_fail_loudly(gs, records):
    white = [r.filename for r in records if r.stratum == ("Brown Spot", "white")]
    field = next(r.filename for r in records if r.stratum == ("Brown Spot", "field"))
    other_class = next(r.filename for r in records if r.stratum == ("Rice Blast", "white"))
    cases = [
        ([[white[0], "ghost.jpg"]], "ghost.jpg is not in the dataset index"),
        ([[white[0], white[1]], [white[1], white[2]]], f"{white[1]} appears in duplicate groups #0 and #1"),
        ([[white[0], white[0]]], f"{white[0]} appears in duplicate groups #0 and #0"),
        ([[white[0], field]], "spans several class x domain strata"),
        ([[white[0], other_class]], "spans several class x domain strata"),
        ([[white[0]]], "at least 2 filenames"),
        ([[]], "at least 2 filenames"),
        ([[white[0], 3]], "at least 2 filenames"),
        ([white[0]], "at least 2 filenames"),
    ]
    for groups, message in cases:
        with pytest.raises(gs.DatasetError, match=message):
            gs.validate_duplicate_groups(groups, records)
        with pytest.raises(gs.DatasetError, match=message):
            gs.make_split(records, groups, 0)


def test_validate_returns_sorted_groups_and_accepts_empty(gs, records):
    a, b, c, d = [r.filename for r in records if r.stratum == ("Brown Spot", "white")][:4]
    assert gs.validate_duplicate_groups([[d, c], [b, a]], records) == sorted([sorted([c, d]), sorted([a, b])])
    assert gs.validate_duplicate_groups([], records) == []


def test_groups_change_the_split_only_through_units(gs, records):
    a, b = [r.filename for r in records if r.stratum == ("Brown Spot", "white")][:2]
    grouped = gs.make_split(records, [[a, b]], 0)
    where = {n: p for p in ("train", "val", "test") for n in grouped[p]}
    assert where[a] == where[b]


def test_write_and_load_round_trip(gs, records, tmp_path):
    status = gs.write_splits(tmp_path, records, [])
    assert status == {s: "new" for s in gs.SPLIT_SEEDS}
    assert gs.write_splits(tmp_path, records, []) == {s: "unchanged" for s in gs.SPLIT_SEEDS}
    for seed in gs.SPLIT_SEEDS:
        loaded = gs.load_split(tmp_path, seed)
        assert loaded == gs.make_split(records, [], seed)
        assert set(json.loads(gs.split_path(tmp_path, seed).read_text())) == {"seed", "train", "val", "test", "sha256"}
    # a different duplicate state is reported as CHANGED and rewritten
    pair = [r.filename for r in records if r.stratum == ("Brown Spot", "white")][:2]
    changed = gs.write_splits(tmp_path, records, [pair])
    assert "CHANGED" in changed.values()


def test_load_split_detects_hand_edits_and_missing_files(gs, records, tmp_path):
    with pytest.raises(gs.DatasetError, match="prepare"):
        gs.load_split(tmp_path, 0)
    gs.write_splits(tmp_path, records, [], seeds=(0,))
    path = gs.split_path(tmp_path, 0)
    data = json.loads(path.read_text())
    data["test"], data["train"] = data["train"][:1], data["test"] + data["train"][1:]
    path.write_text(json.dumps(data))
    with pytest.raises(gs.DatasetError, match="sha256"):
        gs.load_split(tmp_path, 0)
