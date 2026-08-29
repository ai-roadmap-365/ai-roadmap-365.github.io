# Day 131 lab — Time Told Honestly

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Time Series Visualization
- **Day number:** 131 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-131-time-series-visualization
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-131-time-series-visualization` when the site is running.
<!-- generated-links:end -->

## Purpose

Nine numbered exercises, seventeen tests, each proving one real pandas
3.0.5 / matplotlib 3.11.1 behaviour about how time series get plotted
wrong — headless, via the `Agg` backend, by reading real x-positions,
computed values, and artist state. The through-line is that **time is
not just another axis — it has structure, and the commonest charting
mistakes are the ones that throw that structure away.** Exercise 1 makes
that concrete immediately: the exact same data, plotted with the exact
same code except for one axis, either hides a real fourteen-day sensor
outage completely (against a row index) or reveals it as a single wide
jump between otherwise identical steps (against a parsed datetime).
Every later exercise adds one more way that structure gets discarded:
resampling's choice of aggregation, aliasing (downsampling below a
signal's own frequency, which does not just lose detail but manufactures
a pattern that was never there), a trailing rolling window's lag against
a centred one, a missing row silently connected across instead of shown
as a gap, log-scale straightness as the test for constant growth, and
correct year-over-year alignment across a leap year — finishing with the
fact that a single calendar day can genuinely contain 23 or 25 hours.

## Learning objectives

By the end of this lab you will be able to:

- Demonstrate that plotting a time series against its row index instead
  of its parsed `DatetimeIndex` silently erases a real gap in
  observations, and read the difference directly off each line's
  x-positions.
- Resample the same series to monthly `mean`, `sum` and `last`, and
  state which question each of the three different, equally true answers
  actually answers.
- Construct a signal with a known short period, downsample it below that
  frequency, and demonstrate that the result is not merely less detailed
  but contains a specific, predictable, spurious period that exists
  nowhere in the source signal.
- Measure a trailing rolling window's lag against the true peak it is
  meant to summarize, and show that a centred window of the same size
  does not lag at all.
- Demonstrate that matplotlib connects straight across a physically
  absent row but genuinely breaks its line at an explicit `NaN`, and
  that reindexing to the full period converts the first case into the
  second.
- Show that constant-percentage growth is collinear on a log-scaled axis
  to a tight numerical tolerance, while constant linear growth is
  measurably not, and explain why that distinguishes compounding from
  linear growth by eye.
- Align two years of daily data by calendar (month, day) rather than
  ordinal day-of-year, and explain why the ordinal version silently
  misaligns every date after a leap year's Feb 29.
- Facet a many-series frame into small multiples and confirm the exact
  number of Axes and lines that produced.
- Resample hourly timezone-aware data across a real Daylight Saving Time
  boundary and confirm that one calendar day genuinely contains 23 hours
  and another genuinely contains 25.

## Prerequisites

- **Day 121** — loading and inspecting data, specifically `parse_dates`,
  which is exactly what turns a plain string column into the
  `DatetimeIndex` every exercise in this lab depends on.
- **Day 123** — groupby and aggregation, the mechanics this lab's
  `resample` calls (exercise 2) build directly on.
- **Day 127** — why to visualize and how to choose a chart type; this lab
  assumes that decision is already made and focuses on what a *time*
  axis specifically can get wrong.
- **Day 128** — matplotlib's object model (`fig, ax = plt.subplots()`,
  the `Figure`/`Axes`/`Artist` hierarchy, and testing by asserting on
  artists), which every x-position and `Line2D` assertion in this lab
  depends on directly.
- A working `python3` on your `PATH` to create the lab's virtual
  environment.

## Supported operating systems

| System | Status |
| --- | --- |
| macOS (Apple Silicon or Intel) | Captured here — macOS 26.5.2, arm64 |
| Linux (any current distribution) | Expected identical, given the pinned versions below, the headless `Agg` backend, and a system IANA timezone database |
| Windows | Use WSL and follow the Linux path. `mktemp -d` is used inside `tests/run_tests.sh`; native Windows was not tested and no output is claimed for it. Exercise 9 may additionally need `pip install tzdata` — see `requirements/README.md` |

## Hardware requirements

Anything. Every table and signal in this lab is a small, deterministic
construction — at most a few hundred rows. No GPU, no display, no
meaningful disk use, and no network beyond the one-time install.

## Required software

| Tool | Minimum | Used here | Why |
| --- | --- | --- | --- |
| `python3` | 3.11 | 3.14.0 | Runs everything; standard library `venv` builds the lab's environment |
| `pandas` | 3.0.5 exactly | 3.0.5 | Every `DatetimeIndex`, `resample`, `rolling` and `tz_convert` call in this lab |
| `matplotlib` | 3.11.1 exactly | 3.11.1 | Every plot; every assertion reads its `Axes`/`Figure`/`Line2D` objects directly |
| `numpy` | 2.5.2 | 2.5.2 | The aliasing signal (exercise 3) and log-space arithmetic (exercise 6) |
| `pytest` | 9.1.1 | 9.1.1 | The test harness every exercise is written against |
| `bash` | 3.2 | 3.2.57 | The outer test harness |

Check your Python in one line: `python3 --version`.

## Free and open-source options

Everything here is free.

- **pandas** (BSD 3-Clause), **matplotlib** (PSF-derived, BSD-style),
  **NumPy** (BSD 3-Clause) and **pytest** (MIT) are fully open source
  with no paid tier.
- **Plotly** (MIT core library, paid Dash Enterprise tier for deployment)
  and **Bokeh** (BSD 3-Clause, fully free) — both described from
  documentation only, not run here — offer free interactive zooming on
  long series in a browser or notebook.

No account, no key, no paid tier, and no part of this lab is degraded
without one.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-131-time-series-visualization
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import pandas; print(pandas.__version__)"
```

