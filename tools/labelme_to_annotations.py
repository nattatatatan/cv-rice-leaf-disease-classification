#!/usr/bin/env python3
"""Convert the labelme files of the 30 hand-annotated field images into annotations/field_salient_leaf.json.

Dev-only (labelme is not a runtime dependency and this tool is not part of the submission). Usage, from the
repo root, after annotating with the command in docs/instructions/annotation-guide.md::

    python tools/labelme_to_annotations.py

Input:  one labelme JSON per selected image in ``annotations/labelme/`` (``--labelme-dir``), and the list of the 30
        images in ``Dhan-Shomadhan/_work/annotations/selection.json`` (written by ``prepare``).
Output: ``annotations/field_salient_leaf.json`` (``--out``)::

    {"bsf_11.jpg": {"polygon": [[x, y], ...], "ambiguous": false}, ...}

        Vertices are normalised to [0, 1] by the cached image size and simplified with ``cv2.approxPolyDP`` to at
        most 60 vertices. ``tools/export_py.py`` embeds the file as the constant ``FIELD_ANNOTATIONS``.

Per image the tool requires exactly one polygon labelled ``leaf`` and nothing else. The flag ``ambiguous`` (labelme
image flag) is optional. Missing files, extra files, wrong shapes and images annotated at a different size are all
reported together; nothing is written unless every one of the 30 images is fine.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_ROOT = REPO_ROOT / "Dhan-Shomadhan"
DEFAULT_LABELME_DIR = REPO_ROOT / "annotations" / "labelme"
DEFAULT_OUT = REPO_ROOT / "annotations" / "field_salient_leaf.json"

LABEL = "leaf"
AMBIGUOUS_FLAG = "ambiguous"
MAX_VERTICES = 60
# approxPolyDP tolerances (pixels of the 1280 px cached image), tried in order until the polygon fits.
EPSILONS = (0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0, 32.0, 48.0, 64.0)
DECIMALS = 5


class ConversionError(Exception):
    """One or more problems, already formatted as a bullet list."""


def load_selection(path: Path) -> list[dict]:
    if not path.is_file():
        raise ConversionError(f"{path} does not exist; run `python group3-starvenus.py prepare` first")
    return json.loads(path.read_text(encoding="utf-8"))["images"]


def simplify_polygon(points: np.ndarray, max_vertices: int = MAX_VERTICES) -> np.ndarray:
    """``points`` (N, 2) in pixels -> at most ``max_vertices`` vertices. The smallest tolerance of EPSILONS that
    fits is used, so a polygon that is already small is only cleaned (collinear and duplicate points removed)."""
    contour = points.astype(np.float32).reshape(-1, 1, 2)
    for epsilon in EPSILONS:
        approx = cv2.approxPolyDP(contour, epsilon, True).reshape(-1, 2)
        if len(approx) <= max_vertices:
            return approx.astype(np.float64)
    raise ConversionError(f"cannot simplify a polygon with {len(points)} vertices to {max_vertices}")


def polygon_area(points: np.ndarray) -> float:
    x, y = points[:, 0], points[:, 1]
    return float(abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2.0)


def convert_one(entry: dict, labelme: dict) -> tuple[dict, list[str]]:
    """(annotation, problems) for one selected image and its parsed labelme file."""
    problems: list[str] = []
    width, height = entry.get("width"), entry.get("height")
    if (labelme.get("imageWidth"), labelme.get("imageHeight")) != (width, height):
        problems.append(
            f"image size {labelme.get('imageWidth')}x{labelme.get('imageHeight')} differs from the cached image "
            f"{width}x{height}: annotate the files in Dhan-Shomadhan/_work/annotations/images/, not the originals"
        )
    shapes = labelme.get("shapes", [])
    polygons = [s for s in shapes if s.get("label") == LABEL and s.get("shape_type") == "polygon"]
    others = [s for s in shapes if s not in polygons]
    if len(polygons) != 1:
        problems.append(f"expected exactly one polygon labelled '{LABEL}', found {len(polygons)}")
    if others:
        described = ", ".join(f"{s.get('shape_type')} '{s.get('label')}'" for s in others)
        problems.append(f"unexpected extra shapes: {described}")
    if problems or not width or not height:
        return {}, problems
    points = np.asarray(polygons[0]["points"], dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) < 3:
        return {}, ["the polygon has fewer than 3 vertices"]
    simple = simplify_polygon(points)
    if len(simple) < 3 or polygon_area(simple) <= 0:
        return {}, ["the polygon has no area after simplification"]
    normalised = np.clip(simple / (width, height), 0.0, 1.0)
    flags = labelme.get("flags") or {}
    return {
        "polygon": [[round(float(x), DECIMALS), round(float(y), DECIMALS)] for x, y in normalised],
        "ambiguous": bool(flags.get(AMBIGUOUS_FLAG, False)),
    }, []


def convert(labelme_dir: Path, selection: list[dict]) -> tuple[dict, list[str], dict]:
    """(annotations, problems, report). ``annotations`` is only complete when ``problems`` is empty."""
    wanted = {entry["filename"]: entry for entry in selection}
    files = {p.stem: p for p in sorted(labelme_dir.glob("*.json"))} if labelme_dir.is_dir() else {}
    stems = {Path(name).stem: name for name in wanted}
    problems: list[str] = []
    annotations: dict = {}
    report = {"vertices_before": {}, "vertices_after": {}}
    missing = [name for stem, name in stems.items() if stem not in files]
    extra = [stem for stem in files if stem not in stems]
    if not labelme_dir.is_dir():
        problems.append(f"labelme folder {labelme_dir} does not exist")
    if missing:
        problems.append(f"{len(missing)} selected images have no labelme file: {', '.join(sorted(missing))}")
    if extra:
        problems.append(f"{len(extra)} labelme files are not in the selection: {', '.join(sorted(extra))}")
    for stem, name in sorted(stems.items(), key=lambda kv: kv[1]):
        if stem not in files:
            continue
        try:
            labelme = json.loads(files[stem].read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            problems.append(f"{files[stem].name}: cannot read: {exc}")
            continue
        annotation, issues = convert_one(wanted[name], labelme)
        problems.extend(f"{files[stem].name}: {issue}" for issue in issues)
        if not issues:
            annotations[name] = annotation
            polygons = [s for s in labelme["shapes"] if s.get("label") == LABEL]
            report["vertices_before"][name] = len(polygons[0]["points"])
            report["vertices_after"][name] = len(annotation["polygon"])
    return annotations, problems, report


def write_annotations(path: Path, annotations: dict) -> None:
    """One image per line: small, readable diffs."""
    names = sorted(annotations)
    lines = ",\n".join(f" {json.dumps(name)}: {json.dumps(annotations[name])}" for name in names)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{\n" + lines + "\n}\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--labelme-dir", type=Path, default=DEFAULT_LABELME_DIR, help=f"default: {DEFAULT_LABELME_DIR.relative_to(REPO_ROOT)}")
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT, help="folder that holds _work/annotations/selection.json")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help=f"default: {DEFAULT_OUT.relative_to(REPO_ROOT)}")
    args = parser.parse_args(argv)
    try:
        selection = load_selection(args.data_root / "_work" / "annotations" / "selection.json")
    except ConversionError as exc:
        print(f"labelme_to_annotations: error: {exc}", file=sys.stderr)
        return 1
    annotations, problems, report = convert(args.labelme_dir, selection)
    n_files = len(list(args.labelme_dir.glob("*.json"))) if args.labelme_dir.is_dir() else 0
    print(f"labelme_to_annotations: {n_files} labelme files in {args.labelme_dir}, {len(selection)} images selected, "
          f"{len(annotations)} converted")
    for name, after in report["vertices_after"].items():
        print(f"  {name:<12} polygons 1  vertices {report['vertices_before'][name]:>3} -> {after:>2}"
              f"{'  ambiguous' if annotations[name]['ambiguous'] else ''}")
    if problems:
        print("problems (nothing was written):", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    write_annotations(args.out, annotations)
    ambiguous = sum(a["ambiguous"] for a in annotations.values())
    print(f"labelme_to_annotations: wrote {args.out} ({len(annotations)} images, {ambiguous} ambiguous)")
    print("next: python tools/export_py.py && python group3-starvenus.py prepare   (embeds the polygons and draws "
          "_work/figures/annotations_overview.png)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
