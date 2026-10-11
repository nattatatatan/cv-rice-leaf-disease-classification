"""CSCI935 rice leaf disease classification (white vs field background)

Group: group3-starvenus

GENERATED FILE - DO NOT EDIT. It is built from the notebooks in notebooks/ by
tools/export_py.py. Edit the notebooks and re-run the export instead.

Run `python group3-starvenus.py --help` to list the commands.
"""

# ---- from 10_data.ipynb ----
# Phase 02 (data): dataset index, EXIF IO, cache, splits and audits are added here.

# ---- from 20_classifier.ipynb ----
# Phase 03 (classifier): datasets, transforms, models and the train/eval loop are added here.

# ---- from 30_copy_paste.ipynb ----
# Phase 05 (copy-paste): pseudo-masks and composites are added here.

# ---- from 40_segmentation.ipynb ----
# Phase 06 (segmentation): the segmenter and the crop pipeline are added here.

# ---- from 50_analysis.ipynb ----
# Phase 07 (analysis): aggregation, tables, figures and Grad-CAM are added here.

# ---- from 90_cli.ipynb ----
import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

DEFAULT_DATA_ROOT = "Dhan-Shomadhan"
DEVICE_CHOICES = ("auto", "cuda", "mps", "cpu")
DEFAULT_SPLITS = (0, 1, 2, 3, 4)
IMAGE_SUFFIXES = frozenset({".jpg", ".jpeg"})
WORK_DIRNAME = "_work"  # everything the code generates lives in <data_root>/_work/

EXIT_OK = 0
EXIT_FAILURE = 1
EXIT_NOT_IMPLEMENTED = 3

def find_images(data_root: Path) -> list[Path]:
    """All JPEGs under data_root (recursive, case-insensitive), skipping the generated _work/ folder."""
    found = []
    for dirpath, dirnames, filenames in data_root.walk():
        if dirpath == data_root and WORK_DIRNAME in dirnames:
            dirnames.remove(WORK_DIRNAME)
        for filename in filenames:
            if Path(filename).suffix.lower() in IMAGE_SUFFIXES:
                found.append(dirpath / filename)
    return sorted(found)


def resolve_device(requested: str = "auto") -> str:
    """Map the --device flag to a concrete torch device name; raise if it is unavailable."""
    import torch

    available = {
        "cuda": torch.cuda.is_available(),
        "mps": torch.backends.mps.is_available(),
        "cpu": True,
    }
    if requested == "auto":
        return next(name for name in ("cuda", "mps", "cpu") if available[name])
    if not available.get(requested, False):
        raise RuntimeError(f"device {requested!r} was requested but is not available here")
    return requested

def cmd_smoke(args: argparse.Namespace) -> int:
    """Phase 01 smoke check: data root, image discovery, library imports, device.

    Later phases extend this into the full tiny end-to-end run (20 images, 1 epoch, CPU).
    """
    data_root = Path(args.data_root)
    print(f"smoke: data root = {data_root.resolve()}")
    if not data_root.is_dir():
        print(f"smoke: FAIL - data root {data_root} is not a directory (see --data-root)", file=sys.stderr)
        return EXIT_FAILURE
    images = find_images(data_root)
    if not images:
        print(f"smoke: FAIL - no JPEG images found under {data_root}", file=sys.stderr)
        return EXIT_FAILURE
    print(f"smoke: OK - found {len(images)} JPEG images (excluding {WORK_DIRNAME}/)")

    import cv2
    import matplotlib
    import numpy
    import skimage
    import sklearn
    import torch
    import torchvision

    print(f"smoke: python {sys.version.split()[0]}")
    for module in (numpy, matplotlib, cv2, sklearn, skimage, torch, torchvision):
        print(f"smoke: {module.__name__} {module.__version__}")
    device = resolve_device(args.device)
    print(f"smoke: OK - device = {device} (requested: {args.device}), fast = {args.fast}")
    print("smoke: PASSED")
    return EXIT_OK


def not_implemented(command: str, phase: str) -> Callable[[argparse.Namespace], int]:
    """Placeholder handler: say which phase will provide the command and exit non-zero."""

    def handler(args: argparse.Namespace) -> int:
        print(f"{command}: not implemented yet (phase {phase})", file=sys.stderr)
        return EXIT_NOT_IMPLEMENTED

    return handler

