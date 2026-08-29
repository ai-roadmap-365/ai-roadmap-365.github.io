# Day 146 lab — The Estimator API, From Scratch

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Your First Model with scikit-learn
- **Day number:** 146 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-146-your-first-model-with-scikit-learn
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-146-your-first-model-with-scikit-learn` when the site is running.
<!-- generated-links:end -->

## Purpose

Days 141-145 called `.fit(X, y)` and `.predict(X)` on scikit-learn objects
dozens of times without ever explaining what those two words mean. This
lab builds a classifier that implements the whole estimator API by hand —
no inheritance from scikit-learn at all — and measures exactly where it
agrees with the library, and exactly where it stops.

The headline result:

```text
MajorityClassifier, built entirely from first principles:
  predictions match DummyClassifier(strategy="most_frequent") exactly : True
  called directly -- .fit(), .predict(), .score() -- all work fine

The SAME classifier, handed to cross_val_score:
  AttributeError: 'MajorityClassifier' object has no attribute '__sklearn_tags__'
  ...Make sure to inherit from `BaseEstimator`...

The identical classifier, now inheriting (ClassifierMixin, BaseEstimator):
  works inside a real Pipeline, scored by a real cross_val_score -> 5 real scores
  get_params/set_params are not written anywhere in its source -- inherited
```

Five methods — `fit`, `predict`, `score`, `get_params`, `set_params` — are
enough to reproduce a library estimator's output exactly, and enough to
call all five directly. They are not enough, in this version of
scikit-learn, to interoperate with `Pipeline` or `cross_val_score`, which
both lean on `__sklearn_tags__` — a method only `BaseEstimator` supplies.
That gap, found by testing rather than assumed, is the centrepiece of this
lab.

## Learning objectives

By the end of this lab you will be able to:

1. Implement `fit`, `predict`, `predict_proba`, `score`, `get_params` and
   `set_params` from scratch and verify they reproduce a library
   estimator's output exactly.
2. State precisely what `fit()` adds to an object — every learned
   attribute ends in a trailing underscore, by convention, and nothing
   else does.
3. Explain why `NotFittedError` exists and reproduce its message on both a
   library estimator and a hand-built one.
4. Show that `get_params`/`set_params` round-trip correctly, and that
   `clone()` copies configuration without ever copying learned state.
5. Read a `Pipeline`'s own `get_params(deep=True)` and change a nested
   step's hyper-parameter through it.
6. Measure that a `Pipeline` step is refit once per cross-validation fold,
   on that fold's training rows only, and connect that mechanism to why
   nothing fitted can leak between folds.
7. Identify, from a real failure, exactly what `Pipeline` and
   `cross_val_score` require beyond the five core methods in this version
   of scikit-learn, and fix it with one line of inheritance.
8. State how many of scikit-learn's discovered estimators implement `fit`,
   and that `transform` and `predict` are not mutually exclusive.
9. Show that `predict()` is `argmax(predict_proba())`, restated through
   `classes_`, and that `decision_function` agrees with it too.
10. Measure what `random_state=None` costs: identical predictions under a
    fixed seed, and a different model on every fit without one.
11. Run `check_estimator()` against a real estimator and report, honestly,
    which of its 52 checks pass and why the other two do not.

## Prerequisites

- Day 141 for what a model score means, Day 143 for stage ordering and
  what "anything fitted" refers to, and Day 144 for the splitters this lab
  uses without re-teaching. Day 145's bias-variance material is not needed
  here.
- Comfort reading a Python class definition and a pytest failure, and
  `python3` 3.11 or newer on your `PATH`.

## Supported operating systems

- macOS (Apple Silicon or Intel) — the capture machine was macOS 26.5.2
  on arm64.
- Linux (any distribution with Python 3.11+ and bash).
- Windows via WSL2. The harness is a bash script and uses `mktemp -d`,
  `find` and process substitution; native PowerShell is not supported.

## Hardware requirements

Any machine that can run Python. **No GPU is needed or used** — everything
here is small-array NumPy and scikit-learn on the CPU (CPU only during
capture; no GPU was present or required). The heaviest step is
`check_estimator()`'s 52 checks plus 25 random-forest fits for exercise 9,
which complete in a few seconds on the capture machine. Around 400 MB of
disk for the virtual environment, almost all of it scikit-learn and scipy.

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
- No dataset is downloaded or bundled: every dataset is generated on the
  spot from a seeded generator or from scikit-learn's own internal
  synthetic-data helpers, so no dataset licence applies to your use of
  this lab.

Everything used here — `Pipeline`, `StandardScaler`, `LogisticRegression`,
`RandomForestClassifier`, `DummyClassifier`, `cross_val_score`,
`StratifiedKFold`, `all_estimators`, `check_estimator` — is part of
scikit-learn itself. There is no alternative library to choose between for
this lesson's subject: the estimator API is scikit-learn's own contract.

## Installation

From the repository root:

```bash
cd labs/sections/machine-learning/day-146-your-first-model-with-scikit-learn
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
day-146-your-first-model-with-scikit-learn/
├── README.md                      this file
├── metadata.yml                   how the lab was actually executed
├── security.md                    what the lab touches, and what it does not
├── troubleshooting.md             every failure this lab is known to produce
├── requirements/
│   ├── README.md                  why the pins are exact
│   └── requirements.txt           numpy, scikit-learn, pytest
├── starter/
│   ├── 00_brief.md                read this first
│   ├── estimator_lib.py           complete machinery — not the exercise
│   ├── test_estimator_lib.py      five machinery checks, already solved
│   └── test_estimator_claims.py   eighteen exercises, each a skip to replace
├── examples/
│   ├── estimator_lib.py           identical to the starter copy
│   ├── test_estimator_lib.py      the same five machinery checks
│   ├── test_estimator_claims.py   the reference solutions
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

