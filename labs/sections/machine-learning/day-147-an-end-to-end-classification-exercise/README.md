# Day 147 lab — One Classification Project, Run Properly

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** An End-to-End Classification Exercise
- **Day number:** 147 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-147-an-end-to-end-classification-exercise
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-147-an-end-to-end-classification-exercise` when the site is running.
<!-- generated-links:end -->

## Purpose

Days 141 through 146 each isolated one discipline in a lab built to show
it alone: what a score means, the three feedback shapes, the workflow's
stage contract, the three sets and the selection optimism they exist to
control, the bias/variance trade, and the scikit-learn estimator API.

This lab is every one of those disciplines, spent on one real dataset, in
the order a working project actually uses them: frame, baseline, split,
pipeline, cross-validate, select, **one** test evaluation, error analysis,
an honest verdict with an interval.

The dataset is chosen by measuring, not by habit — `iris` and `wine` are
both tried first and both discarded, because both saturate near-perfect
accuracy on 30-36 test rows, too coarse for an honest interval:

| dataset | rows | features | classes | baseline | test rows |
| --- | --- | --- | --- | --- | --- |
| iris | 150 | 4 | 3 | 0.3333 | 30 |
| wine | 178 | 13 | 3 | 0.3889 | 36 |
| breast_cancer | 569 | 30 | 2 | 0.6316 | 114 |

Using `breast_cancer`: 36 candidate pipelines are cross-validated on train
rows only, the winner (`LogisticRegression(C=1)`, cv accuracy 0.9780) is
evaluated exactly once on test (0.9825), and Day 144's selection-optimism
formula predicts an inflation of 0.0326 for that sweep — while the
measured drop over 20 seeds averages **−0.0001**, because the formula
assumes independent zero-skill candidates and these 36 are neither
independent nor skill-free. A separate leaky version, which selects by
scoring all 36 candidates directly against the test set, never scores
worse than the honest one across 20 seeds, by a mean gap of +0.0096.

## Learning objectives

By the end of this lab you will be able to:

1. Choose a dataset for a classification project by measuring headroom,
   not by picking whichever one is most familiar.
2. Establish a majority-class baseline before fitting any model.
3. Build a real train/test split and hold the test rows back until one
   evaluation, using the discipline Days 143-144 built.
4. Sweep a genuine set of candidate pipelines with scikit-learn's
   `Pipeline`, and count K rather than losing track of it.
5. Select a winner using cross-validation on training rows only, never on
   test rows.
6. Enforce a one-evaluation budget on a test set mechanically.
7. Compute the selection optimism Day 144's formula predicts for a real
   sweep, and explain honestly where that prediction fails.
8. Read a confusion matrix for the specific mistakes it reveals, not only
   for the accuracy it summarises.
9. State a verdict with a 95 percent interval, and judge whether an
   improvement is distinguishable from a baseline at the test-set size you
   actually have.
10. Reproduce, and recognise, the mistake of selecting a model by scoring
    every candidate directly against the test set.

## Prerequisites

- Day 141 for what a score means, Day 142 for the winner's curse, Day 143
  for stage ordering, Day 144 for the three sets and selection optimism,
  Day 145 for overfitting and underfitting, and Day 146 for the
  scikit-learn estimator API — `fit`, `predict`, `Pipeline`. This lab uses
  every one of them and teaches none of them again.
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
here is small-array NumPy and scikit-learn on the CPU. The heaviest steps
are the two 20-seed sweeps in exercises 7b and 10b, each cross-validating
36 candidates 20 times over; on the capture machine the full harness
completes in well under a minute. Around 400 MB of disk for the virtual
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
- The dataset, `sklearn.datasets.load_breast_cancer`, ships inside the
  scikit-learn package itself; nothing is downloaded and no dataset
  licence beyond scikit-learn's own applies to your use of this lab.

The estimators used here — `LogisticRegression`, `KNeighborsClassifier`,
`DecisionTreeClassifier`, `DummyClassifier` — and the selection machinery
— `Pipeline`, `StratifiedKFold`, `cross_val_score`, `train_test_split` —
are all part of scikit-learn.

## Installation

From the repository root:

```bash
cd labs/sections/machine-learning/day-147-an-end-to-end-classification-exercise
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
day-147-an-end-to-end-classification-exercise/
├── README.md                      this file
├── metadata.yml                   how the lab was actually executed
├── security.md                    what the lab touches, and what it does not
├── troubleshooting.md             every failure this lab is known to produce
├── requirements/
│   ├── README.md                  why the pins are exact
│   └── requirements.txt           numpy, scikit-learn, pytest
├── starter/
│   ├── 00_brief.md                read this first
│   ├── classification_lib.py      complete machinery — not the exercise
│   ├── test_classification_lib.py four machinery checks, already solved
│   └── test_classification_claims.py  fourteen exercises, each a skip to replace
├── examples/
│   ├── classification_lib.py      identical to the starter copy
│   ├── test_classification_lib.py the same four machinery checks
│   ├── test_classification_claims.py  the reference solutions
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

