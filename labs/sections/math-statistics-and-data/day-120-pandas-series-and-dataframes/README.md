# Day 120 lab — Frames You Can Trust

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** pandas: Series and DataFrames
- **Day number:** 120 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-120-pandas-series-and-dataframes
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-120-pandas-series-and-dataframes` when the site is running.
<!-- generated-links:end -->

## Purpose

Nine numbered exercises, each asserting real pandas behaviour against a
value computed independently, on **pandas 3.0.5** specifically. This is
the day pandas 3.0 changed two things that almost every existing tutorial
still gets wrong — Copy-on-Write is now unconditional, and the default
dtype for a column of strings is `str`, not `object` — and you verify both
by running code and reading the real output, not by taking anyone's word
for it, including this lab's own comments.

The throughline is the index. A DataFrame is not a spreadsheet; it is a
set of Series sharing one index, and every exercise in this lab is really
about what that index buys you and what it costs when you forget it is
there — starting with exercise 2, where adding two Series with different
indexes produces `NaN` instead of the position-by-position sum almost
everyone expects the first time they see it.

## Learning objectives

By the end of this lab you will be able to:

- Build a Series and a DataFrame from a dict, from records, and from a bare
  NumPy array, and say correctly what the index becomes in each case.
- Explain why adding two Series with different indexes produces `NaN`
  rather than a positional sum, and opt out of alignment with `.to_numpy()`
  or `.reset_index(drop=True)` when that is genuinely what you want.
- State the pandas 3.0 default string dtype (`str`) and how it differs from
  the pre-3.0 `object` default.
- Demonstrate that an `int64` column silently promotes to `float64` the
  moment a missing value enters it, losing exact precision past `2**53`,
  and use the nullable `Int64` dtype to avoid it.
- Show that chained assignment (`df[mask]['col'] = value`) leaves the
  original frame completely unchanged under pandas 3.0's unconditional
  Copy-on-Write, and write the single `.loc` statement that actually
  performs the assignment.
- State the exact endpoint difference between `.loc` (label-based,
  inclusive of the stop) and `.iloc` (positional, exclusive of the stop),
  and predict which rows a given slice returns before running it.
- Explain why `series == np.nan` never finds a missing value and `.isna()`
  always does.
- Measure vectorised arithmetic against `.apply(lambda ...)` on the same
  column and report the gap as a ratio and a shape, never a millisecond
  figure.
- Read `.describe()`, `.info()`, `.head()` and `memory_usage(deep=True)` as
  the four commands you run on any frame you have not met before, and
  check `.describe()`'s numbers against hand computation.

## Prerequisites

- **Day 104** — NumPy arrays, dtypes, shape and vectorised thinking. A
  Series is a NumPy array with an index bolted on; this lab assumes you
  already have the array half of that picture.
- **Day 116** — descriptive statistics (mean, standard deviation, quartiles,
  Bessel's correction). Exercise 9's `.describe()` computes exactly what
  that day taught by hand.
- **Days 92–98** — data formats, pipelines and the habit of reading data
  before trusting it.
- **Week 13 (SQL)** — this lab's Tools section in the lesson compares
  pandas against SQLite for tabular questions; you do not need SQL to run
  anything here.
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
single-column DataFrame of random floats for exercise 7's timing
comparison, which needs a few megabytes and finishes in well under a
second. No GPU, no network beyond the one-time install, no meaningful disk
use.

## Required software

| Tool | Minimum | Used here | Why |
| --- | --- | --- | --- |
| `python3` | 3.11 | 3.14.0 | Runs everything; standard library `venv` builds the lab's environment |
| `pandas` | 3.0.5 exactly | 3.0.5 | Pinned exactly, not just floored — see `requirements/README.md` for why |
| `pyarrow` | 25.0.1 | 25.0.1 | Backs the pandas 3.0 `str` dtype and `Int64` nullable arrays |
| `numpy` | 2.5.2 | 2.5.2 | Underlies every Series; `np.nan`, `np.dtype` |
| `bash` | 3.2 | 3.2.57 | The test harness |

Check your Python in one line: `python3 --version`.

## Free and open-source options

Everything here is free.

- **pandas** (BSD 3-Clause) and **NumPy** (BSD 3-Clause) are fully open
  source with no paid tier.
- **PyArrow** (Apache 2.0) is the Arrow project's Python bindings, also
  fully open source, and is what makes pandas 3.0's `str` dtype possible.
- **polars** (MIT), described from its documentation in the lesson's Tools
  section rather than run here, is a free alternative worth knowing about
  specifically because it has **no implicit row index at all** — a
  deliberate design choice that throws pandas's index-centred behaviour
  (this whole lab) into sharp relief by contrast.
- **DB Browser for SQLite** (GPL/MPL) or plain **SQLite** (public domain),
  covered in Week 13, is the better tool when the "table" in question does
  not fit in memory or needs concurrent writers — the lesson's Tools
  section says exactly when to prefer it over pandas.

No account, no key, no paid tier, and no part of this lab is degraded
without one.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-120-pandas-series-and-dataframes
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import pandas; print(pandas.__version__)"
```

