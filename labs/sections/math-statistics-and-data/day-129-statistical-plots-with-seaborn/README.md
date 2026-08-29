# Day 129 lab — Plots That Say What They Computed

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Statistical Plots with seaborn
- **Day number:** 129 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-129-statistical-plots-with-seaborn
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-129-statistical-plots-with-seaborn` when the site is running.
<!-- generated-links:end -->

## Purpose

Nine numbered exercises, sixteen tests, each proving one real seaborn
0.13.2 / matplotlib 3.11.1 behaviour by drawing a real plot, headless via
the `Agg` backend, and reading real return types, artist state, or
numeric values. The through-line is that **seaborn does statistics for
you before it draws** — a `barplot` is a chart of a computed estimator
with a bootstrapped interval, not a chart of your raw data. Exercise 2
makes that concrete immediately: the four bar heights equal the four
group means, none of which is a value any of that group's own
observations actually holds, and a stripplot of the same column recovers
every one of the sixteen raw points a bar chart aggregated away. Every
later exercise adds one more piece of the API this fact depends on:
axes-level versus figure-level functions and their different return
types, the bootstrap's own randomness and how to fix it with `seed=`,
`errorbar=` alternatives, long-versus-wide data, faceting, the
matplotlib escape hatch, theme side effects, and the honest overlay of
raw points on an aggregated chart.

## Learning objectives

By the end of this lab you will be able to:

- Distinguish axes-level seaborn functions (which draw into an `Axes`
  you own and return that `Axes`) from figure-level functions (which
  create and own their own `Figure` and return a `FacetGrid`), and read
  the return type to tell which one you called.
- Demonstrate that a `barplot`'s bar heights equal the group means, that
  none of those means is a value present in that group's own raw data,
  and recover every raw observation instead with a `stripplot` of the
  same column.
- Demonstrate that two `barplot` calls without `seed=` produce
  bootstrapped error bars of slightly different extent, and that fixing
  `seed=` makes two runs identical.
- Compare `errorbar='sd'` against `errorbar=('ci', 95)` on the same data
  and state which one is a closed-form statistic (does not depend on the
  seed) and which is a resampling procedure (does).
- Explain why a wide DataFrame fails when asked for a `hue` mapping by
  column name, and use `melt` (Day 124) to produce the long form that
  works.
- Use `col=` to facet a plot into one `Axes` per category, and `col_wrap=`
  to reshape that grid without changing how many `Axes` exist.
- Use the Day 128 matplotlib object API (`ax.set_ylabel`, `ax.set_ylim`,
  and similar) as the escape hatch after a seaborn call has already
  drawn.
- Demonstrate that `sns.set_theme()` mutates global matplotlib `rcParams`
  and know how to capture and restore the prior state.
- Overlay a `stripplot` on a `boxplot` in the same `Axes` and confirm
  both kinds of artist (box patches and point collections) are present —
  the honest form for a small sample.

## Prerequisites

- **Day 124** — merging and reshaping; this lab's exercise 5 uses the
  exact `melt` call that day taught to turn a wide table long.
- **Day 117** — sampling and the Central Limit Theorem, specifically the
  bootstrap resampling technique that reappears unannounced in this lab's
  exercise 3 as `barplot`'s default error bar.
- **Day 127** — why to visualize and how to choose a chart type; this lab
  assumes you already know when a bar, box or scatter chart is the right
  starting point and focuses instead on what seaborn actually draws.
- **Day 128** — matplotlib's object model (`fig, ax = plt.subplots()`,
  the `Figure`/`Axes`/`Artist` hierarchy, and testing by asserting on
  artists), which this lab's escape-hatch exercise (7) and every artist
  assertion in exercises 2 and 9 depend on directly.
- A working `python3` on your `PATH` to create the lab's virtual
  environment.

## Supported operating systems

| System | Status |
| --- | --- |
| macOS (Apple Silicon or Intel) | Captured here — macOS 26.5.2, arm64 |
| Linux (any current distribution) | Expected identical, given the pinned versions below and the headless `Agg` backend |
| Windows | Use WSL and follow the Linux path. `mktemp -d` is used inside `tests/run_tests.sh`; native Windows was not tested and no output is claimed for it |

## Hardware requirements

Anything. Every table in this lab is a small hand-built literal, at most
sixteen rows. No GPU, no display, no meaningful disk use, and no network
beyond the one-time install.

## Required software

| Tool | Minimum | Used here | Why |
| --- | --- | --- | --- |
| `python3` | 3.11 | 3.14.0 | Runs everything; standard library `venv` builds the lab's environment |
| `seaborn` | 0.13.2 exactly | 0.13.2 | Every plotting call in this lab |
| `matplotlib` | 3.11.1 exactly | 3.11.1 | seaborn's drawing engine; every assertion reads its `Axes`/`Figure`/`Patch`/`Line2D` objects directly |
| `pandas` | 3.0.5 exactly | 3.0.5 | `team_scores`, `wide_revenue`, `long_revenue`, and the exercise-5 `melt` call |
| `numpy` | 2.5.2 | 2.5.2 | Transitive dependency of pandas and matplotlib |
| `pytest` | 9.1.1 | 9.1.1 | The test harness every exercise is written against |
| `bash` | 3.2 | 3.2.57 | The outer test harness |

Check your Python in one line: `python3 --version`.

## Free and open-source options

Everything here is free.

- **seaborn** (BSD 3-Clause), **matplotlib** (PSF-derived, BSD-style),
  **pandas** (BSD 3-Clause), **NumPy** (BSD 3-Clause) and **pytest**
  (MIT) are fully open source with no paid tier.
- **plotnine** (MIT/BSD, described from documentation only, not run
  here) offers a ggplot2-style grammar-of-graphics alternative, also
  free and open source.
- **Vega-Lite / Altair** (BSD 3-Clause, described from documentation
  only, not run here) is a free, declarative, JSON-based alternative
  that renders interactively in a browser or notebook.

No account, no key, no paid tier, and no part of this lab is degraded
without one.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-129-statistical-plots-with-seaborn
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
day-129-statistical-plots-with-seaborn/
├── README.md                     this file
├── metadata.yml                  lab metadata and the recorded run
├── security.md                   what this lab does to your machine
├── troubleshooting.md            grouped by the message you actually see
├── requirements/
│   ├── README.md                  versions, and what each package is for
│   └── requirements.txt           seaborn==0.13.2, matplotlib==3.11.1, pandas==3.0.5, numpy==2.5.2, pytest==9.1.1
├── starter/                      YOUR work happens here
│   ├── 00_brief.md                exercise-by-exercise instructions
│   ├── data.py                    team_scores, wide_revenue, long_revenue
│   ├── conftest.py                fixtures wrapping data.py, headless Agg setup
│   └── test_seaborn.py            nine exercises, sixteen tests, each a pytest.skip to replace
├── examples/                     the reference. Read AFTER you have tried
│   ├── data.py
│   ├── conftest.py
│   └── test_seaborn.py            the fully worked, 16-test answer key
├── tests/
│   └── run_tests.sh               17 checks of real behaviour
└── expected-output/               captured from a real run on 2026-08-20
    ├── FIELDS.md                   what must match, what is version-specific, and what is sampled by design
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
#    16 skipped, 0 failed.
.venv/bin/pytest starter -v

# 3. Your work: open starter/test_seaborn.py and starter/00_brief.md, and
#    replace each pytest.skip(...) with real assertions.
.venv/bin/pytest starter -v -k test_1
.venv/bin/pytest starter -v -k test_2
# ... and so on through test_9, or just:
.venv/bin/pytest starter -v

# 4. Check everything, including the harness's own proof that it can fail.
bash tests/run_tests.sh
```

