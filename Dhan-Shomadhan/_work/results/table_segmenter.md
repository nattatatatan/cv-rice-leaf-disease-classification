# Salient-leaf segmenter (S-seg, one per split)

Mean +- std over the 5 split-segmenters (std with ddof=1). Eval annotations: the 20 hand-annotated field images that are looked at once per final segmenter. IoU and Dice compare the post-processed mask (the selected component; a fallback scores 0) with the annotated polygon at 512x256. Hit: the crop box (with the 15% margin, at the classifier's input aspect) contains at least 50% of the annotated leaf area; a fallback box is the whole image. Fallback: no component covers 2% of the image, so the whole image is used. The validation IoUs threshold the raw mask at 0.5.

| Metric | Images per split | Mean +- std | Per split (0-4) |
| --- | --- | --- | --- |
| IoU, eval annotations | 20 | pending | pending |
| Dice, eval annotations | 20 | pending | pending |
| Salient-leaf hit rate (%), eval annotations | 20 | pending | pending |
| Crop box area (% of the image), eval annotations | 20 | pending | pending |
| IoU, eval annotations without the ambiguous ones | 15 | pending | pending |
| Dice, eval annotations without the ambiguous ones | 15 | pending | pending |
| Salient-leaf hit rate (%), eval annotations without the ambiguous ones | 15 | pending | pending |
| Crop box area (% of the image), eval annotations without the ambiguous ones | 15 | pending | pending |
| Fallbacks on the eval annotations (%) | 20 | pending | pending |
| Fallbacks, all cached white images (%) | - | pending | pending |
| Fallbacks, all cached field images (%) | - | pending | pending |
| IoU, white val pseudo-masks (checkpoint data) | - | pending | pending |
| IoU, val composites (checkpoint data) | - | pending | pending |
