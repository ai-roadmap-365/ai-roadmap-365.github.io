# Day 153 lab — Linear Regression from Scratch

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Linear Regression from Scratch
- **Day number:** 153 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-153-linear-regression-from-scratch
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-153-linear-regression-from-scratch` when the site is running.
<!-- generated-links:end -->

## Purpose

`LinearRegression().fit()` returns coefficients in a fraction of a second.
This lab builds the same fit three ways -- the normal equations, an
`lstsq`-based solve, and gradient descent -- and measures exactly where
they agree with the library and where they do not, and why.

The centrepiece is a design matrix with a near-duplicate column: three
random predictors plus a fourth that is almost the first, true coefficients
`[1, 2, 3, 4]`:

| method | coefficients (intercept, c0, c1, c2, c3-duplicate) |
| --- | --- |
| normal equations | `[0.001, 196747.976, 1.997, 2.994, -196742.975]` |
| lstsq | `[0.001, 207112.776, 1.997, 2.994, -207107.775]` |
| sklearn `LinearRegression` | `[0.001, 2.501, 2.0, 2.997, 2.501]` |

Both textbook routes explode to plus and minus two hundred thousand.
sklearn's SVD-based minimum-norm solve stays sane and splits the shared
weight evenly. Nothing here is a bug in either from-scratch implementation
-- both solve the least-squares problem correctly. The difference is what
"correctly" costs when the columns are almost linearly dependent.

The rest of the lab traces exactly why, and measures four more contrasts:

| What's measured | Result |
| --- | --- |
| normal equations vs sklearn, well-conditioned data | max gap 1.2153e-10 |
| lstsq vs sklearn, same data | max gap 1.1990e-12 -- about 101x closer |
| `cond(X'X)` against `cond(X)^2` | 1.0000000000 -- exact to ten decimals |
| gradient descent to 9 decimals, standardized features | 7291 iterations |
| the same setup, raw unscaled features, 95% of stability threshold | still 0.4692 away after 200,000 iterations |
| closed form vs gradient descent, operation count | 54,813 vs 64,452,440 -- about 1176x fewer |
| `check_estimator` on the from-scratch estimator | 48 of 52 checks pass; 2 fail by name |

## Learning objectives

By the end of this lab you will be able to:

1. Implement ordinary least squares via the normal equations, an
   `lstsq`-based solve, and batch gradient descent, and state precisely
   where each agrees with a library implementation and where it does not.
2. Explain why `cond(X'X)` is exactly the square of `cond(X)`, and why that
   is the textbook reason the normal equations lose precision a direct
   solve does not.
3. Predict and measure a design matrix on which the normal equations and
   `lstsq` both fail badly while scikit-learn's own `LinearRegression`
   does not, and explain the mechanism (an SVD-based minimum-norm solve).
4. Apply Day 111's gradient-descent stability condition,
   `|1 - eta * a| < 1`, to a real Hessian's eigenvalues, and use it to
   predict the exact learning rate at which gradient descent stops
   converging and starts diverging.
5. Measure how badly scaled features slow gradient descent, in terms of
   the Hessian's condition number, and connect it to Day 111's material.
6. Count the operations a closed-form solve and an iterative method use,
   without timing anything, and explain when each is the right choice.
7. Build a scikit-learn-compatible estimator by inheriting `BaseEstimator`
   and `RegressorMixin`, citing Day 146's measured reason for doing so.
8. Run `sklearn.utils.estimator_checks.check_estimator` against a
   from-scratch estimator and report the real result, including failures,
   by name.
9. Compare two ways of handling `fit_intercept` -- centring versus
   appending a column of ones -- and confirm they agree.

## Prerequisites

- Day 111 for gradient descent, its update rule, and the condition number
  as the ratio of the Hessian's eigenvalues -- assumed here, not re-derived.
- Day 146 for the scikit-learn estimator API and the measured reason a
  from-scratch estimator needs `BaseEstimator` to survive `Pipeline` and
  `cross_val_score`.
- Days 148-152 for what a fitted coefficient means, the normal equations'
  origin, multicollinearity, regularization and regression metrics --
  assumed as background, not re-taught.
- Comfort with NumPy arrays and reading a pytest failure, and `python3`
  3.11 or newer on your `PATH`.

## Supported operating systems

- macOS (Apple Silicon or Intel) -- the capture machine was macOS 26.5.2 on
  arm64.
- Linux (any distribution with Python 3.11+ and bash).
- Windows via WSL2. The harness is a bash script and uses `mktemp -d`,
  `find` and process substitution; native PowerShell is not supported.

## Hardware requirements

Any machine that can run Python. **No GPU is needed or used** -- everything
here is small-array NumPy and scikit-learn linear algebra on the CPU. The
capture machine is Apple Silicon with no CUDA GPU; the heaviest step is
200,000 gradient-descent iterations on a 442-by-10 matrix, which completes
in a few seconds. Around 400 MB of disk for the virtual environment, almost
all of it scikit-learn and scipy.

## Required software

- Python 3.11 or newer (3.14.0 during capture).
- bash 3.2 or newer (3.2.57 during capture -- the macOS system bash).
- The three pinned packages in `requirements/requirements.txt`:
  `numpy==2.5.2`, `scikit-learn==1.9.0`, `pytest==9.1.1`.

`find`, `grep`, `awk`, `sed`, `diff` and `mktemp` are used by the harness
and ship with every supported system.

## Free and open-source options

Everything here is free and open source, and there is no paid tier anywhere
in this lab.

- **NumPy** and **scikit-learn** are BSD 3-Clause licensed.
- **pytest** is MIT licensed.
- No dataset is downloaded: `sklearn.datasets.load_diabetes` ships bundled
  inside the installed `scikit-learn` package, so no dataset licence
  applies beyond scikit-learn's own.

## Installation

From the repository root:

```bash
cd labs/sections/machine-learning/day-153-linear-regression-from-scratch
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
day-153-linear-regression-from-scratch/
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
│   ├── test_regression_lib.py     five machinery checks, already solved
│   └── test_regression_claims.py  ten exercises, each a skip to replace
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
    └── run_tests.sh               the harness -- the definition of done
```

`starter/regression_lib.py` and `examples/regression_lib.py` are byte
identical on purpose. The library is machinery; the exercises are the work.

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
| `.venv/bin/pytest starter -q` | Runs your work: five machinery checks pass, ten exercises skip until you write them |
| `.venv/bin/pytest examples -q` | Runs the reference solutions -- fifteen assertions about the three fitting methods |
| `.venv/bin/python3 examples/report_measurements.py` | Recomputes every published number and prints them as one table |
| `bash tests/run_tests.sh` | Fourteen checks: version pins, every claim reproduced without pytest, both suites, the collision, a byte-comparison of the report, a deliberate self-break, seeds the lesson does not quote, and cleanliness |

## Expected output

`bash tests/run_tests.sh` ends with:

```
---------------------------------------------------------------
14 checks, 0 failure(s)
```

and exits 0. `pytest examples -q` reports `15 passed`.
`pytest starter -q` reports `5 passed, 10 skipped` until you start work.

The complete captured runs are in `expected-output/`. The measurement table
is compared byte for byte by check 6, so if a number in the lesson ever
drifts from the code, the harness fails rather than the lesson quietly
becoming wrong.

Read `expected-output/FIELDS.md` before concluding that a mismatch on your
machine is a bug. It separates what is exact everywhere -- the squaring
relationship, the direction of every result -- from what holds only under
the pinned versions, which is most of the far-right decimal places.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` → `14 checks, 0 failure(s)`
   and `exit=0`.
2. `.venv/bin/pytest examples -q` → `15 passed`.
3. `.venv/bin/pytest starter -q` → `5 passed, 10 skipped` before you start;
   `15 passed` when you have finished every exercise.
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
4. Every published claim reproduced directly against `regression_lib`, with
   no pytest involved -- so a broken test file cannot hide a broken
   library, and vice versa.
5. `pytest examples -q` reports 15 passed.
6. `pytest starter -q` reports 5 passed, 10 skipped.
7. The combined `pytest examples starter` invocation aborts, as documented.
8. `report_measurements.py` output is byte-identical to the captured table.
9-10. A scratch copy of `examples/` passes, then fails with a non-zero exit
   and the failing test named after one assertion is deliberately
   rewritten.
11. The near-duplicate-column explosion, lstsq's advantage over the normal
    equations, and the `cond(X'X) = cond(X)^2` relationship are re-confirmed
    at seeds and constructions the lesson never quotes, so no directional
    claim rests on a single lucky seed.
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

See `troubleshooting.md`, which covers the missing virtual environment, the
`import file mismatch` collision, exploded coefficients whose exact digits
differ from the lesson's, the squaring relationship not landing on exactly
1.0 in the extreme-ill-conditioning exercise, gradient-descent iteration
counts that differ, `check_estimator` reporting different failures on a
different scikit-learn version, and a singular-matrix experiment that does
not raise the error you might expect.

## Security notes

See `security.md`. In short: no network after the install, no credentials,
no `sudo`, no write outside this directory except a `mktemp -d` scratch
directory the harness removes in the same run, and everything reversible
with `rm -rf .venv`. It also reads `check_estimator`'s two named failures
as an input-validation lesson, not only a compatibility gap.

## Extension exercises

1. **Nested collinearity.** Add a fifth column that is a near-duplicate of
   a *different* column, so two independent pairs are both nearly
   collinear at once. Measure whether the normal equations' explosion
   compounds or stays about the same size, and report which.
2. **Ridge as a numerical fix, not just a statistical one.** Day 151
   covered ridge regression as a bias-variance trade-off. Refit the
   near-duplicate-column dataset with a small ridge penalty using the
   normal equations directly (`(X'X + alpha*I)^-1 X'y`) and measure how
   small `alpha` needs to be before the coefficients stop exploding.
3. **A fourth fitting method: QR decomposition.** Implement OLS via
   `numpy.linalg.qr` and compare its accuracy against sklearn on both the
   well-conditioned diabetes data and the dramatic case. Report where it
   sits relative to the normal equations and lstsq.
4. **Momentum.** Add a momentum term to `fit_gradient_descent` and measure
   how many fewer iterations it needs to reach 9-decimal agreement on the
   standardized diabetes data, at the same learning rate.
5. **The break-even matrix size.** `normal_equation_op_count` grows as
   `n*p^2 + p^3`. Find the value of `p`, at a fixed `n`, where the `p^3`
   term first exceeds the `n*p^2` term, and explain what that implies for
   very wide datasets.
6. **A third check_estimator failure, fixed.** Pick one of the two named
   `check_estimator` failures and fix it -- add the missing input
   validation with `sklearn.utils.validation` helpers -- then re-run
   `run_check_estimator` and report the new pass count.
7. **Learning-rate schedules.** Implement a decaying learning rate (for
   example, `lr / (1 + decay * iteration)`) and measure whether it lets you
   start above the fixed-rate stability threshold without diverging.

## Navigation

- Lab brief: `starter/00_brief.md`
- Previous lab: `../day-152-regression-metrics/`
- Next lab: `../day-154-a-complete-regression-project/`
- Week 22 project: `../projects/week-22/`
