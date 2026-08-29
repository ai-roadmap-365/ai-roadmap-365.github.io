# Day 130 lab — Pictures of a Distribution

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Distributions and Relationships
- **Day number:** 130 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-130-distributions-and-relationships
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-130-distributions-and-relationships` when the site is running.
<!-- generated-links:end -->

## Purpose

Nine numbered exercises, each proving one real fact about how NumPy,
seaborn and matplotlib picture a distribution — headless, via the `Agg`
backend, asserting on computed values and artist state rather than image
bytes. The through-line is that **a histogram, a KDE and a boxplot are
each one picture of the data, not the data itself**, and each hides
something a different picture shows. Exercise 5 makes that concrete as
directly as it can be made: two samples are engineered so their
five-number summaries — the entire content of a boxplot — agree to
within 0.3 units, and a histogram of either one at the same bin count
still shows 2 modes for one sample and 1 for the other. Every other
exercise adds one more parameter nobody thinks to ask about: the bin
width (1, 2), the KDE bandwidth and its boundary problem on strictly
positive data (3, 4), overplotting and its fixes (7), the difference
between a linear relationship and a monotonic one and a shaped one (8),
and the honest disclosure jitter requires (9).

## Learning objectives

By the end of this lab you will be able to:

- Demonstrate that the same 500-point sample looks unimodal at a coarse
  bin count and like noise at a fine one, and that
  `numpy.histogram_bin_edges(..., bins='fd')` recovers its real
  structure in between.
- Show that Sturges, Scott and Freedman-Diaconis choose three different
  bin counts on the same skewed sample, and name the statistic each rule
  is built from.
- Demonstrate that a KDE's bandwidth (`bw_adjust` in seaborn) is exactly
  as consequential as a histogram's bin width, by finding two modes at
  one bandwidth and one at another on the identical sample.
- Demonstrate, by direct integration of a KDE curve, that a KDE of
  strictly positive data places real, non-trivial probability mass below
  zero — and state why.
- Construct — or, having read `data.py`, explain — two samples that
  share a five-number summary within a tight tolerance while their
  histograms show a different number of modes, and say what a boxplot of
  either one would never have shown you.
- Confirm an ECDF passes through every observation and that its median
  reading matches `numpy.median` exactly.
- Quantify overplotting directly: convert data coordinates to pixel
  coordinates, count how many of 20,000 points collide onto the same
  pixel, and confirm a hexbin recovers a real density peak from the same
  cloud.
- Demonstrate that a strong quadratic relationship can have near-zero
  Pearson AND Spearman correlation, and that fitting the actual shape
  (or plotting it) is what reveals it.
- Apply jitter to discrete data, quantify exactly how far it moves each
  point, and confirm the source data is untouched.

## Prerequisites

- **Day 116** — descriptive statistics that don't lie, specifically
  Anscombe's quartet and the discipline of asking what a summary
  statistic discarded, which this lab's exercise 5 is a second, more
  extreme instance of.
- **Day 127** — why to visualize and how to choose a chart type.
- **Day 128** — matplotlib's object model and testing by asserting on
  artists, which every exercise in this lab that reads `ax.lines`,
  `ax.transData`, or a `hexbin`'s array depends on directly.
- **Day 129** — seaborn's axes-level/figure-level split and its
  statistical plots, which exercises 3, 4 and 6 (`kdeplot`, `ecdfplot`)
  build on without re-explaining.
- A working `python3` on your `PATH` to create the lab's virtual
  environment.

## Supported operating systems

| System | Status |
| --- | --- |
| macOS (Apple Silicon or Intel) | Captured here — macOS 26.5.2, arm64 |
| Linux (any current distribution) | Expected identical, given the pinned versions below and the headless `Agg` backend |
| Windows | Use WSL and follow the Linux path. `mktemp -d` is used inside `tests/run_tests.sh`; native Windows was not tested and no output is claimed for it |

## Hardware requirements

Anything. The largest sample in this lab is 20,000 points, generated in
memory; no GPU, no display, and no meaningful disk use beyond the
one-time package install.

## Required software

| Tool | Minimum | Used here | Why |
| --- | --- | --- | --- |
| `python3` | 3.11 | 3.14.0 | Runs everything; standard library `venv` builds the lab's environment |
| `seaborn` | 0.13.2 exactly | 0.13.2 | `kdeplot` (exercises 3, 4) and `ecdfplot` (exercise 6) |
| `matplotlib` | 3.11.1 exactly | 3.11.1 | `hist`, `scatter`, `hexbin`, and seaborn's own drawing engine underneath |
| `pandas` | 3.0.5 exactly | 3.0.5 | `.corr()` (exercise 8) |
| `numpy` | 2.5.2 | 2.5.2 | Every sample in `data.py`; `histogram_bin_edges`, `percentile`, `polyfit`, `trapezoid` |
| `pytest` | 9.1.1 | 9.1.1 | The test harness every exercise is written against |
| `bash` | 3.2 | 3.2.57 | The outer test harness |

Check your Python in one line: `python3 --version`.

## Free and open-source options

Everything here is free.

- **seaborn** (BSD 3-Clause), **matplotlib** (PSF-derived, BSD-style),
  **pandas** (BSD 3-Clause), **NumPy** (BSD 3-Clause) and **pytest**
  (MIT) are fully open source with no paid tier.
- **`scipy.stats.gaussian_kde`** (BSD 3-Clause, described from
  documentation only, **not installed** in this environment) is the
  general-purpose free KDE implementation the wider Python ecosystem
  reaches for outside a plotting call specifically.
- **plotnine** and **Vega-Lite / Altair** (both free and open source,
  described from documentation only, not run here) are grammar-of-
  graphics alternatives mentioned briefly in the lesson.

No account, no key, no paid tier, and no part of this lab is degraded
without one.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-130-distributions-and-relationships
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import seaborn; print(seaborn.__version__)"
```