If your tools live somewhere unusual, `tests/run_tests.sh` takes an
override rather than guessing:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## File structure

```text
day-131-time-series-visualization/
├── README.md                     this file
├── metadata.yml                  lab metadata and the recorded run
├── security.md                   what this lab does to your machine
├── troubleshooting.md            grouped by the message you actually see
├── requirements/
│   ├── README.md                  versions, and what each package is for
│   └── requirements.txt           pandas==3.0.5, matplotlib==3.11.1, numpy==2.5.2, pytest==9.1.1
├── starter/                      YOUR work happens here
│   ├── 00_brief.md                exercise-by-exercise instructions
│   ├── data.py                    every builder function the exercises use
│   ├── conftest.py                fixtures wrapping data.py, headless Agg setup
│   └── test_timeseries.py         nine exercises, seventeen tests, each a pytest.skip to replace
├── examples/                     the reference. Read AFTER you have tried
│   ├── data.py
│   ├── conftest.py
│   └── test_timeseries.py         the fully worked, 17-test answer key
├── tests/
│   └── run_tests.sh               17 checks of real behaviour
└── expected-output/               captured from a real run on 2026-08-20
    ├── FIELDS.md                   what must match, what is version-specific, and what is exact
    ├── examples-run.txt            pytest examples -v, captured
    ├── starter-run.txt             pytest starter -v, captured (all skip)
    └── test-run.txt                the full harness run
```

## How to run

```bash
# 1. The reference suite. Read this AFTER you have tried the exercises,
#    never before -- it is the answer key.
.venv/bin/pytest examples
.venv/bin/pytest examples -v

# 2. Where you stand on the exercises. An untouched checkout reports
#    17 skipped, 0 failed.
.venv/bin/pytest starter -v

# 3. Your work: open starter/test_timeseries.py and starter/00_brief.md,
#    and replace each pytest.skip(...) with real assertions.
.venv/bin/pytest starter -v -k test_1
.venv/bin/pytest starter -v -k test_2
# ... and so on through test_9, or just:
.venv/bin/pytest starter -v

# 4. Check everything, including the harness's own proof that it can fail.
bash tests/run_tests.sh
```

