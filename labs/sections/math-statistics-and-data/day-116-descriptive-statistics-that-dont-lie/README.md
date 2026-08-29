# Day 116 lab — Statistics That Don't Lie

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Descriptive Statistics That Don’t Lie
- **Day number:** 116 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-116-descriptive-statistics-that-dont-lie
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-116-descriptive-statistics-that-dont-lie` when the site is running.
<!-- generated-links:end -->

## Purpose

A summary statistic is a compression, and every compression discards. This
lab's whole strategy is one sentence: **compute it two ways, or compute
what a single number hides, and show the gap.**

**The opening failure is the one that settles the whole day.** Anscombe's
quartet is four small, real, published datasets that agree — to the
documented precision — on the mean of x, the mean of y, the variance of
both, the correlation, and the fitted regression line. Every summary
statistic a reader currently trusts is identical across all four. Exercise
6 computes that agreement, and then computes three diagnostics the classic
five cannot see, which finally tell the four sets apart, each for a
different structural reason.

From there the lab builds outward through the breakdown point (the median
tolerates half the data being corrupted; the mean's breakdown point is
zero), Bessel's correction measured by simulation rather than asserted,
the fact that "the 75th percentile" is not one number — NumPy alone
documents nine disagreeing conventions — Pearson versus Spearman (a
perfect parabola fools one and not the other), Simpson's paradox (a
treatment that wins every subgroup and loses overall, from the same
table), robust spread under contamination, and standardisation's one
genuinely invariant property: it does not change correlation.

## Learning objectives

By the end you will be able to:

- Compute mean, median and mode from scratch and know precisely when each
  one misleads — including why "average income" reported as a mean is
  usually the wrong number.
- State the breakdown point of the mean (zero) and the median (up to 50%)
  and demonstrate the gap with a concrete corrupted salary list.
- Explain and measure Bessel's correction: why dividing by `n` biases the
  sample variance low by the factor `(n-1)/n`, and why dividing by `n-1`
  fixes it.
- Show that "the 75th percentile" is not a well-defined number by
  computing it under several of NumPy's `method=` conventions and reading
  off genuinely different answers.
- Distinguish Pearson correlation (linear association only) from Spearman
  correlation (monotone association), with a worked case where they
  disagree completely.
- Reproduce Anscombe's quartet, the founding demonstration that identical
  summary statistics can describe entirely different-shaped data.
- Construct and explain Simpson's paradox: a result that reverses when
  subgroups are pooled, purely because of how the subgroups were
  weighted.
- Compare the standard deviation and the median absolute deviation under
  contamination, and quantify how much less the robust measure moves.
- Standardise data to z-scores and prove that doing so changes nothing
  about the correlation between two variables.

## Prerequisites

- Days 113–115 — probability, random variables and Bayes' theorem; this
  lab assumes that vocabulary without repeating it.
- Day 107 — norms and distances, referenced directly by the
  standardisation exercise.
- Comfort with Python lists, basic arithmetic, and reading a `pytest`
  failure message.
- Days 71–74 — running pytest and reading its output.
- Day 43 — `python3 -m venv` and installing a package with `pip`.

## Supported operating systems

- macOS — run and captured here (macOS 26.5.2, Apple Silicon, arm64).
- Linux — the same commands apply unchanged. Not run here.
- Windows — use the Windows Subsystem for Linux and follow the Linux
  instructions, or Git Bash with `.venv\Scripts\python.exe` in place of
  `.venv/bin/python3`. Not run here; `troubleshooting.md` says so plainly.

## Hardware requirements

Anything that runs Python. The largest computation this lab performs is
20,000 repeated samples of size 5 for the Bessel-correction simulation —
100,000 random draws, finished in a fraction of a second. Roughly 60 MB of
disk for the virtual environment, almost all of it NumPy.

## Required software

- `python3` — 3.14.0 here.
- `numpy` 2.5.2 and `pytest` 9.1.1, installed into a lab-local virtual
  environment from `requirements/requirements.txt`.
- `bash` — 3.2.57 here, for the test harness.

## Free and open-source options

Both dependencies are free and open source and there is no paid tier of
anything in this lab. NumPy is distributed under the BSD 3-Clause licence
and pytest under the MIT licence. No account, no key, no signup,
personally or commercially.

Exercises 1, 2, 5, 6, 7 and 9 need only the standard library — `statistics`
and `collections.Counter` — and do not touch NumPy at all. Only exercise 4
needs `numpy.percentile`'s `method=` argument specifically (the standard
library has no equivalent), and exercises 3 and 8 use
`numpy.random.Generator` for simulation, where `requirements/README.md`
shows the standard-library substitution.

`pandas.DataFrame.describe()` and `scipy.stats` do related work and are
**not installed here, so no output from either is reproduced anywhere** in
this lab or its lesson. The lesson's Tools section describes both from
their documentation.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-116-descriptive-statistics-that-dont-lie
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Expect `2.5.2`. That is the only time this lab needs the network.

## File structure

```
.
├── README.md                                       this file
├── metadata.yml                                    how the lab was actually run, and when
├── requirements/
│   ├── README.md                                   why each package is here, its licence, and the no-install path
│   └── requirements.txt                            numpy==2.5.2, pytest==9.1.1
├── starter/                                         your work goes here
│   ├── 00_brief.md                                  the nine exercises, in order
│   ├── conftest.py                                  makes this directory's modules the ones its tests import
│   ├── dataset.py                                   every dataset and tolerance -- read it, do not change it
│   ├── descriptive.py                                exercises 1, 2, 4, 5, 6, 7, 9 -- statistics to write from scratch
│   ├── simulate.py                                   exercises 3, 8 -- simulation to write
│   ├── answers.py                                    seventeen predictions
│   └── test_starter.py                               your running score; unattempted work skips
├── examples/                                        the reference, to read after you have tried
│   ├── conftest.py                                  the same import guard
│   ├── dataset.py                                   the data, and every tolerance with its derivation
│   ├── descriptive.py                                the finished statistics functions
│   ├── simulate.py                                   the finished simulation functions
│   ├── 01_mean_median_mode.py                        mean, median, mode, checked against the statistics module
│   ├── 02_breakdown_point.py                         one corrupted salary: the mean moves, the median does not
│   ├── 03_bessel_correction.py                       divide-by-n bias, measured; divide-by-(n-1), confirmed unbiased
│   ├── 04_percentile_ambiguity.py                     nine NumPy conventions, genuinely different answers
│   ├── 05_pearson_vs_spearman.py                      a parabola fools Pearson; a monotone cubic does not fool Spearman
│   ├── 06_anscombes_quartet.py                         the founding demonstration, reproduced and separated
│   ├── 07_simpsons_paradox.py                          A wins every subgroup, B wins overall, same table
│   ├── 08_robust_spread_under_contamination.py         standard deviation vs. MAD under 3% contamination
│   ├── 09_standardization.py                           z-scores: mean 0, std 1, correlation unchanged
│   └── test_reference.py                               32 tests over real values and real exceptions
├── tests/
│   └── run_tests.sh                                  the bash harness: 55 checks, exits non-zero on any failure
├── expected-output/                                  captured from real runs on 2026-08-17
│   ├── FIELDS.md                                     what may legitimately differ on your machine
│   ├── 01-mean-median-mode.txt
│   ├── 02-breakdown-point.txt
│   ├── 03-bessel-correction.txt
│   ├── 04-percentile-ambiguity.txt
│   ├── 05-pearson-vs-spearman.txt
│   ├── 06-anscombes-quartet.txt
│   ├── 07-simpsons-paradox.txt
│   ├── 08-robust-spread-under-contamination.txt
│   ├── 09-standardization.txt
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

