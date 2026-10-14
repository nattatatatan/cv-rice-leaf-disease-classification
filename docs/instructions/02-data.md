# 02 - Data: index, IO, cache, splits, audits

Goal: one deterministic, leakage-safe data layer that every later phase uses. After this phase, `python <group_name>.py prepare` builds the index, cache, 5 splits and audit outputs from the original dataset.

Prerequisites: 01 complete. Notebook: `notebooks/10_data.ipynb`.

## Facts established by the audit (see `notebooks/00_dataset_audit.ipynb`)

| Fact | Consequence |
|---|---|
| 1106 JPEGs, all RGB, unique filenames, CSV and disk match 1:1 | Filename is a safe primary key. |
| White 769 / Field 337. Per class x domain from 49 (Brown Spot, field) to 219 (Sheath Blight, white) | Stratify on class x domain; report macro-F1. |
| 381 images carry an EXIF rotation tag (orientations 3, 6, 8) | Every read must apply EXIF orientation. |
| After EXIF: 1089 are 1952x4160, 6 are 1536x3264 (portrait), 11 field images are 4160x1952 (landscape) | Aspect is ~0.47 almost everywhere. |
| Field images: dense canopy, target leaf ~10-15% of area (planning estimate; measured on the 30 annotated field images: about 7%, 2% for Rice Tungro), lesions small | Resolution matters; motivates segmentation. |

## Label mapping (single source of truth)

Labels come from the **filename prefix**. They are cross-checked against the CSV `Diseases` column. Folder names are never used.

| Prefix | Class | Domain | CSV `Diseases` string |
|---|---|---|---|
| `bs_wb_` | Brown Spot | white | `Brown Spot(white Background)` |
| `ls_wb_` | Leaf Scald | white | `Leaf Scaled(white Background)` |
| `rb_wb_` | Rice Blast | white | `Rice Blast(white Background)` |
| `rt_wb_` | Rice Tungro | white | `Rice Tungro(white Background)` |
| `sb_wb_` | Sheath Blight | white | `Shath Blight(white Background)` |
| `bsf_` | Brown Spot | field | `Browon Spot(Feild Background)` |
| `lsf_` | Leaf Scald | field | `Leaf Scaled(Feild Background)` |
| `rbf_` | Rice Blast | field | `Rice Blast(Feild Background)` |
| `rtf_` | Rice Tungro | field | `Rice Turgro(Feild Background)` |
| `sbf_` | Sheath Blight | field | `Sheath Blight(Feild Background)` |

Class index order (fixed, used in every confusion matrix): `0 Brown Spot, 1 Leaf Scald, 2 Rice Blast, 3 Rice Tungro, 4 Sheath Blight`.

## Tasks

### T2.1 Dataset index
- [x] `build_index(data_root) -> list[Record]` where `Record` is a dataclass: `filename, rel_path, cls, cls_idx, domain, exif_orientation, sha1`.
- [x] Walk `data_root` recursively for `*.jpg` / `*.jpeg` (case-insensitive), skipping `_work/`. Match the prefixes above (check longest prefix first). Raise with the offending path if any file matches no prefix.
- [x] If the CSV exists, assert every file's prefix label equals its CSV label. If the CSV is missing, warn and continue.
- [x] Assert exactly 1106 records and the per class x domain counts from the audit (keep the expected counts as a constant; a mismatch must fail loudly, not silently train on a different dataset).
- [x] Write `_work/index.json`.
- Tests: counts per stratum; works when the folder is renamed `Sheath Blight` <-> `Shath Blight` (build a tiny temp tree in the test); unknown prefix raises.

### T2.2 EXIF-correct image IO
- [x] `read_rgb(path) -> np.ndarray (H,W,3) uint8 RGB` via `cv2.imdecode` on the file bytes (Windows/non-ASCII safe). Verified: OpenCV 4.12 does honour EXIF by default (imread and imdecode, orientations 3/6/8, pixel-identical to PIL); the code still applies the tag explicitly (`IMREAD_IGNORE_ORIENTATION` + numpy) so it cannot depend on build defaults. Convert BGR to RGB.
- [x] Rotate landscape images (after EXIF) by 90 degrees clockwise so that **every image is portrait**. Disease labels do not depend on orientation, and a single orientation keeps the rectangular input (E0-rect) meaningful. Record this in the method section.
- Tests: `sbf_30.jpg` (EXIF 6) and one EXIF-8 image come out portrait with the same pixels as `PIL.ImageOps.exif_transpose` (PIL only inside the test, which is fine because tests are not submitted). If OpenCV does not honour EXIF in the pinned version, implement the transpose manually from the orientation tag and keep the test.

