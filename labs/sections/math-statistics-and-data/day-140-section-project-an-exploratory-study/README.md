# Day 140 lab — A Study That Holds Together

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Section Project: An Exploratory Study
- **Day number:** 140 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-140-section-project-an-exploratory-study
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-140-section-project-an-exploratory-study` when the site is running.
<!-- generated-links:end -->

## Purpose

Course 03 taught a dozen separable skills. A study is what happens when they
have to hold each other up — and the thing that breaks in a capstone is never
a single skill. It is the seams. A clean dataset with an unstated question. A
beautiful chart of a leaked feature. A confident conclusion drawn from an
exploration that examined forty things. Every component correct, the study
worthless.

This lab has two halves, and the second is the one you keep.

**A. A worked miniature study, executed end to end.** A small synthetic
dataset ships with the lab. `examples/study.py` carries it through the whole
arc — question written first, provenance with a verified checksum, ingestion
with an asserted grain, cleaning with a measured damage report, an
exploration/confirmation split, two honest figures, a difference of means with
an interval, and a generated report that names what it cannot do. It is small
enough to read in one sitting on purpose. It is a demonstration, not a
portfolio piece.

**B. An acceptance harness you run against your own study.**
`check_study(path)` reads a study directory and returns a verdict: eight
gates, each passing or carrying findings that name exactly what is missing.
That is the deliverable. It is what makes the section project gradeable by
you, before anyone else sees it.

The nine exercises in `starter/acceptance.py` build the harness. The worked
study is your test subject and your reference.

## Learning objectives

By the end you will be able to:

- Carry one small question through the whole arc — question, provenance,
  ingestion, cleaning, exploration, statistics, visuals, report — and see
  every handoff between stages as an artefact on disk rather than a habit.
- Write a checker that fails a study whose question file is missing or empty,
  and names the file.
- Write a checker that fails a source record lacking a URL, retrieval date or
  checksum, names which one, and recomputes the checksum against the file.
- Assert a row grain at ingestion, record that the assertion *failed* on
  arrival, and check the recorded result rather than the intention.
- Tell a damage report from a changelog, and fail a cleaning step documented
  without a before/after measurement.
- Detect a study whose confirmation set was used during exploration, by
  reading the research log's ordering — the only place that failure leaves a
  trace.
- Fail a reported estimate that carries no interval, and name the sentence.
- Fail a figure that carries no question and no claim, and catch a figure file
  no record mentions.
- Prove a study is reproducible by rebuilding it and comparing bytes, and
  detect one whose outputs moved after its manifest was written.
- Run all eight gates against a real, complete study, then delete one required
  element and watch exactly one gate fail — the proof that the harness works
  on a study and not only on fixtures.

## Prerequisites

- **Day 119** — the decision framing: would the answer change what anybody
  does? The worked study's `QUESTION.md` states the decision it informs.
- **Day 134** — provenance: licence, dictionary, checksum, retrieval record.
- **Day 135** — ingestion with a stated grain.
- **Days 121 and 125** — loading, inspecting and cleaning messy data.
- **Day 126** — a reproducible cleaning pipeline and its manifest.
- **Day 133** — building an EDA report, and the rule that every figure carries
  a question and a claim.
- **Day 136** — the exploratory process, the research log, and the
  confirmation set held out before any hypothesis exists.
- **Days 117 and 118** — the standard error and the confidence interval; this
  lab rebuilds the interval from `math.erf` alone, as Day 118 did.
- **Days 127–132** — choosing the chart, and chart honesty.
- **Day 138** — ethics, proxies, and who is missing from the data.
- **Days 71–74** — running pytest and reading its skip-versus-fail output.
- **Day 43** — `python3 -m venv` and installing a package with `pip`.

## Supported operating systems

- macOS — run and captured here (macOS 26.5.2, Apple Silicon, arm64).
- Linux — the same commands apply unchanged. Not run here.
- Windows — use the Windows Subsystem for Linux and follow the Linux
  instructions, or Git Bash with `.venv\Scripts\python.exe` in place of
  `.venv/bin/python3`. Not run here.

## Hardware requirements

Anything that runs Python 3.11 or later. The dataset is 264 rows and 12 KB.
The whole test harness completes in a few seconds; the two figures are the
slowest thing in the lab and they are small. No GPU, no network after the
one-time install, no more than a few hundred megabytes of disk for the
virtual environment.

## Required software

- Python 3.11 or later (3.14.0 here).
- The four pinned packages in `requirements/requirements.txt`: NumPy 2.5.2,
  pandas 3.0.5, matplotlib 3.11.1, pytest 9.1.1.
- `bash` for the test harness (3.2.57 here — no bash 4 features are used).

## Free and open-source options

Every package in this lab is free and open source, and there is no paid tier
of anything, no account, no key and no signup. `requirements/README.md` lists
each package, its licence and what this lab uses it for, and says plainly what
is deliberately *not* installed — seaborn, scipy, statsmodels, scikit-learn
and Jupyter — and that no output from any of them is reproduced anywhere here.

The harness itself has no third-party dependency at all: `acceptance.py`
imports only `hashlib`, `json`, `re`, `dataclasses` and `pathlib`. If you can
run Python, you can run `check_study` against a study directory.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-140-section-project-an-exploratory-study
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy, pandas, matplotlib; print(numpy.__version__, pandas.__version__, matplotlib.__version__)"
```

