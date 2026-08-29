# Day 144 lab — Three Sets, and Why

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Train, Validation, and Test Splits
- **Day number:** 144 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-144-train-validation-and-test-splits
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-144-train-validation-and-test-splits` when the site is running.
<!-- generated-links:end -->

## Purpose

Everybody knows you hold out a test set. Rather fewer people can say why
there are supposed to be *three* sets rather than two, and almost nobody
has seen the number that justifies the third one.

This lab measures it, and then measures the four ways a split goes wrong.

The headline experiment uses candidates with **exactly zero skill** — each
one is a coin flip, a fixed vector of random predictions. Score them on a
validation set, keep whichever wins, and look at what it does on a test
set it never influenced:

| candidates considered | best validation | its test score | optimism |
| --- | --- | --- | --- |
| 1 | 0.4984 | 0.5011 | −0.0028 |
| 10 | 0.5331 | 0.4999 | +0.0332 |
| 100 | 0.5567 | 0.4992 | +0.0575 |
| 1000 | 0.5720 | 0.4992 | +0.0728 |

Read the test column first: **it never moves**. It sits at chance for
every K, because it was never selected on. That is the control, and it is
what makes the validation column mean something.

Now read the validation column. It climbs to 0.5720 on coin flips. Try a
thousand things and the best will look seven points better than chance,
whether or not any of them is any good.

Then four ways a split goes wrong, each measured:

| The mistake | What it cost, here |
| --- | --- |
| not stratifying a rare class | 21 of 500 random splits had a test half with **no positives at all** |
| splitting rows when the unit is a person | **+0.5648** — 0.9760 against 0.4112 |
| shuffling data with a direction in time | +0.0728 on average; shuffling won **20 of 20** times |
| reading a trend off one holdout | one holdout swung **0.19** across seeds; 5-fold swung 0.0325 |

## Learning objectives

By the end of this lab you will be able to:

1. Explain why a validation set and a test set are different objects, in
   terms of a measured quantity rather than a convention.
2. Quantify selection optimism as a function of how many candidates were
   considered, and identify the control that makes the measurement valid.
3. Connect that optimism to the expected maximum of K noise draws, and
   report where the standard closed-form approximation fails.
4. Demonstrate that a random split of a rare class sometimes produces a
   test set on which recall is undefined.
5. Identify when the row is not the unit of independence, and measure what
   ignoring that costs.
6. Split data that has a direction in time correctly, and report the
   effect's size honestly when it varies between datasets.
7. Choose between a single holdout and k-fold cross-validation using the
   measured spread of each.
8. Size a test set before splitting, from the smallest difference you need
   to detect.
9. Enforce a one-evaluation budget on a test set mechanically.

## Prerequisites

- Day 141 for what a score means, Day 142 for the winner's curse — which
  reappears here as selection bias — and Day 143 for stage ordering.
- Days 117-118 for the standard error and the sampling distribution. This
  lab is largely that arithmetic applied to evaluation.
- Day 136 for the forking-paths problem, which is what exercise 1
  measures and what exercise 4's reporting decision avoids committing.
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
are 400 selection replications and 200 cross-validation repeats, which
complete in well under a minute on the capture machine. Around 400 MB of
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
  spot from a seeded generator, so no dataset licence applies to your use
  of this lab.

The splitters used here — `train_test_split`,
`StratifiedShuffleSplit`, `GroupShuffleSplit`, `StratifiedKFold` — are all
part of scikit-learn. `TimeSeriesSplit` covers the chronological case at
project scale and is discussed in the lesson.

## Installation

From the repository root:

```bash
cd labs/sections/machine-learning/day-144-train-validation-and-test-splits
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
day-144-train-validation-and-test-splits/
├── README.md                      this file
├── metadata.yml                   how the lab was actually executed
├── security.md                    what the lab touches, and what it does not
├── troubleshooting.md             every failure this lab is known to produce
├── requirements/
│   ├── README.md                  why the pins are exact
│   └── requirements.txt           numpy, scikit-learn, pytest
├── starter/
│   ├── 00_brief.md                read this first
│   ├── splits_lib.py              complete machinery — not the exercise
│   ├── test_splits_lib.py         four machinery checks, already solved
│   └── test_splits_claims.py      fourteen exercises, each a skip to replace
├── examples/
│   ├── splits_lib.py              identical to the starter copy
│   ├── test_splits_lib.py         the same four machinery checks
│   ├── test_splits_claims.py      the reference solutions
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

