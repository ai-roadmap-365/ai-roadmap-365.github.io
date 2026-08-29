# Day 149 lab — Loss Functions and Least Squares

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Loss Functions and Least Squares
- **Day number:** 149 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-149-loss-functions-and-least-squares
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-149-loss-functions-and-least-squares` when the site is running.
<!-- generated-links:end -->

## Purpose

Everybody who has fit a line knows to minimise the error. Rather fewer
people have measured what "the error" actually means, or noticed that it
is a choice rather than a single obvious thing.

This lab measures the choice, using one outlier moved 80 units off an
otherwise ordinary straight line:

| estimator | loss it minimises | slope before | slope after | movement |
| --- | --- | --- | --- | --- |
| `LinearRegression` | squared error | 3.0465 | 3.8010 | **+0.7545** |
| `HuberRegressor` | Huber (blended) | 2.9870 | 3.0308 | +0.0437 |
| `QuantileRegressor(0.5)` | absolute error | 2.9961 | 3.0064 | +0.0104 |

One point, and least squares moves seventeen times further than Huber and
seventy-two times further than the median fit. That gap is not a quirk of
scikit-learn's solvers — it is squaring the residual: an 80-unit error
contributes 6,400 to a squared-error total and only 80 to an
absolute-error total.

Before that, the lab measures the two textbook facts underneath every
loss function: the mean minimises squared error and the median minimises
absolute error, confirmed by a numerical grid search rather than asserted;
and squared error's landscape is a smooth parabola while absolute error's
is piecewise-linear and kinked, which is exactly why squared error has a
closed-form solution — the normal equations — and absolute error does
not.

The last two exercises ask what squared error is silently betting on.
Fit both estimators 500 times each on freshly generated data, once with
Gaussian errors and once with heavy-tailed errors of similar spread:

| errors | OLS spread (sd) | Huber spread (sd) | which is tighter |
| --- | --- | --- | --- |
| Gaussian | 0.0560 | 0.0588 | OLS |
| heavy-tailed | 0.0589 | 0.0422 | Huber |

Gauss-Markov's promise that ordinary least squares is the **best linear
unbiased estimator** is conditional on the errors. Change what the errors
look like and the ranking measurably flips.

## Learning objectives

By the end of this lab you will be able to:

1. Demonstrate numerically that the mean minimises squared error and the
   median minimises absolute error, using a grid search rather than a
   citation.
2. Distinguish a smooth loss landscape from a kinked one by its second
   differences, and explain why that distinction is exactly why one loss
   has a closed-form solution and the other does not.
3. Solve the normal equations directly and confirm the result matches
   `LinearRegression` to many decimal places.
4. Measure how far a single outlier moves a squared-error fit compared
   with a Huber fit and a median (absolute-error) fit on identical data.
5. Sweep Huber's `epsilon` parameter and observe it interpolate smoothly
   between absolute-error-like and squared-error-like behaviour.
6. State the Gauss-Markov result precisely — best **linear**, **unbiased**
   estimator, under its assumptions — and explain why every one of those
   words is load-bearing.
7. Measure that OLS is the more precise (lower-variance) estimator under
   Gaussian errors and that Huber is more precise under heavy-tailed
   errors, on identical true parameters.
8. State the distinction between a loss (what you optimise) and a metric
   (what you report), and explain why they need not be the same function.
9. Verify that `HuberRegressor` and `QuantileRegressor` both exist and
   converge in a specific scikit-learn release, rather than assuming it.

## Prerequisites

- Day 148 for the linear model itself: geometry, coefficient
  interpretation, and residual plots. This lab assumes you can already
  fit a line and read a residual; it does not re-teach that.
- Days 141-147 for what a score means, splits, overfitting, and the
  scikit-learn estimator API in general.
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
here is small-array NumPy and scikit-learn on the CPU. The heaviest step
is 2,000 model fits behind the last two exercises, which completes in a
few seconds on the capture machine. Around 400 MB of disk for the virtual
environment, almost all of it scikit-learn and scipy.

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
- No dataset is downloaded or bundled: every dataset is a synthetic
  straight line generated on the spot from a seeded generator, so no
  dataset licence applies to your use of this lab.

The estimators used here — `LinearRegression`, `HuberRegressor`,
`QuantileRegressor` — are all part of scikit-learn. Ridge and lasso, which
add a penalty on top of a loss, are Day 151's subject and are not used
here.

## Installation

From the repository root:

```bash
cd labs/sections/machine-learning/day-149-loss-functions-and-least-squares
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
day-149-loss-functions-and-least-squares/
├── README.md                      this file
├── metadata.yml                   how the lab was actually executed
├── security.md                    what the lab touches, and what it does not
├── troubleshooting.md             every failure this lab is known to produce
├── requirements/
│   ├── README.md                  why the pins are exact
│   └── requirements.txt           numpy, scikit-learn, pytest
├── starter/
│   ├── 00_brief.md                read this first
│   ├── loss_lib.py                complete machinery — not the exercise
│   ├── test_loss_lib.py           four machinery checks, already solved
│   └── test_loss_claims.py        ten exercises, each a skip to replace
├── examples/
│   ├── loss_lib.py                identical to the starter copy
│   ├── test_loss_lib.py           the same four machinery checks
│   ├── test_loss_claims.py        the reference solutions
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

