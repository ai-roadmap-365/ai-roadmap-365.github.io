# Day 151 lab — What the Penalty Does

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Regularization: Ridge and Lasso
- **Day number:** 151 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-151-regularization-ridge-and-lasso
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-151-regularization-ridge-and-lasso` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 145 already measured that a ridge penalty rescued an overfit
degree-24 polynomial by a factor of 39,588. That day treated
"regularization" as one thing. It is not.

This lab measures the CONTRAST between the two most common penalties —
L2 (ridge) and L1 (lasso) — on the same dataset, with the same alphas, so
the difference is not a claim you take on faith:

| alpha | lasso zeros | lasso R2 | ridge zeros | ridge R2 |
| --- | --- | --- | --- | --- |
| 0.001 | 0/10 | 0.3588 | 0/10 | 0.3586 |
| 0.01 | 1/10 | 0.3541 | 0/10 | 0.3567 |
| 0.1 | 3/10 | 0.3550 | 0/10 | 0.3690 |
| 1.0 | 8/10 | 0.2782 | 0/10 | 0.3570 |

**Ridge zeros nothing, at any alpha tried. Lasso zeros progressively
more.** `sklearn.datasets.load_diabetes`, `train_test_split(test_size=0.25,
random_state=0)`. That contrast, measured on real data, is the spine of
this lab.

Eight groups of exercises measure why, and what it costs:

1. The headline table above.
2. The coefficient path — the exact alpha at which each lasso coefficient
   hits zero, and confirmation that no ridge coefficient ever does, across
   a 60-point sweep.
3. Whether lasso recovers the RIGHT features against a known sparse
   ground truth, and how that recovery degrades with noise.
4. Scale-dependence: the same alpha, on the same data, in three different
   units, selects 10, 7 and 3 features respectively.
5. ElasticNet, and the alpha-scale mismatch between it and plain Ridge.
6. Correlated predictors — ridge splits the weight, lasso picks one.
7. Ridge's closed form against lasso's iterative solve.
8. The corner: a two-feature case small enough to see the geometry.

## Learning objectives

By the end of this lab you will be able to:

1. State, from a measurement rather than a rule of thumb, that ridge
   never zeros a coefficient while lasso zeros progressively more as
   alpha grows.
2. Explain the L1-versus-L2 difference in terms of constraint-region
   geometry — a diamond has corners on the axes, a circle does not — and
   point to the exact alpha where a lasso coefficient reaches zero.
3. Distinguish lasso as simultaneous shrinkage and feature selection from
   ridge as shrinkage alone.
4. Measure whether lasso recovers a KNOWN set of informative features,
   and report honestly when it does not.
5. Demonstrate that regularization requires scaled features, with three
   different feature-selection outcomes from the same alpha in three
   different units.
6. Use ElasticNet as the combination of both penalties and know when it
   is preferable to either alone.
7. State that Ridge and ElasticNet do NOT share an alpha scale, and
   correct for the difference.
8. Predict what ridge and lasso each do to a pair of near-duplicate
   (highly correlated) predictors, connecting back to Day 150.
9. State that ridge has a closed-form solution while lasso requires an
   iterative solve, and say why the L1 penalty forces that.

## Prerequisites

- Day 145's measurement that a penalty trades variance for bias — this
  lab does not re-measure that trade, it measures the shape of the
  penalty itself.
- Day 148 (the one-predictor linear model), Day 149 (loss functions and
  the normal equations) and Day 150 (many predictors, the design matrix
  and multicollinearity) — this lab uses all three without re-teaching
  them.
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
machine is Apple Silicon with no CUDA GPU, and everything here is
small-array NumPy and scikit-learn on the CPU. The heaviest step is a
60-point alpha sweep refitting ten small linear models; the whole harness
completes in well under a minute on the capture machine. Around 400 MB
of disk for the virtual environment, almost all of it scikit-learn and
scipy.

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
- `load_diabetes` ships bundled inside the scikit-learn package and is
  read from local disk; no dataset is downloaded, and no dataset licence
  beyond scikit-learn's own applies.

`Ridge`, `Lasso`, `LassoCV` and `ElasticNet` are all part of
scikit-learn, along with the `make_regression` synthetic-data generator
used for the known-sparse-ground-truth exercise.

## Installation

From the repository root:

```bash
cd labs/sections/machine-learning/day-151-regularization-ridge-and-lasso
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
day-151-regularization-ridge-and-lasso/
├── README.md                          this file
├── metadata.yml                       how the lab was actually executed
├── security.md                        what the lab touches, and what it does not
├── troubleshooting.md                 every failure this lab is known to produce
├── requirements/
│   ├── README.md                      why the pins are exact
│   └── requirements.txt               numpy, scikit-learn, pytest
├── starter/
│   ├── 00_brief.md                    read this first
│   ├── regularization_lib.py          complete machinery — not the exercise
│   ├── test_regularization_lib.py     four machinery checks, already solved
│   └── test_regularization_claims.py  fourteen exercises, each a skip to replace
├── examples/
│   ├── regularization_lib.py          identical to the starter copy
│   ├── test_regularization_lib.py     the same four machinery checks
│   ├── test_regularization_claims.py  the reference solutions
│   └── report_measurements.py         prints every measured pair as one table
├── expected-output/
│   ├── FIELDS.md                      what is exact everywhere, and what is not
│   ├── measured-values.txt            the captured report, compared byte for byte
│   ├── examples-run.txt               captured `pytest examples -q`
│   ├── starter-run.txt                captured `pytest starter -q`
│   └── test-run.txt                   captured `bash tests/run_tests.sh`
└── tests/
    └── run_tests.sh                   the harness — the definition of done
