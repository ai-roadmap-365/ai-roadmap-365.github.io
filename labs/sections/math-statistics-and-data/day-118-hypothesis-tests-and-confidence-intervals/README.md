# Day 118 lab — Tests You Can Defend

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Hypothesis Tests and Confidence Intervals
- **Day number:** 118 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-118-hypothesis-tests-and-confidence-intervals
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-118-hypothesis-tests-and-confidence-intervals` when the site is running.
<!-- generated-links:end -->

## Purpose

A p-value answers a far narrower question than almost everyone treats it
as answering. This lab builds the machinery of a hypothesis test and a
confidence interval from scratch, checks every claim two ways, and spends
real simulation effort proving the two most common ways this machinery
gets misused in practice: checking a metric dashboard repeatedly and
stopping at the first "significant" result (peeking), and checking many
metrics at once without correcting for it (multiple comparisons).

The centrepiece is exercise 2: build 10,000 nominal-95% confidence
intervals from a population with a KNOWN true mean, and count how many
actually contain it. The measured coverage -- not a textbook sentence
about it -- is the proof that "95% confidence" means something precise
about the *procedure*, not about any single interval.

Every exercise follows the same design as Days 113-117: **compute
everything two ways and assert they agree** -- exact where a formula
exists (the two-sample z-test, the exact family-wise error rate), seeded
simulation otherwise, with tolerances derived from a standard error rather
than guessed.

## Learning objectives

By the end you will be able to:

- Build a two-sample z-test and a confidence interval from `math.erf`
  alone, and state precisely what a p-value is and is not: P(data this
  extreme | null true), never P(null true | data).
- Measure, by building 10,000 real intervals, what "95% confidence"
  actually means -- a property of the interval-building procedure, not a
  probability statement about one fixed interval.
- Demonstrate the test/interval duality: a two-sided test at level alpha
  rejects the null value exactly when the (1 - alpha) interval excludes
  it, with zero exceptions.
- Build a permutation test from scratch, with no distributional
  assumption, and compare it against the z-test where the normal
  approximation does and does not hold well.
- Derive and confirm, by exact arithmetic and by simulation, that twenty
  independent alpha=0.05 tests carry a 64% chance of at least one false
  positive, and that a Bonferroni correction pulls that back to about 5%.
- Compute statistical power and explain why it depends on effect size, n,
  and alpha together -- so "found nothing" without a power figure is not
  evidence of absence.
- Demonstrate that the same tiny relative difference can be "not
  significant" at a small n and "significant" at an enormous one, with the
  underlying effect size completely unchanged.
- Measure, by simulation under a true null, how much testing after every
  batch of new data and stopping at the first p < 0.05 inflates the real
  false-positive rate past the nominal alpha.

## Prerequisites

- Day 113 -- probability rules and Monte Carlo error shrinking as
  `1/sqrt(n)`.
- Day 114 -- random variables, expectation, variance, and
  `numpy.random.Generator`.
- Day 115 -- Bayes' theorem and the base-rate error this lab's p-value
  section names explicitly.
- Day 117 -- the sampling distribution, the standard error, and the
  bootstrap built from scratch, all reused here directly.
- Comfort with NumPy arrays and basic vectorised operations.
- Days 71-74 -- running pytest and reading its skip-versus-fail output.
- Day 43 -- `python3 -m venv` and installing a package with `pip`.

## Supported operating systems

- macOS -- run and captured here (macOS 26.5.2, Apple Silicon, arm64).
- Linux -- the same commands apply unchanged. Not run here.
- Windows -- use the Windows Subsystem for Linux and follow the Linux
  instructions, or Git Bash with `.venv\Scripts\python.exe` in place of
  `.venv/bin/python3`. Not run here; `troubleshooting.md` says so plainly.

## Hardware requirements

Anything that runs Python. The heaviest single computation is exercise
2's 10,000 confidence intervals over a 300-observation sample each --well
under a second. Roughly 60 MB of disk for the virtual environment, almost
all of it NumPy.

## Required software

- `python3` -- 3.14.0 here.
- `numpy` 2.5.2 and `pytest` 9.1.1, installed into a lab-local virtual
  environment from `requirements/requirements.txt`.
- `bash` -- 3.2.57 here, for the test harness.

## Free and open-source options

Both dependencies are free and open source and there is no paid tier of
anything in this lab. NumPy is distributed under the BSD 3-Clause licence
and pytest under the MIT licence. No account, no key, no signup, personally
or commercially.

`scipy.stats.ttest_ind` and `scipy.stats.norm.interval` do exercises 1 and
2's core work for you in one call each, and **are not installed here, so
no output from them is reproduced anywhere** in this lab or its lesson --
both are described from their documentation. `statsmodels.stats.multitest`
likewise is not installed and not run; the lesson describes it from
documentation only.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-118-hypothesis-tests-and-confidence-intervals
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Expect `2.5.2`. That is the only time this lab needs the network.

## File structure

```
.
├── README.md                                     this file
├── metadata.yml                                   how the lab was actually run, and when
├── requirements/
│   ├── README.md                                  why each package is here, its licence, and what scipy would add
│   └── requirements.txt                           numpy==2.5.2, pytest==9.1.1
├── starter/                                        your work goes here
│   ├── 00_brief.md                                 the nine exercises, in order
│   ├── conftest.py                                 makes this directory's modules the ones its tests import
│   ├── dataset.py                                  populations, parameters and tolerances — read it, do not change it
│   ├── inference.py                                all nine exercises — functions to write
│   └── test_starter.py                             your running score; unattempted work skips
├── examples/                                       the reference, to read after you have tried
│   ├── conftest.py                                 the same import guard
│   ├── dataset.py                                  the data, and every tolerance with its derivation
│   ├── inference.py                                the finished testing and interval machinery
│   ├── 01_two_sample_z_test.py                     the z-test, checked against a hand computation
│   ├── 02_coverage.py                              the centrepiece: 10,000 intervals, measured coverage
│   ├── 03_duality.py                               reject at alpha <=> the interval excludes the null, exactly
│   ├── 04_permutation_test.py                      no distributional assumption, checked against the z-test
│   ├── 05_multiple_comparisons.py                  1 - 0.95^20 = 0.6415, confirmed, then Bonferroni-corrected
│   ├── 06_power.py                                 power rises with n and with effect size
│   ├── 07_effect_size_vs_n.py                      the same tiny effect: not significant, then significant
│   ├── 08_peeking.py                               stopping at the first p<0.05 inflates the false-positive rate
│   ├── 09_bootstrap_vs_normal_ci.py                two roads to the same interval, checked against each other
│   └── test_reference.py                           22 tests over real values and real exceptions
├── tests/
│   └── run_tests.sh                                the bash harness: 32 checks, exits non-zero on any failure
├── expected-output/                                captured from real runs on 2026-08-19
│   ├── FIELDS.md                                   what may legitimately differ on your machine
│   ├── 01-two-sample-z-test.txt
│   ├── 02-coverage.txt
│   ├── 03-duality.txt
│   ├── 04-permutation-test.txt
│   ├── 05-multiple-comparisons.txt
│   ├── 06-power.txt
│   ├── 07-effect-size-vs-n.txt
│   ├── 08-peeking.txt
│   └── 09-bootstrap-vs-normal-ci.txt
├── troubleshooting.md
└── security.md
```

## How to run

Read `starter/00_brief.md` first. Then work, checking yourself as you go:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `1 passed, 15 skipped`. A skip means
"not attempted"; a failure means "attempted and wrong", and prints both
your answer and the real one.

Afterwards, read the reference -- each script prints its working and
asserts every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_two_sample_z_test.py
../.venv/bin/python3 02_coverage.py
../.venv/bin/python3 03_duality.py
../.venv/bin/python3 04_permutation_test.py
../.venv/bin/python3 05_multiple_comparisons.py
../.venv/bin/python3 06_power.py
../.venv/bin/python3 07_effect_size_vs_n.py
../.venv/bin/python3 08_peeking.py
../.venv/bin/python3 09_bootstrap_vs_normal_ci.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `inference.py` and
`dataset.py` from beside themselves.

Then the full harness:

```bash
bash tests/run_tests.sh
echo "exit=$?"
```

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 -m venv .venv` | Creates a virtual environment inside the lab, so nothing here can affect the rest of your machine. `rm -rf .venv` is a complete undo. |
| `.venv/bin/pip install -r requirements/requirements.txt` | Installs numpy 2.5.2 and pytest 9.1.1. The one command that uses the network. |
| `.venv/bin/pytest starter -q` | Your running score. Unattempted exercises skip; wrong answers fail with both values printed. |
| `01_two_sample_z_test.py` | A two-sample z-test built from `math.erf`, checked against an independent hand computation. |
| `02_coverage.py` | 10,000 nominal-95% confidence intervals from a known population; measures how many actually cover the true mean. |
| `03_duality.py` | Across hundreds of datasets, confirms the test rejects at alpha exactly when the interval excludes the null. |
| `04_permutation_test.py` | Shuffles labels to build a null distribution with no distributional assumption; compares to the z-test. |
| `05_multiple_comparisons.py` | The exact 64.15% family-wise error rate for 20 tests, confirmed by simulation, then Bonferroni-corrected to ~4.9%. |
| `06_power.py` | Power as a function of n and effect size, checked against a direct simulation of the test. |
| `07_effect_size_vs_n.py` | A fixed 0.5% relative difference: not significant at n=30, significant at n=100,000. |
| `08_peeking.py` | Checking every 10 observations and stopping at the first p<0.05, under a true null, measures the real false-positive rate. |
| `09_bootstrap_vs_normal_ci.py` | The bootstrap interval and the normal-approximation interval, checked against each other. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 22 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 32-check harness: versions, every script, both suites, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
32 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `22 passed`, and an untouched
starter with `1 passed, 15 skipped`.

