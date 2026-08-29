# Day 124 lab — Joins That Keep Their Shape

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Merging and Reshaping
- **Day number:** 124 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-124-merging-and-reshaping
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-124-merging-and-reshaping` when the site is running.
<!-- generated-links:end -->

## Purpose

Nine numbered exercises, each proving one real pandas 3.0.5 merge,
concat, or reshape behaviour by running code and reading real values. The
throughline is that **a join is a claim about cardinality, and pandas
will not check it for you unless you ask**. Exercise 1 makes the failure
concrete before anything else: merging two frames on a key that is
duplicated on both sides produces a per-key Cartesian product, not an
error. Exercise 2 gives the fix immediately — `validate=` turns a stated
assumption into an enforced one. Every later exercise adds one more piece
of the reshaping toolkit: `indicator=True`, the dtype-mismatch join,
the four join types, suffixes and `join()`, `concat` alignment, the
melt/pivot round trip, and `pivot` versus `pivot_table`.

## Learning objectives

By the end of this lab you will be able to:

- Demonstrate that a many-to-many merge produces exactly the product of
  the per-key group sizes on each side, and read a merge's input and
  output shapes to catch an unintended row explosion.
- Use `validate='one_to_one'` (or `'one_to_many'`) to make pandas raise a
  `MergeError` the instant a stated cardinality assumption is violated.
- Use `indicator=True` to see whether each row matched on the left only,
  the right only, or both, and confirm those three counts reconcile
  exactly with the input row counts.
- Demonstrate that a dtype-mismatched join key can fail either silently
  (zero matching rows, no exception) or loudly (`ValueError`), depending
  on the specific dtype mismatch, and know which pandas 3.0.5 catches.
- State the row counts inner, left, right and outer joins produce on the
  same pair of frames, and explain why each differs.
- Use `suffixes=` to control overlapping non-key column names instead of
  accepting the default `_x`/`_y`, and use `on=` versus `left_on=`/
  `right_on=` and `.join()` on an index correctly.
- Explain why `pd.concat`'s alignment fills unmatched columns or labels
  with `NaN` rather than erroring, on both `axis=0` and `axis=1`.
- Convert a wide DataFrame to long form with `melt` and back with
  `pivot`, and get the original frame back exactly.
- Explain the difference between `pivot` (raises on duplicate index/
  column pairs) and `pivot_table` (aggregates them), and choose correctly
  between an error and a silently averaged number.

## Prerequisites

- **Day 120** — Series and DataFrames, index alignment, and Copy-on-Write.
  This lab's tables are ordinary DataFrames built the way that day taught.
- **Day 121** — loading and inspecting data, and the type-inference traps
  that this lab's exercise 4 turns into a join failure.
- **Day 122** — boolean masks and the partition invariant, the same
  "check the parts reconcile with the whole" habit this lab applies to
  merges via `indicator=True`.
- **Day 123** — split-apply-combine and the reconciliation habit this lab
  extends from `groupby` to `merge`.
- **Week 13 (SQL)** — this lab's Tools section in the lesson compares
  `merge` against SQL joins and `sqlite3`; you do not need SQL to run
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

Anything. Every table in this lab is a small hand-built literal, at most
a dozen rows. No GPU, no network beyond the one-time install, no
meaningful disk use.

## Required software

| Tool | Minimum | Used here | Why |
| --- | --- | --- | --- |
| `python3` | 3.11 | 3.14.0 | Runs everything; standard library `venv` builds the lab's environment |
| `pandas` | 3.0.5 exactly | 3.0.5 | Every `merge`, `concat`, `melt`, `pivot` and `pivot_table` call |
| `pyarrow` | 25.0.1 | 25.0.1 | pandas 3.0's default backend, installed for parity with Days 120-123 |
| `numpy` | 2.5.2 | 2.5.2 | `NaN`-related comparisons in the `concat` alignment exercise |
| `pytest` | 9.1.1 | 9.1.1 | The test harness every exercise is written against |
| `bash` | 3.2 | 3.2.57 | The outer test harness |

Check your Python in one line: `python3 --version`.

## Free and open-source options

Everything here is free.

- **pandas** (BSD 3-Clause), **NumPy** (BSD 3-Clause) and **pytest** (MIT)
  are fully open source with no paid tier.
- **PyArrow** (Apache 2.0) is the Arrow project's Python bindings, also
  fully open source.
- **polars** (MIT), described from its documentation in the lesson's
  Tools section rather than run here, offers `join` with an explicit
  `validate` argument as a free alternative.
- Plain **SQLite** (public domain), covered in Week 13, is demonstrated
  in the lesson via the standard library's `sqlite3` module and enforces
  referential integrity pandas cannot — the lesson's Tools section says
  exactly when to prefer it.

No account, no key, no paid tier, and no part of this lab is degraded
without one.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-124-merging-and-reshaping
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
day-124-merging-and-reshaping/
├── README.md                     this file
├── metadata.yml                  lab metadata and the recorded run
├── security.md                   what this lab does to your machine
├── troubleshooting.md            grouped by the message you actually see
├── requirements/
│   ├── README.md                  versions, and what each package is for
│   └── requirements.txt           pandas==3.0.5, pyarrow==25.0.1, numpy==2.5.2, pytest==9.1.1
├── starter/                      YOUR work happens here
│   ├── 00_brief.md                exercise-by-exercise instructions
│   ├── data.py                    the ten tables every exercise uses
│   ├── conftest.py                fixtures wrapping data.py
│   └── test_merge.py              nine exercises, each a pytest.skip to replace
├── examples/                     the reference. Read AFTER you have tried
│   ├── data.py
│   ├── conftest.py
│   └── test_merge.py              the fully worked, 22-assertion answer key
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
#    22 skipped, 0 failed.
.venv/bin/pytest starter -v

# 3. Your work: open starter/test_merge.py and starter/00_brief.md, and
#    replace each pytest.skip(...) with real assertions.
.venv/bin/pytest starter -v -k test_1
.venv/bin/pytest starter -v -k test_2
# ... and so on through test_9, or just:
.venv/bin/pytest starter -v

# 4. Check everything, including the harness's own proof that it can fail.
bash tests/run_tests.sh
```

