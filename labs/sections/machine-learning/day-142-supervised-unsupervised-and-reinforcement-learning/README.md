# Day 142 lab — Three Kinds of Feedback

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Supervised, Unsupervised, and Reinforcement Learning
- **Day number:** 142 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-142-supervised-unsupervised-and-reinforcement-learning
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-142-supervised-unsupervised-and-reinforcement-learning` when the site is running.
<!-- generated-links:end -->

## Purpose

Machine learning is usually introduced as three boxes with algorithms in
them. That framing survives about ten minutes of real work, because the
same algorithm keeps turning up in more than one box and the boxes stop
predicting anything useful.

This lab teaches the taxonomy that does hold up: **the three settings are
three shapes of feedback**, and everything else follows.

- **Supervised** — instructive feedback. Every input arrives with its
  correct output attached, so error is defined per example.
- **Unsupervised** — no feedback at all. There is no correct output, only
  structure, and structure is not unique.
- **Reinforcement** — evaluative and usually delayed feedback. You are
  told how good the action you took was, never what the best action would
  have been, and often only long afterwards.

You will build a ten-armed bandit and a gridworld agent from first
principles in NumPy — no reinforcement-learning library anywhere — so
that the shape of each feedback signal is visible in the code rather than
hidden behind an API. You will measure what never exploring costs, watch
a reward travel backwards through a grid one state per episode, and find
out why a log of a working policy is not a supervised dataset no matter
how many rows it has.

Two of the exercises exist because building this lab went wrong in
instructive ways. Standardising the features before clustering — advice
you will read everywhere — makes k-means measurably worse on iris. And an
agent written the obvious way, with `np.argmax` choosing greedy actions,
reaches the goal in **zero** of three hundred episodes without raising a
single warning. Both are kept, and measured, rather than tidied away.

## Learning objectives

By the end of this lab you will be able to:

1. Classify a problem by its feedback signal rather than by its
   algorithm, and name the one question that decides the most.
2. Demonstrate that cluster identifiers are arbitrary, and that comparing
   them directly to class labels produces a number with no meaning.
3. Read a cluster-versus-class confusion table and say precisely what an
   unsupervised method did and did not recover.
4. Show that preprocessing changes what "the structure" of a dataset is,
   and report a case where the standard advice loses.
5. Explain why inertia can never choose the number of clusters, and show
   a silhouette score choosing the wrong one.
6. Implement epsilon-greedy action-value learning from scratch and
   measure the cost of pure exploitation.
7. Implement tabular Q-learning from scratch and count how far a
   terminal-only reward has propagated after n episodes.
8. Diagnose a silent exploration failure caused by argmax tie-breaking.
9. Explain why logged policy data cannot be treated as a supervised
   dataset, and demonstrate the winner's curse in a concrete measurement.
10. Use unsupervised structure to spend a small label budget better.

## Prerequisites

- Day 141, which established what a model score does and does not mean.
  This lab assumes you will not be impressed by a training accuracy.
- Days 117-118 for the standard error, which is why exercise 9 averages
  over forty splits instead of reporting one.
- Comfort with NumPy array indexing and with reading a pytest failure.
- `python3` 3.11 or newer on your `PATH`. The lab builds its own virtual
  environment; it does not touch your system packages.

No prior exposure to reinforcement learning is assumed. Both agents in
this lab are written out in full, in about thirty lines each.

## Supported operating systems

- macOS (Apple Silicon or Intel) — the capture machine was macOS 26.5.2
  on arm64.
- Linux (any distribution with Python 3.11+ and bash).
- Windows via WSL2. The harness is a bash script and uses `mktemp -d`,
  `find` and process substitution; native PowerShell is not supported.

## Hardware requirements

Any machine that can run Python. The whole harness completes in a few
seconds here, and the heaviest single step is two hundred simulated
bandit runs of a thousand steps each, which is a few million floating
point operations. No GPU. Around 400 MB of disk for the virtual
environment, almost all of it scikit-learn and its scipy dependency.

## Required software

- Python 3.11 or newer (3.14.0 during capture).
- bash 3.2 or newer (3.2.57 during capture — the macOS system bash).
- The three pinned packages in `requirements/requirements.txt`:
  `numpy==2.5.2`, `scikit-learn==1.9.0`, `pytest==9.1.1`.

`find`, `grep`, `awk`, `sed`, `diff` and `mktemp` are used by the
harness and ship with every supported system.

## Free and open-source options

Everything here is free and open source, and there is no paid tier
anywhere in this lab.

- **NumPy** and **scikit-learn** are BSD 3-Clause licensed.
- **pytest** is MIT licensed.
- The **iris measurements** are bundled inside the installed scikit-learn
  package, so no dataset download is needed and no dataset licence
  applies to your use of this lab.

The two agents are deliberately written from scratch rather than pulled
from a reinforcement-learning framework. Gymnasium (the maintained
successor to OpenAI Gym, MIT licensed) and Stable-Baselines3 (MIT) are
the usual free choices when you want more than a gridworld, and the
lesson discusses when reaching for them is the right call. Neither is
installed here and no output from either is reproduced.

## Installation

From the repository root:

```bash
cd labs/sections/machine-learning/day-142-supervised-unsupervised-and-reinforcement-learning
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy, sklearn; print(numpy.__version__, sklearn.__version__)"
```

That last line should print `2.5.2 1.9.0`. The install step is the only
part of this lab that needs the network.

## File structure

```
day-142-supervised-unsupervised-and-reinforcement-learning/
├── README.md                      this file
├── metadata.yml                   how the lab was actually executed
├── security.md                    what the lab touches, and what it does not
├── troubleshooting.md             every failure this lab is known to produce
├── requirements/
│   ├── README.md                  why the pins are exact
│   └── requirements.txt           numpy, scikit-learn, pytest
├── starter/
│   ├── 00_brief.md                read this first
│   ├── feedback_lib.py            complete machinery — not the exercise
│   ├── test_feedback_lib.py       four machinery checks, already solved
│   └── test_feedback_claims.py    fifteen exercises, each a skip to replace
├── examples/
│   ├── feedback_lib.py            identical to the starter copy
│   ├── test_feedback_lib.py       the same four machinery checks
│   ├── test_feedback_claims.py    the reference solutions
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

