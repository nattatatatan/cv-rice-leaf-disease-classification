# 08 - Report, user manual, submission

Goal: a report that earns every mark the spec lists, written in Word / Google Docs from the frozen results, plus a zip that a marker can reproduce from.

Prerequisites: sections 3-4 can start on day 2. Sections 5-6 start after the `results-freeze` tag (or are drafted earlier with placeholders like `[[E1-U field F1]]`, which are filled from `_work/results/` at freeze).

## Format rules (check before export)
- Single column, **12-point font**, margins **>= 1.25 cm** on all sides, page numbers starting at 1 **after** the coversheet.
- Content beyond a section's page limit is **not marked**. Treat the limits as hard.
- Figures and tables are numbered, captioned, and referenced in the text ("as shown in Fig. 3").
- IEEE citation style `[1]`. Own words throughout. **No Python code in the report**: pseudocode and block diagrams only (the spec applies a heavy penalty for copied code).
- Check the subject's policy on generative-AI use and add whatever acknowledgement it requires (coversheet or a short note).

## Section-by-section brief

### 1. Coversheet (no marks, required)
Title, group members' names, and each member's contribution (be specific: "implemented composite generator; wrote sections 3 and 5").

### 2. Executive summary - 1 mark, <= 1/2 page (write last)
One paragraph each for: the problem; the method in two sentences; headline results for scenarios (a), (b), (c) as mean +- std macro-F1 and accuracy; the main finding about the white -> field transfer; one sentence on limitations.

### 3. Problem description - 5 marks, <= 1 page
- Client need -> CV problem: **supervised 5-class image classification** across **two visual domains** (domain shift). In the field domain there is a **localisation sub-problem**: which leaf is diseased.
- Image analysis from the audit, with numbers: class x domain counts and imbalance; 1952x4160 portrait images, aspect 0.47; EXIF rotation on 381 images; white = one leaf covering ~X% of the image (from T5.1); field = dense canopy, target leaf ~10-15%, small lesions, varied illumination; visually confusable classes (Brown Spot vs Rice Blast).
- A **challenge -> implication -> design response** table. This is what "analysis must support the choice of method" means. Example rows: small dataset -> overfitting -> transfer learning from ImageNet (justify pretrained models here, as the spec requires); tall aspect and small lesions -> resolution/geometry matters -> input-mode ablation; background clutter and shortcut risk -> leaf localisation (B) / composite training (A); domain imbalance (769 vs 337) -> unified model plus white-to-field transfer.
- Figure 1: `dataset_grid.png`.

### 4. Related work - 2 marks, <= 2 pages
- **At least 4 IEEE Xplore papers published after 2021.** From the diary, these count: the paddy DL survey (IEEE 10574294) and the paddy transfer-learning paper (IEEE 10441084). The ScienceDirect, MDPI and TechScience papers may be cited but **do not count** toward the 4.
- Nattan finds **2-4 more** (aim for 6 IEEE total, for margin). Selection criteria, one paper per theme ideally:
  1. Transfer learning / fine-tuning CNNs for rice or plant disease, small datasets.
  2. Vision transformers or Swin for plant disease (supports the E2 comparison).
  3. Lab-to-field domain shift in plant disease (e.g. PlantVillage-trained models failing in the field) or domain adaptation.
  4. Leaf segmentation or background removal before disease classification.
  5. Synthetic / copy-paste augmentation for plant or agricultural images.
- Search queries for IEEE Xplore (filter: 2022 onwards, Journals + Conferences): `"rice" AND "disease" AND ("transfer learning" OR "fine-tuning")`; `"plant disease" AND ("vision transformer" OR "Swin")`; `"plant disease" AND ("field" OR "in-the-wild") AND ("domain shift" OR "domain adaptation" OR "generalization")`; `"leaf" AND "segmentation" AND "disease classification"`; `"copy-paste" OR "synthetic" AND "plant disease"`.
- Organise **by theme, not paper by paper**, and end each theme with how it informs our method. Diary notes are the starting material; rewrite them, don't copy them.

### 5. Method and implementation - 8 marks, <= 3 pages (highest-value section)
- **Rationale first**: tie each design choice to a challenge from section 3 and a paper from section 4. Justify the pretrained models (spec requirement).
- **Recommended method** (from G2) described step by step so a classmate could implement it:
  - Figure: overall block diagram (training path and inference path).
  - Algorithm 1 (pseudocode): composite generation (T5.2), if A or B is recommended.
  - Algorithm 2 (pseudocode): inference pipeline (read with EXIF -> portrait -> [segment -> crop] -> resize -> classify).
  - Training procedure: LP-FT, augmentation, why hue jitter is small.
