# Day 125 lab — Cleaning With Receipts

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Cleaning Messy Data
- **Day number:** 125 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-125-cleaning-messy-data
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-125-cleaning-messy-data` when the site is running.
<!-- generated-links:end -->

## Purpose

Nine numbered exercises, each proving one specific way a cleaning decision
changes the answer — on **pandas 3.0.5** specifically. Cleaning is not a
neutral chore that removes a warning; it is a sequence of irreversible
decisions about data you do not have, and every one of them changes what
a downstream analysis or model sees.

Exercise 1 opens with the failure that looks like good practice: impute a
numeric column's missing values with its own mean, then check the mean.
It is exactly unchanged — which is why the check proves nothing. This lab
measures what actually moves: the standard deviation strictly shrinks, and
a real correlation with another column strictly *attenuates*, toward zero
— never the direction a first guess usually expects.

Every table this lab uses is a small literal or a seeded random
construction, invented for the exercises; nothing is downloaded, and
nothing is left behind.

## Learning objectives

By the end of this lab you will be able to:

- State exactly which statistic mean imputation cannot disturb (the mean)
  and which two it always does (the standard deviation, which strictly
  shrinks, and a real correlation, which strictly attenuates toward zero).
- Explain, algebraically, why mean imputation can never inflate a
  correlation with an untouched column — only dilute one.
- Distinguish `fillna(0)` from a true missing-value fill, and show a case
  where zero collides with a value the data already legitimately contains.
- Choose among `dropna`'s `how`, `thresh` and `subset` arguments and state
  the exact row count each one produces on the same frame.
- Show, with a constructed example, why `ffill` on unsorted data is a real
  bug — and confirm sorting first fixes it.
- Build a missing-indicator column that survives after imputation has
  erased the original `isna()` evidence.
- Use `pd.to_numeric(errors='coerce')` and count exactly how many values
  it silently converted to missing, never coercing a column blind.
- Normalise string categories (`.str.strip()`, `.str.lower()`,
  `.str.replace()`) and show a raw `groupby` splitting one true category
  into several.
- Distinguish exact duplicates from duplicates on a named subset, and
  state which definition answers which real question.
- Write a small cleaning contract that asserts its own post-conditions and
  genuinely raises when they are violated.

## Prerequisites

- **Days 120–124** — pandas Series and DataFrames, loading and inspecting
  data, selecting and filtering, `groupby` and aggregation, and merging
  and reshaping. This lab assumes that foundation and does not re-teach
  it.
- **Day 116** — the mean's zero breakdown point and robust measures of
  spread, which motivate why a single imputed statistic is not the whole
  picture.
- **Day 117** — bias does not shrink with sample size, which is exactly
  why informative missingness is not fixed by having more rows.
- A working `python3` on your `PATH` to create the lab's virtual
  environment.

## Supported operating systems

| System | Status |
| --- | --- |
| macOS (Apple Silicon or Intel) | Captured here — macOS 26.5.2, arm64 |
| Linux (any current distribution) | Expected identical, given the pinned versions below |
| Windows | Use WSL and follow the Linux path. `mktemp -d` is used inside `tests/run_tests.sh`; native Windows was not tested and no output is claimed for it |

## Hardware requirements

Anything. Every table in this lab is forty rows or fewer. No GPU, no
meaningful disk use, and no network beyond the one-time install.

## Required software

| Tool | Minimum | Used here | Why |
| --- | --- | --- | --- |
| `python3` | 3.11 | 3.14.0 | Runs everything; standard library `venv` builds the lab's environment |
| `pandas` | 3.0.5 exactly | 3.0.5 | Pinned exactly — see `requirements/README.md` for why |
| `pyarrow` | 25.0.1 | 25.0.1 | Backs pandas 3.0's `str` dtype |
| `numpy` | 2.5.2 | 2.5.2 | Seeded random columns for the imputation and duplicates exercises |
| `pytest` | 9.1.1 | 9.1.1 | The test harness |

Check your Python in one line: `python3 --version`.

## Free and open-source options

Everything here is free.

- **pandas** (BSD 3-Clause), **NumPy** (BSD 3-Clause) and **PyArrow**
  (Apache 2.0) are fully open source with no paid tier.
- **pyjanitor** (MIT), described from its documentation in the lesson's
  Tools section rather than run here, offers a verb-style chaining API
  (`.clean_names()`, `.remove_empty()`) over the same pandas primitives
  this lab uses directly.
- **scikit-learn**'s `SimpleImputer` (BSD 3-Clause), also described from
  documentation only, performs the same imputation arithmetic behind a
  `fit`/`transform` boundary — the mechanism that stops a test set's
  statistics from leaking into training.
- **Great Expectations** and **pandera** (both Apache 2.0), described from
  documentation only, are declarative alternatives to the hand-rolled
  `assert_cleaning_contract` this lab's exercise 9 builds from scratch.

No account, no key, no paid tier, and no part of this lab is degraded
without one.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-125-cleaning-messy-data
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
day-125-cleaning-messy-data/
├── README.md                  this file
├── metadata.yml                lab metadata and the recorded run
├── security.md                 what this lab does to your machine
├── troubleshooting.md          grouped by the message you actually see
├── requirements/
│   ├── README.md                versions, and why they are pinned exactly
│   └── requirements.txt         pandas==3.0.5, pyarrow==25.0.1, numpy==2.5.2, pytest==9.1.1
├── starter/                    YOUR work happens here
│   ├── 00_brief.md               exercise-by-exercise explanation
│   ├── data.py                   the tables every exercise uses
│   ├── contract.py               the cleaning-contract helper (exercise 9)
│   ├── conftest.py               shared pytest fixtures
│   └── test_cleaning.py          nine exercises, each a pytest.skip to replace
├── examples/                   the reference. Read AFTER you have tried
│   ├── data.py
│   ├── contract.py
│   ├── conftest.py
│   └── test_cleaning.py          the 19-assertion reference suite
├── tests/
│   └── run_tests.sh             13 checks of real values
└── expected-output/              captured from a real run on 2026-08-19
    ├── FIELDS.md                 what must match and what may differ
    ├── examples-run.txt
    ├── starter-run.txt
    └── test-run.txt
```

