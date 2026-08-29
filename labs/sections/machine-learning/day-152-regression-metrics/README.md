# Day 152 lab — What You Report Is Not What You Optimise

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Regression Metrics
- **Day number:** 152 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-152-regression-metrics
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-152-regression-metrics` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 149 established the line: a loss is what you optimise, a metric is
what you report, and they do not have to be the same function. This lab
measures the reporting side for regression -- RMSE, MAE, MAPE, R2 and
adjusted R2 -- and the specific way each one can mislead you.

The centrepiece is R2, because it is the most quoted and least understood
number in regression. Add columns of pure noise to a linear model and its
**training** R2 climbs anyway, from 0.5554 to 0.7403 with a hundred
useless columns, because more predictors can only help a training-set fit.
Adjusted R2 corrects that climb at a modest number of extra columns and
then **breaks down itself** once the predictor count approaches the sample
size. And R2 has no lower bound at all: a deliberately bad predictor scores
-4.7009, not the 0 most people expect as a floor.

The other headline measurement is a genuine metric ranking inversion:

| Model | RMSE | MAE |
| --- | --- | --- |
| A: many small, consistent errors | 1.947 | 1.586 |
| B: right almost everywhere, badly wrong a few times | 4.4353 | 0.8417 |

RMSE prefers Model A. MAE prefers Model B. Reporting only one metric
silently picks a winner the other metric disagrees with.

## Learning objectives

By the end of this lab you will be able to:

1. Explain why a rising training R2 is not evidence a model has improved,
   and demonstrate it by adding pure-noise predictors.
2. Compute adjusted R2 and identify the point at which its own correction
   breaks down.
3. State the exact baseline R2 is measured against, and demonstrate that
   R2 has no lower bound.
4. Show that RMSE and MAE respond differently to a single outlier, and
   explain the mechanism (squaring versus not squaring the error).
5. Break MAPE at a zero true value and at a near-zero true value, and
   state what scikit-learn does instead of raising an exception.
6. Demonstrate MAPE's structural asymmetry between over- and
   under-prediction.
7. Construct two models where RMSE and MAE disagree about which is better,
   and explain why both rankings are correct about different things.
8. State the unit RMSE and MAE are reported in, for a real dataset.
9. Confirm that `sklearn.metrics.r2_score` agrees with
   `LinearRegression.score`.
10. Demonstrate that `r2_score`'s argument order changes its answer, and
    explain the mechanism.

## Prerequisites

- Day 149 for the loss/metric distinction and least squares; Day 143 for
  the machine-learning workflow this lab's split follows; Day 150 for
  multiple regression, which this lab's noise-column exercise extends.
- Comfort with NumPy arrays and reading a pytest failure, and `python3`
  3.11 or newer on your `PATH`.

## Supported operating systems

- macOS (Apple Silicon or Intel) -- the capture machine was macOS 26.5.2
  on arm64.
- Linux (any distribution with Python 3.11+ and bash).
- Windows via WSL2. The harness is a bash script and uses `mktemp -d`,
  `find` and process substitution; native PowerShell is not supported.

## Hardware requirements

Any machine that can run Python. **No GPU is needed or used** -- this lab
is fitting `LinearRegression` on at most 442 rows and 110 columns, which
completes in well under a second on the capture machine (macOS 26.5.2,
Apple Silicon, CPU only). Around 400 MB of disk for the virtual
environment, almost all of it scikit-learn and scipy.

## Required software

- Python 3.11 or newer (3.14.0 during capture).
- bash 3.2 or newer (3.2.57 during capture -- the macOS system bash).
- The three pinned packages in `requirements/requirements.txt`:
  `numpy==2.5.2`, `scikit-learn==1.9.0`, `pytest==9.1.1`.

`find`, `grep`, `awk`, `sed`, `diff` and `mktemp` are used by the harness
and ship with every supported system.

## Free and open-source options

Everything here is free and open source, and there is no paid tier
anywhere in this lab.

- **NumPy** and **scikit-learn** are BSD 3-Clause licensed.
- **pytest** is MIT licensed.
- No dataset is downloaded: `load_diabetes` ships bundled inside
  scikit-learn's own installed files, and every synthetic example is
  generated on the spot from a seeded generator.

## Installation

From the repository root:

```bash
cd labs/sections/machine-learning/day-152-regression-metrics
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy, sklearn; print(numpy.__version__, sklearn.__version__)"
```

That last line should print `2.5.2 1.9.0`. The install step is the only
part of this lab that needs the network, and it installs into a
**lab-local** environment -- never into your system Python. `rm -rf .venv`
reverses it completely.

## File structure

```
day-152-regression-metrics/
├── README.md                        this file
├── metadata.yml                     how the lab was actually executed
├── security.md                      what the lab touches, and what it does not
├── troubleshooting.md               every failure this lab is known to produce
├── requirements/
│   ├── README.md                    why the pins are exact
│   └── requirements.txt             numpy, scikit-learn, pytest
├── starter/
│   ├── 00_brief.md                  read this first
│   ├── regression_metrics_lib.py    complete machinery -- not the exercise
│   ├── test_metrics_lib.py          four machinery checks, already solved
│   └── test_metrics_claims.py       twelve exercises, each a skip to replace
├── examples/
│   ├── regression_metrics_lib.py    identical to the starter copy
│   ├── test_metrics_lib.py          the same four machinery checks
│   ├── test_metrics_claims.py       the reference solutions
│   └── report_measurements.py       prints every measured pair as one table
├── expected-output/
│   ├── FIELDS.md                    what is exact everywhere, and what is not
│   ├── measured-values.txt          the captured report, compared byte for byte
│   ├── examples-run.txt             captured `pytest examples -q`
│   ├── starter-run.txt              captured `pytest starter -q`
│   └── test-run.txt                 captured `bash tests/run_tests.sh`
└── tests/
    └── run_tests.sh                 the harness -- the definition of done