**Never run `pytest examples starter` in one command.** Both directories
define a module named `test_merge.py`; pytest imports test modules by
their dotted name, and running both together was tested directly in this
lab and aborts collection outright with an `import file mismatch` error
before running a single test. Run them as two separate commands, always,
as shown above.

## What the commands do

**`.venv/bin/pytest examples`** runs the fully worked reference suite: 22
tests across the nine exercises, each asserting a real value computed
from one of the ten tables in `data.py`.

**`.venv/bin/pytest starter`** runs your own suite. On an untouched
checkout, every one of the 22 tests calls `pytest.skip(...)` and is
reported as `s`, so the run exits 0 with nothing yet proven. Replace a
skip with real assertions and delete the skip line; when all 22 are
written and passing, the exercise is done.

**`bash tests/run_tests.sh`** confirms the installed pandas matches
`requirements.txt` exactly, runs `pytest examples` and requires 22
passed, runs `pytest starter` and requires 22 skipped on the checked-in
state, then solves every exercise in a **scratch copy** made with
`mktemp -d` (never touching the real `starter/test_merge.py`), confirms
that copy passes in full, deliberately breaks one assertion inside it,
confirms the run now exits non-zero with a failure reported, restores the
line, and confirms it passes again — proving the suite can genuinely fail
rather than merely claiming to. It finishes by checking no file in
`examples/` or `starter/` contains a URL, and that nothing is left on
disk.

## Expected output

The harness ends with a real captured line:

```text
13 checks, 0 failure(s)
```

and exits 0. `pytest examples` ends with:

```text
22 passed in 0.05s
```

`pytest starter`, on the checked-in state, ends with:

```text
22 skipped in 0.02s
```

The explosion this whole lab opens with, exactly as captured:

```text
left_dup shape  = (6, 3)
right_dup shape = (7, 3)
merged (inner)  = (14, 5)   # 3*2 (key A) + 2*4 (key B)
```

The full capture of both suites is in `expected-output/`, and
`expected-output/FIELDS.md` says which values are specific to pandas
3.0.5 or to this machine, and which would not differ on any correctly
installed copy of this exact version.

## Validation steps

1. `bash tests/run_tests.sh` ends with `13 checks, 0 failure(s)` and
   exits 0.
2. `left_dup` (6 rows) merged inner against `right_dup` (7 rows) on
   `cust_id` produces exactly **14** rows — 6 from key A, 8 from key B —
   matching the product of each side's per-key counts.
3. `validate='one_to_one'` raises `pandas.errors.MergeError` on
   `left_dup`/`right_dup`, and raises nothing on `left_keys`/`right_keys`.
