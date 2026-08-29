# Day 143 lab — The Workflow, Wired Up

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** The Machine Learning Workflow
- **Day number:** 143 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-143-the-machine-learning-workflow
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-143-the-machine-learning-workflow` when the site is running.
<!-- generated-links:end -->

## Purpose

The machine learning workflow is normally drawn as a row of boxes with
arrows between them. Everybody nods at the diagram, and then everybody
goes and writes a notebook where the boxes are cells and the arrows are
whatever order they happened to run them in.

This lab builds the same workflow with the arrows made load-bearing.
Every stage declares what it **requires** and what it **produces**, the
runner refuses to run a stage whose inputs are absent, and every run
leaves a step log and a manifest of content hashes behind it.

The reason for all that machinery is one measurement. On a dataset of 100
rows and 5000 features where the labels are coin flips and no feature
carries any information at all:

| Pipeline | Order | Score |
| --- | --- | --- |
| honest | load, **split, select**, fit, baseline | **0.50** |
| leaky, contracts off | load, **select, split**, fit, baseline | **0.73** |
| leaky, contracts on | same as above | `StageContractError` |

Twenty-three accuracy points on data with nothing in it, produced by
transposing two stages. Same data, same model, same folds, same seed.
Nothing raises. Nothing warns.

The third row is the point of the lab: a stage contract is what turns a
silent twenty-three point lie into a loud error naming the stage that
broke.

You will also measure the decision that comes before any model exists —
which metric you optimise. On an eight-percent-positive problem, a
majority-class baseline scores 0.92 accuracy with **zero** recall, and the
one model that actually finds most of the positives scores *worse than the
constant*.

## Learning objectives

By the end of this lab you will be able to:

1. Express a workflow as stages with declared input and output contracts,
   rather than as cells in an execution order.
2. Demonstrate that transposing two stages changes the reported score,
   and quantify by how much.
3. Explain why an honest contract declaration is the mechanism that makes
   a mis-ordering detectable at all.
4. Show that a leaky ordering's inflation grows with the number of
   features selected.
5. Choose an evaluation metric before choosing a model, and demonstrate a
   case where the metric inverts the decision.
6. Compare any reported score against a majority-class baseline, including
   the case where a useful model loses to a constant.
7. Read a confusion matrix and state what an accuracy figure concealed.
8. Prove a pipeline is deterministic with a manifest of content hashes,
   and prove the manifest is not a constant.
9. Measure the relative size of the modelling stage in your own pipeline
   rather than repeating a folklore percentage.
10. Distinguish a failure that names the broken stage from one that names
    a missing dictionary key.

## Prerequisites

- Day 141 for what a score means, and Day 142 for naming the setting
  before choosing an algorithm.
- Day 126, whose reproducible-pipeline discipline — idempotence,
  determinism, contracts at both ends, a step log, a manifest of hashes —
  is what this lab applies to a modelling workflow.
- Day 137 for the concept of leakage. This lab is about the *ordering*
  that causes it rather than the concept itself.
- Days 117-118 for the standard error, which is why two honest scores here
  land below chance and the lab asserts an inequality rather than a value.
- Comfort with NumPy arrays and reading a pytest failure, and `python3`
  3.11 or newer on your `PATH`.

## Supported operating systems

- macOS (Apple Silicon or Intel) — the capture machine was macOS 26.5.2
  on arm64.
- Linux (any distribution with Python 3.11+ and bash).
- Windows via WSL2. The harness is a bash script and uses `mktemp -d`,
  `find` and process substitution; native PowerShell is not supported.

## Hardware requirements

Any machine that can run Python. The heaviest single step computes 5000
feature-label correlations five times over, which takes a few seconds
here. No GPU. Around 400 MB of disk for the virtual environment, almost
all of it scikit-learn and its scipy dependency.

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
  spot from a seeded generator, so no dataset licence applies to your use
  of this lab.

The stage runner is written from scratch in about forty lines rather than
pulled from a workflow framework. scikit-learn's own `Pipeline` and
`ColumnTransformer` solve the specific leakage this lab measures, and are
the right tool in practice; the lesson covers them. Kedro, Metaflow and
Prefect (all free and open source) solve the same problem at project
scale. None of those is installed here and no output from any of them is
reproduced.

## Installation

From the repository root:

```bash
cd labs/sections/machine-learning/day-143-the-machine-learning-workflow
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy, sklearn; print(numpy.__version__, sklearn.__version__)"
```

That last line should print `2.5.2 1.9.0`. The install step is the only
part of this lab that needs the network.

## File structure

```
day-143-the-machine-learning-workflow/
├── README.md                      this file
├── metadata.yml                   how the lab was actually executed
├── security.md                    what the lab touches, and what it does not
├── troubleshooting.md             every failure this lab is known to produce
├── requirements/
│   ├── README.md                  why the pins are exact
│   └── requirements.txt           numpy, scikit-learn, pytest
├── starter/
│   ├── 00_brief.md                read this first
│   ├── workflow_lib.py            complete machinery — not the exercise
│   ├── test_workflow_lib.py       four machinery checks, already solved
│   └── test_workflow_claims.py    thirteen exercises, each a skip to replace
├── examples/
│   ├── workflow_lib.py            identical to the starter copy
│   ├── test_workflow_lib.py       the same four machinery checks
│   ├── test_workflow_claims.py    the reference solutions
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

