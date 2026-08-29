# Day 122 lab — Filters That Add Up

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Selecting and Filtering
- **Day number:** 122 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-122-selecting-and-filtering
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-122-selecting-and-filtering` when the site is running.
<!-- generated-links:end -->

## Purpose

Nine numbered exercises, each asserting real pandas behaviour against a
value computed independently, on **pandas 3.0.5**. This is the day you
stop trusting that a filter shows you the whole picture. Split a column of
scores into "high performers" and "everyone else" with two ordinary
comparisons, and the two groups do not add up to the total — rows with a
missing score fail both comparisons and simply are not in either answer,
with no error raised anywhere.

The through-line is that invariant: **a filter is a claim about which rows
you kept, and the rows you did not keep are your responsibility too.**
Every exercise after the first builds on it — precedence traps that make
`&` silently misgroup a compound condition, a mask that keeps its promise
across a reordered frame but breaks the moment you strip its labels off,
and a `.str.contains()` call that behaves differently depending on a
dtype default that changed under pandas 3.0.

## Learning objectives

By the end of this lab you will be able to:

- Demonstrate that a naive two-way split of a column with missing values
  (`score > 50`, `score <= 50`) does not sum to the total row count, name
  the exact shortfall, and build a three-way partition that does.
- Explain why `mask1 and mask2` raises `ValueError` while `mask1 & mask2`
  does not, and use `&`, `|` and `~` correctly to combine masks.
- Recognise the `&`-binds-tighter-than-comparisons precedence trap in an
  unparenthesised compound filter, and parenthesise every comparison
  correctly.
- Filter and select in one `.loc` call, and know why that stays safe under
  Copy-on-Write when you assign through it.
- Explain why a boolean mask built from a reordered copy of a DataFrame
  still selects the correct rows when applied to the original — because
  filtering aligns by label — and why stripping the mask to a raw NumPy
  array with `.to_numpy()` breaks that guarantee.
- Use `.query()` for readability, including its `@variable` syntax, and
  state honestly when a plain mask is the simpler choice.
- Use `.isin()`, `.between()` and `.str.contains()` correctly, including
  the `na=False` fix for `.str.contains()` on a column with missing
  values, and state which pandas-3.0 dtype default changes whether that
  trap fires at all.
- Choose between `.nlargest()`/`.nsmallest()` and
  `.sort_values().head()`, and explain the one case — a tie sitting on the
  cutoff — where they can return a different number of rows.
- Use `.drop_duplicates()` with `subset` and `keep`, and explain why
  "duplicate" means whatever columns `subset` names, not a fixed property
  of a row.
- Explain why `.filter()` selects labels, not rows, and predict what it
  does when given row-shaped arguments by mistake.

## Prerequisites

- **Day 120** — Series and DataFrames, index alignment, and Copy-on-Write.
  This lab assumes you already know a mask is a Series with an index, and
  that `df.loc[mask, 'col'] = value` is the safe assignment form.
- **Day 121** — loading and inspecting data, including how missing values
  arrive in a real column. This lab's `score` column with two missing
  entries plays the same role Day 121's inspection battery prepared you
  for.
- A working `python3` on your `PATH` to create the lab's virtual
  environment.

## Supported operating systems

| System | Status |
| --- | --- |
| macOS (Apple Silicon or Intel) | Captured here — macOS 26.5.2, arm64 |
| Linux (any current distribution) | Expected identical, given the pinned versions below |
| Windows | Use WSL and follow the Linux path. `mktemp -d` and `sed -i.bak` are used inside `tests/run_tests.sh`; native Windows was not tested and no output is claimed for it |

## Hardware requirements

Anything. Every table built in this lab has at most eight rows and lives
entirely in memory as a literal. No GPU, no network beyond the one-time
install, no meaningful disk use.

## Required software

| Tool | Minimum | Used here | Why |
| --- | --- | --- | --- |
| `python3` | 3.11 | 3.14.0 | Runs everything; standard library `venv` builds the lab's environment |
| `pandas` | 3.0.5 exactly | 3.0.5 | Pinned exactly because exercise 5's `.str.contains()` result depends on the pandas-3.0 `str`-dtype default — see `requirements/README.md` |
| `pyarrow` | 25.0.1 | 25.0.1 | Backs the pandas 3.0 `str` dtype exercised in exercise 5 |
| `numpy` | 2.5.2 | 2.5.2 | Underlies every Series; `np.nan` and its comparison semantics |
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
  specifically because its `.filter(pl.col('a') > 1)` composes conditions
  inside one expression object rather than through Python's `&`/`|`/`~`
  operators, which removes exercise 3's precedence trap by construction.
- **SQLite** (public domain) or **DB Browser for SQLite** (GPL/MPL),
  covered in Week 13, is the better tool when "filter" really means
  `WHERE` against data too large to hold in memory, or shared by
  concurrent writers — the lesson's Tools section says exactly when to
  push a filter into the database instead of pandas.

No account, no key, no paid tier, and no part of this lab is degraded
without one.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-122-selecting-and-filtering
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
day-122-selecting-and-filtering/
├── README.md                        this file
├── metadata.yml                     lab metadata and the recorded run
├── security.md                      what this lab does to your machine
├── troubleshooting.md               grouped by the message you actually see
├── requirements/
│   ├── README.md                    versions, and why they are pinned exactly
│   └── requirements.txt             pandas==3.0.5, pyarrow==25.0.1, numpy==2.5.2
├── starter/                         YOUR work happens here
│   ├── exercises.py                  nine functions, one blank each
│   └── check_progress.py             "N of 9 exercises complete."
├── examples/                        the reference. Read AFTER you have tried
│   ├── 01_partition_invariant.py
│   ├── 02_and_or_raise.py
│   ├── 03_precedence.py
│   ├── 04_mask_alignment.py
│   ├── 05_str_contains_na.py
│   ├── 06_query_equivalence.py
│   ├── 07_isin_vs_chained.py
│   ├── 08_nlargest_vs_sort_head.py
│   └── 09_drop_duplicates_and_filter.py
├── tests/
│   └── run_tests.sh                 41 checks of real values
└── expected-output/                  captured from a real run on 2026-08-19
    ├── FIELDS.md                     what must match and what may differ
    ├── 01-partition-invariant.txt ... 09-drop-duplicates-and-filter.txt
    ├── starter-progress.txt          0 of 9 before you begin
    └── test-run.txt                  the full harness run
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
../.venv/bin/python3 01_partition_invariant.py
../.venv/bin/python3 02_and_or_raise.py
../.venv/bin/python3 03_precedence.py
../.venv/bin/python3 04_mask_alignment.py
../.venv/bin/python3 05_str_contains_na.py
../.venv/bin/python3 06_query_equivalence.py
../.venv/bin/python3 07_isin_vs_chained.py
../.venv/bin/python3 08_nlargest_vs_sort_head.py
../.venv/bin/python3 09_drop_duplicates_and_filter.py
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

**Each `examples/NN_*.py` script** is self-contained: it builds its own
small DataFrame, runs the behaviour the exercise is about, prints what it
found, and asserts every claim with a `check()` helper that prints `ok:`
or `FAIL:` per line and a final `N checks, M failure(s).` summary, exiting
non-zero if anything failed.

## Expected output

See `expected-output/` for the full captured output of every script and
the full test run, and `expected-output/FIELDS.md` for exactly which
values are specific to pandas 3.0.5 and which are stable across versions.
The short version: `bash tests/run_tests.sh` ends with
`41 checks, 0 failure(s).` and exit code `0`.

## Validation steps

```bash
bash tests/run_tests.sh; echo "exit=$?"     # should print 41 checks, 0 failure(s). and exit=0
.venv/bin/python3 starter/check_progress.py # on the untouched checkout: 0 of 9, exit 1
```

## Tests

`tests/run_tests.sh` is the only test suite. It has six sections: tool
versions, the nine reference scripts, the starter checker (both empty and
solved), an independent re-check of the lesson's sharpest claims, a
deliberate-failure proof, and a cleanliness check. Run it with
`bash tests/run_tests.sh` from the lab root; it needs no arguments and no
network beyond the one-time `pip install`.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab's virtual environment entirely
git checkout -- starter/   # optional: discard your exercise attempts
```