### T2.3 Resolution cache
- [x] Cache every image at **long side 1280 px**, aspect preserved, portrait, JPEG quality 95, to `_work/cache/<filename>`. Decoding 8 MP JPEGs every epoch would dominate training time; 1280 px leaves headroom for 448 px inputs plus random-resized-crop zoom and for Method B crops.
- [x] Idempotent: skip if the cached file exists and `index.json` sha1 matches.
- [x] Multiprocess with `concurrent.futures.ProcessPoolExecutor`.
- Done when: a full cache build takes under ~5 min on Colab, and the cached image count is 1106.

### T2.4 Near-duplicate audit (leakage guard)
- [x] Compute a 64-bit difference hash (dHash) per cached image: grayscale, resize to 9x8, compare adjacent pixels. Report all pairs with Hamming distance <= 6, within and across domains. (Implemented deviation: the hash is taken while caching and stored in the cache manifest. Because the dHash alone flags 1526 pairs on this dataset, almost all unrelated leaves on a plain wall, every pair also gets a SIFT/RANSAC `feature_inliers` score used only to rank the review order.)
- [x] Save `_work/results/near_duplicates.csv` (all candidates, in review order) and contact sheets `_work/figures/near_duplicates_<n>.png` (top 48 pairs, 8 per page) for visual confirmation.
- [x] Nattan confirms which pairs are true duplicates (same leaf/scene). The confirmed groups live in `annotations/duplicate_groups.json` (committed) and are **embedded in the generated `.py` as the constant `DUPLICATE_GROUPS`** by `tools/export_py.py`, because the marker only receives the `.py` and the PDF and must get identical splits. Groups are kept in the same split by T2.5. `prepare` validates them against the index (every filename exists, none in two groups, each group inside one class x domain stratum) and fails loudly otherwise.
- Outcome: dHash found **no true duplicates** (1526 coincidental candidates; reframed consecutive shots defeat a 9x8 hash). A one-off SIFT + RANSAC audit (`tools/dup_audit/`, not exported) found **36 groups covering 77 images**, mostly consecutive field shots of one scene, plus a few white-background leaves shot twice. The grouping is inclusive (a false group costs nothing, a missed duplicate inflates test scores). See decision P6 in [README](README.md).
- Why: if the same leaf appears twice and lands in train and test, test accuracy is inflated. Small agricultural datasets often contain bursts of near-identical shots.

### T2.5 Stratified, group-aware splits
- [x] For seed `k` in `0..4`: within each class x domain stratum, sort units (single images, or duplicate groups as one unit) by filename, shuffle with `np.random.default_rng(k)`, and assign `round(0.15 n)` to test, `round(0.15 n)` to val, rest to train.
- [x] Write `_work/splits/split_k.json` with `{"seed", "train", "val", "test", "sha256"}`. Committed (final, generated with the embedded duplicate groups) so local and Colab runs are guaranteed identical. A test checks them against a fresh regeneration.
- [x] Every run's `metrics.json` records the split sha256 (`split_sha256`, phase 03); a run is re-done when the split changed.
- [ ] `summarize` refuses to aggregate runs whose sha differs from the committed split (phase 07).
- Tests: train/val/test disjoint and covering all 1106; each stratum within +-1 of target counts (without groups; with groups the target is in units, so images can deviate by a group size); duplicate groups never straddle splits for any seed; regenerating gives identical sha256.
- Size per split with the duplicate groups (a group counts as one unit, so counts differ by a few images between seeds): train 773-780, val 163-171, test 162-165, of which 47-49 are field test images. Seed 0: 778 / 166 / 162 (test 115 white + 47 field).

### T2.6 Dataset figures and tables for the report
- [x] `_work/results/dataset_counts.md`: class x domain table with totals.
- [x] `_work/figures/dataset_grid.png`: 2 rows (white, field) x 5 classes, one sample each, fixed seed, EXIF-correct (reuse the audit notebook's layout). This becomes Figure 1 of the report.
- [x] `_work/figures/class_domain_counts.png`: grouped bar chart.

### T2.7 `prepare` command
- [x] Wires T2.1-T2.6 (and later the pseudo-masks of T5.1) behind `python <group_name>.py prepare`.
- [x] Prints a one-screen summary: counts, EXIF fixes applied, duplicates found, split sizes.

## Phase acceptance
- [ ] `prepare` succeeds on the original Mendeley tree on Colab and locally, and produces identical `split_*.json` sha256 in both places.
- [x] All T2 tests pass against the exported module.
