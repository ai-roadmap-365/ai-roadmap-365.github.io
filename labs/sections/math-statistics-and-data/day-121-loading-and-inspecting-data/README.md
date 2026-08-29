# Day 121 lab — Read It Right

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Loading and Inspecting Data
- **Day number:** 121 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-121-loading-and-inspecting-data
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-121-loading-and-inspecting-data` when the site is running.
<!-- generated-links:end -->

## Purpose

Nine numbered exercises, each proving one specific way `read_csv()` — and
its siblings for JSON, Parquet and SQL — silently guesses wrong, on
**pandas 3.0.5** specifically. `read_csv()` is a type-inference engine
wearing the costume of a file reader: it guesses correctly most of the
time, and when it guesses wrong, nothing raises. You get different data
than the file contained, and every downstream computation runs on it
without complaint.

Every file this lab reads is written by the lab itself, into a temporary
directory it creates and deletes; nothing is downloaded, and nothing is
left behind — this lab proves that with a real check, not a promise.

The throughline is the moment the file is read. Exercise 1 opens with the
famous case: a country-code column contains `NA` for Namibia, and pandas'
default `na_values` list includes the literal string `"NA"` — so Namibia
silently becomes a missing value. Exercise 2 hits the second one almost
everyone meets at work within a month: an identifier column of `00123`
becomes the integer `123`, leading zeros gone, with no warning anywhere.

## Learning objectives

By the end of this lab you will be able to:

- Explain why `read_csv()` reading `"NA"` as missing, by default, is not a
  bug — and use `keep_default_na=False` when a literal `"NA"` value must
  survive.
- Preserve a leading-zero identifier column with `dtype={"col": "str"}`
  instead of letting it silently become a shorter integer.
- Demonstrate that an integer above `2**53` survives `read_csv()`'s
  `int64` inference exactly, but is silently corrupted by a `float64` cast.
- State what `parse_dates` changes about a date column's dtype, and show a
  concrete case where a string-sorted date column returns the wrong
  chronological order.
- Diagnose an encoding mismatch (`UnicodeDecodeError` or mojibake) and fix
  it by naming the correct `encoding=` argument.
- Read a file larger than memory with `chunksize`, and confirm a
  chunk-by-chunk aggregate equals the whole-file answer exactly.
- State, and demonstrate with a real round-trip, why CSV loses dtypes and
  Parquet preserves them exactly — the strongest practical argument
  against using CSV as an interchange format between your own programs.
- Run the eight-command inspection battery (`.head()`, `.info()`,
  `.dtypes`, `.describe()`, `.isna().sum()`, `.nunique()`,
  `.value_counts()`, `memory_usage(deep=True)`) on an unfamiliar frame and
  say what each command is for.
- Convert a low-cardinality string column to `category` and measure the
  memory reduction as a ratio, not a byte count.

## Prerequisites

- **Day 120** — pandas Series and DataFrames: the index, dtypes including
  the pandas-3.0 `str` default and `Int64`/`int64` promotion, and
  Copy-on-Write. This lab assumes that foundation and does not re-teach it.
- **Days 92–98** — data formats and pipelines, and the habit of reading
  data before trusting it.
- **Week 13 (SQL)** — exercise 10's `read_sql()` demonstration runs a real
  query against a real `sqlite3` connection; no SQL beyond a `SELECT ...
  WHERE` is required.
- A working `python3` on your `PATH` to create the lab's virtual
  environment.

## Supported operating systems

| System | Status |
| --- | --- |
| macOS (Apple Silicon or Intel) | Captured here — macOS 26.5.2, arm64 |
| Linux (any current distribution) | Expected identical, given the pinned versions below |
| Windows | Use WSL and follow the Linux path. `mktemp -d` is used inside `tests/run_tests.sh`; native Windows was not tested and no output is claimed for it |

## Hardware requirements

Anything. The largest file this lab writes is a 50,000-row, single-column
CSV for the chunking exercise, a few hundred kilobytes on disk. No GPU, no
meaningful disk use, and no network beyond the one-time install.

## Required software

| Tool | Minimum | Used here | Why |
| --- | --- | --- | --- |
| `python3` | 3.11 | 3.14.0 | Runs everything; standard library `venv` builds the lab's environment |
| `pandas` | 3.0.5 exactly | 3.0.5 | Pinned exactly — see `requirements/README.md` for why |
| `pyarrow` | 25.0.1 | 25.0.1 | Backs `to_parquet()`/`read_parquet()` and pandas 3.0's `str`/`Int64` dtypes |
| `numpy` | 2.5.2 | 2.5.2 | Seeded random columns for the chunking and category-memory exercises |
| `bash` | 3.2 | 3.2.57 | The test harness |

`sqlite3`, `csv`, `json` and `io` are all standard library — nothing extra
to install for exercise 10 or the inspection battery.

Check your Python in one line: `python3 --version`.

## Free and open-source options

Everything here is free.

- **pandas** (BSD 3-Clause), **NumPy** (BSD 3-Clause) and **PyArrow**
  (Apache 2.0) are fully open source with no paid tier.
- **SQLite** (public domain) is the database engine behind exercise 10's
  `read_sql()` demonstration — no server to install or run.
- **polars** (MIT), described from its documentation in the lesson's Tools
  section rather than run here, offers a lazy `scan_csv()` that defers
  reading until a query actually needs the data — a different answer to
  the "file larger than memory" problem than pandas' `chunksize`.
- **openpyxl** (MIT), also described from documentation only, is the
  library `pandas.read_excel()` uses under the hood for `.xlsx` files.

No account, no key, no paid tier, and no part of this lab is degraded
without one.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-121-loading-and-inspecting-data
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
day-121-loading-and-inspecting-data/
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
│   ├── 01_the_namibia_trap.py
│   ├── 02_leading_zeros.py
│   ├── 03_precision_loss.py
│   ├── 04_dates.py
│   ├── 05_encoding.py
│   ├── 06_chunking.py
│   ├── 07_csv_vs_parquet.py
│   ├── 08_inspection_battery.py
│   ├── 09_category_memory.py
│   └── 10_other_formats.py           supplementary: JSON, sqlite3, stdlib csv
├── tests/
│   └── run_tests.sh                 42 checks of real values
└── expected-output/                  captured from a real run on 2026-08-19
    ├── FIELDS.md                     what must match and what may differ
    ├── 01-the-namibia-trap.txt ... 10-other-formats.txt
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
../.venv/bin/python3 01_the_namibia_trap.py
../.venv/bin/python3 02_leading_zeros.py
../.venv/bin/python3 03_precision_loss.py
../.venv/bin/python3 04_dates.py
../.venv/bin/python3 05_encoding.py
../.venv/bin/python3 06_chunking.py
../.venv/bin/python3 07_csv_vs_parquet.py
../.venv/bin/python3 08_inspection_battery.py
../.venv/bin/python3 09_category_memory.py
../.venv/bin/python3 10_other_formats.py
cd ..
```

