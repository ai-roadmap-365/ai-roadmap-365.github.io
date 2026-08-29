# Day 132 Lab — Charts That Cannot Lie To You

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Visual Storytelling and Chart Honesty
- **Day number:** 132 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-132-visual-storytelling-and-chart-honesty
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-132-visual-storytelling-and-chart-honesty` when the site is running.
<!-- generated-links:end -->

## Purpose

Most misleading charts are made by honest people. The techniques in this
lab are not tricks a villain reaches for — they are defaults,
conveniences and reasonable-looking choices that happen to change the
conclusion. So the goal here is not a gallery of villainy. It is an
instrument: a way to check your own work.

You build that instrument in nine exercises. Each one takes a distortion
that reads as a judgment call and turns it into a number measured off the
chart's own rendered geometry. By the end you have `review_chart` — four
checks you can run on any figure you are about to publish, which pass an
honest chart, fail a truncated one, and pass a chart that breaks a rule
and says so.

The measuring stick throughout is **Tufte's lie factor**: the size of the
effect shown in the graphic divided by the size of the effect in the
data. Two bars, 100 and 102. On a zero baseline the lie factor is
`1.0000`. Move the axis floor to 99 and one bar is three times the height
of the other — a measured drawn ratio of `3.0000` — for a lie factor of
`2.9412`. Same two numbers, one line of code apart.

## Learning objectives

By the end of this lab you can:

- Compute a lie factor from a chart's rendered geometry rather than from
  the numbers that were plotted.
- Explain why a truncated axis destroys a bar chart's encoding and
  leaves a line chart's intact, and prove both with a measurement.
- State precisely what a dual y-axis can and cannot do to an apparent
  relationship — including the part almost every warning about dual axes
  gets wrong.
- Show that a trend's sign is chosen by the window, and defend against it.
- Show that two citable bin rules can support opposite claims about the
  same sample.
- Explain why encoding by radius squares every ratio.
- Measure how far 3D perspective moves a comparison that a flat chart
  gets exactly right.
- Treat ordering, annotation and luminance contrast as measurable craft
  rather than decoration.
- Run a reusable review contract over your own charts before publishing.

## Prerequisites

- Day 127 — chart choice and the perceptual ranking, including that
  radius encoding squares ratios and that a red/green palette collapses
  for colour-deficient readers.
- Day 128 — the matplotlib object model, and testing a chart by
  asserting on its artists rather than diffing pixels. Every measurement
  here is that pattern applied.
- Day 130 — bin width as a choice. This lab supplies the consequences.
- Day 131 — time series, including what a chosen window does to a trend.
- Day 116 — Simpson's paradox, referenced in the lesson, not re-derived
  here.
- Comfort with Python functions, NumPy arrays, and reading a stack trace.

## Supported operating systems

macOS and Linux, exactly as written. Everything runs headless on
matplotlib's `Agg` backend — no display server, no GUI toolkit, no
window — so it works identically over SSH and in a container.

This lab was executed and captured on **macOS 26.5.2 (Apple Silicon,
arm64)** only. Linux uses identical commands. The Windows equivalents are
in `troubleshooting.md`, documented from the standard Python packaging
layout; they were **not** exercised on the authoring machine, and that is
stated rather than glossed.

## Hardware requirements

Any machine that runs Python 3.14. The whole suite finishes in a few
seconds and holds a couple of dozen small figures in memory, one at a
time. No GPU, no special hardware, roughly 400 MB of disk for the virtual
environment.

## Required software

- Python 3.14.0
- matplotlib 3.11.1
- seaborn 0.13.2
- pandas 3.0.5
- NumPy 2.5.2
- pytest 9.1.1
- bash, for the test harness

Exact pins are in `requirements/requirements.txt`, and
`tests/run_tests.sh` checks each installed version against that file so a
mismatch is reported rather than silently producing different numbers.

## Free and open-source options

Every tool in this lab is free and open source, and there is no paid tier
of any of it to be nudged toward. matplotlib, seaborn, pandas, NumPy and
pytest are all permissively licensed and installed with one `pip`
command. Python itself is free.

The commercial BI tools discussed in the lesson — Tableau, Power BI —
are **not** used here, are not installed, and produce no output anywhere
in this lab. Everything said about them comes from their published
documentation and is marked as such.

## Installation

From this directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import matplotlib, seaborn, pandas; print(matplotlib.__version__, seaborn.__version__, pandas.__version__)"
```

