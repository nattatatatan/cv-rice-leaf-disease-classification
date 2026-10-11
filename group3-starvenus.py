"""CSCI935 rice leaf disease classification (white vs field background)

Group: group3-starvenus

GENERATED FILE - DO NOT EDIT. It is built from the notebooks in notebooks/ by
tools/export_py.py. Edit the notebooks and re-run the export instead.

Run `python group3-starvenus.py --help` to list the commands.
"""

# ---- from 10_data.ipynb ----
import csv
import hashlib
import json
import multiprocessing
import os
import struct
import sys
import tempfile
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import cv2
import numpy as np

IMAGE_SUFFIXES = frozenset({".jpg", ".jpeg"})
WORK_DIRNAME = "_work"  # everything the code generates lives in <data_root>/_work/

# Fixed class order, used in every confusion matrix, table and figure.
CLASS_NAMES = ("Brown Spot", "Leaf Scald", "Rice Blast", "Rice Tungro", "Sheath Blight")
DOMAINS = ("white", "field")

# (filename prefix, class, domain, exact string in the CSV `Diseases` column)
LABEL_TABLE = (
    ("bs_wb_", "Brown Spot", "white", "Brown Spot(white Background)"),
    ("ls_wb_", "Leaf Scald", "white", "Leaf Scaled(white Background)"),
    ("rb_wb_", "Rice Blast", "white", "Rice Blast(white Background)"),
    ("rt_wb_", "Rice Tungro", "white", "Rice Tungro(white Background)"),
    ("sb_wb_", "Sheath Blight", "white", "Shath Blight(white Background)"),
    ("bsf_", "Brown Spot", "field", "Browon Spot(Feild Background)"),
    ("lsf_", "Leaf Scald", "field", "Leaf Scaled(Feild Background)"),
    ("rbf_", "Rice Blast", "field", "Rice Blast(Feild Background)"),
    ("rtf_", "Rice Tungro", "field", "Rice Turgro(Feild Background)"),
    ("sbf_", "Sheath Blight", "field", "Sheath Blight(Feild Background)"),
)
# Longest prefix first, so that a prefix that extends another one always wins.
PREFIXES_LONGEST_FIRST = tuple(sorted(LABEL_TABLE, key=lambda row: -len(row[0])))
CSV_LABELS = {csv_label: (cls, domain) for _, cls, domain, csv_label in LABEL_TABLE}

# Image counts per (class, domain) established by the audit. A different dataset must fail loudly.
EXPECTED_COUNTS = {
    ("Brown Spot", "white"): 90,
    ("Leaf Scald", "white"): 143,
    ("Rice Blast", "white"): 198,
    ("Rice Tungro", "white"): 119,
    ("Sheath Blight", "white"): 219,
    ("Brown Spot", "field"): 49,
    ("Leaf Scald", "field"): 74,
    ("Rice Blast", "field"): 74,
    ("Rice Tungro", "field"): 76,
    ("Sheath Blight", "field"): 64,
}
EXPECTED_TOTAL = sum(EXPECTED_COUNTS.values())  # 1106

CSV_FILENAME = "Dhan-Shomadhan_picture_Information.csv"


class DatasetError(Exception):
    """The dataset on disk is not what the code expects. The message names the offending path."""


def warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)


def extended_path(absolute_path: str, windows: bool) -> str:
    """Windows silently strips trailing spaces from path components (the dataset has folders called
    'Field Background  '). The extended-length prefix switches that off. No-op elsewhere."""
    if not windows or absolute_path.startswith("\\\\?\\"):
        return absolute_path
    if absolute_path.startswith("\\\\"):  # UNC share: \\server\share -> \\?\UNC\server\share
        return "\\\\?\\UNC\\" + absolute_path[2:]
    return "\\\\?\\" + absolute_path


def fs_path(path) -> str:
    """The string to hand to open()/os functions for ``path`` (absolute, Windows-safe)."""
    return extended_path(os.path.abspath(os.fspath(path)), os.name == "nt")


def read_file_bytes(path) -> bytes:
    with open(fs_path(path), "rb") as handle:
        return handle.read()


