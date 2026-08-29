# Day 136 lab — Exploration You Can Report

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** The Exploratory Data Analysis Process
- **Day number:** 136 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-136-the-exploratory-data-analysis-process
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-136-the-exploratory-data-analysis-process` when the site is running.
<!-- generated-links:end -->

## Purpose

Exploring data and confirming a finding are different activities, and the
mistake this lab is built to prevent is doing the first and reporting it
as the second. It builds the machinery of an honest exploratory loop --
comparisons that are counted, a confirmation set held out before any
hypothesis is chosen, a stopping rule that does not depend on what was
found -- and proves, with real simulation, exactly how much a p-value is
worth when none of that discipline is in place.

The centrepiece is exercise 3: one dataset with a REAL, planted effect and
thirty SPURIOUS columns, split in half before anything is examined. The
real effect survives testing on the untouched confirmation half. The
best-looking spurious column, chosen from thirty candidates on the
exploration half, does not. That is the whole day's argument, made
concrete instead of asserted.

Every exercise follows the same design as recent days in this section:
**compute a claim two ways and assert they agree** -- exact where a
formula exists (the family-wise error rate, the Bonferroni correction),
seeded simulation otherwise, with tolerances derived from a standard
error rather than guessed.

## Learning objectives

By the end you will be able to:

- Measure, by exact formula and by simulation, that k independent
  alpha=0.05 comparisons on data with no real signal produce at least one
  "significant" result `1 - 0.95^k` of the time -- 22.6% at k=5, 64.2% at
  k=20, 87.2% at k=40.
- Explain why a forking-paths result is tempting rather than obviously
  wrong: demonstrate that the "winning" comparison from such a scan can
  carry both a low p-value and a publishable-looking effect size.
- Hold out a confirmation set before forming a hypothesis, and demonstrate
  both outcomes on real data: a genuine effect surviving confirmation, and
  a spurious one chosen for looking best on exploration failing it.
- Show that varying a subset filter or an outcome definition, with no
  test formally declared per variant, still inflates the apparent
  significance rate -- quantified, not asserted.
- Apply a Bonferroni correction correctly when the comparison count is
  known, and demonstrate exactly how it fails when the true count exceeds
  the reported one.
- Build a research log as a data structure whose own length is the true
  comparison count, recording every question, look, and outcome --
  including the nothings.
- Score candidate questions by expected information, cost, and decision
  relevance, and rank them the way Day 119 frames "would the answer
  change a decision".
- Measure, by simulation, how much "stop when significant" inflates the
  real false-positive rate above a time-boxed rule using the identical
  budget of looks.
- Build the handoff object a report stage needs -- a finding, its
  confirmation-set result, and a comparison count -- and prove the report
  stage refuses to run without all three.

## Prerequisites

- Day 118 -- hypothesis tests, confidence intervals, and multiple
  comparisons; this lab reuses the from-scratch z-test built there
  directly, and extends its Bonferroni section.
- Day 117 -- sampling and the standard error, which every tolerance in
  this lab is derived from.
- Day 119 -- the pre-registered analysis plan and the decision-relevance
  framing this lab's triage exercise applies before any data is touched.
- Day 133 -- building an EDA report; this lab's exercise 9 builds the
  object that day's report generator needs.
- Comfort with NumPy arrays, vectorised operations, and pandas
  `DataFrame.groupby`.
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
8's two 20,000-replicate stopping-rule simulations, which together take
well under a second. Roughly 90 MB of disk for the virtual environment,
most of it pandas and NumPy.

## Required software

- `python3` -- 3.14.0 here.
- `numpy` 2.5.2, `pandas` 3.0.5 and `pytest` 9.1.1, installed into a
  lab-local virtual environment from `requirements/requirements.txt`.
- `bash` -- 3.2.57 here, for the test harness.

## Free and open-source options

All three dependencies are free and open source and there is no paid tier
of anything in this lab. NumPy and pandas are distributed under the
BSD 3-Clause licence and pytest under the MIT licence. No account, no key,
no signup, personally or commercially.

`statsmodels.stats.multitest` implements Bonferroni, Holm and false
discovery rate corrections in one call each and **is not installed
here, so no output from it is reproduced anywhere** in this lab or its
lesson -- it is described from its documentation only. Jupyter/`nbconvert`
and Weights & Biases are likewise not installed; the lesson's Tools
section describes both from their public documentation and names exactly
what was and was not run.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-136-the-exploratory-data-analysis-process
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy, pandas; print(numpy.__version__, pandas.__version__)"
```

Expect `2.5.2 3.0.5`. That is the only time this lab needs the network.

## File structure

