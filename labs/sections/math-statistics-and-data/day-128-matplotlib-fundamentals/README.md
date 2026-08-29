# Day 128 lab — Plots You Can Assert On

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Matplotlib Fundamentals
- **Day number:** 128 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-128-matplotlib-fundamentals
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-128-matplotlib-fundamentals` when the site is running.
<!-- generated-links:end -->

## Purpose

Two lines of code look almost identical and behave completely differently.
`plt.plot(x, y)` draws into whichever figure happens to be "current" —
call a helper built that way twice and both calls silently land on the
same figure, with nobody having asked for that. `ax.plot(x, y)`, on a
named `ax` from `fig, ax = plt.subplots()`, cannot make that mistake,
because there is no "current" for it to guess at — every instruction says
exactly which Axes it means.

This lab builds nine small, checkable pieces of that distinction and the
practices that follow from it: the object model (Figure holds Axes, Axes
holds Artists), `savefig`'s exact pixel arithmetic, subplot grids as
genuinely independent Axes, what a log scale actually does to a
zero-valued point (nothing dramatic — it just silently stops drawing it),
the label-then-legend pattern, the figure-lifecycle leak that a
non-interactive report script can accumulate for hours before a memory
warning ever fires, and the concrete difference between a raster and a
vector output file. Every exercise is checked by reading state directly
off the Figure and Axes objects matplotlib returns — never by comparing
rendered pixels to a stored "golden" image, which is fragile across
fonts, DPI and matplotlib versions in a way that artist-state assertions
are not.

## Learning objectives

By the end you will be able to:

- Explain why the pyplot state-machine API (`plt.plot`, `plt.xlabel`) and
  the object API (`fig, ax = plt.subplots()`, then `ax.plot`,
  `ax.set_xlabel`) behave differently when a drawing routine is called
  more than once, and demonstrate the difference with `plt.get_fignums()`.
- Name the three-level object model — Figure, Axes, Artist — and say what
  each level owns: a Figure holds one or more Axes; an Axes owns its
  plotted Artists, its labels, its limits and its ticks.
- Predict a saved PNG's exact pixel dimensions from `figsize` and `dpi`,
  and explain why `bbox_inches='tight'` breaks that exact arithmetic.
- Build a grid of subplots with `plt.subplots(nrows, ncols)`, read the
  shape of the returned Axes array, and demonstrate that each Axes in the
  grid is independent of every other.
- Set labels, a title and explicit axis limits, and demonstrate that an
  explicit `set_ylim` overrides autoscaling rather than being merged with
  it.
- Describe exactly what `set_yscale('log')` does to a data point with
  value zero or negative — it does not raise, and it does not always
  warn — and demonstrate the effect by inspecting `ax.get_ylim()`.
- Apply the label-then-legend pattern and verify a legend's text and
  order by reading `ax.get_legend().get_texts()`.
- Explain matplotlib's figure lifecycle, reproduce the leak that follows
  from plotting in a loop without `plt.close()`, and trigger matplotlib's
  own too-many-open-figures warning for real.
- State the concrete, testable difference between a raster (PNG) and a
  vector (SVG) output — one contains text as literal markup, the other
  does not — and choose between them for a given downstream use.
- Test a chart by asserting on its artists (`ax.get_xlabel()`,
  `len(ax.lines)`, `ax.lines[0].get_xydata()`, `ax.get_yscale()`) instead
  of diffing image bytes, and explain why that approach is more robust.

## Prerequisites

- Day 91 — running and reading pytest output, this lab's testing pattern.
- Days 71-74 — installing packages with `pip` into a virtual environment.
- Day 43 — `python3 -m venv` and `pip install -r requirements.txt`.
- Comfort with Python functions, tuples, and reading a stack trace.
- No prior matplotlib experience is assumed — this lab and its lesson
  build the object model from the ground up.

## Supported operating systems

- macOS — run and captured here (macOS 26.5.2, Apple Silicon, arm64).
- Linux — the same commands apply unchanged. Not run here.
- Windows — use the Windows Subsystem for Linux and follow the Linux
  instructions, or Git Bash with `.venv\Scripts\python.exe` in place of
  `.venv/bin/python3`. Not run here; `troubleshooting.md` says so plainly.

## Hardware requirements

Anything that runs Python. Every chart in this lab is a handful of points
rendered headlessly to a temporary file; the heaviest single operation is
saving a figure at 200 dpi, well under a tenth of a second. Roughly 90 MB
of disk for the virtual environment, almost all of it matplotlib and its
own dependencies (contourpy, fonttools, kiwisolver, pillow).

## Required software

- `python3` — 3.14.0 here.
- `matplotlib` 3.11.1, `numpy` 2.5.2 and `pytest` 9.1.1, installed into a
  lab-local virtual environment from `requirements/requirements.txt`.
- `bash` — 3.2.57 here, for the test harness.

## Free and open-source options

All three dependencies are free and open source and there is no paid tier
of anything in this lab. matplotlib is distributed under its own
BSD-compatible licence, NumPy under BSD 3-Clause, and pytest under MIT. No
account, no key, no signup, personally or commercially.

`seaborn` (installed in the authoring environment, not imported by this
lab — see Day 129), `plotnine` and `plotly` are all free and open source
too; `plotnine` and `plotly` are not installed here and are described from
documentation only in the lesson's Tools section. `plotly`'s static-image
export (via the separate `kaleido` package) and its paid Dash Enterprise
product are the only parts of that ecosystem with a commercial tier —
interactive charts in a notebook or exported HTML are free.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-128-matplotlib-fundamentals
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import matplotlib; print(matplotlib.__version__)"
```

