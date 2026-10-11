"""CSCI935 rice leaf disease classification (white vs field background)

Group: group3-starvenus

GENERATED FILE - DO NOT EDIT. It is built from the notebooks in notebooks/ by
tools/export_py.py. Edit the notebooks and re-run the export instead.

Run `python group3-starvenus.py --help` to list the commands.
"""

# ---- embedded:annotations/duplicate_groups.json ----
# Embedded from annotations/duplicate_groups.json by tools/export_py.py. Edit that file, not this block.
DUPLICATE_GROUPS = [
    ["bs_wb_4.jpg", "bs_wb_5.jpg"],
    ["bs_wb_55.jpg", "bs_wb_56.jpg"],
    ["bs_wb_80.jpg", "bs_wb_81.jpg"],
    ["bsf_0.jpg", "bsf_1.jpg"],
    ["bsf_2.jpg", "bsf_3.jpg"],
    ["bsf_4.jpg", "bsf_5.jpg"],
    ["bsf_7.jpg", "bsf_8.jpg"],
    ["bsf_15.jpg", "bsf_16.jpg"],
    ["ls_wb_1.jpg", "ls_wb_2.jpg"],
    ["ls_wb_85.jpg", "ls_wb_86.jpg"],
    ["ls_wb_99.jpg", "ls_wb_100.jpg"],
    ["lsf_0.jpg", "lsf_1.jpg"],
    ["lsf_6.jpg", "lsf_7.jpg"],
    ["lsf_12.jpg", "lsf_23.jpg"],
    ["lsf_34.jpg", "lsf_45.jpg"],
    ["lsf_67.jpg", "lsf_72.jpg"],
    ["rb_wb_20.jpg", "rb_wb_21.jpg"],
    ["rb_wb_91.jpg", "rb_wb_92.jpg"],
    ["rb_wb_113.jpg", "rb_wb_114.jpg"],
    ["rb_wb_146.jpg", "rb_wb_147.jpg"],
    ["rb_wb_169.jpg", "rb_wb_170.jpg"],
    ["rb_wb_180.jpg", "rb_wb_181.jpg"],
    ["rbf_1.jpg", "rbf_2.jpg"],
    ["rbf_13.jpg", "rbf_14.jpg"],
    ["rbf_21.jpg", "rbf_22.jpg"],
    ["rtf_0.jpg", "rtf_1.jpg"],
    ["rtf_5.jpg", "rtf_6.jpg"],
    ["rtf_7.jpg", "rtf_8.jpg", "rtf_9.jpg", "rtf_10.jpg"],
    ["rtf_11.jpg", "rtf_12.jpg"],
    ["rtf_17.jpg", "rtf_18.jpg", "rtf_19.jpg"],
    ["rtf_20.jpg", "rtf_21.jpg"],
    ["rtf_22.jpg", "rtf_23.jpg"],
    ["rtf_25.jpg", "rtf_26.jpg", "rtf_27.jpg"],
    ["rtf_32.jpg", "rtf_33.jpg"],
    ["sb_wb_210.jpg", "sb_wb_211.jpg"],
    ["sbf_1.jpg", "sbf_19.jpg", "sbf_47.jpg"],
]


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

DHASH_SIZE = (9, 8)  # width, height of the resized gray image -> 8 x 8 = 64 bits


def dhash_bits(rgb: np.ndarray) -> np.ndarray:
    """64 bits (uint8 0/1) of the difference hash of an RGB image."""
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    small = cv2.resize(gray, DHASH_SIZE, interpolation=cv2.INTER_AREA).astype(np.int16)
    return (small[:, 1:] > small[:, :-1]).ravel().astype(np.uint8)


def dhash_hex(bits: np.ndarray) -> str:
    return np.packbits(bits).tobytes().hex()


def hex_to_bits(text: str) -> np.ndarray:
    return np.unpackbits(np.frombuffer(bytes.fromhex(text), dtype=np.uint8))

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
    return filename, {
        "width": int(small.shape[1]),
        "height": int(small.shape[0]),
        "rotated_landscape": bool(rotated),
        "dhash": dhash_hex(dhash_bits(small)),  # of the downsized image, before JPEG encoding
    }


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
    output_root=None,
    log=None,
) -> CacheStats:
    """Cache every record (see section text). Idempotent. ``records`` need their sha1 (not the
    ``with_sha1=False`` kind). Images are read from ``data_root``; the cache is written under
    ``<output_root>/_work/cache`` (default: the same data root; the smoke check uses a temp folder)."""
    if any(not r.sha1 for r in records):
        raise DatasetError("build_cache needs records with sha1 (build_index(..., with_sha1=True))")
    data_root = Path(data_root)
    output_root = Path(output_root) if output_root is not None else data_root
    root = cache_dir(output_root)
    manifest = load_manifest(output_root)

    def current(record: Record) -> bool:
        entry = manifest.get(record.filename)
        return (
            bool(entry)
            and entry.get("sha1") == record.sha1
            and "dhash" in entry
            and (root / record.filename).is_file()
        )

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
            write_manifest(output_root, manifest)  # also after an interrupted run: finished images are kept
    rotated = sum(bool(manifest[r.filename]["rotated_landscape"]) for r in records)
    return CacheStats(total=len(records), built=len(todo), reused=len(records) - len(todo), rotated_landscape=rotated)


def read_cached_rgb(data_root, filename: str) -> np.ndarray:
    """A cached image: (H, W, 3) uint8 RGB, portrait, long side <= 1280."""
    return read_rgb(cache_dir(data_root) / filename)

NEAR_DUPLICATE_MAX_DISTANCE = 6
FEATURE_LONG_SIDE = 1000  # images are downscaled to this long side before SIFT
FEATURE_MAX_KEYPOINTS = 3000
FEATURE_CONTRAST = 0.01  # below OpenCV's 0.04 default: leaves on a plain wall have few strong corners
FEATURE_RATIO = 0.75  # Lowe ratio test
FEATURE_RANSAC_PX = 6.0
SHEET_MAX_PAIRS = 48  # pairs shown on contact sheets (the top of the ranking)
SHEET_PAIRS_PER_PAGE = 8


def hamming_matrix(bits: np.ndarray) -> np.ndarray:
    """All pairwise Hamming distances of an (N, 64) 0/1 matrix, as an (N, N) int matrix."""
    b = bits.astype(np.float32)
    return np.rint(b @ (1.0 - b).T + (1.0 - b) @ b.T).astype(np.int32)


def find_near_duplicates(bits: np.ndarray, max_distance: int = NEAR_DUPLICATE_MAX_DISTANCE) -> list[tuple[int, int, int]]:
    """(i, j, distance) with i < j and distance <= max_distance, sorted by distance then index."""
    dist = hamming_matrix(bits)
    rows, cols = np.nonzero(np.triu(dist <= max_distance, k=1))
    pairs = [(int(i), int(j), int(dist[i, j])) for i, j in zip(rows, cols)]
    return sorted(pairs, key=lambda p: (p[2], p[0], p[1]))


def sift_features(rgb: np.ndarray):
    """(keypoint coordinates (K, 2) float32, descriptors (K, 128) float32) at FEATURE_LONG_SIDE."""
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    scale = FEATURE_LONG_SIDE / max(gray.shape)
    if scale < 1.0:
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    keypoints, descriptors = cv2.SIFT_create(nfeatures=FEATURE_MAX_KEYPOINTS, contrastThreshold=FEATURE_CONTRAST).detectAndCompute(gray, None)
    points = np.float32([k.pt for k in keypoints]).reshape(-1, 2)
    return points, descriptors


def feature_inliers(features_a, features_b) -> int:
    """Number of ratio-test SIFT matches consistent with one similarity transform (RANSAC)."""
    (points_a, desc_a), (points_b, desc_b) = features_a, features_b
    if desc_a is None or desc_b is None or len(desc_a) < 8 or len(desc_b) < 8:
        return 0
    matches = cv2.BFMatcher(cv2.NORM_L2).knnMatch(desc_a, desc_b, k=2)
    good = [m[0] for m in matches if len(m) == 2 and m[0].distance < FEATURE_RATIO * m[1].distance]
    if len(good) < 8:
        return 0
    src = points_a[[m.queryIdx for m in good]]
    dst = points_b[[m.trainIdx for m in good]]
    _, mask = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=FEATURE_RANSAC_PX)
    return int(mask.sum()) if mask is not None else 0


@dataclass(frozen=True)
class DuplicatePair:
    pair_id: int  # review rank, 1 = most likely a duplicate
    hamming: int
    feature_inliers: int
    a: Record
    b: Record

    @property
    def scope(self) -> str:
        return "within domain" if self.a.domain == self.b.domain else "across domains"


def load_dhashes(data_root, records: list[Record]) -> np.ndarray:
    """(N, 64) uint8 matrix of the dHashes stored in the cache manifest (run build_cache first)."""
    manifest = load_manifest(data_root)
    missing = [r.filename for r in records if "dhash" not in manifest.get(r.filename, {})]
    if missing:
        raise DatasetError(f"no dHash for {len(missing)} images (e.g. {missing[:3]}); run `prepare` to build the cache")
    return np.stack([hex_to_bits(manifest[r.filename]["dhash"]) for r in records]) if records else np.zeros((0, 64), np.uint8)


def duplicate_pairs(
    data_root, records: list[Record], bits: np.ndarray, max_distance: int = NEAR_DUPLICATE_MAX_DISTANCE
) -> list[DuplicatePair]:
    """All candidate pairs, ranked: most feature inliers first, then smallest Hamming distance, then names."""
    candidates = find_near_duplicates(bits, max_distance)
    needed = sorted({i for i, j, _ in candidates} | {j for i, j, _ in candidates})
    features = {i: sift_features(read_cached_rgb(data_root, records[i].filename)) for i in needed}
    scored = [
        (-feature_inliers(features[i], features[j]), d, records[i].filename, records[j].filename, records[i], records[j])
        for i, j, d in candidates
    ]
    scored.sort(key=lambda t: t[:4])
    return [DuplicatePair(rank, d, -neg, a, b) for rank, (neg, d, _, _, a, b) in enumerate(scored, start=1)]


def duplicate_stats(pairs: list[DuplicatePair]) -> dict:
    """Counts of candidate pairs per Hamming distance and per scope (within / across domains)."""
    by_distance = Counter(p.hamming for p in pairs)
    by_scope = Counter(p.scope for p in pairs)
    inliers = [p.feature_inliers for p in pairs]
    return {
        "total": len(pairs),
        "by_distance": {d: by_distance[d] for d in sorted(by_distance)},
        "within_domain": by_scope["within domain"],
        "across_domains": by_scope["across domains"],
        "same_class": sum(p.a.cls == p.b.cls for p in pairs),
        "images_involved": len({p.a.filename for p in pairs} | {p.b.filename for p in pairs}),
        "max_feature_inliers": max(inliers, default=0),
    }


def results_dir(data_root) -> Path:
    return work_dir(data_root) / "results"


def figures_dir(data_root) -> Path:
    return work_dir(data_root) / "figures"


def write_duplicate_report(data_root, pairs: list[DuplicatePair]) -> Path:
    """`_work/results/near_duplicates.csv`: every candidate pair, in review order."""
    path = results_dir(data_root) / "near_duplicates.csv"
    lines = ["pair_id,hamming,feature_inliers,scope,file_a,file_b,class_a,class_b,domain_a,domain_b"]
    for p in pairs:
        lines.append(
            f"{p.pair_id},{p.hamming},{p.feature_inliers},{p.scope},{p.a.filename},{p.b.filename},"
            f"{p.a.cls},{p.b.cls},{p.a.domain},{p.b.domain}"
        )
    write_text_atomic(path, "\n".join(lines) + "\n")
    return path


def validate_duplicate_groups(groups, records: list[Record]) -> list[list[str]]:
    """Check the duplicate groups (the embedded ``DUPLICATE_GROUPS``) against the index and return them
    normalised: members sorted, groups sorted. Raises DatasetError unless

    * every group is a list of at least two filenames,
    * every filename exists in the index,
    * no filename appears in two groups (nor twice in one), and
    * every group lies within one class x domain stratum, because the splits stratify on it.

    Nothing is merged or repaired: a wrong group list is a bug in ``annotations/duplicate_groups.json``."""
    stratum_of = {r.filename: r.stratum for r in records}
    first_group: dict[str, int] = {}
    for number, group in enumerate(groups):
        if not isinstance(group, (list, tuple)) or len(group) < 2 or not all(isinstance(n, str) for n in group):
            raise DatasetError(f"duplicate group #{number}: expected a list of at least 2 filenames, got {group!r}")
        for name in group:
            if name not in stratum_of:
                raise DatasetError(f"duplicate group #{number}: {name} is not in the dataset index")
            if name in first_group:
                raise DatasetError(f"{name} appears in duplicate groups #{first_group[name]} and #{number}")
            first_group[name] = number
        strata = sorted({stratum_of[n] for n in group})
        if len(strata) != 1:
            raise DatasetError(f"duplicate group #{number} {list(group)} spans several class x domain strata: {strata}")
    return sorted((sorted(g) for g in groups), key=lambda g: g[0])

# Okabe-Ito colour-blind-safe palette.
OKABE_ITO = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky": "#56B4E9",
    "green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermilion": "#D55E00",
    "purple": "#CC79A7",
}
# One colour per domain (2 series: they must stay distinguishable in grayscale print as well).
DOMAIN_COLORS = {"white": OKABE_ITO["blue"], "field": OKABE_ITO["orange"]}
FIGURE_DPI = 300