**Never run `pytest examples starter` in one command.** Both directories
define a module named `test_seaborn.py`; pytest imports test modules by
their dotted name, and running both together was tested directly in this
lab and aborts collection outright with an `import file mismatch` error
before running a single test. Run them as two separate commands, always,
as shown above.

## What the commands do

**`.venv/bin/pytest examples`** runs the fully worked reference suite: 16
tests across the nine exercises, each asserting a real value read off a
real seaborn/matplotlib object built from one of the two tables in
`data.py`.

**`.venv/bin/pytest starter`** runs your own suite. On an untouched
checkout, every one of the 16 tests calls `pytest.skip(...)` and is
reported as `s`, so the run exits 0 with nothing yet proven. Replace a
skip with real assertions and delete the skip line; when all 16 are
written and passing, the exercise is done.

**`bash tests/run_tests.sh`** confirms the installed packages match
`requirements.txt` exactly, runs `pytest examples` and requires 16
passed, runs `pytest starter` and requires 16 skipped on the checked-in
state, then solves every exercise in a **scratch copy** made with
`mktemp -d` (never touching the real `starter/test_seaborn.py`), confirms
that copy passes in full, deliberately breaks one assertion inside it,
confirms the run now exits non-zero with a failure reported, restores the
line, and confirms it passes again. It then draws one real barplot,
saves it headless to a temporary PNG file, confirms the file exists, and
removes it — proving both that headless rendering genuinely works and
that this lab leaves no image file behind. It finishes by checking no
file in `examples/` or `starter/` contains a URL, and that nothing is
left on disk.

## Expected output

The harness ends with a real captured line:

```text
17 checks, 0 failure(s)
```

and exits 0. `pytest examples` ends with:

```text
16 passed in 0.83s
```

`pytest starter`, on the checked-in state, ends with:

```text
16 skipped in 0.03s
```

Exercise 2's barplot trap, exactly as captured — the four bar heights are
the four group means, and team B's mean is lower than team A's despite
three of team B's four raw scores beating every one of team A's:

```text
team
A    79.0
B    70.0
C    67.5
D    57.5
Name: score, dtype: float64
```

The full capture of both suites is in `expected-output/`, and
`expected-output/FIELDS.md` says which values are exact everywhere,
which are specific to this seaborn/matplotlib pin, and which
(exercise 3's unseeded bootstrap extents) are expected to differ between
runs by design.

## Validation steps

1. `bash tests/run_tests.sh` ends with `17 checks, 0 failure(s)` and
   exits 0.
2. `sns.scatterplot(..., ax=ax)` returns that same `ax`; `sns.relplot(...)`
   returns a `seaborn.axisgrid.FacetGrid` whose `.figure` owns its own
   `.ax`.
3. A `barplot` of `team_scores` produces bars of height `79.0`, `70.0`,
   `67.5`, `57.5` — the four group means — and none of those four numbers
   is one of that group's own raw scores.
4. Six `barplot` calls with no `seed=` do not all produce identical
   bootstrapped error-bar extents; the same call with `seed=42` twice
   produces identical extents.
5. `errorbar='sd'` and `errorbar=('ci', 95)` produce different extents on
   the same data; `'sd'` alone is identical regardless of seed.
6. `sns.lineplot` on `wide_revenue` asking for `x="quarter"` raises
   `ValueError`; the same call on `long_revenue` (produced by `melt`)
   succeeds with one legend entry per region.
7. `sns.catplot(..., col="region")` on five regions produces exactly 5
   `Axes` arranged `(1, 5)`; adding `col_wrap=3` keeps 5 `Axes` but
   reshapes the grid to `(2, 3)`.
8. `ax.set_ylabel(...)` called after a seaborn `boxplot` call sticks and
   is readable back with `ax.get_ylabel()`.
9. `sns.set_theme()` changes seven specific `matplotlib.rcParams` keys,
   including `axes.facecolor` to `"#EAEAF2"` and `axes.grid` to `True`;
   restoring the captured dictionary returns matplotlib to its prior
   state exactly.
10. A `boxplot` followed by a `stripplot` on the same `Axes` carries
    `4` box patches and `4` point collections, together showing all 16
    raw observations.

## Tests

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

17 checks, exit 0 when they all pass and non-zero otherwise. They are
value checks, not file-existence checks: the reference suite's 16 tests
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
- **Exercise 2's bar heights are not exactly `79.0, 70.0, 67.5, 57.5`** —
  recompute them from `team_scores.groupby("team")["score"].mean()`
  rather than hardcoding a number.
- **Exercise 3's two "unseeded" runs come out identical** — can happen by
  chance on a tiny sample; the *seeded* half must always agree.

## Security notes

`security.md` has the full account. In short: this lab opens the network
exactly once, to install its five pinned packages, renders entirely
headless via matplotlib's `Agg` backend, writes only inside its own
`.venv` and one deliberately temporary directory it cleans up itself, and
touches no real data — every table is a small invented literal built by
hand in `data.py`.

## Extension exercises

1. **Reproduce the barplot trap with more groups.** Build a ten-group
   version of `team_scores` where every group's mean is close together
   but one group has an extreme outlier; confirm the bar chart alone
   cannot distinguish "consistently middling" from "excellent except for
   one bad day", and that a stripplot or swarmplot immediately can.
2. **Compare `boxplot` against `violinplot`.** Draw both on `team_scores`
   and describe, in one paragraph, what a violin plot shows about team
   B's distribution that a box plot's five-number summary does not.
3. **`errorbar='pi'` (a prediction interval) versus `('ci', 95)`.** Add a
   third comparison to exercise 4 using `errorbar=('pi', 95)` and report
   how its extent differs from both `'sd'` and the confidence interval,
   and explain in one sentence what a prediction interval claims that a
   confidence interval does not.
4. **`row=` in addition to `col=`.** Extend exercise 6 with a second
   categorical column and facet on both `row=` and `col=` at once;
   confirm the resulting `Axes` count is the product of the two
   categories' counts.
5. **A theme that persists across a whole notebook session.** Call
   `sns.set_theme(context="talk", palette="colorblind")` instead of the
   bare default, draw a plot, and write down which additional `rcParams`
   keys changed compared to this lab's exercise 8 -- and why forgetting
   to reset a theme before a screenshot for a report is a common way a
   chart's colours stop matching a team's usual style guide.

## Navigation

- **Previous day:** Day 128 — Matplotlib Fundamentals
  (`labs/sections/math-statistics-and-data/day-128-matplotlib-fundamentals/`).
- **Next day:** Day 130 — Distributions and Relationships
  (`labs/sections/math-statistics-and-data/`), continuing Week 19.
- **Week 19 project:** the week's project directory
  (`labs/sections/math-statistics-and-data/projects/week-19/`), building
  directly on this week's charting fundamentals.