def write_bytes_atomic(path: Path, data: bytes) -> None:
    """Write via a temp file and rename, so an interrupted run never leaves a truncated file."""
    path = Path(path)
    os.makedirs(fs_path(path.parent), exist_ok=True)
    tmp = path.with_name(path.name + f".tmp{os.getpid()}")
    with open(fs_path(tmp), "wb") as handle:
        handle.write(data)
    os.replace(fs_path(tmp), fs_path(path))


def write_text_atomic(path: Path, text: str) -> None:
    write_bytes_atomic(path, text.encode("utf-8"))  # bytes: identical files on every OS (no CRLF)


def find_images(data_root: Path) -> list[Path]:
    """All JPEGs under data_root (recursive, case-insensitive), skipping the generated _work/ folder."""
    found = []
    for dirpath, dirnames, filenames in Path(data_root).walk():
        if dirpath == Path(data_root) and WORK_DIRNAME in dirnames:
            dirnames.remove(WORK_DIRNAME)
        for filename in filenames:
            if Path(filename).suffix.lower() in IMAGE_SUFFIXES:
                found.append(dirpath / filename)
    return sorted(found)


def classify_filename(filename: str) -> tuple[str, str]:
    """(class, domain) from the filename prefix; longest prefix wins. Raises DatasetError."""
    lowered = filename.lower()
    for prefix, cls, domain, _ in PREFIXES_LONGEST_FIRST:
        if lowered.startswith(prefix):
            return cls, domain
    known = ", ".join(row[0] for row in LABEL_TABLE)
    raise DatasetError(f"{filename}: filename matches no known prefix ({known})")

def _tiff_orientation(tiff: bytes) -> int:
    """Orientation (1..8) from the TIFF block of an EXIF segment; 1 if absent."""
    if len(tiff) < 8 or tiff[:2] not in (b"II", b"MM"):
        return 1
    endian = "<" if tiff[:2] == b"II" else ">"
    if struct.unpack_from(endian + "H", tiff, 2)[0] != 42:
        return 1
    offset = struct.unpack_from(endian + "I", tiff, 4)[0]
    if offset + 2 > len(tiff):
        return 1
    (count,) = struct.unpack_from(endian + "H", tiff, offset)
    for entry in range(count):
        base = offset + 2 + 12 * entry
        if base + 12 > len(tiff):
            break
        tag, kind, n_values = struct.unpack_from(endian + "HHI", tiff, base)
        if tag == 0x0112 and kind == 3 and n_values == 1:  # SHORT, one value, stored inline
            value = struct.unpack_from(endian + "H", tiff, base + 8)[0]
            return value if 1 <= value <= 8 else 1
    return 1


def parse_exif_orientation(data: bytes) -> int:
    """EXIF orientation (1..8) of a JPEG given its bytes. 1 means upright (also when there is no tag)."""
    if data[:2] != b"\xff\xd8":
        return 1
    pos, end = 2, len(data)
    while pos + 4 <= end:
        if data[pos] != 0xFF:
            break
        marker = data[pos + 1]
        if marker == 0xFF:  # fill byte
            pos += 1
            continue
        if marker == 0x01 or 0xD0 <= marker <= 0xD8:  # markers without a length
            pos += 2
            continue
        if marker in (0xD9, 0xDA):  # end of image / start of scan: no EXIF after this
            break
        (length,) = struct.unpack_from(">H", data, pos + 2)
        if marker == 0xE1 and data[pos + 4 : pos + 10] == b"Exif\x00\x00":
            return _tiff_orientation(data[pos + 10 : pos + 2 + length])
        pos += 2 + length
    return 1

@dataclass(frozen=True)
class Record:
    filename: str  # primary key (unique across the dataset)
    rel_path: str  # path relative to the data root, '/' separated
    cls: str
    cls_idx: int
    domain: str  # "white" or "field"
    exif_orientation: int  # 1..8; 1 = upright or no tag
    sha1: str  # of the file bytes; "" when hashing was skipped (smoke only)

    @property
    def stratum(self) -> tuple[str, str]:
        return (self.cls, self.domain)


def work_dir(data_root) -> Path:
    return Path(data_root) / WORK_DIRNAME


def index_path(data_root) -> Path:
    return work_dir(data_root) / "index.json"


