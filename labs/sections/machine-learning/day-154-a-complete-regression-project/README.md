# Day 154 lab — A Complete Regression Project

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** A Complete Regression Project
- **Day number:** 154 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-154-a-complete-regression-project
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-154-a-complete-regression-project` when the site is running.
<!-- generated-links:end -->

## Purpose

Days 148 through 153 each isolated one discipline in a lab built to show
it alone: the one-predictor model and its four assumptions, the loss
function as a choice, multicollinearity, ridge and lasso, the metrics
that can be gamed or inverted, and OLS built from scratch.

This lab is every one of those disciplines, spent on one real dataset, in
the order a working project actually uses them: frame, baseline, split,
pipeline, cross-validate, select, **one** test evaluation, residual
diagnostics, a fairness check, prediction intervals, an honest verdict
with an interval on the margin.

The dataset is `sklearn.datasets.load_diabetes(scaled=False)` — the only
regression dataset bundled inside scikit-learn that needs no download.
`fetch_california_housing` downloads by default and is forbidden by this
lab's offline rule. 442 rows, 10 real-valued measurements in raw units,
and a target with no physical unit — a composite disease-progression
score, not mg/dL.

| quantity | value |
| --- | --- |
| dataset | `load_diabetes(scaled=False)` |
| rows / features | 442 / 10 |
| target range / mean | [25.0, 346.0] / 152.1335 |
| split (seed 0, 25 percent test) | 331 train / 111 test |
| mean-predictor baseline RMSE / R2 | 70.4637 / -0.0001 |
| K candidate pipelines | 23 (11 ridge, 11 lasso, 1 OLS) |
| winner (5-fold CV RMSE) | `Lasso(alpha=1)`, 53.8958 |
| ONE test evaluation (RMSE / R2 / MAE) | 56.5566 / 0.3557 / 45.2846 |
| margin over baseline, 95 percent bootstrap interval | 13.9071, [5.5852, 22.3324] |
| leaky-vs-honest gap over 20 seeds | mean +0.5279, never negative |
| prediction-interval coverage (nominal 0.95) | 0.9459 |

## Learning objectives

By the end of this lab you will be able to:

1. Choose a regression dataset by what is actually available offline, not
   by habit, and explain plainly what a target with no physical unit
   means for reading an RMSE.
2. Establish a mean-predictor baseline before fitting any model.
3. Build a real train/test split and hold the test rows back until one
   evaluation, using the discipline Days 144 and 147 built.
4. Sweep a genuine set of candidate pipelines with scikit-learn's
   `Pipeline`, and count K rather than losing track of it.
5. Select a winner using cross-validation on training rows only, never on
   test rows, choosing RMSE as the metric before any model is fitted.
6. Enforce a one-evaluation budget on a test set mechanically.
7. Compute a bootstrap interval around a model's margin over baseline,
   and judge whether the improvement is distinguishable from noise at the
   test-set size actually available.
8. Read residual-vs-fitted, curvature and normal-probability diagnostics
   for what they reveal about a regression model, not only its RMSE.
9. Measure whether a model's errors are worse for high-value targets than
   low-value ones, and read the result honestly whichever way it comes
   out.
10. Reproduce, and recognise, the mistake of selecting a model by scoring
    every candidate directly against the test set.
11. Build a prediction interval from held-out residuals and measure its
    realised coverage against its nominal rate.

## Prerequisites

- Day 141 for what a score means, Day 144 for the three sets and the
  `GatedTestSet` pattern, Day 147 for the full classification protocol
  this lab mirrors, Day 148 for the one-predictor model and its four
  assumptions, Day 149 for the loss as a choice, Day 150 for
  multicollinearity, Day 151 for ridge and lasso, Day 152 for metrics
  that can be gamed or inverted, and Day 153 for OLS built from scratch.
  This lab uses every one of them and teaches none of them again.
- Comfort with NumPy arrays and reading a pytest failure, and `python3`
  3.11 or newer on your `PATH`.

## Supported operating systems

- macOS (Apple Silicon or Intel) — the capture machine was macOS 26.5.2
  on arm64.
- Linux (any distribution with Python 3.11+ and bash).
- Windows via WSL2. The harness is a bash script and uses `mktemp -d`,
  `find` and process substitution; native PowerShell is not supported.

## Hardware requirements

Any machine that can run Python. **No GPU is needed or used** — this
lab is small-array NumPy and scikit-learn on the CPU throughout, and the
authoring machine (Apple Silicon, no CUDA GPU) ran the entire harness in
under a minute. The heaviest step is the 20-seed leaky-gap comparison in
exercise 10b, which cross-validates all 23 candidates 20 times over and
took 2.9559 seconds on the capture machine. Around 400 MB of disk for the
virtual environment, almost all of it scikit-learn and scipy.

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
- The dataset, `sklearn.datasets.load_diabetes`, ships inside the
  scikit-learn package itself; nothing is downloaded and no dataset
  licence beyond scikit-learn's own applies to your use of this lab.

The estimators used here — `Ridge`, `Lasso`, `LinearRegression`,
`DummyRegressor` — and the selection machinery — `Pipeline`, `KFold`,
`cross_val_score`, `cross_val_predict`, `train_test_split` — are all part
of scikit-learn. The Q-Q normal-probability check is built from scratch
in `regression_lib.py` (a rational approximation to the inverse normal
CDF) so this lab needs no scipy dependency.

## Installation

From the repository root:

```bash
cd labs/sections/machine-learning/day-154-a-complete-regression-project
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
day-154-a-complete-regression-project/
├── README.md                      this file
├── metadata.yml                   how the lab was actually executed
├── security.md                    what the lab touches, and what it does not
├── troubleshooting.md             every failure this lab is known to produce
├── requirements/
│   ├── README.md                  why the pins are exact
│   └── requirements.txt           numpy, scikit-learn, pytest
├── starter/
│   ├── 00_brief.md                read this first
│   ├── regression_lib.py          complete machinery — not the exercise
│   ├── test_regression_lib.py     five machinery checks, already solved
│   └── test_regression_claims.py  fourteen exercises, each a skip to replace
├── examples/
│   ├── regression_lib.py          identical to the starter copy
│   ├── test_regression_lib.py     the same five machinery checks
│   ├── test_regression_claims.py  the reference solutions
│   └── report_measurements.py     prints every measured pair as one table
├── expected-output/
│   ├── FIELDS.md                  what is exact everywhere, and what is not
│   ├── measured-values.txt        the captured report, compared byte for byte
│   ├── examples-run.txt           captured `pytest examples -q`
│   ├── starter-run.txt            captured `pytest starter -q`
│   └── test-run.txt               captured `bash tests/run_tests.sh`
└── tests/
    └── run_tests.sh               the harness — the definition of done
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
collision with `import file mismatch`. Check 5 of the harness asserts
that it does, so the behaviour is documented rather than surprising.