**Never run `pytest examples starter` in one command.** Both directories
define a module named `test_timeseries.py`; pytest imports test modules
by their dotted name, and running both together was tested directly in
this lab and aborts collection outright with an `import file mismatch`
error before running a single test. Run them as two separate commands,
always, as shown above.

## What the commands do

**`.venv/bin/pytest examples`** runs the fully worked reference suite: 17
tests across the nine exercises, each asserting a real value read off a
real pandas/matplotlib object built from one of the builder functions in
`data.py`.

**`.venv/bin/pytest starter`** runs your own suite. On an untouched
checkout, every one of the 17 tests calls `pytest.skip(...)` and is
reported as `s`, so the run exits 0 with nothing yet proven. Replace a
skip with real assertions and delete the skip line; when all 17 are
written and passing, the exercise is done.

**`bash tests/run_tests.sh`** confirms the installed packages match
`requirements.txt` exactly, runs `pytest examples` and requires 17
passed, runs `pytest starter` and requires 17 skipped on the checked-in
state, then solves every exercise in a **scratch copy** made with
`mktemp -d` (never touching the real `starter/test_timeseries.py`),
confirms that copy passes in full, deliberately breaks one assertion
inside it, confirms the run now exits non-zero with a failure reported,
restores the line, and confirms it passes again. It then draws one real
line plot, saves it headless to a temporary PNG file, confirms the file
exists, and removes it — proving both that headless rendering genuinely
works and that this lab leaves no image file behind. It finishes by
checking no file in `examples/` or `starter/` contains a URL, and that
nothing is left on disk.

## Expected output

The harness ends with a real captured line:

```text
17 checks, 0 failure(s)
```

and exits 0. `pytest examples` ends with:

```text
17 passed in 0.05s
```

`pytest starter`, on the checked-in state, ends with:

```text
17 skipped in 0.01s
```

Exercise 3's aliasing trap, exactly as captured — a signal whose true
period is 4 days, sampled every 5th day, produces an observed period of
20 days:

```text
>>> ALIASING_TRUE_PERIOD_DAYS, ALIASING_SAMPLE_INTERVAL_DAYS
4, 5
>>> observed spurious period (days)
20
```

