# Day 114 lab — Distributions You Can Sample

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Random Variables and Distributions
- **Day number:** 114 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-114-random-variables-and-distributions
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-114-random-variables-and-distributions` when the site is running.
<!-- generated-links:end -->

## Purpose

A random variable is the step that turns outcomes into numbers you can do
arithmetic on -- a *function* from a sample space to the reals -- and that
single shift is what makes expectation, variance and every loss function in
machine learning possible. Day 113 counted outcomes. This lab builds the
machinery that measures them.

**The opening failure is one almost everyone gets wrong on the first
guess.** Two fair dice summed together look, at a glance, roughly
even-handed across 2 through 12. They are not remotely: 7 is exactly **six
times** as likely as 2 or 12. Exercise 1 enumerates the 36-outcome sample
space and turns that gut feeling into an exact `fractions.Fraction`
probability mass function, and the ratio is not close to 6 -- it is exactly
6, by counting.

Every exercise in this lab follows the same design as Day 113: **compute
everything two ways and assert they agree** -- exact enumeration with
`Fraction` where the answer is rational, seeded simulation otherwise, with
tolerances derived from a standard error rather than guessed. From there
the lab builds outward through the cdf as a running total, expectation and
variance measured two ways, the sharp asymmetry between linearity of
expectation (holds even for dependent variables, exactly) and variance
(does not, unless the covariance term vanishes), Jensen's inequality in its
simplest form, an inverse-CDF sampler built from scratch for both a
discrete pmf and the exponential distribution, the Poisson distribution
emerging as the limit of a Binomial, and the single most persistent
misconception in the subject: a probability density can exceed 1, because
it is not a probability.

## Learning objectives

By the end you will be able to:

- Build the probability mass function of a random variable by enumeration,
  as an exact `fractions.Fraction`, and read a probability off it directly.
- Build the cumulative distribution function as the pmf's running total,
  and use a cdf difference to read an interval probability with no
  re-summing.
- Compute expectation and variance from their definitions and confirm both
  against a large seeded simulation, with a tolerance derived from the
  standard error of the mean.
- State and demonstrate that linearity of expectation holds even for
  DEPENDENT random variables, with no independence assumption anywhere.
- State and demonstrate that variance is NOT additive under dependence, and
  compute the exact covariance correction that restores the equality.
- State Jensen's inequality in its simplest form, `E[X^2] >= (E[X])^2`, and
  show the gap is exactly the variance.
- Explain `Var[aX + b] = a^2 * Var[X]` and why the additive constant `b`
  disappears entirely.
- Describe the Bernoulli, Binomial, Geometric, Poisson, Uniform,
  Exponential and Normal distributions well enough to pick the right one
  for a situation, state its parameters, and compute its mean and
  variance.
- Build an inverse-CDF sampler from scratch for an arbitrary discrete
  distribution, and an exponential sampler as `-ln(U) / lambda`, and
  confirm both against NumPy's own generator.
- Demonstrate numerically that a Binomial(n, lambda/n) distribution
  converges to a Poisson(lambda) distribution as n grows, by measuring a
  shrinking maximum pmf gap.
- Explain why a probability density can legitimately exceed 1, using
  Uniform(0, 0.5) as a concrete, checkable example.

## Prerequisites

- Day 113 -- sample spaces, events, the addition and complement rules,
  independence versus mutual exclusivity, conditional probability, the law
  of total probability, and Monte Carlo estimation with `numpy.random`.
  This lab builds on all of it and does not repeat it.
- Comfort with Python dictionaries, `fractions.Fraction`, and basic
  arithmetic.
- Days 71-74 -- running pytest and reading its skip-versus-fail output.
- Day 43 -- `python3 -m venv` and installing a package with `pip`.

## Supported operating systems

- macOS -- run and captured here (macOS 26.5.2, Apple Silicon, arm64).
- Linux -- the same commands apply unchanged. Not run here.
- Windows -- use the Windows Subsystem for Linux and follow the Linux
  instructions, or Git Bash with `.venv\Scripts\python.exe` in place of
  `.venv/bin/python3`. Not run here; `troubleshooting.md` says so plainly.

## Hardware requirements

Anything that runs Python. The largest computation this lab performs is a
200,000-draw inverse-CDF sample and a pair of 50,000-draw exponential
samples -- a few hundred thousand random draws in total, finished in well
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

Exercises 1, 2, 4, 5, 6, 9 and 10 need only `fractions` and `math` from the
standard library and do not touch NumPy at all. Only exercises 3, 7 and 8
need `numpy.random.Generator`, and `requirements/README.md` shows the
standard-library substitution using `random.Random` if NumPy is
unavailable.

`scipy.stats` does related work and considerably more -- its
`rv_continuous`/`rv_discrete` interface is the shape every named
distribution in the lesson's table would map onto -- and is **not
installed here, so no output from it is reproduced anywhere** in this lab
or its lesson. The lesson's Tools section describes it from its
documentation.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-114-random-variables-and-distributions
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
│   ├── README.md                                  why each package is here, its licence, and the no-install path
│   └── requirements.txt                           numpy==2.5.2, pytest==9.1.1
├── starter/                                        your work goes here
│   ├── 00_brief.md                                 the ten exercises, in order
│   ├── conftest.py                                 makes this directory's modules the ones its tests import
│   ├── dataset.py                                  the sample spaces, parameters and tolerances — read it, do not change it
│   ├── distributions.py                            exercises 1, 2, 3, 4, 5, 6, 9, 10 — functions to write
│   ├── sampling.py                                 exercises 7, 8 — functions to write
│   ├── answers.py                                  eighteen predictions
│   └── test_starter.py                             your running score; unattempted work skips
├── examples/                                       the reference, to read after you have tried
│   ├── conftest.py                                 the same import guard
│   ├── dataset.py                                  the data, and every tolerance with its derivation
│   ├── distributions.py                            the finished pmf/cdf/expectation/variance/named-distribution functions
│   ├── sampling.py                                 the finished from-scratch samplers and the max-gap statistic
│   ├── 01_pmf_of_a_sum.py                          the two-dice-sum pmf, and how far from uniform it is
│   ├── 02_cdf_from_pmf.py                          the cdf as a running total
│   ├── 03_expectation_and_variance.py              by definition versus a large seeded simulation
│   ├── 04_linearity_with_dependence.py             E[X+Y] = E[X]+E[Y], exactly, for a dependent pair
│   ├── 05_variance_is_not_additive.py              Var[X+Y] != Var[X]+Var[Y] for that same pair
│   ├── 06_jensens_inequality.py                    E[X^2] > (E[X])^2, and the gap is the variance
│   ├── 07_inverse_cdf_discrete_sampler.py          a from-scratch sampler for an arbitrary pmf
│   ├── 08_exponential_from_scratch.py              -ln(U)/lambda versus NumPy's own, and a hand-written max-gap statistic
│   ├── 09_poisson_as_binomial_limit.py             the Binomial-to-Poisson convergence, measured
│   ├── 10_density_above_one.py                     Uniform(0, 0.5) has density 2 and still integrates to 1
│   └── test_reference.py                           69 tests over real values and real exceptions
├── tests/
│   └── run_tests.sh                                the bash harness: 63 checks, exits non-zero on any failure
├── expected-output/                                captured from real runs on 2026-08-17
│   ├── FIELDS.md                                   what may legitimately differ on your machine
│   ├── 01-pmf-of-a-sum.txt
│   ├── 02-cdf-from-pmf.txt
│   ├── 03-expectation-and-variance.txt
│   ├── 04-linearity-with-dependence.txt
│   ├── 05-variance-is-not-additive.txt
│   ├── 06-jensens-inequality.txt
│   ├── 07-inverse-cdf-discrete-sampler.txt
│   ├── 08-exponential-from-scratch.txt
│   ├── 09-poisson-as-binomial-limit.txt
│   ├── 10-density-above-one.txt
│   ├── reference-tests.txt
│   ├── starter-progress.txt
│   └── test-run.txt
├── troubleshooting.md
└── security.md
```