def read_csv_labels(csv_path: Path) -> dict[str, str]:
    """{picture name: Diseases string}. The CSV has an unnamed index column, then `pictureName` and
    `Diseases`; it may start with a UTF-8 BOM."""
    with open(fs_path(csv_path), newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        header = [cell.strip().lower() for cell in next(reader, [])]
        try:
            name_col, label_col = header.index("picturename"), header.index("diseases")
        except ValueError:
            raise DatasetError(f"{csv_path}: expected columns 'pictureName' and 'Diseases', found {header}") from None
        labels = {}
        for row in reader:
            if len(row) <= max(name_col, label_col):
                continue
            labels[row[name_col].strip()] = row[label_col].strip()
    return labels


def find_csv(data_root: Path) -> Path | None:
    path = Path(data_root) / CSV_FILENAME
    if path.is_file():
        return path
    others = sorted(Path(data_root).glob("*.csv"))
    return others[0] if len(others) == 1 else None


def check_against_csv(records: list[Record], csv_path: Path, *, require_complete: bool) -> None:
    csv_labels = read_csv_labels(csv_path)
    for record in records:
        if record.filename not in csv_labels:
            raise DatasetError(f"{record.rel_path}: not listed in {csv_path.name}")
        csv_string = csv_labels[record.filename]
        if csv_string not in CSV_LABELS:
            raise DatasetError(f"{csv_path.name}: unknown Diseases string {csv_string!r} for {record.filename}")
        if CSV_LABELS[csv_string] != (record.cls, record.domain):
            raise DatasetError(
                f"{record.rel_path}: filename prefix says {(record.cls, record.domain)} "
                f"but {csv_path.name} says {CSV_LABELS[csv_string]} ({csv_string!r})"
            )
    if require_complete:
        missing = sorted(set(csv_labels) - {r.filename for r in records})
        if missing:
            raise DatasetError(f"{csv_path.name} lists {len(missing)} images that are not on disk, e.g. {missing[:3]}")


def check_expected_counts(records: list[Record], expected: dict[tuple[str, str], int]) -> None:
    actual = Counter(r.stratum for r in records)
    problems = [
        f"{key[0]} / {key[1]}: expected {expected.get(key, 0)}, found {actual.get(key, 0)}"
        for key in sorted(set(expected) | set(actual))
        if expected.get(key, 0) != actual.get(key, 0)
    ]
    if len(records) != sum(expected.values()):
        problems.insert(0, f"total: expected {sum(expected.values())}, found {len(records)}")
    if problems:
        raise DatasetError("this is not the expected dataset (counts differ):\n  " + "\n  ".join(problems))


EXIF_HEADER_BYTES = 128 * 1024  # the EXIF segment is at the very start of the file


def build_index(
    data_root,
    *,
    expected_counts: dict[tuple[str, str], int] | None = EXPECTED_COUNTS,
    with_sha1: bool = True,
) -> list[Record]:
    """Index every JPEG under ``data_root`` (see the section text above), sorted by filename.

    ``expected_counts=None`` skips the count assertion and the CSV completeness check. That is only
    for tiny synthetic trees in tests and for the smoke check on a partial tree; every real run
    (`prepare`) uses the default, so a different dataset fails loudly.
    ``with_sha1=False`` reads only the file headers (fast); records then have ``sha1 == ""``.
    """
    data_root = Path(data_root)
    if not data_root.is_dir():
        raise DatasetError(f"data root {data_root} is not a directory (see --data-root)")
    records, seen = [], {}
    for path in find_images(data_root):
        cls, domain = classify_filename(path.name)
        if path.name in seen:
            raise DatasetError(f"duplicate filename {path.name}: {seen[path.name]} and {path}")
        seen[path.name] = path
        with open(fs_path(path), "rb") as handle:
            data = handle.read() if with_sha1 else handle.read(EXIF_HEADER_BYTES)
        records.append(
            Record(
                filename=path.name,
                rel_path=path.relative_to(data_root).as_posix(),
                cls=cls,
                cls_idx=CLASS_NAMES.index(cls),
                domain=domain,
                exif_orientation=parse_exif_orientation(data),
                sha1=hashlib.sha1(data).hexdigest() if with_sha1 else "",
            )
        )
    records.sort(key=lambda r: r.filename)
    csv_path = find_csv(data_root)
    if csv_path is None:
        warn(f"no label CSV found in {data_root}; labels come from filename prefixes only")
    else:
        check_against_csv(records, csv_path, require_complete=expected_counts is not None)
    if expected_counts is not None:
        check_expected_counts(records, expected_counts)
    return records


def write_json(path: Path, obj, *, indent: int | None = 1) -> None:
    write_text_atomic(path, json.dumps(obj, indent=indent, sort_keys=False) + "\n")


def write_index(data_root, records: list[Record]) -> Path:
    path = index_path(data_root)
    rows = ",\n".join("  " + json.dumps(asdict(r)) for r in records)  # one record per line: readable diffs
    write_text_atomic(path, '{\n "format": 1,\n "records": [\n' + rows + "\n ]\n}\n")
    return path


def load_index(data_root) -> list[Record]:
    """The records written by `prepare`, sorted by filename."""
    path = index_path(data_root)
    if not path.is_file():
        raise DatasetError(f"{path} does not exist; run the `prepare` command first")
    payload = json.loads(read_file_bytes(path).decode("utf-8"))
    if payload.get("format") != 1:
        raise DatasetError(f"{path}: unsupported index format {payload.get('format')!r}")
    return [Record(**row) for row in payload["records"]]

def apply_orientation(rgb: np.ndarray, orientation: int) -> np.ndarray:
    """Undo an EXIF orientation tag (same conventions as PIL.ImageOps.exif_transpose)."""
    if orientation == 2:
        return rgb[:, ::-1]
    if orientation == 3:
        return np.rot90(rgb, 2)
    if orientation == 4:
        return rgb[::-1]
    if orientation == 5:  # transpose
        return rgb.transpose(1, 0, 2)
    if orientation == 6:  # stored rotated 90 degrees counter-clockwise: rotate clockwise
        return np.rot90(rgb, -1)
    if orientation == 7:  # transverse
        return np.rot90(rgb.transpose(1, 0, 2), 2)
    if orientation == 8:
        return np.rot90(rgb, 1)
    return rgb


def to_portrait(rgb: np.ndarray) -> tuple[np.ndarray, bool]:
    """Rotate a landscape image 90 degrees clockwise. Returns (image, was_rotated)."""
    if rgb.shape[1] > rgb.shape[0]:
        return np.rot90(rgb, -1), True
    return rgb, False


def decode_oriented(data: bytes, source: str = "<bytes>") -> np.ndarray:
    """JPEG bytes -> (H, W, 3) uint8 RGB with the EXIF orientation applied (not yet portrait)."""
    bgr = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION)
    if bgr is None:
        raise DatasetError(f"{source}: cannot decode image")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return apply_orientation(rgb, parse_exif_orientation(data))


