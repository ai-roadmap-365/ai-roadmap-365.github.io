# Lab — Day 365: Graduation: Your AI Roadmap Going Forward

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Graduation: Your AI Roadmap Going Forward
- **Day number:** 365 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-365-graduation-your-ai-roadmap-going-forward
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-365-graduation-your-ai-roadmap-going-forward` when the site is running.
<!-- generated-links:end -->

## Purpose

Check whether the plan you make today is a plan or a wish list — before week one rather than in week three.

Two things kill a post-course plan, and both are visible in the plan itself before it starts: commitments phrased as topics rather than next actions, and a total that exceeds the hours you actually have. The second is what usually does it, and almost nobody checks it.

The tool does not judge whether your goals are worthwhile. It checks whether the plan is one you could execute.

## Learning objectives

- Distinguish a next action from a topic, including a topic dressed as an action.
- Require an artifact — something that exists afterwards and did not before.
- Compute a plan's weekly load against your real available hours.
- Re-cost a plan at your own measured calibration from Day 364.
- Trim to what fits by dropping commitments rather than shaving them, and name what was cut.

## Prerequisites

- Day 364, "Capstone Retrospective" — this lab consumes its calibration number.
- Comfortable with Python dataclasses and regular expressions.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key, no network — the input is a written plan, so there is nothing to fetch.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/plan.py        your work: eight stubbed tasks
examples/plan.py       reference implementation
examples/plan_demo.py  a plausible post-course plan, checked
tests/test_plan.py     grouped by what the check decides
tests/run_tests.sh     suite entry point
expected-output/       real captured output and measured values
requirements/          pinned dependency
```

## How to run

```bash
python3 examples/plan_demo.py   # check a post-course plan
bash tests/run_tests.sh         # run the suite
```

To work on the exercise, edit `starter/plan.py`, then copy it over the reference:

```bash
cp starter/plan.py examples/plan.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/plan_demo.py` checks six commitments against five available hours a week, twice: as written, and re-costed at the 1.20x calibration measured on Day 364. It then prints what survives, what is cut, and the findings as sentences.

`bash tests/run_tests.sh` runs `pytest` over twenty-seven tests grouped by what the check decides: actionability, artifacts, load, calibration, the trim, the review and the findings.

## Expected output

```text
--- as written ---
  needs 17.0h/week  have 5.0h/week  3.40x  OVER
  2 kept / 4 cut  not-actionable=3 no-artifact=3
--- in my own hours ---
  needs 20.4h/week  have 5.0h/week  4.08x  OVER
  2 kept / 4 cut  not-actionable=3 no-artifact=3
--- what survives ---
  keep  p1   3.6h/wk  evaluation harness for my capstone
  keep  p2   1.2h/wk  writing about the work
  cut   p3   4.8h/wk  fine-tuning
```

Not one of the six commitments is unreasonable on its own. Together they are three and a half times the available time, and four times it once your own calibration is applied.

`expected-output/FIELDS.md` explains every field, and `expected-output/measured-values.txt` records why three commitments fail the wording check and have no artifact — the same three, which is not a coincidence.

## Validation steps

1. `bash tests/run_tests.sh` reports `27 passed`.
2. The demo must report `3.40x` as written and `4.08x` once calibrated. If both are the same, the calibration is being applied after the load is measured rather than before.
3. `"build up my understanding of evals"` must fail the actionability check despite starting with an action verb.
4. Two identical commitments must yield one kept and one cut, not zero kept. `Commitment` is a frozen dataclass and compares by value.
5. A calibration of `0.0` must leave the plan unchanged rather than reporting that it fits comfortably.

## Tests

Twenty-seven tests in seven groups:

- **actionable** — action verbs pass; topic verbs fail; a topic verb disqualifies even when an action verb is present; empty fails; multi-word topic verbs are listed.
- **artifact** — an artifact is required; whitespace is not one; total hours multiply out.
- **load** — the weekly hours are summed; one hour over does not fit; zero available hours does not divide by zero.
- **calibration** — every commitment is re-costed; nothing but the hours changes; a nonsensical ratio leaves the plan alone.
- **trim** — highest priority first; not proportional; it skips past something too big and carries on; a fitting plan is kept whole; cuts are named; duplicates are not confused.
- **review** — every failure kind is reported; calibration is applied before the load is measured.
- **findings** — how far over, each cut named, the wording quoted, the fitting case stated, and the calibration disclosed.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: no network, no credentials — and a note on which habits from this year are cheap enough to keep once nobody is grading you.

## Extension exercises

1. **Add dependencies.** Let a commitment depend on another, and refuse a plan whose dependencies cannot be satisfied in order. Detect cycles rather than looping.
2. **Run it on your own plan**, with your own available hours and your own calibration from Day 364. Measure the hours; do not estimate them.
3. **Add a decay model.** Available hours are not constant — holidays, deadlines, illness. Check the plan against your worst plausible month rather than your best, and see how many commitments survive that instead.

## Navigation

- [Lesson](../../../../content/sections/capstone/day-365-graduation-your-ai-roadmap-going-forward/README.md)
- Previous: Day 364 — Capstone Retrospective
- Next: none — this is the final day.