def pyplot():
    """matplotlib.pyplot on the Agg backend (no display needed, also on Colab and on servers)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def thumbnail(rgb: np.ndarray, height: int) -> np.ndarray:
    scale = height / rgb.shape[0]
    return cv2.resize(rgb, (max(1, round(rgb.shape[1] * scale)), height), interpolation=cv2.INTER_AREA)


def save_duplicate_sheets(
    data_root,
    pairs: list[DuplicatePair],
    *,
    max_pairs: int = SHEET_MAX_PAIRS,
    per_page: int = SHEET_PAIRS_PER_PAGE,
) -> list[Path]:
    """Contact sheets `near_duplicates_<n>.png` of the top-ranked pairs, side by side, labelled with
    filename, class, domain, dHash distance and feature inliers. Old pages are removed first."""
    plt = pyplot()
    out_dir = figures_dir(data_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("near_duplicates*.png"):
        old.unlink()
    shown = pairs[:max_pairs]
    cols, rows = 4, max(1, per_page // 4)
    pages = [shown[i : i + per_page] for i in range(0, len(shown), per_page)]
    paths = []
    for number, chunk in enumerate(pages, start=1):
        fig = plt.figure(figsize=(20, 11.4 if rows == 2 else 6), dpi=100)
        grid = fig.add_gridspec(rows, cols, left=0.005, right=0.995, top=0.935, bottom=0.005, wspace=0.05, hspace=0.1)
        for k, pair in enumerate(chunk):
            inner = grid[k // cols, k % cols].subgridspec(2, 2, height_ratios=[0.055, 1], wspace=0.03, hspace=0.01)
            head = fig.add_subplot(inner[0, :])
            head.axis("off")
            head.text(
                0.5, 0.5,
                f"#{pair.pair_id}   dHash {pair.hamming}   inliers {pair.feature_inliers}   ({pair.scope})",
                ha="center", va="center", fontsize=11, fontweight="bold",
            )
            for side, record in enumerate((pair.a, pair.b)):
                ax = fig.add_subplot(inner[1, side])
                ax.imshow(thumbnail(read_cached_rgb(data_root, record.filename), 560))
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_edgecolor(DOMAIN_COLORS[record.domain])
                    spine.set_linewidth(2.5)
                ax.set_xlabel(f"{record.filename}\n{record.cls}, {record.domain}", fontsize=9)
        first, last = chunk[0].pair_id, chunk[-1].pair_id
        fig.suptitle(
            f"Near-duplicate candidates, page {number}/{len(pages)} (pairs #{first}-#{last} of {len(pairs)}; "
            "border colour: blue = white background, orange = field)",
            fontsize=13, y=0.985,
        )
        path = out_dir / f"near_duplicates_{number:02d}.png"
        fig.savefig(path, dpi=100)
        plt.close(fig)
        paths.append(path)
    return paths

SPLIT_SEEDS = (0, 1, 2, 3, 4)
SPLIT_PERCENT = 15  # test and val each; train gets the remaining 70


def split_size(n_units: int, percent: int = SPLIT_PERCENT) -> int:
    """round(percent / 100 * n) with halves rounded up, in integer arithmetic."""
    return (percent * n_units + 50) // 100


def split_sha256(seed: int, train: list[str], val: list[str], test: list[str]) -> str:
    payload = json.dumps(
        {"seed": seed, "train": sorted(train), "val": sorted(val), "test": sorted(test)},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def stratum_order(stratum: tuple[str, str]) -> tuple[int, int]:
    return (CLASS_NAMES.index(stratum[0]), DOMAINS.index(stratum[1]))


def build_units(records: list[Record], groups: list[list[str]]) -> dict[tuple[str, str], list[tuple[str, ...]]]:
    """{stratum: units}; a unit is a sorted tuple of filenames: a duplicate group, or a single image.
    ``groups`` is validated first (see ``validate_duplicate_groups``); ``[]`` gives one unit per image."""
    by_name = {r.filename: r for r in records}
    units: dict[tuple[str, str], list[tuple[str, ...]]] = {}
    grouped: set[str] = set()
    for group in validate_duplicate_groups(groups, records):
        members = tuple(group)
        grouped.update(members)
        units.setdefault(by_name[members[0]].stratum, []).append(members)
    for record in records:
        if record.filename not in grouped:
            units.setdefault(record.stratum, []).append((record.filename,))
    return units


def make_split(records: list[Record], groups: list[list[str]], seed: int) -> dict:
    """One split as a dict with keys seed, train, val, test (sorted filename lists) and sha256."""
    train: list[str] = []
    val: list[str] = []
    test: list[str] = []
    units_by_stratum = build_units(records, groups)
    for stratum in sorted(units_by_stratum, key=stratum_order):
        units = sorted(units_by_stratum[stratum])
        shuffled = [units[i] for i in np.random.default_rng(seed).permutation(len(units))]
        n_test = split_size(len(units))
        n_val = split_size(len(units))
        for target, chosen in (
            (test, shuffled[:n_test]),
            (val, shuffled[n_test : n_test + n_val]),
            (train, shuffled[n_test + n_val :]),
        ):
            target.extend(name for unit in chosen for name in unit)
    train, val, test = sorted(train), sorted(val), sorted(test)
    return {"seed": seed, "train": train, "val": val, "test": test, "sha256": split_sha256(seed, train, val, test)}


def splits_dir(data_root) -> Path:
    return work_dir(data_root) / "splits"


def split_path(data_root, seed: int) -> Path:
    return splits_dir(data_root) / f"split_{seed}.json"


def write_splits(data_root, records: list[Record], groups: list[list[str]], seeds=SPLIT_SEEDS) -> dict[int, str]:
    """Generate and write split_<k>.json. Returns {seed: "new" | "unchanged" | "CHANGED"} so that the
    caller can say loudly when an existing (committed) split differs from the regenerated one."""
    status = {}
    for seed in seeds:
        split = make_split(records, groups, seed)
        path = split_path(data_root, seed)
        before = None
        if path.is_file():
            try:
                before = json.loads(read_file_bytes(path).decode("utf-8")).get("sha256")
            except ValueError:
                before = ""
        status[seed] = "new" if before is None else "unchanged" if before == split["sha256"] else "CHANGED"
        if status[seed] != "unchanged":
            write_json(path, split)
    return status


def load_split(data_root, seed: int) -> dict:
    """A split written by `prepare`, with its sha256 re-computed and verified."""
    path = split_path(data_root, seed)
    if not path.is_file():
        raise DatasetError(f"{path} does not exist; run the `prepare` command first")
    split = json.loads(read_file_bytes(path).decode("utf-8"))
    expected = split_sha256(split["seed"], split["train"], split["val"], split["test"])
    if split.get("sha256") != expected:
        raise DatasetError(f"{path}: sha256 does not match its content (file edited by hand?)")
    return split


def split_counts(split: dict, records: list[Record]) -> dict:
    """{'train': {'white': n, 'field': n, 'all': n}, 'val': ..., 'test': ...}"""
    domain_of = {r.filename: r.domain for r in records}
    return {
        part: {**{d: sum(domain_of[n] == d for n in split[part]) for d in DOMAINS}, "all": len(split[part])}
        for part in ("train", "val", "test")
    }

GRID_SEED = 42
DOMAIN_LABELS = {"white": "White background", "field": "Field background"}


def class_domain_counts(records: list[Record]) -> dict[tuple[str, str], int]:
    counts = Counter(r.stratum for r in records)
    return {(c, d): counts.get((c, d), 0) for c in CLASS_NAMES for d in DOMAINS}


def dataset_counts_markdown(records: list[Record]) -> str:
    counts = class_domain_counts(records)
    lines = ["| Class | White background | Field background | Total |", "|---|---:|---:|---:|"]
    for cls in CLASS_NAMES:
        white, field = counts[(cls, "white")], counts[(cls, "field")]
        lines.append(f"| {cls} | {white} | {field} | {white + field} |")
    white_total = sum(counts[(c, "white")] for c in CLASS_NAMES)
    field_total = sum(counts[(c, "field")] for c in CLASS_NAMES)
    lines.append(f"| **Total** | **{white_total}** | **{field_total}** | **{white_total + field_total}** |")
    return "\n".join(lines) + "\n"


def write_dataset_counts(data_root, records: list[Record]) -> Path:
    path = results_dir(data_root) / "dataset_counts.md"
    write_text_atomic(path, dataset_counts_markdown(records))
    return path


def save_dataset_grid(data_root, records: list[Record], path: Path | None = None, seed: int = GRID_SEED) -> Path:
    """2 rows (white, field) x 5 classes, one random (seeded) sample each, read from the cache."""
    plt = pyplot()
    path = path or figures_dir(data_root) / "dataset_grid.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    chosen = {}
    for domain in DOMAINS:
        for cls in CLASS_NAMES:
            names = sorted(r.filename for r in records if r.stratum == (cls, domain))
            chosen[(cls, domain)] = names[int(rng.integers(len(names)))] if names else None
    with plt.rc_context({"font.size": 8.5}):
        fig = plt.figure(figsize=(5.6, 4.72))
        grid = fig.add_gridspec(2, 5, left=0.065, right=0.995, top=0.94, bottom=0.004, wspace=0.05, hspace=0.02)
        for row, domain in enumerate(DOMAINS):
            for col, cls in enumerate(CLASS_NAMES):
                ax = fig.add_subplot(grid[row, col])
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
                name = chosen[(cls, domain)]
                if name is not None:
                    ax.imshow(thumbnail(read_cached_rgb(data_root, name), 760))
                if row == 0:
                    ax.set_title(cls, fontsize=8.5, fontweight="bold", pad=3)
                if col == 0:
                    ax.set_ylabel(DOMAIN_LABELS[domain], fontsize=8.5, fontweight="bold", labelpad=4)
        fig.savefig(path, dpi=FIGURE_DPI)
        plt.close(fig)
    return path


def save_class_domain_counts(data_root, records: list[Record], path: Path | None = None) -> Path:
    """Grouped bar chart: images per class, one bar per domain, value labels on the bars."""
    plt = pyplot()
    path = path or figures_dir(data_root) / "class_domain_counts.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = class_domain_counts(records)
    x = np.arange(len(CLASS_NAMES))
    width = 0.38
    with plt.rc_context({"font.size": 9}):
        fig, ax = plt.subplots(figsize=(5.4, 3.3))
        for k, domain in enumerate(DOMAINS):
            values = [counts[(c, domain)] for c in CLASS_NAMES]
            bars = ax.bar(
                x + (k - 0.5) * width, values, width * 0.94, color=DOMAIN_COLORS[domain], label=DOMAIN_LABELS[domain]
            )
            ax.bar_label(bars, fontsize=8, padding=2)
        ax.set_xticks(x, [c.replace(" ", "\n") for c in CLASS_NAMES])
        ax.set_ylabel("Number of images")
        ax.set_ylim(0, max(counts.values(), default=1) * 1.15)
        ax.yaxis.grid(True, color="#DDDDDD", linewidth=0.6)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.legend(frameon=False, loc="upper left", fontsize=8.5)
        fig.tight_layout(pad=0.6)
        fig.savefig(path, dpi=FIGURE_DPI)
        plt.close(fig)
    return path

def exif_summary(records: list[Record]) -> str:
    tagged = Counter(r.exif_orientation for r in records if r.exif_orientation != 1)
    detail = ", ".join(f"orientation {o}: {n}" for o, n in sorted(tagged.items()))
    return f"{sum(tagged.values())} images carry an EXIF rotation tag ({detail or 'none'}); all applied"


def prepare_data(
    data_root, *, expected_counts=EXPECTED_COUNTS, groups=None, workers: int | None = None, out=print
) -> dict:
    """index -> cache -> near-duplicate audit -> splits -> tables and figures. Returns a summary dict
    (also printed through ``out``). Raises DatasetError on any dataset problem.

    ``groups`` are the duplicate groups kept together in the splits; ``None`` means the embedded
    ``DUPLICATE_GROUPS``, which is what every real run uses (tests pass their own for tiny datasets)."""
    import time

    start = time.time()
    data_root = Path(data_root)
    out(f"prepare: data root {data_root.resolve()}")
    records = build_index(data_root, expected_counts=expected_counts)
    write_index(data_root, records)
    counts = Counter(r.domain for r in records)
    out(f"  index       {len(records)} images: white {counts['white']}, field {counts['field']}; {len(CLASS_NAMES)} classes")
    out(f"  exif        {exif_summary(records)}")

    t = time.time()
    cache = build_cache(data_root, records, workers=workers, log=out)
    out(
        f"  portrait    {cache.rotated_landscape} images were landscape after EXIF and were turned 90 degrees clockwise"
    )
    out(
        f"  cache       {cache.total} images, long side {CACHE_LONG_SIDE} px, JPEG q{CACHE_JPEG_QUALITY}: "
        f"built {cache.built}, already up to date {cache.reused} ({time.time() - t:.0f} s)"
    )

    t = time.time()
    pairs = duplicate_pairs(data_root, records, load_dhashes(data_root, records))
    stats = duplicate_stats(pairs)
    write_duplicate_report(data_root, pairs)
    sheets = save_duplicate_sheets(data_root, pairs)
    by_distance = " ".join(f"{d}:{n}" for d, n in stats["by_distance"].items())
    out(
        f"  duplicates  {stats['total']} dHash candidate pairs (distance <= {NEAR_DUPLICATE_MAX_DISTANCE}): "
        f"{stats['within_domain']} within domain, {stats['across_domains']} across; by distance {by_distance}"
    )
    out(
        f"              best feature-match score {stats['max_feature_inliers']} (a real duplicate shares hundreds); "
        f"{len(sheets)} contact sheets in {figures_dir(data_root)} ({time.time() - t:.0f} s)"
    )
    source = "embedded" if groups is None else "given"
    groups = validate_duplicate_groups(DUPLICATE_GROUPS if groups is None else groups, records)
    out(f"  groups      duplicate groups: {len(groups)} ({sum(len(g) for g in groups)} images), {source}; each is kept in one split")

    status = write_splits(data_root, records, groups)
    first = load_split(data_root, SPLIT_SEEDS[0])
    sizes = split_counts(first, records)
    out(
        f"  splits      seeds {SPLIT_SEEDS[0]}-{SPLIT_SEEDS[-1]}: train/val/test = "
        f"{sizes['train']['all']}/{sizes['val']['all']}/{sizes['test']['all']} "
        f"(test: {sizes['test']['white']} white, {sizes['test']['field']} field); "
        + ", ".join(f"{seed}: {state}" for seed, state in status.items())
    )
    if "CHANGED" in status.values():
        out("  WARNING     an existing split file differs from the regenerated one and was overwritten")
        out("              (expected only if the duplicate groups or the dataset changed; otherwise investigate before training)")
    out("              sha256 " + " ".join(load_split(data_root, s)["sha256"][:10] for s in SPLIT_SEEDS))

    write_dataset_counts(data_root, records)
    save_dataset_grid(data_root, records)
    save_class_domain_counts(data_root, records)
    out(f"  report      dataset_counts.md, dataset_grid.png, class_domain_counts.png in {work_dir(data_root)}")
    elapsed = time.time() - start
    out(f"prepare: done in {elapsed:.0f} s")
    return {
        "records": len(records),
        "cache": cache,
        "duplicates": stats,
        "duplicate_groups": groups,
        "splits": status,
        "seconds": elapsed,
    }


def synthetic_records(per_stratum: int = 20) -> list[Record]:
    """Fake index entries (no files) covering every class x domain stratum; for smoke checks and tests."""
    prefix = {(cls, domain): p for p, cls, domain, _ in LABEL_TABLE}
    return [
        Record(f"{prefix[(cls, domain)]}{i}.jpg", f"x/{prefix[(cls, domain)]}{i}.jpg", cls, CLASS_NAMES.index(cls), domain, 1, "")
        for cls in CLASS_NAMES
        for domain in DOMAINS
        for i in range(per_stratum)
    ]


def pick_smoke_records(records: list[Record], n: int = 20) -> list[Record]:
    """Up to ``n`` records: first one of each EXIF orientation 3/6/8 present, then round-robin over strata."""
    chosen: list[Record] = []
    for orientation in (3, 6, 8):
        match = next((r for r in records if r.exif_orientation == orientation), None)
        if match:
            chosen.append(match)
    queues = {}
    for r in records:
        queues.setdefault(r.stratum, []).append(r)
    order = sorted(queues, key=stratum_order)
    while len(chosen) < min(n, len(records)):
        progressed = False
        for stratum in order:
            while queues[stratum] and queues[stratum][0] in chosen:
                queues[stratum].pop(0)
            if queues[stratum] and len(chosen) < n:
                chosen.append(queues[stratum].pop(0))
                progressed = True
        if not progressed:
            break
    return chosen


def smoke_require(condition: bool, message: str) -> None:
    if not condition:
        raise DatasetError(f"data smoke check failed: {message}")


def run_data_smoke(data_root, n_images: int = 20, workers: int = 2, log=print, extra_checks=None) -> None:
    """Cheap end-to-end check of the data path on ~20 real images. Writes only to a temp folder.

    ``extra_checks(tmp_root, selected_records)``, if given, runs at the end while the temp folder (with the
    cache of the selected images) still exists; later phases use it to build on the same tiny dataset."""
    data_root = Path(data_root)
    records = build_index(data_root, expected_counts=None, with_sha1=False)
    log(f"smoke: OK - index of {len(records)} images, labels match filename prefixes (and the CSV if present)")
    if class_domain_counts(records) == EXPECTED_COUNTS:
        groups = validate_duplicate_groups(DUPLICATE_GROUPS, records)
        for seed in SPLIT_SEEDS:
            split = make_split(records, groups, seed)
            where = {name: part for part in ("train", "val", "test") for name in split[part]}
            smoke_require(all(len({where[n] for n in g}) == 1 for g in groups), f"a duplicate group straddles splits (seed {seed})")
        log(f"smoke: OK - {len(groups)} embedded duplicate groups ({sum(len(g) for g in groups)} images) match the index and stay in one split")
    else:
        log("smoke: SKIPPED - embedded duplicate groups are not checked: this is not the full dataset")
    selected = [
        replace(r, sha1=hashlib.sha1(read_file_bytes(data_root / r.rel_path)).hexdigest())
        for r in pick_smoke_records(records, n_images)
    ]
    with tempfile.TemporaryDirectory(prefix="csci935-smoke-") as tmp:
        tmp_root = Path(tmp)
        stats = build_cache(data_root, selected, workers=workers, output_root=tmp_root)
        smoke_require(stats.built == len(selected), f"expected {len(selected)} cached images, built {stats.built}")
        for record in selected:
            rgb = read_cached_rgb(tmp_root, record.filename)
            smoke_require(rgb.ndim == 3 and rgb.shape[2] == 3 and rgb.dtype == np.uint8, f"{record.filename}: bad array")
            smoke_require(rgb.shape[0] >= rgb.shape[1], f"{record.filename}: cached image is not portrait")
            smoke_require(max(rgb.shape[:2]) <= CACHE_LONG_SIDE, f"{record.filename}: cached image too large")
        for record in [r for r in selected if r.exif_orientation != 1][:3]:
            full = read_rgb(data_root / record.rel_path)
            cached = read_cached_rgb(tmp_root, record.filename)
            smoke_require(full.shape[0] >= full.shape[1], f"{record.filename}: EXIF-corrected image is not portrait")
            smoke_require(abs(full.shape[1] / full.shape[0] - cached.shape[1] / cached.shape[0]) < 0.01, f"{record.filename}: aspect changed")
        again = build_cache(data_root, selected, workers=workers, output_root=tmp_root)
        smoke_require(again.built == 0, "second cache run is not idempotent")
        log(f"smoke: OK - read and cached {len(selected)} images (EXIF orientations {sorted({r.exif_orientation for r in selected})}), idempotent")

        bits = load_dhashes(tmp_root, selected)
        smoke_require(bits.shape == (len(selected), 64), "dHash matrix has the wrong shape")
        smoke_require(int(np.trace(hamming_matrix(bits))) == 0, "dHash distance to itself is not 0")
        log("smoke: OK - dHash computed")

        fake = synthetic_records()
        names = {r.filename for r in fake}
        for seed in SPLIT_SEEDS:
            split = make_split(fake, [], seed)
            parts = [set(split[k]) for k in ("train", "val", "test")]
            smoke_require(sum(len(p) for p in parts) == len(names) and set.union(*parts) == names, "split does not partition")
            smoke_require(split == make_split(fake, [], seed), "split is not deterministic")
        log("smoke: OK - splits are deterministic partitions")

        write_dataset_counts(tmp_root, selected)
        save_class_domain_counts(tmp_root, selected)
        save_dataset_grid(tmp_root, selected)
        smoke_require(
            all((figures_dir(tmp_root) / f).stat().st_size > 1000 for f in ("class_domain_counts.png", "dataset_grid.png")),
            "figures were not written",
        )
        log("smoke: OK - tables and figures")
        if extra_checks is not None:
            extra_checks(tmp_root, selected)

# ---- from 20_classifier.ipynb ----
import gc
import math
import platform
import random
import re
import time
from urllib.parse import urlparse

import torch
import torch.nn.functional as F
import torchvision
from sklearn.metrics import confusion_matrix, f1_score, precision_recall_fscore_support

NUM_CLASSES = len(CLASS_NAMES)
BACKBONES = ("resnet50", "convnext_tiny", "swin_t")
INPUT_MODES = ("squash", "pad", "rect")
# (height, width) of the network input at an equal pixel budget (~100k px): E0 compares geometry, not resolution.
INPUT_SIZES = {"squash": (320, 320), "pad": (320, 320), "rect": (448, 224)}
SUBSETS = ("white", "field", "mixed")
KINDS = ("classifier", "segmenter", "analysis")


class ExperimentError(Exception):
    """Base class of errors that the CLI reports as one clean line (no traceback)."""


class UnknownExperimentError(ExperimentError):
    pass


class ChoicesError(ExperimentError):
    """A value that a gate should have written to choices.json is missing."""


class NotReadyError(ExperimentError):
    """The experiment needs a later phase that is not implemented yet."""


@dataclass(frozen=True)
class ExperimentConfig:
    exp_id: str
    backbone: str | None  # None: the winning backbone of gate G1 (choices.json "backbone")
    train_domains: tuple[str, ...]
    select_domains: tuple[str, ...]  # must equal train_domains
    test_subsets: tuple[str, ...]  # which test subsets the report uses (all three are always evaluated)
    input_mode: str | None  # None: the winning input mode of gate G0 (choices.json "input_mode")
    use_composites: bool = False  # Method A: extra training samples from CompositeSource (phase 05)
    seg_crop: bool = False  # Method B: input_hook crops to the segmenter box (phase 06)
    kind: str = "classifier"  # "segmenter" / "analysis" rows exist in the matrix but are not run here
    alias_of_winner: str = ""  # "E0": this row is the winning E0 row (same run folder, no retraining)
    # Recipe (section 6.1 of the report). Defaults are the T3.4 table.
    stage1_epochs: int = 2  # linear probe: backbone frozen, head only
    stage1_lr: float = 1e-3
    epochs: int = 30  # stage 2: fine-tune everything
    lr: float | None = None  # None: choices.json lr[backbone] (split-0 sweep over SWEEP_LRS)
    weight_decay: float = 0.05
    warmup_epochs: int = 1
    label_smoothing: float = 0.1
    batch_size: int = 32
    grad_accum: int = 1
    clip_norm: float = 1.0
    patience: int = 10  # stage-2 epochs without improvement of the selection metric
    dropout: float = 0.2
    pretrained: bool = True
    size_div: int = 1  # dev/smoke only: divide the input size (448x224 -> 112x56 with 4)
    note: str = ""

    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"{self.exp_id}: kind must be one of {KINDS}, got {self.kind!r}")
        if self.backbone is not None and self.backbone not in BACKBONES and self.kind == "classifier":
            raise ValueError(f"{self.exp_id}: unknown backbone {self.backbone!r}")
        if self.input_mode is not None and self.input_mode not in INPUT_MODES:
            raise ValueError(f"{self.exp_id}: unknown input mode {self.input_mode!r}")
        for name in ("train_domains", "select_domains"):
            domains = getattr(self, name)
            if not domains or not set(domains) <= set(DOMAINS):
                raise ValueError(f"{self.exp_id}: {name} must be a non-empty subset of {DOMAINS}, got {domains!r}")
        if set(self.select_domains) != set(self.train_domains):
            raise ValueError(
                f"{self.exp_id}: select_domains must equal train_domains (checkpoints are chosen on the domains "
                f"the model was trained on; anything else leaks information), got {self.select_domains} vs {self.train_domains}"
            )
        if not set(self.test_subsets) <= set(SUBSETS):
            raise ValueError(f"{self.exp_id}: test_subsets must be a subset of {SUBSETS}")

    def is_resolved(self) -> bool:
        return self.backbone is not None and self.input_mode is not None and self.lr is not None

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
PAD_COLOR = tuple(round(m * 255) for m in IMAGENET_MEAN)  # letterbox colour: the ImageNet mean, (124, 116, 104)

AUG_CROP_AREA = (0.6, 1.0)  # fraction of the image area kept by the random crop
AUG_ROTATION_DEG = 15.0
AUG_BRIGHTNESS = 0.2
AUG_CONTRAST = 0.2
AUG_SATURATION = 0.15
AUG_HUE = 0.02  # fraction of the hue circle: +-7.2 degrees at most


def input_size(mode: str, size_div: int = 1) -> tuple[int, int]:
    """(height, width) of the network input for an input mode. ``size_div`` > 1 is for smoke tests only."""
    if mode not in INPUT_SIZES:
        raise ValueError(f"unknown input mode {mode!r}, expected one of {INPUT_MODES}")
    height, width = INPUT_SIZES[mode]
    return max(8, height // size_div), max(8, width // size_div)


def resize_exact(rgb: np.ndarray, height: int, width: int) -> np.ndarray:
    shrinking = height * width < rgb.shape[0] * rgb.shape[1]
    return cv2.resize(rgb, (width, height), interpolation=cv2.INTER_AREA if shrinking else cv2.INTER_LINEAR)


def resize_content(rgb: np.ndarray, mode: str, size: tuple[int, int]) -> np.ndarray:
    """The image content at network resolution. For `pad` this is the aspect-preserving fit inside the
    box (smaller than the box in one dimension); `letterbox` then places it on the canvas."""
    height, width = size
    if mode != "pad":
        return resize_exact(rgb, height, width)
    scale = min(height / rgb.shape[0], width / rgb.shape[1])
    return resize_exact(rgb, max(1, round(rgb.shape[0] * scale)), max(1, round(rgb.shape[1] * scale)))


def letterbox(content: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    height, width = size
    if content.shape[:2] == (height, width):
        return content
    canvas = np.empty((height, width, 3), dtype=np.uint8)
    canvas[:] = PAD_COLOR
    top, left = (height - content.shape[0]) // 2, (width - content.shape[1]) // 2
    canvas[top : top + content.shape[0], left : left + content.shape[1]] = content
    return canvas


def random_crop(rgb: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Crop covering 60-100% of the area at the image's own aspect (a zoom / framing change)."""
    height, width = rgb.shape[:2]
    side = math.sqrt(rng.uniform(*AUG_CROP_AREA))
    crop_h, crop_w = max(1, round(height * side)), max(1, round(width * side))
    top = int(rng.integers(0, height - crop_h + 1))
    left = int(rng.integers(0, width - crop_w + 1))
    return rgb[top : top + crop_h, left : left + crop_w]


