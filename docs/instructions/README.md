# Rice Leaf Disease Classification - Implementation Instructions

This folder is the single source of truth for completing the CSCI935 group project. The intended executor is Nattan plus coding agents. Read this file fully before starting any phase file.

| File | Phase | Priority tier |
|---|---|---|
| [01-setup.md](01-setup.md) | Environment, repo layout, notebook-to-`.py` export, Colab runner | Required |
| [02-data.md](02-data.md) | Dataset index, EXIF handling, cache, splits, audits | Required |
| [03-classifier-core.md](03-classifier-core.md) | Shared training/evaluation engine | Required |
| [04-experiments-baseline.md](04-experiments-baseline.md) | E0-E2: input size, baseline, domain-wise, cross-domain, architectures | Required |
| [05-copy-paste-method-a.md](05-copy-paste-method-a.md) | Pseudo-masks, composites, Method A | Tier 2 |
| [06-segmentation-method-b.md](06-segmentation-method-b.md) | Annotation, leaf segmenter, Method B, decision gate | Tier 3 |
| [07-analysis.md](07-analysis.md) | Aggregation, tables, figures, Grad-CAM, failure cases | Required (Grad-CAM is Tier 4) |
| [08-report-and-submission.md](08-report-and-submission.md) | Report sections, user manual, packaging | Required |

Source context: [project spec](../project-specs.md), [dataset paper](../rice-leaf-disease-classfication.md), [research diary](../../research-diary.md), [draft plan](../../implementation-plan.md), [dataset audit notebook](../../dataset.ipynb).

---

## 1. Objective

Build, evaluate and report a method that predicts which of 5 diseases (Brown Spot, Leaf Scald, Rice Blast, Rice Tungro, Sheath Blight) is present in a rice leaf image taken on a **white background** or in the **field**.

The research question that makes this project ours, not a generic fine-tuning exercise:

> Can knowledge from the clean white-background domain (769 images, one isolated leaf) be transferred to the cluttered field domain (337 images, dense canopy, many leaves)? Does explicitly finding the leaf help?

Deliverables (spec, due ~26 Oct 2026):

1. `<group_name>.py` - a single Python file that reproduces every reported number.
2. `<group_name>.pdf` - the consulting report (sections, marks and page limits in [08](08-report-and-submission.md)).
3. Both zipped as `<group_name>.zip`. No images, no interim data in the zip.

---

## 2. Decision log

These were decided with Nattan on 2026-10-11. Do not reopen them without asking. Each has a one-line reason so the report can justify it.

| # | Decision | Reason |
|---|---|---|
| D1 | **Deep transfer learning**, not hand-crafted features | Disease cues are combinations of colour, texture and lesion shape; 1106 images is too few to train from scratch but enough to fine-tune ImageNet-pretrained models. |
| D2 | **Recommended method = one unified model** trained on white + field together. Scenarios (a) white-test, (b) field-test, (c) mixed-test are subsets of the same test split. | One model is what the client deploys. Domain-specific and cross-domain models are supporting experiments. |
| D3 | Backbones: **ResNet50** (baseline) -> **ConvNeXt-Tiny** (stronger CNN) vs **Swin-Tiny** (transformer). torchvision only. | ConvNeXt-T and Swin-T are both ~28M params, so "CNN vs transformer" is a controlled comparison. Both accept rectangular inputs. torchvision avoids the permitted-package risk of timm. |
| D4 | Input size is an **ablation** (E0): squash vs pad vs rectangular, at an equal pixel budget. | Images are 0.47 aspect (tall, thin) and lesions are small; the right choice is empirical. |
| D5 | **Copy-paste synthesis**: cut white leaves out with HSV pseudo-masks, paste onto **same-class** field training images. | Makes "learn from white, apply to field" plausible. Same-class backgrounds keep labels consistent. |
| D6 | **Decision gate** between Method A (classifier trained with composites, raw image in) and Method B (segment salient leaf -> crop with context -> classify). Plain unified classifier is the fallback candidate. Winner by **validation** mixed macro-F1. | Both are reasonable; data decides. The loser becomes an ablation. |
| D7 | Segmenter target in field images = **the single salient leaf** (the in-focus, symptomatic leaf the photographer aimed at). | The dataset paper says field photos "focus only on the affected spot". Mirrors what a white image contains. |
| D8 | Segmenter quality measured on **~30 hand-annotated field images** (6 per class), polygons embedded in the `.py`. | Without real field masks there is no honest evidence the segmenter works; embedding polygons keeps IoU reproducible. |
| D9 | Method B classifier input = **crop to leaf bbox with margin, keep context** (no background painting). | More forgiving of imperfect masks than whitening the background. |
| D10 | Develop in **notebooks, export to a single `.py`**, with an automated export tool and a smoke test from day one. | Fast iteration; the export gate keeps the submitted file always working. |
| D11 | Training runs on **Colab/Kaggle GPU**; agents develop and smoke-test locally on the M2. | Full matrix is ~70 classification runs + 5 segmenter runs. |
| D12 | Report written in **Word / Google Docs**; code emits CSV + Markdown tables and 300 dpi PNG figures. | Team preference. |
| D13 | Related work: Nattan finds 2+ additional IEEE Xplore papers (post-2021) using the criteria in [08](08-report-and-submission.md). | Only 2 of the 5 diary papers are IEEE Xplore. |

