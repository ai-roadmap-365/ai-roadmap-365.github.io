# Day 141 lab — What the Number Is Not Telling You

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** What Machine Learning Is and Is Not
- **Day number:** 141 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-141-what-machine-learning-is-and-is
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-141-what-machine-learning-is-and-is` when the site is running.
<!-- generated-links:end -->

## Purpose

You measure, on real runs, the nine things an accuracy number does not
tell you. The lab opens by fitting a one-nearest-neighbour model to a
dataset whose labels are coin flips: it scores **exactly 1.000** on its
training data and **0.518** — chance — on unseen data. It has learned
nothing at all and reports perfection.

Everything after that is the same discipline applied nine ways: a
three-line rule that beats every trained model on the same problem, a
generalisation gap measured on iris and on constructed data, an accuracy
that collapses from 0.948 to 0.4895 when the input region moves, a
regressor that is 774 times worse one step outside its training range, a
"82 percent accurate" model that loses to predicting the majority class,
an irreducible ceiling no model crosses, a hundredfold increase in
training data that fixes one problem and not another, and a decision
function that says when not to use machine learning at all.

This is the first day of Course04 and the first day you use
scikit-learn. It is deliberately not a tour of its API — every model
here is constructed by a one-line helper with its settings already
fixed, because the models are not the subject. What their scores mean
is.

## Learning objectives

By the end of this lab you will be able to:

- Demonstrate that a training-set score is not evidence, by producing a
  perfect one from a model that has learned nothing.
- Write a nearest-neighbour classifier from scratch in NumPy and explain
  why its training accuracy is 1.000 by construction.
- Show a problem where an exact three-line rule beats every trained
  model, and state when that is the professional answer.
- Measure a generalisation gap and read what its size tells you.
- Make a model's accuracy collapse under a distribution shift it was
  never told about.
- Distinguish interpolation from extrapolation with measured error on
  both sides of a training range.
- Compare any model against a majority-class baseline before believing
  its score, including the case where it loses.
- Measure an irreducible error ceiling set by label noise and confirm no
  model crosses it.
- Say when more data helps and when it cannot, with numbers for both.
- Apply a four-question decision function to decide whether machine
  learning is the right tool at all.

## Prerequisites

- Day 137 — features and leakage. You already know that a result which
  looks too good is a bug report; this lab supplies the measurements
  behind that instinct.
- Day 136 — the untouched confirmation set and the forking-paths
  problem.
- Days 117-118 — the standard error, and why a small margin on a small
  sample is noise.
- Comfort with `pytest` and NumPy array indexing, and a working
  `python3` (3.11 or newer) on your PATH.

## Supported operating systems

- **macOS** (Intel or Apple Silicon) — the machine this lab was written
  and run on: macOS 26.5.2, arm64.
- **Linux** — any distribution with Python 3.11 or newer. Every command
  below is identical.
- **Windows** — use WSL2 and follow the Linux path. Native PowerShell
  works if you substitute `.venv\Scripts\python.exe` for
  `.venv/bin/python3`, but the harness is a bash script: run it under
  Git Bash or WSL2, not `cmd.exe`.

## Hardware requirements

Nothing special. The largest dataset in this lab is 5,000 rows with two
features; the whole harness runs in under fifteen seconds on a laptop
and needs no GPU, no display and no network after install. Peak memory
is a few tens of megabytes, dominated by scikit-learn's import.

## Required software

- Python 3.11 or newer (3.14.0 here).
- The pins in `requirements/requirements.txt`: `numpy` 2.5.2,
  `scikit-learn` 1.9.0, `pytest` 9.1.1. Installing scikit-learn also
  pulls in `scipy` (1.18.1 here), `joblib` and `threadpoolctl` as its
  own dependencies; nothing in this lab imports them directly.
- `bash` for the test harness (3.2 or newer; macOS's system bash is
  fine).

No dataset download is required. The iris measurements come from
`sklearn.datasets.load_iris`, which reads a copy bundled inside the
installed scikit-learn package — 150 rows, 4 features, 3 classes.

## Free and open-source options

Everything this lab installs is free and open source: `scikit-learn`
(BSD-3-Clause), `numpy` (BSD-3-Clause), `scipy` (BSD-3-Clause) and
`pytest` (MIT). There is no paid tier anywhere in this lab and no
account to create. The two commercial platforms discussed in the lesson
are named there with their pricing models stated qualitatively; nothing
here depends on either, and no output in this lab or lesson comes from
running them.

## Installation

```bash
cd labs/sections/machine-learning/day-141-what-machine-learning-is-and-is
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy, sklearn; print(numpy.__version__, sklearn.__version__)"
```

That last line should print `2.5.2 1.9.0`. The `pip install` is the only
step that touches the network; nothing after it does.

## File structure

```
day-141-what-machine-learning-is-and-is/
├── README.md                      this file
├── metadata.yml                   lab metadata and the literal result of the real run
├── security.md                    what this lab does to your machine
├── troubleshooting.md             the failures you are most likely to hit
├── requirements/
│   ├── README.md                  why each pin is there
│   └── requirements.txt           numpy, scikit-learn, pytest, pinned
├── starter/
│   ├── 00_brief.md                read this first
│   ├── ml_lib.py                  the machinery: datasets, models, the hand-written 1-NN
│   ├── test_ml_lib.py             three solved checks on the machinery
│   └── test_ml_claims.py          ten pytest.skip stubs — your work
├── examples/
│   ├── ml_lib.py                  identical to starter/ml_lib.py
│   ├── test_ml_lib.py             identical to starter/test_ml_lib.py
│   ├── test_ml_claims.py          the reference solution, all ten written out
│   └── report_measurements.py     prints every measured pair as one table
├── tests/
│   └── run_tests.sh               the harness: 13 checks, exits non-zero on any failure
└── expected-output/
    ├── FIELDS.md                  what is exact, what may differ, and why
    ├── measured-values.txt        the captured measurement table
    ├── examples-run.txt           captured `pytest examples -q`
    ├── starter-run.txt            captured `pytest starter -q`
    └── test-run.txt               captured `bash tests/run_tests.sh`