def random_flips(rgb: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    flip_h, flip_v = rng.random() < 0.5, rng.random() < 0.5
    if flip_h:
        rgb = rgb[:, ::-1]
    if flip_v:
        rgb = rgb[::-1]
    return np.ascontiguousarray(rgb)


def random_rotation(rgb: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    angle = rng.uniform(-AUG_ROTATION_DEG, AUG_ROTATION_DEG)
    height, width = rgb.shape[:2]
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
    return cv2.warpAffine(rgb, matrix, (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)


def _gray(img: np.ndarray) -> np.ndarray:
    return img[..., 0] * 0.299 + img[..., 1] * 0.587 + img[..., 2] * 0.114


def color_jitter(rgb: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Brightness, contrast, saturation (multiplicative factors) and a small hue shift, in random order."""
    brightness = rng.uniform(1 - AUG_BRIGHTNESS, 1 + AUG_BRIGHTNESS)
    contrast = rng.uniform(1 - AUG_CONTRAST, 1 + AUG_CONTRAST)
    saturation = rng.uniform(1 - AUG_SATURATION, 1 + AUG_SATURATION)
    hue = rng.uniform(-AUG_HUE, AUG_HUE)
    order = rng.permutation(4)  # all draws happen up front so the stream does not depend on the order
    img = rgb.astype(np.float32) / 255.0
    for op in order:
        if op == 0:
            img = np.clip(img * brightness, 0.0, 1.0)
        elif op == 1:
            mean = float(_gray(img).mean())
            img = np.clip((img - mean) * contrast + mean, 0.0, 1.0)
        elif op == 2:
            gray = _gray(img)[..., None]
            img = np.clip((img - gray) * saturation + gray, 0.0, 1.0)
        else:
            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)  # float32: H in [0, 360), S and V in [0, 1]
            hsv[..., 0] = (hsv[..., 0] + hue * 360.0) % 360.0
            img = np.clip(cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB), 0.0, 1.0)
    return np.clip(img * 255.0 + 0.5, 0, 255).astype(np.uint8)


@dataclass(frozen=True)
class ImageTransform:
    """uint8 RGB image -> uint8 RGB image of the network input size. ``train`` adds the augmentation (and
    needs an ``rng``); the evaluation transform is the input-mode resize only and is deterministic."""

    mode: str
    train: bool = False
    size_div: int = 1

    @property
    def size(self) -> tuple[int, int]:
        return input_size(self.mode, self.size_div)

    def __call__(self, rgb: np.ndarray, rng: np.random.Generator | None = None) -> np.ndarray:
        if self.train:
            if rng is None:
                raise ValueError("the training transform needs an rng")
            rgb = random_rotation(random_flips(random_crop(rgb, rng), rng), rng)
        content = resize_content(np.ascontiguousarray(rgb), self.mode, self.size)
        if self.train:
            content = color_jitter(content, rng)
        return letterbox(content, self.size)


def normalize_batch(images: torch.Tensor, device) -> torch.Tensor:
    """uint8 [N, 3, H, W] -> float32 on ``device``, scaled to [0, 1] and normalised with the ImageNet mean/std."""
    x = images.to(device, non_blocking=True).float().div_(255.0)
    mean = torch.tensor(IMAGENET_MEAN, device=x.device).view(1, 3, 1, 1)
    std = torch.tensor(IMAGENET_STD, device=x.device).view(1, 3, 1, 1)
    return (x - mean) / std


def select_records(records: list[Record], filenames, domains=None) -> list[Record]:
    """Records of a split part (``filenames``, e.g. split['train']) restricted to ``domains``, in split order."""
    by_name = {r.filename: r for r in records}
    missing = [name for name in filenames if name not in by_name]
    if missing:
        raise DatasetError(f"{len(missing)} split entries are not in the index, e.g. {missing[:3]}; re-run `prepare`")
    chosen = [by_name[name] for name in filenames]
    return [r for r in chosen if domains is None or r.domain in domains]


def subsample_records(records: list[Record], n: int) -> list[Record]:
    """At most ``n`` records, round-robin over the class x domain strata (deterministic). For smoke runs."""
    queues: dict = {}
    for record in records:
        queues.setdefault(record.stratum, []).append(record)
    order = sorted(queues, key=stratum_order)
    chosen: list[Record] = []
    while len(chosen) < min(n, len(records)):
        for stratum in order:
            if queues[stratum] and len(chosen) < n:
                chosen.append(queues[stratum].pop(0))
    return chosen


def _sample_seed(seed: int) -> int:
    return int(seed) & 0x7FFFFFFF


class LeafDataset:
    """Map-style dataset over cached images.

    ``dataset[i]`` and ``dataset[(i, epoch)]`` both return ``(uint8 CHW tensor, class index, i)``. The
    augmentation of a sample is a pure function of ``(seed, epoch, i)``. Indices ``0..len(records)-1`` are
    the real records; the extra sources follow.
    """

    def __init__(self, data_root, records, transform, *, seed=0, extra_sources=(), input_hook=None, epoch=0):
        self.data_root = Path(data_root)
        self.records = list(records)
        self.transform = transform
        self.seed = _sample_seed(seed)
        self.extra_sources = tuple(extra_sources)
        self.input_hook = input_hook
        self.epoch = epoch
        self._extra_offsets = np.cumsum([0, *[len(s) for s in self.extra_sources]])

    def __len__(self) -> int:
        return len(self.records) + int(self._extra_offsets[-1])

    def sample_rng(self, index: int, epoch: int) -> np.random.Generator:
        return np.random.default_rng([self.seed, int(epoch), int(index)])

    def load_raw(self, index: int, epoch: int = 0) -> tuple[np.ndarray, int, str]:
        """(uint8 RGB before the transform, class index, name) after the hook for real images."""
        if index < len(self.records):
            record = self.records[index]
            rgb = read_cached_rgb(self.data_root, record.filename)
            if self.input_hook is not None:
                rgb = self.input_hook(rgb, record)
            return rgb, record.cls_idx, record.filename
        extra = index - len(self.records)
        which = int(np.searchsorted(self._extra_offsets, extra, side="right") - 1)
        return self.extra_sources[which].load(extra - int(self._extra_offsets[which]), epoch)

    def __getitem__(self, key):
        index, epoch = key if isinstance(key, tuple) else (key, self.epoch)
        if not 0 <= index < len(self):
            raise IndexError(index)
        rgb, label, _ = self.load_raw(index, epoch)
        rng = self.sample_rng(index, epoch) if self.transform.train else None
        image = self.transform(rgb, rng)
        return torch.from_numpy(np.ascontiguousarray(image.transpose(2, 0, 1))), int(label), index


class EpochSampler(torch.utils.data.Sampler):
    """Shuffled ``(index, epoch)`` pairs; the order is a function of (seed, epoch) only."""

    def __init__(self, n: int, seed: int):
        self.n, self.seed, self.epoch = n, _sample_seed(seed), 0

    def set_epoch(self, epoch: int) -> None:
        self.epoch = epoch

    def __len__(self) -> int:
        return self.n

    def __iter__(self):
        order = np.random.default_rng([self.seed, self.epoch]).permutation(self.n)
        return iter([(int(i), self.epoch) for i in order])


def _worker_init(worker_id: int) -> None:
    cv2.setNumThreads(0)  # OpenCV's own thread pool would fight with the DataLoader workers
    torch.set_num_threads(1)


def default_num_workers() -> int:
    """Data-loading processes, at most 4. Decoding and augmenting one image costs ~30 ms of CPU, so on a 2-vCPU
    Colab machine the workers, not the GPU, set the speed; the main process mostly waits for the GPU there, so
    every core gets a worker. From 3 cores up, one core is left to the main process."""
    try:
        cores = len(os.sched_getaffinity(0))
    except AttributeError:
        cores = os.cpu_count() or 1
    return max(1, min(4, cores if cores <= 2 else cores - 1))


def usable_workers(requested: int) -> int:
    """Workers that can really start: under `spawn` they re-import this file, which only works when it runs
    as the main script (the same rule as the cache's process pool)."""
    return requested if requested > 0 and pool_is_safe() else 0


def make_loader(dataset, batch_size, *, sampler=None, num_workers=0, drop_last=False, pin_memory=False, mp_context=None):
    num_workers = usable_workers(num_workers) if mp_context is None else num_workers
    kwargs = {}
    if num_workers > 0:
        kwargs.update(
            persistent_workers=True, worker_init_fn=_worker_init, multiprocessing_context=mp_context, prefetch_factor=4
        )
    return torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        sampler=sampler,
        shuffle=False,
        num_workers=num_workers,
        drop_last=drop_last,
        pin_memory=pin_memory,
        **kwargs,
    )


@dataclass
class EvalSet:
    """A fully materialised evaluation set: the deterministic eval transform applied once, kept as uint8."""

    images: torch.Tensor  # [N, 3, H, W] uint8
    labels: np.ndarray  # [N] int64
    names: list[str]
    domains: list[str]

    def __len__(self) -> int:
        return len(self.names)


def materialize(dataset: LeafDataset, *, num_workers: int = 0, batch_size: int = 32) -> EvalSet:
    """Run the (deterministic) eval transform over a dataset once. Per-epoch validation then costs only the
    forward pass instead of decoding JPEGs every epoch."""
    if len(dataset) != len(dataset.records):
        raise ValueError("materialize() is for real records only (no extra_sources)")
    loader = make_loader(dataset, batch_size, num_workers=num_workers)
    batches = [images for images, _, _ in loader]
    images = torch.cat(batches) if batches else torch.empty(0, 3, *dataset.transform.size, dtype=torch.uint8)
    return EvalSet(
        images,
        np.array([r.cls_idx for r in dataset.records], dtype=np.int64),
        [r.filename for r in dataset.records],
        [r.domain for r in dataset.records],
    )

from torch import nn


@dataclass(frozen=True)
class BackboneSpec:
    builder: str  # function in torchvision.models
    weights: str  # "<Weights enum>.<member>", resolved with torchvision.models.get_weight


BACKBONE_SPECS = {
    "resnet50": BackboneSpec("resnet50", "ResNet50_Weights.IMAGENET1K_V2"),
    "convnext_tiny": BackboneSpec("convnext_tiny", "ConvNeXt_Tiny_Weights.IMAGENET1K_V1"),
    "swin_t": BackboneSpec("swin_t", "Swin_T_Weights.IMAGENET1K_V1"),
}
# Weights that `download-weights` fetches: (name, weights enum member, what it is for).
SEGMENTER_WEIGHTS = "LRASPP_MobileNet_V3_Large_Weights.COCO_WITH_VOC_LABELS_V1"
WEIGHT_TABLE = (
    ("resnet50", BACKBONE_SPECS["resnet50"].weights, "ResNet50 classifier (E0, E1)"),
    ("convnext_tiny", BACKBONE_SPECS["convnext_tiny"].weights, "ConvNeXt-Tiny classifier (E2)"),
    ("swin_t", BACKBONE_SPECS["swin_t"].weights, "Swin-Tiny classifier (E2)"),
    ("lraspp_mobilenet_v3_large", SEGMENTER_WEIGHTS, "leaf segmenter (phase 06)"),
)


def backbone_weights(backbone: str):
    return torchvision.models.get_weight(BACKBONE_SPECS[backbone].weights)


def backbone_of(model: nn.Module) -> str:
    models = torchvision.models
    for name, cls in (("resnet50", models.ResNet), ("convnext_tiny", models.ConvNeXt), ("swin_t", models.SwinTransformer)):
        if isinstance(model, cls):
            return name
    raise ValueError(f"not one of our backbones: {type(model).__name__}")


def build_model(backbone: str, num_classes: int = NUM_CLASSES, *, pretrained: bool = True, dropout: float = 0.2, data_root=None):
    """torchvision backbone with the final layer replaced by Dropout + Linear. ``pretrained=False`` (tests,
    ``predict``) builds the same architecture with random weights and downloads nothing. With ``data_root``
    the weights are read from, and downloaded to, ``<data_root>/_work/weights``."""
    if backbone not in BACKBONE_SPECS:
        raise ValueError(f"unknown backbone {backbone!r}, expected one of {BACKBONES}")
    if data_root is not None and pretrained:
        set_torch_home(data_root)
    spec = BACKBONE_SPECS[backbone]
    model = getattr(torchvision.models, spec.builder)(weights=backbone_weights(backbone) if pretrained else None)
    if backbone == "resnet50":
        model.fc = nn.Sequential(nn.Dropout(dropout), nn.Linear(model.fc.in_features, num_classes))
    elif backbone == "convnext_tiny":
        model.classifier[2] = nn.Sequential(nn.Dropout(dropout), nn.Linear(model.classifier[2].in_features, num_classes))
    else:
        model.head = nn.Sequential(nn.Dropout(dropout), nn.Linear(model.head.in_features, num_classes))
    return model


def head_module(model: nn.Module) -> nn.Module:
    return {"resnet50": lambda m: m.fc, "convnext_tiny": lambda m: m.classifier[2], "swin_t": lambda m: m.head}[
        backbone_of(model)
    ](model)


def head_parameters(model: nn.Module) -> list[nn.Parameter]:
    return list(head_module(model).parameters())


def backbone_parameters(model: nn.Module) -> list[nn.Parameter]:
    head_ids = {id(p) for p in head_parameters(model)}
    return [p for p in model.parameters() if id(p) not in head_ids]


def gradcam_target_layer(model: nn.Module) -> nn.Module:
    """Layer whose activations Grad-CAM uses. Swin's output is NHWC: pass it through `cam_to_nchw`."""
    return model.layer4 if backbone_of(model) == "resnet50" else model.features[-1]


def cam_to_nchw(activation: torch.Tensor, model: nn.Module) -> torch.Tensor:
    return activation.permute(0, 3, 1, 2) if backbone_of(model) == "swin_t" else activation


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())

def weights_dir(data_root) -> Path:
    return work_dir(data_root) / "weights"


def set_torch_home(data_root, create: bool = True) -> Path:
    """Point torch's download cache at <data_root>/_work/weights (documented location of the pretrained weights)."""
    path = weights_dir(data_root)
    if create:
        path.mkdir(parents=True, exist_ok=True)
    os.environ["TORCH_HOME"] = str(path)
    return path


def weight_checkpoint_path(weights) -> Path:
    """Where torch stores the file of a torchvision weights enum member (under the current TORCH_HOME)."""
    return Path(torch.hub.get_dir()) / "checkpoints" / Path(urlparse(weights.url).path).name


def weight_file_ok(path: Path) -> bool:
    """The file exists and, when its name carries a sha256 prefix (resnet50-11ad3fa6.pth), matches it."""
    if not path.is_file() or path.stat().st_size == 0:
        return False
    match = re.search(r"-([0-9a-f]{8})\.pth$", path.name)
    if not match:
        return True
    digest = hashlib.sha256()
    with open(fs_path(path), "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().startswith(match.group(1))


def download_weights(data_root, out=print) -> list[dict]:
    """Fetch every pretrained weight file into <data_root>/_work/weights. Safe to call repeatedly."""
    home = set_torch_home(data_root)
    out(f"download-weights: TORCH_HOME = {home}")
    rows = []
    for name, member, purpose in WEIGHT_TABLE:
        weights = torchvision.models.get_weight(member)
        path = weight_checkpoint_path(weights)
        state = "already present"
        if not weight_file_ok(path):
            if path.exists():
                path.unlink()
                state = "re-downloaded (the stored file was damaged)"
            else:
                state = "downloaded"
            weights.get_state_dict(progress=True, check_hash=True)
            if not weight_file_ok(path):
                raise ExperimentError(f"{member}: the downloaded file {path} fails its checksum")
        size = path.stat().st_size / 1e6
        out(f"  {member}: {state}\n    purpose  {purpose}\n    url      {weights.url}\n    stored   {path} ({size:.1f} MB)")
        rows.append({"name": name, "weights": member, "url": weights.url, "path": str(path), "bytes": path.stat().st_size, "state": state})
    return rows

def classification_metrics(y_true, y_pred) -> dict:
    """Accuracy, macro-F1, per-class precision / recall / F1 / support and the 5x5 confusion matrix
    (rows = true class, columns = predicted class, in CLASS_NAMES order)."""
    y_true, y_pred = np.asarray(y_true, dtype=np.int64), np.asarray(y_pred, dtype=np.int64)
    n = int(len(y_true))
    if n == 0:
        return {"n": 0, "accuracy": None, "macro_f1": None, "per_class": {}, "confusion_matrix": []}
    labels = list(range(NUM_CLASSES))
    precision, recall, f1, support = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
    present = sorted(set(y_true.tolist()) | set(y_pred.tolist()))
    return {
        "n": n,
        "accuracy": float((y_true == y_pred).mean()),
        "macro_f1": float(f1_score(y_true, y_pred, labels=present, average="macro", zero_division=0)),
        "per_class": {
            name: {"precision": float(precision[i]), "recall": float(recall[i]), "f1": float(f1[i]), "support": int(support[i])}
            for i, name in enumerate(CLASS_NAMES)
        },
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
    }


def subset_mask(domains, subset: str) -> np.ndarray:
    domains = np.asarray(domains)
    return np.ones(len(domains), dtype=bool) if subset == "mixed" else domains == subset


def subset_metrics(probs: np.ndarray, labels, domains) -> dict:
    """{"white": ..., "field": ..., "mixed": ..., "domain_balanced": {"accuracy", "macro_f1"}} for one split part."""
    preds = probs.argmax(axis=1)
    result = {s: classification_metrics(labels[m], preds[m]) for s in SUBSETS for m in [subset_mask(domains, s)]}
    balanced = {}
    for key in ("accuracy", "macro_f1"):
        values = [result[s][key] for s in DOMAINS]
        balanced[key] = None if any(v is None for v in values) else float(np.mean(values))
    result["domain_balanced"] = balanced
    return result


def macro_f1(labels, preds) -> float:
    return classification_metrics(labels, preds)["macro_f1"] if len(labels) else float("nan")


@torch.no_grad()
def predict_probs(model: nn.Module, images: torch.Tensor, device, *, batch_size: int = 64, amp: bool = False) -> np.ndarray:
    """Softmax probabilities [N, 5] (float32, numpy) for a uint8 image tensor."""
    model.eval()
    out = []
    for start in range(0, len(images), batch_size):
        x = normalize_batch(images[start : start + batch_size], device)
        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=amp):
            logits = model(x)
        out.append(torch.softmax(logits.float(), dim=1).cpu())
    return torch.cat(out).numpy() if out else np.zeros((0, NUM_CLASSES), dtype=np.float32)


def evaluate_model(model: nn.Module, eval_set: EvalSet, device, *, amp: bool = False) -> tuple[dict, np.ndarray]:
    """(metrics for white / field / mixed / domain_balanced, probabilities) of a model on an EvalSet."""
    probs = predict_probs(model, eval_set.images, device, amp=amp)
    return subset_metrics(probs, eval_set.labels, eval_set.domains), probs

import contextlib

FALLBACK_BATCH = 16


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed % (2**32))
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def lr_at_step(step: int, *, base_lr: float, warmup_steps: int, total_steps: int) -> float:
    """Linear warmup over ``warmup_steps`` optimiser steps, then cosine decay to 0 at ``total_steps``."""
    if warmup_steps > 0 and step < warmup_steps:
        return base_lr * (step + 1) / warmup_steps
    progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
    return base_lr * 0.5 * (1.0 + math.cos(math.pi * min(1.0, max(0.0, progress))))


class CheckpointSelector:
    """Remembers the best state by the selection metric and decides when to stop early. Only epochs that are
    passed with ``counts_for_patience=True`` (stage 2) can run the patience out."""

    def __init__(self, patience: int):
        self.patience, self.stale = patience, 0
        self.best_score, self.best_epoch, self.best_state = -math.inf, 0, None

    def update(self, score: float, epoch: int, snapshot, *, counts_for_patience: bool) -> bool:
        """Record an epoch. ``snapshot`` is a function returning the state to keep. True if it is the new best."""
        if score > self.best_score:
            self.best_score, self.best_epoch, self.best_state, self.stale = score, epoch, snapshot(), 0
            return True
        if counts_for_patience:
            self.stale += 1
        return False

    @property
    def should_stop(self) -> bool:
        return self.stale >= self.patience


def is_out_of_memory(exc: BaseException) -> bool:
    return isinstance(exc, torch.cuda.OutOfMemoryError) or (
        isinstance(exc, RuntimeError) and "out of memory" in str(exc).lower()
    )


def free_device_memory(device: str) -> None:
    gc.collect()
    if device == "cuda":
        torch.cuda.empty_cache()
    elif device == "mps":
        torch.mps.empty_cache()


def cpu_state_dict(model: nn.Module) -> dict:
    return {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}


@dataclass
class TrainOutcome:
    best_state: dict
    best_epoch: int
    best_score: float
    history: list[dict]
    stopped_early: bool
    seconds: float


def train_classifier(cfg: ExperimentConfig, model: nn.Module, train_ds: LeafDataset, val_set: EvalSet, device: str, *,
                     seed: int, num_workers: int = 0, mp_context=None, log=print) -> TrainOutcome:
    """The two-stage LP-FT loop. Returns the best checkpoint (by validation macro-F1 on cfg.select_domains)."""
    started = time.time()
    amp = device == "cuda"
    sampler = EpochSampler(len(train_ds), seed)
    drop_last = len(train_ds) % cfg.batch_size == 1  # a final batch of one sample breaks BatchNorm
    loader = make_loader(train_ds, cfg.batch_size, sampler=sampler, num_workers=num_workers, drop_last=drop_last,
                         pin_memory=device == "cuda", mp_context=mp_context)
    micro_steps = len(loader)
    steps_per_epoch = math.ceil(micro_steps / cfg.grad_accum)
    select_mask = np.isin(np.asarray(val_set.domains), cfg.select_domains)
    if not select_mask.any():
        raise ExperimentError(f"{cfg.exp_id}: the validation part has no images of the domains {cfg.select_domains}")
    scaler = torch.amp.GradScaler("cuda", enabled=amp)
    selector = CheckpointSelector(cfg.patience)
    history: list[dict] = []
    epoch = 0
    stopped_early = False
    head_params = head_parameters(model)

    for stage, n_epochs in (("lp", cfg.stage1_epochs), ("ft", cfg.epochs)):
        if n_epochs <= 0:
            continue
        trainable = head_params if stage == "lp" else list(model.parameters())
        for p in model.parameters():
            p.requires_grad_(False)
        for p in trainable:
            p.requires_grad_(True)
        base_lr = cfg.stage1_lr if stage == "lp" else cfg.lr
        optimizer = torch.optim.AdamW(trainable, lr=base_lr, weight_decay=cfg.weight_decay)
        total_steps = n_epochs * steps_per_epoch
        warmup_steps = cfg.warmup_epochs * steps_per_epoch if stage == "ft" else 0
        step = 0
        for _ in range(n_epochs):
            epoch += 1
            epoch_started = time.time()
            sampler.set_epoch(epoch - 1)
            train_ds.epoch = epoch - 1
            model.train() if stage == "ft" else model.eval()  # LP: frozen backbone incl. BatchNorm statistics
            if stage == "lp":
                head_module(model).train()
            loss_sum, seen, lr_now = 0.0, 0, base_lr
            optimizer.zero_grad(set_to_none=True)
            for i, (images, labels, _) in enumerate(loader):
                x = normalize_batch(images, device)
                y = labels.to(device)
                with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=amp):
                    loss = F.cross_entropy(model(x), y, label_smoothing=cfg.label_smoothing)
                loss_value = loss.item()
                if not math.isfinite(loss_value):
                    raise ExperimentError(f"{cfg.exp_id}: the training loss became {loss_value} (diverged); try a lower lr")
                scaler.scale(loss / cfg.grad_accum).backward()
                loss_sum += loss_value * len(y)
                seen += len(y)
                if (i + 1) % cfg.grad_accum == 0 or i + 1 == micro_steps:
                    lr_now = base_lr if stage == "lp" else lr_at_step(step, base_lr=base_lr, warmup_steps=warmup_steps,
                                                                    total_steps=total_steps)
                    for group in optimizer.param_groups:
                        group["lr"] = lr_now
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(trainable, cfg.clip_norm)
                    scaler.step(optimizer)
                    scaler.update()
                    optimizer.zero_grad(set_to_none=True)
                    step += 1
            probs = predict_probs(model, val_set.images, device, amp=amp)
            preds, labels_np = probs.argmax(axis=1), val_set.labels
            domains = np.asarray(val_set.domains)
            score = macro_f1(labels_np[select_mask], preds[select_mask])
            improved = selector.update(score, epoch, lambda: cpu_state_dict(model), counts_for_patience=stage == "ft")
            row = {
                "epoch": epoch, "stage": stage, "lr": lr_now, "train_loss": loss_sum / max(1, seen),
                "val_loss": float(-np.log(np.clip(probs[np.arange(len(labels_np)), labels_np], 1e-8, 1.0)).mean()),
                "val_macro_f1": score,
                "val_accuracy": float((preds[select_mask] == labels_np[select_mask]).mean()),
                "val_f1_white": macro_f1(labels_np[domains == "white"], preds[domains == "white"]),
                "val_f1_field": macro_f1(labels_np[domains == "field"], preds[domains == "field"]),
                "val_f1_mixed": macro_f1(labels_np, preds),
                "best": int(improved), "seconds": time.time() - epoch_started,
            }
            history.append(row)
            log(f"  epoch {epoch:2d}/{cfg.stage1_epochs + cfg.epochs} {stage}  lr {lr_now:.2e}  loss {row['train_loss']:.3f}  "
                f"val F1 {score:.3f}{' *' if improved else '  '} (white {row['val_f1_white']:.3f} field {row['val_f1_field']:.3f})  "
                f"{row['seconds']:.1f}s")
            if stage == "ft" and selector.should_stop:
                stopped_early = True
                log(f"  early stop: no improvement for {cfg.patience} fine-tuning epochs (best epoch {selector.best_epoch})")
                break
    return TrainOutcome(selector.best_state, selector.best_epoch, selector.best_score, history, stopped_early,
                        time.time() - started)

import io

RUN_FORMAT = 1
FINGERPRINT_IGNORED = ("batch_size", "grad_accum")
RUN_FILES = ("config.json", "env.json", "history.csv", "predictions_val.csv", "predictions_test.csv", "metrics.json")


def runs_dir(data_root) -> Path:
    return work_dir(data_root) / "runs"


def sweep_dir(data_root) -> Path:
    return runs_dir(data_root) / "sweep"


def scratch_dir(data_root) -> Path:
    return runs_dir(data_root) / "scratch"


def lr_tag(lr: float) -> str:
    """1e-4 -> '1e-4', 3e-4 -> '3e-4' (used in sweep folder names)."""
    return f"{lr:.0e}".replace("e-0", "e-").replace("e+0", "e+")


def sweep_run_name(exp_id: str, lr: float) -> str:
    return f"{exp_id}_lr{lr_tag(lr)}"


def split_dir(root: Path, split_seed: int) -> Path:
    return Path(root) / f"split_{split_seed}"


def config_fingerprint(cfg: ExperimentConfig, extra: dict | None = None) -> str:
    payload = {k: v for k, v in asdict(cfg).items() if k not in FINGERPRINT_IGNORED}
    payload.update(extra or {})
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def environment_record(device: str) -> dict:
    import numpy
    import sklearn

    info = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "torch": torch.__version__,
        "torchvision": torchvision.__version__,
        "opencv": cv2.__version__,
        "numpy": numpy.__version__,
        "sklearn": sklearn.__version__,
        "device": device,
        "cpu_count": os.cpu_count(),
        "torch_home": os.environ.get("TORCH_HOME", ""),
        "gpu": None,
        "cuda": torch.version.cuda,
    }
    if device == "cuda":
        info["gpu"] = torch.cuda.get_device_name(0)
    elif device == "mps":
        info["gpu"] = "Apple MPS"
    return info


