#!/usr/bin/env python3
"""Export notebook cells tagged ``#| export`` into the single submission file.

Usage (from the repo root)::

    python tools/export_py.py

What it does:

1. Reads ``notebooks/[0-9][0-9]_*.ipynb`` in sorted order. ``00_*`` (exploration)
   and anything not matching the pattern (e.g. ``runner.ipynb``) are skipped.
2. Collects every code cell whose first line is exactly ``#| export`` (the marker
   line itself is dropped) and concatenates them, with a comment header per notebook.
3. Prepends a module docstring and appends ``if __name__ == "__main__": main()``.
4. Embeds the JSON files listed in ``EMBEDDED_FILES`` (``annotations/*.json``) as Python
   constants before the notebook code, because the submission is the single ``.py``.
5. Validates the result and refuses to write anything if a check fails:
   - cells contain no notebook-only syntax (``!cmd``, ``%magic``, ``display(...)``),
   - every import is stdlib or one of ``ALLOWED_THIRD_PARTY`` (the import guard),
   - the module defines a top-level ``main`` function,
   - the whole module byte-compiles.

The output is deterministic (no timestamps), so ``git diff`` on the generated
file shows exactly what changed. This borrows the idea from nbdev without the
dependency. Stdlib only, on purpose: the tool must run anywhere.
"""

from __future__ import annotations

import argparse
import ast
import json
import py_compile
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

# Single source of truth for the deliverable name: `<GROUP_NAME>.py` at the repo root.
GROUP_NAME = "group3-starvenus"
PROJECT_TITLE = "CSCI935 rice leaf disease classification (white vs field background)"

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = REPO_ROOT / "notebooks"

EXPORT_MARKER = "#| export"
# Notebook file names that are exported: two digits, underscore, anything. `00_*` is skipped.
NOTEBOOK_GLOB = "[0-9][0-9]_*.ipynb"
SKIPPED_PREFIXES = ("00_",)

# Spec: imports in the submitted file are restricted to the stdlib plus these packages.
ALLOWED_THIRD_PARTY = frozenset(
    {"numpy", "matplotlib", "cv2", "sklearn", "skimage", "torch", "torchvision"}
)
# Names that only exist inside Jupyter. Calling them in exported code is an error.
NOTEBOOK_ONLY_CALLS = frozenset({"display", "get_ipython"})

_NEAR_MISS_MARKER = re.compile(r"^#\s*\|\s*export", re.IGNORECASE)


class ExportError(Exception):
    """A validation failure. The message already names the notebook and cell."""


@dataclass(frozen=True)
class Section:
    """One chunk of source destined for the output file.

    ``origin`` is used in error messages, e.g. ``"20_classifier.ipynb, cell 3"``.
    """

    origin: str
    source: str


@dataclass(frozen=True)
class NotebookExport:
    name: str
    sections: list[Section]


@dataclass(frozen=True)
class EmbeddedFile:
    """A JSON data file that is embedded in the generated module as a Python constant.

    ``path`` is relative to the repo root. A ``required`` file that is missing is an error;
    an optional one is skipped (its phase has not produced the file yet).
    """

    path: str
    constant: str
    required: bool = True


# The data files that ship inside the single .py (the marker only receives the .py and the PDF).
# To embed another file, add a row here and read the constant in a notebook cell.
EMBEDDED_FILES = (
    EmbeddedFile("annotations/duplicate_groups.json", "DUPLICATE_GROUPS"),
    # Phase 05 (T5.1): the reviewed white pseudo-mask rejects; they decide which leaves Method A pastes.
    EmbeddedFile("annotations/white_rejects.json", "WHITE_REJECTS"),
    # Phase 06 (T6.1): hand-annotated salient-leaf polygons. Skipped until the file exists.
    EmbeddedFile("annotations/field_salient_leaf.json", "FIELD_ANNOTATIONS", required=False),
)

LITERAL_WIDTH = 100  # soft line-length limit of embedded literals


def _scalar_literal(value) -> str:
    if isinstance(value, str):
        return json.dumps(value)  # double quotes; ASCII escapes are valid Python too
    if value is None or isinstance(value, (bool, int, float)):
        return repr(value)
    raise ExportError(f"cannot embed value of type {type(value).__name__}")


def _is_numeric(value) -> bool:
    """A number, or a (nested) list of numbers: such lists are packed several entries per line."""
    if isinstance(value, list):
        return all(_is_numeric(v) for v in value)
    return not isinstance(value, (str, dict))


