# Day 150 lab — Many Predictors, One Model

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Multiple and Polynomial Regression
- **Day number:** 150 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-150-multiple-and-polynomial-regression
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-150-multiple-and-polynomial-regression` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 148 gave you a line through one predictor. Day 149 gave you a reason
to square the error before minimising it. Neither told you what changes
once a second predictor joins the first — and the honest answer is: more
than you would guess.

This lab measures it on `sklearn.datasets.load_diabetes(scaled=False)`:
442 patients, ten predictors in their real clinical units, one target.

The centrepiece: `s1` and `s2`, two of the six serum measurements,
correlate at 0.8967. Append an exact copy of `s1` to the design matrix and
refit:

| | original | duplicate model |
| --- | --- | --- |
| `s1` coefficient | −1.0900 | −0.5450 |
| copy's coefficient | — | −0.5450 |
| **sum** | −1.0900 | **−1.0900** |
| R2 | 0.5177 | 0.5177 |
| max prediction change | — | 3.98 × 10⁻¹² |

Neither half matches the original coefficient. Their **sum** does, to
eight decimal places. Break the exact tie with one percent of noise and
refit at ten seeds: both individual coefficients swing with a standard
deviation above 4.4 and cross zero, while their sum's standard deviation
is 0.0144 and the largest single prediction move across all ten seeds is
6.5911, on a target whose own standard deviation is 77.

**Wild coefficients, stable predictions.** A model can be excellent at
what it predicts and worthless as a description of "the effect of `s1`"
at the same time, and its accuracy will never tell you so.

## Learning objectives

By the end of this lab you will be able to:

1. Compute variance inflation factors directly, from the definition, and
   read what they say about ten real predictors.
2. Demonstrate that duplicating a predictor splits its coefficient in a
   way that is arbitrary in isolation but conserved in sum.
3. Show that breaking an exact duplicate with a small amount of noise
   turns a stable split into a wildly unstable one, while predictions
   barely move.
4. Connect a predictor's variance inflation factor to how much its
   coefficient wobbles under bootstrap resampling.
5. Identify a sign flip between a predictor's simple and multiple
   regression coefficients, and explain what "holding the others
   constant" changed.
6. Prove, by direct computation, that a polynomial fit is linear in its
   parameters rather than in the input.
7. Measure what an interaction term buys in R2, separately from the
   quadratic terms.
8. Demonstrate that R2 never decreases when a predictor is added, even a
   column of pure noise.
9. Demonstrate that standardising a design matrix changes every
   coefficient's size without changing a single prediction.

## Prerequisites

- Day 148 for the geometry of a single-predictor line and coefficient
  interpretation, and Day 149 for why squared error is the loss being
  minimised here.
- Comfort with NumPy arrays and reading a pytest failure, and `python3`
  3.11 or newer on your `PATH`.

## Supported operating systems

- macOS (Apple Silicon or Intel) — the capture machine was macOS 26.5.2
  on arm64.
- Linux (any distribution with Python 3.11+ and bash).
- Windows via WSL2. The harness is a bash script and uses `mktemp -d`,
  `find` and process substitution; native PowerShell is not supported.

## Hardware requirements

Any machine that can run Python. **No GPU is needed or used** — every fit
here is `LinearRegression` on 442 rows and at most eleven columns, which
solves in milliseconds on the CPU. The heaviest step is 500 bootstrap
refits, which completes in well under a second on the capture machine.
Around 400 MB of disk for the virtual environment, almost all of it
scikit-learn and scipy.

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
- No dataset is downloaded: `sklearn.datasets.load_diabetes` ships bundled
  inside the scikit-learn package as a compressed CSV, so no dataset
  licence applies beyond scikit-learn's own.

`LinearRegression`, `PolynomialFeatures` and `StandardScaler` are all part
of scikit-learn. Statsmodels offers an alternative regression API with
built-in variance-inflation-factor and standard-error tooling; it is not
installed here, and this lab computes VIF directly from its definition
instead so nothing beyond the three pinned packages is required.

## Installation

From the repository root:

```bash
cd labs/sections/machine-learning/day-150-multiple-and-polynomial-regression
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
day-150-multiple-and-polynomial-regression/
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
│   └── test_regression_claims.py  twelve exercises, each a skip to replace
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
| `.venv/bin/pytest starter -q` | Runs your work: five machinery checks pass, twelve exercises skip until you write them |
| `.venv/bin/pytest examples -q` | Runs the reference solutions — seventeen assertions about what changes with more than one predictor |
| `.venv/bin/python3 examples/report_measurements.py` | Recomputes every published number and prints them as one table |
| `bash tests/run_tests.sh` | Fourteen checks: version pins, every claim reproduced without pytest, both suites, the collision, a byte-comparison of the report, a deliberate self-break, key results re-confirmed at seeds and predictors the lesson does not quote, and cleanliness |