def fmt3(value) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def csv_text(header: list[str], rows) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue()


HISTORY_COLUMNS = ["epoch", "stage", "lr", "train_loss", "val_loss", "val_macro_f1", "val_accuracy",
                   "val_f1_white", "val_f1_field", "val_f1_mixed", "best", "seconds"]


def history_csv(history: list[dict]) -> str:
    return csv_text(HISTORY_COLUMNS, [[f"{row[c]:.6g}" if isinstance(row[c], float) else row[c] for c in HISTORY_COLUMNS] for row in history])


def predictions_csv(eval_set: EvalSet, probs: np.ndarray) -> str:
    preds = probs.argmax(axis=1)
    rows = [
        [name, domain, CLASS_NAMES[int(true)], CLASS_NAMES[int(pred)], *[f"{p:.6f}" for p in row]]
        for name, domain, true, pred, row in zip(eval_set.names, eval_set.domains, eval_set.labels, preds, probs)
    ]
    return csv_text(["filename", "domain", "true", "pred", *[f"p{i}" for i in range(NUM_CLASSES)]], rows)


def save_torch_atomic(obj, path: Path) -> None:
    path = Path(path)
    os.makedirs(fs_path(path.parent), exist_ok=True)
    tmp = path.with_name(path.name + f".tmp{os.getpid()}")
    with open(fs_path(tmp), "wb") as handle:
        torch.save(obj, handle)
    os.replace(fs_path(tmp), fs_path(path))