`starter/estimator_lib.py` and `examples/estimator_lib.py` are byte
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
| `.venv/bin/pytest starter -q` | Runs your work: five machinery checks pass, eighteen exercises skip until you write them |
| `.venv/bin/pytest examples -q` | Runs the reference solutions — twenty-two assertions about how the estimator API behaves |
| `.venv/bin/python3 examples/report_measurements.py` | Recomputes every published number and prints them as one table |
| `bash tests/run_tests.sh` | Fourteen checks: version pins, every claim reproduced without pytest, both suites, the collision, a byte-comparison of the report, a deliberate self-break, results reconfirmed at unquoted seeds and parameters, and cleanliness |

## Expected output

`bash tests/run_tests.sh` ends with:

```
---------------------------------------------------------------
14 checks, 0 failure(s)
```

and exits 0. `pytest examples -q` reports `23 passed`.
`pytest starter -q` reports `5 passed, 18 skipped` until you start work.

The complete captured runs are in `expected-output/`. The measurement
table is compared byte for byte by check 6, so if a number in the lesson
ever drifts from the code, the harness fails rather than the lesson
quietly becoming wrong. Section 8 of the report — what `random_state=None`
costs — prints only structural booleans for exactly this reason: those
numbers are fresh OS entropy on every run and cannot be byte-compared.

