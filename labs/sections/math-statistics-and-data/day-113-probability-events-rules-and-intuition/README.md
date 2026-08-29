# Day 113 lab — Probability You Can Count

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Probability: Events, Rules, and Intuition
- **Day number:** 113 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-113-probability-events-rules-and-intuition
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-113-probability-events-rules-and-intuition` when the site is running.
<!-- generated-links:end -->

## Purpose

Probability is bookkeeping about sets, and almost every "paradox" in this
subject is a bookkeeping error you can find. This lab's whole strategy is
one sentence: **when intuition and arithmetic disagree, enumerate — and when
the space is too large to enumerate, simulate.**

Two fair dice give a sample space of 36 equally likely outcomes, small
enough to write out by hand and small enough that a computer can enumerate
it in a fraction of a second. Every exercise in this lab computes something
two independent ways — exact enumeration against a formula, or exact
arithmetic against a simulation — and asserts that they agree. Where the
answer is rational, it is computed with `fractions.Fraction` so the
assertion is exact rather than "close enough".

**The opening failure is the one that founded the subject.** In the 1650s
the Chevalier de Méré believed two bets were equally good: at least one 6 in
4 rolls of one die, and at least one double-six in 24 rolls of two dice. The
reasoning was seductive — a double six is 1/6 as likely, so roll 6x as many
times and it evens out — and it is wrong. The exact answers are
`1 - (5/6)^4 = 0.5177...` and `1 - (35/36)^24 = 0.4914...`. One bet is
favourable to the player; the other is not. Exercise 3 derives both by hand
with the complement rule, then confirms both by simulation.

From there the lab builds outward through the addition rule (and exactly
how the naive shortcut lies), independence versus mutual exclusivity (the
most common conflation in the subject), conditioning as literally throwing
away rows of a table, the law of total probability (which Day 115's Bayes'
theorem runs backwards), and Monte Carlo error scaling — a hundred times the
samples buys a tenth of the error, not a hundredth, because the error falls
like `1/sqrt(n)`.

## Learning objectives

By the end you will be able to:

- Build a sample space by enumeration and read a probability off the exact
  ratio of two counts, using `fractions.Fraction` so the answer has no
  floating-point noise.
- State and apply the addition rule, and show precisely how much a naive sum
  overstates the truth when two events overlap.
- Collapse an "at least one" question to one line with the complement rule,
  and use it to resolve de Méré's paradox exactly.
- Confirm an exact probability by simulation, with a tolerance derived from
  the standard error of a proportion rather than guessed.
- Distinguish independence from mutual exclusivity, and explain why
  mutually exclusive events with non-zero probability are *necessarily*
  dependent.
- Compute a conditional probability by formula and by restricting the
  sample space, and see that these are the same operation.
- Apply the law of total probability across a partition of the sample
  space, verified against a direct enumeration of the combined experiment.
- Demonstrate that Monte Carlo error shrinks like `1/sqrt(n)`, not `1/n`,
  and say why a hundredfold increase in samples buys only a tenfold
  reduction in error.
- Use `numpy.random.default_rng(seed)` correctly, and explain why it is
  preferred over the legacy `numpy.random.seed` global state.
- Explain the gambler's fallacy, the confusion between `P(A|B)` and
  `P(B|A)`, base-rate neglect, and the conjunction fallacy well enough to
  spot each one outside a textbook.

## Prerequisites

- Comfort with Python sets, `itertools.product`, and basic arithmetic on
  fractions.
- No calculus and no statistics beyond counting. This is the first day of
  probability in the course.
- Days 99–112 — the mathematics arc that precedes it, though nothing here
  depends on linear algebra or calculus directly.
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
Monte Carlo sweep of 100,000 simulated dice rolls, repeated across 20 seeds
at four sample sizes — a few hundred thousand random draws in total,
finished in well under a second. Roughly 60 MB of disk for the virtual
environment, almost all of it NumPy.

## Required software

- `python3` — 3.14.0 here.
- `numpy` 2.5.2 and `pytest` 9.1.1, installed into a lab-local virtual
  environment from `requirements/requirements.txt`.
- `bash` — 3.2.57 here, for the test harness.

## Free and open-source options

Both dependencies are free and open source and there is no paid tier of
anything in this lab. NumPy is distributed under the BSD 3-Clause licence
and pytest under the MIT licence. No account, no key, no signup, personally
or commercially.

The six exact-probability exercises (1, 2, 4, 5, 6, 7) need only
`itertools` and `fractions` from the standard library and do not touch
NumPy at all. Only the three simulation exercises (3, 8, 9) need
`numpy.random.Generator`, and `requirements/README.md` shows the
standard-library substitution using `random.Random` if NumPy is
unavailable.

`scipy.stats` does related work — and more, once distributions arrive on
Day 114 — and is **not installed here, so no output from it is reproduced
anywhere** in this lab or its lesson. The lesson's Tools section describes
it from its documentation.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-113-probability-events-rules-and-intuition
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
│   ├── dataset.py                                   the sample space, events, urns and tolerances — read it, do not change it
│   ├── probability.py                               exercises 1, 2, 4, 5, 6, 7 — exact probability functions to write
│   ├── simulate.py                                  exercises 3, 8, 9 — simulation functions to write
│   ├── answers.py                                   eighteen predictions
│   └── test_starter.py                              your running score; unattempted work skips
├── examples/                                        the reference, to read after you have tried
│   ├── conftest.py                                  the same import guard
│   ├── dataset.py                                   the data, and every tolerance with its derivation
│   ├── probability.py                                the finished exact-probability functions
│   ├── simulate.py                                  the finished simulation functions
│   ├── 01_sample_space_and_events.py                 the sample space, events as sets, probability as counting
│   ├── 02_addition_rule.py                           the addition rule and exactly how the naive sum lies
│   ├── 03_de_mere.py                                 de Méré's two bets, exact and simulated — the centrepiece
│   ├── 04_independence_vs_dependence.py               one independent pair, one dependent pair
│   ├── 05_mutual_exclusivity_implies_dependence.py    mutually exclusive events are necessarily dependent
│   ├── 06_conditioning_by_restriction.py              conditioning as throwing away rows
│   ├── 07_law_of_total_probability.py                 two urns, weighted total vs. direct enumeration
│   ├── 08_monte_carlo_error_scaling.py                 error shrinks like 1/sqrt(n), not 1/n
│   ├── 09_reproducibility.py                          same seed, byte-identical results
│   └── test_reference.py                              93 tests over real values and real exceptions
├── tests/
│   └── run_tests.sh                                  the bash harness: 57 checks, exits non-zero on any failure
├── expected-output/                                  captured from real runs on 2026-08-17
│   ├── FIELDS.md                                     what may legitimately differ on your machine
│   ├── 01-sample-space-and-events.txt
│   ├── 02-addition-rule.txt
│   ├── 03-de-mere.txt
│   ├── 04-independence-vs-dependence.txt
│   ├── 05-mutual-exclusivity-implies-dependence.txt
│   ├── 06-conditioning-by-restriction.txt
│   ├── 07-law-of-total-probability.txt
│   ├── 08-monte-carlo-error-scaling.txt
│   ├── 09-reproducibility.txt
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

On an untouched checkout that prints `3 passed, 43 skipped`. A skip means
"not attempted"; a failure means "attempted and wrong", and prints both your
answer and the real one. When it prints `46 passed`, you are finished.

Afterwards, read the reference — each script prints its working and asserts
every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_sample_space_and_events.py
../.venv/bin/python3 02_addition_rule.py
../.venv/bin/python3 03_de_mere.py
../.venv/bin/python3 04_independence_vs_dependence.py
../.venv/bin/python3 05_mutual_exclusivity_implies_dependence.py
../.venv/bin/python3 06_conditioning_by_restriction.py
../.venv/bin/python3 07_law_of_total_probability.py
../.venv/bin/python3 08_monte_carlo_error_scaling.py
../.venv/bin/python3 09_reproducibility.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `probability.py`,
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
| `01_sample_space_and_events.py` | Builds the 36-outcome sample space, defines an event as a filtered subset, and reads `P(sum == 7) = Fraction(1, 6)` off the ratio of two counts. |
| `02_addition_rule.py` | `A = "sum is 7"`, `B = "first die is 6"`. Shows the naive sum overstating the truth by exactly `P(A and B)`, then confirms the true union by counting it directly. |
| `03_de_mere.py` | Both of de Méré's bets, derived exactly with the complement rule and confirmed by 200,000-trial simulations, each within three standard errors. |
| `04_independence_vs_dependence.py` | One pair of dice events that is genuinely independent ("sum is 7" and "first die is 3") and one that is genuinely dependent ("sum is 2" and "first die is 1"). |
| `05_mutual_exclusivity_implies_dependence.py` | A mutually exclusive pair, showing `P(A \| B) = 0 != P(A)` — the sharpest possible form of dependence. |
| `06_conditioning_by_restriction.py` | `P(sum = 8 \| first die is even)` computed by formula and by filtering the sample space, shown to agree exactly. |
| `07_law_of_total_probability.py` | Two urns of different composition, drawn from with a fair coin; the weighted total checked against a direct enumeration of the combined 20-outcome experiment. |
| `08_monte_carlo_error_scaling.py` | Estimates `P(sum == 7)` at four sample sizes four decades apart, averaged over 20 seeds, and shows the error shrinking like `1/sqrt(n)`. |
| `09_reproducibility.py` | The same `default_rng(seed)` gives byte-identical results across two calls; a different seed gives a different, still-close result. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 93 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 57-check harness: versions, every script, both suites, twenty-three individual values, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
57 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `93 passed`, and an untouched
starter with `3 passed, 43 skipped`.

De Méré's two bets, the block worth recognising before you meet it:

```
  bet 1 (one die,  4 rolls):  0.517747  -- above 0.5, favours the player
  bet 2 (two dice, 24 rolls): 0.491404  -- below 0.5, favours the house
