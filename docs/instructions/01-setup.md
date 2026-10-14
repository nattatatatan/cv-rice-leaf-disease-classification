# 01 - Setup: environment, layout, export, Colab

Goal: by the end of this phase, an empty but valid `<group_name>.py` is exported from notebooks, passes tests, and runs on both the M2 laptop and Colab against the **original** dataset structure.

Prerequisites: none.

## Background: why an export tool

The spec requires one `.py` file, but we iterate in notebooks (D10). The risk is that the final file breaks at the last minute. To avoid that, the submission file is generated from notebook cells from day one, and every task ends with exporting and running the generated file. "Export" here means a small script that copies all code cells tagged `#| export` from the notebooks, in order, into `<group_name>.py`. This borrows the idea from nbdev without the dependency.

## Target repo layout

```
group/
  <group_name>.py            # GENERATED - never edit by hand
  requirements.txt           # runtime deps (what the marker installs)
  requirements-dev.txt       # jupyter, pytest, pandas (exploration only)
  notebooks/
    00_dataset_audit.ipynb   # moved from ./dataset.ipynb (not exported)
    10_data.ipynb            # index, EXIF IO, cache, splits, audits
    20_classifier.ipynb      # datasets, transforms, models, train/eval loop
    30_copy_paste.ipynb      # pseudo-masks, composites
    40_segmentation.ipynb    # segmenter, annotations, crop pipeline
    50_analysis.ipynb        # aggregation, tables, figures, Grad-CAM
    90_cli.ipynb             # argparse CLI + experiment registry
    runner.ipynb             # not exported; drives runs on Colab and Kaggle
  tools/
    export_py.py             # notebook -> <group_name>.py
  tests/
    test_*.py                # pytest against the exported module
  docs/...
  Dhan-Shomadhan/            # dataset, original structure
    _work/                   # ALL generated data (gitignored except results)
      cache/  splits/  masks/  runs/  weights/  results/  figures/
```

## Tasks

### T1.1 Python 3.12 environment
- [x] Recreate `.venv` with Python 3.12 (currently 3.14). Example: `python3.12 -m venv .venv` or `uv venv -p 3.12`.
- [x] `requirements.txt` (runtime): `torch`, `torchvision`, `numpy`, `matplotlib`, `opencv-python-headless==4.12.0.88`, `scikit-learn`, `scikit-image`. Pin exact versions after the first successful Colab run (copy from `pip freeze` on Colab so local and Colab match).
- [x] `requirements-dev.txt`: `-r requirements.txt`, `jupyter`, `ipykernel`, `pytest`, `pandas`.
- Done when: `python -c "import torch, torchvision, cv2, sklearn, skimage; print(cv2.__version__)"` prints `4.12.x` on Python 3.12, and `torch.backends.mps.is_available()` is `True` on the M2.

### T1.2 Restore original dataset structure
- [x] Revert the rename from commit `8a7b131`: `Dhan-Shomadhan/White Background /Sheath Blight` -> `Dhan-Shomadhan/White Background /Shath Blight` (use `git mv`; note the trailing space in `White Background `).
- [x] Compare the tree against the original download (initial commit `e6af236`; a fresh Mendeley download, doi 10.17632/znsxdctwtt.1, is the upstream fallback). Any other difference in folder or file names must be reverted too. Done 2026-10-11: all 1107 dataset file paths identical to `e6af236`. Record the original tree (folder names with `repr()` so trailing spaces are visible) in `docs/instructions/dataset-tree.txt`.
- [ ] Upload an **unmodified** dataset zip (rebuilt with `zip -r -X`, no `.DS_Store`/`__MACOSX`) to Google Drive (`MyDrive/csci935/Dhan-Shomadhan.zip`). Colab always runs against this copy, so it doubles as an E2E test of what the marker will have.
- Why: the marker runs our code on their copy. If we only test against a cleaned copy, a path bug only shows up during marking.

### T1.3 Git hygiene
- [x] `.gitignore`: `.DS_Store`, `.venv/`, `__pycache__/`, `Dhan-Shomadhan/_work/cache/`, `Dhan-Shomadhan/_work/weights/`, `*.pt`, `*.pth`, `.ipynb_checkpoints/`. Keep `Dhan-Shomadhan/_work/{splits,runs,results,figures}` tracked, but with checkpoints excluded, so results are versioned.
- [x] `git rm --cached` all tracked `.DS_Store` files.
- [x] Move `dataset.ipynb` -> `notebooks/00_dataset_audit.ipynb`. Delete `dataset.html` from the repo (it can be regenerated).
- [x] Update its hardcoded label mapping to the class/domain mapping defined in [02](02-data.md) once T2.1 exists (it now reads `CSV_LABELS` from the generated module).