If your tools live somewhere unusual, `tests/run_tests.sh` takes an
override rather than guessing:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## File structure

```text
day-130-distributions-and-relationships/
├── README.md                     this file
├── metadata.yml                  lab metadata and the recorded run
├── security.md                   what this lab does to your machine
├── troubleshooting.md            grouped by the message you actually see
├── requirements/
│   ├── README.md                  versions, and what each package is for
│   └── requirements.txt           seaborn==0.13.2, matplotlib==3.11.1, pandas==3.0.5, numpy==2.5.2, pytest==9.1.1
├── starter/                      YOUR work happens here
│   ├── 00_brief.md                exercise-by-exercise instructions
│   ├── data.py                    every sample this lab is built from
│   ├── conftest.py                fixtures wrapping data.py, headless Agg setup
│   └── test_distributions.py      nine exercises, each a pytest.skip to replace
├── examples/                     the reference. Read AFTER you have tried
│   ├── data.py
│   ├── conftest.py
│   └── test_distributions.py      the fully worked, 9-test answer key
├── tests/
│   └── run_tests.sh               16 checks of real behaviour
└── expected-output/               captured from a real run on 2026-08-20
    ├── FIELDS.md                   what must match, what is version-specific, and what is sampled
    ├── examples-run.txt            pytest examples -v -s, captured
    ├── starter-run.txt             pytest starter -v, captured (all skip)
    └── test-run.txt                the full harness run
```

## How to run

```bash
# 1. The reference suite. Read this AFTER you have tried the exercises,
#    never before -- it is the answer key.
.venv/bin/pytest examples
.venv/bin/pytest examples -v -s

# 2. Where you stand on the exercises. An untouched checkout reports
#    9 skipped, 0 failed.
.venv/bin/pytest starter -v

# 3. Your work: open starter/test_distributions.py and starter/00_brief.md,
#    and replace each pytest.skip(...) with real assertions.
.venv/bin/pytest starter -v -k test_01
.venv/bin/pytest starter -v -k test_02
# ... and so on through test_09, or just:
.venv/bin/pytest starter -v

# 4. Check everything, including the harness's own proof that it can fail.
bash tests/run_tests.sh
```

