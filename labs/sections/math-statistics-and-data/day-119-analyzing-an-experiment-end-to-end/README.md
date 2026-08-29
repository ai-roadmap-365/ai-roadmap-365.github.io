# Day 119 lab — One Experiment, Start to Finish

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Analyzing an Experiment End to End
- **Day number:** 119 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-119-analyzing-an-experiment-end-to-end
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-119-analyzing-an-experiment-end-to-end` when the site is running.
<!-- generated-links:end -->

## Purpose

Two experiments, same nine-step pipeline, opposite endings. Dataset A is
16,000 rows of a clean, well-run checkout experiment: a real effect, a
trustworthy split, a guardrail that holds. Dataset B is 20,000 rows of an
experiment that *looks* just as clean -- same columns, same nominal design
-- but carries two planted problems: the realized split drifted to 48/52
instead of the planned 50/50, and every one of its three segments shows a
NEGATIVE effect while the pooled number shows a positive one. Nothing about
B's arithmetic is wrong. The process that produced the data is broken in a
way the arithmetic alone cannot see.

This lab builds the nine-step pipeline that catches both problems: load and
validate, check the randomization itself before trusting anything
downstream of it, look at the data before testing it, test the primary
metric with a confidence interval rather than a bare p-value, express the
effect in real units, check a guardrail that can veto a positive result,
report segments without concluding from them, watch what peeking would have
done to a real dataset, and combine everything into one verdict that knows
when to refuse to give one at all.

## Learning objectives

By the end you will be able to:

- Build a sample-ratio mismatch (SRM) check from a chi-squared
  goodness-of-fit test with a closed-form p-value (`math.erfc`), run it
  once over final counts, and explain why it is the single most valuable
  check in this lab and the one most often skipped.
- Report a primary metric's effect as a confidence interval AND an effect
  size in its own units, never as a bare p-value, using the same
  `math.erf`-based normal CDF Day 118 built.
- Detect and flag a Simpson's-paradox-shaped segment reversal -- every
  segment pointing one way, the pooled number pointing the other -- and
  explain why segment analysis must report rather than conclude.
- Demonstrate, on one real dataset walked in arrival order, why a p-value
  crossing below 0.05 partway through data collection is not the same
  evidence as the same p-value at a pre-declared sample size.
- Build a verdict function that ships a clean experiment and REFUSES to
  compute an effect estimate at all once randomization has failed its own
  check -- and explain why that refusal, not a number, is the correct
  output.
- Distinguish "the mean and the median disagree" (Day 116's outliers) from
  "the split is wrong" (Day 119's SRM) from "the segments disagree with the
  pool" (Simpson's paradox) as three separate failure modes with three
  separate checks.

## Prerequisites

- Day 116 -- descriptive statistics, the mean-versus-median divergence
  under outliers, and Simpson's paradox as a phenomenon. This lab measures
  both on real (simulated) data rather than a constructed toy example.
- Day 117 -- the standard error and its `1/sqrt(n)` law, used implicitly in
  every confidence interval this lab computes.
- Day 118 -- hypothesis tests, confidence intervals, the normal CDF built
  from `math.erf`, and the cost of peeking. This lab assumes that
  machinery and applies it to one experiment end to end rather than
  re-deriving it.
- Comfort with the standard library `csv`, `statistics` and `math` modules.
- Days 71-74 -- running pytest and reading its skip-versus-fail output.
- Day 43 -- `python3 -m venv` and installing a package with `pip`.

## Supported operating systems

Developed and verified on macOS (Apple Silicon). Linux should work
identically -- nothing in this lab is platform-specific. Windows: use the
Windows Subsystem for Linux, or Git Bash with `.venv\Scripts\python.exe` in
place of `.venv/bin/python3`; not run here (see `troubleshooting.md`).

## Hardware requirements

Trivial. The larger dataset is 20,000 rows; every exercise runs in well
under a second. No GPU, no meaningful memory or disk footprint beyond the
two CSVs (under 2 MB combined) and a standard Python virtual environment.

## Required software

- Python 3.11 or later (written against 3.14.0).
- `numpy` 2.5.2 and `pytest` 9.1.1, pinned in `requirements/requirements.txt`
  -- see `requirements/README.md` for what each is used for, and note that
  `experiment.py` itself is pure standard library (`csv`, `math`,
  `statistics`); only the data-generation script uses NumPy.

## Free and open-source options

Everything in this lab is free and open source. `scipy.stats` and
`statsmodels` would shorten several functions here considerably and are
described from their public documentation in the lesson's Tools section --
neither is installed or run in this lab; see `requirements/README.md` for
the full breakdown of what is and is not installed, and why.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-119-analyzing-an-experiment-end-to-end
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

## File structure

```
day-119-analyzing-an-experiment-end-to-end/
├── README.md
├── metadata.yml
├── troubleshooting.md
├── security.md
├── requirements/
│   ├── requirements.txt
│   └── README.md
├── data/
│   ├── exp_a.csv          # 16,000 rows -- the clean experiment
│   └── exp_b.csv          # 20,000 rows -- the haunted experiment
├── starter/
│   ├── 00_brief.md
│   ├── dataset.py          # generation parameters, shared reference
│   ├── experiment.py       # nine functions to implement
│   ├── test_starter.py     # your running score
│   └── conftest.py
├── examples/
│   ├── dataset.py
│   ├── generate_data.py    # the seeded script that produced data/*.csv
│   ├── experiment.py       # reference implementation
│   ├── 01_load_and_validate.py ... 09_verdict.py
│   ├── test_reference.py
│   └── conftest.py
├── tests/
│   └── run_tests.sh
└── expected-output/
    ├── 01_load_and_validate.txt ... 09_verdict.txt
    ├── run_tests.txt
    └── FIELDS.md