```

`expected-output/FIELDS.md` records exactly which parts of the captured
output may legitimately differ on your machine — the simulated values, not
the exact `Fraction` results — and tabulates both tolerances against the
error bounds they were derived from.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `57 checks, 0 failure(s).`
   and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `93 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `46 passed` once
   you have finished, and never prints a failure you have not been shown.
4. Each of the nine reference scripts ends with `every assertion held.`
5. `find . -path ./.venv -prune -o -type d -name '__pycache__' -print`
   prints nothing after a full run.

## Tests

`tests/run_tests.sh` runs 57 checks in seven sections:

1. **Versions** — reads the installed numpy and compares it against
   `requirements/requirements.txt`, and confirms it is NumPy 2 or later.
2. **The nine reference scripts** — each must exit 0 and print that every
   one of its internal assertions held.
3. **The reference pytest suite** — must exit 0, report no failures, and
   have collected at least 80 tests, so a collection error cannot pass as
   success.
4. **The starter suite** — must exit 0 on an untouched checkout with skips
   rather than failures; and collecting both suites at once must not turn
   any of those skips into passes, which is a real hazard here because both
   directories contain modules called `probability`, `simulate`, `dataset`
   and `answers`.
5. **Twenty-three individual values** — the sample space size, the
   addition-rule error and its exact size, both de Méré bets rounded to the
   historical figures and confirmed favourable or not, both simulations
   within tolerance, the independent and dependent pair checks, the mutual
   exclusivity result, the two conditioning methods agreeing exactly, the
   urn total matching a direct enumeration, the Monte Carlo error trend,
   and the reproducibility guarantees.
