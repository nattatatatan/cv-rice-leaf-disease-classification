# Domain-wise and cross-domain experiments, test split

W->W is E1-WW, F->F is E1-FF, W->F is E1-WF (field is its main result, white the reference), U is E1-U. '-' marks subsets that a row is not about. Mean +- std over the 5 splits. Rows that are not complete yet read 'pending'.

| Experiment | Backbone | Train on | White macro-F1 | White accuracy (%) | Field macro-F1 | Field accuracy (%) | Mixed macro-F1 | Mixed accuracy (%) | Domain-balanced macro-F1 | Domain-balanced accuracy (%) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1-WW | resnet50 | white | 0.809 +- 0.037 | 83.0 +- 3.9 | - | - | - | - | - | - |
| E1-FF | resnet50 | field | - | - | 0.539 +- 0.128 | 55.2 +- 11.4 | - | - | - | - |
| E1-WF | resnet50 | white | 0.809 +- 0.037 | 83.0 +- 3.9 | 0.141 +- 0.039 | 24.5 +- 4.0 | - | - | - | - |
| E1-U | resnet50 | white + field | 0.802 +- 0.062 | 82.9 +- 5.2 | 0.687 +- 0.048 | 68.8 +- 4.6 | 0.772 +- 0.049 | 78.8 +- 4.6 | 0.744 +- 0.048 | 75.8 +- 4.3 |
| E2-cnx-WF | convnext_tiny | white | 0.805 +- 0.044 | 83.4 +- 4.4 | 0.442 +- 0.060 | 47.2 +- 4.8 | - | - | - | - |
| E2-swin-WF | swin_t | white | 0.809 +- 0.031 | 83.6 +- 3.7 | 0.300 +- 0.027 | 33.4 +- 3.0 | - | - | - | - |