Expect `3.11.1`. That is the only time this lab needs the network.

## File structure

```
.
├── README.md                                     this file
├── metadata.yml                                   how the lab was actually run, and when
├── requirements/
│   ├── README.md                                  why each package is here, its licence, and what seaborn/plotnine/plotly would add
│   └── requirements.txt                           matplotlib==3.11.1, numpy==2.5.2, pytest==9.1.1
├── starter/                                        your work goes here
│   ├── 00_brief.md                                 the nine exercises, in order
│   ├── conftest.py                                 makes this directory's own module the one its tests import
│   ├── plotting.py                                 all nine exercises — functions to write
│   └── test_starter.py                             your running score; unattempted work skips
├── examples/                                       the reference, to read after you have tried
│   ├── conftest.py                                 the same import guard
│   ├── plotting.py                                 the finished nine functions
│   ├── 01_the_two_apis.py                          the bug: two plt.* calls land on one figure; two fig,ax calls do not
│   ├── 02_data_round_trip.py                       ax.lines[0].get_xydata() equals the input arrays exactly
│   ├── 03_pixel_arithmetic.py                      figsize x dpi predicts the saved PNG's pixel size exactly
│   ├── 04_labels_limits_and_scales.py               set_ylim overrides autoscaling
│   ├── 05_subplots.py                              plt.subplots(2, 3) returns an independent (2, 3) Axes array
│   ├── 06_log_scale_drops_nonpositive.py            a zero-valued point silently falls outside a log-scale view
│   ├── 07_legends.py                               legend text matches the labels supplied, in order
│   ├── 08_figure_leak.py                           unclosed figures accumulate; matplotlib's own warning fires past 20
│   ├── 09_vector_versus_raster.py                  SVG carries text as markup; PNG does not
│   └── test_reference.py                           19 tests over real artist state and real exceptions
├── tests/
│   └── run_tests.sh                                the bash harness: 34 checks, exits non-zero on any failure
├── expected-output/                                captured from real runs on 2026-08-20
│   ├── FIELDS.md                                   what may legitimately differ on your machine
│   ├── 01-the-two-apis.txt
│   ├── 02-data-round-trip.txt
│   ├── 03-pixel-arithmetic.txt
│   ├── 04-labels-limits-and-scales.txt
│   ├── 05-subplots.txt
│   ├── 06-log-scale-drops-nonpositive.txt
│   ├── 07-legends.txt
│   ├── 08-figure-leak.txt
│   ├── 09-vector-versus-raster.txt
│   └── test-run.txt
├── troubleshooting.md
└── security.md
```

## How to run