## How to run

```bash
# 1. The whole thing. Start here — it should be green before you change
#    anything, and green again when you have finished.
bash tests/run_tests.sh
echo "exit code: $?"

# 2. See where you stand. On an untouched checkout this reports 19 skipped.
.venv/bin/pytest starter -v

# 3. Open starter/test_cleaning.py and replace each pytest.skip(...) with
#    real assertions, re-running step 2 as you go.

# --- everything below is the reference. Look after you have tried. ---

# 4. Run the reference suite directly.
.venv/bin/pytest examples -v
```

## What the commands do

**`bash tests/run_tests.sh`** confirms the installed pandas matches
`requirements.txt` exactly, runs `examples/` and confirms all 19
assertions pass, runs `starter/` on the untouched checkout and confirms it
honestly reports 19 skipped, then solves every exercise in a **scratch
copy** (never touching the real `starter/test_cleaning.py`), confirms 19
passed, deliberately breaks one assertion to prove the suite can fail,
restores it, confirms 19 passed again, checks neither directory contains a
network call, and confirms nothing is left on disk.

**`.venv/bin/pytest examples`** or **`.venv/bin/pytest starter`**, always
as two *separate* commands — see `troubleshooting.md` for what happens if
you pass both directories to one invocation.

## Expected output

The harness ends with a real captured line:

```text
13 checks, 0 failure(s)
```

and exits 0. `pytest examples` ends with `19 passed`; `pytest starter` on
an untouched checkout ends with `19 skipped`.

The day's sharpest fact, exactly as captured:

```text
income.mean() before imputation:  52666.679...
income.mean() after imputation:   52666.679...   (identical)
income.std()  before imputation:  10663.947
income.std()  after imputation:    9195.697   (strictly smaller)
corr(income, spending) before:        0.745156
corr(income, spending) after:         0.606148   (strictly SMALLER in magnitude)
```

The full capture of every run is in `expected-output/`, and
`expected-output/FIELDS.md` says which values are specific to pandas
3.0.5 and which would not differ on any correctly installed copy of this
exact version.

## Validation steps

1. `bash tests/run_tests.sh` ends with `13 checks, 0 failure(s)` and exits
   0.
2. Mean-imputing `income_spending`'s `income` column leaves the mean
   unchanged to six decimal places, strictly shrinks the standard
   deviation (10663.947 → 9195.697), and strictly shrinks
   `corr(income, spending)` in magnitude (0.745156 → 0.606148).
3. `fillna(0)` on `temperature_readings` moves the mean by exactly
   -3.197143, and makes the genuine `0.0` reading indistinguishable from
   the three imputed ones.
4. `dropna_frame.dropna(...)` gives row counts 2 (`how='any'`), 8
   (`how='all'`), 5 (`thresh=2`) and 4 (`subset=['email']`).