The result worth recognising before you meet it, from exercise 5:

```
P(at least one false positive among 20 independent alpha=0.05 tests) = 1 - (1-0.05)^20 = 0.6415
Simulated over 20000 families: 0.6435
Bonferroni-corrected per-test alpha: 0.05/20 = 0.0025
Simulated family-wise rate WITH Bonferroni: 0.0515
Analytic Bonferroni family-wise rate: 0.0488
```

`expected-output/FIELDS.md` records exactly which captured numbers are
sampled and will differ, within their stated tolerance, on your machine.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `32 checks, 0 failure(s).`
   and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `22 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `16 passed`
   once you have finished, and never prints a failure you have not been
   shown.
4. Each of the nine reference scripts ends with a line starting `OK:`.
5. `find . -path ./.venv -prune -o -type d -name '__pycache__' -print`
   prints nothing after a full run.

## Tests

`tests/run_tests.sh` runs 32 checks in six sections:

1. **Versions** -- reads the installed numpy and compares it against
   `requirements/requirements.txt`, and confirms it is NumPy 2 or later.
2. **The nine reference scripts** -- each must exit 0 and print an `OK:`
   line confirming every one of its internal assertions held.
3. **The reference pytest suite** -- must exit 0, report no failures, and
   have collected at least 18 tests, so a collection error cannot pass as
   success.
4. **The starter suite** -- must exit 0 on an untouched checkout with
   skips rather than failures; and auto-discovering both suites at once
   (running `pytest` with no path argument from the lab directory) must
   report the same skip count as `pytest starter` alone, which is a real
   hazard here because both directories contain modules called
   `inference` and `dataset`.
5. **A deliberate failure** -- the harness re-runs script 05 (multiple
   comparisons) with its expected exact family-wise error rate
   temporarily swapped for a wrong one, and asserts the re-run reports the
   named failure and exits non-zero. A green suite proves nothing until
   you have watched it go red.
6. **A clean disk** -- no `__pycache__` and no `.pytest_cache` outside
   `.venv`, and no source file that opens a network connection.

Before section 1, the harness clears any `__pycache__` and `.pytest_cache`
that an **earlier** command left behind, pruning `.venv` as it goes. This
matters more than it sounds. The README above tells you to run
`.venv/bin/pytest starter -q`, and that command legitimately writes
`starter/__pycache__` and `.pytest_cache`. Without the pre-run clear,
section 6 would then report those as litter -- failing you for following
the instructions in this file. Clearing them at the start makes the final
check measure what *this* run left behind.

The harness was confirmed to exit 0 on a fresh lab-local `.venv` created by
the documented setup commands, and to correctly report a non-zero exit and
a named failure when section 5 deliberately breaks one assertion -- and,
separately, when a real bug was introduced directly into `inference.py`'s
`two_sample_z_test` during development, the harness caught it too (10 of
32 checks failed), confirming section 5 is not the only thing standing
between a real bug and a green run. `.venv` is the documented setup, not a
stray file, and nothing in the suite treats it as one or deletes anything
inside it.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: resets your work
```

