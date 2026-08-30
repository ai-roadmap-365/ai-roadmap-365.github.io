# Lab — Day 364: Capstone Retrospective

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Capstone Retrospective
- **Day number:** 364 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-364-capstone-retrospective
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-364-capstone-retrospective` when the site is running.
<!-- generated-links:end -->

## Purpose

Turn a project's record into findings that transfer to the next project: how wrong the estimates were and in which direction, whether that error is uniform or concentrated in one kind of work, and which incidents reached a user.

The tool does not judge whether the project was good. It measures what was predictable and was not predicted, which is the only part that carries forward.

## Learning objectives

- Compute a calibration ratio, and explain why it is a median rather than a mean.
- Split the error by area and decide whether a single multiplier is a valid correction.
- Rank incidents by detection stage and identify which escaped to production.
- Separate a preventable escape, which names a gate, from a genuine unknown.
- Produce sentences a reader can act on rather than scores.

## Prerequisites

- Day 363, "Portfolio, Resume, and Sharing Your Work".
- Comfortable with Python dataclasses, enums and dictionaries.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key, no network — the input is a recorded list of tasks and incidents, so there is nothing to fetch.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/retro.py        your work: eight stubbed tasks
examples/retro.py       reference implementation
examples/retro_demo.py  a capstone's record, turned into findings
tests/test_retro.py     grouped by what the retrospective computes
tests/run_tests.sh      suite entry point
expected-output/        real captured output and measured values
requirements/           pinned dependency
```

## How to run

```bash
python3 examples/retro_demo.py   # analyse a capstone's record
bash tests/run_tests.sh          # run the suite
```

To work on the exercise, edit `starter/retro.py`, then copy it over the reference:

```bash
cp starter/retro.py examples/retro.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/retro_demo.py` analyses seven tasks and five incidents from a capstone: it prints the calibration line, the median ratio per area, what a future estimate becomes under your own history, where each incident was caught, and the findings as sentences.

`bash tests/run_tests.sh` runs `pytest` over twenty-two tests grouped by what the retrospective computes: median, calibration, spread, multiplier, detection and findings.

## Expected output

```text
--- calibration ---
  median ratio 1.20x  under 6 / over 0  worst unfamiliar 3.33x  best familiar 1.15x
  uniform across areas: False
  median ratio by area:
    familiar     1.15x
    unfamiliar   3.33x
--- detection ---
  review=1 tests=1 staging=1 monitoring=1 user=1  escaped=2 (40%)
--- findings ---
  - Estimates ran 1.20x long at the median. Multiply the next one by 1.20 before
    committing to it.
  - The error is concentrated, not uniform: unfamiliar ran 3.33x while familiar
    ran 1.15x. A single multiplier will not fix this.
```

The second finding contradicts the first, deliberately. Both are true, and the second is the one that changes what you do — there is no task in this record for which 1.20x was the right multiplier.

`expected-output/FIELDS.md` explains every field, and `expected-output/measured-values.txt` records the threshold sensitivity.

## Validation steps

1. `bash tests/run_tests.sh` reports `22 passed`.
2. The demo must report `uniform across areas: False`. If it reports `True`, `is_uniform` is comparing areas against the overall median instead of against each other.
3. The median of `[1.0, 1.1, 1.2, 1.3, 8.0]` must be `1.2`. If you get a value above `2.0`, you are computing a mean.
4. Five incidents, one per stage, must yield `escaped=2`. Staging is deployed and reached nobody, so it is not an escape.
5. A clean record — accurate estimates, nothing escaped — must produce the "no systematic pattern" line rather than a manufactured finding.

## Tests

Twenty-two tests in six groups:

- **median** — one extreme task does not move it; even counts average the middle two; an empty list is zero rather than an error.
- **calibration** — the ratio is actual over estimated; a zero estimate does not divide by zero; direction is counted separately from size; the worst and best areas are named; empty input returns an empty result.
- **spread** — a uniform error and a concentrated one are distinguished; a single area is trivially uniform; each area gets its own median.
- **multiplier** — your own history applied to a new estimate.
- **detection** — incidents are counted by stage; only production incidents escape; preventable escapes are separated from unknowns; no incidents is a zero rate rather than an error.
- **findings** — the multiplier is stated when estimates ran long and padding when they ran short; a concentrated error is called out specifically; each preventable escape names its gate; a clean record says so.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: no network, no credentials — and a retrospective is a document that describes, in order, what your system got wrong and which controls are still missing.

## Extension exercises

1. **Group by estimate size.** Under two hours, two to eight, over eight. If large estimates are worse, break work down; if small ones are worse, you are underestimating fixed overheads that do not scale down. The two findings have opposite fixes.
2. **Run it on your own capstone**, with the real numbers.
3. **Split the escapes honestly.** For each incident that reached production, decide whether a gate would genuinely have caught it. If everything looks preventable in hindsight, you are hindsight-biasing — the test is what you would have needed to know *at the time* to justify building the gate before the incident.

## Navigation

- [Lesson](../../../../content/sections/capstone/day-364-capstone-retrospective/README.md)
- Previous: Day 363 — Portfolio, Resume, and Sharing Your Work
- Next: Day 365 — Graduation: Your AI Roadmap Going Forward
