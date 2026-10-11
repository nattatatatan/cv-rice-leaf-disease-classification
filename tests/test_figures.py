"""Phase 02 T2.6: report tables and figures."""

import pytest


@pytest.fixture
def cached(gs, tiny_tree):
    records = gs.build_index(tiny_tree, expected_counts=None)
    gs.build_cache(tiny_tree, records, workers=1)
    return tiny_tree, records


def test_counts_markdown_uses_fixed_class_order_and_totals(gs):
    def rec(i, cls, domain):
        return gs.Record(f"f{i}.jpg", "x", cls, gs.CLASS_NAMES.index(cls), domain, 1, "")

    records = [rec(0, "Sheath Blight", "white"), rec(1, "Sheath Blight", "field"), rec(2, "Brown Spot", "white"), rec(3, "Brown Spot", "white")]
    text = gs.dataset_counts_markdown(records)
    lines = text.splitlines()
    assert lines[0] == "| Class | White background | Field background | Total |"
    assert [line.split("|")[1].strip() for line in lines[2:7]] == list(gs.CLASS_NAMES)
    assert lines[2] == "| Brown Spot | 2 | 0 | 2 |"
    assert lines[6] == "| Sheath Blight | 1 | 1 | 2 |"
    assert lines[7] == "| **Total** | **3** | **1** | **4** |"


def test_real_counts_table(gs, tmp_path):
    prefix = {(cls, domain): p for p, cls, domain, _ in gs.LABEL_TABLE}
    records = [
        gs.Record(f"{prefix[k]}{i}.jpg", "x", k[0], gs.CLASS_NAMES.index(k[0]), k[1], 1, "")
        for k, n in gs.EXPECTED_COUNTS.items()
        for i in range(n)
    ]
    path = gs.write_dataset_counts(tmp_path, records)
    assert path == tmp_path / "_work/results/dataset_counts.md"
    text = path.read_text()
    assert "| Brown Spot | 90 | 49 | 139 |" in text and "| **Total** | **769** | **337** | **1106** |" in text


def png_info(path):
    from PIL import Image

    with Image.open(path) as image:
        return image.size, image.info.get("dpi")


def test_dataset_grid_is_300_dpi_and_deterministic(gs, cached):
    root, records = cached
    first = gs.save_dataset_grid(root, records)
    assert first == root / "_work/figures/dataset_grid.png"
    size, dpi = png_info(first)
    assert round(dpi[0]) == 300 and size[0] == round(5.6 * 300)
    data = first.read_bytes()
    assert gs.save_dataset_grid(root, records).read_bytes() == data, "fixed seed -> identical figure"


def test_dataset_grid_tolerates_missing_cells(gs, cached, tmp_path):
    root, records = cached  # the tiny tree has only 2 of the 5 classes
    path = gs.save_dataset_grid(root, records, tmp_path / "grid.png")
    assert path.stat().st_size > 5000


def test_class_domain_bar_chart(gs, cached, tmp_path):
    root, records = cached
    path = gs.save_class_domain_counts(root, records)
    assert path == root / "_work/figures/class_domain_counts.png"
    size, dpi = png_info(path)
    assert round(dpi[0]) == 300 and size[0] >= 1500


def test_palette_is_okabe_ito(gs):
    assert gs.OKABE_ITO["blue"] == "#0072B2" and gs.OKABE_ITO["orange"] == "#E69F00"
    assert gs.DOMAIN_COLORS == {"white": "#0072B2", "field": "#E69F00"}
    assert gs.pyplot().get_backend().lower() == "agg"