6. **A deliberate failure** — the harness temporarily swaps one reference
   assertion for a wrong one, re-runs the reference suite, and asserts that
   the run reports exactly one failure and a non-zero exit — then restores
   the file. A green suite proves nothing until you have watched it go red.
7. **A clean disk** — no `__pycache__` and no `.pytest_cache` outside
   `.venv`, and no source file that opens a network connection.

Before section 1, the harness clears any `__pycache__` and `.pytest_cache`
that an **earlier** command left behind, pruning `.venv` as it goes. This
matters more than it sounds. The README above tells you to run
`.venv/bin/pytest starter -q`, and that command legitimately writes
`starter/__pycache__` and `.pytest_cache`. Without the pre-run clear,
section 7 would then report those as litter — failing you for following the
instructions in this file. Clearing them at the start makes the final check
measure what it claims to measure: what *this* run left behind.

The harness was confirmed to exit 0 on a fresh lab-local `.venv` created by
the documented setup commands, and to correctly report a non-zero exit and
exactly one failure when section 6 deliberately breaks one assertion.
`.venv` is the documented setup, not a stray file, and nothing in the suite
treats it as one or deletes anything inside it.

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
starter tests that keep skipping because a `raise NotImplementedError`
survived below your code, `Fraction`-versus-`float` return-type mistakes,
de Méré's exponents swapped between the two bets, mutual exclusivity
confused with independence, the `__pycache__` search that must prune
`.venv`, and the import collision the two `conftest.py` files prevent. All
of them were hit while building this lab or are named by a test.

