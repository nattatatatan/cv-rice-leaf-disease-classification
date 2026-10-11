# 04 - Required experiments: input size, baseline, domains, architectures

Goal: produce the spec-required results (3 scenarios, 5 splits, mean +- std) with plain classifiers, and make two data-driven choices that later phases depend on: **input mode** (G0) and **backbone** (G1).

Prerequisites: 03 complete; the `E0-rect` split-0 sanity run has passed.

All runs happen on Colab via `python <group_name>.py run --exp <ID>`. Agents prepare the registry entries, smoke-test each ID locally with `--fast`, and hand Nattan the batch commands.

## Batch 1 - E0 input-size ablation (ResNet50, unified)

- [ ] LR sweep for ResNet50 on split 0 with `rect` mode (T3.4 rule). Record the result in `choices.json`.
- [ ] Run `E0-squash`, `E0-pad`, `E0-rect` on all 5 splits.
- [ ] **Gate G0**: choose the input mode with the highest **mean val mixed macro-F1**. If the top two are within one std of each other, prefer `rect`: it preserves leaf geometry at no extra cost, and that rationale is easy to defend. Write `{"input_mode": ...}` to `choices.json`.
- Report use: a small table in 6.2, plus one sentence in 5 justifying the input size.

## Batch 2 - E1 ResNet50 baseline and domain experiments

- [ ] `E1-U` is an alias of the winning E0 row. Do not retrain; the registry points to the same run folder.
- [ ] Run `E1-WW`, `E1-FF`, `E1-WF`.

| Row | Train | Checkpoint chosen on | Report on test |
|---|---|---|---|
| E1-U | white + field train | white + field val | white, field, mixed |
| E1-WW | white train | white val | white |
| E1-FF | field train (~235 imgs) | field val | field |
| E1-WF | white train | white val | field (main), white (reference) |

Questions these runs answer (write the answers into `_work/results/findings.md` as they come in; they feed 6.3):
1. **Domain gap**: how far does field macro-F1 drop from E1-FF to E1-WF? This number motivates Methods A and B.
2. **Does white data help field?** Compare field-test macro-F1 of E1-U vs E1-FF. If U wins, the unified model is learning transferable disease features from white images.
3. **Does field data hurt white?** Compare white-test of E1-U vs E1-WW.
4. Which classes collapse under W->F? Look at the confusion matrix. The audit expects Brown Spot vs Rice Blast confusion and weak Sheath Blight.

## Batch 3 - E2 architecture comparison

- [ ] LR sweeps on split 0 for ConvNeXt-T and Swin-T.
- [ ] Run `E2-cnx-U`, `E2-swin-U` (5 splits each).
- [ ] Run `E2-cnx-WF`, `E2-swin-WF` (first to cut if behind schedule; see the README cut lines).
- [ ] **Gate G1**: choose the backbone among {ResNet50 (E1-U), ConvNeXt-T, Swin-T} with the highest **mean val mixed macro-F1**. If the top two are within one std, prefer the one with higher **val field** macro-F1, because field is the harder and more valuable domain for the client. Write `{"backbone": ..., "lr": ...}` to `choices.json`.
- [ ] Paired comparison: because all models share the same 5 splits, also report the mean +- std of the **per-split difference** (e.g. ConvNeXt minus ResNet50). Variation between splits largely cancels in the difference, so it shows whether a gap is consistent. The spec only requires mean +- std, so this is an extra column, not a replacement.

## Batch 4 (Tier 4, only after results freeze is safe) - X-domain
- [ ] If G1 picks a backbone other than ResNet50, rerun W->W and F->F with it, so scenarios (a)/(b) can also be answered by domain-specific models of the best architecture.

## Phase acceptance
- [ ] `summarize` produces `_work/results/table_required.md` and `.csv`: rows = E1-U, E2-cnx-U, E2-swin-U, (later the recommended method); columns = white / field / mixed / domain-balanced, each as accuracy and macro-F1 mean +- std over 5 splits.
- [ ] `_work/results/table_domains.md`: E1-WW, E1-FF, E1-WF, E1-U (and E2 WF rows).
- [ ] `choices.json` contains `input_mode`, `backbone` and `lr`, each with the val numbers that justified it.
- [ ] `findings.md` answers questions 1-4 with numbers.

This is the **minimum complete submission**. If everything after this phase fails, the report can still be written with E1/E2 as the recommended method.