def read_metrics(run_dir: Path) -> dict | None:
    path = Path(run_dir) / "metrics.json"
    if not path.is_file():
        return None
    try:
        return json.loads(read_file_bytes(path).decode("utf-8"))
    except ValueError:
        return None  # atomic writes make this impossible in practice; treat as "not done"


def result_state(run_dir: Path, split_sha256: str, fingerprint: str) -> tuple[str, str]:
    """('fresh' | 'stale' | 'missing', reason) for the metrics.json of a run folder."""
    metrics = read_metrics(run_dir)
    if metrics is None:
        return "missing", "no metrics.json"
    if metrics.get("split_sha256") != split_sha256:
        return "stale", "the split changed since this run (split sha256 differs)"
    if metrics.get("config_fingerprint") != fingerprint:
        return "stale", "the experiment config changed since this run (config fingerprint differs)"
    return "fresh", "metrics.json is current"


def make_extra_sources(cfg: ExperimentConfig, data_root, split_seed: int, seed: int) -> tuple:
    """Extra training samples. PHASE 05 REPLACES THIS BODY: return (CompositeSource(split_seed, n_per_epoch, seed),)
    when ``cfg.use_composites``."""
    if cfg.use_composites:
        raise NotReadyError(
            f"{cfg.exp_id} trains with copy-paste composites (Method A), which need phase 05 "
            "(CompositeSource, docs/instructions/05-copy-paste-method-a.md)"
        )
    return ()


