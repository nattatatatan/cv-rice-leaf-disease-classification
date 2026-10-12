# Kaggle guide - running the GPU batches on Kaggle (and Colab)

One notebook, `notebooks/runner.ipynb`, drives the experiments on Kaggle, Colab and (for dry runs) locally. This guide is
the step-by-step for Kaggle. Colab is at the end.

Why Kaggle: the free Colab GPU quota ran out. Kaggle gives about 30 GPU hours per week and lets a notebook run in the
background ("Save & Run All", up to about 12 hours) with the browser closed. The T4 x2 accelerator has two GPUs, and the
runner uses both (two experiments at once).

## 1. One-time account setup

1. Create or open your account at kaggle.com.
2. Verify your phone: profile picture > Settings > Phone verification. Without it the **Internet** switch and GPU access are
   locked. The notebook needs internet for `pip install` and for the torchvision pretrained weights.
3. Your weekly GPU quota is shown on the notebook page (Session options) and under your profile. Check it before a long run.

## 2. Create the two private Datasets

Both must be **Private**. The notebook finds them by looking at what is mounted under `/kaggle/input`, so the exact slug does
not matter to the code, but use these names so that this guide stays true.

### 2.1 `csci935-dhan-shomadhan` (the images, once)

1. kaggle.com > Datasets > New Dataset.
2. Upload `Dhan-Shomadhan.zip` from the repo root (the original, unmodified zip, 1.96 GB).
3. Title: `csci935-dhan-shomadhan`. Visibility: Private. Create.

Kaggle may extract the zip and may change folder names (for example drop the trailing spaces of `White Background `). Both are
fine: the notebook handles a zip and an extracted tree, asserts 1106 JPEGs either way, and prints the top-level folder names
with `repr()` so you can see what Kaggle did (it is also saved in `out/env.json` under `dataset_layout`). The code never
depends on folder names.

### 2.2 `csci935-code` (small, new version before every session)

Files, all at the top level of the dataset:

| File | Where from | Required |
|---|---|---|
| `group3-starvenus.py` | repo root, after `python tools/export_py.py` | yes |
| `requirements.txt` | repo root | yes |
| `choices.json` | `Dhan-Shomadhan/_work/results/choices.json` | yes for batches that read `input_mode` / `lr.*` (Batch 3 needs `input_mode` and `lr.resnet50`) |
| `runs.zip` | earlier runs that must be skipped or checked, see below | optional |

Create it like the first dataset: Datasets > New Dataset > upload the files > title `csci935-code` > Private.

Optional `runs.zip` (resume or hardware check): put in it the finished runs you want the session to know about. The
`out.zip` of an earlier Kaggle session works as is (rename it `runs.zip`). To build one from the repo:

```
cd Dhan-Shomadhan/_work
zip -r -X ../../runs.zip runs -x 'runs/scratch/*' -x '*.pt'
```

The notebook unpacks it into `_work/runs/` before running, so finished splits are skipped, and `choices.json` from the
dataset is applied last. For the first Batch 3 session you do not need a `runs.zip` (E0 results are not needed to run E2).

## 3. Create the notebook

1. kaggle.com > Code > New Notebook.
2. File > Import Notebook > upload `notebooks/runner.ipynb` from the repo.
3. Right sidebar > Input > Add Input > Your Datasets > add **both** `csci935-dhan-shomadhan` and `csci935-code`.
   They appear under `/kaggle/input/...`; the exact path is found by the notebook (it prints what it found, and if something
   is missing it lists what is mounted).

## 4. Session options (right sidebar > Session options / Settings)

| Setting | Value | Why |
|---|---|---|
| Accelerator | **GPU T4 x2** | Two T4s. **Not** "GPU P100": the pinned torch 2.11 builds have no kernels for the P100 (sm_60), and all committed results ran on Tesla T4. The notebook stops immediately if it sees a P100. |
| Internet | **On** | `pip install`, `download-weights`. Needs the phone verification. |
| Environment | latest ("Always use latest environment") | The script needs Python 3.12 or newer. |
| Persistence | any | Nothing outside `/kaggle/working/out*` is needed afterwards. |

## 5. Choose what to run: `BATCHES_TO_RUN`

It is the only line you edit: the first code cell of the notebook (cell 2).

```python
BATCHES_TO_RUN = ["batch3-core"]
```