## What the commands do

**`bash tests/run_tests.sh`** confirms the installed pandas matches
`requirements.txt` exactly, runs all ten reference scripts and checks each
exits 0 with every internal assertion held, runs `starter/check_progress.py`
on the untouched checkout and confirms it honestly reports 0 of 9, then
solves every blank in a **scratch copy** (never touching the real
`starter/exercises.py`) and confirms the checker reports 9 of 9 with exit 0.
It then re-checks the lesson's sharpest claims independently in one Python
process, deliberately breaks one assertion to prove the suite can fail,
restores it, and confirms nothing was left on disk — including a dedicated
check that no `.csv`, `.parquet` or `.db` file survives anywhere in the lab.

**`.venv/bin/python3 starter/check_progress.py`** runs your
`starter/exercises.py`, catching the `NameError` an unfilled
`_FILL_THIS_IN` raises so one incomplete exercise does not stop the others
from being checked, and reports each one as complete, wrong, or not yet
attempted.

**Each `examples/0N_*.py` script** is self-contained: it writes whatever
small file the exercise needs into a temporary directory it created, reads
it back, prints what it found, asserts the real values against
independently computed expectations, deletes the temporary directory, and
ends with `0N_name.py: every assertion held.` on success.

## Expected output

The harness ends with a real captured line:

```text
42 checks, 0 failure(s).
```

and exits 0. `starter/check_progress.py` reports
`0 of 9 exercises complete.` with exit 1 on an untouched checkout.

The day's two sharpest facts, exactly as captured:

```text
default read:  NA for Namibia -> NaN (missing)
keep_default_na=False:  NA for Namibia -> 'NA' (the literal string)
```

```text
order_id (nullable Int64, one missing value):
  after CSV round-trip:      float64  -- 1001.0, 1002.0, NaN
  after Parquet round-trip:  Int64    -- 1001, 1002, <NA>  (exact)
```

The full capture of every script is in `expected-output/`, and
`expected-output/FIELDS.md` says which values are specific to pandas 3.0.5
and would legitimately differ on 2.x, and which would not differ on any
correctly-installed copy of this exact version.

## Validation steps

1. `bash tests/run_tests.sh` ends with `42 checks, 0 failure(s).` and exits
   0.
2. The default read of a country-code CSV turns Namibia's `NA` into a real
   missing value; `keep_default_na=False` keeps it as the string `'NA'`.
3. The default read of `id` column `"00123"` gives the integer **`123`**;
   `dtype={"id": "str"}` gives **`'00123'`** exactly.
4. An integer past `2**53` survives `int64` inference exactly, and loses
   exactly its last digit through a `float64` cast.
5. A date column left unparsed is the `str` dtype and sorts lexically —
   getting the chronological order wrong the moment one date drops a
   leading zero; `parse_dates=[...]` gives the `datetime64` dtype and
   sorts correctly.
6. Reading a latin-1 file with `encoding="utf-8"` raises
   `UnicodeDecodeError`; the correct encoding round-trips the text exactly.