def make_input_hook(cfg: ExperimentConfig, data_root, split_seed: int):
    """``hook(image, record) -> image`` applied before the transforms. PHASE 06 REPLACES THIS BODY: return the
    segmentation-crop hook when ``cfg.seg_crop``. ``record`` is None for ad-hoc images (the predict command)."""
    if cfg.seg_crop:
        raise NotReadyError(
            f"{cfg.exp_id} crops to the segmented leaf (Method B), which needs phase 06 "
            "(docs/instructions/06-segmentation-method-b.md)"
        )
    return None


def check_cache_complete(data_root, records: list[Record]) -> None:
    missing = [r.filename for r in records if not (cache_dir(data_root) / r.filename).is_file()]
    if missing:
        raise DatasetError(f"{len(missing)} cached images are missing under {cache_dir(data_root)}, e.g. {missing[:3]}; run `prepare`")

@dataclass(frozen=True)
class RunOptions:
    """How to run (as opposed to what to run): nothing here changes the experiment's result definition."""

    device: str = "cpu"
    seed_offset: int = 0
    num_workers: int | None = None  # None: default_num_workers()
    force: bool = False
    limit: int | None = None  # --fast: at most this many images per split part
    overrides: tuple = ()  # (name, value) pairs applied on top of the registry, recorded in config.json
    weights_root: Path | None = None  # where the pretrained weights live (default: the data root)
    mp_context: str | None = None  # tests only: force the worker start method


