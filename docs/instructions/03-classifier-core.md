# 03 - Classifier core: one engine for every experiment

Goal: a single, config-driven train/evaluate engine. Each experiment in the README matrix is just a config entry. Methods A and B later plug in through two hooks: extra training samples (composites) and an input transform (segmentation crop).

Prerequisites: 02 complete. Notebooks: `notebooks/20_classifier.ipynb`, registry in `notebooks/90_cli.ipynb`.

## Concepts used here

- **Fine-tuning**: start from ImageNet-pretrained weights and update them on our data, instead of training from random weights.
- **Linear-probe-then-fine-tune (LP-FT)**: first train only the new classification head with the backbone frozen, then unfreeze everything at a lower learning rate. The randomly initialised head is not allowed to send large, noisy gradients into good pretrained features. This matches the two-level scheme in the research diary (MDPI paper).
- **Macro-F1**: compute F1 per class and average them unweighted. Unlike accuracy, it does not let the large classes hide poor performance on a small one.

## Tasks

### T3.1 Experiment config and registry
- [ ] `@dataclass ExperimentConfig`: `exp_id, backbone ("resnet50"|"convnext_tiny"|"swin_t"), train_domains ({"white","field"} subset), select_domains (domains whose val images pick the checkpoint), test_subsets, input_mode ("squash"|"pad"|"rect"), use_composites: bool, seg_crop: bool, epochs, lr, batch_size, ...` with defaults from T3.4.
- [ ] `EXPERIMENTS: dict[str, ExperimentConfig]` holds every row of the README matrix. Rows marked "best of E0/E2" resolve at runtime from `_work/results/choices.json`, which is written by the gates in [04](04-experiments-baseline.md). They fail with a clear message if that file does not exist yet.
- [ ] `select_domains` rule: equals `train_domains`. For W->F rows, checkpoints are chosen on **white** val only. Picking on field val would leak field information into a "white-only" model.

### T3.2 Dataset and transforms (no PIL; torch tensors + OpenCV)
- [ ] `LeafDataset(records, split_ids, transform, extra_sources=())` reads from `_work/cache/`. `extra_sources` is the hook for composites (Method A).
- [ ] Input modes at an **equal pixel budget** (~100k px), so E0 compares geometry, not resolution:
  - `squash`: resize to 320x320 (aspect distorted ~2x horizontally).
  - `pad`: letterbox to 320x320 with the ImageNet mean colour, aspect preserved.
  - `rect`: resize to 448x224 (H x W), aspect ~preserved (0.5 vs 0.47).
- [ ] Train augmentation, applied before the input-mode resize:
  - random crop covering 60-100% of the area, keeping the image's own aspect (simulates zoom/framing);
  - horizontal and vertical flip (p = 0.5 each);
  - rotation +-15 degrees, reflect border;
  - colour jitter: brightness 0.2, contrast 0.2, saturation 0.15, **hue 0.02 only**. Colour is diagnostic (Tungro is yellow-orange, Brown Spot lesions are brown), so a large hue shift would change the evidence.
- [ ] Eval transform: input-mode resize only. Normalise with ImageNet mean/std, never with dataset statistics, because those would include test images.
- [ ] Optional `input_hook(image, record) -> image` applied before transforms, at train and eval alike. This is the hook for Method B's crop.
- Tests: output tensor shapes for all three modes; pad mode keeps aspect; augmentation is deterministic under a fixed seed.

### T3.3 Models
- [ ] `build_model(backbone, num_classes=5)` using torchvision weights `ResNet50_Weights.IMAGENET1K_V2`, `ConvNeXt_Tiny_Weights.IMAGENET1K_V1`, `Swin_T_Weights.IMAGENET1K_V1`. Replace the final layer with `Dropout(0.2) + Linear(in_features, 5)`.
- [ ] `head_parameters(model)` and `backbone_parameters(model)` for LP-FT freezing.
- [ ] `gradcam_target_layer(model)`: ResNet `layer4`, ConvNeXt `features[-1]`, Swin `features[-1]`. Swin outputs NHWC, so permute to NCHW for CAM. This is used in 07.
- Tests: forward pass on CPU for every backbone x input mode, output shape `(2, 5)`. Swin-T must accept 448x224 and 320x320 (torchvision pads windows internally).

### T3.4 Training recipe (fixed for all backbones; this is section 6.1 of the report)

| Hyperparameter | Value |
|---|---|
| Stage 1 (linear probe) | backbone frozen, 2 epochs, AdamW lr 1e-3 on head |
| Stage 2 (fine-tune) | all layers, 30 epochs, AdamW, lr from the split-0 sweep in {1e-4, 3e-4}, weight decay 0.05 |
| Schedule | 1 epoch linear warmup, then cosine decay to 0 |
| Loss | cross-entropy, label smoothing 0.1 |
| Batch size | 32 (reduce to 16 with gradient accumulation 2 if Swin runs out of memory at 448x224) |
| Precision | AMP (fp16) on CUDA, fp32 on MPS/CPU |
| Gradient clipping | max norm 1.0 |
| Checkpoint selection | best val macro-F1 on `select_domains`; early stop after 10 epochs without improvement |
| Seeds | `random`, `numpy`, `torch` seeded with split seed `k` |
| Class/domain reweighting | none (macro-F1 is reported instead; a balanced sampler is an optional Tier 4 extra) |

- [ ] **LR sweep rule**: for each backbone, run only split 0 at lr 1e-4 and 3e-4, choose by **val** macro-F1, and record it in `choices.json`. Then run all 5 splits with the chosen lr. The sweep runs are kept in `_work/runs/sweep/` and are never reported as results.

### T3.5 Evaluation and run artefacts
- [ ] `evaluate(model, split, subsets)` produces, per subset in `{white, field, mixed}` and for both val and test: accuracy, macro-F1, per-class precision/recall/F1, and the 5x5 confusion matrix (sklearn).
- [ ] Run folder `_work/runs/<EXP>/split_<k>/`:
  - `config.json`, `env.json` (python/torch/cv2 versions, device, GPU name), `history.csv` (per-epoch loss, val macro-F1, lr)
  - `metrics.json` (includes split sha256 and wall time)
  - `predictions_val.csv`, `predictions_test.csv` with `filename, domain, true, pred, p0..p4`
  - `best.pt` (gitignored; keep on Drive for the recommended model and anything used for Grad-CAM/predict)
- [ ] **Idempotent**: `run` skips a split whose `metrics.json` exists unless `--force` is passed, so a Colab disconnect resumes where it stopped.
- [ ] Mixed-test note for the report: "mixed" is the full test split, so it is ~70% white and ~30% field, matching dataset composition. Also report the domain-balanced mean (average of white and field macro-F1) so the headline number is not dominated by the easy domain.

### T3.6 `predict` command
- [ ] Loads `best.pt` of the given experiment/split (default: recommended experiment, split 0), applies the same eval pipeline (including Method B crop if applicable), and prints class probabilities. This is what the user manual shows the client.

## Phase acceptance
- [ ] `smoke` runs one tiny experiment end to end on CPU and writes a complete run folder.
- [ ] One real run (`E0-rect`, split 0) on Colab finishes in < 10 min and reaches val macro-F1 clearly above chance (> 0.5). If not, debug before launching batches: check the labels on a contact sheet of a training batch, the LR, and the normalisation.