On an untouched checkout that prints `1 passed, 38 skipped`. A skip means
"not attempted"; a failure means "attempted and wrong", and prints both
your answer and the real one. When it prints `39 passed`, you are
finished.

Afterwards, read the reference — each script prints its working and
asserts every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_mean_median_mode.py
../.venv/bin/python3 02_breakdown_point.py
../.venv/bin/python3 03_bessel_correction.py
../.venv/bin/python3 04_percentile_ambiguity.py
../.venv/bin/python3 05_pearson_vs_spearman.py
../.venv/bin/python3 06_anscombes_quartet.py
../.venv/bin/python3 07_simpsons_paradox.py
../.venv/bin/python3 08_robust_spread_under_contamination.py
../.venv/bin/python3 09_standardization.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `descriptive.py`,
`simulate.py` and `dataset.py` from beside themselves.

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
| `01_mean_median_mode.py` | Mean, median and mode from scratch, checked against the `statistics` module, including a multimodal case `statistics.mode()` silently gets wrong. |
| `02_breakdown_point.py` | Replaces a salary list's largest value with an absurd one: the mean moves by over a million dollars, the median moves by exactly $0. |
| `03_bessel_correction.py` | Simulates 20,000 samples of size 5 and measures the divide-by-n estimator's bias against the predicted `(n-1)/n` factor. |
| `04_percentile_ambiguity.py` | Computes the 75th percentile of eight numbers under nine NumPy conventions and shows they disagree. |
| `05_pearson_vs_spearman.py` | Pearson on a symmetric parabola (essentially zero); Spearman on a monotone cubic (exactly 1.0). |
| `06_anscombes_quartet.py` | The published 1973 quartet: five agreeing summary statistics, then three diagnostics that separate the sets. |
| `07_simpsons_paradox.py` | The smallest table where a treatment wins every subgroup and loses overall — both directions verified. |
| `08_robust_spread_under_contamination.py` | 3% contamination: the standard deviation inflates by double digits; the MAD barely moves. |
| `09_standardization.py` | Standardises a sample and confirms mean 0, standard deviation 1, and unchanged correlation. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 32 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 55-check harness: versions, every script, both suites, twenty-one individual values, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
55 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `32 passed`, and an untouched
starter with `1 passed, 38 skipped`.

