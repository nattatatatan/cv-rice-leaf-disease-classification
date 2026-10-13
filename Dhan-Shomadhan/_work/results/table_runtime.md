# Training and inference cost

Training time and seconds per epoch are the mean +- std (ddof=1) over the 5 runs of an experiment; a run's time includes validation after every epoch, and the time is wall clock on a machine whose load varied (shared Kaggle/Colab sessions, a laptop), so it is only comparable within one hardware group and only roughly. Early stopping makes the epochs run differ between runs. Hardware is read from env.json (the findings list the groups with their torch versions). E1-U and E1-WW are aliases that read the run folder named in the second column. Parameters are those of the classifier with its 5-class head. Inference time is not measured by `summarize` (it would not be reproducible): the `benchmark` command writes inference_benchmark.json and this table reads it. It times the model forward pass for one image (batch 1), not image decoding, resizing or the first call. Measured on - cpu: macOS-26.5-arm64-arm-64bit, 8 cores, no GPU, torch 2.11.0, rect input 448x224, fp32, median of 50 after 10 warm-up passes; mps: macOS-26.5-arm64-arm-64bit, 8 cores, Apple MPS, torch 2.11.0, rect input 448x224, fp32, median of 50 after 10 warm-up passes.

| Experiment | Run folder | Hardware | Training time per run (min) | Seconds per epoch | Epochs run | Parameters (M) | Inference ms/image, median (quartiles), cpu | Inference ms/image, median (quartiles), mps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E0-squash | E0-squash | Colab, cuda (Tesla T4) | 8.6 +- 2.5 | 19.7 +- 0.1 | 26.2 +- 7.6 | 23.5 | 63.2 (57.5-70.1) | 21.7 (20.1-23.5) |
| E0-pad | E0-pad | Colab, cuda (Tesla T4) | 8.7 +- 1.1 | 17.7 +- 0.2 | 29.4 +- 3.7 | 23.5 | 63.2 (57.5-70.1) | 21.7 (20.1-23.5) |
| E0-rect | E0-rect | Colab, cuda (Tesla T4) | 9.1 +- 1.5 | 19.7 +- 0.1 | 27.8 +- 4.6 | 23.5 | 63.2 (57.5-70.1) | 21.7 (20.1-23.5) |
| E1-U | E0-rect | Colab, cuda (Tesla T4) | 9.1 +- 1.5 | 19.7 +- 0.1 | 27.8 +- 4.6 | 23.5 | 63.2 (57.5-70.1) | 21.7 (20.1-23.5) |
| E1-WW | E1-WF | local macOS, mps (Apple MPS) | 42.1 +- 18.9 | 96.8 +- 40.8 | 26.0 +- 3.9 | 23.5 | 63.2 (57.5-70.1) | 21.7 (20.1-23.5) |
| E1-FF | E1-FF | local macOS, mps (Apple MPS) | 24.2 +- 16.2 | 53.1 +- 37.5 | 26.6 +- 7.6 | 23.5 | 63.2 (57.5-70.1) | 21.7 (20.1-23.5) |
| E1-WF | E1-WF | local macOS, mps (Apple MPS) | 42.1 +- 18.9 | 96.8 +- 40.8 | 26.0 +- 3.9 | 23.5 | 63.2 (57.5-70.1) | 21.7 (20.1-23.5) |
| E2-cnx-U | E2-cnx-U | Kaggle, cuda (Tesla T4) | 8.2 +- 2.1 | 19.8 +- 1.9 | 24.6 +- 5.7 | 27.8 | 857.4 (846.1-884.2) | 48.9 (45.2-54.9) |
| E2-cnx-WF | E2-cnx-WF | Kaggle, cuda (Tesla T4) | 6.0 +- 0.6 | 12.7 +- 1.4 | 28.8 +- 2.9 | 27.8 | 857.4 (846.1-884.2) | 48.9 (45.2-54.9) |
| E2-swin-U | E2-swin-U | Kaggle, cuda (Tesla T4) | 7.6 +- 2.1 | 18.9 +- 0.2 | 24.0 +- 6.6 | 27.5 | 78.3 (75.6-82.3) | 59.7 (56.8-62.0) |
| E2-swin-WF | E2-swin-WF | Kaggle, cuda (Tesla T4) | 5.5 +- 1.0 | 11.9 +- 0.1 | 27.6 +- 5.0 | 27.5 | 78.3 (75.6-82.3) | 59.7 (56.8-62.0) |
| E3-A | E3-A | Kaggle, cuda (Tesla T4) | 15.2 +- 6.3 | 36.9 +- 7.2 | 24.4 +- 7.4 | 27.5 | 78.3 (75.6-82.3) | 59.7 (56.8-62.0) |
| E3-A-WF | E3-A-WF | Kaggle, cuda (Tesla T4) | 14.9 +- 4.2 | 31.2 +- 3.6 | 28.2 +- 5.8 | 27.5 | 78.3 (75.6-82.3) | 59.7 (56.8-62.0) |
