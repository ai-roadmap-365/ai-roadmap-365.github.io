# Day 148 lab — One Line, Measured

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Linear Regression
- **Day number:** 148 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-148-linear-regression
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-148-linear-regression` when the site is running.
<!-- generated-links:end -->

## Purpose

Everybody has seen a line fitted through a scatterplot. Rather fewer
people can read the slope off in real units, attach a standard error to
it, or catch from a residual plot when the line is quietly wrong.

This lab fits exactly one line — BMI against one-year diabetes-progression
score, in raw units — and then measures four specific ways a line can
mislead you even while its R-squared looks fine.

| quantity | measured |
| --- | --- |
| slope | 10.2331 |
| intercept | −117.7734 |
| R-squared | 0.3439 |
| slope standard error | 0.6738 |
| 95% confidence interval | [8.9125, 11.5538] |

In one sentence a clinician could read: each additional unit of BMI is
associated with about ten more points of one-year disease progression —
and that slope sits about fifteen standard errors from zero.

Two facts about that line hold exactly, on any dataset, forever: it passes
through the point `(mean(x), mean(y))`, and its residuals sum to zero.

Then four ways a fit can look fine and be wrong:

| The check | What it revealed, here |
| --- | --- |
| residuals binned by x, on curved data | R-squared 0.852 looked fine; residuals traced the missed curve exactly |
| residual spread, low half of x against high | R-squared 0.5723 looked fine; residual sd more than doubled, ratio **2.5446** |
| the fit with and without one added point | slope dropped from 1.5196 to 0.2138 — **one row out of forty-one** |
| RMSE with and without a fitted intercept | **59 percent worse** when the intercept was forced to zero |

## Learning objectives

By the end of this lab you will be able to:

1. Fit a simple linear regression in real units and read the slope as a
   real-world statement, with a standard error attached.
2. State and check the two facts that hold exactly for any least-squares
   line with an intercept.
3. Recover a known slope from generated data and observe the recovery
   error shrink as the sample size grows.
4. Diagnose non-linearity from a residual plot, on data whose R-squared
   alone gives no warning.
5. Diagnose heteroscedasticity from a residual plot, on data whose
   R-squared alone gives no warning.
6. Identify a high-leverage point and compute its leverage directly from
   its x-value, before considering its y-value.
7. State the cost of forcing `fit_intercept=False` on data whose true
   intercept is not near zero.
8. Distinguish real curvature in the residuals from ordinary noise, using
   a quadratic-fit diagnostic on the residuals themselves.

## Prerequisites

- Days 141-147 (Week 21) for what a model score means, splits, the
  bias-variance decomposition, and the scikit-learn estimator API. This
  lab assumes all of it and does not re-explain any of it.
- Comfort with NumPy arrays and reading a pytest failure, and `python3`
  3.11 or newer on your `PATH`.

## Supported operating systems

- macOS (Apple Silicon or Intel) — the capture machine was macOS 26.5.2
  on arm64.
- Linux (any distribution with Python 3.11+ and bash).
- Windows via WSL2. The harness is a bash script and uses `mktemp -d`,
  `find` and process substitution; native PowerShell is not supported.

## Hardware requirements

Any machine that can run Python. **No GPU is needed or used** — everything
here is a one-predictor least-squares fit on at most a few thousand rows.
The heaviest step is exercise 2's slope-recovery table, 1,000 total fits,
which completes in well under a second on the capture machine. Around
400 MB of disk for the virtual environment, almost all of it scikit-learn
and scipy.

## Required software

- Python 3.11 or newer (3.14.0 during capture).
- bash 3.2 or newer (3.2.57 during capture — the macOS system bash).
- The three pinned packages in `requirements/requirements.txt`:
  `numpy==2.5.2`, `scikit-learn==1.9.0`, `pytest==9.1.1`.

`find`, `grep`, `awk`, `sed`, `diff` and `mktemp` are used by the harness
and ship with every supported system.

## Free and open-source options

Everything here is free and open source, and there is no paid tier
anywhere in this lab.

- **NumPy** and **scikit-learn** are BSD 3-Clause licensed.
- **pytest** is MIT licensed.
- The diabetes dataset ships inside scikit-learn's own package data under
  a licence permitting this use; every other dataset here is generated on
  the spot from a seeded generator.

`LinearRegression` is the only model used in this lab and is part of
scikit-learn.

## Installation

From the repository root:

```bash
cd labs/sections/machine-learning/day-148-linear-regression
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy, sklearn; print(numpy.__version__, sklearn.__version__)"
```

That last line should print `2.5.2 1.9.0`. The install step is the only
part of this lab that needs the network, and it installs into a
**lab-local** environment — never into your system Python. `rm -rf .venv`
reverses it completely.

## File structure

```
day-148-linear-regression/
├── README.md                      this file
├── metadata.yml                   how the lab was actually executed
├── security.md                    what the lab touches, and what it does not
├── troubleshooting.md             every failure this lab is known to produce
├── requirements/
│   ├── README.md                  why the pins are exact
│   └── requirements.txt           numpy, scikit-learn, pytest
├── starter/
│   ├── 00_brief.md                read this first
│   ├── regression_lib.py          complete machinery -- not the exercise
│   ├── test_regression_lib.py     four machinery checks, already solved
│   └── test_regression_claims.py  twelve exercises, each a skip to replace
├── examples/
│   ├── regression_lib.py          identical to the starter copy
│   ├── test_regression_lib.py     the same four machinery checks
│   ├── test_regression_claims.py  the reference solutions
│   └── report_measurements.py     prints every measured pair as one table
├── expected-output/
│   ├── FIELDS.md                  what is exact everywhere, and what is not
│   ├── measured-values.txt        the captured report, compared byte for byte
│   ├── examples-run.txt           captured `pytest examples -q`
│   ├── starter-run.txt            captured `pytest starter -q`
│   └── test-run.txt               captured `bash tests/run_tests.sh`
└── tests/
    └── run_tests.sh               the harness -- the definition of done