Defaults chosen by the planner (override freely, but update this table):

| # | Default | Reason |
|---|---|---|
| P1 | Split 70/15/15 train/val/test, stratified by **class x domain**, seeds 0-4 | Spec requires 5 random splits with fixed percentages; stratifying on both keeps ~50 field test images per split. |
| P2 | Primary metric **macro-F1**; also accuracy, per-class recall, confusion matrix | Classes are imbalanced (139 to 283); macro-F1 weighs Brown Spot equally with Sheath Blight. |
| P3 | All gates and model choices use **validation** metrics; test metrics are only reported | Choosing on test inflates results and is the most common way to lose marks for leakage. |
| P4 | Revert the `Sheath Blight` folder rename back to the original `Shath Blight`; code never depends on folder names | The marker's dataset copy has the original names. |
| P5 | Everything the code writes lives under `Dhan-Shomadhan/_work/` | Spec: interim data must be under the dataset folder and be generated by a Python tool. |

---

## 3. Hard constraints (checklist for every task)

- [ ] Python **3.12**. Imports in `<group_name>.py` restricted to: stdlib, `numpy`, `matplotlib`, `cv2` (OpenCV 4.12), `sklearn`, `skimage`, `torch`, `torchvision`. **No pandas, no PIL, no timm** in exported code. (Notebooks used only for exploration may use pandas.)
- [ ] Dataset root default is `Dhan-Shomadhan` relative to the working directory, overridable by `--data-root`. Use `pathlib` everywhere; the marker may be on Windows (`.\Dhan-Shomadhan\`).
- [ ] Never hardcode folder names (they contain typos and trailing spaces: `Field Background  `, `Browon Spot`, `Rice Turgro`, `Shath Blight`). Discover images by walking the tree; derive labels from filename prefixes and cross-check with the CSV.
- [ ] Apply EXIF orientation on every image read (381 of 1106 images carry a rotation tag).
- [ ] Test images never contribute to training anything: classifier weights, segmenter weights, composites, pseudo-mask thresholds, normalisation statistics, hyperparameter choices.
- [ ] Every reported number = mean +- std over the 5 splits.
- [ ] Pretrained weights are downloadable by a provided command and stored in a documented location.

---

## 4. Pipeline overview

```
                    Dhan-Shomadhan/ (original structure)
                                 |
                       prepare: index + EXIF + cache
                       + 5 stratified splits + audits
                                 |
            +--------------------+---------------------+
            |                                          |
   E0 input-size ablation (ResNet50)          pseudo-masks on white
            |                                  (HSV + QC)  [Tier 2]
   E1 ResNet50: U, W->W, F->F, W->F                    |
            |                                  copy-paste composites
   E2 ConvNeXt-T / Swin-T: U, W->F                     |
            |                                  +-------+--------+
     best backbone (val)  ------------------>  |                |
            |                          Method A: classifier   segmenter (per split)
            |                          + composites [Tier 2]  on composites + white
            |                                  |                |   [Tier 3]
            |                                  |          IoU on 30 annotated field
            |                                  |                |
            |                                  |      Method B: seg -> crop -> classifier
            |                                  |                |
            +---------------> DECISION GATE (val mixed macro-F1) <+
                                 |
                   recommended method -> scenarios (a)(b)(c) on test
                                 |
              analysis: tables, confusion, failure cases, Grad-CAM
                                 |
                       report + user manual + zip
```

Legend: **U** = unified (train white+field), **W->W** = train white, test white, **F->F** = train field, test field, **W->F** = train white only, test field (cross-domain).

---

## 5. Experiment matrix

Every row runs on all 5 splits. "Test sets" lists which test subsets are reported. IDs are used verbatim in configs, run folders and report tables.

| ID | Backbone | Train data | Input | Test sets | Tier | Purpose |
|---|---|---|---|---|---|---|
| E0-squash | ResNet50 | U | 320x320 squash | W, F, mixed | Req | Input-size ablation |
| E0-pad | ResNet50 | U | 320x320 letterbox | W, F, mixed | Req | Input-size ablation |
| E0-rect | ResNet50 | U | 448x224 (HxW) | W, F, mixed | Req | Input-size ablation |
| E1-U | ResNet50 | U | best of E0 | W, F, mixed | Req | Baseline (same run as winning E0 row) |
| E1-WW | ResNet50 | W | best of E0 | W | Req | Domain-specific white |
| E1-FF | ResNet50 | F | best of E0 | F | Req | Domain-specific field |
| E1-WF | ResNet50 | W | best of E0 | F (and W) | Req | Cross-domain gap |
| E2-cnx-U | ConvNeXt-T | U | best of E0 | W, F, mixed | Req | Stronger CNN |
| E2-cnx-WF | ConvNeXt-T | W | best of E0 | F (and W) | Req | Stronger CNN cross-domain |
| E2-swin-U | Swin-T | U | best of E0 | W, F, mixed | Req | Transformer |
| E2-swin-WF | Swin-T | W | best of E0 | F (and W) | Req | Transformer cross-domain |
| E3-A | best of E2 | U + composites | best of E0 | W, F, mixed | Tier 2 | Method A |
| E3-A-WF | best of E2 | W + composites | best of E0 | F (and W) | Tier 4 | Does synthesis close the W->F gap? (uses field images as backgrounds, so state it is not pure W->F) |
| S-seg | LRASPP-MobileNetV3 | composites + white pseudo-masks | 512x256 | IoU: white val, 30 annotated field | Tier 3 | Leaf segmenter |
| E4-B | best of E2 | U, cropped by S-seg | best of E0 | W, F, mixed | Tier 3 | Method B |
| X-domain | best of E2 | W / F | best of E0 | W / F | Tier 4 | Domain-specific models with best backbone |
| X-gradcam | recommended | - | - | annotated field + samples | Tier 4 | Shortcut analysis |

Rough budget on a T4: ResNet50 ~3 min/run, ConvNeXt-T / Swin-T ~6 min/run, segmenter ~10 min/run. Required tier is ~55 runs (~4 h). Everything is ~80 runs (~7-8 h GPU). Run in batches by experiment ID so a Colab disconnect loses at most one batch.

---

## 6. Workflow for agents

1. Pick the next unchecked task in the lowest-numbered phase file whose prerequisites are met.
2. Implement in the phase's notebook, inside cells marked `#| export` for anything the final `.py` needs (see [01](01-setup.md)).
3. Run `python tools/export_py.py && python -m pytest -q && python <group_name>.py smoke` locally. All three must pass before a task is done.
4. For GPU work, hand Nattan the exact Colab command (`python <group_name>.py run --exp <ID>`). Do not mark an experiment done until its `metrics.json` files for all 5 splits are back in `Dhan-Shomadhan/_work/runs/`.
5. Commit per task with a message naming the task ID (e.g. `T2.3 stratified splits`). No co-author lines.
6. Update the checkbox in the phase file and, if a decision changed, the decision log above.

Stop and ask Nattan when: a gate result is ambiguous (difference smaller than one std), a constraint in section 3 cannot be met, a task needs more than ~2x its estimate, or anything would change D1-D13.

---

## 7. Timeline and cut lines

Today is Sun 11 Oct 2026. Due ~Mon 26 Oct 2026.

| Dates | Work | Owner |
|---|---|---|
| Sun 11 - Mon 12 | 01 setup, 02 data | agents |
| Mon 12 - Wed 14 | 03 core engine; E0, E1 on Colab | agents + Nattan (Colab) |
| Tue 13 - Thu 15 | Annotate 30 field images (06, T6.1); find 2+ IEEE papers; draft report sections 3-4 | Nattan |
| Wed 14 - Thu 15 | E2 architectures; pick best backbone | agents + Nattan |
| Thu 15 - Sat 17 | 05 pseudo-masks, composites, E3-A | agents + Nattan |
| Sat 17 - Mon 19 | 06 segmenter, E4-B, decision gate | agents + Nattan |
| Mon 19 - Tue 20 | 07 analysis; **results freeze end of Tue 20** | agents |
| Mon 19 - Fri 23 | Report sections 5-6, exec summary, user manual | Nattan + agents |
| Sat 24 - Sun 25 | Clean-environment reproduction, packaging, proofread, buffer | Nattan |

Cut lines (priority: Required > A > B > extras):

- If E2 is not finished by **Thu 15**, drop E2-*-WF rows and keep only the U rows.
- If E3-A is not finished by **Sun 18**, skip Method B entirely. Recommend the best plain unified model; describe A/B as proposed improvements in 6.3.
- If E4-B is not finished by **Tue 20**, report Method A vs plain only; the segmenter goes into "how the method may be improved".
- Tier 4 extras happen only after the results freeze is safe.