```

`starter/regularization_lib.py` and `examples/regularization_lib.py` are
byte identical on purpose. The library is machinery; the exercises are
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
collision with `import file mismatch`. Check 5 of the harness asserts
that it does, so the behaviour is documented rather than surprising.

Capture the exit status of `run_tests.sh` itself, as shown. Writing
`bash tests/run_tests.sh | tail -3` and then reading `$?` gives you
*tail's* exit status, which is essentially always zero.

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 -m venv .venv` | Creates a lab-local environment so nothing installs into your system Python |
| `.venv/bin/pip install -r requirements/requirements.txt` | Installs the three pinned packages, plus scipy, joblib and threadpoolctl as scikit-learn's own dependencies |
| `.venv/bin/pytest starter -q` | Runs your work: four machinery checks pass, fourteen exercises skip until you write them |
| `.venv/bin/pytest examples -q` | Runs the reference solutions — eighteen assertions about what a penalty does |
| `.venv/bin/python3 examples/report_measurements.py` | Recomputes every published number and prints them as one table |
| `bash tests/run_tests.sh` | Fourteen checks: version pins, every claim reproduced without pytest, both suites, the collision, a byte-comparison of the report, a deliberate self-break, directions re-confirmed at unquoted alphas and seeds, and cleanliness |

## Expected output

`bash tests/run_tests.sh` ends with:

```
---------------------------------------------------------------
14 checks, 0 failure(s)
```

and exits 0. `pytest examples -q` reports `18 passed`.
`pytest starter -q` reports `4 passed, 14 skipped` until you start work.

The complete captured runs are in `expected-output/`. The measurement
table is compared byte for byte by check 6, so if a number in the lesson
ever drifts from the code, the harness fails rather than the lesson
quietly becoming wrong.