4. `indicator=True` on `left_keys`/`right_keys` gives `left_only=1`,
   `right_only=1`, `both=3`, reconciling exactly with both input row
   counts (4 and 4) and the merged total (5).
5. `int_keyed` (int64) merged against `str_keyed` (categorical, same
   digits) returns **0** rows silently; casting `str_keyed`'s key to
   `int64` recovers **3** matching rows. A plain-string key of the same
   digits, in contrast, makes the merge **raise `ValueError`**.
6. The four join types on `left_keys`/`right_keys` give row counts
   `inner=3`, `left=4`, `right=4`, `outer=5`.
7. A plain merge on `price_left`/`price_right` produces `price_x` and
   `price_y`; `suffixes=('_catalog', '_live')` produces `price_catalog`
   and `price_live` instead.
8. `pd.concat` with mismatched columns (`axis=0`) or mismatched index
   labels (`axis=1`) fills exactly the unmatched cells with `NaN` and
   nothing else.
9. `wide.melt(...)` then `.pivot(...)` round-trips back to `wide` exactly,
   once the pivoted frame's index is reset and its columns reordered.
10. `dup_index_col.pivot(...)` raises `ValueError` on the duplicate
    `('Ann', 'math')` pair; `.pivot_table(..., aggfunc='mean')` returns
    **85.0** for that same cell instead.

## Tests

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

13 checks, exit 0 when they all pass and non-zero otherwise. They are
value checks, not file-existence checks: the reference suite's 22
assertions are exercised through `pytest`, the exercise suite is
confirmed all-skip on the checked-in state, and a scratch copy proves
the suite can genuinely fail and then recover.

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

- **`pytest examples starter` aborts with `import file mismatch`** — do
  not run both directories in one invocation; they share a module name.
- **Exercise 1's expected row count is not 14** — recompute it from each
  side's `value_counts()` rather than hardcoding a number.
- **Exercise 4's dtype-mismatch merge does not return zero rows** —
  confirm `str_keyed['id']` is a `pandas.Categorical`, not a plain string
  column; plain strings against `int64` now raise instead.
- **Exercise 8's round trip does not equal the original** — drop the
  pivoted columns' axis name with `.rename_axis(columns=None)` and
  reorder the columns back to the original order before comparing.

## Security notes

`security.md` has the full account. In short: this lab opens the network
exactly once, to install its four pinned packages, and everything else
runs offline, writes only inside its own `.venv`, needs no credential,
and touches no real data — every table is a small invented literal built
by hand in `data.py`.

## Extension exercises

1. **Reproduce the lesson's opening explosion at scale.** Build two
   100-row frames that each share a single duplicated key value and
   merge them; confirm you get exactly 10,000 rows, then add
   `validate='one_to_one'` and confirm it raises immediately, before any
   row is materialized.
2. **Feature-engineering angle.** Build a small "orders" frame and a
   "customer lookup" frame where the lookup table has one accidentally
   duplicated customer ID. Merge without `validate=`, then with it, and
   write one paragraph on what a machine-learning feature pipeline built
   on the unvalidated merge would have silently over-weighted.
3. **Compare `.join()` against `.merge()` on three or more frames.**
   Chain three lookup tables together with `.join()` on a shared index
   and again with two `.merge()` calls, and confirm the results agree.
4. **Simulate the SQL alternative.** Using Week 13's `sqlite3`, load
   `left_dup` and `right_dup` into two tables, add a `UNIQUE` constraint
   on the column that should not be duplicated, and confirm the database
   rejects the insert that a pandas `validate=` would have caught instead
   — but *before* any join runs, not at merge time.
5. **`pivot_table` with a different `aggfunc`.** Repeat exercise 9 with
   `aggfunc='sum'`, `aggfunc='max'`, and a custom function, and record how
   each one answers the "what happens to Ann's two math scores" question
   differently.

## Navigation

- **Previous day:** Day 123 — Groupby and Aggregation
  (`labs/sections/math-statistics-and-data/day-123-groupby-and-aggregation/`).
- **Next day:** Day 125
  (`labs/sections/math-statistics-and-data/`), continuing Week 18.
- **Week 18 project:** the week's project directory
  (`labs/sections/math-statistics-and-data/projects/week-18/`), "Messy
  Dataset Rescue" — building directly on the merge and reshape
  fundamentals from this lab.
