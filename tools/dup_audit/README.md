# Near-duplicate audit (SIFT + RANSAC)

A **one-off audit**, not part of the submission and not exported into `group3-starvenus.py`. Its only
product is `annotations/duplicate_groups.json` (36 groups covering 77 images), which
`tools/export_py.py` embeds in the generated module as `DUPLICATE_GROUPS`. The splits keep every group in
one split (T2.4 / T2.5, `docs/instructions/02-data.md`). This folder exists so the report can say how
the groups were found and so the result can be re-derived.

## Why it exists

The built-in dHash audit (`prepare`) found no real duplicates: 1526 candidates, almost all unrelated leaves
on a plain wall. It misses what is actually in the data: the dataset was photographed in series, and
consecutive shots of one scene are reframed (shifted, zoomed), which defeats a 9x8 hash. Matching local
features and verifying them geometrically finds those, mostly consecutive **field** shots (e.g.
`rtf_32` / `rtf_33`, 799 inliers) and a few white-background leaves shot twice.

## Pipeline

Needs the dataset index and image cache from `python group3-starvenus.py prepare`
(`Dhan-Shomadhan/_work/index.json` and `_work/cache/`), plus `cv2`, `numpy`, `pandas` (the repo's dev
requirements). Run from the repo root; every script is independent of the working directory. Large
intermediates go to `Dhan-Shomadhan/_work/dup_audit/` (git-ignored).

| Step | Script | What it does | Runtime (8 cores) |
|---|---|---|---|
| 1 | `features.py` | RootSIFT features per cached image (long side 800, up to 1500 keypoints, contrastThreshold 0.005). White images: keypoints restricted to a leaf mask (`leaf_mask`), otherwise matches on the wall (sensor noise, smudges) give false "identical" pairs. | 1 min |
| 2 | `run_pairs.py` | Matches pairs: kNN + Lowe ratio 0.75, then RANSAC homography (6 px) and fundamental matrix (1.5 px) via `matching.py`. Degenerate fits are rejected (ill-conditioned H, inlier cloud under 40 px in either image). Resumable, one `.npy` per 100 pairs. | tier 1: 6 min on 6 workers; tiers 2 and 3: about 1 h (not re-run for this cleanup) |
| 3 | `collect.py` | Joins chunks into one table, defines the score, prints a score histogram per pair group (the threshold evidence), writes `results/pairs_sift.csv` (score >= 15). | seconds |
| 4 | `build_groups.py` | Edges by the thresholds below, connected components, writes `annotations/duplicate_groups.json`. | instant |
| (check) | `calibrate.py` | Scores synthetic "next shots" (crop, scale, rotation, brightness, JPEG) of 40 random images per domain: what a known duplicate scores. | 1 min |

```
python tools/dup_audit/features.py
python tools/dup_audit/run_pairs.py --tiers 1,2,3     # add 4 for the white cross-class null (hours)
python tools/dup_audit/collect.py
python tools/dup_audit/build_groups.py                # compare with the committed file; --write to overwrite
python tools/dup_audit/calibrate.py
```

Pair tiers (`run_pairs.py`): 1 same class + same domain (where duplicates can be), 2 same class across
domains, 3 field vs field with different class (null), 4 white vs white with different class (null). Cost
per pair is about 6 ms for white and 40 ms for field-field on one core; tier 4 has 230k pairs, which is why
the original run covered only 75 % of it (the null was already clear).

## Score and thresholds

* Score: field vs field = `max(H inliers, F inliers)` (canopy is not planar); any pair with a white image
  = `H inliers` only (F on few matches over a narrow leaf is under-constrained).
* **Field**: edge if score >= 20. Null (45172 cross-class pairs) tops out at 16; simulated hard bursts
  never fall below 213; real pairs jump from 16 to 20+, so anything in 17-40 gives the same groups.
* **White**: edge if score >= 40, or score >= 20 and the file numbers are at most 3 apart. White needs a
  second condition because different leaves can score up to 36 (vein texture is nearly periodic), while
  every true white burst in the data is consecutive files (no non-consecutive pair reached 10).
* Only same-class, same-domain pairs become edges. No cross-class or cross-domain pair came near a
  threshold (field cross-class max 16, field-white same-class max 9).
* Inclusive on purpose: a falsely grouped pair costs a little split flexibility; a missed duplicate puts
  near-identical images in train and test and inflates the reported scores. `sbf_1` is grouped with
  `sbf_19` and `sbf_47` although the reviewer was unsure (F-only fits); that is the inclusive choice.

## Result

36 groups, 77 images: 23 field groups (51 images) and 13 white groups (26 images); 32 are pairs, three
have three members (`rtf_17-19`, `rtf_25-27`, `sbf_1/19/47`) and one has four (`rtf_7-10`). Every group lies within one class x domain stratum, which
`validate_duplicate_groups` enforces on every `prepare`.

## Files

* `results/summary.md` - the full audit report: method, calibration table, null distributions, a verdict for
  each top pair after viewing it. It was written during the scratch run, so its **Files** section names
  intermediate files (`feats2.pkl`, `final_pairs.pkl`, contact-sheet PNGs, `calib_bursts2.csv`) that are
  not committed; they correspond to `feats.pkl`, the chunk folders and `calibration_bursts.csv` produced by
  the scripts here.
* `results/pairs_sift.csv` - the 67 pairs with score >= 15 from the original run, all tiers.
* Not committed: the feature pickles (hundreds of MB), the pair pickles, the contact sheets.

## Reproducibility

`features.py` reproduces the original features bit for bit, and tiers 1 of `run_pairs.py` + `collect.py`
reproduce all 55 same-class same-domain rows of `pairs_sift.csv` with identical scores, and
`build_groups.py` reproduces `annotations/duplicate_groups.json` byte for byte. RANSAC is randomised, so
counts at the noise floor (scores of 0 to 11) can differ by a pair between runs; nothing near a threshold
did.