## Expected output

`bash tests/run_tests.sh` ends with:

```
---------------------------------------------------------------
14 checks, 0 failure(s)
```

and exits 0. `pytest examples -q` reports `17 passed`.
`pytest starter -q` reports `5 passed, 12 skipped` until you start work.

The complete captured runs are in `expected-output/`. The measurement
table is compared byte for byte by check 6, so if a number in the lesson
ever drifts from the code, the harness fails rather than the lesson
quietly becoming wrong.

Read `expected-output/FIELDS.md` before concluding that a mismatch on your
machine is a bug. It separates what is exact everywhere — every formula,
the exact-duplicate result, the polynomial-equals-normal-equations result,
R2 never decreasing, scaling leaving predictions unchanged — from what
holds only under the pinned versions, which is the noisy-duplicate and
bootstrap decimals.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` → `14 checks, 0 failure(s)`
   and `exit=0`.
2. `.venv/bin/pytest examples -q` → `17 passed`.
3. `.venv/bin/pytest starter -q` → `5 passed, 12 skipped` before you
   start; `17 passed` when you have finished every exercise.
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

The fourteen checks are:

1-3. The installed numpy, scikit-learn and pytest match the pins exactly.
4. Every published claim reproduced directly against `regression_lib`,
   with no pytest involved — so a broken test file cannot hide a broken
   library, and vice versa.
5. `pytest examples -q` reports 17 passed.
6. `pytest starter -q` reports 5 passed, 12 skipped.
7. The combined `pytest examples starter` invocation aborts, as
   documented.
8. `report_measurements.py` output is byte-identical to the captured
   table.
9-10. A scratch copy of `examples/` passes, then fails with a non-zero
   exit and the failing test named after one assertion is deliberately
   rewritten.
11. The duplicate-column instability, R2 monotonicity, and VIF-linked
    bootstrap instability are re-confirmed at seeds, predictors and
    replication counts the lesson never quotes, so no directional claim
    rests on a single lucky draw.
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
the `import file mismatch` collision, mismatched duplicate-column
coefficients, the missing-pandas error if you pass `as_frame=True`,
slow bootstrap or noise-column exercises, an `inf` variance inflation
factor, and why no estimator here should warn about convergence.

## Security notes

See `security.md`. In short: no network after the install, no
credentials, no `sudo`, no write outside this directory except a
`mktemp -d` scratch directory the harness removes in the same run, and
everything reversible with `rm -rf .venv`. It also reads the
duplicate-column result as a warning about trusting a coefficient in
production: a model can be accurate and its coefficients meaningless at
the same time, and no accuracy metric will tell you so.

## Extension exercises

1. **Ridge, applied by hand.** Day 151 owns ridge regression properly, but
   you can preview it here: add a small `alpha * I` to the normal
   equations' `X^T X` term before solving, refit the noisy-duplicate case
   from exercise 3, and measure whether the two coefficients stop
   swinging.
2. **VIF against statsmodels.** If you install `statsmodels` in a
   throwaway environment, compare its
   `variance_inflation_factor` against this lab's direct computation on
   the same ten columns, and confirm they agree.
3. **A three-way duplicate.** Append two additional copies of `s1`
   (three total near-identical columns) instead of one, and measure how
   much more unstable the three-way coefficient split becomes compared
   with the two-way split in exercise 3b.
4. **Adjusted R2, by hand.** Day 152 owns the fix for exercise 7's
   never-decreasing R2. Implement the adjusted-R2 formula yourself and
   confirm it can decrease when a noise column is added, even though
   ordinary R2 cannot.
5. **A sign flip you construct.** Build a small synthetic dataset with
   `sklearn.datasets.make_regression` and a confounding correlated
   feature, tuned so that a coefficient's sign flips between the simple
   and multiple regression — deliberately, rather than found in real
   data as exercise 5 does.
6. **Interaction terms beyond degree 2.** Extend `interaction_term_effect`
   to three predictors (`bmi`, `bp`, `s5`) and measure how much of the R2
   gain from `degree=2` comes from the three pairwise interaction terms
   versus the three quadratic terms.

## Navigation

- Lab brief: `starter/00_brief.md`
- Previous lab: `../day-149-loss-functions-and-least-squares/`
- Next lab: `../day-151-ridge-and-lasso-regression/`
- Week 22 project: `../projects/week-22/`