The full capture of both suites is in `expected-output/`, and
`expected-output/FIELDS.md` says which values are exact everywhere,
which are specific to this pin set or timezone database, and which
(exercise 4's trailing-lag offset) are asserted with a tolerance rather
than the single captured integer.

## Validation steps

1. `bash tests/run_tests.sh` ends with `17 checks, 0 failure(s)` and
   exits 0.
2. A gapped series plotted against `range(len(df))` has every x-step
   equal to `1.0`; plotted against the parsed dates, every step is
   `1.0` except one, which is `15.0`.
3. `daily_1to90.resample("MS")` gives January `.mean() == 16.0`,
   `.sum() == 496.0`, `.last() == 31.0` — three different numbers from
   the same 31 rows.
4. A 4-day cosine sampled every 5th day repeats with an observed period
   of 20 days, not 4.
5. A trailing 30-day rolling mean's peak lands 10-20 days after the true
   peak; a centred 30-day window's peak lands exactly on it.
6. A series with a physically absent row plots with no `NaN` and one
   fewer point than the full range; the same gap made an explicit `NaN`
   plots with the full point count and a real `NaN` at that position;
   reindexing the first into the second's own index produces an
   identical series.
7. `numpy.diff(numpy.log(...))` has a standard deviation under `1e-9` for
   constant-percentage growth and over `1e-3` for constant linear
   growth.
8. Merging two years' data on a `(month, day)` key keeps Dec 31 aligned
   in both a leap and a non-leap year; Dec 31's raw `.dayofyear` is `366`
   in 2024 and `365` in 2025.
9. Faceting a 6-column frame produces exactly 6 `Axes`, one `Line2D`
   each.
10. Resampling hourly `America/New_York` data to daily counts gives `23`
    for 2024-03-10, `25` for 2024-11-03, and `24` for an ordinary day.

## Tests

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

17 checks, exit 0 when they all pass and non-zero otherwise. They are
value checks, not file-existence checks: the reference suite's 17 tests
are exercised through `pytest`, the exercise suite is confirmed all-skip
on the checked-in state, a scratch copy proves the suite can genuinely
fail and then recover, and one real headless savefig proves the `Agg`
backend and the lab's own cleanup both work.

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
and after it runs, and its scratch copy of the solved suite and its
savefig demonstration both live in `mktemp -d` directories removed
immediately after use — so if you only ran the harness, there is nothing
left to clean up.

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
- **A plot window tries to open** — something imported `pyplot` before
  `matplotlib.use("Agg")` ran; both `conftest.py` files set the backend
  first, and the harness also exports `MPLBACKEND=Agg`.
- **Exercise 9 raises a timezone-database error** — install the
  pure-Python fallback with `.venv/bin/pip install tzdata`; see
  `requirements/README.md`.
- **Exercise 3's spurious period is not exactly 20** — recompute it from
  `ALIASING_TRUE_PERIOD_DAYS` and `ALIASING_SAMPLE_INTERVAL_DAYS` in
  `data.py` rather than hardcoding the number.

## Security notes

`security.md` has the full account. In short: this lab opens the network
exactly once, to install its four pinned packages, renders entirely
headless via matplotlib's `Agg` backend, writes only inside its own
`.venv` and temporary directories it cleans up itself, reads (never
writes) your system's timezone database for exercise 9, and touches no
real data — every table and signal is a small deterministic construction
built by hand in `data.py`.

## Extension exercises

1. **Aliasing at a different sampling interval.** Change
   `ALIASING_SAMPLE_INTERVAL_DAYS` in a scratch copy of `data.py` to a
   value that shares a common factor with the true period (for example,
   8, which shares a factor of 4 with the true 4-day period) and observe
   that the "spurious period" search either fails to find a short repeat
   or finds a much shorter, less deceptive one — explain in one sentence
   why sampling in lockstep with part of the true cycle is a different
   (and less dangerous) failure than sampling in genuine aliasing
   territory.
2. **A wider or narrower rolling window.** Repeat exercise 4 with window
   sizes of 10 and 60 instead of 30, and confirm the trailing lag scales
   with roughly half of whichever window you chose.
3. **A second, larger missing stretch.** Extend exercise 5's series with
   a five-day gap in addition to the single missing day, reindex to the
   full range, and confirm matplotlib now breaks the line at five
   consecutive `NaN` points rather than one.
4. **Year-over-year with three years.** Extend exercise 7's alignment to
   2023, 2024 and 2025 at once (a `(month, day)` key working across all
   three), and confirm Feb 29 appears with a value only in 2024.
5. **`col_wrap`-style reshaping of the small multiples.** Instead of one
   column of Axes in exercise 8, arrange the same six series in a 2×3
   grid with `plt.subplots(2, 3, ...)` and confirm the Axes count is
   unchanged while the shape is not — the same distinction Day 129's
   `col_wrap=` made for a `FacetGrid`.

## Navigation

- **Previous day:** Day 130 — Distributions and Relationships
  (`labs/sections/math-statistics-and-data/day-130-distributions-and-relationships/`).
- **Next day:** Day 132 — Visual Storytelling and Chart Honesty
  (`labs/sections/math-statistics-and-data/`), continuing Week 19.
- **Week 19 project:** the week's project directory
  (`labs/sections/math-statistics-and-data/projects/week-19/`), building
  directly on this week's charting fundamentals.
