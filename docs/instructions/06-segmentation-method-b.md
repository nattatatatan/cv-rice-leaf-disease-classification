# 06 - Salient-leaf segmentation, Method B, decision gate

Goal: train a segmenter that finds the salient leaf in a field image without any real field masks (it learns only from composites and white pseudo-masks), measure honestly whether it works, and use it to build **Method B**: segment -> crop with context -> classify. Then choose the recommended method (Gate G2).

Prerequisites: 05 T5.1-T5.3 done. T6.1 (annotation) is manual and can start on day 2. Notebook: `notebooks/40_segmentation.ipynb`. Tier 3.

## T6.1 Hand annotation of 30 field images (Nattan, ~1.5 h, time-boxed)

- [x] Selection: 6 field images per class, sampled with `np.random.default_rng(2026)` from all field images. The exported code writes the list to `_work/annotations/selection.json`, so the selection is reproducible.
- [x] Split the 30 into **dev** (2 per class = 10) and **eval** (4 per class = 20), also seeded. Dev may be used to tune composite realism and segmenter settings. Eval is looked at only once per final segmenter, for the reported IoU. *Tuning on the images you report on is the same leakage as tuning on test.*
- [x] Annotate on the **cached** images (`prepare` copies them to `_work/annotations/images/`) (`_work/cache/`, portrait, 1280 px long side), so the coordinates match what the code sees.
- [x] Tool: `labelme` (dev-only install; see [annotation-guide.md](annotation-guide.md)) or CVAT. One polygon per image, label `leaf`.
- [ ] **Protocol for "salient leaf"** (put this verbatim in the report appendix or method section):
  1. The leaf that is in focus, shows disease symptoms, and is closest to the image centre.
  2. If several qualify, the one with the largest visible area.
  3. Trace only visible parts; exclude leaves crossing in front of it.
  4. If no single leaf is clearly salient, still annotate the best candidate and set the flag `ambiguous: true`.
- [x] (converter `tools/labelme_to_annotations.py` is done) Convert to a compact JSON: per filename, polygon vertices normalised to [0, 1], simplified with `cv2.approxPolyDP` to <= 60 vertices, plus the `ambiguous` flag. Commit it as `annotations/field_salient_leaf.json`.
- [x] Extend `tools/export_py.py` to embed this JSON as a Python constant `FIELD_ANNOTATIONS` in `<group_name>.py`. (Done with the duplicate groups: the `EMBEDDED_FILES` table in `tools/export_py.py` already lists `annotations/field_salient_leaf.json` as optional and skips it until the file exists; once it is committed the constant appears automatically.) The submission can only contain the `.py` and `.pdf`, so this is the only way for the marker to reproduce the IoU numbers. (~30 x 60 x 2 numbers, a few KB.)
- [x] These 30 images are excluded from the composite background pool in every split (T5.2).

## T6.2 Segmenter

- [x] Model: `torchvision.models.segmentation.lraspp_mobilenet_v3_large(weights="COCO_WITH_VOC_LABELS_V1")`, heads replaced with 1 output channel (leaf logit). It is small and fast, and COCO pretraining already knows object boundaries.
- [x] Training data for split `k` (no val/test pixels):
  - 50% composites from T5.2 (target = pasted-leaf mask; everything else, including real field leaves, = background);
  - 50% white **train** images with accepted pseudo-masks.
- [x] Input 512x256 (H x W), portrait; flips, +-15 degree rotation, colour jitter as in T3.2.
- [x] Loss: BCE + soft Dice. AdamW lr 3e-4, wd 1e-4, 40 epochs x 1000 samples, batch 16, cosine schedule.
- [x] Checkpoint selection: IoU on **val composites** (built from white val leaves on field val backgrounds; fixed seed, 200 images) + white val pseudo-masks.
- [ ] One segmenter per split: `_work/runs/S-seg/split_<k>/` (same artefact layout as classifiers, plus `seg_metrics.json`). (Code done: `run --exp S-seg`, idempotent like `run` (split sha256 + fingerprint, `--force`), `--fast` / `--epochs` / `--seg-arch` go to `scratch/`. The GPU runs are open: batch5.)
- [ ] Development loop on the **dev** annotations only: if the dev IoU is poor, adjust composite realism (T5.2 steps 4-6) or the post-processing below. One allowed architecture swap, decided on dev only: `deeplabv3_mobilenet_v3_large`.
  - Dev loop run on 2026-10-13 (split 0, 8 epochs, M2; dev annotations only): LRASPP dev IoU 0.000, 9 of 10 dev images
    fall back, 311 of 337 field images fall back, while val composites reach IoU 0.73 and white val 0.92. The segmenter
    learns "pasted leaf vs real field leaf" (real field leaves are background in every composite), so it rejects the real
    salient leaf. DeepLabV3 swap: dev IoU 0.015, 8 of 10 fallbacks (not adopted). Post-processing sweep (threshold
    0.1-0.5, min area 0.5-2%): best dev IoU 0.05, 1 of 10 boxes with >= 50% of the leaf. Whites at the composites'
    resolution: no change. **Open: needs Nattan's decision before batch5** (see the agent report for options).