If your tools live somewhere unusual, `tests/run_tests.sh` takes an
override rather than guessing:

```bash
PYTHON=/path/to/python3 bash tests/run_tests.sh
```

## File structure

```text
day-120-pandas-series-and-dataframes/
├── README.md                     this file
├── metadata.yml                  lab metadata and the recorded run
├── security.md                   what this lab does to your machine
├── troubleshooting.md            grouped by the message you actually see
├── requirements/
│   ├── README.md                 versions, and why they are pinned exactly
│   └── requirements.txt          pandas==3.0.5, pyarrow==25.0.1, numpy==2.5.2
├── starter/                      YOUR work happens here
│   ├── exercises.py               nine functions, one blank each
│   └── check_progress.py          "N of 9 exercises complete."
├── examples/                     the reference. Read AFTER you have tried
│   ├── 01_three_ways_to_build.py
│   ├── 02_alignment.py
│   ├── 03_dtype_promotion.py
│   ├── 04_copy_on_write.py
│   ├── 05_loc_vs_iloc.py
│   ├── 06_nan_semantics.py
│   ├── 07_vectorized_vs_apply.py
│   ├── 08_string_dtype.py
│   └── 09_describe_known_column.py
├── tests/
│   └── run_tests.sh              41 checks of real values
└── expected-output/               captured from a real run on 2026-08-19
    ├── FIELDS.md                  what must match and what may differ
    ├── 01-three-ways-to-build.txt ... 09-describe-known-column.txt
    ├── starter-progress.txt       0 of 9 before you begin
    └── test-run.txt               the full harness run
```

## How to run

```bash
# 1. The whole thing. Start here — it should be green before you change
#    anything, and green again when you have finished.
bash tests/run_tests.sh
echo "exit code: $?"

# 2. Find out where you stand on the exercises. It will say 0 of 9.
.venv/bin/python3 starter/check_progress.py

# 3. Open starter/exercises.py and replace each `_FILL_THIS_IN` with real
#    code, re-running step 2 as you go.

# --- everything below is the reference. Look after you have tried. ---

# 4. Run any single reference script directly.
cd examples
../.venv/bin/python3 01_three_ways_to_build.py
../.venv/bin/python3 02_alignment.py
../.venv/bin/python3 03_dtype_promotion.py
../.venv/bin/python3 04_copy_on_write.py
../.venv/bin/python3 05_loc_vs_iloc.py
../.venv/bin/python3 06_nan_semantics.py
../.venv/bin/python3 07_vectorized_vs_apply.py
../.venv/bin/python3 08_string_dtype.py
../.venv/bin/python3 09_describe_known_column.py
cd ..
```

## What the commands do