That last command printed `2.5.2 3.0.5 3.11.1` here. The `pip install` is the
only command in this lab that opens a network connection.

## File structure

```
day-140-section-project-an-exploratory-study/
├── README.md
├── metadata.yml
├── security.md
├── troubleshooting.md
├── requirements/
│   ├── README.md            what is installed, why, licences, what is not
│   └── requirements.txt     four pinned versions
├── examples/                the reference: worked study + working harness
│   ├── dataset.py           the synthetic source, four defects, one real effect
│   ├── data/observations.csv  the committed source file (264 rows)
│   ├── study.py             the worked study: the whole arc, executed
│   ├── acceptance.py        the harness: eight gates and check_study
│   ├── fixtures.py          deliberately broken copies, one defect at a time
│   ├── 01_question_recorded.py … 09_whole_harness.py
│   ├── conftest.py          import guard (see below)
│   └── test_reference.py    54 tests
├── starter/                 your work
│   ├── 00_brief.md          read this first
│   ├── dataset.py, study.py, fixtures.py, data/  given, complete
│   ├── acceptance.py        nine exercises to fill in
│   ├── conftest.py          import guard
│   └── test_starter.py      33 tests: skip until attempted
├── tests/run_tests.sh       the full harness, 81 checks
└── expected-output/         captured from real runs, never fabricated
    ├── FIELDS.md            what is exact and what is machine-dependent
    ├── 01-…-.txt … 09-whole-harness.txt
    ├── worked-study-report.md, -damage-report.md, -research-log.md
    ├── worked-study-manifest.txt, -verdict.txt
    └── examples-run.txt, starter-run.txt, test-run.txt
```

Both `examples/` and `starter/` contain modules called `acceptance`, `study`,
`dataset` and `fixtures`. Each directory's `conftest.py` puts its own
directory first on `sys.path` and drops any already-imported module of those
names from elsewhere, so `pytest starter` can never silently import the
reference solution and report a pass for work you have not done.

## How to run

Read the worked study before you grade anything:

```bash
.venv/bin/python3 -c "
import sys; sys.path.insert(0, 'examples')
import fixtures, pathlib
print(fixtures.worked_study(pathlib.Path('/tmp/day140-look')))
"
```

Then open `QUESTION.md`, `SOURCE.json`, `INGEST.json`, `CLEANING.md`,
`RESEARCH_LOG.md`, `FIGURES.json`, `REPORT.md` and `MANIFEST.json` in
`/tmp/day140-look/study/`, and `rm -rf /tmp/day140-look` when you are done.