### T1.4 Export tool `tools/export_py.py` (stdlib only)
- [x] Read `notebooks/[0-9][0-9]_*.ipynb` in sorted order, skipping `00_*` and `runner`.
- [x] Collect code cells whose first line is exactly `#| export`. Strip that line. Concatenate with a comment header per notebook (`# ---- from 20_classifier.ipynb ----`).
- [x] Prepend a module docstring (project title, group name, "generated file, do not edit", how to run `--help`) and append `if __name__ == "__main__": main()`.
- [x] **Import guard**: parse the result with `ast`; fail with a clear message if any import's top-level package is not in `{stdlib, numpy, matplotlib, cv2, sklearn, skimage, torch, torchvision}`. Use `sys.stdlib_module_names` for stdlib.
- [x] Fail if any exported cell contains notebook-only syntax (`!`, `%`, `display(`).
- [x] Run `py_compile` on the output.
- [x] Group name lives in one constant at the top of `export_py.py` (`GROUP_NAME = "<group_name>"`), and the output filename comes from it.
- Done when: running it on placeholder notebooks produces a file that imports cleanly, and a deliberate `import pandas` in an export cell makes it fail.

### T1.5 CLI skeleton (`notebooks/90_cli.ipynb`)
Subcommands (each can be a stub at first; later phases fill them in):

| Command | Purpose |
|---|---|
| `download-weights` | Fetch all torchvision pretrained weights into `_work/weights/` (sets `TORCH_HOME`). |
| `prepare` | Index, cache, splits, audits, pseudo-masks. Idempotent: skips work whose outputs exist and are valid. Also writes `_work/results/choices.json` from the decisions frozen at results-freeze (embedded in the `.py` as `FROZEN_CHOICES`) when that file does not exist yet, so `run --exp E2-swin-U` works right after `download-weights` and `prepare` and trains the reported configuration. |
| `run --exp ID [--splits 0,1,2,3,4] [--device auto]` | Train and evaluate one experiment over the given splits. |
| `choose-lr --backbone NAME [--force]`, `choose-composites [--force]`, `gate g0\|g1\|g2 [--force]` | Recompute a decision from the runs (learning rate of a backbone, composites per epoch of Method A, input mode, backbone, recommended method). No entry in `choices.json` yet: write it with its evidence. Same value as the recorded one: keep the recorded entry and print both sets of numbers. Another value: keep the recorded entry, print a warning, exit 0 (so `reproduce` goes on); `--force` overwrites (`gate g2` without `--force` refuses, as before). |
| `summarize` | Aggregate all runs into tables and figures under `_work/results/` and `_work/figures/`. |
| `gradcam [--exp ID] [--compare ID] [--split k] [--runs-dir DIR]` | Grad-CAM of the plain model and Method A: figures of the success and failure images, the shortcut check on the annotated field images, and its `findings.md` section. Needs the retrained checkpoints (`runs/retrain/`). |
| `predict --exp ID --image PATH` | Client-facing single-image prediction with class probabilities. |
| `smoke` | Tiny end-to-end run: 20 images, 1 epoch, CPU, every code path (data, composites, segmenter, classifier, summarize). Must finish in < 3 min on the M2. |
| `reproduce [--recommended] [--splits LIST]` | Runs, in-process and in order, the 20 steps of the reported chain (`download-weights`, `prepare`, the learning-rate sweeps and `choose-lr`, E0, `gate g0`, E1, E2, `gate g1`, the composite sweep and `choose-composites`, E3-A and E3-A-WF, `gate g2 --cut B`, `benchmark`, `gradcam`, `summarize`) and verifies the frozen decisions on the way; about 10 h on one T4. `--recommended`: `download-weights`, `prepare`, `run --exp <recommended>`, `summarize` (about 40 min on a T4 plus the one-off `prepare`). `--splits 0`: split 0 only (gates and Grad-CAM, which need five splits, are skipped). Resumable: run the same command again. This is the one command the user manual tells the marker to run. |

Global flags: `--data-root` (default `Dhan-Shomadhan`), `--device {auto,cuda,mps,cpu}`, `--seed-offset` (default 0), `--fast` (smoke settings).

