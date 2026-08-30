# Lab — Day 363: Portfolio, Resume, and Sharing Your Work

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Portfolio, Resume, and Sharing Your Work
- **Day number:** 363 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-363-portfolio-resume-and-sharing-your-work
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-363-portfolio-resume-and-sharing-your-work` when the site is running.
<!-- generated-links:end -->

## Purpose

Build a checker for the claims in a portfolio: is each one specific, does it name a baseline, does it say who did the work, and does it link to something a stranger can open.

The checker does not judge whether a claim is **true**. It judges whether it is **checkable**, which is the property a reader can assess without knowing you.

## Learning objectives

- Detect a measurement, including a stated change between two figures with no unit.
- Detect a baseline, and explain why a figure without one is not a result.
- Classify attribution as yours, shared, mixed or unattributed.
- Decide whether an evidence link is openable by a reader, without a network.
- Produce a rewrite instruction rather than only a grade.

## Prerequisites

- Day 362, "Documentation and Demo".
- Comfortable with Python regular expressions, dataclasses and enums.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key, no network — evidence links are judged from the string rather than by fetching them, which keeps the check fast and offline.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/claims.py         your work: five detection and grading functions
examples/claims.py        reference implementation
examples/claims_demo.py   assesses five claims and shows one rewritten
tests/test_claims.py      grouped by property
tests/run_tests.sh        suite entry point
expected-output/          real captured output and measured values
requirements/             pinned dependency
```

## How to run

```bash
python3 examples/claims_demo.py   # assess a set of claims
bash tests/run_tests.sh           # run the suite
```

To work on the exercise, edit `starter/claims.py`, then copy it over the reference:

```bash
cp starter/claims.py examples/claims.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/claims_demo.py` assesses five portfolio claims ranging from vague to strong, prints what each weak one is missing as an instruction, then shows one claim written badly and written well.

`bash tests/run_tests.sh` runs `pytest` over nineteen tests grouped by property: measurement, baseline, attribution, evidence, grading, hints and the report.

## Expected output

```text
  VAGUE   Significantly improved retrieval quality.
          vague wording: significantly; no measurement; does not say who did it;
          no evidence link
  WEAK    Reduced answer latency to 840ms.
          measurement without a baseline; does not say who did it
  STRONG  I cut p95 answer latency from 4.2s to 840ms by adding an
  => strong=1 weak=2 vague=2
--- the same claim, before and after ---
  VAGUE   Significantly improved retrieval quality.
  STRONG  I raised recall@10 from 0.71 to 0.94 by adding a reranking stage,
          measured over 200 held-out questions.
```

`expected-output/FIELDS.md` explains the grades and why `WEAK` and `VAGUE` are distinguished.

## Validation steps

1. `bash tests/run_tests.sh` reports `19 passed`.
2. "Reduced answer latency to 840ms" must grade `WEAK`, not `STRONG`. A number alone is not a result.
3. "from 0.71 to 0.94" must count as a measurement despite having no unit.
4. A claim with a vague word **and** a measurement must be `WEAK`, not `VAGUE` — vague is reserved for claims with nothing measured to fall back on.

## Tests

Nineteen tests in seven groups:

- **measurement** — units, percentages and multipliers count; a stated change between two figures counts without a unit; adjectives do not; hyphenated vague words are caught.
- **baseline** — "from", "previously" and "compared to" are recognised; an end value alone is not.
- **attribution** — mine, shared and unattributed are classified; mixed is detected; the match is case-insensitive.
- **evidence** — a public URL is openable; empty, `localhost`, a loopback IP, `file://` and bare paths are not.
- **grading** — a complete claim is strong with no reasons; an adjective with no measurement is vague; a measurement without a baseline is weak; every missing property is named.
- **hints** — a strong claim needs nothing; a weak one is told what to add.
- **report** — each grade is counted.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: no network, no credentials — and the lesson covers a portfolio as a permanent public disclosure.

## Extension exercises

1. **A verb check.** Flag claims that describe a position ("was responsible for") rather than an action ("rebuilt, cutting p95 from 2.1s to 600ms").
2. **Run it on your own portfolio.** Record the grade distribution before and after rewriting.
3. **Categorise what you cannot fix.** For each claim that resists becoming strong, decide whether the missing piece is a measurement you never took, evidence an employer owns, or attribution you are reluctant to make precise.

## Navigation

- [Lesson](../../../../content/sections/capstone/day-363-portfolio-resume-and-sharing-your-work/README.md)
- Previous: Day 362 — Documentation and Demo
- Next: Day 364 — Capstone Retrospective