Capture the exit status of `run_tests.sh` itself, as shown. Writing
`bash tests/run_tests.sh | tail -3` and then reading `$?` gives you
*tail's* exit status, which is essentially always zero — the classic
always-passing test suite.

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 -m venv .venv` | Creates a lab-local environment so nothing installs into your system Python |
| `.venv/bin/pip install -r requirements/requirements.txt` | Installs the three pinned packages, plus scipy, joblib and threadpoolctl as scikit-learn's own dependencies |
| `.venv/bin/pytest starter -q` | Runs your work: five machinery checks pass, fourteen exercises skip until you write them |
| `.venv/bin/pytest examples -q` | Runs the reference solutions — nineteen assertions about the whole project |
| `.venv/bin/python3 examples/report_measurements.py` | Recomputes every published number and prints them as one table |
| `bash tests/run_tests.sh` | Fifteen checks: version pins, every claim reproduced without pytest, both suites, the collision, a byte-comparison of the report, the one-evaluation guarantee, a deliberate self-break, an unquoted-seed re-check, and cleanliness |

## Expected output

`bash tests/run_tests.sh` ends with:

```
---------------------------------------------------------------
15 checks, 0 failure(s)
```

and exits 0. `pytest examples -q` reports `19 passed`.
`pytest starter -q` reports `5 passed, 14 skipped` until you start work.

The complete captured runs are in `expected-output/`. The measurement
table is compared byte for byte by check 6, so if a number in the lesson
ever drifts from the code, the harness fails rather than the lesson
quietly becoming wrong.

Read `expected-output/FIELDS.md` before concluding that a mismatch on
your machine is a bug. It separates what is exact everywhere — the
dataset's shape, the RMSE and R2 formulas, the leaky RMSE never being
worse than the honest one — from what holds only under the pinned
versions, which is most of the decimals.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` → `15 checks, 0 failure(s)`
   and `exit=0`.