| Entry | What it runs |
|---|---|
| `"batch3-core"` | ConvNeXt-T and Swin-T LR sweeps (one per GPU), `choose-lr` for each (one after the other), then `E2-cnx-U` and `E2-swin-U` on all 5 splits (one experiment per GPU) |
| `"batch3-wf"` | `E2-cnx-WF` and `E2-swin-WF` (one per GPU). Cut first if behind schedule. |
| `"batch3"` | both of the above |
| `"batch3-sweeps"` | only the sweeps and `choose-lr` |
| `"batch2"` | E1 rows (planned for the local M2, works here too) |
| `"run:E3-A"` | any single experiment ID, 5 splits |
| `"parallel:E3-A,E3-A-WF"` | two experiments at once, one per GPU |
| `[]` | setup, smoke test and `prepare` only (a cheap check of the whole setup) |

A full run executes: setup, smoke test, `download-weights` and `prepare`, the selected batches (in notebook order), then the
final zip. A typo in the list is reported at the start of the run, not after an hour. Batch 4 cells (Method A, segmenter,
Method B) will be added to the notebook later; until then use the `run:` / `parallel:` entries.

## 6. Run it in the background

1. Top right: **Save Version**.
2. Version type: **Save & Run All (Commit)**. Check that the Accelerator shown in the dialog is T4 x2. Save.
3. Close the tab if you like. The run continues on Kaggle. Under Notebook > Versions you can open the running version
   and watch the log (the log is the same text as `out/runner_log.txt`).

The notebook has no interactive input, so it works unattended. If a batch fails, the outputs are synced and `out.zip` is rebuilt
before the error stops the run.

## 7. Download the results

When the version has finished (or failed, or hit the time limit), open it > **Output** tab:

- `out.zip` - everything you need in one file;
- `out/` - the same files unpacked: `runs/` (all runs without `*.pt` checkpoints), `results/choices.json`, `env.json`,
  `pip_freeze.txt`, `runner_log.txt`.

`out.zip` is rebuilt after **every completed split** and at the end of every batch, so a session that dies still leaves the
splits finished so far. (Not yet verified on a real session: check that the Output tab of a failed or timed-out version
still lists `out.zip`.)

## 8. Unpack into the local repo

From the repo root (adjust the zip path):

```
rm -rf /tmp/kaggle_out && unzip -q ~/Downloads/out.zip -d /tmp/kaggle_out
rsync -a /tmp/kaggle_out/runs/ Dhan-Shomadhan/_work/runs/
git diff --stat Dhan-Shomadhan/_work/results/choices.json
cp /tmp/kaggle_out/results/choices.json Dhan-Shomadhan/_work/results/choices.json
cp /tmp/kaggle_out/env.json docs/env/kaggle-env.json
cp /tmp/kaggle_out/pip_freeze.txt docs/env/kaggle-pip-freeze.txt
```

Notes:

- `choices.json` in the zip is your uploaded copy plus the new `lr.convnext_tiny` / `lr.swin_t` entries from `choose-lr`.
  Your local copy stays the source of truth: copy it over only if you changed nothing locally meanwhile, otherwise merge by hand.
- Check `env.json` for `"torch_pin_honoured": true`. If it is `false` the notebook printed a loud warning at the start: the
  Kaggle torch differs from the pinned 2.11.0 and the numbers may differ slightly from Colab. The actual versions are recorded.
- Then run locally: `python group3-starvenus.py gate g1` and `summarize`, and commit the runs and `choices.json`.

## 9. Update `csci935-code` before the next batch

Whenever the script, `choices.json` or `requirements.txt` changed (new gate result, new code, new batch):

1. Re-export locally (`python tools/export_py.py`) and make sure the checks pass.
2. Datasets > `csci935-code` > New Version > replace the changed files (`group3-starvenus.py`, `choices.json`, optionally
   `runs.zip`) > Create.
3. In the notebook, Input panel: make sure `csci935-code` uses the newest version (use the version selector next to the
   dataset if it still shows the old one), edit `BATCHES_TO_RUN`, Save Version > Save & Run All.

## 10. Expected times

Measured on a Colab T4: ResNet50 `rect`, 19.7 s per epoch, about 28 epochs per run, so about 9 min per run. ConvNeXt-T and
Swin-T are not measured; assume 2x per epoch (about 18 min per U run, about 13 min per W run). Check the first epoch time
in the log and rescale. Add 10 to 15 minutes of setup per session (installs, dataset copy, smoke test, `prepare`).

