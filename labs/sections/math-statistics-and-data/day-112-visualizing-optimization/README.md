# Day 112 lab — Seeing the Descent

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Visualizing Optimization
- **Day number:** 112 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-112-visualizing-optimization
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-112-visualizing-optimization` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 111 gave you a working gradient-descent loop. This lab gives you the
ability to look at what it actually did — because a final loss number cannot
tell you that.

Two runs in `examples/06_two_runs_same_loss.py` start at the same point, use
the same learning rate, and take the same number of steps. Their final losses
land within 3% of each other. If that number were the only thing you ever
looked at, you would call the runs equivalent. Draw the paths and they are
not: one is short and nearly straight; the other is over 13x longer because
it spent most of its steps bouncing across a narrow valley. The final-loss
number hid the thing that actually mattered.

The lab builds, from nothing but NumPy arrays and Pillow's `ImageDraw`, the
four pictures that diagnose an optimisation run:

1. **Loss against iteration, on a log axis.** For the well-conditioned bowl
   here the update is an exact geometric recursion, so `log10(loss)` against
   iteration is provably a straight line — the lab fits one to the drawn
   pixel coordinates and measures the residual, rather than asserting it in
   prose.
2. **The contour map with the path drawn on top of it.** The only picture
   that shows *why* a run was slow: the zig-zag across a narrow valley is
   obvious here and invisible in the loss curve alone.
3. **Gradient norm and path length**, which distinguish "converged" from
   "stopped for another reason" — the number the whole lab is built around.
4. **A learning-rate sweep**, final loss against eta, which has a
   characteristic shape: slow on the left, a broad basin of good rates, then
   a cliff where the run diverges — caught deliberately as `float('inf')`
   rather than allowed to raise.

**No matplotlib, no scipy, in this environment.** The lab's `heatmap_png` and
`draw_path_on_heatmap` do, by hand, what `matplotlib.pyplot.contourf` and
`plt.plot` do for you: evaluate a function over a grid with
`numpy.meshgrid`, map values to colours, and place pixels. `requirements/README.md`
and the lesson's Tools section describe matplotlib, Plotly, TensorBoard and
Weights & Biases from their documentation and state plainly that no output
from any of them is reproduced here.

## Learning objectives

By the end you will be able to:

- Evaluate a function over a 2D grid with `numpy.meshgrid` and locate its
  minimum from the resulting array.
- Render a 2D array as a terminal contour map by mapping values to level
  bands, and explain why a transposed grid or a flipped axis fails loudly in
  that rendering.
- Build a heatmap image from a value array using only `PIL.Image` and a
  hand-written colour ramp.
- Write a correct world-to-pixel coordinate transform, and explain which
  axis has to flip and why.
- Draw a path over a heatmap with `PIL.ImageDraw` and verify, in pixels, that
  it starts and ends where it should.
- Explain why loss should be read on a log axis for a linearly-convergent
  method, and prove that a specific run's log-scale points are collinear.
- Build an animated GIF with `Image.save(..., save_all=True)` and verify its
  frame count.
- Run a learning-rate sweep that catches divergence (overflow to `inf`)
  deliberately instead of letting it raise or warn.
- Use path length, not final loss alone, to tell two optimisation runs apart.
- State, for each of matplotlib, Pillow, Plotly, TensorBoard and Weights &
  Biases, when to choose it and what it costs.

## Prerequisites

- Day 111 — gradient descent from scratch: the update rule
  `x <- x - eta * grad(x)` and the three learning-rate regimes for a
  quadratic. This lab implements its own descent loop rather than importing
  Day 111's, but assumes you already know what the loop is doing.
- Day 109 — partial derivatives and the gradient, which is what `grad(x)`
  computes at each step.
- Day 104 — NumPy arrays and vectorized thinking, including
  `numpy.meshgrid`.
- Day 43 — `python3 -m venv` and installing a package with `pip`.
- Days 71-74 — running pytest and reading its output.
- No image-processing background assumed. Every Pillow call used here is
  explained at first use.

## Supported operating systems

- macOS — run and captured here (macOS 26.5.2, Apple Silicon, arm64).
- Linux — the same commands apply unchanged. Not run here.
- Windows — use the Windows Subsystem for Linux and follow the Linux
  instructions, or Git Bash with `.venv\Scripts\python.exe` in place of
  `.venv/bin/python3`. Not run here; `troubleshooting.md` says so plainly.

## Hardware requirements

Anything that runs Python. The largest image this lab draws is 101x101
pixels; the largest computation is a 300-step 1D descent repeated 25 times
for the learning-rate sweep. Nothing here is a benchmark, nothing is timed,
and the whole suite finishes in well under a second. Roughly 60-70 MB of
disk for the virtual environment.

## Required software

- `python3` — 3.14.0 here.
- `numpy` 2.5.2, `Pillow` 12.3.0 and `pytest` 9.1.1, installed into a
  lab-local virtual environment from `requirements/requirements.txt`.
- `bash` — 3.2.57 here, for the test harness.

## Free and open-source options

All three dependencies are free and open source and there is no paid tier of
anything in this lab. NumPy is BSD 3-Clause, Pillow is the MIT-CMU licence,
pytest is MIT. No account, no key, no signup, personally or commercially.

If you cannot install Pillow, `evaluate_grid` and `ascii_contour` still work
with only NumPy — the ASCII contour renderer is a genuinely complete
diagnostic on its own, without an image viewer. Every PNG and the GIF need
Pillow directly; there is no standard-library substitute. `requirements/README.md`
states this cost plainly.

Four other tools do parts of this job and **none of them is installed here,
so no output from any of them is reproduced anywhere in this lab or its
lesson**: matplotlib (`pyplot.contour`/`contourf`), Plotly (interactive
HTML), and TensorBoard and Weights & Biases (live training-curve dashboards,
the latter free for individuals and paid for teams). The lesson's
Alternatives section describes all four from their documentation and says
so.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-112-visualizing-optimization
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy, PIL; print(numpy.__version__, PIL.__version__)"
```