7. An aggregate computed chunk-by-chunk (`chunksize=1000`, and again with
   an odd `chunksize=777`) equals the whole-file aggregate exactly.
8. A CSV round-trip changes at least one dtype (a nullable `Int64` column
   with a missing value becomes `float64`); a Parquet round-trip preserves
   every dtype, and every value, exactly.
9. The inspection battery reports exact, known values on a constructed
   frame: 1 missing value per column, `north` as the top `value_counts()`
   entry with count 4.
10. Converting a low-cardinality string column to `category` reduces
    `memory_usage(deep=True)` by **at least 5x** (this run measured
    roughly 12.4x — a ratio, not a promise).

## Tests

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

42 checks, exit 0 when they all pass and non-zero otherwise. They are value
checks, not file-existence checks: every reference script's internal
assertions are exercised, the lesson's sharpest claims are re-checked
independently in a second pass, and the starter checker is exercised both
incomplete and fully solved.

The suite also proves it is not vacuous: section 5 deliberately breaks the
assertion inside `03_precision_loss.py`, confirms the run exits non-zero
with a printed `FAIL:` line, restores the file, and confirms it passes
again.

Override, if your tools are somewhere unusual:

```bash
PYTHON=/path/to/python3 bash tests/run_tests.sh
```

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

Every exercise script writes into its own `tempfile.mkdtemp()` directory
and removes it, in a `finally:` block, before exiting — including when an
assertion fails. `tests/run_tests.sh` also clears `__pycache__` and
`.pytest_cache` both before and after it runs, and independently checks
that no `.csv`, `.parquet` or `.db` file survives anywhere in the lab — so
if you only ran the harness or the reference scripts, there is nothing
left to clean up.

To remove the lab's virtual environment entirely: `rm -rf .venv`.

To reset your own work and start the exercises again:

```bash
git checkout -- starter/
```

## Troubleshooting

`troubleshooting.md` has the full list, grouped by the message you
actually see. The ones you are most likely to meet:

- **Exercise 1's `code` column doesn't come back as missing for Namibia**
  — you are running with `keep_default_na=False` already, or an older
  pandas with a different `na_values` default.
- **Exercise 3's precision numbers look "off by more than one"** — confirm
  `2**53 + 1` is computed in Python, not truncated by a shell.
- **Exercise 5 doesn't raise `UnicodeDecodeError`** — some byte sequences
  are valid under both encodings and mojibake silently instead; that is
  the other half of the danger this exercise is about.
- **A `.csv`/`.parquet`/`.db` file is left behind** — a script was likely
  interrupted before its cleanup ran; re-run the harness.

## Security notes

`security.md` has the full account. In short: this lab opens the network
exactly once, to install its three pinned packages, and everything else
runs offline, writes only into `.venv/` and per-exercise temporary
directories it deletes itself, needs no credential, and touches no real
data — every value in every exercise is a small invented literal or a
seeded random column generated purely to make the chunking and
category-memory exercises meaningful at scale.

## Extension exercises

1. **Reproduce exercise 5 with a byte sequence that mojibakes instead of
   raising.** Find (or construct) a short latin-1 string whose bytes also
   happen to decode as valid — but different — UTF-8, and show the silent
   wrong-text result side by side with this lab's loud
   `UnicodeDecodeError` case. Write one sentence on which failure mode is
   more dangerous in a real pipeline and why.
2. **Measure the CSV-versus-Parquet gap at scale.** Build a 500,000-row
   DataFrame with a mix of `Int64`, `float64`, `bool` and `str` columns,
   round-trip it through both formats, and compare not just dtypes but
   file size and read time. Report the file-size ratio as a ratio, not a
   byte count.
3. **Use `chunksize` to compute something `.sum()` cannot: a running
   maximum.** Read a CSV in chunks and compute the true whole-file maximum
   without ever loading the whole file into memory at once. Confirm it
   equals the whole-file `.max()`.
4. **Read the polars documentation on `scan_csv()` and lazy evaluation.**
   Write down, from the documentation alone (polars is not installed
   here), what specifically it defers that pandas' `chunksize` does not,
   and when that difference would matter for a file that does not fit in
   memory even one chunk at a time.
5. **Find your own real "NA" trap.** Pick any small, real dataset you have
   access to (or a public one you already trust) and run
   `pd.read_csv(path, keep_default_na=False)` next to the default read.
   Diff the two frames column by column and write down every value that
   changed — this is the fastest way to discover whether a dataset you
   already use has silently absorbed a false-missing value.

## Navigation

- **Previous day:** Day 120 — pandas: Series and DataFrames
  (`labs/sections/math-statistics-and-data/day-120-pandas-series-and-dataframes/`).
- **Next day:** Day 122 — Selecting and Filtering
  (`labs/sections/math-statistics-and-data/day-122-selecting-and-filtering/`).
- **Week 18 project:** the week's project directory
  (`labs/sections/math-statistics-and-data/projects/week-18/`), "Messy
  Dataset Rescue" — building directly on the loading and inspection
  habits from this lab.
