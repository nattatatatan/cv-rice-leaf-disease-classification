# 05 - Copy-paste synthesis and Method A

Goal: generate realistic "white leaf in a field" training images and use them to train **Method A**: the G1 backbone, trained on real white + real field + composites, with the raw image as input at inference.

Prerequisites: 04 Gates G0 and G1 decided. Notebook: `notebooks/30_copy_paste.ipynb`. Tier 2.

## Concepts

- **Pseudo-mask**: an automatically generated (not hand-drawn) leaf mask. On white paper this is easy: paper has low colour saturation and the leaf has high saturation.
- **Composite**: a white-background leaf cut out with its pseudo-mask and pasted onto a field image of the **same class** (D5). The label is that class.
- **Shortcut risk**: a network can learn to recognise pasting artifacts (hard edges, mismatched lighting) instead of disease. Every realism step below exists to remove such cues.

## Tasks

### T5.1 White-image pseudo-masks
- [ ] For each white image in the cache: convert to HSV and blur lightly. Otsu-threshold the **S** channel (the leaf is saturated, paper is not), then AND with `V > v_min` to drop dark shadow edges.
- [ ] Morphology: close (fills lesion holes, which are browner and sometimes less saturated), open (removes specks), fill holes (`scipy`-free: flood fill from the border with `cv2.floodFill`), keep the largest connected component.
- [ ] Save `_work/masks/white/<filename>.png` (uint8 0/255) at cache resolution.
- [ ] **QC**: `_work/figures/pseudo_mask_qc_<k>.png` contact sheets (all 769, mask outline over image, 48 per sheet). Nattan reviews them and lists failures in `_work/masks/white_rejects.txt` (committed). Rejected leaves are never used as paste sources or segmenter targets. Target: >= 95% accepted. If below, tune thresholds on a **training-split** sample only.
- [ ] Record mask area fraction per class (for the report's problem description: "a leaf covers on average X% of a white image").
- Note: threshold rules are fixed by hand, not learned from test images, so this step does not leak. Keep thresholds as named constants.
- Tests: a synthetic image (grey paper plus a green ellipse with brown spots) yields IoU > 0.95.

### T5.2 Composite generator `make_composite(leaf_rec, bg_rec, rng) -> (image, alpha_mask, label)`
Steps, each with its reason:
1. **Source sampling**: leaf from the white **train** split (not rejected); background from the field **train** split, same class, excluding the 30 annotated images of T6.1. *No val/test pixels enter training.*
2. **Leaf extraction**: crop the leaf's bounding box, with its alpha from the pseudo-mask.
3. **Geometry**: rotate +-25 degrees; scale so the leaf length is 55-95% of background height; place the centre within the middle 50% of the frame. *Field photographers centred the affected leaf (D7).*
4. **Background defocus**: Gaussian blur on the background with sigma drawn from [0, 4] px at 1280 px scale. *Mimics the shallow depth of field of the salient, in-focus leaf, and weakens competing lesions in the background.*
5. **Colour harmonisation**: in LAB, shift the leaf's L mean toward the background's local L mean (blend factor 0.3-0.7). Apply a small random white-balance gain (+-5%) to the leaf. *White images were shot indoors in sunlight, field images outdoors at various times of day; without this, brightness alone reveals the pasted leaf.*
6. **Edge feathering**: blur alpha with sigma 1.5-3 px and alpha-blend. *Removes the hard cut-out edge.*
7. **Optional shadow** (p = 0.3): a darkened, blurred, offset copy of the alpha under the leaf.
8. Output at cache resolution: the composite plus a binary mask (`alpha > 0.5`), which the segmenter in 06 uses.
- [ ] All randomness from a passed `np.random.Generator`, so a seed reproduces a composite exactly.
- [ ] `_work/figures/composites_examples.png`: 10 composites (2 per class) next to their source leaf and background. This goes into report section 5.
- [ ] **Realism check (cheap)**: Nattan looks at 20 composites mixed with 20 real field images. If the composites are trivially identifiable at a glance, iterate on steps 4-6 before training on them.
- Tests: output shapes; mask non-empty; the same seed gives the same output; a test-split filename can never be sampled (assert).

### T5.3 Composite source for training (`extra_sources` hook from T3.2)
- [ ] `CompositeSource(split_k, n_per_epoch, seed)`: generates composites **on the fly** with a fresh rng per epoch (`seed * 1000 + epoch`), so each epoch sees new variations at no storage cost.
- [ ] Default `n_per_epoch` = number of white training images (~538), roughly tripling the "field-like" samples per epoch. Composites pass through the same train augmentation as real images.
- [ ] Hyperparameter: on split 0 val only, compare `n_per_epoch` in {0.5x, 1x} white-train count. Record the choice in `choices.json`.

### T5.4 Experiments
- [ ] `E3-A`: G1 backbone, G0 input mode, `train_domains = {white, field}`, `use_composites = True`, all 5 splits.
- [ ] `E3-A-WF` (Tier 4): white train + composites only (no real field images as training samples). It tests whether synthesis closes the W->F gap from E1-WF/E2-*-WF. State clearly in the report that field images are still used as backgrounds and their class is used to choose them, so this is "white + field backgrounds", not pure W->F.
- [ ] Add to `findings.md`: E3-A vs plain G1 model on field / white / mixed val and test, with the paired per-split difference.

## Phase acceptance
- [ ] Pseudo-mask QC reviewed and the reject list committed.
- [ ] Composite example figure looks plausible to Nattan.
- [ ] E3-A has 5 complete splits; `summarize` includes it.
