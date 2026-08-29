# Day 145 lab — Two Ways to Be Wrong

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Overfitting and Underfitting
- **Day number:** 145 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-145-overfitting-and-underfitting
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-145-overfitting-and-underfitting` when the site is running.
<!-- generated-links:end -->

## Purpose

There are exactly two ways a model can be wrong, and they are not two ends
of one dial. They are two different quantities, they respond to completely
different interventions, and this lab measures both directly rather than
describing them.

The centrepiece fits **200 models to 200 independent training sets**,
predicts the same fixed grid with all of them, and separates the error by
brute force:

| degree | bias² | variance | noise | predicted | observed |
| --- | --- | --- | --- | --- | --- |
| 1 | 4.2985 | 0.7112 | 4.0000 | 9.0097 | 9.0295 |
| 3 | 0.0033 | 0.8399 | 4.0000 | 4.8432 | 4.8431 |
| 12 | 2803.5354 | 452183.1336 | 4.0000 | 454990.6691 | 455027.8625 |

**Underfitting is bias. Overfitting is variance.** And the last two
columns are why this is a lab rather than an analogy: the three parts add
up to the error actually observed, at every capacity, to within one
percent.

Then the measurement that changes what teams do with their budgets:

```text
      n    degree 1     degree 4        degree 24
     15      8.5023      4.9218      215413.2388
   2000      8.2393      3.9880           4.0055
```

A hundred and thirty times more data took the overfit model from 215,413
to 4.0055 — the irreducible floor, exactly — and the underfit model from
8.5023 to 8.2393. **More data cures one failure completely and the other
not at all.**

Two of the exercises exist because building this lab went somewhere
unplanned. A degree-2 model, which contains every degree-1 model as a
special case, measures more bias *and* more variance. And a degree-24
model is worse at 25 training rows than at 15 — because degree 24 supplies
exactly 25 features, and 25 rows is the interpolation threshold. Both are
kept and measured rather than tidied away.

## Learning objectives

By the end of this lab you will be able to:

1. Measure bias and variance directly by fitting many models to many
   independent training sets.
2. Verify that bias squared plus variance plus noise equals the error
   actually observed.
3. Diagnose which failure a model has from the sign of its generalisation
   gap, using a single fit.
4. Recognise a negative gap as the signature of underfitting rather than
   as a broken split.
5. Explain why a strictly larger model class can carry more bias as well
   as more variance.
6. Predict which interventions help each failure, and name the expensive
   mistake each diagnosis rules out.
7. Tune a regularisation penalty and explain why the training error rising
   is the mechanism rather than a side effect.
8. Estimate an irreducible noise floor and use it to decide when to stop.
9. Treat training time as a capacity dial, and say why early stopping
   needs patience rather than a stop-on-first-rise rule.
10. Identify the interpolation threshold where features meet rows.

## Prerequisites

- Day 141 for what a training score is worth, Day 143 for the workflow,
  and Day 144 for the generalisation gap and for selection bias — which
  this lab is repeatedly careful to distinguish from overfitting.
- Days 117-118 for the sampling distribution, which is what the variance
  term measures.
- Day 111 for gradient descent, which the early-stopping exercise runs.
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
here is a small least-squares solve on the CPU. The heaviest step is the
decomposition, which fits 200 models per capacity across seven capacities
and completes in a couple of seconds on the capture machine. Around
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
- No dataset is downloaded or bundled: every dataset is generated from a
  seeded generator, so no dataset licence applies to your use of this lab.

scikit-learn also ships `validation_curve` and `learning_curve`, which do
in one call what exercises 1 and 3 do by hand. This lab computes them
manually so the mechanism is visible; in a real project reach for the
library versions, which handle the cross-validation correctly.

## Installation

From the repository root:

```bash
cd labs/sections/machine-learning/day-145-overfitting-and-underfitting
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
day-145-overfitting-and-underfitting/
├── README.md                      this file
├── metadata.yml                   how the lab was actually executed
├── security.md                    what the lab touches, and what it does not
├── troubleshooting.md             every failure this lab is known to produce
├── requirements/
│   ├── README.md                  why the pins are exact
│   └── requirements.txt           numpy, scikit-learn, pytest
├── starter/
│   ├── 00_brief.md                read this first
│   ├── fitting_lib.py             complete machinery — not the exercise
│   ├── test_fitting_lib.py        four machinery checks, already solved
│   └── test_fitting_claims.py     fourteen exercises, each a skip to replace
├── examples/
│   ├── fitting_lib.py             identical to the starter copy
│   ├── test_fitting_lib.py        the same four machinery checks
│   ├── test_fitting_claims.py     the reference solutions
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