## How to run

Read `starter/00_brief.md` first. Then work, checking yourself as you go:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `2 passed, 43 skipped`. A skip means
"not attempted"; a failure means "attempted and wrong", and prints both
your answer and the real one. When it prints `45 passed`, you are
finished.

Afterwards, read the reference -- each script prints its working and
asserts every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_pmf_of_a_sum.py
../.venv/bin/python3 02_cdf_from_pmf.py
../.venv/bin/python3 03_expectation_and_variance.py
../.venv/bin/python3 04_linearity_with_dependence.py
../.venv/bin/python3 05_variance_is_not_additive.py
../.venv/bin/python3 06_jensens_inequality.py
../.venv/bin/python3 07_inverse_cdf_discrete_sampler.py
../.venv/bin/python3 08_exponential_from_scratch.py
../.venv/bin/python3 09_poisson_as_binomial_limit.py
../.venv/bin/python3 10_density_above_one.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `distributions.py`,
`sampling.py` and `dataset.py` from beside themselves.

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
| `01_pmf_of_a_sum.py` | Enumerates the 36-outcome sample space, builds the sum's pmf, and shows 7 is exactly six times as likely as 2. |
| `02_cdf_from_pmf.py` | Accumulates the pmf into a cdf and confirms `F(7) - F(6) == pmf[7]` exactly. |
| `03_expectation_and_variance.py` | E[Y] and Var[Y] by definition, then measured from 200,000 simulated dice rolls with `statistics` and NumPy side by side. |
| `04_linearity_with_dependence.py` | X = first die, Y = the sum. `E[X+Y] == E[X]+E[Y]` exactly, despite Y depending on X directly. |
| `05_variance_is_not_additive.py` | The same dependent pair: `Var[X+Y] != Var[X]+Var[Y]`, but equals `Var[X]+Var[Y]+2*Cov(X,Y)` exactly. |
| `06_jensens_inequality.py` | `E[X^2] > (E[X])^2` for a die, and the gap equals `Var[X]` exactly. |
| `07_inverse_cdf_discrete_sampler.py` | A from-scratch inverse-CDF sampler applied to the dice-sum pmf, checked against the exact pmf and against itself for reproducibility. |
| `08_exponential_from_scratch.py` | `-ln(U)/rate` versus `Generator.exponential`, compared on sample mean and with a hand-written max-gap statistic. |
| `09_poisson_as_binomial_limit.py` | Binomial(n, 2/n) versus Poisson(2) at four values of n, showing the maximum pmf gap shrink monotonically. |
| `10_density_above_one.py` | Uniform(0, 0.5)'s density is exactly 2 -- above 1 -- while its numeric integral over the support is exactly 1. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 69 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 63-check harness: versions, every script, both suites, twenty-eight individual values, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
63 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `69 passed`, and an untouched
starter with `2 passed, 43 skipped`.