```

## How to run

```bash
# 1. Read the brief
cat starter/00_brief.md

# 2. See where you are starting from: three passes, ten skips
.venv/bin/pytest starter -q

# 3. Work through the ten stubs in starter/test_ml_claims.py, one at a time
.venv/bin/pytest starter -q

# 4. Compare against the reference solution
.venv/bin/pytest examples -q

# 5. See every measured pair as one table
.venv/bin/python3 examples/report_measurements.py

# 6. Run the full harness
bash tests/run_tests.sh
```

Run `pytest starter` and `pytest examples` as **two separate commands**.
Both directories contain modules with the same names, and a single
`pytest starter examples` invocation aborts collection with an
`import file mismatch` error. The harness checks that this is still
true, so you can see the failure rather than take it on trust.

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 -m venv .venv` | Creates a lab-local virtual environment. Nothing is installed system-wide |
| `.venv/bin/pip install -r requirements/requirements.txt` | Installs the three pinned packages and their dependencies. The only networked step |
| `.venv/bin/pytest starter -q` | Runs your work in progress. Skips are exercises not yet written |
| `.venv/bin/pytest examples -q` | Runs the reference solution: 13 passes |
| `.venv/bin/python3 examples/report_measurements.py` | Prints all nine exercises' measured values as one readable table |
| `bash tests/run_tests.sh` | The 13-check harness: version pins, the nine claims reproduced without pytest, both suites, the collision check, a byte-comparison against the captured table, a deliberate break-and-restore, and a clean-up sweep |

## Expected output

`.venv/bin/pytest examples -q` ends with:

```
13 passed
```

`.venv/bin/pytest starter -q`, before you have written anything, ends
with:

```
3 passed, 10 skipped
```

`bash tests/run_tests.sh` ends with:

```
13 checks, 0 failure(s)
```

and exits 0. The full captured runs are in `expected-output/`. The
measurement table, captured verbatim, is
`expected-output/measured-values.txt`; the headline pairs are:

| Exercise | Measured |
| --- | --- |
| 1. Perfect accuracy, zero learning | train **1.000**, test **0.518** |
| 2. A rule beats a model | rule **1.000**, best model **0.9675** |
| 3. The generalisation gap | iris **1.000 / 0.960**; noisy data **1.000 / 0.6535**, where a simpler model scores **0.780 / 0.7655** |
| 4. Distribution shift | in-distribution **0.948**, shifted **0.4895** |
| 5. Extrapolation | error **0.180** inside, **139.704** outside |
| 6. The baseline | baseline **0.900**, 1-NN **0.821**, tree **0.817** |
| 7. The noise ceiling | ceiling **0.750**; best measured **0.73725** |
| 8. More data | variance **0.5995 → 0.99725**; noise **0.6655 → 0.68675** |
| 9. `should_use_ml` | five distinct verdicts across six cases |