`starter/splits_lib.py` and `examples/splits_lib.py` are byte identical on
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
| `.venv/bin/pytest starter -q` | Runs your work: four machinery checks pass, fourteen exercises skip until you write them |
| `.venv/bin/pytest examples -q` | Runs the reference solutions — eighteen assertions about how splits behave |
| `.venv/bin/python3 examples/report_measurements.py` | Recomputes every published number and prints them as one table |
| `bash tests/run_tests.sh` | Fourteen checks: version pins, every claim reproduced without pytest, both suites, the collision, a byte-comparison of the report, a deliberate self-break, three directions re-confirmed at unquoted seeds, and cleanliness |

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
machine is a bug. It separates what is exact everywhere — the
standard-error formula, all 50 people appearing in both halves, every
direction — from what holds only under the pinned versions, which is most
of the decimals.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` → `14 checks, 0 failure(s)`
   and `exit=0`.
2. `.venv/bin/pytest examples -q` → `18 passed`.
3. `.venv/bin/pytest starter -q` → `4 passed, 14 skipped` before you
   start; `18 passed` when you have finished every exercise.
4. `.venv/bin/python3 examples/report_measurements.py | diff - expected-output/measured-values.txt`
   → no output.
5. Break one assertion in `examples/test_splits_claims.py` on purpose,
   re-run the harness, and confirm it reports failures and exits non-zero.
   Restore it. A test suite you have never seen fail is not evidence.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints one `ok:` or
`FAIL:` line per check, ends with `N checks, M failure(s)`, and exits
non-zero when `M` is not zero.

The fourteen checks are:

1-3. The installed numpy, scikit-learn and pytest match the pins exactly.
4. Every published claim reproduced directly against `splits_lib`, with no
   pytest involved — so a broken test file cannot hide a broken library,
   and vice versa.
5. `pytest examples -q` reports 18 passed.
6. `pytest starter -q` reports 4 passed, 14 skipped.
7. The combined `pytest examples starter` invocation aborts, as
   documented.
8. `report_measurements.py` output is byte-identical to the captured
   table.
9-10. A scratch copy of `examples/` passes, then fails with a non-zero
   exit and the failing test named after one assertion is deliberately
   rewritten.
11. Group leakage, selection optimism and stratification are re-confirmed
    at seeds and replication counts the lesson never quotes, so no
    directional claim rests on a single lucky seed.
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
the `import file mismatch` collision, the harness taking a while on slower
machines, a group-aware score below chance, temporal numbers that differ
from the lesson's, `sqrt(2 ln K)` not matching the measurement, sampled
figures moving with the NumPy pin, and `LogisticRegression` convergence
warnings.

## Security notes

See `security.md`. In short: no network after the install, no credentials,
no `sudo`, no write outside this directory except a `mktemp -d` scratch
directory the harness removes in the same run, and everything reversible
with `rm -rf .venv`. It also reads `GatedTestSet` as an access-control
pattern — a one-time budget enforced by the resource itself, whose counter
deliberately does not advance on a refused attempt.

## Extension exercises

1. **Nested cross-validation.** Exercise 1 measures the optimism from
   selecting on a validation set. Implement nested cross-validation — an
   inner loop that selects, an outer loop that scores — and measure
   whether the optimism disappears. Report what it costs in fits.
2. **Find the break-even K.** At what number of candidates does the
   selection optimism exceed the true difference you are trying to detect?
   Compute it for a validation set of 500 rows and a real difference of
   two accuracy points, and say what that implies about hyper-parameter
   sweeps.
3. **Bigger validation set.** Repeat exercise 1 with 2000-row validation
   sets instead of 500. Confirm the optimism scales with the standard
   error rather than staying fixed, and report the ratio.
4. **Repeated k-fold.** Exercise 5 compares one holdout against 5-fold.
   Add repeated 5-fold with ten repetitions and measure how much further
   the spread narrows, and what it costs in fits.
5. **Leave-one-group-out.** Replace `GroupShuffleSplit` in exercise 3 with
   `LeaveOneGroupOut` and report both the mean and the spread across the
   fifty people. Say which is the more honest number to publish.
6. **Make the temporal effect large on purpose.** Exercise 4's effect
   varies by a factor of sixteen. Find what property of a construction
   makes it large — the number of regimes, their length, how different
   consecutive rules are — and report a rule of thumb for when a
   chronological split matters most.
7. **A stricter gate.** Extend `GatedTestSet` to log every attempted
   evaluation with a caller identifier, so a refused attempt leaves a
   trace. Then argue, in two sentences, whether a gate that logs is more
   or less useful than one that simply refuses.

## Navigation

- Lab brief: `starter/00_brief.md`
- Previous lab: `../day-143-the-machine-learning-workflow/`
- Next lab: `../day-145-overfitting-and-underfitting/`
- Week 21 project: `../projects/week-21/`