Read `expected-output/FIELDS.md` before concluding that a mismatch on
your machine is a bug. It separates what is exact everywhere — ridge
never zeroing, the directions of every comparison — from what holds only
under the pinned versions.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` → `14 checks, 0 failure(s)`
   and `exit=0`.
2. `.venv/bin/pytest examples -q` → `18 passed`.
3. `.venv/bin/pytest starter -q` → `4 passed, 14 skipped` before you
   start; `18 passed` when you have finished every exercise.
4. `.venv/bin/python3 examples/report_measurements.py | diff - expected-output/measured-values.txt`
   → no output.
5. Break one assertion in `examples/test_regularization_claims.py` on
   purpose, re-run the harness, and confirm it reports a failure and
   exits non-zero. Restore it. A test suite you have never seen fail is
   not evidence.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints one `ok:` or
`FAIL:` line per check, ends with `N checks, M failure(s)`, and exits
non-zero when `M` is not zero.

The fourteen checks are:

1-3. The installed numpy, scikit-learn and pytest match the pins exactly.
4. Every published claim reproduced directly against `regularization_lib`,
with no pytest involved — so a broken test file cannot hide a broken
library, and vice versa.
5. `pytest examples -q` reports 18 passed.
6. `pytest starter -q` reports 4 passed, 14 skipped.
7. The combined `pytest examples starter` invocation aborts, as
documented.
8. `report_measurements.py` output is byte-identical to the captured
table.
9-10. A scratch copy of `examples/` passes, then fails with a non-zero
exit and the failing test named after one assertion is deliberately
rewritten.
11. Ridge's never-zeros behaviour, lasso's monotone zeroing, and the
near-duplicate splitting are re-confirmed at alphas and dataset seeds the
lesson never quotes, so no directional claim rests on a single value.
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
created outside this directory, so those four commands return your
machine to exactly the state it was in.

## Troubleshooting

See `troubleshooting.md`, which covers the missing virtual environment,
the `import file mismatch` collision, a near-duplicate split that is not
an exact zero at some seeds, ElasticNet's alpha not matching Ridge's, and
`Lasso` convergence warnings.

## Security notes

See `security.md`. In short: no network after the install, no
credentials, no `sudo`, no write outside this directory except a
`mktemp -d` scratch directory the harness removes in the same run, and
everything reversible with `rm -rf .venv`.

## Extension exercises

1. **Sweep alpha finer, and plot the path.** Exercise 2 samples 60 alphas.
   Use `sklearn.linear_model.lasso_path` to get the exact piecewise-linear
   path scikit-learn computes internally, and compare the alphas it
   reports crossing zero to the ones this lab measured by grid search.
2. **A three-way tie.** Build three near-identical columns instead of two
   and measure whether lasso still picks exactly one, or splits its
   selection across two of the three at some alphas.
3. **LassoCV versus a hand-rolled grid search.** Exercise 1b uses
   `LassoCV`. Reimplement its cross-validation loop by hand with
   `KFold` and `Lasso`, and confirm you recover the same alpha.
4. **RidgeCV.** Do the same for ridge: does `RidgeCV`'s chosen alpha
   ever zero a coefficient? It should not, by the same geometry that
   governs the rest of this lab — confirm it.
5. **A harder sparse-recovery case.** Exercise 3 uses independent
   informative features. Rebuild it with `make_regression(effective_rank=...)`
   or correlated informative features, and measure whether recovery
   degrades even without adding noise.
6. **The geometry in three features.** Exercise 8 uses two features so
   the constraint region is a 2-D diamond or circle. Extend it to three
   features (an octahedron versus a sphere) and measure how many
   coefficients lasso zeros as you push alpha up, compared to the
   two-feature case.
7. **Standardize inside a Pipeline.** Exercise 4 standardizes by hand.
   Rebuild it with `sklearn.pipeline.Pipeline([("scale", StandardScaler()),
   ("lasso", Lasso(...))])` and confirm the selected feature set matches.

## Navigation

- Lab brief: `starter/00_brief.md`
- Previous lab: `../day-150-multiple-and-polynomial-regression/`
- Next lab: `../day-152-regression-metrics/`
- Week 22 project: `../projects/week-22/`