def format_literal(value, indent: int = 0, width: int = LITERAL_WIDTH) -> str:
    """Render JSON-compatible data as a readable, deterministic Python literal.

    A container is written on one line when it fits in ``width`` columns, otherwise one entry per
    line (lists of numbers, e.g. polygon vertices, are packed several per line). Starts at column
    ``indent`` of the first line; continuation lines are indented relative to ``indent``.
    """
    if not isinstance(value, (list, dict)):
        return _scalar_literal(value)
    pad = " " * (indent + 4)
    if isinstance(value, list):
        items = [format_literal(v, indent + 4, width) for v in value]
        open_, close = "[", "]"
    else:
        if not all(isinstance(k, str) for k in value):
            raise ExportError("cannot embed an object with non-string keys")
        items = [f"{_scalar_literal(k)}: {format_literal(v, indent + 4, width)}" for k, v in value.items()]
        open_, close = "{", "}"
    one_line = open_ + ", ".join(items) + close
    if "\n" not in one_line and indent + len(one_line) <= width:
        return one_line
    if isinstance(value, list) and all(_is_numeric(v) for v in value):
        lines, current = [], ""
        for item in items:
            piece = item + ","
            if current and len(pad) + len(current) + 1 + len(piece) > width:
                lines.append(pad + current)
                current = piece
            else:
                current = f"{current} {piece}" if current else piece
        lines.append(pad + current)
        return open_ + "\n" + "\n".join(lines) + "\n" + " " * indent + close
    body = "".join(f"{pad}{item},\n" for item in items)
    return open_ + "\n" + body + " " * indent + close


def embedded_sections(repo_root: Path, files: tuple[EmbeddedFile, ...] = EMBEDDED_FILES) -> list[Section]:
    """Python source for every embedded data file, to be placed before the notebook code.

    Each file becomes ``CONSTANT = <literal>`` preceded by a comment naming the source file. The
    sections go through the same guards (imports, syntax, compile) as notebook cells. A missing
    required file is an ``ExportError``; a missing optional file is skipped.
    """
    sections = []
    for spec in files:
        path = repo_root / spec.path
        if not path.is_file():
            if spec.required:
                raise ExportError(f"embedded data file {spec.path} is missing (needed for {spec.constant})")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ExportError(f"{spec.path}: cannot read JSON: {exc}") from exc
        source = (
            f"# Embedded from {spec.path} by tools/export_py.py. Edit that file, not this block.\n"
            f"{spec.constant} = {format_literal(data)}\n"
        )
        sections.append(Section(f"embedded:{spec.path}", source))
    return sections


# ---------------------------------------------------------------------------
# Reading notebooks
# ---------------------------------------------------------------------------


def find_notebooks(notebooks_dir: Path) -> list[Path]:
    paths = sorted(notebooks_dir.glob(NOTEBOOK_GLOB))
    return [p for p in paths if not p.name.startswith(SKIPPED_PREFIXES)]


def _cell_source(cell: dict) -> str:
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else src


def _describe(source: str) -> str:
    first = next((ln.strip() for ln in source.splitlines() if ln.strip()), "")
    first = first if len(first) <= 50 else first[:47] + "..."
    return f"starts with {first!r}"


def read_notebook(path: Path) -> NotebookExport:
    try:
        nb = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExportError(f"{path.name}: cannot read notebook: {exc}") from exc
    if nb.get("nbformat") != 4:
        raise ExportError(f"{path.name}: expected nbformat 4, got {nb.get('nbformat')!r}")

    sections: list[Section] = []
    for index, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        source = _cell_source(cell)
        lines = source.splitlines()
        first = lines[0] if lines else ""
        if first.rstrip() != EXPORT_MARKER:
            if _NEAR_MISS_MARKER.match(first.strip()):
                raise ExportError(
                    f"{path.name}, cell {index}: first line {first!r} looks like an export "
                    f"marker but is not exactly {EXPORT_MARKER!r}; the cell would be "
                    "silently skipped"
                )
            continue
        body = "\n".join(lines[1:]).strip("\n")
        if body.strip():
            sections.append(Section(f"{path.name}, cell {index} ({_describe(body)})", body))
    return NotebookExport(path.name, sections)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def parse_section(section: Section) -> ast.Module:
    """Parse one cell, turning notebook-only syntax into a clear error."""
    try:
        return ast.parse(section.source)
    except SyntaxError as exc:
        text = (exc.text or "").lstrip()
        if text.startswith(("!", "%")):
            raise ExportError(
                f"{section.origin}: notebook-only syntax on line {exc.lineno}: {text.rstrip()!r} "
                "(shell commands and magics cannot be exported)"
            ) from exc
        raise ExportError(
            f"{section.origin}: syntax error on line {exc.lineno}: {exc.msg}"
        ) from exc