`starter/loss_lib.py` and `examples/loss_lib.py` are byte identical on
purpose. The library is machinery; the exercises are the work.

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
| `.venv/bin/pytest starter -q` | Runs your work: four machinery checks pass, ten exercises skip until you write them |
| `.venv/bin/pytest examples -q` | Runs the reference solutions — fourteen assertions about how losses behave |
| `.venv/bin/python3 examples/report_measurements.py` | Recomputes every published number and prints them as one table |
| `bash tests/run_tests.sh` | Fourteen checks: version pins, every claim reproduced without pytest, both suites, the collision, a byte-comparison of the report, a deliberate self-break, three directions re-confirmed beyond the quoted seeds, and cleanliness |

## Expected output

`bash tests/run_tests.sh` ends with:

```
---------------------------------------------------------------
14 checks, 0 failure(s)
```

and exits 0. `pytest examples -q` reports `14 passed`.
`pytest starter -q` reports `4 passed, 10 skipped` until you start work.

The complete captured runs are in `expected-output/`. The measurement
table is compared byte for byte by check 6, so if a number in the lesson
ever drifts from the code, the harness fails rather than the lesson
quietly becoming wrong.

Read `expected-output/FIELDS.md` before concluding that a mismatch on your
machine is a bug. It separates what is exact everywhere — the mean and
median as minimisers, the normal equations matching `LinearRegression`,
the direction of every comparison — from what holds only under the pinned
versions, which is most of the sampled decimals.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` → `14 checks, 0 failure(s)`
   and `exit=0`.
2. `.venv/bin/pytest examples -q` → `14 passed`.
3. `.venv/bin/pytest starter -q` → `4 passed, 10 skipped` before you
   start; `14 passed` when you have finished every exercise.
4. `.venv/bin/python3 examples/report_measurements.py | diff - expected-output/measured-values.txt`
   → no output.
5. Break one assertion in `examples/test_loss_claims.py` on purpose,
   re-run the harness, and confirm it reports failures and exits non-zero.
   Restore it. A test suite you have never seen fail is not evidence.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints one `ok:` or
`FAIL:` line per check, ends with `N checks, M failure(s)`, and exits
non-zero when `M` is not zero.

The fourteen checks are:

1-3. The installed numpy, scikit-learn and pytest match the pins exactly.
4. Every published claim reproduced directly against `loss_lib`, with no
   pytest involved — so a broken test file cannot hide a broken library,
   and vice versa.
5. `pytest examples -q` reports 14 passed.
6. `pytest starter -q` reports 4 passed, 10 skipped.
7. The combined `pytest examples starter` invocation aborts, as
   documented.
8. `report_measurements.py` output is byte-identical to the captured
   table.
9-10. A scratch copy of `examples/` passes, then fails with a non-zero
   exit after exercise 4's outlier-movement assertion is deliberately
   rewritten, naming the failing test.
11. Outlier sensitivity, the normal equations, and the Gauss-Markov
    efficiency ranking are re-confirmed at seeds and a replication count
    the lesson never quotes, so no directional claim rests on a single
    lucky seed.
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
the `import file mismatch` collision, sampled figures moving with the
package pins, `QuantileRegressor`'s solver argument, `HuberRegressor`
convergence, the grid search's finite resolution, and how long the
efficiency comparison takes.

## Security notes

See `security.md`. In short: no network after the install, no
credentials, no `sudo`, no write outside this directory except a
`mktemp -d` scratch directory the harness removes in the same run, and
everything reversible with `rm -rf .venv`. It also reads the
outlier-sensitivity result as a security idea: a loss function decides,
silently, how much weight one extreme input gets, and squared error gives
it the most.

## Extension exercises

1. **Ridge, ahead of schedule.** Fit `Ridge(alpha=1.0)` on the outlier-
   contaminated dataset from exercise 4 and measure how far its slope
   moves compared with plain `LinearRegression`. Ridge adds a penalty on
   top of squared error rather than changing the loss itself — Day 151
   owns this properly, but the comparison is worth seeing once here.
2. **A third heavy tail.** Repeat exercises 6 and 6b with a Laplace-
   distributed error instead of Student's t, and report whether the
   efficiency ranking still flips in Huber's favour.
3. **Where does the ranking cross?** Sweep the degrees of freedom of the
   Student's t error from 30 down to 1 and find, approximately, the value
   at which `sd(OLS) == sd(Huber)`. Report what that implies about how
   heavy the tails need to be before Huber earns its keep.
4. **A second outlier.** Add a second point 80 units off the line at a
   different x position and re-measure the outlier-shift table. Does OLS's
   movement roughly double, or is it worse than that?
5. **`epsilon` versus outlier size.** Fix `epsilon=1.35` and sweep the
   outlier's offset from 5 to 200. At what offset does Huber's slope start
   moving noticeably, and how does that connect to the residual scale in
   this dataset?
6. **The quantile beyond the median.** Fit `QuantileRegressor` at
   `quantile=0.1` and `quantile=0.9` on the outlier-contaminated data and
   compare the two fitted lines. What does each one describe about the
   conditional distribution of y that a single squared-error fit cannot?
7. **Time the normal equations against gradient descent.** Day 153 owns
   gradient descent properly, but as a preview: write a five-line gradient
   descent loop for squared error on the 300-row dataset from exercise 3,
   and report how many iterations it takes to match the normal equations'
   answer to four decimal places.

## Navigation

- Lab brief: `starter/00_brief.md`
- Previous lab: `../day-148-linear-regression/`
- Next lab: `../day-150-multiple-and-polynomial-regression/`
- Week 22 project: `../projects/week-22/`