The breakdown point, the block worth recognising before you meet it:

```
mean before        = 50,777.78
mean after         = 1,155,222.22
mean moved by      = 1,104,444.44
median before      = 50,000.00
median after       = 50,000.00
median moved by    = 0.00
```

`expected-output/FIELDS.md` records exactly which parts of the captured
output may legitimately differ on your machine — the simulated
contamination and Bessel-correction figures, not the exact arithmetic
results — and tabulates the tolerances they are checked against.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `55 checks, 0
   failure(s).` and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `32 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `39 passed`
   once you have finished, and never prints a failure you have not been
   shown.
4. Each of the nine reference scripts ends with `every assertion held.`
5. `find . -path ./.venv -prune -o -type d -name '__pycache__' -print`
   prints nothing after a full run.

## Tests

`tests/run_tests.sh` runs 55 checks in seven sections:

1. **Versions** — reads the installed numpy and compares it against
   `requirements/requirements.txt`, and confirms it is NumPy 2 or later.
2. **The nine reference scripts** — each must exit 0 and print that every
   one of its internal assertions held.
3. **The reference pytest suite** — must exit 0, report no failures, and
   have collected at least 25 tests, so a collection error cannot pass as
   success.
4. **The starter suite** — must exit 0 on an untouched checkout with
   skips rather than failures; and collecting both suites at once must
   not turn any of those skips into passes, which is a real hazard here
   because both directories contain modules called `descriptive`,
   `simulate`, `dataset` and `answers`.
5. **Twenty-one individual values** — the odd list's mean and median, the
   multimodal modes, the breakdown-point mean and median shifts, both
   Bessel-correction checks, the percentile disagreement and the default
   value, Pearson and Spearman on the parabola and the cubic, Anscombe's
   agreement and its separating diagnostics, both directions of Simpson's
   paradox, both contamination multipliers against their floor and
   ceiling, and both standardisation invariants.
6. **A deliberate failure** — the harness temporarily swaps one reference
   assertion for a wrong one, re-runs the reference suite, and asserts
   that the run reports exactly one failure and a non-zero exit — then
   restores the file. A green suite proves nothing until you have watched
   it go red.
7. **A clean disk** — no `__pycache__` and no `.pytest_cache` outside
   `.venv`, and no source file that opens a network connection.

Before section 1, the harness clears any `__pycache__` and
`.pytest_cache` that an **earlier** command left behind, pruning `.venv`
as it goes. This matters more than it sounds. The README above tells you
to run `.venv/bin/pytest starter -q`, and that command legitimately
writes `starter/__pycache__` and `.pytest_cache`. Without the pre-run
clear, section 7 would then report those as litter — failing you for
following the instructions in this file. Clearing them at the start makes
the final check measure what it claims to measure: what *this* run left
behind.

The harness was confirmed to exit 0 on a fresh lab-local `.venv` created
by the documented setup commands, and to correctly report a non-zero exit
and exactly one failure when section 6 deliberately breaks one assertion.
`.venv` is the documented setup, not a stray file, and nothing in the
suite treats it as one or deletes anything inside it.

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
survived below your code, the breakdown-point median that should never
move, the Bessel-correction divisor swap, the percentile convention left
implicit, the `__pycache__` search that must prune `.venv`, and the
import collision the two `conftest.py` files prevent. All of them were
hit while building this lab or are named by a test.

## Security notes

See `security.md`. In short: this lab computes and prints. It writes no
files, opens no connection after the one-time install, needs no
credentials and no `sudo`, and the data is either invented or a cited
published dataset (Anscombe's quartet). Three points there are worth
carrying away: a summary statistic is a claim about what was safe to
discard, and every one is wrong for some dataset; a reported percentile is
not comparable across tools without knowing the convention; and a
subgroup breakdown is not optional when a decision rides on an aggregate.

## Extension exercises

1. **Weighted means and Simpson's paradox.** Extend exercise 7 with a
   third subgroup, choose sizes so the paradox reverses back the other
   way (B wins every subgroup, A wins overall), and explain in one
   paragraph what property of the weights made that possible.
2. **A fifth Anscombe-like dataset.** Construct your own small `(x, y)`
   pair that matches set I's mean, variance, correlation and slope to the
   same precision, but has a visibly different shape from all four
   published sets. Confirm the match with `anscombe_summary()` and
   describe what makes your set structurally different.
3. **Bessel's correction at other sample sizes.** Repeat exercise 3's
   simulation at `n = 2`, `n = 10` and `n = 50`, and confirm the
   divide-by-n bias factor `(n-1)/n` gets closer to 1 (less biased) as
   `n` grows — explain why, in terms of how much "room" the sample mean
   has to fit itself to a small sample versus a large one.
4. **A percentile method that matches your intuition.** Read NumPy's
   `numpy.percentile` documentation for all nine `method=` conventions,
   pick the one whose definition you find most intuitive, and write one
   paragraph on why a dashboard or reporting tool should always state
   which convention it uses.
5. **Trimmed mean.** Implement a trimmed mean (drop the top and bottom
   5% of values, then average what remains) and measure its breakdown
   point empirically against the same corrupted salary list from
   exercise 2 — how much corruption can it absorb before it starts
   moving, compared to the plain mean and the median?

## Navigation

- Previous day: Day 115 — Bayes' Theorem
- Next day: Day 117 — Sampling and the Central Limit Theorem
- Week 17: Probability and Statistics
- Section: Mathematics, Statistics and Data