```

`starter/regression_metrics_lib.py` and `examples/regression_metrics_lib.py`
are byte identical on purpose. The library is machinery; the exercises are
the work.

## How to run

```bash
# the exercises, as you will find them
.venv/bin/pytest starter -q

# the reference solutions
.venv/bin/pytest examples -q

# every measured pair, as one table
.venv/bin/python3 examples/report_measurements.py

# the harness: the only definition of done
bash tests/run_tests.sh
echo "exit=$?"
```

Run `starter` and `examples` as **two separate invocations**. Both
directories define modules with the same names, and pytest aborts on the
collision with `import file mismatch`. Check 5 of the harness asserts that
it does, so the behaviour is documented rather than surprising.

Capture the exit status of `run_tests.sh` itself, as shown. Writing
`bash tests/run_tests.sh | tail -3` and then reading `$?` gives you
*tail's* exit status, which is essentially always zero -- the classic
always-passing test suite.

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 -m venv .venv` | Creates a lab-local environment so nothing installs into your system Python |
| `.venv/bin/pip install -r requirements/requirements.txt` | Installs the three pinned packages, plus scipy, joblib and threadpoolctl as scikit-learn's own dependencies |
| `.venv/bin/pytest starter -q` | Runs your work: four machinery checks pass, twelve exercises skip until you write them |
| `.venv/bin/pytest examples -q` | Runs the reference solutions -- sixteen assertions about what each regression metric reports |
| `.venv/bin/python3 examples/report_measurements.py` | Recomputes every published number and prints them as one table |
| `bash tests/run_tests.sh` | Fourteen checks: version pins, every claim reproduced without pytest, both suites, the collision, a byte-comparison of the report, a deliberate self-break, three directions re-confirmed at unquoted seeds, and cleanliness |

## Expected output

`bash tests/run_tests.sh` ends with:

```
---------------------------------------------------------------
14 checks, 0 failure(s)
```

and exits 0. `pytest examples -q` reports `16 passed`.
`pytest starter -q` reports `4 passed, 12 skipped` until you start work.

The complete captured runs are in `expected-output/`. The measurement
table is compared byte for byte by check 6, so if a number in the lesson
ever drifts from the code, the harness fails rather than the lesson
quietly becoming wrong.

