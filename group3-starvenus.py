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
DUPLICATE_GROUPS_FILENAME = "duplicate_groups.json"
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


def merge_groups(groups: list[list[str]]) -> list[list[str]]:
    """Transitive merge: groups that share a filename become one group. Sorted, deterministic."""
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for group in groups:
        for name in group:
            parent.setdefault(name, name)
        for name in group[1:]:
            parent[find(name)] = find(group[0])
    merged: dict[str, list[str]] = {}
    for name in parent:
        merged.setdefault(find(name), []).append(name)
    return sorted((sorted(members) for members in merged.values() if len(members) > 1), key=lambda m: m[0])


def duplicate_groups_path(data_root) -> Path:
    return work_dir(data_root) / DUPLICATE_GROUPS_FILENAME


def load_duplicate_groups(data_root, filenames) -> list[list[str]] | None:
    """The human-confirmed duplicate groups, transitively merged; ``None`` if the file does not exist
    (duplicates are then UNCONFIRMED, which is different from an empty list: "confirmed, none")."""
    path = duplicate_groups_path(data_root)
    if not path.is_file():
        return None
    try:
        raw = json.loads(read_file_bytes(path).decode("utf-8"))
    except ValueError as exc:
        raise DatasetError(f"{path}: not valid JSON: {exc}") from exc
    if not isinstance(raw, list) or not all(isinstance(g, list) and all(isinstance(n, str) for n in g) for g in raw):
        raise DatasetError(f"{path}: expected a list of lists of filenames")
    known = set(filenames)
    unknown = sorted({n for g in raw for n in g} - known)
    if unknown:
        raise DatasetError(f"{path}: {len(unknown)} filenames are not in the index, e.g. {unknown[:5]}")
    return merge_groups(raw)

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


def build_units(records: list[Record], groups: list[list[str]] | None) -> dict[tuple[str, str], list[tuple[str, ...]]]:
    """{stratum: units}; a unit is a sorted tuple of filenames. ``groups=None`` (unconfirmed) and
    ``groups=[]`` (confirmed, none) both give one unit per image."""
    by_name = {r.filename: r for r in records}
    units: dict[tuple[str, str], list[tuple[str, ...]]] = {}
    grouped: set[str] = set()
    for group in merge_groups(groups or []):
        members = tuple(sorted(group))
        grouped.update(members)
        units.setdefault(by_name[members[0]].stratum, []).append(members)
    for record in records:
        if record.filename not in grouped:
            units.setdefault(record.stratum, []).append((record.filename,))
    return units


def make_split(records: list[Record], groups: list[list[str]] | None, seed: int) -> dict:
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


def write_splits(
    data_root, records: list[Record], groups: list[list[str]] | None, seeds=SPLIT_SEEDS
) -> dict[int, str]:
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


def prepare_data(data_root, *, expected_counts=EXPECTED_COUNTS, workers: int | None = None, out=print) -> dict:
    """index -> cache -> near-duplicate audit -> splits -> tables and figures. Returns a summary dict
    (also printed through ``out``). Raises DatasetError on any dataset problem."""
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
    groups = load_duplicate_groups(data_root, [r.filename for r in records])
    if groups is None:
        out(f"  WARNING     duplicates are UNCONFIRMED: no {duplicate_groups_path(data_root).name} in {work_dir(data_root)}.")
        out("              Every image is treated as its own unit in the splits. Review the contact sheets and the")
        out("              CSV, then write the confirmed groups (list of lists of filenames) to that file and re-run.")
    else:
        out(f"  duplicates  {len(groups)} confirmed groups ({sum(len(g) for g in groups)} images) are kept together in the splits")

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
        out("              (expected after the duplicate groups changed; otherwise investigate before training)")
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


def run_data_smoke(data_root, n_images: int = 20, workers: int = 2, log=print) -> None:
    """Cheap end-to-end check of the data path on ~20 real images. Writes only to a temp folder."""
    data_root = Path(data_root)
    records = build_index(data_root, expected_counts=None, with_sha1=False)
    log(f"smoke: OK - index of {len(records)} images, labels match filename prefixes (and the CSV if present)")
    groups = load_duplicate_groups(data_root, [r.filename for r in records])
    log("smoke: OK - duplicate groups: " + ("not confirmed yet (no file)" if groups is None else f"{len(groups)} confirmed groups"))
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
            split = make_split(fake, None, seed)
            parts = [set(split[k]) for k in ("train", "val", "test")]
            smoke_require(sum(len(p) for p in parts) == len(names) and set.union(*parts) == names, "split does not partition")
            smoke_require(split == make_split(fake, None, seed), "split is not deterministic")
        log("smoke: OK - splits are deterministic partitions")

        write_dataset_counts(tmp_root, selected)
        save_class_domain_counts(tmp_root, selected)
        save_dataset_grid(tmp_root, selected)
        smoke_require(
            all((figures_dir(tmp_root) / f).stat().st_size > 1000 for f in ("class_domain_counts.png", "dataset_grid.png")),
            "figures were not written",
        )
        log("smoke: OK - tables and figures")

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


def cmd_smoke(args: argparse.Namespace) -> int:
    """Tiny end-to-end check: data root, image discovery, library imports, device, and the data path
    (index, EXIF read, cache, dHash, splits, figures on ~20 images in a temp folder).

    Later phases extend this into the full tiny run (20 images, 1 epoch, CPU).
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
    try:
        run_data_smoke(data_root)
    except DatasetError as exc:
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
        "fetch the torchvision pretrained weights into <data-root>/_work/weights/ (idempotent)",
        cmd_download_weights,
    ),
    Command(
        "prepare",
        "index, cache, near-duplicate audit, splits, tables and figures (idempotent)",
        cmd_prepare,
        _configure_prepare,
    ),
    Command("run", "train and evaluate one experiment over the given splits", not_implemented("run", "03"), _configure_run),
    Command(
        "summarize",
        "aggregate all runs into tables and figures",
        not_implemented("summarize", "07"),
    ),
    Command("gradcam", "Grad-CAM figures for one experiment and split", not_implemented("gradcam", "07"), _configure_gradcam),
    Command("predict", "classify a single image and print class probabilities", not_implemented("predict", "03"), _configure_predict),
    Command("smoke", "tiny end-to-end check (currently: data root, imports, device, data path)", cmd_smoke),
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