`starter/workflow_lib.py` and `examples/workflow_lib.py` are byte
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
| `.venv/bin/pytest starter -q` | Runs your work: four machinery checks pass, thirteen exercises skip until you write them |
| `.venv/bin/pytest examples -q` | Runs the reference solutions — seventeen assertions about the workflow and its ordering |
| `.venv/bin/python3 examples/report_measurements.py` | Recomputes every published number and prints them as one table |
| `bash tests/run_tests.sh` | Fourteen checks: version pins, every claim reproduced without pytest, both suites, the collision, a byte-comparison of the report, a deliberate self-break, the contract at five seeds, and cleanliness |

## Expected output

`bash tests/run_tests.sh` ends with:

```
---------------------------------------------------------------
14 checks, 0 failure(s)
```

and exits 0. `pytest examples -q` reports `17 passed`.
`pytest starter -q` reports `4 passed, 13 skipped` until you start work.

The complete captured runs are in `expected-output/`. The measurement
table is compared byte for byte by check 6, so if a number in the lesson
ever drifts from the code, the harness fails rather than the lesson
quietly becoming wrong.

Read `expected-output/FIELDS.md` before concluding that a mismatch on your
machine is a bug. It separates the results that are exact everywhere — the
step logs, the `StageContractError`, the direction of the inflation, the
two-runs-agree property — from the ones that hold only under the pinned
versions, which includes all four manifest hashes.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` → `14 checks, 0 failure(s)`
   and `exit=0`.
2. `.venv/bin/pytest examples -q` → `17 passed`.
3. `.venv/bin/pytest starter -q` → `4 passed, 13 skipped` before you
   start; `17 passed` when you have finished every exercise.
4. `.venv/bin/python3 examples/report_measurements.py | diff - expected-output/measured-values.txt`
   → no output.
5. Break one assertion in `examples/test_workflow_claims.py` on purpose,
   re-run the harness, and confirm it reports failures and exits non-zero.
   Restore it. A test suite you have never seen fail is not evidence.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints one `ok:` or
`FAIL:` line per check, ends with `N checks, M failure(s)`, and exits
non-zero when `M` is not zero.

The fourteen checks are:

1-3. The installed numpy, scikit-learn and pytest match the pins exactly.
4. Every published claim reproduced directly against `workflow_lib`, with
   no pytest involved — so a broken test file cannot hide a broken
   library, and vice versa.
5. `pytest examples -q` reports 17 passed.
6. `pytest starter -q` reports 4 passed, 13 skipped.
7. The combined `pytest examples starter` invocation aborts, as
   documented.
8. `report_measurements.py` output is byte-identical to the captured
   table.
9-10. A scratch copy of `examples/` passes, then fails with a non-zero
   exit and the failing test named after one assertion is deliberately
   rewritten.
11. The stage contract rejects the out-of-order pipeline at five different
   seeds, not just the one the lesson quotes.
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
created outside this directory.

## Troubleshooting

See `troubleshooting.md`, which covers the missing virtual environment,
`StageContractError` when you did not expect one, the bare `KeyError` you
get with contracts disabled, the `import file mismatch` collision, honest
scores landing below chance, manifest hashes moving with the NumPy pin,
stage line counts changing when you edit the library, and
`LogisticRegression` convergence warnings.

## Security notes

See `security.md`. In short: no network after the install, no credentials,
no `sudo`, and the only write outside this directory is a `mktemp -d`
scratch directory that the harness removes in the same run. It also
explains why the manifest is a supply-chain control and not only a
reproducibility one.

## Extension exercises

1. **Add the missing stages.** This pipeline has no cleaning, no
   monitoring and no deployment stage, which is why exercise 7 reports its
   30 percent as an upper bound. Add a `clean` stage with an honest
   contract, re-measure `stage_source_lines`, and report how the fraction
   moves.
2. **Make the leaky pipeline pass its contracts, dishonestly.** Change
   `select` to declare `requires=("X", "y", "k")` and watch the whole
   thing run green at 0.73. Then write two sentences on what that tells
   you about where the real control lives.
3. **Replace the runner with `sklearn.pipeline.Pipeline`.** Wrap the
   selection and the model in a `Pipeline` and pass it to
   `cross_val_score`. Confirm you get the honest number, and explain in a
   comment which part of `Pipeline` makes the leak impossible.
4. **Find the threshold.** Exercise 4 compares logistic regression at its
   default threshold against balanced class weights. Instead, sweep the
   decision threshold from 0.05 to 0.95 with `predict_proba` and plot
   precision against recall. Report the threshold at which F1 is highest
   and compare it to both models in the table.
5. **Break determinism on purpose.** Remove `random_state` from the
   `StratifiedKFold` in `folds()` and confirm the manifest stops matching
   between runs. Then say what you would have concluded if you had found
   that in a real project without a manifest to tell you.
6. **Extend the manifest.** Hash the selected feature indices as well, and
   check whether the honest pipeline picks the same features at two
   different seeds. Report what you find and what it implies about the
   stability of correlation-based selection.
7. **Cost the ordering error.** At k = 50 the wrong order invents 0.47 of
   accuracy. Find the k at which the inflation is largest by sweeping k
   from 5 to 100, and explain the shape of the curve.

## Navigation

- Lab brief: `starter/00_brief.md`
- Previous lab: `../day-142-supervised-unsupervised-and-reinforcement-learning/`
- Next lab: `../day-144-train-validation-and-test-splits/`
- Week 21 project: `../projects/week-21/`