Read `expected-output/FIELDS.md` before concluding that a mismatch on your
machine is a bug. It separates what is exact on any machine — the shape of
every finding — from what holds only under the pinned scikit-learn version,
which includes the exact `AttributeError` behind exercise 6 and the exact
`check_estimator()` totals in exercise 10.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` → `14 checks, 0 failure(s)`
   and `exit=0`.
2. `.venv/bin/pytest examples -q` → `23 passed`.
3. `.venv/bin/pytest starter -q` → `5 passed, 18 skipped` before you
   start; `23 passed` when you have finished every exercise.
4. `.venv/bin/python3 examples/report_measurements.py | diff - expected-output/measured-values.txt`
   → no output.
5. Break one assertion in `examples/test_estimator_claims.py` on purpose,
   re-run the harness, and confirm it reports failures and exits non-zero.
   Restore it. A test suite you have never seen fail is not evidence.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints one `ok:` or
`FAIL:` line per check, ends with `N checks, M failure(s)`, and exits
non-zero when `M` is not zero.

The fourteen checks are:

1-3. The installed numpy, scikit-learn and pytest match the pins exactly.
4. Every published claim reproduced directly against `estimator_lib`, with
   no pytest involved — so a broken test file cannot hide a broken
   library, and vice versa.
5. `pytest examples -q` reports 23 passed.
6. `pytest starter -q` reports 5 passed, 18 skipped.
7. The combined `pytest examples starter` invocation aborts, as
   documented.
8. `report_measurements.py` output is byte-identical to the captured
   table.
9-10. A scratch copy of `examples/` passes, then fails with a non-zero
   exit and the failing test named, after one assertion is deliberately
   rewritten.
11. The hand-built classifier's agreement with `DummyClassifier`, the
    fold-fitting count, `predict_proba`/`predict` agreement and the
    bare-estimator failure are re-confirmed at seeds, dataset shapes and
    fold counts the lesson never quotes.
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
the `import file mismatch` collision, the `__sklearn_tags__` AttributeError
in exercise 6 and its fix, why `check_estimator()`'s two failures are
expected, the harness taking a while, `random_state=None` numbers
differing from `FIELDS.md`, and `LogisticRegression` convergence warnings.

## Security notes

See `security.md`. In short: no network after the install, no credentials,
no `sudo`, no write outside this directory except a `mktemp -d` scratch
directory the harness removes in the same run, and everything reversible
with `rm -rf .venv`. It also reads `get_params`/`set_params`/`clone`
correctness as a security-relevant property: a `clone()` that ever leaked
learned state between folds would be the same shape of bug Day 143 spent a
day on, arriving from the object model instead of the workflow.

## Extension exercises

1. **Give `MajorityClassifier` a `transform` method, and explain why you
   should not.** Add one that returns a one-hot encoding of the
   prediction, then argue in two sentences why a *classifier* growing a
   `transform` method is a design smell rather than a convenience — tie
   your answer to exercise 7b's finding about which 20 estimators
   legitimately have both.
2. **Fix `check_classifiers_regression_target`.** Make `MajorityClassifierBase.fit()`
   validate that `y` looks like classification labels — `sklearn.utils.multiclass.type_of_target`
   is the tool — and confirm with `check_estimator()` that the failure
   count drops from 2 to 1.
3. **Measure `__sklearn_tags__` directly.** Call `BaseEstimator().__sklearn_tags__()`
   and print its fields. Which of them would change if `MajorityClassifierBase`
   inherited `ClassifierMixin` only, without `BaseEstimator`? Test it.
4. **A custom transformer.** Build a `MinMaxByColumn` transformer from
   scratch, with `fit`/`transform`/`fit_transform`, and put it inside a
   `Pipeline` ahead of `MajorityClassifierBase`. Confirm `fit_transform`
   gives the same result as calling `fit` then `transform` separately.
5. **`GridSearchCV` on the hand-built estimator.** Since `MajorityClassifierBase`
   supports `get_params`/`set_params` through `BaseEstimator`, wrap it in
   `GridSearchCV` searching over `strategy` and report what `best_params_`
   comes back as, and why.
6. **Time `check_estimator()`.** Measure how much of its runtime is the
   two failing checks versus the fifty passing ones, and report whether
   `on_fail="warn"` changes the total time meaningfully.
7. **A stricter `random_state` audit.** Extend exercise 9 to also fit
   `LogisticRegression` and `KNeighborsClassifier` under `random_state=None`
   and report which of the three model types actually varies — not every
   estimator has randomness to seed in the first place.

## Navigation

- Lab brief: `starter/00_brief.md`
- Previous lab: `../day-145-overfitting-and-underfitting/`
- Next lab: `../day-147-an-end-to-end-classification-exercise/`
- Week 21 project: `../projects/week-21/`