2. `.venv/bin/pytest examples -q` → `19 passed`.
3. `.venv/bin/pytest starter -q` → `5 passed, 14 skipped` before you
   start; `19 passed` when you have finished every exercise.
4. `.venv/bin/python3 examples/report_measurements.py | diff - expected-output/measured-values.txt`
   → no output.
5. Break one assertion in `examples/test_regression_claims.py` on
   purpose, re-run the harness, and confirm it reports failures and exits
   non-zero. Restore it. A test suite you have never seen fail is not
   evidence.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints one `ok:` or
`FAIL:` line per check, ends with `N checks, M failure(s)`, and exits
non-zero when `M` is not zero.

The fifteen checks are:

1-3. The installed numpy, scikit-learn and pytest match the pins exactly.
4. Every published claim reproduced directly against `regression_lib`,
   with no pytest involved — so a broken test file cannot hide a broken
   library, and vice versa.
5. `pytest examples -q` reports 19 passed.
6. `pytest starter -q` reports 5 passed, 14 skipped.
7. The combined `pytest examples starter` invocation aborts, as
   documented.
8. `report_measurements.py` output is byte-identical to the captured
   table.
9. `GatedTestSet` permits exactly one evaluation, then refuses five
   further attempts in a row without ever advancing its counter.
10-11. A scratch copy of `examples/` passes, then fails with a non-zero
   exit and the failing test named after one assertion is deliberately
   rewritten.
12. The leaky-gap direction and the selection mechanics are re-confirmed
    at seeds this lab never quotes, so no directional claim rests on a
    single lucky seed.
13-15. No URL appears in any source file; no `__pycache__` and no
   `.pytest_cache` are left behind.

Caches are cleared at the **start** of the run as well as the end, so the
cleanliness checks measure what that run left rather than what a previous
manual pytest invocation left.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: reset your work
```

The harness already removes its own scratch directory. Nothing else is
created outside this directory, so those four commands return your
machine to exactly the state it was in.

## Troubleshooting

See `troubleshooting.md`, which covers the missing virtual environment,
the `import file mismatch` collision, a winning configuration that
differs from the lesson's, the bootstrap interval not matching a by-hand
run, residual diagnostics that look different at another seed, a leaky
RMSE that should never come out higher than the honest one, and
convergence warnings from `Lasso` or `Ridge`.

## Security notes

See `security.md`. In short: no network after the install, no
credentials, no `sudo`, no write outside this directory except a
`mktemp -d` scratch directory the harness removes in the same run, and
everything reversible with `rm -rf .venv`. It also reads `GatedTestSet`
as an access-control pattern, and shows explicitly that a budget enforced
only at one call site — as opposed to on the resource itself — can be
bypassed, which the leaky-selection exercise deliberately does.

## Extension exercises

1. **Nested cross-validation.** Implement an inner loop that selects
   among the 23 candidates and an outer loop that scores the winner, so
   the outer score is never contaminated by the selection. Measure
   whether the gap between cv_rmse and test RMSE shrinks further, and
   report the cost in fits.
2. **A fourth family.** Add `ElasticNet` to `candidate_configs`, re-run
   the sweep, and report whether the winner or its cross-validated RMSE
   changes at seed 0.
3. **Cost-weighted residual analysis.** Exercise 9 splits the test set
   at the median. Try a more granular split — quartiles instead of
   halves — and report whether the fairness signal strengthens or
   weakens toward the extremes.
4. **Scale the test set.** Repeat the leaky-gap comparison (exercise 10b)
   using a 60/40 train/test split instead of 75/25, so the test set has
   roughly 177 rows instead of 111. Report whether the mean gap changes.
5. **A per-row prediction interval.** Exercise 11 builds one constant
   half-width for every prediction. Build a version whose half-width
   varies with the fitted value (using, for instance, the local density
   of out-of-fold residuals near each prediction) and compare its
   coverage and average width to the constant-width version.
6. **Break the independence assumption on purpose.** Duplicate 10 percent
   of the rows into both the train and test splits before running the
   sweep, and measure how much the reported test RMSE improves
   (misleadingly). This is Day 144's group-leakage lesson, reconstructed
   on real data.

## Navigation

- Lab brief: `starter/00_brief.md`
- Previous lab: `../day-153-linear-regression-from-scratch/`
- Week 22 (Regression) ends here. Day 155 begins Week 23.
- Week 22 project: `../projects/week-22/`
