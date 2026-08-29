# Day 115 lab — Bayes You Can Trust

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Bayes’ Theorem
- **Day number:** 115 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-115-bayes-theorem
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-115-bayes-theorem` when the site is running.
<!-- generated-links:end -->

## Purpose

Bayes' theorem is the law of total probability read backwards, and human
intuition fails it so reliably that the failure has a name. A test is 99%
sensitive and 99% specific. The condition affects 1 person in 1,000. You
test positive. Almost everyone — including, in published studies, most
physicians asked the same question — answers "about 99%". The true answer
is close to 9%. This lab derives that number exactly, confirms it three
independent ways, and then builds outward through the odds form, sequential
updating, a case where the naive "multiply the likelihood ratios" move
badly overstates confidence, and a from-scratch spam classifier that
confronts the two things every Naive Bayes tutorial glosses over: Laplace
smoothing and log space.

Same design principle as Days 113 and 114: **compute everything two
independent ways and assert they agree** — exact rational arithmetic with
`fractions.Fraction` wherever the answer is rational, seeded simulation
otherwise, with tolerances derived from the standard error of a
proportion.

## Learning objectives

By the end you will be able to:

- Derive `P(condition | positive)` exactly with Bayes' theorem, and explain
  precisely why the intuitive "the test is 99% accurate, so I'm 99% likely
  to have it" answer is wrong.
- Rebuild the same computation as a natural-frequencies count over 100,000
  people, and see the same arithmetic that was opaque as percentages become
  obvious as integers.
- Confirm an exact posterior by seeded simulation of a large population,
  with a tolerance derived from the standard error of a proportion.
- Explain why the posterior is strictly increasing in prevalence, and
  identify the prevalence at which the naive "99%" guess becomes the
  actual right answer.
- State and use the odds form of Bayes' theorem — posterior odds equal
  prior odds times the likelihood ratio — and explain why it isolates a
  piece of evidence's worth independently of the prior.
- Update a belief sequentially across two different pieces of evidence, and
  explain why the order those updates arrive in never changes the result.
- Construct a case where two pieces of "independent" evidence are actually
  correlated, and show that treating them as independent overstates
  confidence rather than merely producing a different number.
- Build a Naive Bayes classifier from scratch with Laplace smoothing, and
  explain what a single unsmoothed zero-probability word does to an
  otherwise well-evidenced classification.
- Explain why a real classifier is built in log space rather than as a
  literal product of probabilities, and demonstrate the underflow that
  makes the difference visible.
- Say plainly what "naive" names in Naive Bayes, and why the classifier
  works despite the assumption being false.

## Prerequisites

- Day 113 — sample spaces, events, the addition and complement rules, and
  especially the law of total probability, which is this lesson's
  denominator run forward.
- Day 114 — random variables and distributions (referenced by number only;
  this lab does not depend on its files).
- Comfort with `fractions.Fraction` and basic Python.
- Day 46 — floating-point representation, directly relevant to exercise 9.
- Days 71–74 — running pytest and reading its output.
- Day 43 — `python3 -m venv` and installing a package with `pip`.

## Supported operating systems

- macOS — run and captured here (macOS 26.5.2, Apple Silicon, arm64).
- Linux — the same commands apply unchanged. Not run here.
- Windows — use the Windows Subsystem for Linux and follow the Linux
  instructions, or Git Bash with `.venv\Scripts\python.exe` in place of
  `.venv/bin/python3`. Not run here; `troubleshooting.md` says so plainly.

## Hardware requirements

Anything that runs Python. The largest computation this lab performs is a
seeded simulation of 2,000,000 people in exercise 3 — a few million random
draws, finished in well under a second. Roughly 60 MB of disk for the
virtual environment, almost all of it NumPy.

## Required software

- `python3` — 3.14.0 here.
- `numpy` 2.5.2, installed into a lab-local virtual environment, used only
  by exercise 3's population simulation.
- `pytest` 9.1.1, from the same virtual environment.
- `bash` — 3.2.57 here, for the test harness.

## Free and open-source options

Both dependencies are free and open source and there is no paid tier of
anything in this lab. NumPy is distributed under the BSD 3-Clause licence
and pytest under the MIT licence. No account, no key, no signup,
personally or commercially.

Eight of the nine exercises (1, 2, 4, 5, 6, 7, 8, 9) need only `fractions`,
`math` and `collections` from the standard library and do not touch NumPy
at all. Only exercise 3's population simulation needs
`numpy.random.Generator`, and `requirements/README.md` shows the
standard-library substitution using `random.Random` if NumPy is
unavailable.

`scipy.stats`, scikit-learn's `MultinomialNB`, and PyMC/Stan do related and
more advanced work, and are **not installed here, so no output from any of
them is reproduced anywhere** in this lab or its lesson. The lesson's
Tools section describes each from its documentation.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-115-bayes-theorem
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Expect `2.5.2`. That is the only time this lab needs the network.

## File structure

```
.
├── README.md                                    this file
├── metadata.yml                                 how the lab was actually run, and when
├── requirements/
│   ├── README.md                                why each package is here, its licence, and the no-install path
│   └── requirements.txt                         numpy==2.5.2, pytest==9.1.1
├── starter/                                      your work goes here
│   ├── 00_brief.md                               the nine exercises, in order
│   ├── conftest.py                               makes this directory's modules the ones its tests import
│   ├── dataset.py                                the scenario, the corpus and every tolerance — read it, do not change it
│   ├── bayes.py                                  exercises 1, 4, 5, 6, 7 — Bayes' theorem functions to write
│   ├── simulate.py                               exercise 3 — the population simulation to write
│   ├── naive_bayes.py                            exercises 8, 9 — the classifier and log-space functions to write
│   ├── answers.py                                fifteen predictions
│   └── test_starter.py                           your running score; unattempted work skips
├── examples/                                     the reference, to read after you have tried
│   ├── conftest.py                               the same import guard
│   ├── dataset.py                                the data, and every tolerance with its derivation
│   ├── bayes.py                                  the finished Bayes'-theorem functions
│   ├── simulate.py                                the finished population simulation
│   ├── naive_bayes.py                             the finished classifier and log-space functions
│   ├── 01_opening_posterior.py                    the opening failure, derived exactly
│   ├── 02_natural_frequencies.py                  the same arithmetic, counted instead of multiplied
│   ├── 03_simulation.py                           a 2,000,000-person seeded confirmation
│   ├── 04_prevalence_sweep.py                     the base rate decides the answer
│   ├── 05_odds_form.py                            posterior odds = prior odds x likelihood ratio
│   ├── 06_sequential_updating.py                  two tests, both orders, one identical answer
│   ├── 07_correlated_tests.py                     the honest caveat, made concrete
│   ├── 08_naive_bayes_smoothing.py                a from-scratch classifier and the one-word veto
│   ├── 09_log_space.py                            the underflow that makes log space non-optional
│   └── test_reference.py                          71 tests over real values and real exceptions
├── tests/
│   └── run_tests.sh                               the bash harness: 53 checks, exits non-zero on any failure
├── expected-output/                               captured from real runs on 2026-08-17
│   ├── FIELDS.md                                  what may legitimately differ on your machine
│   ├── 01-opening-posterior.txt
│   ├── 02-natural-frequencies.txt
│   ├── 03-simulation.txt
│   ├── 04-prevalence-sweep.txt
│   ├── 05-odds-form.txt
│   ├── 06-sequential-updating.txt
│   ├── 07-correlated-tests.txt
│   ├── 08-naive-bayes-smoothing.txt
│   ├── 09-log-space.txt
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