**Never run `pytest examples starter` in one command.** Both directories
define a module named `test_distributions.py`; pytest imports test
modules by their dotted name, and running both together was tested
directly in this lab and aborts collection outright with an `import file
mismatch` error before running a single test. Run them as two separate
commands, always, as shown above.

## What the commands do

**`.venv/bin/pytest examples`** runs the fully worked reference suite: 9
tests across the nine exercises, each asserting a real value read off a
real NumPy/seaborn/matplotlib/pandas computation built from one of the
samples in `data.py`.

**`.venv/bin/pytest starter`** runs your own suite. On an untouched
checkout, every one of the 9 tests calls `pytest.skip(...)` and is
reported as `s`, so the run exits 0 with nothing yet proven. Replace a
skip with real assertions and delete the skip line; when all 9 are
written and passing, the exercise is done.

**`bash tests/run_tests.sh`** confirms the installed packages match
`requirements.txt` exactly, runs `pytest examples` and requires 9
passed, runs `pytest starter` and requires 9 skipped on the checked-in
state, confirms `pytest examples starter` in one invocation aborts
collection with `import file mismatch` rather than silently letting one
shadow the other, then solves every exercise in a **scratch copy** made
with `mktemp -d` (never touching the real `starter/test_distributions.py`),
confirms that copy passes in full, deliberately breaks one assertion
inside it, confirms the run now exits non-zero with a failure reported,
restores the line, and confirms it passes again. It finishes by checking
no file in `examples/` or `starter/` contains a URL, that no image file
is left anywhere inside the lab, and that nothing is left on disk.

## Expected output

The harness ends with a real captured line:

```text
16 checks, 0 failure(s)
```

and exits 0. `pytest examples` ends with:

```text
9 passed in 0.27s
```

`pytest starter`, on the checked-in state, ends with:

```text
9 skipped in 0.17s
```

Exercise 2's rule disagreement, exactly as captured:

```text
sturges=10 scott=14 fd=21
```

Exercise 5's centrepiece, exactly as captured — two samples whose
five-number summaries agree to within 0.3 units of the same five target
numbers, while their histograms at 15 bins show a different number of
modes:

```text
bimodal 5-num: [10.21 28.02 40.   51.98 69.79] (2 modes at 15 bins)
unimodal 5-num: [10.17 28.06 40.   51.94 69.83] (1 mode at 15 bins)
```