**`bash tests/run_tests.sh`** confirms the installed pandas matches
`requirements.txt` exactly, runs all nine reference scripts and checks each
exits 0 with every internal assertion held, runs `starter/check_progress.py`
on the untouched checkout and confirms it honestly reports 0 of 9, then
solves every blank in a **scratch copy** (never touching the real
`starter/exercises.py`) and confirms the checker reports 9 of 9 with exit 0.
It then re-checks the lesson's sharpest claims independently in one Python
process, deliberately breaks one assertion to prove the suite can fail,
restores it, and confirms nothing was left on disk.

**`.venv/bin/python3 starter/check_progress.py`** runs your
`starter/exercises.py`, catching the `NameError` an unfilled
`_FILL_THIS_IN` raises so one incomplete exercise does not stop the others
from being checked, and reports each one as complete, wrong, or not yet
attempted.

**Each `examples/0N_*.py` script** is self-contained: it builds the data
for one exercise, prints what it built, asserts the real values against
independently computed expectations, and ends with
`0N_name.py: every assertion held.` on success.

## Expected output

The harness ends with a real captured line:

```text
41 checks, 0 failure(s).
```

and exits 0. `starter/check_progress.py` reports
`0 of 9 exercises complete.` with exit 1 on an untouched checkout.

The two facts this day is built around, exactly as captured:

```text
pd.Series(['a', 'b']).dtype  ->  str
```

```text
df['b'] before:  [10, 20, 30]
df['b'] after chained assignment `df[df['a'] > 1]['b'] = 0`:  [10, 20, 30]
warning(s) raised by that statement: ['ChainedAssignmentError']
df['b'] after `.loc[df['a'] > 1, 'b'] = 0`:  [10, 0, 0]
```

The full capture of every script is in `expected-output/`, and
`expected-output/FIELDS.md` says which values are specific to pandas 3.0.5
and would legitimately differ on 2.x, and which would not differ on any
correctly-installed copy of this exact version.

## Validation steps

1. `bash tests/run_tests.sh` ends with `41 checks, 0 failure(s).` and exits
   0.
2. `pd.Series(['a', 'b']).dtype` reads **`str`**, not `object`.
3. Chained assignment leaves `df['b']` at **`[10, 20, 30]`**, unchanged, and
   raises a **`ChainedAssignmentError`** warning; the equivalent `.loc`
   statement changes it to **`[10, 0, 0]`**.
4. Adding `x` (index `a, b, c`) to `y` (index `b, c, d`) puts `NaN` at
   **exactly** `a` and `d`, and sums `b` to **12.0** and `c` to **23.0**.
5. `df.loc['b':'d']` and `df.iloc[1:4]` return the **same three rows**;
   `df.iloc[1:3]` returns **one row fewer**, even though `3` is the
   position of the label `'d'` that `.loc` included.
6. An `int64` column `.reindex()`ed onto a label that was never there
   becomes **`float64`**, and a value past `2**53` loses exact precision;
   the same reindex on an `Int64` column keeps its dtype and its precision.
7. `.describe()` on `[2, 4, 4, 4, 5, 5, 7, 9]` gives count **8**, mean
   **5.0**, min **2**, max **9**, and a standard deviation matching Day
   116's Bessel-corrected formula to 9 decimal places.
8. Vectorised arithmetic beats `.apply(lambda ...)` by **at least 20x** on
   200,000 rows (this run measured roughly 250x — a ratio, not a promise).
9. `starter/check_progress.py` reports `0 of 9` on an untouched checkout
   and `9 of 9` once every `_FILL_THIS_IN` is replaced correctly.

## Tests

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

41 checks, exit 0 when they all pass and non-zero otherwise. They are value
checks, not file-existence checks: every reference script's internal
assertions are exercised, the exact alignment result and `.loc`/`.iloc`
row counts are checked independently in a second pass, and the starter
checker is exercised both incomplete and fully solved.