def train_with_fallback(cfg, train_ds, val_set, options: RunOptions, seed: int, log):
    """Build a fresh model and train it; on out-of-memory retry once with batch 16 and accumulation x2
    (same effective batch). Returns (model, outcome, cfg actually used)."""
    workers = default_num_workers() if options.num_workers is None else options.num_workers
    while True:
        try:
            seed_everything(seed)
            model = build_model(cfg.backbone, pretrained=cfg.pretrained, dropout=cfg.dropout,
                                data_root=options.weights_root).to(options.device)
            outcome = train_classifier(cfg, model, train_ds, val_set, options.device, seed=seed, num_workers=workers,
                                       mp_context=options.mp_context, log=log)
            return model, outcome, cfg
        except Exception as exc:
            if not (is_out_of_memory(exc) and cfg.batch_size > FALLBACK_BATCH):
                raise
            model = None
            log(f"  out of memory at batch {cfg.batch_size}: retrying with batch {FALLBACK_BATCH} and gradient accumulation "
                f"{cfg.grad_accum * cfg.batch_size // FALLBACK_BATCH}")
            cfg = replace(cfg, batch_size=FALLBACK_BATCH, grad_accum=cfg.grad_accum * cfg.batch_size // FALLBACK_BATCH)
        free_device_memory(options.device)


def run_split(resolved: "ResolvedExperiment", split_seed: int, *, data_root, out_dir: Path, options: RunOptions,
              log=print) -> dict:
    """Train and evaluate one experiment on one split and write the run folder (see the table above).

    Returns {"status": "skipped" | "done", "metrics": dict, "out_dir": Path}."""
    data_root, out_dir = Path(data_root), Path(out_dir)
    cfg = resolved.config
    split = load_split(data_root, split_seed)  # verifies the sha256
    fingerprint = config_fingerprint(cfg, {"seed_offset": options.seed_offset, "limit": options.limit})
    state, reason = result_state(out_dir, split["sha256"], fingerprint)
    if state == "fresh" and not options.force:
        log(f"[{resolved.requested} split {split_seed}] skipped: {out_dir / 'metrics.json'} exists and is current (--force to retrain)")
        return {"status": "skipped", "metrics": read_metrics(out_dir), "out_dir": out_dir}
    if state == "stale":
        log(f"[{resolved.requested} split {split_seed}] existing result is stale: {reason}; retraining")
    (out_dir / "metrics.json").unlink(missing_ok=True)  # a half-finished retrain must not look complete

    started = time.time()
    seed = split_seed + options.seed_offset
    records = load_index(data_root)
    train_recs = select_records(records, split["train"], cfg.train_domains)
    val_recs = select_records(records, split["val"])
    test_recs = select_records(records, split["test"])
    if options.limit:
        train_recs, val_recs, test_recs = (subsample_records(r, options.limit) for r in (train_recs, val_recs, test_recs))
    check_cache_complete(data_root, [*train_recs, *val_recs, *test_recs])

    extra_sources = make_extra_sources(cfg, data_root, split_seed, seed)
    input_hook = make_input_hook(cfg, data_root, split_seed)
    train_tf = ImageTransform(cfg.input_mode, train=True, size_div=cfg.size_div)
    eval_tf = ImageTransform(cfg.input_mode, train=False, size_div=cfg.size_div)
    train_ds = LeafDataset(data_root, train_recs, train_tf, seed=seed, extra_sources=extra_sources, input_hook=input_hook)
    workers = default_num_workers() if options.num_workers is None else options.num_workers
    val_set = materialize(LeafDataset(data_root, val_recs, eval_tf, input_hook=input_hook), num_workers=workers)

    log(f"[{resolved.requested} split {split_seed}] {cfg.exp_id}: {cfg.backbone} / {cfg.input_mode}  lr {cfg.lr:g}  "
        f"train {len(train_ds)} ({'+'.join(cfg.train_domains)}), val {len(val_set)}, test {len(test_recs)}  "
        f"device {options.device}, batch {cfg.batch_size}x{cfg.grad_accum}, workers {usable_workers(workers)}")
    write_json(out_dir / "config.json", {
        "format": RUN_FORMAT, "requested_exp_id": resolved.requested, "experiment": asdict(cfg),
        "split": split_seed, "seed": seed, "seed_offset": options.seed_offset, "limit": options.limit,
        "choices_used": resolved.choices_used, "notes": list(resolved.notes), "overrides": dict(options.overrides),
        "weights": BACKBONE_SPECS[cfg.backbone].weights if cfg.pretrained else None,
        "input_size": list(input_size(cfg.input_mode, cfg.size_div)), "config_fingerprint": fingerprint,
    })
    write_json(out_dir / "env.json", environment_record(options.device))

    model, outcome, used_cfg = train_with_fallback(cfg, train_ds, val_set, options, seed, log)
    model.load_state_dict(outcome.best_state)
    amp = options.device == "cuda"
    val_metrics, val_probs = evaluate_model(model, val_set, options.device, amp=amp)
    test_set = materialize(LeafDataset(data_root, test_recs, eval_tf, input_hook=input_hook), num_workers=workers)
    test_metrics, test_probs = evaluate_model(model, test_set, options.device, amp=amp)

    write_text_atomic(out_dir / "history.csv", history_csv(outcome.history))
    write_text_atomic(out_dir / "predictions_val.csv", predictions_csv(val_set, val_probs))
    write_text_atomic(out_dir / "predictions_test.csv", predictions_csv(test_set, test_probs))
    save_torch_atomic({
        "format": RUN_FORMAT, "state_dict": outcome.best_state, "backbone": cfg.backbone, "input_mode": cfg.input_mode,
        "size_div": cfg.size_div, "dropout": cfg.dropout, "class_names": list(CLASS_NAMES), "epoch": outcome.best_epoch,
        "val_select_macro_f1": outcome.best_score, "exp_id": cfg.exp_id, "split": split_seed, "config": asdict(cfg),
    }, out_dir / "best.pt")
    epoch_seconds = [row["seconds"] for row in outcome.history]
    metrics = {
        "format": RUN_FORMAT, "exp_id": cfg.exp_id, "requested_exp_id": resolved.requested, "split": split_seed,
        "seed": seed, "split_sha256": split["sha256"], "config_fingerprint": fingerprint,
        "wall_time_s": round(time.time() - started, 2), "train_time_s": round(outcome.seconds, 2),
        "seconds_per_epoch": round(float(np.mean(epoch_seconds)), 3) if epoch_seconds else None,
        "device": options.device, "backbone": cfg.backbone, "input_mode": cfg.input_mode, "lr": cfg.lr,
        "parameters": count_parameters(model), "train_domains": list(cfg.train_domains),
        "select_domains": list(cfg.select_domains), "test_subsets": list(cfg.test_subsets),
        "n_train": len(train_ds), "n_val": len(val_set), "n_test": len(test_set),
        "epochs_run": len(outcome.history), "best_epoch": outcome.best_epoch,
        "best_val_select_macro_f1": outcome.best_score, "stopped_early": outcome.stopped_early,
        "batch_size": used_cfg.batch_size, "grad_accum": used_cfg.grad_accum,
        "oom_fallback": used_cfg.batch_size != cfg.batch_size, "fast": options.limit is not None,
        "overrides": dict(options.overrides), "val": val_metrics, "test": test_metrics,
    }
    write_json(out_dir / "metrics.json", metrics, indent=1)  # last: its presence marks the run as complete
    log(f"[{resolved.requested} split {split_seed}] done in {metrics['wall_time_s']:.0f}s  best epoch {outcome.best_epoch}  "
        f"val mixed F1 {fmt3(val_metrics['mixed']['macro_f1'])}  test F1 mixed {fmt3(test_metrics['mixed']['macro_f1'])} "
        f"white {fmt3(test_metrics['white']['macro_f1'])} field {fmt3(test_metrics['field']['macro_f1'])}")
    return {"status": "done", "metrics": metrics, "out_dir": out_dir}

def load_run_model(run_dir, device: str = "cpu") -> tuple[nn.Module, dict]:
    """(model in eval mode on ``device``, checkpoint dict) from <run_dir>/best.pt."""
    path = Path(run_dir) / "best.pt"
    if not path.is_file():
        raise ExperimentError(
            f"{path} does not exist. Checkpoints are not synced back from Colab by default "
            "(*.pt is excluded): re-run the batch with keep_checkpoints=True, or copy best.pt from the Colab session."
        )
    checkpoint = torch.load(fs_path(path), map_location="cpu", weights_only=True)
    model = build_model(checkpoint["backbone"], pretrained=False, dropout=checkpoint["dropout"])
    model.load_state_dict(checkpoint["state_dict"])
    return model.to(device).eval(), checkpoint


def read_image_like_the_cache(path) -> np.ndarray:
    """An arbitrary JPEG as the classifier saw its training images: EXIF applied, portrait, long side <= 1280."""
    return resize_long_side(read_rgb(path), CACHE_LONG_SIDE)


def classify_rgb(model: nn.Module, checkpoint: dict, rgb: np.ndarray, device: str, input_hook=None) -> np.ndarray:
    """Class probabilities [5] of one RGB image under the evaluation pipeline of the checkpoint's experiment."""
    if input_hook is not None:
        rgb = input_hook(rgb, None)
    transform = ImageTransform(checkpoint["input_mode"], train=False, size_div=checkpoint["size_div"])
    batch = torch.from_numpy(np.ascontiguousarray(transform(rgb).transpose(2, 0, 1)))[None]
    return predict_probs(model, batch, device)[0]


def format_prediction(image, probs: np.ndarray, label: str) -> str:
    order = np.argsort(-probs)
    lines = [f"image       {image}", f"model       {label}", f"prediction  {CLASS_NAMES[order[0]]} ({100 * probs[order[0]]:.1f}%)", "probabilities"]
    lines += [f"  {CLASS_NAMES[i]:<14}{100 * probs[i]:5.1f}%  {'#' * round(40 * probs[i])}" for i in order]
    return "\n".join(lines)


def predict_image(run_dir, image, device: str, data_root=None, out=print) -> np.ndarray:
    model, checkpoint = load_run_model(run_dir, device)
    cfg = ExperimentConfig(**checkpoint["config"])
    hook = make_input_hook(cfg, data_root, checkpoint["split"]) if cfg.seg_crop else None
    probs = classify_rgb(model, checkpoint, read_image_like_the_cache(image), device, hook)
    out(format_prediction(image, probs, f"{checkpoint['exp_id']} split {checkpoint['split']} ({Path(run_dir) / 'best.pt'})"))
    return probs

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

import difflib

CHOICES_FILENAME = "choices.json"
SWEEP_LRS = (1e-4, 3e-4)  # T3.4: split-0 learning-rate sweep
# Experiment whose split-0 run is swept for each backbone (04: ResNet50 on rect, the others on their U row).
SWEEP_EXPERIMENT = {"resnet50": "E0-rect", "convnext_tiny": "E2-cnx-U", "swin_t": "E2-swin-U"}
# Used by `--fast` when choices.json does not exist yet, so that every experiment ID can be sanity-checked.
FAST_PLACEHOLDERS = {"input_mode": "rect", "backbone": "resnet50", "lr": 3e-4}
CHOICE_SOURCES = {
    "input_mode": 'the winning E0 input mode ("best of E0"), written by gate G0 (phase 04, Batch 1)',
    "backbone": 'the winning backbone ("best of E2"), written by gate G1 (phase 04, Batch 3)',
    "lr": "the learning rate of this backbone, written by `choose-lr --backbone NAME` after the split-0 sweep "
    "(`run --exp <ID> --sweep-lr`)",
}


def choices_path(data_root) -> Path:
    return results_dir(data_root) / CHOICES_FILENAME


@dataclass(frozen=True)
class Choices:
    """The contents of choices.json plus its path (for error messages)."""

    path: Path
    data: dict

    def raw(self, key: str, sub: str | None = None):
        entry = self.data.get(key)
        if sub is not None:
            entry = entry.get(sub) if isinstance(entry, dict) else None
        if isinstance(entry, dict) and "value" in entry:
            entry = entry["value"]
        return entry

    def get(self, key: str, sub: str | None = None):
        """The validated choice, or ChoicesError that says which step writes it."""
        value = self.raw(key, sub)
        label = key if sub is None else f"{key}[{sub}]"
        if value is None:
            where = f"{self.path} does not exist" if not self.path.is_file() else f"{self.path} has no such entry"
            raise ChoicesError(f"{where} (needed: {label}). It holds {CHOICE_SOURCES[key]}. Schema: see 90_cli.ipynb.")
        valid = {
            "input_mode": lambda v: v in INPUT_MODES,
            "backbone": lambda v: v in BACKBONES,
            "lr": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and 0 < v < 1,
        }[key]
        if not valid(value):
            options = {"input_mode": INPUT_MODES, "backbone": BACKBONES, "lr": "a number in (0, 1)"}[key]
            raise ChoicesError(f"{self.path}: invalid {label} = {value!r} (expected {options})")
        return float(value) if key == "lr" else value


def load_choices(data_root) -> Choices:
    path = choices_path(data_root)
    if not path.is_file():
        return Choices(path, {})
    try:
        data = json.loads(read_file_bytes(path).decode("utf-8"))
    except ValueError as exc:
        raise ChoicesError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ChoicesError(f"{path}: expected a JSON object at the top level")
    return Choices(path, data)


def write_choice(data_root, key: str, value, evidence=None, *, sub: str | None = None) -> Path:
    """Set choices[key] (or choices[key][sub]) to {"value": value, "evidence": evidence}, keeping the rest."""
    choices = load_choices(data_root)
    data = dict(choices.data)
    entry = {"value": value, "evidence": evidence if evidence is not None else {}}
    if sub is None:
        data[key] = entry
    else:
        group = dict(data[key]) if isinstance(data.get(key), dict) else {}
        group[sub] = entry
        data[key] = group
    write_json(choices.path, data, indent=2)
    return choices.path


def _row(exp_id: str, backbone, train, test_subsets, **kwargs) -> ExperimentConfig:
    train = tuple(train)
    return ExperimentConfig(
        exp_id=exp_id,
        backbone=backbone,
        train_domains=train,
        select_domains=train,
        test_subsets=tuple(test_subsets),
        input_mode=kwargs.pop("input_mode", None),
        **kwargs,
    )


_U, _W, _F = DOMAINS, ("white",), ("field",)
_ALL3 = ("white", "field", "mixed")
_WF_TEST = ("field", "white")  # field is the main result of a W->F row, white the reference

_ROWS = (
    # E0: input-size ablation, ResNet50 on white + field, equal pixel budget.
    _row("E0-squash", "resnet50", _U, _ALL3, input_mode="squash", note="320x320, aspect distorted"),
    _row("E0-pad", "resnet50", _U, _ALL3, input_mode="pad", note="320x320 letterbox"),
    _row("E0-rect", "resnet50", _U, _ALL3, input_mode="rect", note="448x224 (HxW)"),
    # E1: ResNet50 baseline and domain experiments at the winning E0 input mode.
    _row("E1-U", "resnet50", _U, _ALL3, alias_of_winner="E0", note="alias of the winning E0 row, no retraining"),
    _row("E1-WW", "resnet50", _W, ("white",), note="train white, test white"),
    _row("E1-FF", "resnet50", _F, ("field",), note="train field, test field"),
    _row("E1-WF", "resnet50", _W, _WF_TEST, note="train white, test field (cross-domain)"),
    # E2: ConvNeXt-T and Swin-T.
    _row("E2-cnx-U", "convnext_tiny", _U, _ALL3),
    _row("E2-cnx-WF", "convnext_tiny", _W, _WF_TEST),
    _row("E2-swin-U", "swin_t", _U, _ALL3),
    _row("E2-swin-WF", "swin_t", _W, _WF_TEST),
    # Later phases: runnable only once their hooks exist.
    _row("E3-A", None, _U, _ALL3, use_composites=True, note="Method A (phase 05): composites as extra training samples"),
    _row("E3-A-WF", None, _W, _WF_TEST, use_composites=True, note="white + composites; field images are only backgrounds"),
    _row("S-seg", "lraspp_mobilenet_v3_large", _U, (), kind="segmenter", note="leaf segmenter (phase 06)"),
    _row("E4-B", None, _U, _ALL3, seg_crop=True, note="Method B (phase 06): segment, crop, classify"),
    _row("X-domain-WW", None, _W, ("white",), note="best backbone, train white, test white"),
    _row("X-domain-FF", None, _F, ("field",), note="best backbone, train field, test field"),
    _row("X-gradcam", None, _U, (), kind="analysis", note="Grad-CAM shortcut analysis (phase 07), see the gradcam command"),
)
EXPERIMENTS: dict[str, ExperimentConfig] = {row.exp_id: row for row in _ROWS}
# `run --exp <GROUP>` runs every member in order.
EXPERIMENT_GROUPS = {
    "E0": ("E0-squash", "E0-pad", "E0-rect"),
    "E1": ("E1-U", "E1-WW", "E1-FF", "E1-WF"),
    "E2": ("E2-cnx-U", "E2-cnx-WF", "E2-swin-U", "E2-swin-WF"),
    "X-domain": ("X-domain-WW", "X-domain-FF"),
}
NON_CLASSIFIER_MESSAGE = {
    "segmenter": "is the leaf segmenter, trained by the segmentation pipeline of phase 06 (06-segmentation-method-b.md)",
    "analysis": "is a Grad-CAM analysis, produced by the `gradcam` command of phase 07 (07-analysis.md)",
}


def run_folder_name(exp_id: str, choices: Choices) -> str:
    """Folder (under runs/) that holds the results of an experiment ID: itself, except for the E1-U alias."""
    if exp_id not in EXPERIMENTS:
        expand_experiment_ids(exp_id)  # raises with suggestions
    base = EXPERIMENTS[exp_id]
    return f"{base.alias_of_winner}-{choices.get('input_mode')}" if base.alias_of_winner else exp_id


def expand_experiment_ids(text: str) -> list[str]:
    """'E0' -> its three rows; 'E1-U,E1-WW' -> two rows. Unknown IDs raise UnknownExperimentError."""
    ids: list[str] = []
    for part in (p.strip() for p in text.split(",") if p.strip()):
        for exp_id in EXPERIMENT_GROUPS.get(part, (part,)):
            if exp_id not in EXPERIMENTS:
                close = difflib.get_close_matches(exp_id, [*EXPERIMENTS, *EXPERIMENT_GROUPS], n=3)
                hint = f" Did you mean: {', '.join(close)}?" if close else ""
                raise UnknownExperimentError(
                    f"unknown experiment {exp_id!r}.{hint} Known: {', '.join([*EXPERIMENTS, *EXPERIMENT_GROUPS])}"
                )
            if exp_id not in ids:
                ids.append(exp_id)
    if not ids:
        raise UnknownExperimentError("no experiment ID given")
    return ids


@dataclass(frozen=True)
class ResolvedExperiment:
    config: ExperimentConfig  # fully concrete: backbone, input_mode and lr are set
    requested: str  # the ID that was asked for (differs from config.exp_id for the E1-U alias)
    choices_used: dict  # which values came from choices.json (or FAST placeholders), for config.json
    notes: tuple[str, ...] = ()


def resolve_experiment(
    exp_id: str, choices: Choices, *, lr: float | None = None, placeholders: bool = False
) -> ResolvedExperiment:
    """Turn a registry entry into a concrete config.

    ``lr`` overrides the choices.json learning rate (sweeps, ``--lr``). ``placeholders=True`` (``--fast``)
    substitutes FAST_PLACEHOLDERS for choices that do not exist yet, and says so in ``notes``.
    """
    if exp_id not in EXPERIMENTS:
        expand_experiment_ids(exp_id)  # raises with a helpful message
    base = EXPERIMENTS[exp_id]
    if base.kind != "classifier":
        raise NotReadyError(f"{exp_id} {NON_CLASSIFIER_MESSAGE[base.kind]}; it cannot be run as a classifier")
    used: dict = {}
    notes: list[str] = []

    def pick(key: str, sub: str | None = None):
        label = key if sub is None else f"{key}[{sub}]"
        try:
            value = choices.get(key, sub)
            used[label] = value
            return value
        except ChoicesError as exc:
            if not placeholders:
                raise ChoicesError(f"{exp_id}: {exc}") from None
            value = FAST_PLACEHOLDERS[key]
            used[label] = value
            notes.append(f"--fast: no choice for {label}, using the placeholder {value!r}")
            return value

    if base.alias_of_winner:
        mode = pick("input_mode")
        inner = resolve_experiment(f"{base.alias_of_winner}-{mode}", choices, lr=lr, placeholders=placeholders)
        note = f"{exp_id} is an alias of {inner.config.exp_id} (the winning input mode): same run folder, no retraining"
        return ResolvedExperiment(inner.config, exp_id, {**inner.choices_used, **used}, (note, *inner.notes, *notes))

    backbone = base.backbone if base.backbone is not None else pick("backbone")
    mode = base.input_mode if base.input_mode is not None else pick("input_mode")
    if lr is None:
        lr = base.lr if base.lr is not None else pick("lr", backbone)
    config = replace(base, backbone=backbone, input_mode=mode, lr=lr)
    return ResolvedExperiment(config, exp_id, used, tuple(notes))

def cmd_download_weights(args: argparse.Namespace) -> int:
    try:
        download_weights(Path(args.data_root))
    except (ExperimentError, OSError) as exc:
        print(f"download-weights: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE
    return EXIT_OK

FAST_CONFIG = {"stage1_epochs": 1, "epochs": 1, "size_div": 4, "batch_size": 8}
FAST_IMAGES = 24


def pretrained_available(backbone: str, data_root) -> bool:
    """True if the pretrained file is already stored under <data_root>/_work/weights (no download is triggered)."""
    previous = os.environ.get("TORCH_HOME")
    try:
        set_torch_home(data_root, create=False)
        return weight_file_ok(weight_checkpoint_path(backbone_weights(backbone)))
    finally:
        if previous is None:
            os.environ.pop("TORCH_HOME", None)
        else:
            os.environ["TORCH_HOME"] = previous


def run_destination(data_root, args, cfg: ExperimentConfig, dev: bool) -> tuple[Path, str]:
    """(root folder, run name) for one resolved config; see the table in the notebook."""
    if args.out_dir:
        root = Path(args.out_dir)
    elif dev:
        root = scratch_dir(data_root)
    else:
        root = sweep_dir(data_root) if args.sweep_lr else runs_dir(data_root)
    if args.sweep_lr:
        return root, sweep_run_name(cfg.exp_id, cfg.lr)
    suffix = "" if args.out_dir or not dev else "_fast" if args.fast else "_dev"
    return root, cfg.exp_id + suffix


def apply_run_flags(args, resolved: ResolvedExperiment, data_root) -> tuple[ResolvedExperiment, dict, int | None]:
    """Apply --fast and the dev/system overrides to a resolved experiment. Returns (resolved, overrides, limit)."""
    changes: dict = {}
    overrides: dict = {}
    limit = None
    if args.fast:
        changes.update(FAST_CONFIG)
        changes["pretrained"] = pretrained_available(resolved.config.backbone, data_root)
        overrides["fast"] = True
        limit = FAST_IMAGES
    for flag, field_name in (("epochs", "epochs"), ("stage1_epochs", "stage1_epochs"), ("lr", "lr")):
        value = getattr(args, flag, None)
        if value is not None:
            changes[field_name] = value
            overrides[flag] = value
    for flag in ("batch_size", "grad_accum"):
        value = getattr(args, flag, None)
        if value is not None:
            changes[flag] = value
    notes = resolved.notes
    if args.fast and not changes["pretrained"]:
        notes = (*notes, f"--fast: {resolved.config.backbone} weights are not downloaded, using random initialisation")
    return replace(resolved, config=replace(resolved.config, **changes), notes=notes), overrides, limit


def run_command(args) -> int:
    data_root = Path(args.data_root)
    choices = load_choices(data_root)
    device = resolve_device(args.device)
    ids = expand_experiment_ids(args.exp)
    sweep = args.sweep_lr
    if sweep and args.lr is not None:
        raise ExperimentError("--sweep-lr already sets the learning rates (1e-4 and 3e-4); do not combine it with --lr")
    splits = (0,) if sweep else tuple(args.splits)
    if sweep and tuple(args.splits) != DEFAULT_SPLITS and tuple(args.splits) != (0,):
        print("run: note - --sweep-lr always uses split 0 only (T3.4 rule)")
    dev = bool(args.fast or args.lr is not None or args.epochs is not None or args.stage1_epochs is not None)
    options_base = dict(device=device, seed_offset=args.seed_offset, num_workers=args.num_workers, force=args.force,
                        weights_root=data_root)
    weights_home = set_torch_home(data_root)
    print(f"run: device {device}, data root {data_root}, TORCH_HOME {weights_home}")
    summary = []
    for exp_id in ids:
        for sweep_lr in (SWEEP_LRS if sweep else (None,)):
            resolved = resolve_experiment(exp_id, choices, lr=sweep_lr if sweep else args.lr, placeholders=args.fast)
            resolved, overrides, limit = apply_run_flags(args, resolved, data_root)
            cfg = resolved.config
            if sweep and cfg.exp_id != SWEEP_EXPERIMENT.get(cfg.backbone):
                print(f"run: note - choose-lr reads the sweep of {SWEEP_EXPERIMENT.get(cfg.backbone)} for {cfg.backbone}, not {cfg.exp_id}")
            root, name = run_destination(data_root, args, cfg, dev)
            for note in resolved.notes:
                print(f"run: {note}")
            print(f"run: {resolved.requested} -> {root / name}/split_<k>/" + ("  (sweep, never a result)" if sweep else "  (scratch, never a result)" if dev else ""))
            options = RunOptions(limit=limit, overrides=tuple(overrides.items()), **options_base)
            for split_seed in splits:
                result = run_split(resolved, split_seed, data_root=data_root, out_dir=split_dir(root / name, split_seed),
                                   options=options, log=lambda text: print(text, flush=True))
                metrics = result["metrics"]
                summary.append((name, split_seed, result["status"], metrics["val"]["mixed"]["macro_f1"], metrics["test"]["mixed"]["macro_f1"]))
    print("run: summary (macro-F1)")
    print(f"  {'run':<22}{'split':>5}  {'status':<8}{'val mixed':>10}{'test mixed':>11}")
    for name, split_seed, status, val_f1, test_f1 in summary:
        print(f"  {name:<22}{split_seed:>5}  {status:<8}{fmt3(val_f1):>10}{fmt3(test_f1):>11}")
    return EXIT_OK


def cmd_run(args: argparse.Namespace) -> int:
    try:
        return run_command(args)
    except (ExperimentError, DatasetError) as exc:
        print(f"run: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE


def choose_lr(data_root, backbone: str, out=print) -> dict:
    """T3.4 rule: of the two split-0 sweep runs, take the lr with the higher validation mixed macro-F1."""
    if backbone not in SWEEP_EXPERIMENT:
        raise ExperimentError(f"unknown backbone {backbone!r}, expected one of {', '.join(SWEEP_EXPERIMENT)}")
    exp_id = SWEEP_EXPERIMENT[backbone]
    scores, shas = {}, set()
    for lr in SWEEP_LRS:
        run_dir = split_dir(sweep_dir(data_root) / sweep_run_name(exp_id, lr), 0)
        metrics = read_metrics(run_dir)
        if metrics is None:
            raise ExperimentError(f"missing sweep result {run_dir / 'metrics.json'}; run `run --exp {exp_id} --sweep-lr` first")
        if metrics.get("fast") or metrics.get("overrides"):
            raise ExperimentError(f"{run_dir} is a --fast / dev-override run, not a real sweep run; re-run the sweep without those flags")
        if metrics.get("backbone") != backbone or abs(metrics.get("lr", -1) - lr) > 1e-12:
            raise ExperimentError(f"{run_dir}: expected backbone {backbone} at lr {lr}, found {metrics.get('backbone')} at {metrics.get('lr')}")
        scores[lr] = metrics["val"]["mixed"]["macro_f1"]
        shas.add(metrics["split_sha256"])
    if len(shas) != 1:
        raise ExperimentError("the two sweep runs used different splits; re-run both")
    best = max(SWEEP_LRS, key=lambda lr: (scores[lr], -lr))  # ties: the smaller lr
    evidence = {
        "experiment": exp_id, "split": 0, "split_sha256": shas.pop(),
        "val_mixed_macro_f1": {lr_tag(lr): scores[lr] for lr in SWEEP_LRS},
        "rule": "higher validation mixed macro-F1 on split 0; ties go to the smaller lr",
    }
    path = write_choice(data_root, "lr", best, evidence, sub=backbone)
    out(f"choose-lr: {backbone}: " + ", ".join(f"lr {lr_tag(lr)} -> val mixed F1 {fmt3(scores[lr])}" for lr in SWEEP_LRS)
        + f"  =>  lr {lr_tag(best)}  (written to {path})")
    return {"lr": best, "evidence": evidence}


def cmd_choose_lr(args: argparse.Namespace) -> int:
    try:
        choose_lr(Path(args.data_root), args.backbone)
    except (ExperimentError, DatasetError) as exc:
        print(f"choose-lr: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE
    return EXIT_OK

def cmd_predict(args: argparse.Namespace) -> int:
    data_root = Path(args.data_root)
    try:
        if args.run_dir is not None:
            run_dir = Path(args.run_dir)
        else:
            choices = load_choices(data_root)
            exp_id = args.exp or choices.raw("recommended")
            if not exp_id:
                raise ExperimentError(
                    f"no --exp given and {choices.path} has no 'recommended' experiment (written by gate G2, phase 06). "
                    "Pass --exp ID, for example --exp E1-U, or --run-dir PATH"
                )
            run_dir = split_dir(runs_dir(data_root) / run_folder_name(exp_id, choices), args.split)
        if not Path(args.image).is_file():
            raise ExperimentError(f"image {args.image} does not exist")
        predict_image(run_dir, args.image, resolve_device(args.device), data_root)
    except (ExperimentError, DatasetError) as exc:
        print(f"predict: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE
    return EXIT_OK

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

def cmd_prepare(args: argparse.Namespace) -> int:
    """Index, cache, near-duplicate audit, splits, tables and figures (phase 02). Idempotent."""
    try:
        prepare_data(Path(args.data_root), workers=args.workers)
    except DatasetError as exc:
        print(f"prepare: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE
    return EXIT_OK


def smoke_split(selected: list[Record], seed: int = 0) -> dict:
    """A deterministic tiny split of the smoke images: every class x domain stratum contributes to train, and
    val / test get the other members alternately (the real splits need >= 7 images per stratum, the smoke
    images have ~2)."""
    parts: dict[str, list[str]] = {"train": [], "val": [], "test": []}
    by_stratum: dict = {}
    for record in sorted(selected, key=lambda r: r.filename):
        by_stratum.setdefault(record.stratum, []).append(record.filename)
    for (cls, domain), names in by_stratum.items():
        even = (CLASS_NAMES.index(cls) + DOMAINS.index(domain)) % 2 == 0
        cycle = ("train", "val" if even else "test", "test" if even else "val", "train")
        for k, name in enumerate(names):
            parts[cycle[k % 4]].append(name)
    train, val, test = (sorted(parts[key]) for key in ("train", "val", "test"))
    return {"seed": seed, "train": train, "val": val, "test": test, "sha256": split_sha256(seed, train, val, test)}


def classifier_smoke(data_root, tmp_root, selected: list[Record], log=print) -> None:
    """One tiny experiment (E0-rect, ResNet50, 1 epoch per stage, input size / 4) through the real `run` code
    path on CPU, with a complete run folder written under ``tmp_root``; then `predict` on one image of it."""
    started = time.time()
    write_index(tmp_root, selected)
    split = smoke_split(selected)
    smoke_require(all(split[k] for k in ("train", "val", "test")), "tiny split has an empty part")
    write_json(split_path(tmp_root, 0), split)
    resolved = resolve_experiment("E0-rect", Choices(choices_path(tmp_root), {}), lr=3e-4)
    pretrained = pretrained_available(resolved.config.backbone, data_root)
    resolved = replace(resolved, config=replace(resolved.config, pretrained=pretrained, **FAST_CONFIG))
    options = RunOptions(device="cpu", num_workers=2, weights_root=Path(data_root))
    run_dir = split_dir(tmp_root / WORK_DIRNAME / "runs" / "E0-rect_smoke", 0)
    lines: list[str] = []
    result = run_split(resolved, 0, data_root=tmp_root, out_dir=run_dir, options=options, log=lines.append)
    smoke_require(result["status"] == "done", "the tiny run did not train")
    for name in (*RUN_FILES, "best.pt"):
        smoke_require((run_dir / name).is_file(), f"run folder lacks {name}")
    smoke_require(not list(run_dir.glob("*.tmp*")), "temporary files left behind (non-atomic write)")
    metrics = read_metrics(run_dir)
    smoke_require(metrics["split_sha256"] == split["sha256"] and metrics["wall_time_s"] > 0, "metrics.json is incomplete")
    for part in ("val", "test"):
        with open(run_dir / f"predictions_{part}.csv", newline="") as handle:
            rows = list(csv.reader(handle))
        smoke_require(rows[0][:4] == ["filename", "domain", "true", "pred"] and len(rows) - 1 == len(split[part]),
                      f"predictions_{part}.csv has the wrong rows")
    again = run_split(resolved, 0, data_root=tmp_root, out_dir=run_dir, options=options, log=lines.append)
    smoke_require(again["status"] == "skipped", "a finished split was not skipped (idempotence)")
    image = Path(data_root) / selected[0].rel_path
    probs = predict_image(run_dir, image, "cpu", data_root, out=lambda text: None)
    smoke_require(probs.shape == (NUM_CLASSES,) and abs(float(probs.sum()) - 1.0) < 1e-4, "predict returned bad probabilities")
    log(f"smoke: OK - tiny {resolved.config.exp_id} run ({'pretrained' if pretrained else 'random'} weights, "
        f"{len(split['train'])}/{len(split['val'])}/{len(split['test'])} train/val/test images, workers 2): complete run folder, "
        f"skipped on rerun, predict OK ({time.time() - started:.0f} s)")


def cmd_smoke(args: argparse.Namespace) -> int:
    """Tiny end-to-end check: data root, image discovery, library imports, device, the data path (index, EXIF
    read, cache, dHash, splits, figures on ~20 images in a temp folder) and one tiny classifier experiment
    through the real `run` code path on CPU, followed by `predict` (everything in a temp folder)."""
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
    try:
        run_data_smoke(data_root, extra_checks=lambda tmp_root, selected: classifier_smoke(data_root, tmp_root, selected))
    except (DatasetError, ExperimentError) as exc:
        print(f"smoke: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE
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


def _configure_prepare(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        metavar="N",
        help="worker processes for image caching (default: number of CPU cores, at most 8)",
    )


def _configure_run(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--exp", required=True, metavar="ID", help="experiment ID (E1-U), a group (E0, E1, E2, X-domain) or a comma-separated list")
    parser.add_argument(
        "--splits",
        type=parse_splits,
        default=DEFAULT_SPLITS,
        metavar="LIST",
        help="comma-separated split seeds (default: 0,1,2,3,4)",
    )
    parser.add_argument("--force", action="store_true", help="retrain splits whose metrics.json already exists")
    parser.add_argument("--sweep-lr", action="store_true",
                        help="learning-rate sweep: split 0 at lr 1e-4 and 3e-4 into _work/runs/sweep/ (never a result)")
    parser.add_argument("--batch-size", type=int, default=None, metavar="N", help="batch size (default 32; 16 + --grad-accum 2 if memory is short)")
    parser.add_argument("--grad-accum", type=int, default=None, metavar="N", help="gradient accumulation steps (default 1)")
    parser.add_argument("--num-workers", type=int, default=None, metavar="N", help="data-loading processes (default: cores - 1, at most 4)")
    parser.add_argument("--out-dir", type=Path, default=None, metavar="DIR", help="write DIR/<ID>/split_<k>/ instead of _work/runs/<ID>/")
    dev = parser.add_argument_group("dev overrides (output goes to _work/runs/scratch/, never counted as a result)")
    dev.add_argument("--lr", type=float, default=None, metavar="LR", help="fine-tuning learning rate instead of choices.json")
    dev.add_argument("--epochs", type=int, default=None, metavar="N", help="fine-tuning epochs (default 30)")
    dev.add_argument("--stage1-epochs", type=int, default=None, metavar="N", help="linear-probe epochs (default 2)")


def _configure_choose_lr(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--backbone", required=True, choices=BACKBONES, help="backbone whose split-0 sweep to evaluate")


def _configure_gradcam(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--exp", required=True, metavar="ID", help="experiment ID")
    parser.add_argument("--split", type=int, required=True, metavar="K", help="split seed")


def _configure_predict(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--exp", default=None, metavar="ID", help="experiment ID (default: the recommended one in choices.json)")
    parser.add_argument("--split", type=int, default=0, metavar="K", help="split seed (default: 0)")
    parser.add_argument("--image", type=Path, required=True, metavar="PATH", help="image to classify")
    parser.add_argument("--run-dir", type=Path, default=None, metavar="DIR", help="use DIR/best.pt directly instead of the run folder of --exp")


@dataclass(frozen=True)
class Command:
    name: str
    help: str
    handler: Callable[[argparse.Namespace], int]
    configure: Callable[[argparse.ArgumentParser], None] | None = None


COMMANDS = (
    Command(
        "download-weights",
        "fetch the torchvision pretrained weights into <data-root>/_work/weights/ (idempotent)",
        cmd_download_weights,
    ),
    Command(
        "prepare",
        "index, cache, near-duplicate audit, splits, tables and figures (idempotent)",
        cmd_prepare,
        _configure_prepare,
    ),
    Command("run", "train and evaluate one experiment over the given splits", cmd_run, _configure_run),
    Command(
        "choose-lr",
        "record the learning rate of a backbone from its split-0 sweep (T3.4 rule) in choices.json",
        cmd_choose_lr,
        _configure_choose_lr,
    ),
    Command(
        "summarize",
        "aggregate all runs into tables and figures",
        not_implemented("summarize", "07"),
    ),
    Command("gradcam", "Grad-CAM figures for one experiment and split", not_implemented("gradcam", "07"), _configure_gradcam),
    Command("predict", "classify a single image and print class probabilities", cmd_predict, _configure_predict),
    Command("smoke", "tiny end-to-end check: imports, device, data path, one tiny experiment and predict", cmd_smoke),
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
