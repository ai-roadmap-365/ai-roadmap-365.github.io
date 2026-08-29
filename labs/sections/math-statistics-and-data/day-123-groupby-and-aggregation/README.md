# Day 123 lab — Groups That Reconcile

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Groupby and Aggregation
- **Day number:** 123 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-123-groupby-and-aggregation
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-123-groupby-and-aggregation` when the site is running.
<!-- generated-links:end -->

## Purpose

Nine numbered exercises, each proving one real pandas 3.0.5 `groupby`
behaviour by running code and reading real values. The throughline is
**split, apply, combine** — and the day's discipline is that the pieces
must add back up to the whole. `groupby` drops rows whose key is missing
by default, silently, and exercise 1 makes that failure concrete before
anything else: the sum of per-group totals comes back **less** than the
overall total, and the gap equals exactly the missing-key rows' total.
Every later exercise adds one more piece of the split-apply-combine model
— `count` versus `size`, `.agg()`'s four forms, `agg` versus `transform`
versus `apply`, `GroupBy.filter`, multi-key grouping, `observed=`,
performance, and a weighted mean checked two ways.

## Learning objectives

By the end of this lab you will be able to:

- State that `groupby(...).sum()` silently excludes rows with a missing
  key by default, and use `dropna=False` when the parts must sum back to
  the whole.
- Explain the difference between `size()` (rows) and `count()` (non-missing
  values per column), and predict exactly where they disagree.
- Write `.agg()` four ways — a single function, a list of functions, a
  per-column dict, and named aggregation — and say which produces a flat
  column index and which produces a `MultiIndex`.
- Explain and demonstrate the shape difference between `agg` (one row per
  group) and `transform` (the input's shape), and use `transform` to
  attach a group statistic back to every row.
- Use `GroupBy.filter` to keep or drop whole groups by a predicate, and
  say how that differs from Day 122's row-level filtering.
- Build a multi-key `groupby`, read its `MultiIndex`, and produce the same
  values in a flat frame with `as_index=False`.
- Explain what `observed=` controls for a categorical `groupby`, and
  measure how many rows `observed=False` manufactures that were never
  actually in the data.
- Measure a built-in aggregation against the equivalent `.apply(lambda ...)`
  and report the gap as a ratio, never a millisecond figure.
- Compute a weighted mean per group with `apply` and again without it, and
  check that the two agree.

## Prerequisites

- **Day 120** — Series and DataFrames, index alignment, and Copy-on-Write.
  This lab's tables are ordinary DataFrames built the way that day taught.
- **Day 121** — loading and inspecting data, the habit of checking a
  frame before trusting it.
- **Day 122** — boolean masks, `.query()`, and the partition invariant
  (a filter that silently drops rows so the halves no longer sum to the
  whole) that this lab's exercise 1 directly extends to `groupby`.
- **Week 13 (SQL)** — this lab's Tools section in the lesson compares
  `groupby` against SQL `GROUP BY`; you do not need SQL to run anything
  here.
- A working `python3` on your `PATH` to create the lab's virtual
  environment.

## Supported operating systems

| System | Status |
| --- | --- |
| macOS (Apple Silicon or Intel) | Captured here — macOS 26.5.2, arm64 |
| Linux (any current distribution) | Expected identical, given the pinned versions below |
| Windows | Use WSL and follow the Linux path. `mktemp -d` is used inside `tests/run_tests.sh`; native Windows was not tested and no output is claimed for it |

## Hardware requirements

Anything. The largest structure built in this lab is a 200,000-row,
two-column DataFrame of random floats for exercise 8's timing comparison,
which needs a few megabytes and finishes in well under a second. No GPU,
no network beyond the one-time install, no meaningful disk use.

## Required software

| Tool | Minimum | Used here | Why |
| --- | --- | --- | --- |
| `python3` | 3.11 | 3.14.0 | Runs everything; standard library `venv` builds the lab's environment |
| `pandas` | 3.0.5 exactly | 3.0.5 | Every `groupby`, `.agg`, `.transform` and `.filter` call |
| `pyarrow` | 25.0.1 | 25.0.1 | pandas 3.0's default backend, installed for parity with Days 120-122 |
| `numpy` | 2.5.2 | 2.5.2 | `np.average` for exercise 9; `np.random.default_rng` for exercise 8 |
| `pytest` | 9.1.1 | 9.1.1 | The test harness every exercise is written against |
| `bash` | 3.2 | 3.2.57 | The outer test harness |

Check your Python in one line: `python3 --version`.

## Free and open-source options

Everything here is free.

- **pandas** (BSD 3-Clause), **NumPy** (BSD 3-Clause) and **pytest** (MIT)
  are fully open source with no paid tier.
- **PyArrow** (Apache 2.0) is the Arrow project's Python bindings, also
  fully open source.
- **polars** (MIT), described from its documentation in the lesson's Tools
  section rather than run here, offers `group_by` as a free alternative
  with a lazy query-planning model.
- Plain **SQLite** (public domain), covered in Week 13, is the better tool
  when the "table" in question does not fit in memory or needs concurrent
  writers — the lesson's Tools section says exactly when to prefer it.

No account, no key, no paid tier, and no part of this lab is degraded
without one.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-123-groupby-and-aggregation
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
day-123-groupby-and-aggregation/
├── README.md                     this file
├── metadata.yml                  lab metadata and the recorded run
├── security.md                   what this lab does to your machine
├── troubleshooting.md            grouped by the message you actually see
├── requirements/
│   ├── README.md                  versions, and what each package is for
│   └── requirements.txt           pandas==3.0.5, pyarrow==25.0.1, numpy==2.5.2, pytest==9.1.1
├── starter/                      YOUR work happens here
│   ├── 00_brief.md                exercise-by-exercise instructions
│   ├── data.py                    the five tables every exercise uses
│   ├── conftest.py                fixtures wrapping data.py
│   └── test_groupby.py            nine exercises, each a pytest.skip to replace
├── examples/                     the reference. Read AFTER you have tried
│   ├── data.py
│   ├── conftest.py
│   └── test_groupby.py            the fully worked, 20-assertion answer key
├── tests/
│   └── run_tests.sh               13 checks of real behaviour
└── expected-output/               captured from a real run on 2026-08-19
    ├── FIELDS.md                   what must match and what may differ
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
#    20 skipped, 0 failed.
.venv/bin/pytest starter -v

# 3. Your work: open starter/test_groupby.py and starter/00_brief.md,
#    and replace each pytest.skip(...) with real assertions.
.venv/bin/pytest starter -v -k test_1
.venv/bin/pytest starter -v -k test_2
# ... and so on through test_9, or just:
.venv/bin/pytest starter -v

# 4. Check everything, including the harness's own proof that it can fail.
bash tests/run_tests.sh
```