`starter/fitting_lib.py` and `examples/fitting_lib.py` are byte identical
on purpose. The library is machinery; the exercises are the work.

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
| `.venv/bin/pytest starter -q` | Runs your work: four machinery checks pass, fourteen exercises skip until you write them |
| `.venv/bin/pytest examples -q` | Runs the reference solutions — eighteen assertions about capacity, regularisation, data and time |
| `.venv/bin/python3 examples/report_measurements.py` | Recomputes every published number and prints them as one table |
| `bash tests/run_tests.sh` | Fourteen checks: version pins, every claim reproduced without pytest, both suites, the collision, a byte-comparison of the report, a deliberate self-break, the shape of every result re-confirmed at unquoted seeds, and cleanliness |

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

Read `expected-output/FIELDS.md` before concluding that a mismatch on your
machine is a bug. It separates what is exact everywhere — the 4.0000
floor, the 25-feature count, the monotonicity of training error in the
penalty, the shape of every result — from what holds only under the
pinned versions.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` → `14 checks, 0 failure(s)`
   and `exit=0`.
2. `.venv/bin/pytest examples -q` → `18 passed`.
3. `.venv/bin/pytest starter -q` → `4 passed, 14 skipped` before you
   start; `18 passed` when you have finished every exercise.
4. `.venv/bin/python3 examples/report_measurements.py | diff - expected-output/measured-values.txt`
   → no output.
5. Break one assertion in `examples/test_fitting_claims.py` on purpose,
   re-run the harness, and confirm it reports failures and exits non-zero.
   Restore it. A test suite you have never seen fail is not evidence.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints one `ok:` or
`FAIL:` line per check, ends with `N checks, M failure(s)`, and exits
non-zero when `M` is not zero.

The fourteen checks are:

1-3. The installed numpy, scikit-learn and pytest match the pins exactly.
4. Every published claim reproduced directly against `fitting_lib`, with
   no pytest involved — so a broken test file cannot hide a broken
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
11. The shape of every result — training error falling with capacity, the
    degree-24 model overfitting, the degree-1 model underfitting, bias
    dominant when rigid and variance dominant when flexible — is
    re-confirmed at three data seeds the lesson never quotes.
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
training error rising at high degree, the degree-24 model getting worse
with more data, test error below training error, the decomposition not
summing exactly, a differing early-stopping epoch, the harness taking a
while, the `import file mismatch` collision, and conditioning warnings.

## Security notes

See `security.md`. In short: no network after the install, no credentials,
no `sudo`, no write outside this directory except a `mktemp -d` scratch
directory the harness removes in the same run, CPU only, and everything
reversible with `rm -rf .venv`. It also explains why exercise 2 is a
privacy measurement as well as an accuracy one — a high-variance model has
literally stored particulars of its training rows, which is what
membership-inference attacks exploit.

## Extension exercises

1. **Find the double descent.** Push the degree-24 column past the
   interpolation threshold in both directions with a finer grid of `n`,
   and report the shape you actually get.
2. **Compare L1 with L2.** Repeat the regularisation sweep with `Lasso`
   and report how many coefficients it drives to zero at the best alpha,
   and whether its best test error beats ridge's 5.7257.
3. **Decompose a tree.** Run `bias_variance` on decision trees at several
   `max_depth` values. Report where bias and variance cross, and compare
   the shape with the polynomial one.
4. **Break the early-stopping rule.** Find a seed on which the test curve
   dips below a local rise, so that stop-at-first-increase does worse than
   patience. Report the seed and both scores.
5. **Change the noise.** Re-run the capacity sweep at a noise standard
   deviation of 0.5 and of 5.0. Report how the best degree moves and
   explain the direction.
6. **Ensemble the variance away.** Average twenty degree-12 models fitted
   to twenty bootstrap resamples, and report the ensemble's bias and
   variance against a single model's 2803.5354 and 452183.1336.
7. **Remove the scaler.** Delete the `StandardScaler` from
   `polynomial_model` and re-run the capacity sweep. Report at which
   degree the training error starts rising, and explain why that is a
   statement about floating point rather than about learning.

## Navigation

- Lab brief: `starter/00_brief.md`
- Previous lab: `../day-144-train-validation-and-test-splits/`
- Next lab: `../day-146-your-first-model-with-scikit-learn/`
- Week 21 project: `../projects/week-21/`