def parse_splits(text: str) -> tuple[int, ...]:
    """Parse '0,1,2' into (0, 1, 2); duplicates are dropped, order is kept."""
    try:
        values = [int(part) for part in text.split(",") if part.strip() != ""]
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected comma-separated integers, got {text!r}") from None
    if not values or min(values) < 0:
        raise argparse.ArgumentTypeError(f"expected one or more non-negative integers, got {text!r}")
    return tuple(dict.fromkeys(values))


def add_global_flags(parser: argparse.ArgumentParser, *, is_subcommand: bool) -> None:
    """Add the global flags. On subparsers the defaults are suppressed so that a flag given
    before the command is not overwritten by the subparser's default."""

    def default(value):
        return argparse.SUPPRESS if is_subcommand else value

    group = parser.add_argument_group("global flags (accepted before or after the command)")
    group.add_argument(
        "--data-root",
        type=Path,
        default=default(Path(DEFAULT_DATA_ROOT)),
        help=f"dataset folder, relative to the working directory (default: {DEFAULT_DATA_ROOT})",
    )
    group.add_argument(
        "--device",
        choices=DEVICE_CHOICES,
        default=default("auto"),
        help="compute device (default: auto = cuda, then mps, then cpu)",
    )
    group.add_argument(
        "--seed-offset",
        type=int,
        default=default(0),
        help="added to every seed, for repeating an experiment with different randomness (default: 0)",
    )
    group.add_argument(
        "--fast",
        action="store_true",
        default=default(False),
        help="smoke settings: tiny subsets, 1 epoch",
    )


def _configure_run(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--exp", required=True, metavar="ID", help="experiment ID, e.g. E1-U")
    parser.add_argument(
        "--splits",
        type=parse_splits,
        default=DEFAULT_SPLITS,
        metavar="LIST",
        help="comma-separated split seeds (default: 0,1,2,3,4)",
    )


def _configure_gradcam(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--exp", required=True, metavar="ID", help="experiment ID")
    parser.add_argument("--split", type=int, required=True, metavar="K", help="split seed")


def _configure_predict(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--exp", default=None, metavar="ID", help="experiment ID (default: the recommended one)")
    parser.add_argument("--split", type=int, default=0, metavar="K", help="split seed (default: 0)")
    parser.add_argument("--image", type=Path, required=True, metavar="PATH", help="image to classify")


@dataclass(frozen=True)
class Command:
    name: str
    help: str
    handler: Callable[[argparse.Namespace], int]
    configure: Callable[[argparse.ArgumentParser], None] | None = None


COMMANDS = (
    Command(
        "download-weights",
        "fetch the torchvision pretrained weights into <data-root>/_work/weights/",
        not_implemented("download-weights", "03"),
    ),
    Command(
        "prepare",
        "index, cache, splits, audits, pseudo-masks (idempotent)",
        not_implemented("prepare", "02"),
    ),
    Command("run", "train and evaluate one experiment over the given splits", not_implemented("run", "03"), _configure_run),
    Command(
        "summarize",
        "aggregate all runs into tables and figures",
        not_implemented("summarize", "07"),
    ),
    Command("gradcam", "Grad-CAM figures for one experiment and split", not_implemented("gradcam", "07"), _configure_gradcam),
    Command("predict", "classify a single image and print class probabilities", not_implemented("predict", "03"), _configure_predict),
    Command("smoke", "tiny end-to-end check (currently: data root, imports, device)", cmd_smoke),
    Command(
        "reproduce",
        "download-weights, prepare, every reported experiment, summarize",
        not_implemented("reproduce", "08"),
    ),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=Path(__file__).name,
        description="CSCI935 rice leaf disease classification - reproduces every reported number.",
        epilog="Global flags may be placed before or after the command.",
    )
    add_global_flags(parser, is_subcommand=False)
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    for command in COMMANDS:
        sub = subparsers.add_parser(command.name, help=command.help, description=command.help)
        if command.configure is not None:
            command.configure(sub)
        add_global_flags(sub, is_subcommand=True)
        sub.set_defaults(handler=command.handler)
    return parser

def run_cli(argv: list[str] | None = None) -> int:
    """Parse argv and run the chosen command. Returns the process exit code."""
    args = build_parser().parse_args(argv)
    return args.handler(args)


def main() -> None:
    sys.exit(run_cli())

if __name__ == "__main__":
    main()