### T1.6 Test harness
- [x] `tests/conftest.py` imports the exported module via `importlib` from the repo root, so tests always exercise the generated file.
- [x] One trivial test now (`--help` exits 0). Later phases add their own tests.
- Done when: `python tools/export_py.py && python -m pytest -q && python <group_name>.py smoke` passes.

### T1.7 Platform-aware runner (`notebooks/runner.ipynb`: Colab, Kaggle, local)
- [x] Cells: mount Drive; `pip install -r requirements.txt` (record `pip freeze` to Drive the first time); unzip `MyDrive/csci935/Dhan-Shomadhan.zip` to `/content/`; copy the latest `<group_name>.py` from `MyDrive/csci935/`; set `--data-root /content/Dhan-Shomadhan`.
- [x] Restore `_work/cache` and `_work/weights` from Drive if present (saves ~5 min per session); otherwise run `download-weights` and `prepare`, then save them to Drive.
- [x] One cell per experiment batch: `!python <group_name>.py run --exp E1-U`.
- [x] After each batch, rsync `_work/runs/<ID>/` (excluding `*.pt` unless needed for Grad-CAM/predict) back to `MyDrive/csci935/_work/runs/`.
- [x] Assert a GPU at the top and print GPU name, Python, torch and OpenCV versions into a `env.json` saved with runs.
- [x] Kaggle (the Colab GPU quota ran out; step-by-step in [kaggle-guide.md](kaggle-guide.md)). The first cells detect the platform (Kaggle first: `KAGGLE_KERNEL_RUN_TYPE` set or `/kaggle/input` exists, because Kaggle images ship `google.colab`; colab: `/var/colab/hostname` or `COLAB_RELEASE_TAG` / `COLAB_GPU`; else local; never by importability) and everything after is shared:
  - inputs are two private Datasets found by globbing `/kaggle/input` (`csci935-dhan-shomadhan`: the zip or Kaggle's extracted tree, 1106 JPEGs asserted, top-level names printed with `repr()`; `csci935-code`: script, `requirements.txt`, `choices.json`, optional `runs.zip`);
  - the data root, caches and weights live in `/kaggle/tmp`, not in `/kaggle/working`; results go to `/kaggle/working/out/` (runs without `*.pt`, `choices.json`, `env.json`, `pip_freeze.txt`, log) and `/kaggle/working/out.zip` is rebuilt after every completed split and every batch;
  - GPU check fails early on no GPU or a P100 (the pinned torch 2.11 builds have no sm_60 kernels; select GPU T4 x2); the pinned torch is kept if the preinstalled one matches, otherwise installed for the driver (CUDA 13.0, else 12.8, else 12.6) with a loud warning and `env.json` record if the pin cannot be honoured; exactly one OpenCV 4.12;
  - `run_parallel([a, b])` runs two experiments at once, one per GPU (`CUDA_VISIBLE_DEVICES`, `--num-workers 2`), output prefixed per experiment, sync after every split; sweeps run in parallel, then `choose-lr` one backbone after the other (only `choose-lr` and the gates write `choices.json`);
  - before training, a warning if finished splits of the experiment ran on a different GPU model (reads their `env.json`);
  - `BATCHES_TO_RUN` (first code cell) selects which batch cells execute under "Save & Run All"; no interactive input anywhere; a failing batch still syncs and zips before it stops the run.
- [x] Testability: the helpers are plain functions in notebook cells tagged `#| lib` (no side effects at import); `tests/test_runner.py` loads exactly those cells and exercises them on fake `/kaggle` trees, mocked subprocess calls and a stand-in script, and runs the whole notebook in `local` mode (`RUNNER_PLATFORM=local`) against the real dataset.
- Handoff: Colab: download `MyDrive/csci935/_work/runs/` into the local `Dhan-Shomadhan/_work/runs/`. Kaggle: download `out.zip` and unpack it (kaggle-guide.md section 8). Commit.

## Phase acceptance
- [x] Local: export + pytest + smoke pass on Python 3.12.
- [ ] Colab: runner reaches the `smoke` command against the original Mendeley structure and prints a GPU name.
- [ ] Kaggle: first session reaches `smoke` and the first epochs of the sweeps (checklist in [kaggle-guide.md](kaggle-guide.md)); confirm `env.json` shows `torch_pin_honoured` and the dataset layout Kaggle produced.
