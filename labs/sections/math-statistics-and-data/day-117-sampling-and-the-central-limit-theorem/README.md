# Day 117 lab — Sampling You Can Trust

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Sampling and the Central Limit Theorem
- **Day number:** 117 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-117-sampling-and-the-central-limit-theorem
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-117-sampling-and-the-central-limit-theorem` when the site is running.
<!-- generated-links:end -->

## Purpose

A sample statistic is itself a random variable, with its own distribution
and its own spread. Measure the average session length across 30 users
today and you might get 42 seconds; measure it again from a fresh sample of
30 users from the exact same population and you might get 51 seconds.
Neither measurement is wrong. Nothing was done incorrectly. Reporting
either one as *the* answer, without its variability, is the single most
common quantitative mistake this lab exists to prevent.

This lab builds, from scratch and checked against real numbers, the
machinery that makes a sample statistic trustworthy: the sampling
distribution itself, the standard error and its `1/sqrt(n)` law (the same
law Day 113's Monte Carlo error obeyed, named properly this time), the
central limit theorem's flattening of a skewed population's sampling
distribution, the Cauchy distribution's flat refusal to obey any of it, the
sharp and often-missed difference between sampling bias and sampling error,
the bootstrap built with nothing but resampling and a standard deviation,
and the quiet way dependence between observations makes the textbook
formula for the standard error understate the truth.

Every exercise follows the same design as Days 113-116: **compute
everything two ways and assert they agree** -- exact where a formula
exists, seeded simulation otherwise, with tolerances derived from the
standard error rather than guessed.

## Learning objectives

By the end you will be able to:

- Build the sampling distribution of a statistic directly, by literally
  repeating an experiment many times, and explain why a sample statistic is
  itself a random variable with its own mean and spread.
- State and demonstrate the standard error's `1/sqrt(n)` law: quadrupling
  the sample size roughly halves the standard error, not quarters it.
- Demonstrate the central limit theorem numerically, by measuring the
  skewness of the sampling distribution of the mean fall toward zero as `n`
  grows, starting from a population that looks nothing like a bell curve.
- State the Cauchy distribution's counterexample precisely: the mean of `n`
  Cauchy draws is itself Cauchy distributed, with the same spread, for
  every `n` -- and explain why this means the central limit theorem's
  finite-variance condition is a real constraint, not decoration.
- Distinguish sampling bias from sampling error and explain, with a
  measurement, why more data shrinks the second and not the first.
- Build the bootstrap from scratch -- resample with replacement, recompute
  a statistic, read its standard error off the spread -- and apply it to a
  statistic (the median) with no simple closed-form standard error.
- Demonstrate that dependence between observations makes the naive
  `sample_std / sqrt(n)` formula UNDERSTATE the true standard error, and
  explain why that is a worse failure mode than an honest formula being
  merely imprecise.
- Compute the standard error of a model evaluation accuracy from the
  binomial formula, and use it to judge whether a leaderboard margin is a
  real improvement or noise.

## Prerequisites

- Day 113 -- probability rules and Monte Carlo error shrinking as
  `1/sqrt(n)`. This lab names that law properly and builds on it directly.
- Day 114 -- random variables, expectation, variance, the named
  distributions, and inverse-CDF sampling with `numpy.random.Generator`.
- Day 116 -- descriptive statistics, including the bootstrap's general
  shape, applied here to a specific standard-error question.
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

Anything that runs Python. The heaviest single computation is 50,000 trials
of a 320-observation sample, drawn and averaged in one vectorised call --
well under a second. Roughly 60 MB of disk for the virtual environment,
almost all of it NumPy.

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

`scipy.stats` provides `bootstrap` and `sem` (standard error of the mean)
functions that do exercises 6 and part of exercise 1 for you, and **is not
installed here, so no output from it is reproduced anywhere** in this lab
or its lesson -- it is described from its documentation. `pandas`'
`DataFrame.sample` is likewise not installed and not run; the lesson
describes it from documentation only.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-117-sampling-and-the-central-limit-theorem
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
│   ├── sampling.py                                 all nine exercises — functions to write
│   └── test_starter.py                             your running score; unattempted work skips
├── examples/                                       the reference, to read after you have tried
│   ├── conftest.py                                 the same import guard
│   ├── dataset.py                                  the data, and every tolerance with its derivation
│   ├── sampling.py                                 the finished sampling, bootstrap and standard-error functions
│   ├── 01_sampling_distribution.py                 a statistic has its own distribution, its own mean and spread
│   ├── 02_the_sqrt_n_law.py                        quadrupling n halves the standard error
│   ├── 03_clt_from_a_skewed_population.py          the sampling distribution's skewness falls toward zero
│   ├── 04_the_cauchy_counterexample.py             Exponential shrinks by ~10x; Cauchy does not shrink at all
│   ├── 05_bias_does_not_shrink.py                  a biased sampler's error stays flat as n grows 100x
│   ├── 06_bootstrap_from_scratch.py                resample, recompute, read off the spread — for the mean and the median
│   ├── 07_dependence_inflates_se.py                autocorrelation makes the naive formula understate the truth
│   ├── 08_the_evaluation_margin.py                 a 0.3-point accuracy gap is well inside one standard error
│   ├── 09_reproducibility.py                       same seed, identical results; different seed, compatible results
│   └── test_reference.py                           19 tests over real values and real exceptions
├── tests/
│   └── run_tests.sh                                the bash harness: 32 checks, exits non-zero on any failure
├── expected-output/                                captured from real runs on 2026-08-17
│   ├── FIELDS.md                                   what may legitimately differ on your machine
│   ├── 01-sampling-distribution.txt
│   ├── 02-the-sqrt-n-law.txt
│   ├── 03-clt-from-a-skewed-population.txt
│   ├── 04-the-cauchy-counterexample.txt
│   ├── 05-bias-does-not-shrink.txt
│   ├── 06-bootstrap-from-scratch.txt
│   ├── 07-dependence-inflates-se.txt
│   ├── 08-the-evaluation-margin.txt
│   └── 09-reproducibility.txt
├── troubleshooting.md
└── security.md
```