On an untouched checkout that prints `2 passed, 38 skipped`. A skip means
"not attempted"; a failure means "attempted and wrong", and prints both
your answer and the real one. When it prints `40 passed`, you are
finished.

Afterwards, read the reference — each script prints its working and
asserts every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_opening_posterior.py
../.venv/bin/python3 02_natural_frequencies.py
../.venv/bin/python3 03_simulation.py
../.venv/bin/python3 04_prevalence_sweep.py
../.venv/bin/python3 05_odds_form.py
../.venv/bin/python3 06_sequential_updating.py
../.venv/bin/python3 07_correlated_tests.py
../.venv/bin/python3 08_naive_bayes_smoothing.py
../.venv/bin/python3 09_log_space.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `bayes.py`,
`simulate.py`, `naive_bayes.py` and `dataset.py` from beside themselves.

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
| `01_opening_posterior.py` | Derives `P(condition \| positive) = 99/1098 ≈ 0.0902` term by term, and asserts it is not the naive `0.99`. |
| `02_natural_frequencies.py` | The same computation as a 100,000-person table: 99 true positives against 999 false positives. |
| `03_simulation.py` | Confirms the exact posterior by simulating and counting 2,000,000 people. |
| `04_prevalence_sweep.py` | Sweeps prevalence from 1-in-100,000 to 1-in-2, and shows the posterior strictly increasing, reaching exactly 0.99 at 1-in-2. |
| `05_odds_form.py` | Posterior odds = prior odds x likelihood ratio, and converts back to a probability matching exercise 1 exactly. |
| `06_sequential_updating.py` | Two different tests, updated one at a time, in both orders — identical results either way. |
| `07_correlated_tests.py` | Same test run twice on one sample; the naive independent-tests posterior versus the correct correlation-aware one. |
| `08_naive_bayes_smoothing.py` | A tiny spam/ham corpus, classified with and without Laplace smoothing, showing the one-word veto. |
| `09_log_space.py` | 500 factors of 0.01 underflow to exactly 0.0 as a float64 product; the corresponding sum of logs stays finite. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 71 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 53-check harness: versions, every script, both suites, nineteen individual values, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
53 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `71 passed`, and an untouched
starter with `2 passed, 38 skipped`.