## Validation steps

1. `.venv/bin/pytest examples -q` reports `13 passed`.
2. `.venv/bin/pytest starter -q` reports `3 passed, 10 skipped` before
   you start, and `13 passed` when you have finished all ten.
3. `.venv/bin/python3 examples/report_measurements.py` prints a table
   byte-identical to `expected-output/measured-values.txt`.
4. `bash tests/run_tests.sh` prints `13 checks, 0 failure(s)` and
   `echo $?` prints `0`.
5. Break one assertion on purpose — change `assert train_acc == 1.0` to
   `0.5` in `examples/test_ml_claims.py` — and confirm the harness
   reports failures and exits non-zero. Restore it afterwards. That was
   done during authoring: the harness reported `13 checks, 2 failure(s)`
   and exit 1.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints one `ok:` or
`FAIL:` line per check, ends with `N checks, M failure(s)`, and exits 0
only when `M` is zero. Its thirteen checks are:

1-3. Each pinned version matches what is actually installed.
4. All nine exercises reproduced directly against `ml_lib`, with pytest
   entirely out of the picture, so a green pytest run cannot be the only
   evidence.
5. `pytest examples -q` reports 13 passed.
6. `pytest starter -q` reports 3 passed, 10 skipped.
7. `pytest examples starter` in one invocation really does abort with
   `import file mismatch`.
8. `report_measurements.py` still reproduces the captured table exactly.
9. A scratch copy of `examples/` passes before it is broken.
10. Breaking exercise 1's assertion in that scratch copy produces a
    non-zero exit that names the failing test.
11. No URL appears anywhere in `examples/` or `starter/` source.
12. No `__pycache__` is left behind.
13. No `.pytest_cache` is left behind.

Nothing in this lab asserts on a timing. Every assertion is on a value
or a shape.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: reset your work
```

The harness already clears `__pycache__` and `.pytest_cache` on its way
out, so the first two lines are usually no-ops.

## Troubleshooting

See `troubleshooting.md` for the full list. The three most common:

- **`No lab .venv found`** — the harness exits 2 before running
  anything. Create the environment with the Installation commands above,
  or point `PYTHON` and `PYTEST` at an interpreter that has the pins.
- **`import file mismatch`** — you ran `pytest starter examples` in one
  invocation. Run them separately.
- **A number is off in the last decimal place** — check that
  `pip list` shows exactly `numpy 2.5.2` and `scikit-learn 1.9.0`. Every
  value here is deterministic given those pins and the seeds in
  `ml_lib.py`; a different scikit-learn can break ties differently.

## Security notes

See `security.md`. In short: this lab writes only inside its own
directory and one temporary directory it creates and removes, reaches no
network after `pip install`, needs no credentials, runs no server, and
uses no data about you. The iris measurements come from a copy bundled
inside scikit-learn, not from a download.

## Extension exercises

1. Change `noise_rate` in exercise 7 from 0.25 to 0.40 and confirm the
   measured ceiling moves to 0.60. Then try to beat it with any model
   you like. You cannot, and the attempt is the lesson.
2. Vary the `offset` in exercise 4 from 0.0 to 3.0 in steps and plot
   accuracy against offset. Find the offset at which the model first
   drops below chance.
3. Replace the checkerboard in exercise 8 with an 8x8 grid and re-run
   the data-size sweep. More boundary needs more data — quantify how
   much.
4. Add a fifth question to `should_use_ml`: whether a person can review
   an individual decision. Decide where in the order it belongs and
   defend the position in a comment.
5. Write a second from-scratch model — a majority-class predictor is
   three lines — and confirm it reproduces `DummyClassifier`'s 0.900
   exactly on exercise 6's data.

## Navigation

- Lab index: `labs/README.md`
- Section: `labs/sections/machine-learning/`
- Previous lab: Day 140 — Section Project: An Exploratory Study
- Next lab: Day 142 — Supervised, Unsupervised, and Reinforcement Learning