```

`starter/regression_lib.py` and `examples/regression_lib.py` are byte
identical on purpose. The library is machinery; the exercises are the
work.

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
*tail's* exit status, which is essentially always zero — the classic
always-passing test suite.

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 -m venv .venv` | Creates a lab-local environment so nothing installs into your system Python |
| `.venv/bin/pip install -r requirements/requirements.txt` | Installs the three pinned packages, plus scipy, joblib and threadpoolctl as scikit-learn's own dependencies |
| `.venv/bin/pytest starter -q` | Runs your work: four machinery checks pass, twelve exercises skip until you write them |
| `.venv/bin/pytest examples -q` | Runs the reference solutions — sixteen assertions about what a fitted line does and does not tell you |
| `.venv/bin/python3 examples/report_measurements.py` | Recomputes every published number and prints them as one table |
| `bash tests/run_tests.sh` | Fourteen checks: version pins, every claim reproduced without pytest, both suites, the collision, a byte-comparison of the report, a deliberate self-break, four directions re-confirmed at unquoted seeds, and cleanliness |

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
machine is a bug. It separates what is exact everywhere — the BMI model,
which is fitted to a fixed bundled array with no randomness involved, and
every direction — from what holds only under the pinned versions, which is
mostly the slope-recovery table's sampled averages.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` → `14 checks, 0 failure(s)`
   and `exit=0`.
2. `.venv/bin/pytest examples -q` → `16 passed`.
3. `.venv/bin/pytest starter -q` → `4 passed, 12 skipped` before you
   start; `16 passed` when you have finished every exercise.
4. `.venv/bin/python3 examples/report_measurements.py | diff - expected-output/measured-values.txt`
   → no output.
5. Break one assertion in `examples/test_regression_claims.py` on purpose,
   re-run the harness, and confirm it reports failures and exits non-zero.
   Restore it. A test suite you have never seen fail is not evidence.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints one `ok:` or
`FAIL:` line per check, ends with `N checks, M failure(s)`, and exits
non-zero when `M` is not zero.

The fourteen checks are:

1-3. The installed numpy, scikit-learn and pytest match the pins exactly.
4. Every published claim reproduced directly against `regression_lib`,
   with no pytest involved — so a broken test file cannot hide a broken
   library, and vice versa.
5. `pytest examples -q` reports 16 passed.
6. `pytest starter -q` reports 4 passed, 12 skipped.
7. The combined `pytest examples starter` invocation aborts, as
   documented.
8. `report_measurements.py` output is byte-identical to the captured
   table.
9-10. A scratch copy of `examples/` passes, then fails with a non-zero
   exit and the failing test named after one assertion is deliberately
   rewritten.
11. Slope recovery, curvature, heteroscedasticity and the leverage point's
    effect are re-confirmed at seeds and settings the lesson never
    quotes, so no directional claim rests on a single lucky seed.
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
the `import file mismatch` collision, a BMI model that does not match
because `scaled=False` was left off, slope-recovery numbers moving with
the NumPy pin, and why nothing here triggers a convergence warning.

## Security notes

See `security.md`. In short: no network after the install, no
credentials, no `sudo`, no write outside this directory except a
`mktemp -d` scratch directory the harness removes in the same run, and
everything reversible with `rm -rf .venv`. It also reads the
high-leverage-point exercise as a preview of a data-poisoning concern —
one unusual row that can dominate a fit far out of proportion to its
count.

## Extension exercises

1. **Multiple leverage points.** Add two or three high-leverage points
   instead of one, at different positions, and measure whether their
   effect on the slope adds up or partly cancels.
2. **A robust alternative.** Read scikit-learn's documentation for
   `HuberRegressor` or `RANSACRegressor`, fit one on the leverage-point
   dataset from exercise 5, and report whether it resists the outlier
   the way `LinearRegression` did not. No output for this is reproduced
   in the lesson; the lesson describes it and says so.
3. **Weaker and stronger curvature.** Repeat exercise 3 with the quadratic
   coefficient scaled down toward zero. Find, by trial, roughly how small
   it can get before the binned residual means stop showing a clear
   shape, and report what that implies about spotting mild non-linearity
   by eye.
4. **A second predictor, informally.** Add a second, unrelated random
   column to the BMI data and refit with both columns (this is Day 150's
   subject, so treat it as a preview). Report whether the BMI coefficient
   changes, and by how much.
5. **Confidence interval coverage.** Simulate 500 datasets like
   `make_known_line`, compute a 95% confidence interval for the slope on
   each, and report what fraction actually contain the true slope. Compare
   it to 0.95.
6. **A real-unit intercept.** For `fit_intercept=False` versus `True`,
   plot both fitted lines against the intercept dataset's scatter and
   explain visually, in your own words, what constraining the intercept
   to zero forces the line to do.

## Navigation

- Lab brief: `starter/00_brief.md`
- Previous lab: `../day-147-an-end-to-end-classification-exercise/`
- Week 21 — Machine Learning Fundamentals — is complete. This lab opens
  Week 22 (Regression) with the model itself; Day 149 covers why squared
  error is the thing to minimize.