The opening failure, worth recognising before you meet it:

```
P(condition | positive) = 99/1098 = 11/122
                         = 0.090164  ~ 0.0902
```

`expected-output/FIELDS.md` records exactly which parts of the captured
output may legitimately differ on your machine — exercise 3's simulated
counts, not the exact `Fraction` results — and includes a correction notice
about a wrong log-space figure this lab does not repeat.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `53 checks, 0 failure(s).`
   and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `71 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `40 passed` once
   you have finished, and never prints a failure you have not been shown.
4. Each of the nine reference scripts ends with `every assertion held.`
5. Your `posterior()` function returns a `Fraction`, never a `float` — an
   assertion comparing it against `Fraction(99, 1098)` must pass exactly,
   not approximately.

## Tests

`tests/run_tests.sh` runs 53 checks in seven sections:

1. **Versions** — reads the installed numpy and compares it against
   `requirements/requirements.txt`, and confirms it is NumPy 2 or later.
2. **The nine reference scripts** — each must exit 0 and print that every
   one of its internal assertions held.
3. **The reference pytest suite** — must exit 0, report no failures, and
   have collected at least 60 tests, so a collection error cannot pass as
   success.
4. **The starter suite** — must exit 0 on an untouched checkout with skips
   rather than failures; and collecting both suites at once must not turn
   any of those skips into passes, which is a real hazard here because
   both directories contain modules called `bayes`, `simulate`,
   `naive_bayes`, `dataset` and `answers`.
5. **Nineteen individual values** — the opening posterior and its rounding,
   the natural-frequency total, the simulation's tolerance check, the
   prevalence sweep's monotonicity and its exact value at prevalence 1/2,
   the odds-form equality, the sequential posterior and its order
   independence, both correlated-test posteriors and their comparison, the
   veto-case classification with and without smoothing, and the underflow
   and log-space results.
6. **A deliberate failure** — the harness temporarily flips one reference
   assertion (the naive-versus-correlated posterior comparison), re-runs
   the reference suite, and asserts that the run reports exactly one
   failure and a non-zero exit — then restores the file. A green suite
   proves nothing until you have watched it go red.
7. **A clean disk** — no `__pycache__` and no `.pytest_cache` outside
   `.venv`, and no source file that opens a network connection.

Before section 1, the harness clears any `__pycache__` and `.pytest_cache`
that an **earlier** command left behind, pruning `.venv` as it goes. This
matters more than it sounds. The README above tells you to run
`.venv/bin/pytest starter -q`, and that command legitimately writes
`starter/__pycache__` and `.pytest_cache`. Without the pre-run clear,
section 7 would then report those as litter — failing you for following
the instructions in this file. Clearing them at the start makes the final
check measure what it claims to measure: what *this* run left behind.

The harness was confirmed to exit 0 on a fresh lab-local `.venv` created by
the documented setup commands, and to correctly report a non-zero exit and
exactly one failure when section 6 deliberately breaks one assertion.
Separately, its ability to catch a genuine bug was confirmed by hand:
`dataset.py`'s `OPENING_POSTERIOR_EXACT` constant was temporarily edited to
a wrong value, the full harness reported 7 failures and a non-zero exit,
and the file was restored and the harness re-run clean. `.venv` is the
documented setup, not a stray file, and nothing in the suite treats it as
one or deletes anything inside it.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: resets your work
```