```

## How to run

```bash
cd examples
../.venv/bin/python3 01_load_and_validate.py
../.venv/bin/python3 02_sample_ratio_mismatch.py
../.venv/bin/python3 03_group_summary.py
../.venv/bin/python3 04_primary_test.py
../.venv/bin/python3 05_effect_size.py
../.venv/bin/python3 06_guardrail.py
../.venv/bin/python3 07_segment_analysis.py
../.venv/bin/python3 08_peeking.py
../.venv/bin/python3 09_verdict.py
cd ..
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

To work the exercises yourself, edit `starter/experiment.py` in place and
re-run `.venv/bin/pytest starter -q` after each function.

## What the commands do

Each numbered script in `examples/` loads one or both of the shipped
datasets, runs one step of the pipeline, prints the real numbers it
computed, and asserts the claim that step exists to prove -- ending with
`<script>.py: every assertion held.` on success. `pytest examples` runs an
independent pytest suite over the same reference implementation.
`pytest starter` runs the same claims against whatever you have written in
`starter/experiment.py`, skipping anything still unimplemented.

## Expected output

See `expected-output/` for the full captured output of every script and of
`tests/run_tests.sh`. In outline: `02_sample_ratio_mismatch.py` reports the
SRM check passing on A (`p_value ≈ 1.0`) and failing on B
(`p_value ≈ 1.5e-8`, well under B's own `alpha=0.001`). `07_segment_analysis.py`
reports all three of B's segments (desktop, mobile, tablet) with a NEGATIVE
lift while B's pooled lift is positive, and `reversal_flagged=True`.
`09_verdict.py` reports `"ship"` for A and `"do not trust this result"`,
`refused=True` for B.

## Validation steps

```bash
bash tests/run_tests.sh; echo "exit=$?"
```

Expect the literal final line `35 checks, 0 failure(s).` and `exit=0`.

## Tests

`tests/run_tests.sh` is the full harness: version checks, all nine
reference scripts, the reference pytest suite, the starter suite's
skip-vs-fail behaviour (checked both on an untouched checkout and against a
temporarily-swapped-in solved copy), a proof that the harness itself can
fail and report it, and a cleanliness check.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv            # optional: removes the lab virtual environment
git checkout -- starter/experiment.py   # optional: reset your work
```

## Troubleshooting

See `troubleshooting.md` for every issue actually hit while building this
lab, including a wrong-direction `srm_check`, a segment-reversal flag that
never trips, and reading arrival order correctly from the CSV.

## Security notes

See `security.md`. In outline: no network access after the one-time
install, no credentials, no files written outside the lab directory, and a
harness check that greps for network calls in the lab's own source.

## Extension exercises

- Add a second guardrail metric (for example, an unsubscribe or refund
  rate) and confirm `verdict()` can be vetoed by either guardrail
  independently, not just the one this lab ships with.
- Rebuild `primary_test`'s confidence interval using the pooled standard
  error instead of the unpooled one, and measure how much the interval's
  width changes on dataset A -- then read `troubleshooting.md`'s note on
  why the two are conventionally kept separate.
- Add a third dataset of your own, `exp_c.csv`, generated with
  `examples/generate_data.py`'s parameters changed so the SRM check passes
  but the guardrail fails -- confirm `verdict()` correctly reports
  `"do not trust this result"` for a reason other than randomization.
- Change `peek_path`'s `checkpoint_every` from 500 to 100 on dataset A and
  describe, in your own words, whether the peeking instability from
  exercise 8 gets more or less pronounced -- and why that direction makes
  sense given what a smaller checkpoint interval means about how little
  data each intermediate p-value is based on.

## Navigation

- Previous day: Day 118 — Hypothesis Tests and Confidence Intervals
- Week 17 project: A/B Test Analyzer
- Week 17: Probability and Statistics
- Section: Mathematics, Statistics and Data
