# Annotation guide: 30 salient-leaf polygons (T6.1)

Time box: **about 1.5 hours** (3 minutes per image). Stop at 2 hours even if images are left and tell the team; do not
polish. The result is the only real field ground truth we have, so it is judged by IoU in the report, but one slightly
loose polygon does not change a conclusion.

## What you produce

One polygon per image on 30 field images (6 per class: 2 `dev` + 4 `eval`), label `leaf`. The segmenter of phase 06 is
measured against these polygons. `dev` images may be used to tune the pipeline, `eval` images are looked at once, so
**annotate all 30 in the same way** and do not tune your polygons after seeing model output.

## 1. Install labelme (once)

labelme is a dev-only tool (it is not part of the submitted `.py`). It is listed in `requirements-dev.txt` and was checked
on Python 3.12 / macOS arm64: it adds 24 packages (PySide6 is the large one, about 450 MB) and does not change any pinned
package (numpy, OpenCV, torch, ... stay as they are).

```sh
uv pip install --python .venv/bin/python -r requirements-dev.txt     # or: .venv/bin/pip install -r requirements-dev.txt
.venv/bin/labelme --version                                          # Labelme 7.8.1
```

## 2. Get the images

`prepare` copies the 30 selected **cached** images (portrait, 1280 px long side) to
`Dhan-Shomadhan/_work/annotations/images/`. It also writes the list `_work/annotations/selection.json`. If the folder is
missing or empty:

```sh
.venv/bin/python group3-starvenus.py prepare        # idempotent, a couple of minutes
```

Annotate **these copies, never the originals in `Field Background  /`**: the coordinates must match the pixels the code sees
(the converter rejects files with another image size).

## 3. Open labelme

From the repo root:

```sh
.venv/bin/labelme Dhan-Shomadhan/_work/annotations/images \
    --output annotations/labelme --labels leaf --flags ambiguous --validate-label exact
```

* `--labels leaf` and `--validate-label exact`: `leaf` is the only label that is accepted.
* `--flags ambiguous`: adds an **ambiguous** tick box in the "Flags" panel (it applies to the whole image).
* `--output annotations/labelme`: the JSON files are written here (one per image, saved automatically when you move to the
  next image; no image data inside, so they are small). Commit this folder when you are done: it is the raw source of the
  annotations. If you quit and re-open labelme with the same command, finished images show their polygon again.

Keys: **Ctrl+N** (or right-click, "Create Polygon") starts a polygon, click along the outline, close it by clicking the first
point (or Enter), type or pick `leaf`, OK. **D** = next image, **A** = previous. Zoom with the scroll wheel (hold Ctrl) when the
outline is fiddly. Edit a vertex by dragging it; delete a polygon with Delete.

## 4. The protocol (this text goes verbatim into the report)

**Protocol for "salient leaf":**

1. The leaf that is in focus, shows disease symptoms, and is closest to the image centre.
2. If several qualify, the one with the largest visible area.
3. Trace only visible parts; exclude leaves crossing in front of it.
4. If no single leaf is clearly salient, still annotate the best candidate and set the flag `ambiguous: true`.

Practical notes:

* Exactly **one** polygon per image. Do not add a second leaf, points, lines or rectangles; the converter rejects those.
* 20 to 40 clicks are plenty (the converter simplifies to at most 60 vertices). Follow the leaf edge, cut across a
  leaf tip you cannot see, do not trace lesions separately; a lesion on the leaf is inside the polygon.
* Where another leaf crosses in front, run the outline along the front leaf's edge (the covered part is not in the polygon).

## 5. Mark an image as ambiguous

Tick **ambiguous** in the Flags panel (left or right dock) while that image is open, in addition to drawing the polygon of the
best candidate. Use it when you could not say, in two seconds, which leaf the photographer aimed at (several equally
sharp and symptomatic leaves, or none in focus). Do not use it for "the outline was hard to draw". Expect a few of the 30.

## 6. Convert, embed, check

```sh
.venv/bin/python tools/labelme_to_annotations.py          # annotations/labelme/*.json -> annotations/field_salient_leaf.json
.venv/bin/python tools/export_py.py                       # embeds the polygons as FIELD_ANNOTATIONS
.venv/bin/python group3-starvenus.py prepare              # also draws _work/figures/annotations_overview.png
```

The converter checks that all 30 selected images have exactly one `leaf` polygon and tells you about missing files, extra
files and wrong shapes, and writes nothing until every image is fine. It prints the polygon count and the vertex count before
and after simplification. Then **open `_work/figures/annotations_overview.png`** (5 rows = classes, 2 `dev` + 4 `eval`
columns, outline in yellow, `?` = ambiguous) and check that every outline is on the leaf you meant. Fix a wrong one in
labelme and re-run the three commands. Finally commit `annotations/labelme/`, `annotations/field_salient_leaf.json` and the
regenerated `group3-starvenus.py`.
