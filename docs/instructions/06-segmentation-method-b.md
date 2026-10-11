# 06 - Salient-leaf segmentation, Method B, decision gate

Goal: train a segmenter that finds the salient leaf in a field image without any real field masks (it learns only from composites and white pseudo-masks), measure honestly whether it works, and use it to build **Method B**: segment -> crop with context -> classify. Then choose the recommended method (Gate G2).

Prerequisites: 05 T5.1-T5.3 done. T6.1 (annotation) is manual and can start on day 2. Notebook: `notebooks/40_segmentation.ipynb`. Tier 3.

## T6.1 Hand annotation of 30 field images (Nattan, ~1.5 h, time-boxed)

- [ ] Selection: 6 field images per class, sampled with `np.random.default_rng(2026)` from all field images. The exported code writes the list to `_work/annotations/selection.json`, so the selection is reproducible.
- [ ] Split the 30 into **dev** (2 per class = 10) and **eval** (4 per class = 20), also seeded. Dev may be used to tune composite realism and segmenter settings. Eval is looked at only once per final segmenter, for the reported IoU. *Tuning on the images you report on is the same leakage as tuning on test.*
- [ ] Annotate on the **cached** images (`_work/cache/`, portrait, 1280 px long side), so the coordinates match what the code sees.
- [ ] Tool: `labelme` (dev-only install) or CVAT. One polygon per image, label `leaf`.
- [ ] **Protocol for "salient leaf"** (put this verbatim in the report appendix or method section):
  1. The leaf that is in focus, shows disease symptoms, and is closest to the image centre.
  2. If several qualify, the one with the largest visible area.
  3. Trace only visible parts; exclude leaves crossing in front of it.
  4. If no single leaf is clearly salient, still annotate the best candidate and set the flag `ambiguous: true`.
- [ ] Convert to a compact JSON: per filename, polygon vertices normalised to [0, 1], simplified with `cv2.approxPolyDP` to <= 60 vertices, plus the `ambiguous` flag. Commit it as `annotations/field_salient_leaf.json`.
- [ ] Extend `tools/export_py.py` to embed this JSON as a Python constant `FIELD_ANNOTATIONS` in `<group_name>.py`. The submission can only contain the `.py` and `.pdf`, so this is the only way for the marker to reproduce the IoU numbers. (~30 x 60 x 2 numbers, a few KB.)
- [ ] These 30 images are excluded from the composite background pool in every split (T5.2).

## T6.2 Segmenter

- [ ] Model: `torchvision.models.segmentation.lraspp_mobilenet_v3_large(weights="COCO_WITH_VOC_LABELS_V1")`, heads replaced with 1 output channel (leaf logit). It is small and fast, and COCO pretraining already knows object boundaries.
- [ ] Training data for split `k` (no val/test pixels):
  - 50% composites from T5.2 (target = pasted-leaf mask; everything else, including real field leaves, = background);
  - 50% white **train** images with accepted pseudo-masks.
- [ ] Input 512x256 (H x W), portrait; flips, +-15 degree rotation, colour jitter as in T3.2.
- [ ] Loss: BCE + soft Dice. AdamW lr 3e-4, wd 1e-4, 40 epochs x 1000 samples, batch 16, cosine schedule.
- [ ] Checkpoint selection: IoU on **val composites** (built from white val leaves on field val backgrounds; fixed seed, 200 images) + white val pseudo-masks.
- [ ] One segmenter per split: `_work/runs/S-seg/split_<k>/` (same artefact layout as classifiers, plus `seg_metrics.json`).
- [ ] Development loop on the **dev** annotations only: if the dev IoU is poor, adjust composite realism (T5.2 steps 4-6) or the post-processing below. One allowed architecture swap, decided on dev only: `deeplabv3_mobilenet_v3_large`.

### Post-processing: mask -> crop box
1. Sigmoid > 0.5 -> connected components -> keep the component with the largest `area x centrality`, where centrality = 1 - (normalised distance of the component centroid from the image centre).
2. If no component covers >= 2% of the image: **fallback** to the full image, and log it. Count fallbacks per domain for the report.
3. Bounding box of the component, expanded by 15% per side, then grown along the shorter side to the classifier's input aspect, then clamped to the image. *Context is kept on purpose (D9): a slightly wrong mask still yields a usable crop.*

### Segmenter metrics (reported as mean +- std over the 5 split-segmenters)
- [ ] IoU and Dice on the 20 **eval** annotations (all, and excluding `ambiguous`).
- [ ] **Salient-leaf hit rate**: the fraction of eval images whose crop box contains >= 50% of the annotated leaf area. This matters more than IoU, because Method B only uses the box.
- [ ] IoU on white val pseudo-masks (sanity check: should be high).
- [ ] Figure `_work/figures/seg_examples.png`: 10 field images (incl. 2 failures) with predicted mask, annotation and crop box overlaid.

## T6.3 Method B classifier (`E4-B`)

- [ ] For split `k`, run the split-`k` segmenter over **all** cached images once and store the boxes in `_work/runs/S-seg/split_<k>/boxes.json`. White and field images are treated the same, so train and test see one consistent pipeline.
- [ ] `input_hook` (T3.2) crops by the stored box. At train time, jitter the box by +-5% (augmentation); at eval time, use it exactly.
- [ ] Classifier: G1 backbone, G0 input mode, unified training, **no composites** (keeps A and B separable; A+B combined is a Tier 4 extra only if both beat plain).
- [ ] Run all 5 splits.

## T6.4 Gate G2: recommended method

- [ ] Candidates: plain G1 unified model, `E3-A`, `E4-B`.
- [ ] Rule: highest **mean val mixed macro-F1**. If the top two are within one std, pick the higher **val field** macro-F1. If still within one std, pick the simpler (plain < A < B).
- [ ] Write `{"recommended": ..., "evidence": {...}}` to `choices.json`. Freeze it. Then, and only then, open the test-set table for the recommended method. Its test results answer scenarios (a), (b), (c).
- [ ] If the decision is ambiguous, or the recommended method differs from what the test numbers would suggest, **report the val-based choice anyway** and discuss the discrepancy in 6.3. Flipping the choice after seeing test numbers is test-set selection.

## Phase acceptance
- [ ] `FIELD_ANNOTATIONS` embedded; segmenter metrics table and figure produced.
- [ ] E4-B complete over 5 splits.
- [ ] `choices.json.recommended` set; `findings.md` explains why, with numbers.