## How to run

Read `starter/00_brief.md` first. Then work, checking yourself as you go:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `1 passed, 12 skipped`. A skip means
"not attempted"; a failure means "attempted and wrong", and prints both
your answer and the real one.

Afterwards, read the reference -- each script prints its working and
asserts every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_sampling_distribution.py
../.venv/bin/python3 02_the_sqrt_n_law.py
../.venv/bin/python3 03_clt_from_a_skewed_population.py
../.venv/bin/python3 04_the_cauchy_counterexample.py
../.venv/bin/python3 05_bias_does_not_shrink.py
../.venv/bin/python3 06_bootstrap_from_scratch.py
../.venv/bin/python3 07_dependence_inflates_se.py
../.venv/bin/python3 08_the_evaluation_margin.py
../.venv/bin/python3 09_reproducibility.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `sampling.py` and
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
| `01_sampling_distribution.py` | Builds the sampling distribution of the mean and checks its own mean and spread against theory. |
| `02_the_sqrt_n_law.py` | Four sample sizes, each 4x the last; the standard error ratio should sit near 2.0 at every step. |
| `03_clt_from_a_skewed_population.py` | The sampling distribution's skewness, measured at five values of n, falling monotonically. |
| `04_the_cauchy_counterexample.py` | Exponential vs Cauchy sample means, compared by IQR at n=10 and n=1,000. |
| `05_bias_does_not_shrink.py` | A sampler restricted to the upper half of the population, compared against an unbiased one across a 100x growth in n. |
| `06_bootstrap_from_scratch.py` | Resample-and-recompute for the mean (checked against a formula) and the median (checked for sanity). |
| `07_dependence_inflates_se.py` | An AR(1) series' true standard error (by replication) versus the naive formula. |
| `08_the_evaluation_margin.py` | The binomial standard error for a 91.4%-on-500 accuracy figure, and what it says about a 0.3-point margin. |
| `09_reproducibility.py` | Same seed twice; a different seed once more, compared for statistical compatibility. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 19 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 32-check harness: versions, every script, both suites, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
32 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `19 passed`, and an untouched
starter with `1 passed, 12 skipped`.

The result worth recognising before you meet it, from exercise 4:

```
Exponential(scale=1.0): IQR of the mean at n=10 = 0.4212, at n=1000 = 0.0428
  ratio = 9.85  (100x more data, expected shrink ~ sqrt(100) = 10x)

standard Cauchy: IQR of the mean at n=10 = 2.0035, at n=1000 = 1.9561
  ratio = 1.02  (100x more data, expected shrink: NONE)
```

`expected-output/FIELDS.md` records exactly which captured numbers are
sampled and will differ, within their stated tolerance, on your machine.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `32 checks, 0 failure(s).`
   and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `19 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `13 passed`
   once you have finished, and never prints a failure you have not been
   shown.
4. Each of the nine reference scripts ends with `every assertion held.`
5. `find . -path ./.venv -prune -o -type d -name '__pycache__' -print`
   prints nothing after a full run.

## Tests

`tests/run_tests.sh` runs 32 checks in six sections:

1. **Versions** -- reads the installed numpy and compares it against
   `requirements/requirements.txt`, and confirms it is NumPy 2 or later.
2. **The nine reference scripts** -- each must exit 0 and print that every
   one of its internal assertions held.
3. **The reference pytest suite** -- must exit 0, report no failures, and
   have collected at least 15 tests, so a collection error cannot pass as
   success.
4. **The starter suite** -- must exit 0 on an untouched checkout with
   skips rather than failures; and collecting both suites at once must not
   turn any of those skips into passes, which is a real hazard here
   because both directories contain modules called `sampling` and
   `dataset`.
5. **A deliberate failure** -- the harness re-runs script 08 (the
   evaluation-margin calculation) with its expected standard error
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
a named failure when section 5 deliberately breaks one assertion. `.venv`
is the documented setup, not a stray file, and nothing in the suite treats
it as one or deletes anything inside it.

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
tolerance failures that mean a seed or a sample size was changed, the
`__pycache__` search that must prune `.venv`, and the import collision the
two `conftest.py` files prevent. All of them were hit while building this
lab or are named by a test.

## Security notes

See `security.md`. In short: this lab computes and prints. It writes no
files, opens no connection after the one-time install, needs no
credentials and no `sudo`, and all the data is invented. Two points there
are worth carrying away: a spread measure computed on a heavy-tailed sample
can be meaningless even when it looks like a normal number, and a naive
standard-error formula applied to dependent data does not fail loudly --
it fails by understating exactly the risk you asked it to quantify.

## Extension exercises

1. **Vary the AR(1) autocorrelation strength.** Repeat exercise 7 with
   `phi` at 0.0, 0.3, 0.7 and 0.95, and plot (or tabulate) how the
   true-to-naive standard error ratio grows with `phi`. At `phi = 0` the
   two should agree closely -- confirm that as a control case.
2. **Build a Student's t-distribution sampler and find where it stops
   looking like the Cauchy distribution.** The Cauchy distribution is the
   t-distribution with 1 degree of freedom. Using `rng.standard_t(df)`,
   repeat exercise 4 at `df` in `{1, 2, 5, 30}` and find the smallest `df`
   at which the sample mean's IQR shrinks by at least 5x from n=10 to
   n=1000.
3. **Bootstrap a ratio statistic.** Apply `bootstrap_standard_error` to a
   dataset of paired values and a statistic that computes the ratio of
   their sums, `sum(a) / sum(b)`, which has no simple closed-form standard
   error either.
4. **Measure the standard error of a proportion at the boundary.** Compute
   `binomial_standard_error` for `phat` approaching 0 or 1 (say, 0.01,
   0.5, 0.99) at a fixed `n`, and confirm numerically that the standard
   error is largest at `phat = 0.5` and shrinks toward the extremes.
5. **Simulate a stratified sample and compare it to the biased sampler.**
   Build a sampler that draws proportionally from sub-populations rather
   than only above the median, and compare its error-versus-n curve to
   both the unbiased and biased samplers in exercise 5.

## Navigation

- Previous day: Day 116 — Descriptive Statistics That Don't Lie
- Next day: Day 118 — Hypothesis Tests and Confidence Intervals
- Week 17: Probability and Statistics
- Section: Mathematics, Statistics and Data