The opening result, the block worth recognising before you meet it:

```
  P(Y= 7) = 1/6      0.1667
  P(Y= 2) = 1/36     0.0278
  ratio of most likely to least likely: 6 = 6
```

`expected-output/FIELDS.md` records exactly which captured numbers are
exact rational arithmetic (identical anywhere) and which are sampled (and
so will differ, within their stated tolerance, on your machine).

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `63 checks, 0 failure(s).`
   and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `69 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `45 passed` once
   you have finished, and never prints a failure you have not been shown.
4. Each of the ten reference scripts ends with `every assertion held.`
5. `find . -path ./.venv -prune -o -type d -name '__pycache__' -print`
   prints nothing after a full run.

## Tests

`tests/run_tests.sh` runs 63 checks in seven sections:

1. **Versions** -- reads the installed numpy and compares it against
   `requirements/requirements.txt`, and confirms it is NumPy 2 or later.
2. **The ten reference scripts** -- each must exit 0 and print that every
   one of its internal assertions held.
3. **The reference pytest suite** -- must exit 0, report no failures, and
   have collected at least 60 tests, so a collection error cannot pass as
   success.
4. **The starter suite** -- must exit 0 on an untouched checkout with
   skips rather than failures; and collecting both suites at once must not
   turn any of those skips into passes, which is a real hazard here
   because both directories contain modules called `distributions`,
   `sampling`, `dataset` and `answers`.
5. **Twenty-eight individual values** -- the pmf ratio, the cdf identity,
   both expectation/variance pairs, the linearity and non-additivity
   results with their exact covariance correction, the Jensen gap, the
   discrete sampler's tolerance and reproducibility, the exponential
   sampler's mean and max-gap statistic, the Poisson-limit convergence,
   and the density-above-one result.
6. **A deliberate failure** -- the harness temporarily swaps the
   variance-non-additivity assertion for the wrong belief that variance
   IS additive, re-runs the reference suite, and asserts that the run
   reports exactly one failure and a non-zero exit -- then restores the
   file. A green suite proves nothing until you have watched it go red.
7. **A clean disk** -- no `__pycache__` and no `.pytest_cache` outside
   `.venv`, and no source file that opens a network connection.

Before section 1, the harness clears any `__pycache__` and `.pytest_cache`
that an **earlier** command left behind, pruning `.venv` as it goes. This
matters more than it sounds. The README above tells you to run
`.venv/bin/pytest starter -q`, and that command legitimately writes
`starter/__pycache__` and `.pytest_cache`. Without the pre-run clear,
section 7 would then report those as litter -- failing you for following
the instructions in this file. Clearing them at the start makes the final
check measure what *this* run left behind.

The harness was confirmed to exit 0 on a fresh lab-local `.venv` created
by the documented setup commands, and to correctly report a non-zero exit
and exactly one failure when section 6 deliberately breaks one assertion.
Separately, a reference script (`01_pmf_of_a_sum.py`) was manually edited
to assert a wrong value, the full harness was re-run and confirmed to fail
with a non-zero exit and two named failures, and the file was restored and
the harness re-confirmed green. `.venv` is the documented setup, not a
stray file, and nothing in the suite treats it as one or deletes anything
inside it.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: resets your work
```