- **Pros and cons** of the recommended method (the spec asks for this explicitly): e.g. pros = single forward pass, no field masks needed, works on both domains; cons = relies on pseudo-mask quality, composites are not perfectly realistic, salient-leaf assumption fails on ambiguous scenes, inference cost of two networks (for B).
- **Implementation description** (not code): module structure of `<group_name>.py` (data, models, composites, segmentation, experiments, analysis, CLI), the data flow between modules, and where interim data is stored (`Dhan-Shomadhan/_work/`). Pseudocode for any module, no Python.
- Mention the alternatives evaluated (plain, A, B) and point to 6 for the evidence.

### 6. Experimental results and analysis - 8 marks, <= 2 pages
- **6.1 Settings**: split scheme (70/15/15, stratified by class x domain, duplicate groups kept together, seeds 0-4); `table_hparams`; list of experiments (a compact version of the README matrix); the selection-on-val rule; hardware.
- **6.2 Results**: `table_required` (scenarios a/b/c, mean +- std over 5 runs) first, then compact versions of `table_domains`, `table_methods`, `table_input_mode`, `table_segmenter`. Confusion matrices for the recommended method. Page budget is tight, so put the scenario table and one figure in full and the rest compact.
- **6.3 Discussion**: did the results meet expectations? Typical successes, failures and challenging cases, **with reasons** (T7.4 contact sheets + failure modes, Grad-CAM if available). The domain-gap story (F->F vs W->F vs U vs A/B). How the **method** (not dataset size) could be improved, e.g. better composite realism (harmonisation networks), multi-leaf / multiple-instance classification for canopies, test-time augmentation, higher-resolution tiling, semi-supervised use of unlabelled field images, domain-adversarial training.

### 7. References - 1 mark
IEEE style, exactly the format of the spec's examples. Every reference cited in the text; every citation listed. Include torchvision/PyTorch and the dataset (Mendeley DOI).

### 8. Appendix: user manual - <= 2 pages (missing or unclear = results treated as not reproducible)
- **a) Packages**: Python 3.12; exact pinned versions of torch, torchvision, numpy, matplotlib, opencv-python(-headless) 4.12, scikit-learn, scikit-image; one `pip install ...` line; a note that a CUDA GPU is strongly recommended, and the expected run time on a T4 and on CPU.
- **Pretrained weights**: `python <group_name>.py download-weights` stores them under `Dhan-Shomadhan/_work/weights/`. List the torchvision weight names and their source URLs, plus the manual-download fallback (where to place the `.pth` files).
- **b) Reproduce**: place the original dataset at `.\Dhan-Shomadhan\` next to the `.py`. Then:
  - `python <group_name>.py reproduce` - everything, with expected time;
  - `python <group_name>.py prepare` and `python <group_name>.py run --exp <ID>` - individual experiments (table of IDs -> report tables);
  - `python <group_name>.py summarize` - regenerates every table and figure, and states where they appear;
  - `python <group_name>.py predict --image <path>` - client usage;
  - `python <group_name>.py smoke` - 3-minute installation check.
- State that all interim data is generated under `Dhan-Shomadhan/_work/` by the `.py`, and that the field annotations used for segmentation IoU are embedded in the `.py`.
- Note expected small numerical differences across GPUs (non-deterministic cuDNN kernels).

## T8.x Submission checklist
- [ ] `results-freeze` tag exists; every number in the report traces to a file in `_work/results/` at that tag.
- [ ] **Clean-room reproduction**: on a fresh Colab session with the original Mendeley zip, follow the user manual literally (copy-paste the commands from the PDF). At least `smoke`, `prepare`, and one full experiment must succeed and match the reported split-0 numbers within normal GPU noise.
- [ ] Also run `smoke` on Windows if any teammate has it (path handling, trailing-space folder names).
- [ ] Import guard passes (no pandas/PIL/timm in `<group_name>.py`).
- [ ] `<group_name>.py` docstring header lists the group name, members and `--help` usage.
- [ ] PDF: page limits per section, 12 pt, margins, numbering, all figures/tables referenced, 4+ IEEE post-2021 papers, coversheet contributions.
- [ ] Zip contains exactly `<group_name>.py` and `<group_name>.pdf`. No images, no `_work/`.
- [ ] Submitted via Moodle (not email) before the deadline, with a few hours of buffer.