The full capture of both suites is in `expected-output/`, and
`expected-output/FIELDS.md` says which values are exact everywhere,
which are specific to this seaborn/matplotlib/NumPy pin, and the one
place (exercise 8's Spearman correlation) where a direct measurement
turned out sharper than the day's own brief expected.

## Validation steps

1. `bash tests/run_tests.sh` ends with `16 checks, 0 failure(s)` and
   exits 0.
2. The same bimodal sample shows 1 mode at 5 bins and more than 10 at
   100 bins; `numpy.histogram_bin_edges(..., bins='fd')` on it recovers
   exactly 2 modes.
3. `numpy.histogram_bin_edges` with `'sturges'`, `'scott'` and `'fd'` on
   a skewed sample produce three different bin counts.
4. `sns.kdeplot(..., bw_adjust=1.0)` finds 2 modes on the bimodal sample;
   `bw_adjust=3.0` (over-smoothed) finds 1.
5. A KDE of a strictly positive sample places more than 3% of its total
   density below zero.
6. Two engineered samples' five-number summaries agree within 0.3 units
   of five shared target values, yet their histograms at 15 bins show 2
   modes and 1 mode respectively.
7. An ECDF's x-values include every observation, and the x-value where
   the ECDF first reaches 0.5 equals `numpy.median` to within `1e-9`.
8. A `(3, 3)`-inch, 72-dpi scatter of 20,000 points paints fewer than
   half as many distinct screen pixels as there are points; the same
   cloud's `hexbin` densest bin holds more than 20 points.
9. A quadratic relationship's Pearson AND Spearman correlations are both
   under 0.1 in magnitude, while a fitted quadratic's R² exceeds 0.95.
10. A jittered copy of discrete data never moves any point by more than
    the stated jitter width, and the source array is unchanged.

## Tests

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

16 checks, exit 0 when they all pass and non-zero otherwise. They are
value checks, not file-existence checks: the reference suite's 9 tests
are exercised through `pytest`, the exercise suite is confirmed all-skip
on the checked-in state, running both directories together is confirmed
to abort rather than silently collide, and a scratch copy proves the
suite can genuinely fail and then recover.

Override, if your tools are somewhere unusual:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

`tests/run_tests.sh` clears `__pycache__` and `.pytest_cache` both before
and after it runs, and its scratch copy of the solved suite lives in a
`mktemp -d` directory removed immediately after use — so if you only ran
the harness, there is nothing left to clean up.

To remove the lab's virtual environment entirely: `rm -rf .venv`.

To reset your own work and start the exercises again:

```bash
git checkout -- starter/
```

## Troubleshooting

`troubleshooting.md` has the full list, grouped by the message you
actually see. The ones you are most likely to meet:

- **`pytest examples starter` aborts with `import file mismatch`** — do
  not run both directories in one invocation; they share a module name.
- **`ModuleNotFoundError: No module named 'scipy'`** — expected. `scipy`
  is not installed here; exercise 8 works around pandas needing it for
  Spearman by computing rank correlation directly.
- **A plot window tries to open** — something imported `pyplot` before
  `matplotlib.use("Agg")` ran; both `conftest.py` files set the backend
  first, and the harness also exports `MPLBACKEND=Agg`.
- **Exercise 5's two five-number summaries do not agree within `0.3`** —
  both samples are built deterministically with no randomness at all;
  confirm you are calling `numpy.percentile` with `[0, 25, 50, 75, 100]`
  exactly, not a boxplot's own whisker convention.

## Security notes

`security.md` has the full account. In short: this lab opens the network
exactly once, to install its five pinned packages, renders entirely
headless via matplotlib's `Agg` backend, writes only inside its own
`.venv` and one deliberately temporary directory it cleans up itself, and
touches no real data — every sample is generated from a fixed random seed
or a hand-written deterministic function in `data.py`.

## Extension exercises

1. **A three-way bin-width sweep on your own data.** Pick any numeric
   column from a public dataset you already have on disk, and plot it at
   5, 20 and Freedman-Diaconis's own bin count; write one sentence on
   which one you would actually publish and why.
2. **A second matched-quartile pair.** Using `matched_quartile_pair`'s
   approach in `data.py` as a template, construct a *third* sample
   sharing the same five-number summary but with three modes instead of
   two, and confirm the same tolerance holds.
3. **`sns.rugplot` as a fourth honest option.** Add a rug plot underneath
   this lab's ECDF (exercise 6) and describe, in one paragraph, what it
   shows that the ECDF's smooth step function does not make as visible.
4. **KDE bandwidth selection rules.** Read `scipy.stats.gaussian_kde`'s
   documentation (not installed here) on Scott's and Silverman's rules
   for bandwidth, and compare the bandwidth `seaborn.kdeplot` chooses by
   default (readable via its `bw_method` parameter) against what those
   named rules would choose on this lab's `bimodal_for_binning` sample.
5. **A log-scaled hexbin.** Redraw exercise 7's `hexbin` with
   `bins='log'` and describe, in one paragraph, what changes about which
   part of the density the human eye notices first, and why that might
   matter for a chart meant to draw attention to a rare but important
   cluster of points.

## Navigation

- **Previous day:** Day 129 — Statistical Plots with seaborn
  (`labs/sections/math-statistics-and-data/day-129-statistical-plots-with-seaborn/`).
- **Next day:** Day 131 — Time Series Visualization
  (`labs/sections/math-statistics-and-data/`), continuing Week 19.
- **Week 19 project:** the week's project directory
  (`labs/sections/math-statistics-and-data/projects/week-19/`), building
  directly on this week's charting fundamentals.