That last command should print `3.11.1 0.13.2 3.0.5`. The `pip install`
is the only step that touches the network; everything after it runs
offline.

## File structure

```
day-132-visual-storytelling-and-chart-honesty/
├── README.md                  this file
├── metadata.yml               lab metadata and the literal result of the real run
├── security.md                what this lab touches, and what it does not
├── troubleshooting.md         the failures you are most likely to hit
├── requirements/
│   ├── README.md              why each pin is here
│   └── requirements.txt       the exact versions this lab was run against
├── starter/
│   ├── 00_brief.md            the nine exercises, in order
│   ├── honesty.py             14 functions to write; everything else works
│   ├── test_starter.py        skips what you have not written yet
│   └── conftest.py            keeps this directory's `honesty` module its own
├── examples/
│   ├── honesty.py             the reference implementation
│   ├── 01_lie_factor.py … 09_caption_contract.py
│   ├── test_reference.py      42 tests over the finished module
│   └── conftest.py            the matching import guard
├── expected-output/
│   ├── 01-lie-factor.txt … 09-caption-contract.txt
│   ├── pytest-examples.txt, pytest-starter.txt, test-run.txt
│   └── FIELDS.md              which captured values are exact, and which are not
└── tests/
    └── run_tests.sh           59 checks; exits 0 only if every one passes
```

## How to run

Work through `starter/00_brief.md`, writing one function at a time in
`starter/honesty.py` and checking yourself:

```bash
cd starter
../.venv/bin/pytest . -q
cd ..
```

A fresh checkout reports **22 skipped**. Each function you finish turns
skips into passes.

When you want to see the finished version, run the nine demonstration
scripts:

```bash
cd examples
../.venv/bin/python3 01_lie_factor.py
../.venv/bin/python3 02_bars_versus_lines.py
../.venv/bin/python3 03_dual_axes.py
../.venv/bin/python3 04_cherry_picked_window.py
../.venv/bin/python3 05_binning_changes_the_conclusion.py
../.venv/bin/python3 06_radius_versus_area.py
../.venv/bin/python3 07_three_d_distortion.py
../.venv/bin/python3 08_ordering_and_annotation.py
../.venv/bin/python3 09_caption_contract.py
cd ..
```

Then the two test suites and the full harness:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
bash tests/run_tests.sh
```

Run `pytest examples` and `pytest starter` as **two separate commands**,
never as `pytest examples starter`. Both directories ship a module called
`honesty`, and combining them in one invocation is unreliable in both
directions — see `troubleshooting.md`.

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 -m venv .venv` | Creates the lab-local virtual environment |
| `.venv/bin/pip install -r requirements/requirements.txt` | Installs the five pinned packages; the only network step |
| `01_lie_factor.py` | Draws two bars twice and measures both lie factors off the rendered geometry |
| `02_bars_versus_lines.py` | Same numbers, same axis, two encodings; shows the bar's lie factor at 2.94 and the line's at exactly 1.00 |
| `03_dual_axes.py` | Proves scaling cannot change a drawn correlation, that inverting an axis negates it exactly, and that overlap is achievable for any correlation |
| `04_cherry_picked_window.py` | Fits three trends to three windows of one series and shows the sign flip, with real dates from pandas |
| `05_binning_changes_the_conclusion.py` | Bins one sample by two textbook rules and counts the humps each one draws |
| `06_radius_versus_area.py` | Measures the drawn area ratio under both encodings |
| `07_three_d_distortion.py` | Projects 3D bar corners through the Axes' own matrix and compares drawn areas against a flat control |
| `08_ordering_and_annotation.py` | Measures ordering, retrievable claim text, and luminance separation, using seaborn's `colorblind` palette |
| `09_caption_contract.py` | Runs the four-check review contract over four charts |
| `.venv/bin/pytest examples -q` | The 42-test reference suite |
| `.venv/bin/pytest starter -q` | Your progress: skips what is unwritten, fails what is wrong |
| `bash tests/run_tests.sh` | All 59 checks, including proving the harness can fail |

## Expected output

Every file in `expected-output/` was captured from a real run on
2026-08-20. The headline numbers:

| Measurement | Value |
| --- | --- |
| Lie factor, zero-baseline bar pair | `1.0000` |
| Drawn height ratio, `ylim=(99, 103)` | `3.0000` |
| Lie factor, truncated bar pair | `2.9412` |
| Lie factor, same numbers as a line, any baseline | `1.0000` |
| Data correlation of the dual-axis pair | `-0.001034` |
| Drawn correlation, under every scaling tried | `-0.001034` |
| Drawn correlation of a strong pair with one axis inverted | `-0.913234` |
| Tracking gap, curves parked apart | `0.4938` |
| Tracking gap, both axes widened 20× | `0.0147` |
| Tracking gap, a genuinely correlated pair, same widening | `0.0046` |
| Trend slope, first half / second half | `-0.7305` / `+0.7045` |
| Humps drawn, Sturges / Freedman-Diaconis | `1` / `2` |
| Drawn area ratio, radius encoding of a 4× difference | `16.00` |
| Drawn ratio of two 3D bars (data ratio 2) | `2.341` far, `4.204` near |
| Luminance gap, classic red vs classic green | `0.0996` |
| Luminance gap, deliberate emphasis | `0.5505` |

The last line of the harness:

```
59 checks, 0 failure(s).
```

`expected-output/FIELDS.md` separates the values that are exact on any
machine from the handful that depend on matplotlib's version, and
discloses the two datasets that were deliberately selected.

## Validation steps

1. `bash tests/run_tests.sh` prints `59 checks, 0 failure(s).` and exits 0.
2. `.venv/bin/pytest examples -q` reports `42 passed`.
3. `.venv/bin/pytest starter -q` reports `22 skipped` on an untouched
   checkout, and `22 passed` once every exercise is written.
4. Section 6 of the harness proves the suite can fail: it replaces
   `review_chart` with a function that approves everything and confirms
   script 09 exits non-zero, then does the same with a `lie_factor`
   stuck at 1.0 against script 01. Neither modifies a file on disk.
5. Section 7 confirms the lab left no image, no `__pycache__` and no
   `.pytest_cache` behind — this lab draws around fifty figures and
   saves none of them.

## Tests

`tests/run_tests.sh` runs 59 checks in seven sections: installed versions
against the pins, all nine scripts exiting 0 with every internal
assertion holding, the twenty headline numbers re-measured live and
compared against their captured values, the reference suite, the starter
suite and its import guard, two deliberate self-sabotage runs proving the
harness can go red, and a cleanliness sweep.

Nothing in it compares rendered pixels to a stored reference image, and
nothing asserts on a timing. Every assertion is on a shape, a value, or
a piece of artist state — the pattern Day 128 established, and the reason
this suite is portable.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: reset your work
```

The lab writes nothing outside its own directory, and saves no images at
all, so there is nothing else to remove.

## Troubleshooting

See `troubleshooting.md`. The three most common: running the system
Python instead of `.venv/bin/python3`; expecting `pytest starter` to pass
rather than skip on a fresh checkout; and running `pytest examples
starter` as one command, which you must never do.

## Security notes

See `security.md`. In short: no network after the install, no files
written, no display server, no credentials, no `sudo`, and every dataset
generated from a seeded random number generator inside the lab.

## Extension exercises

1. **Extend the contract.** Add a fifth check to `review_chart`: a bar
   chart whose y-axis floor is not zero should fail regardless of what
   the caption says, because no disclosure repairs a broken encoding.
   You will need to detect a bar chart — `len(ax.patches) > 0` with no
   lines is a start — and you will discover why that detection is harder
   than it looks.
2. **A lie factor for a whole figure.** The current measure takes two
   values. Generalise it to a set of bars: compute the drawn ratio of
   every pair against its data ratio and report the worst.
3. **Aggregation as an editorial choice.** Build a small grouped dataset
   where the overall average points one way and every subgroup points the
   other, then write a check that flags a chart showing only the
   aggregate. Day 116 has the mechanism.
4. **Re-run exercise 7 across cameras.** Sweep `focal_length` from 1.0
   down to 0.15 and plot the drawn ratio against it. The relationship
   tells you how much of a 3D chart's distortion is the projection and
   how much is the viewing angle.
5. **Test your own charts.** Take a figure you have already published,
   run `review_chart` over it, and fix what it finds. This is the only
   extension that changes anything outside this directory.

## Navigation

- Previous day's lab: `../day-131-time-series-visualization/`
- Next day's lab: `../day-133-building-an-eda-report/`
- Week 19 index: `../README.md`