Expect `2.5.2 12.3.0`. That is the only time this lab needs the network.

## File structure

```
.
├── README.md                            this file
├── metadata.yml                         how the lab was actually run, and when
├── requirements/
│   ├── README.md                        why each package is here, its licence, and the no-Pillow path
│   └── requirements.txt                 numpy==2.5.2, Pillow==12.3.0, pytest==9.1.1
├── starter/                             your work goes here
│   ├── 00_brief.md                      the eight exercises, in order
│   ├── conftest.py                      makes this directory's modules the ones its tests import
│   ├── dataset.py                       given: the two bowls, the descent loop, the tolerances
│   ├── gridviz.py                       exercises 1, 2, 4a — evaluate_grid, ascii_contour, world_to_pixel
│   ├── descent.py                       exercises 7, 8 — the learning-rate sweep, path_length
│   ├── imaging.py                       exercises 3, 4b, 5, 6 — the heatmap, the drawn path, the loss curves, the GIF
│   └── test_starter.py                  your running score; unattempted work skips
├── examples/                            the reference, to read after you have tried
│   ├── conftest.py                      the same import guard
│   ├── dataset.py                       the two bowls, the descent loop, the derived tolerances
│   ├── gridviz.py                       the finished grid and pixel functions
│   ├── descent.py                       the finished descent, path length and sweep
│   ├── imaging.py                       the finished heatmap, path, loss-curve and GIF drawing
│   ├── 01_grid_and_ascii.py             evaluate a bowl over a grid; see it in a terminal
│   ├── 02_heatmap_and_path.py           the heatmap PNG, and a descent path drawn on it
│   ├── 03_loss_curves.py                linear vs. log axis, and the collinearity proof
│   ├── 04_animated_gif.py               one GIF frame per step
│   ├── 05_learning_rate_sweep.py        final loss against eta: the basin and the cliff
│   ├── 06_two_runs_same_loss.py         the day's opening claim, as a measurement
│   └── test_reference.py                the reference suite: nine checks, one per exercise
├── tests/
│   └── run_tests.sh                     the bash harness: exits non-zero on any failure
├── expected-output/                     captured from real runs on the date in metadata.yml
│   ├── FIELDS.md                        what may legitimately differ on your machine
│   ├── 01-grid-and-ascii.txt
│   ├── 02-heatmap-and-path.txt
│   ├── 03-loss-curves.txt
│   ├── 04-animated-gif.txt
│   ├── 05-learning-rate-sweep.txt
│   ├── 06-two-runs-same-loss.txt
│   ├── reference-tests.txt
│   ├── starter-progress.txt
│   └── test-run.txt
├── troubleshooting.md
└── security.md
```

