# Day 112 lab — the brief

Eight exercises across three files, in order. Work top to bottom: `gridviz.py`
before `imaging.py`, and `imaging.py`'s later functions before its earlier
ones' consumers. `dataset.py` is given to you — the loss surfaces and the
descent loop are Day 111's subject, not this one.

Check yourself at any point:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `13 skipped`. A **skip** means "not
attempted". A **failure** means "attempted and wrong", and it prints your
answer beside the real one. When every test passes, you are finished.

---

## Exercise 1 — `gridviz.py`, `evaluate_grid`

`numpy.meshgrid` plus a function call. Every picture later in this lab starts
here.

## Exercise 2 — `gridviz.py`, `ascii_contour`

Rescale a 2D array to a small number of character bands and print it. Get the
row/column order wrong and a symmetric bowl stops looking symmetric — in a
terminal, immediately, with no image viewer required.

## Exercise 3 — `imaging.py`, `heatmap_array` and `heatmap_png`

Turn `evaluate_grid`'s output into an image. `heatmap_array` does the one
deliberate axis flip in this lab (`numpy.flipud`); `heatmap_png` wraps it in
`Image.fromarray` and `img.save`.

## Exercise 4 — `gridviz.py`'s `world_to_pixel`, and `imaging.py`'s
`draw_path_on_heatmap`

`world_to_pixel` is the one function every other drawing function in this lab
calls instead of repeating the arithmetic — get it right once, here, and
everything downstream is right too. Then draw a descent path over its
heatmap with `PIL.ImageDraw.line` and `.ellipse`.

## Exercise 5 — `imaging.py`, `loss_curve_points` and `loss_curve_png`

Map a loss sequence to pixel coordinates — on a linear axis directly, on a
log axis via `numpy.log10` — then draw it. Remember pixel row 0 is the TOP:
a larger data value must produce a SMALLER pixel row on both axes.

## Exercise 6 — `imaging.py`, `animated_descent_gif`

One GIF frame per step, built by re-using exercise 4's drawing approach on a
growing prefix of the path. `Image.save(..., save_all=True,
append_images=...)` is the entire animation mechanism.

## Exercise 7 — `descent.py`, `sweep_final_loss` and `learning_rate_sweep`

Run a 1D descent at a given learning rate and report the final loss — or
`float('inf')` if it diverged. A learning rate above the stability threshold
makes the run overflow float64, which must be caught deliberately with
`numpy.errstate`, not allowed to raise.

## Exercise 8 — `descent.py`, `path_length`

Total Euclidean distance travelled along a path. One line: `numpy.diff` plus
`numpy.linalg.norm`. This is the number that tells two runs with
near-identical final losses apart.

---

## When you are done

Read the reference and run every script:

```bash
cd examples
../.venv/bin/python3 01_grid_and_ascii.py
../.venv/bin/python3 02_heatmap_and_path.py
../.venv/bin/python3 03_loss_curves.py
../.venv/bin/python3 04_animated_gif.py
../.venv/bin/python3 05_learning_rate_sweep.py
../.venv/bin/python3 06_two_runs_same_loss.py
cd ..
```

Script 6 is the one to read even if you read nothing else: two runs land
within a few percent of the same final loss, and their path lengths differ
by more than 13x.