The lab's own commands leave none of the first two behind; section 7 of
the harness fails if they appear. It deliberately does not look inside
`.venv`, because the bytecode caches shipped with NumPy and pytest are
theirs, not yours.

## Troubleshooting

See `troubleshooting.md`. It covers wrong-directory import errors, the
starter tests that keep skipping because a `raise NotImplementedError`
survived below your code, `Fraction`-versus-`float` return-type mistakes,
the variance-non-additivity result coming out equal when it should not,
seeds that do not reproduce, the `__pycache__` search that must prune
`.venv`, and the import collision the two `conftest.py` files prevent. All
of them were hit while building this lab or are named by a test.

## Security notes

See `security.md`. In short: this lab computes and prints. It writes no
files, opens no connection after the one-time install, needs no
credentials and no `sudo`, and all the data is invented. Three points
there are worth carrying away: a sampled quantity is only as trustworthy
as the seed and tolerance behind it, and both should be visible; a density
greater than 1 is not a bug; and the from-scratch samplers exist to
demystify a library's random number generator, not to replace it.

## Extension exercises

1. **Build a Binomial pmf sampler from scratch** using the same
   inverse-CDF method as exercise 7, and confirm its empirical mean and
   variance against the closed-form `n*p` and `n*p*(1-p)` for several
   values of `n` and `p`.
2. **Sample a Geometric distribution from scratch.** Its pmf is
   `P(K=k) = (1-p)^(k-1) * p` for `k = 1, 2, 3, ...`. Either build the
   inverse-CDF sampler over an infinite support by truncating at a `k`
   where the tail probability is negligible, or derive and use the
   closed-form inverse: `k = ceil(ln(1-U) / ln(1-p))`.
3. **Measure the Normal distribution's density exceeding 1.** The
   standard Normal's density at `x=0` is `1/sqrt(2*pi) ~= 0.399`, which is
   below 1 -- but for a Normal with a small enough standard deviation, the
   peak density exceeds 1. Find the standard deviation at which the peak
   density first exceeds 1, and confirm the total integral is still 1
   with a numeric integral of your own.
4. **Extend the Poisson-as-Binomial-limit exercise to a different
   lambda.** Repeat exercise 9 with `lambda = 10` instead of `lambda = 2`,
   and compare how quickly the gap shrinks -- does a larger lambda need a
   larger n to reach the same gap, or a smaller one?
5. **Build a rejection sampler and compare its efficiency to inverse-CDF.**
   Implement rejection sampling for the Uniform(0, 0.5) density from
   exercise 10 (trivial, since it is already uniform, but instructive),
   then for a triangular density on the same support, and measure what
   fraction of proposed samples are accepted.

## Navigation

- Previous day: Day 113 — Probability: Events, Rules, and Intuition
- Next day: Day 115 — Bayes' Theorem
- Week 17: Probability and Statistics
- Section: Mathematics, Statistics and Data