**Never run `pytest examples starter` in one command.** Both directories
define a module named `test_groupby.py`; pytest imports test modules by
their dotted name, and the second one collected can shadow the first. Run
them as two separate commands, always, as shown above.

## What the commands do

**`.venv/bin/pytest examples`** runs the fully worked reference suite: 20
tests across the nine exercises, each asserting a real value computed from
one of the five tables in `data.py`.

**`.venv/bin/pytest starter`** runs your own suite. On an untouched
checkout, every one of the 20 tests calls `pytest.skip(...)` and is
reported as `s`, so the run exits 0 with nothing yet proven. Replace a
skip with real assertions and delete the skip line; when all 20 are
written and passing, the exercise is done.

**`bash tests/run_tests.sh`** confirms the installed pandas matches
`requirements.txt` exactly, runs `pytest examples` and requires 20 passed,
runs `pytest starter` and requires 20 skipped on the checked-in state,
then solves every exercise in a **scratch copy** made with `mktemp -d`
(never touching the real `starter/test_groupby.py`), confirms that copy
passes in full, deliberately breaks one assertion inside it, confirms the
run now exits non-zero with a failure reported, restores the line, and
confirms it passes again — proving the suite can genuinely fail rather
than merely claiming to. It finishes by checking no file in `examples/` or
`starter/` contains a URL, and that nothing is left on disk.

## Expected output

The harness ends with a real captured line:

```text
13 checks, 0 failure(s)
```

and exits 0. `pytest examples` ends with:

```text
20 passed in 0.06s
```

`pytest starter`, on the checked-in state, ends with:

```text
20 skipped in 0.01s
```

The reconciliation this whole lab is built on, exactly as captured:

```text
grouped_total (dropna=True)  = 1945.0
overall_total                = 2115.0
gap                           = 170.0
missing-key rows' amount total = 170.0   # matches the gap exactly
```

The full capture of both suites is in `expected-output/`, and
`expected-output/FIELDS.md` says which values are specific to pandas
3.0.5 or to this machine, and which would not differ on any correctly
installed copy of this exact version.

## Validation steps

1. `bash tests/run_tests.sh` ends with `13 checks, 0 failure(s)` and exits
   0.
2. Grouping `orders` by `region` (default `dropna=True`) and summing
   `amount` gives a total of **1945.0**, versus an overall total of
   **2115.0** — a gap of exactly **170.0**, which equals the amount total
   of the two rows whose `region` is missing.