The lab's own commands leave none of the first two behind; section 6 of
the harness fails if they appear. It deliberately does not look inside
`.venv`, because the bytecode caches shipped with NumPy and pytest are
theirs, not yours.

## Troubleshooting

See `troubleshooting.md`. It covers wrong-directory import errors, the
starter tests that keep skipping because a function still returns `None`,
the small-n coverage shortfall this lab's choice of `n=300` is meant to
avoid, why a permutation-test p-value can never read as exactly zero, the
`__pycache__` search that must prune `.venv`, and the import collision the
two `conftest.py` files prevent. All of them were hit while building this
lab or are named by a test.

## Security notes

See `security.md`. In short: this lab computes and prints. It writes no
files, opens no connection after the one-time install, needs no
credentials and no `sudo`, and all the data is invented. Three points
there are worth carrying away: a p-value answers a narrower question than
most people act on it as answering, peeking at a live dashboard is not a
hypothetical failure mode but the default behaviour of watching one, and
multiple comparisons need a family-wise correction built in from the
start, not bolted on once the false-positive rate looks suspicious.

## Extension exercises

1. **Build a one-sided test.** `p_from_z_two_sided` doubles the upper-tail
   probability; write a one-sided variant and confirm that, for the same
   data, a two-sided test at alpha=0.05 and a one-sided test at
   alpha=0.025 in the predicted direction reject on exactly the same
   datasets.
2. **Vary the number of looks in the peeking exercise.** Repeat exercise 8
   with `PEEK_MAX_BATCHES` at 1, 2, 5, 10 and 20, and tabulate how the
   false-positive rate grows with the number of looks. At one look it
   should sit close to the nominal alpha -- confirm that as a control case.
3. **Implement the Holm-Bonferroni step-down correction** and compare its
   family-wise error rate and its power (fraction of TRUE effects it still
   detects) against plain Bonferroni on a family of tests where some
   nulls are false.
4. **Measure how power responds to unequal group sizes.** Extend
   `power_two_sample_z` to accept `n_a` and `n_b` separately, and find how
   much power is lost by moving from `n_a = n_b = 100` to `n_a = 150,
   n_b = 50` at the same total sample size.
5. **Build a sequential test with a fixed error-rate guarantee** (for
   example, an alpha-spending approach) and confirm by simulation, the
   same way exercise 8 does, that its false-positive rate under repeated
   looking stays near the nominal alpha where the naive peeking procedure
   did not.

## Navigation

- Previous day: Day 117 — Sampling and the Central Limit Theorem
- Next day: Day 119 — Analyzing an Experiment End to End
- Week 17: Probability and Statistics
- Section: Mathematics, Statistics and Data