| Batch | Runs | One T4 | T4 x2 in parallel |
|---|---|---|---|
| `batch3-sweeps` | 4 (2 per model) | about 1.2 h | about 0.6 h |
| `E2-cnx-U` + `E2-swin-U` (splits 1 to 4, split 0 comes from the sweep) | 8 | about 2.4 h | about 1.2 h |
| `batch3-core` (sweeps + both U rows) | 12 | about 3.6 h | about 1.8 h |
| `batch3-wf` | 10 | about 2.2 h | about 1.1 h |
| `batch3` (everything of Batch 3) | 22 | about 5.8 h | about 2.9 h |

Early stopping makes some runs shorter. Two GPUs halve the wall time of a batch; Kaggle's quota counts session time, so it
should halve the quota use too (check the quota counter after the first session). Both fit comfortably in one 12 hour session.

## 11. Rules the notebook enforces or warns about

- All 5 splits of one experiment should run on the same GPU type. Before training, the runner reads `env.json` of the
  finished splits already on disk and prints a loud warning if they ran on a different GPU model. Colab T4 and Kaggle T4 are
  both `Tesla T4`, so mixing them is fine.
- Two experiments at once use `CUDA_VISIBLE_DEVICES=0` and `=1`, `--num-workers 2` each (Kaggle has about 4 vCPUs).
  `choose-lr` is the only command that writes `choices.json` besides the gates; it runs after both sweeps finished, one
  backbone after the other, so two processes never write it at the same time.
- The data root, caches and weights live in `/kaggle/tmp` (or another scratch folder), not in `/kaggle/working`, so the saved
  output stays small (20 GB limit). Nothing is kept between sessions except what you upload in `csci935-code`.

## 12. Troubleshooting

| Message | Meaning and fix |
|---|---|
| `... cannot run the pinned torch 2.11 ... P100` | Accelerator is P100. Session options > Accelerator > GPU T4 x2, run again. |
| `no internet` | Session options > Internet > On (needs phone verification). |
| `group3-starvenus.py not found under /kaggle/input` | `csci935-code` is not attached or lacks the file. The message lists what is mounted. |
| `the dataset images were not found` / `expected 1106` | `csci935-dhan-shomadhan` is not attached, or the upload is incomplete. |
| `THE TORCH PIN COULD NOT BE HONOURED` | The pinned torch could not be installed; the run continues with the preinstalled one. Numbers may differ slightly from Colab; see `env.json`. |
| `choices.json has no lr.resnet50` | Put the committed `choices.json` in `csci935-code` (new version). |
| `already ran on 'X' ... same GPU type` | Finished splits of that experiment came from another GPU model. Rerun those splits with the same GPU, or note the mix in the report. |
| Out of memory | The script retries with batch 16 x 2 by itself. With two experiments at once each has its own T4. |

## 13. First-session checklist

1. Phone-verify the account.
2. Create `csci935-dhan-shomadhan` (the zip) and `csci935-code` (`group3-starvenus.py`, `requirements.txt`, `choices.json`), both Private.
3. New Notebook > File > Import Notebook > `notebooks/runner.ipynb`; Input > add both datasets.
4. Session options: Accelerator **GPU T4 x2**, Internet **On**.
5. First cell: `BATCHES_TO_RUN = ["batch3-core"]`.
6. Save Version > Save & Run All.
7. Watch the first 15 minutes of the log: GPU names, `torch ... already match the pin` (or the install), `dataset OK: 1106`, `smoke PASSED`, then the first epoch times of the sweeps.
8. When done: Output tab > `out.zip`, unpack as in section 8.

## Colab

The same notebook runs on Colab (the platform is detected). Nothing changed there:

1. Upload to `My Drive/csci935/`: `Dhan-Shomadhan.zip`, the latest `group3-starvenus.py`, `requirements.txt`, and for
   batches that read them `_work/results/choices.json`.
2. Open `notebooks/runner.ipynb` in Colab (File > Upload notebook), Runtime > Change runtime type > T4 GPU. Colab has one GPU,
   so `run_parallel` runs its experiments one after the other.
3. Set `BATCHES_TO_RUN` (or run the cells by hand), then Run all.
4. Results are synced to `My Drive/csci935/_work/runs/` after every split. Download that folder into
   `Dhan-Shomadhan/_work/runs/` and commit.