Read `expected-output/FIELDS.md` before concluding that a mismatch on your
machine is a bug. It separates what is exact everywhere -- the direction of
every claim -- from what holds only under the pinned versions, which is
most of the decimals.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` → `14 checks, 0 failure(s)`
   and `exit=0`.
2. `.venv/bin/pytest examples -q` → `16 passed`.
3. `.venv/bin/pytest starter -q` → `4 passed, 12 skipped` before you
   start; `16 passed` when you have finished every exercise.
4. `.venv/bin/python3 examples/report_measurements.py | diff - expected-output/measured-values.txt`
   → no output.
5. Break one assertion in `examples/test_metrics_claims.py` on purpose,
   re-run the harness, and confirm it reports failures and exits non-zero.
   Restore it. A test suite you have never seen fail is not evidence.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints one `ok:` or
`FAIL:` line per check, ends with `N checks, M failure(s)`, and exits
non-zero when `M` is not zero.

The fourteen checks are:

1-3. The installed numpy, scikit-learn and pytest match the pins exactly.
4. Every published claim reproduced directly against
   `regression_metrics_lib`, with no pytest involved -- so a broken test
   file cannot hide a broken library, and vice versa.
5. `pytest examples -q` reports 16 passed.
6. `pytest starter -q` reports 4 passed, 12 skipped.
7. The combined `pytest examples starter` invocation aborts, as
   documented.
8. `report_measurements.py` output is byte-identical to the captured
   table.
9-10. A scratch copy of `examples/` passes, then fails with a non-zero
   exit and the failing test named after one assertion is deliberately
   rewritten.
11. The noise-column climb and the RMSE/MAE ranking inversion are
    re-confirmed at seeds the lesson never quotes, so no directional claim
    rests on a single lucky seed.
12-14. No URL appears in any source file; no `__pycache__` and no
   `.pytest_cache` are left behind.

Caches are cleared at the **start** of the run as well as the end, so
check 13 measures what that run left rather than what a previous manual
pytest invocation left.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: reset your work
```

The harness already removes its own scratch directory. Nothing else is
created outside this directory, so those four commands return your machine
to exactly the state it was in.

## Troubleshooting

See `troubleshooting.md`, which covers the missing virtual environment,
the `import file mismatch` collision, an astronomically large MAPE number,
adjusted R2 climbing back above the baseline at a large predictor count,
identical metrics on raw and scaled features, and the r2_score
argument-order bug.

## Security notes

See `security.md`. In short: no network after the install, no credentials,
no `sudo`, no write outside this directory except a `mktemp -d` scratch
directory the harness removes in the same run, and everything reversible
with `rm -rf .venv`. It also reads `r2_score`'s argument-order bug as an
instance of a broader class of function-contract mistakes worth defending
against with keyword arguments and a second, independent check.

## Extension exercises

1. **Find the break-even predictor count.** Exercise 1b shows adjusted R2
   correcting at 20 noise columns and failing at 100. Sweep intermediate
   values and find where the correction stops working, on this dataset.
2. **Repeat the noise-column climb on `make_regression`.** Construct a
   dataset where you control the true number of informative features, and
   confirm the same climb happens even when you know for certain the
   added columns are noise.
3. **A third model for the ranking-inversion exercise.** Construct a
   model that is worse than both A and B on both RMSE and MAE, and confirm
   there is no metric under which it wins. Then construct a fourth model
   that ties Model A on RMSE while beating it on MAE.
4. **Symmetric MAPE.** Look up `symmetric mean absolute percentage error`
   and implement it against the near-zero-target case in exercise 4b.
   Report whether it still explodes, and by how much less.
5. **A confidence interval for RMSE.** Use bootstrap resampling (Days
   117-118) to put an interval around the RMSE in exercise 3, before and
   after the outlier shift, and report how much the interval widens.
6. **Cross-validated R2.** Exercise 1's noise-column climb uses the
   training set. Repeat it with 5-fold cross-validated R2 instead, and
   report whether the climb still happens.

## Navigation

- Lab brief: `starter/00_brief.md`
- Previous lab: `../day-151-regularization-ridge-and-lasso/`
- Next lab: `../day-153-linear-regression-from-scratch/`
- Week 22 project: `../projects/week-22/`