def read_rgb(path) -> np.ndarray:
    """(H, W, 3) uint8 RGB, EXIF applied, always portrait (H >= W). Works for paths that OpenCV's own
    file reader struggles with (non-ASCII, Windows trailing-space folders) because we read the bytes."""
    rgb, _ = to_portrait(decode_oriented(read_file_bytes(path), str(path)))
    return np.ascontiguousarray(rgb)

CACHE_LONG_SIDE = 1280
CACHE_JPEG_QUALITY = 95
MAX_WORKERS = 8


def cache_dir(data_root) -> Path:
    return work_dir(data_root) / "cache"


def manifest_path(data_root) -> Path:
    return cache_dir(data_root) / "manifest.json"


def default_workers() -> int:
    try:
        available = len(os.sched_getaffinity(0))
    except AttributeError:  # macOS, Windows
        available = os.cpu_count() or 1
    return max(1, min(available, MAX_WORKERS))


def pool_is_safe() -> bool:
    """True if worker processes can import the functions we send them: always under `fork`; under
    `spawn` only when this file runs as the main script (children re-run it as `__mp_main__`)."""
    return multiprocessing.get_start_method() == "fork" or __name__ == "__main__"


def _pool_init() -> None:
    cv2.setNumThreads(1)  # one process per core already; avoid oversubscription