## Security notes

See `security.md`. In short: this lab computes and prints. It writes no
files, opens no connection after the one-time install, needs no credentials
and no `sudo`, and all the data is invented. Three points there are worth
carrying away: a probability claim is a number with an error bar, and
reporting one without an error bar is a form of overclaiming; randomness
that is not reproducible (the legacy `numpy.random.seed` global) is a
debugging liability rather than a convenience; and a wrong probability
calculation looks exactly like a right one until you check it against an
independent method — which is the entire structure of this lab.

## Extension exercises

1. **Compute the birthday problem.** With 23 people in a room, what is the
   probability that two share a birthday? Derive it with the complement
   rule — 1 minus the probability that all 23 birthdays are distinct — using
   `Fraction`, then confirm it by simulation. The answer is over 50%, and
   most people guess far lower; explain why, in terms of how many *pairs*
   of people there are.
2. **Add a third urn with a non-uniform prior.** Extend exercise 7 so the
   coin is biased 70/30 rather than fair, and add a third urn. Recompute
   the law of total probability and design a combined enumeration that
   still checks it exactly, being careful about what "equally likely"
   means once the prior is not uniform.
3. **Find your own gambler's-fallacy trap.** Simulate 10,000 sequences of
   20 fair-coin flips and, for every flip that follows a run of 4 or more
   heads, record whether the next flip is heads. Confirm the proportion is
   still statistically indistinguishable from 0.5 — the coin has no memory
   — and write one paragraph on why a real gambler at a real table finds
   this so hard to believe.
4. **Build a Monty Hall simulator from these primitives.** Using only
   `random` or `numpy.random.default_rng`, simulate the classic
   three-door problem 100,000 times for both the "stay" and "switch"
   strategies, and confirm the exact 1/3 versus 2/3 split with a
   standard-error tolerance in the same style as exercise 3.
5. **Measure the conjunction fallacy's actual gap.** Construct two events
   where one implies the other (for example, "rolls a 6" and "rolls a 6
   and the sum with a second die exceeds 8"), and confirm by enumeration
   that the more specific event can never have higher probability than the
   general one — the fact the conjunction fallacy violates in human
   judgement, however natural it feels to violate it.

## Navigation

- Previous day: Day 112 — Visualizing Optimization
- Next day: Day 114 — Random Variables and Distributions
- Week 17: Probability and Statistics
- Section: Mathematics, Statistics and Data