`tests/run_tests.sh` already removes `__pycache__` and `.pytest_cache`
before and after every run, so a normal `bash tests/run_tests.sh` leaves
nothing behind on its own.

## Troubleshooting

See `troubleshooting.md` for messages grouped by what you actually see —
`ValueError` from `and`/`or`, the precedence trap, the mask-alignment
`UserWarning`, the `.str.contains()` `ValueError`, `.query()`'s
`UndefinedVariableError`, and more.

## Security notes

See `security.md`. In short: one network connection ever (the `pip
install`), everything else runs offline, nothing outside this directory is
touched, and every dataset in this lab is a small literal invented for the
demonstration.

## Extension exercises

- Rebuild exercise 1's invariant check as a small reusable function,
  `assert_partition(df, *masks)`, that raises a clear `AssertionError`
  naming the exact row-count shortfall if a list of masks does not
  partition a DataFrame — and use it to check your own work in a future
  lab.
- Exercise 8 showed `nlargest(keep='all')` returning more rows than asked
  for on a tie. Write a version of the same table with a tie at rank 1
  instead of at the cutoff, and predict — then verify — whether
  `keep='all'` changes anything when the tie is not at the boundary.
- Exercise 5's `.str.contains()` trap depends on dtype. Build a DataFrame
  from a real `read_csv()` call (Day 121) on a small CSV you write with a
  blank cell in a text column, and check whether the inferred dtype
  reproduces the `object`-dtype trap or the `str`-dtype non-trap by
  default.
- `.filter()`'s `regex=` argument was only touched briefly in exercise 9.
  Write a filter that selects every column whose name ends in `_id` from
  a wider synthetic table, and compare it against manually listing the
  column names with `items=`.

## Navigation

Part of Week 18 ("pandas and Data Wrangling"), Day 122 of 365, in the
`math-statistics-and-data` section's `data-analysis` subsection. Preceded
by Day 121 (Loading and Inspecting Data) and followed by Day 123 (Groupby
and Aggregation).