```
.
├── README.md                                     this file
├── metadata.yml                                   how the lab was actually run, and when
├── requirements/
│   ├── README.md                                  why each package is here, its licence, and what statsmodels would add
│   └── requirements.txt                           numpy==2.5.2, pandas==3.0.5, pytest==9.1.1
├── starter/                                        your work goes here
│   ├── 00_brief.md                                 the nine exercises, in order
│   ├── conftest.py                                 makes this directory's modules the ones its tests import
│   ├── dataset.py                                  constants, generators and tolerances — read it, do not change it
│   ├── exploration.py                              all nine exercises — functions to write
│   └── test_starter.py                             your running score; unattempted work skips
├── examples/                                       the reference, to read after you have tried
│   ├── conftest.py                                 the same import guard
│   ├── dataset.py                                  the data, and every tolerance with its derivation
│   ├── exploration.py                              the finished exploration machinery
│   ├── 01_forking_paths.py                         the exact rate, confirmed by simulation, plus one real 40-comparison scan
│   ├── 02_plausible_story.py                       the winning comparison's effect size clears the "publishable" threshold
│   ├── 03_holdout_rescues_you.py                   the centrepiece: real effect survives, spurious one does not
│   ├── 04_choices_are_comparisons.py                a silent ten-variant grid inflates the significance rate
│   ├── 05_bonferroni_and_its_limit.py               the correction working, and failing with the wrong comparison count
│   ├── 06_research_log.py                          a dated record whose own length is the true comparison count
│   ├── 07_triage.py                                 scoring candidate questions by information, cost and relevance
│   ├── 08_stopping_rule.py                          time-boxed vs. "stop when significant", both false-positive rates
│   ├── 09_handoff_contract.py                       the object a report stage needs, and its refusal when incomplete
│   └── test_reference.py                           27 tests over real values and real exceptions
├── tests/
│   └── run_tests.sh                                the bash harness: 33 checks, exits non-zero on any failure
├── expected-output/                                captured from real runs on 2026-08-20
│   ├── FIELDS.md                                   what may legitimately differ on your machine
│   ├── 01-forking-paths.txt … 09-handoff-contract.txt
│   ├── examples-run.txt
│   ├── starter-run.txt
│   └── test-run.txt
├── troubleshooting.md
└── security.md
```

## How to run

Read `starter/00_brief.md` first. Then work, checking yourself as you go:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `1 passed, 13 skipped`. A skip means
"not attempted"; a failure means "attempted and wrong", and prints both
your answer and the real one.

Afterwards, read the reference -- each script prints its working and
asserts every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_forking_paths.py
../.venv/bin/python3 02_plausible_story.py
../.venv/bin/python3 03_holdout_rescues_you.py
../.venv/bin/python3 04_choices_are_comparisons.py
../.venv/bin/python3 05_bonferroni_and_its_limit.py
../.venv/bin/python3 06_research_log.py
../.venv/bin/python3 07_triage.py
../.venv/bin/python3 08_stopping_rule.py
../.venv/bin/python3 09_handoff_contract.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `exploration.py` and
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
| `.venv/bin/pip install -r requirements/requirements.txt` | Installs numpy 2.5.2, pandas 3.0.5 and pytest 9.1.1. The one command that uses the network. |
| `.venv/bin/pytest starter -q` | Your running score. Unattempted exercises skip; wrong answers fail with both values printed. |
| `01_forking_paths.py` | The exact false-positive rate for k independent comparisons, confirmed by simulation, plus one concrete 40-comparison scan. |
| `02_plausible_story.py` | The winning comparison's effect size, checked against the "publishable-looking" threshold. |
| `03_holdout_rescues_you.py` | A real effect and a spurious one, tested on an untouched confirmation set. |
| `04_choices_are_comparisons.py` | A silent ten-variant grid, and how much it inflates the apparent significance rate. |
| `05_bonferroni_and_its_limit.py` | Bonferroni restoring the nominal rate, then failing when the true comparison count is under-reported. |
| `06_research_log.py` | A dated log whose own length is the true comparison count. |
| `07_triage.py` | Ranking candidate questions by expected information, cost and decision relevance. |
| `08_stopping_rule.py` | Time-boxed vs. "stop when significant", both measured false-positive rates. |
| `09_handoff_contract.py` | The object a report stage needs, and its refusal when a required field is missing. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 27 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 33-check harness: versions, every script, both suites, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
33 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `27 passed`, and an untouched
starter with `1 passed, 13 skipped`.

The result worth recognising before you meet it, from exercise 1:

```
k= 5: exact = 1 - (1-0.05)^5 = 0.2262   simulated over 2000 families = 0.2355   deviation = 0.0093 (0.99 SE)
k=20: exact = 1 - (1-0.05)^20 = 0.6415   simulated over 2000 families = 0.6595   deviation = 0.0180 (1.68 SE)
k=40: exact = 1 - (1-0.05)^40 = 0.8715   simulated over 2000 families = 0.8780   deviation = 0.0065 (0.87 SE)
```