The suite also proves it is not vacuous: section 5 deliberately breaks the
assertion inside `08_string_dtype.py`, confirms the run exits non-zero with
a printed `FAIL:` line, restores the file, and confirms it passes again.

Override, if your tools are somewhere unusual:

```bash
PYTHON=/path/to/python3 bash tests/run_tests.sh
```

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

`tests/run_tests.sh` clears `__pycache__` and `.pytest_cache` both before
and after it runs, and its scratch copy of the solved starter lives in a
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

- **`pd.Series(['a', 'b']).dtype` prints `object`, not `str`** — you are
  not running pandas 3.0.5; check with
  `python3 -c "import pandas; print(pandas.__version__)"`.
- **Chained assignment doesn't warn, or silently updates the frame** — same
  cause: you are not on pandas 3.0's unconditional Copy-on-Write.
- **`.iloc[1:3]` returns one row fewer than expected** — not a bug; `.iloc`
  stops *before* its stop position, `.loc` stops *at and including* its
  stop label.
- **An ID column now prints with a trailing `.0`** — a `NaN` entered an
  `int64` column and promoted the whole thing to `float64`; use `Int64` if
  the column must never lose exact precision.

## Security notes

`security.md` has the full account. In short: this lab opens the network
exactly once, to install its three pinned packages, and everything else
runs offline, writes only inside its own `.venv`, needs no credential, and
touches no real data — every value in every exercise is a small invented
literal or a seeded random column generated purely to make exercise 7's
timing comparison meaningful at scale.

## Extension exercises

1. **Reproduce exercise 4 on pandas 2.x.** Create a second virtual
   environment with `pandas==2.2.0` (or any 2.x release) installed, run
   `examples/04_copy_on_write.py` against it, and write down exactly what
   differs — the warning class, whether the frame changes, and whether the
   result is the same on two separate runs. This is the fastest way to see
   why "Copy-on-Write is now unconditional" is a stronger guarantee than "you
   can opt into Copy-on-Write."
2. **Break exercise 2 on purpose and fix it two different ways.** Take two
   Series with completely disjoint indexes (no overlap at all) and predict
   what `x + y` returns before running it. Then produce a positional sum
   two different ways — `.to_numpy()` and `.reset_index(drop=True)` — and
   write one sentence on when each is the *safer* choice in a real
   pipeline.
3. **Measure the vectorised-vs-`.apply` ratio at three different row
   counts.** Run exercise 7's comparison at 2,000, 20,000 and 200,000 rows
   and record the ratio at each. Does the ratio grow, shrink, or stay
   roughly constant as the data grows? Explain what that tells you about
   where `.apply`'s overhead actually comes from.
4. **Find the `Int64` cost.** The nullable `Int64` dtype in exercise 3
   avoids the float64 promotion — but it is not free. Read the pandas
   documentation on nullable integer dtypes and write down one concrete
   cost (performance, interoperability, or otherwise) of using `Int64`
   everywhere instead of only where a `NaN` might actually appear.
5. **Rewrite exercise 9's `.describe()` check for a skewed column.** Build
   a column with a genuine outlier (Day 116's territory), run `.describe()`
   on it, and write down which of the eight reported numbers moved the
   most and which barely moved — tying `.describe()`'s output back to Day
   116's breakdown-point argument about the mean versus the median.

## Navigation

- **Previous day:** Day 119 — Analyzing an Experiment End to End
  (`labs/sections/math-statistics-and-data/day-119-analyzing-an-experiment-end-to-end/`).
- **Next day:** Day 121 — Loading and Inspecting Data
  (`labs/sections/math-statistics-and-data/day-121-loading-and-inspecting-data/`).
- **Week 18 project:** the week's project directory
  (`labs/sections/math-statistics-and-data/projects/week-18/`), "Messy
  Dataset Rescue" — building directly on the Series and DataFrame
  fundamentals from this lab.