### Post-processing: mask -> crop box
1. Sigmoid > 0.5 -> connected components -> keep the component with the largest `area x centrality`, where centrality = 1 - (normalised distance of the component centroid from the image centre).
2. If no component covers >= 2% of the image: **fallback** to the full image, and log it. Count fallbacks per domain for the report.
3. Bounding box of the component, expanded by 15% per side, then grown along the shorter side to the classifier's input aspect, then clamped to the image. *Context is kept on purpose (D9): a slightly wrong mask still yields a usable crop.*

### Segmenter metrics (reported as mean +- std over the 5 split-segmenters)
- [ ] IoU and Dice on the 20 **eval** annotations (all, and excluding `ambiguous`). (Code done: `seg-eval --set eval --final` writes the `eval` section of each `seg_metrics.json`, once per segmenter; `summarize` writes `table_segmenter`. Development uses `seg-eval --set dev` only. Numbers need the 5 GPU segmenters.)
- [ ] **Salient-leaf hit rate** (code done, in `seg-eval` and `table_segmenter`, which also reports the mean crop-box area and the fallbacks, because a fallback box is the whole image and always "hits"): the fraction of eval images whose crop box contains >= 50% of the annotated leaf area. This matters more than IoU, because Method B only uses the box.
- [ ] IoU on white val pseudo-masks (sanity check: should be high). (Code done: `metrics.json` of each S-seg split, `table_segmenter`.)
- [ ] Figure `_work/figures/seg_examples.png` (code done, written by `seg-eval --set eval --final` from split 0; the dev variant goes next to the run): 10 field images (incl. 2 failures) with predicted mask, annotation and crop box overlaid.

## T6.3 Method B classifier (`E4-B`)

- [x] For split `k`, run the split-`k` segmenter over **all** cached images once and store the boxes in `_work/runs/S-seg/split_<k>/boxes.json`. White and field images are treated the same, so train and test see one consistent pipeline.
- [x] `input_hook` (T3.2) crops by the stored box. At train time, jitter the box by +-5% (augmentation); at eval time, use it exactly.
- [x] Classifier: G1 backbone, G0 input mode, unified training, **no composites** (keeps A and B separable; A+B combined is a Tier 4 extra only if both beat plain).
- [ ] Run all 5 splits. (Code done: `run --exp E4-B` fails clearly when `S-seg/split_<k>/boxes.json` is missing, records the boxes' sha256 and retrains when they change; `predict` on E4-B segments, crops, then classifies. GPU runs open: batch5, after S-seg.)

## T6.4 Gate G2: recommended method

- [x] Candidates: plain G1 unified model, `E3-A`, `E4-B`. (`gate g2`; `--cut A` / `--cut B` leaves out a method dropped by a cut line, otherwise every candidate must be complete.)
- [x] Rule: highest **mean val mixed macro-F1**. If the top two are within one std, pick the higher **val field** macro-F1. If still within one std, pick the simpler (plain < A < B).
- [ ] Write `{"recommended": ..., "evidence": {...}}` to `choices.json`. Freeze it. (Code done: `gate g2` writes it and refuses a different outcome later unless `--force`; `table_methods` shows test rows only after it exists. The decision itself is open.) Then, and only then, open the test-set table for the recommended method. Its test results answer scenarios (a), (b), (c).
- [ ] If the decision is ambiguous, or the recommended method differs from what the test numbers would suggest, **report the val-based choice anyway** and discuss the discrepancy in 6.3. Flipping the choice after seeing test numbers is test-set selection.

## Phase acceptance
- [ ] `FIELD_ANNOTATIONS` embedded; segmenter metrics table and figure produced.
- [ ] E4-B complete over 5 splits.
- [ ] `choices.json.recommended` set; `findings.md` explains why, with numbers.