`expected-output/FIELDS.md` records exactly which captured numbers are
sampled and will differ, within their stated tolerance, on your machine.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `33 checks, 0 failure(s).`
   and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `27 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `14 passed`
   once you have finished, and never prints a failure you have not been
   shown.
4. Each of the nine reference scripts ends with a line starting `OK:`.
5. `find . -path ./.venv -prune -o -type d -name '__pycache__' -print`
   prints nothing after a full run.

## Tests

`tests/run_tests.sh` runs 33 checks in six sections:

1. **Versions** -- reads the installed numpy, pandas and pytest and
   compares them against `requirements/requirements.txt`.
2. **The nine reference scripts** -- each must exit 0 and print an `OK:`
   line confirming every one of its internal assertions held.
3. **The reference pytest suite** -- must exit 0, report no failures, and
   have collected at least 24 tests, so a collection error cannot pass as
   success.
4. **The starter suite** -- must exit 0 on an untouched checkout with
   skips rather than failures; and auto-discovering both suites at once
   (running `pytest` with no path argument from the lab directory) must
   report the same skip count as `pytest starter` alone, which is a real
   hazard here because both directories contain modules called
   `exploration` and `dataset`.
5. **A deliberate failure** -- the harness re-runs script 01 (forking
   paths) with its expected exact rate for k=20 temporarily swapped for a
   wrong one, and asserts the re-run reports the named failure and exits
   non-zero. A green suite proves nothing until you have watched it go
   red.
6. **A clean disk** -- no `__pycache__` and no `.pytest_cache` outside
   `.venv`, and no source file that opens a network connection.

Before section 1, the harness clears any `__pycache__` and `.pytest_cache`
that an **earlier** command left behind, pruning `.venv` as it goes, so
section 6 measures only what *this* run left behind.

The harness was confirmed to exit 0 on a fresh lab-local `.venv` created by
the documented setup commands, and to correctly report a non-zero exit
and a named failure when section 5 deliberately breaks one assertion --
and, separately, when a real bug was introduced directly into
`exploration.py`'s `bonferroni_alpha` during development (`alpha/m`
changed to `alpha*m`), the harness caught it too (4 of 33 checks failed),
confirming section 5 is not the only thing standing between a real bug
and a green run.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: resets your work
```

The lab's own commands leave none of the first two behind; section 6 of
the harness fails if they appear. It deliberately does not look inside
`.venv`, because the bytecode caches shipped with pandas, NumPy and
pytest are theirs, not yours.

## Troubleshooting

See `troubleshooting.md`. It covers wrong-directory import errors, the
starter tests that keep skipping because a function still raises
`NotImplementedError`, why small `n_per_group` values drift the measured
significance rate above nominal, why the narrative-scan seed and row
count were chosen the way they were, and the import collision the two
`conftest.py` files prevent. All of them were hit while building this lab
or are named by a test.

## Security notes

See `security.md`. In short: this lab computes and prints. It writes no
files, opens no connection after the one-time install, needs no
credentials and no `sudo`, and all the data is invented. Three points
there are worth carrying away: a p-value answers a narrower question than
most people act on it as answering, "we stopped when we found something"
is the failure mode rather than a stopping rule, and a multiple-comparisons
correction is only as honest as the comparison count fed into it.

## Extension exercises

1. **Sweep `n_per_group` in exercise 1** at 10, 25, 50, 100 and 200, and
   tabulate how far the simulated rate drifts from the exact `1 - 0.95^k`
   value at each -- confirming directly the small-n drift
   `troubleshooting.md` describes.
2. **Add a Holm-Bonferroni step-down correction** to exercise 5, and
   compare its family-wise error rate and its power (fraction of TRUE
   effects it still detects, using exercise 3's planted effect) against
   plain Bonferroni on a family where some comparisons carry a real
   effect and others do not.
3. **Vary the confirmation-set fraction** in exercise 3 from 50/50 to
   20/80 and to 80/20, and find how small the confirmation set can get
   before the real effect stops reliably surviving it.
4. **Extend the research log** with a `cost_minutes` field per entry, and
   compute total analyst time spent on nulls versus on the one finding
   that was reported -- a concrete number for "most looks produce
   nothing".
5. **Build an alpha-spending sequential test** for the stopping-rule
   exercise, and confirm by simulation, the same way exercise 8 does,
   that its false-positive rate under repeated looking stays near the
   nominal alpha where the naive "stop when significant" rule does not.

## Navigation

- Previous day: Day 135 — From API to DataFrame
- Next day: Day 137 — Thinking in Features
- Week 20: Working with Real Data
- Section: Mathematics, Statistics and Data