The nine reference scripts, each one gate:

```bash
cd examples && ../.venv/bin/python3 01_question_recorded.py && cd ..
cd examples && ../.venv/bin/python3 02_provenance_complete.py && cd ..
cd examples && ../.venv/bin/python3 03_grain_asserted.py && cd ..
cd examples && ../.venv/bin/python3 04_damage_report.py && cd ..
cd examples && ../.venv/bin/python3 05_confirmation_untouched.py && cd ..
cd examples && ../.venv/bin/python3 06_uncertainty_in_the_prose.py && cd ..
cd examples && ../.venv/bin/python3 07_figures_carry_claims.py && cd ..
cd examples && ../.venv/bin/python3 08_reproducibility.py && cd ..
cd examples && ../.venv/bin/python3 09_whole_harness.py && cd ..
```

The two test suites — **run them as two separate commands, never
`pytest examples starter`**, because both directories carry modules of the
same names and the combined form is unreliable:

```bash
.venv/bin/pytest examples -q -p no:cacheprovider
.venv/bin/pytest starter -q -p no:cacheprovider
```

And the whole harness:

```bash
bash tests/run_tests.sh
```

## What the commands do

| Command | What it proves |
| --- | --- |
| `01_question_recorded.py` | The question gate passes a written question and fails a missing, empty or question-free file, naming `QUESTION.md` every time. |
| `02_provenance_complete.py` | Missing fields are named one at a time, and the recorded checksum is recomputed against the file on disk. |
| `03_grain_asserted.py` | The grain is stated, checked, and honest: it FAILED on arrival with 8 violations, and the record says so. |
| `04_damage_report.py` | Four cleaning steps, each with a before and after. One step reduced to a changelog entry is named. |
| `05_confirmation_untouched.py` | A peeked confirmation set is caught from the log's ordering — and the report, figures and interval are byte-identical either way. |
| `06_uncertainty_in_the_prose.py` | Five forms of interval evidence are accepted; a bare point estimate is rejected and quoted. |
| `07_figures_carry_claims.py` | A figure with no claim, a figure with no question, a stray file and a dangling record are all caught. |
| `08_reproducibility.py` | Two builds produce identical bytes, figures included; a study whose output moved is named. |
| `09_whole_harness.py` | Eight gates pass on the worked study; one deleted field fails exactly one gate; three defects come back as three. |
| `pytest examples` | 54 tests: the dataset, the arithmetic, the arc, and every gate against every fixture. |
| `pytest starter` | Your running score. Skips are unattempted; failures show your answer next to the real one. |
| `bash tests/run_tests.sh` | 81 checks, including a deliberate self-test that proves the suite can go red. |

## Expected output

Everything in `expected-output/` was captured from real runs on the authoring
machine on 2026-08-20. `expected-output/FIELDS.md` says exactly which values
are identical everywhere and which are expected to differ — in this lab that
list is short, because nothing is sampled: the only genuinely
machine-dependent values are the two PNG digests, and no test asserts a PNG
digest against a stored literal.

The verdict on the worked study
(`expected-output/worked-study-verdict.txt`):

```
ACCEPTED: <tmp>/study
[PASS] question_recorded
[PASS] provenance_complete
[PASS] grain_asserted
[PASS] damage_report_quantified
[PASS] confirmation_untouched
[PASS] uncertainty_reported
[PASS] figures_documented
[PASS] outputs_reproducible
```

And the last line of a passing harness run:

```
81 checks, 0 failure(s).
```

## Validation steps

1. `bash tests/run_tests.sh` exits 0 and prints `81 checks, 0 failure(s).`
   Capture its own exit status directly — `bash tests/run_tests.sh; echo $?` —
   never through a pipe, because a pipeline reports the last command's status
   and has hidden a real failure in this repository before.