3. With `dropna=False`, the grouped sum equals the overall total exactly:
   **2115.0 == 2115.0**.
4. `size()` and `count()` disagree by exactly **2** in total, matching
   `orders['amount'].isna().sum()`.
5. Named aggregation (`agg(total=(...), avg=(...), n=(...))`) produces
   flat column names `['total', 'avg', 'n']`, never a `MultiIndex`.
6. `agg` on `sales` returns shape `(4,)`; `transform` on the same call
   returns shape `(12,)`, matching `sales.shape[0]`.
7. `GroupBy.filter` on `orders` with a `>= 3` size predicate drops `West`
   entirely and keeps exactly **9** rows.
8. Grouping `cat_sales` by two categorical keys gives **20** rows with
   `observed=False` and **9** with `observed=True`.
9. Built-in `.agg('mean')` beats the equivalent `.apply(lambda g: g.mean())`
   by at least **3x** on a 200,000-row frame (this run measured roughly
   10-15x — a ratio, not a promise).
10. A weighted mean computed with `apply` and again without it agree
    exactly: North **17.5**, South **13.0**, East **60.0**.

## Tests

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

13 checks, exit 0 when they all pass and non-zero otherwise. They are
value checks, not file-existence checks: the reference suite's 20
assertions are exercised through `pytest`, the exercise suite is confirmed
all-skip on the checked-in state, and a scratch copy proves the suite can
genuinely fail and then recover.

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
`mktemp -d` directory removed by a trap — so if you only ran the harness,
there is nothing left to clean up.

To remove the lab's virtual environment entirely: `rm -rf .venv`.

To reset your own work and start the exercises again:

```bash
git checkout -- starter/
```

## Troubleshooting

`troubleshooting.md` has the full list, grouped by the message you
actually see. The ones you are most likely to meet:

- **`pytest examples starter` reports fewer failures than expected** — do
  not run both directories in one invocation; they share a module name.
- **Exercise 1's grouped sum does not equal the overall total** — that is
  the point of exercise 1; group with `dropna=False` if you want the parts
  to reconcile.
- **`TypeError: agg function failed [how->mean,dtype->object]`** — you
  called `.agg('mean')` on the whole grouped frame instead of one numeric
  column first.
- **Exercise 4's z-score does not average to zero** — check you used
  `transform`, not `agg`, for both the group mean and the group standard
  deviation.

## Security notes

`security.md` has the full account. In short: this lab opens the network
exactly once, to install its four pinned packages, and everything else
runs offline, writes only inside its own `.venv`, needs no credential, and
touches no real data — every table is a small invented literal except one
seeded random column generated purely to make exercise 8's timing
comparison meaningful at scale.

## Extension exercises

1. **Reproduce exercise 1 with a real fairness report in mind.** Replace
   `region` with a demographic segment column, introduce missing values in
   the same pattern, and write one paragraph on what a report that used
   `dropna=True` (the default) without checking the reconciliation
   invariant would have silently hidden.
2. **Measure the `observed=` memory cost at three categorical widths.**
   Repeat exercise 7 with 5, 20 and 50 categories per key (keeping the
   actual data the same size) and record how many rows `observed=False`
   manufactures at each width. Is the growth linear or combinatorial?
3. **Rewrite exercise 9's weighted mean as a single `.agg()` call with no
   `apply` and no intermediate `.assign()` column.** `pandas.NamedAgg`
   composition alone cannot express a ratio of two sums directly — write
   down exactly why, and what the smallest change to the approach would be
   if pandas ever added that capability.
4. **Compare `.filter()` against a two-step `.size()` plus `.merge()`
   equivalent** that achieves the same row selection as exercise 5's
   `GroupBy.filter`, and time both on `large` from `data.py`. Report which
   is faster and by how much, as a ratio.
5. **Find the point where `.apply` stops losing.** Shrink `build_large`'s
   row count in a scratch copy of `data.py` until the measured ratio in
   exercise 8 drops below 2x, and report the row count where that happens
   on your machine. What does that tell you about where `.apply`'s
   Python-level overhead actually comes from?

## Navigation

- **Previous day:** Day 122 — Selecting and Filtering
  (`labs/sections/math-statistics-and-data/day-122-selecting-and-filtering/`).
- **Next day:** Day 124
  (`labs/sections/math-statistics-and-data/`), continuing Week 18.
- **Week 18 project:** the week's project directory
  (`labs/sections/math-statistics-and-data/projects/week-18/`), "Messy
  Dataset Rescue" — building directly on the groupby fundamentals from
  this lab.
