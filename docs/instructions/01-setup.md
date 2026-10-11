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
    colab_runner.ipynb       # not exported; drives runs on Colab
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
- [ ] Recreate `.venv` with Python 3.12 (currently 3.14). Example: `python3.12 -m venv .venv` or `uv venv -p 3.12`.
- [ ] `requirements.txt` (runtime): `torch`, `torchvision`, `numpy`, `matplotlib`, `opencv-python-headless==4.12.0.88`, `scikit-learn`, `scikit-image`. Pin exact versions after the first successful Colab run (copy from `pip freeze` on Colab so local and Colab match).
- [ ] `requirements-dev.txt`: `-r requirements.txt`, `jupyter`, `ipykernel`, `pytest`, `pandas`.
- Done when: `python -c "import torch, torchvision, cv2, sklearn, skimage; print(cv2.__version__)"` prints `4.12.x` on Python 3.12, and `torch.backends.mps.is_available()` is `True` on the M2.

### T1.2 Restore original dataset structure
- [ ] Revert the rename from commit `8a7b131`: `Dhan-Shomadhan/White Background /Sheath Blight` -> `Dhan-Shomadhan/White Background /Shath Blight` (use `git mv`; note the trailing space in `White Background `).
- [ ] Compare the tree against a fresh download from Mendeley (doi 10.17632/znsxdctwtt.1). Any other difference in folder or file names must be reverted too. Record the original tree (folder names with `repr()` so trailing spaces are visible) in `docs/instructions/dataset-tree.txt`.
- [ ] Upload the **original** Mendeley zip to Google Drive (`MyDrive/csci935/Dhan-Shomadhan.zip`). Colab always runs against this copy, so it doubles as an E2E test of what the marker will have.
- Why: the marker runs our code on their copy. If we only test against a cleaned copy, a path bug only shows up during marking.

### T1.3 Git hygiene
- [ ] `.gitignore`: `.DS_Store`, `.venv/`, `__pycache__/`, `Dhan-Shomadhan/_work/cache/`, `Dhan-Shomadhan/_work/weights/`, `*.pt`, `*.pth`, `.ipynb_checkpoints/`. Keep `Dhan-Shomadhan/_work/{splits,runs,results,figures}` tracked, but with checkpoints excluded, so results are versioned.
- [ ] `git rm --cached` all tracked `.DS_Store` files.
- [ ] Move `dataset.ipynb` -> `notebooks/00_dataset_audit.ipynb`. Delete `dataset.html` from the repo (it can be regenerated).
- [ ] Update its hardcoded label mapping to the class/domain mapping defined in [02](02-data.md) once T2.1 exists.

### T1.4 Export tool `tools/export_py.py` (stdlib only)
- [ ] Read `notebooks/[0-9][0-9]_*.ipynb` in sorted order, skipping `00_*` and `colab_runner`.
- [ ] Collect code cells whose first line is exactly `#| export`. Strip that line. Concatenate with a comment header per notebook (`# ---- from 20_classifier.ipynb ----`).
- [ ] Prepend a module docstring (project title, group name, "generated file, do not edit", how to run `--help`) and append `if __name__ == "__main__": main()`.
- [ ] **Import guard**: parse the result with `ast`; fail with a clear message if any import's top-level package is not in `{stdlib, numpy, matplotlib, cv2, sklearn, skimage, torch, torchvision}`. Use `sys.stdlib_module_names` for stdlib.
- [ ] Fail if any exported cell contains notebook-only syntax (`!`, `%`, `display(`).
- [ ] Run `py_compile` on the output.
- [ ] Group name lives in one constant at the top of `export_py.py` (`GROUP_NAME = "<group_name>"`), and the output filename comes from it.
- Done when: running it on placeholder notebooks produces a file that imports cleanly, and a deliberate `import pandas` in an export cell makes it fail.

### T1.5 CLI skeleton (`notebooks/90_cli.ipynb`)
Subcommands (each can be a stub at first; later phases fill them in):

| Command | Purpose |
|---|---|
| `download-weights` | Fetch all torchvision pretrained weights into `_work/weights/` (sets `TORCH_HOME`). |
| `prepare` | Index, cache, splits, audits, pseudo-masks. Idempotent: skips work whose outputs exist and are valid. |
| `run --exp ID [--splits 0,1,2,3,4] [--device auto]` | Train and evaluate one experiment over the given splits. |
| `summarize` | Aggregate all runs into tables and figures under `_work/results/` and `_work/figures/`. |
| `gradcam --exp ID --split k` | Grad-CAM figures. |
| `predict --exp ID --image PATH` | Client-facing single-image prediction with class probabilities. |
| `smoke` | Tiny end-to-end run: 20 images, 1 epoch, CPU, every code path (data, composites, segmenter, classifier, summarize). Must finish in < 3 min on the M2. |
| `reproduce` | Runs `download-weights`, `prepare`, then all reported experiments and `summarize`. This is the one command the user manual tells the marker to run. |

Global flags: `--data-root` (default `Dhan-Shomadhan`), `--device {auto,cuda,mps,cpu}`, `--seed-offset` (default 0), `--fast` (smoke settings).

### T1.6 Test harness
- [ ] `tests/conftest.py` imports the exported module via `importlib` from the repo root, so tests always exercise the generated file.
- [ ] One trivial test now (`--help` exits 0). Later phases add their own tests.
- Done when: `python tools/export_py.py && python -m pytest -q && python <group_name>.py smoke` passes.

### T1.7 Colab runner (`notebooks/colab_runner.ipynb`)
- [ ] Cells: mount Drive; `pip install -r requirements.txt` (record `pip freeze` to Drive the first time); unzip `MyDrive/csci935/Dhan-Shomadhan.zip` to `/content/`; copy the latest `<group_name>.py` from `MyDrive/csci935/`; set `--data-root /content/Dhan-Shomadhan`.
- [ ] Restore `_work/cache` and `_work/weights` from Drive if present (saves ~5 min per session); otherwise run `download-weights` and `prepare`, then save them to Drive.
- [ ] One cell per experiment batch: `!python <group_name>.py run --exp E1-U`.
- [ ] After each batch, rsync `_work/runs/<ID>/` (excluding `*.pt` unless needed for Grad-CAM/predict) back to `MyDrive/csci935/_work/runs/`.
- [ ] Assert `torch.cuda.is_available()` at the top and print GPU name, Python, torch and OpenCV versions into a `env.json` saved with runs.
- Handoff: Nattan downloads `MyDrive/csci935/_work/runs/` into the local `Dhan-Shomadhan/_work/runs/` (or syncs via Google Drive desktop) and commits.

## Phase acceptance
- [ ] Local: export + pytest + smoke pass on Python 3.12.
- [ ] Colab: runner reaches the `smoke` command against the original Mendeley structure and prints a GPU name.