## How to run

Read `starter/00_brief.md` first. Then work, checking yourself as you go:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `13 skipped`. A skip means "not
attempted"; a failure means "attempted and wrong", and prints both your
answer and the real one.

Afterwards, read the reference — each script prints its working and asserts
every claim it makes:

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

Every image these scripts write goes into a temporary directory that is
removed before the script exits. Nothing is left in the lab.

## What the commands do

- `evaluate_grid` calls `numpy.meshgrid` once and applies the loss function
  to the result — the single building block every picture in this lab is
  made from.
- `heatmap_png` rescales the grid to `[0, 1]`, maps it through a four-stop
  colour ramp with `numpy.interp`, and saves the result with
  `PIL.Image.fromarray(...).save(...)`.
- `draw_path_on_heatmap` maps every point on a descent path to a pixel with
  `world_to_pixel` and draws a polyline plus a marker per step with
  `PIL.ImageDraw`.
- `loss_curve_png` maps a loss sequence (or its `log10`) to pixel
  coordinates with the same linear-rescale idea, then draws axes, a
  polyline and markers.
- `animated_descent_gif` builds one frame per step over a shared background
  and writes them all with a single `Image.save(..., save_all=True, ...)`
  call.
- `learning_rate_sweep` runs a 1D descent at each of a range of learning
  rates, catching overflow with `numpy.errstate` and recording it as
  `float('inf')` rather than letting it raise.

## Expected output

Captured verbatim in `expected-output/`. The two headline numbers, from
`06-two-runs-same-loss.txt`:

```
well-conditioned final loss: 2.431009e-03
ill-conditioned final loss:  2.507203e-03
relative gap between the two final losses: 0.0304

well-conditioned path length: 5.6075
ill-conditioned path length:  75.9767
ratio: 13.55x longer
```

## Validation steps

1. `.venv/bin/pytest starter -q` reports `13 skipped` on an untouched
   checkout and `13 passed` once every exercise is solved correctly.
2. `.venv/bin/pytest examples -q` reports all reference tests passing.
3. `bash tests/run_tests.sh` prints `N checks, 0 failure(s).` and exits 0.
4. After every command above, `find . -name '*.png' -o -name '*.gif'` from
   the lab directory returns nothing.

## Tests

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
bash tests/run_tests.sh
```

`tests/run_tests.sh` additionally proves itself capable of failing: it
re-runs itself with an unmeetable threshold and asserts that the re-run
reports exactly one failure and exits non-zero, before reporting its own
real result.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv  # optional: removes the lab virtual environment
git checkout -- starter/  # optional: reset your work
```

Nothing else needs cleaning. Every PNG and GIF this lab produces is written
into a temporary directory and removed before the producing script or test
returns.

## Troubleshooting

See `troubleshooting.md` for the axis-flip bug, the ASCII-ramp direction, GIF
palette conversion, overflow handling in the sweep, and the module-import
guard — every entry there was hit while building this lab.

## Security notes

See `security.md`. In short: no network access after installation, no
credentials, nothing written outside the lab directory or a temporary one it
removes itself.

## Extension exercises

1. **Marching squares.** `ascii_contour` and `heatmap_png` both shade by
   level BAND. Implement a simple marching-squares pass that traces actual
   level LINES between grid cells for one contour value, and compare the
   picture it produces to the shaded version.
2. **Momentum.** Add a velocity term to the descent loop
   (`v <- beta * v + grad(x); x <- x - eta * v`) and draw its path on the
   ill-conditioned bowl next to plain gradient descent's. Does it shorten
   the path, the final loss, or both?
3. **A third bowl.** Add a bowl that is rotated 45 degrees relative to the
   coordinate axes (a non-diagonal quadratic form) and confirm your
   `evaluate_grid` and `heatmap_png` still locate its minimum correctly —
   this is the case a purely-diagonal test suite like this lab's cannot
   catch on its own.
4. **Real matplotlib, if you have it elsewhere.** Reproduce
   `02_heatmap_and_path.py`'s picture with `plt.contourf` and `plt.plot` in
   an environment that has matplotlib installed, and compare the two
   images by eye. Do not paste matplotlib output into this lab's files —
   this environment does not have it, and the lab says so.

## Navigation

- Previous day: Day 111 — Gradient Descent from Scratch
- Next day: Day 113 — Probability: Events, Rules, and Intuition