def run_parallel(func, tasks, *, workers: int, mp_context=None, chunksize: int = 4):
    """Yield ``func(task)`` for every task, in order. Uses a process pool when that is possible and
    worthwhile, otherwise runs inline. ``func`` must be a picklable top-level function."""
    tasks = list(tasks)
    use_pool = workers > 1 and len(tasks) > 1 and (mp_context is not None or pool_is_safe())
    if not use_pool:
        for task in tasks:
            yield func(task)
        return
    with ProcessPoolExecutor(
        max_workers=min(workers, len(tasks)), mp_context=mp_context, initializer=_pool_init
    ) as executor:
        yield from executor.map(func, tasks, chunksize=chunksize)


def resize_long_side(rgb: np.ndarray, long_side: int) -> np.ndarray:
    height, width = rgb.shape[:2]
    scale = long_side / max(height, width)
    if scale >= 1.0:
        return rgb
    size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return cv2.resize(rgb, size, interpolation=cv2.INTER_AREA)


def encode_jpeg(rgb: np.ndarray, quality: int) -> bytes:
    ok, buffer = cv2.imencode(".jpg", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise DatasetError("JPEG encoding failed")
    return buffer.tobytes()


def _cache_one(task: tuple) -> tuple[str, dict]:
    """Worker: source file -> cached portrait JPEG. Returns (filename, manifest entry without sha1)."""
    filename, source, target, long_side, quality = task
    try:
        rgb, rotated = to_portrait(decode_oriented(read_file_bytes(source), source))
        small = resize_long_side(np.ascontiguousarray(rgb), long_side)
        write_bytes_atomic(Path(target), encode_jpeg(small, quality))
    except Exception as exc:
        raise DatasetError(f"{source}: caching failed: {exc}") from exc
    return filename, {"width": int(small.shape[1]), "height": int(small.shape[0]), "rotated_landscape": bool(rotated)}


@dataclass
class CacheStats:
    total: int
    built: int
    reused: int
    rotated_landscape: int  # images (of `total`) that were landscape after EXIF and were turned to portrait


def load_manifest(data_root) -> dict:
    path = manifest_path(data_root)
    if not path.is_file():
        return {}
    try:
        return json.loads(read_file_bytes(path).decode("utf-8"))
    except (OSError, ValueError):
        return {}  # a damaged manifest only means "rebuild everything"


def write_manifest(data_root, manifest: dict) -> None:
    write_json(manifest_path(data_root), dict(sorted(manifest.items())))


def build_cache(
    data_root,
    records: list[Record],
    *,
    workers: int | None = None,
    mp_context=None,
    long_side: int = CACHE_LONG_SIDE,
    quality: int = CACHE_JPEG_QUALITY,
    log=None,
) -> CacheStats:
    """Cache every record (see section text). Idempotent. ``records`` need their sha1 (not the
    ``with_sha1=False`` kind)."""
    if any(not r.sha1 for r in records):
        raise DatasetError("build_cache needs records with sha1 (build_index(..., with_sha1=True))")
    data_root = Path(data_root)
    root = cache_dir(data_root)
    manifest = load_manifest(data_root)

    def current(record: Record) -> bool:
        entry = manifest.get(record.filename)
        return bool(entry) and entry.get("sha1") == record.sha1 and (root / record.filename).is_file()

    todo = [r for r in records if not current(r)]
    tasks = [(r.filename, str(data_root / r.rel_path), str(root / r.filename), long_side, quality) for r in todo]
    sha_of = {r.filename: r.sha1 for r in todo}
    done = 0
    try:
        for filename, entry in run_parallel(_cache_one, tasks, workers=workers or default_workers()):
            manifest[filename] = {"sha1": sha_of[filename], **entry}
            done += 1
            if log and done % 200 == 0:
                log(f"cache: {done}/{len(tasks)}")
    finally:
        if done:
            write_manifest(data_root, manifest)  # also after an interrupted run: finished images are kept
    rotated = sum(bool(manifest[r.filename]["rotated_landscape"]) for r in records)
    return CacheStats(total=len(records), built=len(todo), reused=len(records) - len(todo), rotated_landscape=rotated)


def read_cached_rgb(data_root, filename: str) -> np.ndarray:
    """A cached image: (H, W, 3) uint8 RGB, portrait, long side <= 1280."""
    return read_rgb(cache_dir(data_root) / filename)

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

EXIT_OK = 0
EXIT_FAILURE = 1
EXIT_NOT_IMPLEMENTED = 3

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