The lab's own commands leave none of the first two behind; section 7 of the
harness fails if they appear. It deliberately does not look inside `.venv`,
because the bytecode caches shipped with NumPy and pytest are theirs, not
yours.

## Troubleshooting

See `troubleshooting.md`. It covers wrong-directory import errors, the
`posterior()` formula's most common mistake (returning the sensitivity
directly instead of dividing by the evidence), `Fraction`-versus-`float`
return-type mistakes, the odds-form's sensitivity/specificity swap, the
correlated-versus-naive posterior comparison flipped, the Naive Bayes veto
case explained, and the import collision the two `conftest.py` files
prevent. All of them were hit while building this lab or are named by a
test.

## Security notes

See `security.md`. In short: this lab computes and prints. It writes no
files, opens no connection after the one-time install, needs no
credentials and no `sudo`, and all the data is invented. Three points there
are worth carrying away: a posterior is only as trustworthy as the prior
and independence assumptions that produced it; a classifier's output is a
posterior, and a model trained on the wrong base rate is confidently wrong
at scale; and a wrong probability calculation looks exactly like a right
one until you check it against an independent method — which is the
entire structure of this lab.

## Extension exercises

1. **The prosecutor's fallacy, made concrete.** Construct a scenario where
   a piece of forensic evidence has `P(evidence | innocent) = 1/1,000,000`,
   and compute `P(innocent | evidence)` given a stated prior probability of
   guilt before the evidence — using Bayes' theorem, not by treating the
   two conditional probabilities as interchangeable. Confirm that a tiny
   `P(evidence | innocent)` does not by itself make `P(innocent |
   evidence)` tiny once the prior is properly accounted for, and write one
   paragraph on why conflating the two directions is called a fallacy
   rather than an approximation.
2. **A three-test sequential update.** Extend exercise 6 to three
   different tests of varying quality, confirm the posterior is identical
   across all six orderings, and find the ordering-invariant quantity
   directly (the product of all three likelihood ratios) rather than
   computing it by brute-force permutation.
3. **Vary the correlation weight continuously.** Sweep
   `correlation_weight` from 0 to 1 in exercise 7's scenario, and confirm
   the correlated posterior is a strictly decreasing function of it — full
   independence (0) gives the naive answer as an upper bound, and full
   correlation (1) gives the single-test posterior as a lower bound, since
   two fully-correlated results are worth no more than one.
4. **Add a third class to the Naive Bayes classifier.** Introduce a
   "newsletter" class alongside spam and ham with its own tiny corpus, and
   confirm `classify_log_space()` still selects correctly among three
   classes — the log-space argmax generalises with no changes beyond
   iterating over more classes.
5. **Measure calibration on invented predictions.** Generate 1,000
   invented "model confidence" values and invented true/false outcomes
   where the model is deliberately overconfident, bucket the confidences,
   and compute the empirical accuracy within each bucket — a direct
   application of this lesson's conditioning-as-restriction idea to the
   AI thread's calibration question.

## Navigation

- Previous day: Day 114 — Random Variables and Distributions
- Next day: Day 116 — Descriptive Statistics That Don't Lie
- Week 17: Probability and Statistics
- Section: Mathematics, Statistics and Data