Read `starter/00_brief.md` first. Then work, checking yourself as you go:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `1 passed, 13 skipped`. A skip means
"not attempted"; a failure means "attempted and wrong", and prints both
your answer and the real one.

Afterwards, read the reference — each script prints its working and
asserts every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_the_two_apis.py
../.venv/bin/python3 02_data_round_trip.py
../.venv/bin/python3 03_pixel_arithmetic.py
../.venv/bin/python3 04_labels_limits_and_scales.py
../.venv/bin/python3 05_subplots.py
../.venv/bin/python3 06_log_scale_drops_nonpositive.py
../.venv/bin/python3 07_legends.py
../.venv/bin/python3 08_figure_leak.py
../.venv/bin/python3 09_vector_versus_raster.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `plotting.py` from
beside themselves.

Then the full harness:

```bash
bash tests/run_tests.sh
echo "exit=$?"
```

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 -m venv .venv` | Creates a virtual environment inside the lab, so nothing here can affect the rest of your machine. `rm -rf .venv` is a complete undo. |
| `.venv/bin/pip install -r requirements/requirements.txt` | Installs matplotlib 3.11.1, numpy 2.5.2 and pytest 9.1.1. The one command that uses the network. |
| `.venv/bin/pytest starter -q` | Your running score. Unattempted exercises skip; wrong answers fail with both values printed. |
| `01_the_two_apis.py` | Two `plt.*` calls land on one figure with two lines; two `fig, ax` calls produce two figures with one line each. |
| `02_data_round_trip.py` | Plots an array, reads it back off the Line2D artist, and checks exact equality. |
| `03_pixel_arithmetic.py` | Saves the same figure at three DPI values and reads each PNG's pixel size from its own file header. |
| `04_labels_limits_and_scales.py` | Compares autoscaled y-limits against an explicit `set_ylim` on the same Axes. |
| `05_subplots.py` | Builds a 2x3 grid, checks its shape, and confirms a label on one cell never appears on another. |
| `06_log_scale_drops_nonpositive.py` | Plots data containing a zero, switches to a log y-scale, and inspects where the zero point ends up. |
| `07_legends.py` | Plots two labelled series and checks the legend's text and order. |
| `08_figure_leak.py` | Opens figures without closing them, triggers matplotlib's own >20-figures warning, then closes everything. |
| `09_vector_versus_raster.py` | Saves the same figure as PNG and SVG and searches each file's bytes for the axis label. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 19 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 34-check harness: versions, every script, both suites, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
34 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `19 passed`, and an untouched
starter with `1 passed, 13 skipped`.

The result worth recognising before you meet it, from exercise 1:

```
pyplot-style: plt.get_fignums() = [1]
pyplot-style: lines on that one figure = 2
pyplot-style: BOTH calls landed on the same current figure -- this is
the bug. Two experiments' curves, overlaid, with nobody asking for that.

object-style: plt.get_fignums() = [1, 2]
object-style: lines on figure A = 1, on figure B = 1
```

`expected-output/FIELDS.md` records exactly which captured numbers are
version-specific and will differ, in documented ways, on your machine.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `34 checks, 0 failure(s).`
   and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `19 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `14 passed`
   once you have finished, and never prints a failure you have not been
   shown.
4. Each of the nine reference scripts ends with `every assertion held.`
5. `find . -path ./.venv -prune -o -type f \( -name '*.png' -o -name '*.svg' -o -name '*.pdf' \) -print`
   prints nothing after a full run.

## Tests

`tests/run_tests.sh` runs 34 checks in six sections:

1. **Versions** — reads the installed matplotlib and compares it against
   `requirements/requirements.txt`, confirms it is matplotlib 3 or later,
   and confirms the backend is the headless Agg.
2. **The nine reference scripts** — each must exit 0 and print that every
   one of its internal assertions held.
3. **The reference pytest suite** — must exit 0, report no failures, and
   have collected at least 15 tests, so a collection error cannot pass as
   success.
4. **The starter suite** — must exit 0 on an untouched checkout with
   skips rather than failures; and collecting both suites at once must not
   turn any of those skips into passes, which is a real hazard here
   because both directories contain a module called `plotting`.