`starter/classification_lib.py` and `examples/classification_lib.py` are
byte identical on purpose. The library is machinery; the exercises are the
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
| `.venv/bin/pytest starter -q` | Runs your work: four machinery checks pass, fourteen exercises skip until you write them |
| `.venv/bin/pytest examples -q` | Runs the reference solutions — eighteen assertions about the whole project |
| `.venv/bin/python3 examples/report_measurements.py` | Recomputes every published number and prints them as one table |
| `bash tests/run_tests.sh` | Fifteen checks: version pins, every claim reproduced without pytest, both suites, the collision, a byte-comparison of the report, the one-evaluation guarantee, a deliberate self-break, an unquoted-seed re-check, and cleanliness |

## Expected output

`bash tests/run_tests.sh` ends with:

```
---------------------------------------------------------------
15 checks, 0 failure(s)
```

and exits 0. `pytest examples -q` reports `18 passed`.
`pytest starter -q` reports `4 passed, 14 skipped` until you start work.

The complete captured runs are in `expected-output/`. The measurement
table is compared byte for byte by check 6, so if a number in the lesson
ever drifts from the code, the harness fails rather than the lesson
quietly becoming wrong.

Read `expected-output/FIELDS.md` before concluding that a mismatch on your
machine is a bug. It separates what is exact everywhere — the dataset's
shape, the standard-error formula, the leaky gap never going negative —
from what holds only under the pinned versions, which is most of the
decimals.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` → `15 checks, 0 failure(s)`
   and `exit=0`.
2. `.venv/bin/pytest examples -q` → `18 passed`.
3. `.venv/bin/pytest starter -q` → `4 passed, 14 skipped` before you
   start; `18 passed` when you have finished every exercise.
4. `.venv/bin/python3 examples/report_measurements.py | diff - expected-output/measured-values.txt`
   → no output.
5. Break one assertion in `examples/test_classification_claims.py` on
   purpose, re-run the harness, and confirm it reports failures and exits
   non-zero. Restore it. A test suite you have never seen fail is not
   evidence.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints one `ok:` or
`FAIL:` line per check, ends with `N checks, M failure(s)`, and exits
non-zero when `M` is not zero.

The fifteen checks are:

1-3. The installed numpy, scikit-learn and pytest match the pins exactly.
4. Every published claim reproduced directly against `classification_lib`,
   with no pytest involved — so a broken test file cannot hide a broken
   library, and vice versa.
5. `pytest examples -q` reports 18 passed.
6. `pytest starter -q` reports 4 passed, 14 skipped.
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
the `import file mismatch` collision, the harness taking a while, a
winning configuration that differs from the lesson's, the predicted
optimism not matching the measured drop, leaky-gap numbers that differ
from the lesson's, `LogisticRegression` convergence warnings, and sampled
figures moving with the NumPy pin.

## Security notes

See `security.md`. In short: no network after the install, no
credentials, no `sudo`, no write outside this directory except a
`mktemp -d` scratch directory the harness removes in the same run, and
everything reversible with `rm -rf .venv`. It also reads `GatedTestSet` as
an access-control pattern, and shows explicitly that a budget enforced
only at one call site — as opposed to on the resource itself — can be
bypassed, which exercise 10's leaky search deliberately does.

## Extension exercises

1. **Nested cross-validation.** Implement an inner loop that selects among
   the 36 candidates and an outer loop that scores the winner, so the
   outer score is never contaminated by the selection. Measure whether the
   gap between cv_mean and test accuracy shrinks further, and report the
   cost in fits.
2. **A fourth family.** Add support-vector classifiers to
   `candidate_configs`, re-run the sweep, and report whether the winner or
   its cross-validated accuracy changes at seed 0.
3. **Cost-sensitive error analysis.** Exercise 8 counts false negatives and
   false positives with equal weight. Assign a cost to each — say, ten
   times worse for a missed malignancy — and find whether a different
   candidate in the sweep would have been preferred under that cost.
4. **Scale the test set.** Repeat the leaky-gap comparison (exercise 10b)
   using a 40/60 train/test split instead of 80/20, so the test set has
   roughly 340 rows instead of 114. Report whether the mean gap changes
   and connect it to Day 144's test-sizing table.
5. **Break the independence assumption on purpose.** Duplicate 10 percent
   of the rows into both the train and test splits before running the
   sweep, and measure how much the reported test accuracy inflates. This
   is Day 144's group-leakage lesson, reconstructed on real data.
6. **A stricter gate.** Extend `GatedTestSet` to log every attempted
   evaluation with a caller identifier, so a refused attempt leaves a
   trace, and use the log to show that `leaky_selection_test_score`'s
   accesses never go through the gate at all.

## Navigation

- Lab brief: `starter/00_brief.md`
- Previous lab: `../day-146-your-first-model-with-scikit-learn/`
- Week 21 — Machine Learning Fundamentals — ends here. Day 148 begins
  Week 22 (Regression) with linear regression.
- Week 21 project: `../projects/week-21/`