5. `ffill` on the unsorted `sensor_timeseries` gives the wrong value at
   day 2 (14.0 instead of 10.0) and day 3 (17.0 instead of 10.0); sorting
   by `day` first gives the correct
   `[10.0, 10.0, 10.0, 13.0, 14.0, 14.0, 16.0, 17.0]`.
6. A missing-indicator column recorded before imputation still equals the
   original `isna()` mask exactly, after `isna()` itself reports all
   `False`.
7. `pd.to_numeric(..., errors='coerce')` on `coerce_frame` produces
   exactly 3 new missing values, matching the 3 planted garbage strings.
8. `country_frame['country_raw'].nunique()` is 8 before normalising and 2
   after; a raw `groupby` produces 8 groups where the truth is 2.
9. `duplicates_frame.duplicated().sum()` is 1; `duplicated(subset=[...])`
   is 2.
10. `assert_cleaning_contract` passes on clean data and raises
    `ContractViolation` on three different violations (a null key column,
    a wrong dtype, a row count outside range).

## Tests

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

13 checks, exit 0 when they all pass and non-zero otherwise. They are
value checks, not file-existence checks: the reference suite's 19
assertions are exercised, the starter suite is confirmed all-skip, and the
suite is proven able to fail and then restored.

Override, if your tools are somewhere unusual:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

`tests/run_tests.sh` also clears `__pycache__` and `.pytest_cache` both
before and after it runs, and confirms nothing is left behind — so if you
only ran the harness, there is nothing left to clean up.

To remove the lab's virtual environment entirely: `rm -rf .venv`.

To reset your own work and start the exercises again:

```bash
git checkout -- starter/
```

## Troubleshooting

`troubleshooting.md` has the full list, grouped by the message you
actually see. The ones you are most likely to meet:

- **Exercise 1's correlation assertion fails because you expected it to go
  UP** — that is very likely the point; see `starter/00_brief.md`.
- **`pytest examples starter` errors or behaves strangely** — never run
  both directories in one invocation; they share a module name.
- **Exercise 4's "wrong" and "correct" results look identical** — you
  likely sorted before both calls; the "wrong" branch must skip the sort.

## Security notes

`security.md` has the full account. In short: this lab opens the network
exactly once, to install its four pinned packages, and everything else
runs offline, writes only into `.venv/`, needs no credential, and touches
no real data — every table is a small invented literal or a seeded
random construction generated purely for the exercises.

## Extension exercises

1. **Reproduce exercise 1's attenuation proof from first principles.**
   Write out the Pearson correlation's covariance sum term by term for a
   single imputed row, and show algebraically that its contribution is
   exactly zero regardless of the other column's value. Confirm your
   derivation against a fresh seeded dataset of your own.
2. **Build a genuinely MNAR missingness pattern.** Make `income` more
   likely to be missing exactly where `income` itself is high (simulating
   high earners who decline to report), impute with the mean, and measure
   how much the imputed mean itself is now biased relative to the true
   (unobserved) population mean — a bias no amount of additional
   MCAR-style data would fix, per Day 117.
3. **Extend the cleaning contract with a fourth post-condition**: no
   duplicate `customer_id` values. Add it to `assert_cleaning_contract`,
   write a test proving it passes on clean data, and a second test proving
   it raises on a frame you construct with a repeated `customer_id`.
4. **Read the pandera or Great Expectations documentation** (neither is
   installed here) and rewrite exercise 9's contract as a declarative
   schema in one of them, from the documentation alone. Write down what,
   specifically, the declarative form buys you over the hand-rolled
   function in `contract.py`, and what it costs.
5. **Measure the IQR-versus-z-score outlier count on a skewed column.**
   Build a column with a long right tail (for example, exponential
   noise), flag outliers both ways, and report how many points the two
   rules disagree on — then write one sentence on which of those points
   you would actually remove, and why removal is a judgement call and not
   a mechanical one.

## Navigation

- **Previous day:** Day 124 — Merging and Reshaping
  (`labs/sections/math-statistics-and-data/day-124-merging-and-reshaping/`).
- **Next day:** Day 126 — A Reproducible Cleaning Pipeline
  (`labs/sections/math-statistics-and-data/day-126-a-reproducible-cleaning-pipeline/`).
- **Week 18 project:** the week's project directory
  (`labs/sections/math-statistics-and-data/projects/week-18/`), "Messy
  Dataset Rescue" — building directly on the cleaning habits from this
  lab.