5. **A deliberate failure** — the harness re-runs the legend exercise
   with the reference function's label order monkeypatched to be wrong,
   and asserts the re-run reports the named failure and exits non-zero. A
   green suite proves nothing until you have watched it go red.
6. **A clean disk** — no `__pycache__`, no `.pytest_cache`, and no
   `.png`/`.svg`/`.pdf` file left anywhere outside `.venv`, and no source
   file that opens a network connection.

Before section 1, the harness clears any `__pycache__` and `.pytest_cache`
that an **earlier** command left behind, pruning `.venv` as it goes. This
matters more than it sounds. The README above tells you to run
`.venv/bin/pytest starter -q`, and that command legitimately writes
`starter/__pycache__` and `.pytest_cache`. Without the pre-run clear,
section 6 would then report those as litter — failing you for following
the instructions in this file. Clearing them at the start makes the final
check measure what *this* run left behind.

The harness was confirmed to exit 0 on a fresh lab-local `.venv` created by
the documented setup commands, and to correctly report a non-zero exit and
a named failure when section 5 deliberately breaks one assertion. `.venv`
is the documented setup, not a stray file, and nothing in the suite treats
it as one or deletes anything inside it.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: resets your work
```

The lab's own commands leave none of the above behind; every image file
it saves lives in a `tempfile.TemporaryDirectory()` that deletes itself,
and section 6 of the harness fails if a stray one appears. It deliberately
does not look inside `.venv`, because the bytecode caches shipped with
matplotlib, NumPy and pytest are theirs, not yours.

## Troubleshooting

See `troubleshooting.md`. It covers wrong-directory import errors, the
starter tests that keep skipping because a function still raises
`NotImplementedError`, the `bbox_inches='tight'` mistake that breaks the
pixel-arithmetic exercise, the `fig.canvas.draw()` step a log-scale
readback needs, the `__pycache__` search that must prune `.venv`, and the
import collision the two `conftest.py` files prevent. All of them were
hit while building this lab or are named by a test.

## Security notes

See `security.md`. In short: this lab draws and saves charts to a
temporary directory that deletes itself, opens no connection after the
one-time install, needs no credentials and no `sudo`, and all the plotted
data is invented. One point there is worth carrying away: a plotting
helper written against the pyplot state machine is a shared-mutable-state
bug wearing a data-visualization costume — it draws into "whichever
figure is current" and silently overlays unrelated results when called
more than once, which is exactly the training-curve and evaluation-plot
mistake the lesson's AI thread is about.

## Extension exercises

1. **Measure the SVG size cost of `bbox_inches='tight'`.** Save the same
   figure as SVG with and without `bbox_inches='tight'`, and compare the
   resulting `viewBox` and file size. Confirm which one actually changes
   and which stays fixed.
2. **Find the smallest figure count that reliably triggers the
   too-many-open-figures warning on your machine.** Exercise 8 uses 22;
   binary-search `matplotlib.rcParams['figure.max_open_warning']` to
   confirm the threshold is exactly one more than that rcParam's value.
3. **Build a fourth API-mixing bug.** Write a function that creates
   `fig, ax = plt.subplots()` but then calls `plt.xlabel(...)` (the
   pyplot function, not `ax.set_xlabel`) after a second figure has been
   created elsewhere. Assert which Axes actually receives the label, and
   explain why in a comment.
4. **Add a tenth exercise: `constrained_layout` versus `tight_layout`.**
   Build a `plt.subplots(2, 2)` grid with long titles that overlap by
   default, apply each layout engine in turn, and assert on
   `fig.get_constrained_layout()` or the Axes' bounding boxes to show the
   overlap is resolved.
5. **Measure PNG size versus dpi.** Save the same figure at five dpi
   values from 50 to 400, record each file's byte size alongside its
   pixel dimensions from `png_dimensions`, and confirm file size grows
   roughly with pixel count while staying far from a simple linear
   relationship (PNG compression varies with image content).

## Navigation

- Previous day: Day 127 — Why We Visualize, and Choosing the Right Chart
- Next day: Day 129 — Statistical Plots with seaborn
- Week 19: Data Visualization
- Section: Mathematics, Statistics and Data