def check_notebook_only_calls(tree: ast.Module, section: Section) -> None:
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in NOTEBOOK_ONLY_CALLS
        ):
            raise ExportError(
                f"{section.origin}: notebook-only call {node.func.id}(...) on line "
                f"{node.lineno}; remove it from exported cells"
            )


def top_level_package(module: str) -> str:
    return module.split(".", 1)[0]


def check_imports(tree: ast.Module, section: Section) -> None:
    """Import guard: only stdlib and ALLOWED_THIRD_PARTY may be imported."""
    allowed = ", ".join(sorted(ALLOWED_THIRD_PARTY))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                raise ExportError(
                    f"{section.origin}: relative import on line {node.lineno}; the exported "
                    "file is a single module, use absolute imports"
                )
            modules = [node.module or ""]
        else:
            continue
        for module in modules:
            top = top_level_package(module)
            if top in sys.stdlib_module_names or top in ALLOWED_THIRD_PARTY:
                continue
            raise ExportError(
                f"{section.origin}: import of {top!r} (line {node.lineno}) is not allowed in "
                f"exported code. Allowed: the standard library plus {allowed}"
            )


def validate_section(section: Section) -> None:
    tree = parse_section(section)
    check_notebook_only_calls(tree, section)
    check_imports(tree, section)


def docstring(group_name: str = GROUP_NAME) -> str:
    return (
        f'"""{PROJECT_TITLE}\n'
        f"\n"
        f"Group: {group_name}\n"
        f"\n"
        f"GENERATED FILE - DO NOT EDIT. It is built from the notebooks in notebooks/ by\n"
        f"tools/export_py.py. Edit the notebooks and re-run the export instead.\n"
        f"\n"
        f"Run `python {group_name}.py --help` to list the commands.\n"
        f'"""\n'
    )


def build_module(
    exports: list[NotebookExport],
    embedded: list[Section] | None = None,
    group_name: str = GROUP_NAME,
) -> str:
    """Validate every section and assemble the module text."""
    embedded = embedded or []
    for section in embedded:
        validate_section(section)
    for export in exports:
        for section in export.sections:
            validate_section(section)

    parts = [docstring(group_name)]
    for section in embedded:
        parts.append(f"# ---- {section.origin} ----\n{section.source}\n")
    for export in exports:
        if not export.sections:
            continue
        parts.append(f"# ---- from {export.name} ----")
        parts.extend(section.source + "\n" for section in export.sections)
    parts.append('if __name__ == "__main__":\n    main()\n')
    text = "\n".join(parts)

    check_module(text)
    return text


def check_module(text: str) -> None:
    """Whole-file checks: parses, defines main(), byte-compiles."""
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:  # pragma: no cover - sections are parsed individually
        raise ExportError(f"generated module does not parse: {exc}") from exc
    if not any(isinstance(n, ast.FunctionDef) and n.name == "main" for n in tree.body):
        raise ExportError(
            "generated module defines no top-level main(); 90_cli.ipynb must export it"
        )
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "module.py"
        source.write_text(text, encoding="utf-8")
        try:
            py_compile.compile(str(source), cfile=str(Path(tmp) / "module.pyc"), doraise=True)
        except py_compile.PyCompileError as exc:
            raise ExportError(f"py_compile failed: {exc.msg}") from exc


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


def export(
    notebooks_dir: Path = NOTEBOOKS_DIR,
    out_path: Path | None = None,
    group_name: str = GROUP_NAME,
    repo_root: Path = REPO_ROOT,
    embedded_files: tuple[EmbeddedFile, ...] = EMBEDDED_FILES,
) -> Path:
    """Build the module and write it. Nothing is written if any check fails."""
    out_path = out_path or repo_root / f"{group_name}.py"
    notebooks = find_notebooks(notebooks_dir)
    if not notebooks:
        raise ExportError(f"no notebooks matching {NOTEBOOK_GLOB} in {notebooks_dir}")
    exports = [read_notebook(p) for p in notebooks]
    text = build_module(exports, embedded_sections(repo_root, embedded_files), group_name)
    out_path.write_text(text, encoding="utf-8")
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--notebooks-dir", type=Path, default=NOTEBOOKS_DIR)
    parser.add_argument("--out", type=Path, default=None, help=f"default: <repo>/{GROUP_NAME}.py")
    args = parser.parse_args(argv)
    try:
        out = export(args.notebooks_dir, args.out)
    except ExportError as exc:
        print(f"export_py: error: {exc}", file=sys.stderr)
        return 1
    count = len(find_notebooks(args.notebooks_dir))
    print(f"export_py: wrote {out} from {count} notebooks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