`starter/feedback_lib.py` and `examples/feedback_lib.py` are byte
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
| `.venv/bin/pytest starter -q` | Runs your work: four machinery checks pass, fifteen exercises skip until you write them |
| `.venv/bin/pytest examples -q` | Runs the reference solutions — nineteen assertions about the three feedback shapes |
| `.venv/bin/python3 examples/report_measurements.py` | Recomputes every published number and prints them as one table |
| `bash tests/run_tests.sh` | Fourteen checks: version pins, every claim reproduced without pytest, both suites, the collision, a byte-comparison of the report, a deliberate self-break, determinism, and cleanliness |

## Expected output

`bash tests/run_tests.sh` ends with:

```
---------------------------------------------------------------
14 checks, 0 failure(s)
```

and exits 0. `pytest examples -q` reports `19 passed`.
`pytest starter -q` reports `4 passed, 15 skipped` until you start work.

The complete captured runs are in `expected-output/`. The measurement
table is compared byte for byte by check 6, so if a number in the lesson
ever drifts from the code, the harness fails rather than the lesson
quietly becoming wrong.

Read `expected-output/FIELDS.md` before concluding that a mismatch on
your machine is a bug. It separates the results that are exact everywhere
— the monotonicity of inertia, the eight-step shortest path, the
zero-of-three-hundred tie-breaking failure — from the ones that hold only
under the pinned versions, which is most of the decimals.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` → `14 checks, 0 failure(s)`
   and `exit=0`.
2. `.venv/bin/pytest examples -q` → `19 passed`.
3. `.venv/bin/pytest starter -q` → `4 passed, 15 skipped` before you
   start; `19 passed` when you have finished every exercise.
4. `.venv/bin/python3 examples/report_measurements.py | diff - expected-output/measured-values.txt`
   → no output.
5. Break one assertion in `examples/test_feedback_claims.py` on purpose,
   re-run the harness, and confirm it reports failures and exits non-zero.
   Restore it. A test suite you have never seen fail is not evidence.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints one `ok:` or
`FAIL:` line per check, ends with `N checks, M failure(s)`, and exits
non-zero when `M` is not zero.

The fourteen checks are:

1-3. The installed numpy, scikit-learn and pytest match the pins exactly.
4. Every published claim reproduced directly against `feedback_lib`, with
   no pytest involved — so a broken test file cannot hide a broken
   library, and vice versa.
5. `pytest examples -q` reports 19 passed.
6. `pytest starter -q` reports 4 passed, 15 skipped.
7. The combined `pytest examples starter` invocation aborts, as
   documented.
8. `report_measurements.py` output is byte-identical to the captured
   table.
9-10. A scratch copy of `examples/` passes, then fails with a non-zero
   exit and the failing test named after one assertion is deliberately
   rewritten.
11. The gridworld and bandit reproduce exactly at a fixed seed and differ
   at different seeds.
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
version-pin failures, the `import file mismatch` collision, the exercise
7 agent that never reaches the goal, bandit numbers that differ on
another NumPy, and the deliberately non-monotone curve in exercise 9.

## Security notes

See `security.md`. In short: no network after the install, no
credentials, no `sudo`, and the only write outside this directory is a
`mktemp -d` scratch directory that the harness removes in the same run.

## Extension exercises

1. **Make the bandit non-stationary.** Let each arm's mean drift by a
   small Gaussian step every pull. The incremental-mean update in
   `run_bandit` weights all history equally and will lag badly; replace
   `1/count` with a constant step size and measure the difference.
2. **Optimistic initial values.** Initialise the bandit's estimates to
   +5 instead of 0 and run with `epsilon=0`. Measure the optimal-action
   rate. Explain why a purely greedy agent now explores anyway, and what
   that trick costs on a non-stationary problem.
3. **Break the gridworld's tie-breaking on purpose.** Run exercise 7's
   failing configuration with `epsilon` at 0.4, 0.6 and 0.8 and find the
   value at which the biased random walk starts reaching the goal.
   Report the smallest ε that works.
4. **Add a step cost.** Give every non-goal transition a reward of −0.01
   and re-run. Measure whether the learned path is still eight steps and
   how the number of valued states changes. Explain the difference.
5. **Evaluate the log honestly.** Exercise 8 shows a log naming the wrong
   arm. Implement inverse-propensity weighting — divide each logged
   reward by the probability the logging policy had of choosing that arm
   — and measure whether it recovers the right answer at seed 1. Report
   what it costs in variance.
6. **Spend the label budget better still.** Exercise 9 labels one row per
   k-means cluster. Try labelling the *two* rows furthest from each
   centroid instead, at the same total budget of six, and measure whether
   representative or boundary examples are worth more.
7. **Break the clustering deliberately.** Find a preprocessing step that
   makes k-means agree with the species *better* than raw features do,
   and report the adjusted Rand index you achieved. Then say honestly how
   you would have chosen it without the labels.

## Navigation

- Lab brief: `starter/00_brief.md`
- Previous lab: `../day-141-what-machine-learning-is-and-is/`
- Next lab: `../day-143-the-machine-learning-workflow/`
- Week 21 project: `../projects/week-21/`