2. `.venv/bin/pytest examples -q` reports 54 passed.
3. `.venv/bin/pytest starter -q` reports 1 passed and 32 skipped on an
   untouched checkout, and 33 passed once every exercise is solved.
4. Each of the nine scripts exits 0 and ends with a line beginning `OK:`.
5. Compare a script's output with the matching file in `expected-output/`;
   they differ only in the temporary directory path.
6. Confirm the suite can fail: change `"264"` to `"265"` in the
   `the delivery carries 264 rows` check in `tests/run_tests.sh`, run it, see
   `81 checks, 1 failure(s).` and a non-zero exit, then change it back. That
   was done during authoring and is recorded in `metadata.yml`.

## Tests

`tests/run_tests.sh` is a bash assert harness. It checks real behaviour and
real values, never file existence alone, and it never asserts on a timing.

Ten sections: the pinned versions actually installed; all nine reference
scripts running with every internal assertion holding; the worked study's
measured numbers; one defect at a time failing exactly the gate it should with
a finding that names something; a peeked study being byte-identical outside
its log; one required element removed from the real study failing one gate by
name; the reference suite; the starter suite skipping rather than failing;
a self-test that solves `starter/` in a scratch copy, breaks one gate on
purpose and confirms a red run; and a final sweep for anything left behind.

It exits 0 only if every check passes.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf /tmp/day140-look        # only if you built the study there to read it
rm -rf .venv                   # optional: removes the lab virtual environment
git checkout -- starter/       # optional: reset your work
```

The lab writes nothing outside a temporary directory of its own making. Every
study the scripts and tests build goes into a `mktemp -d` directory that is
removed on exit, and section 10 of the harness checks that neither
`examples/` nor `starter/` has gained a file.

## Troubleshooting

See `troubleshooting.md` for the full list. The three you are most likely to
hit:

- **`pytest starter` reports passes for exercises you have not written.** You
  ran `pytest examples starter` as one command. Run them separately.
- **A gate you wrote returns `None` and the test skips instead of failing.**
  `attempt()` treats `None` as "not attempted". Return a `GateResult`.
- **Your figures do not hash identically across two runs.** Something is
  reading a clock, or you dropped `metadata={"Software": None}` from
  `savefig`.

## Security notes

See `security.md`. In short: no network after the one-time install, no
credentials, no `sudo`, no ports bound, and the study's source URL points at
`example.invalid` — a reserved name that can never resolve — because the file
is generated locally and never fetched. The one genuine caution is that
`check_study` reads whatever directory you hand it: treat a study directory
from someone else as untrusted input, and note that the harness reads files
but never executes anything inside them.

## Extension exercises

1. **A ninth gate: the decision.** Day 119 asks whether an answer would change
   what anybody does. Add `gate_decision_named` requiring `QUESTION.md` to
   state a decision the answer informs, and see how many of your own past
   analyses would fail it.
2. **Make the uncertainty gate stricter.** It currently accepts any interval
   evidence. Make it also require the interval to be *wider* than a threshold
   you set, and think hard about why that is a bad idea before you keep it.
3. **A gate for the leaked feature.** The worked study draws its figures from
   the exploration half only. Extend `FIGURES.json` with a `split` field and
   fail any figure drawn from the confirmation half.
4. **Port the harness to YAML.** Swap `json.loads` for a YAML parser and
   confirm all eight gates pass unchanged against a YAML study directory. The
   gates do not care about the format; that is the point.
5. **Run it on your Week 20 project.** The real extension. Point
   `check_study` at your own study directory and fix what it names — before
   anyone else reads it.

## Navigation

- Course 03 — Math, Statistics, and Data — ends here. Day 141 begins
  Course 04, Machine Learning.
- Previous lab: Day 139 — Reproducible Notebooks.
- The Week 20 project brief (your own full exploratory study) lives with the
  week's projects; this lab supplies the harness you grade it with.
