# Week 52 Capstone Project: Capstone Final Delivery - The Delivery Gate

## Purpose

Week 52 asked for a capstone that is deployed, monitored, security-reviewed, documented and demonstrated. By the end of it, every one of those will feel done.

This project builds the gate that decides whether it actually is. It sorts every requirement into one of four categories — solid, weak, stale or missing — and refuses delivery while any blocking requirement is unsatisfied.

The category that catches people is **weak**: evidence that is a claim rather than a check. "Monitoring is set up" is not evidence of monitoring; it is an assertion offered by the person with the strongest reason to believe it. The same distinction Day 363 applied to a portfolio, turned on your own project.

## Learning objectives

- Rank evidence by whether somebody who does not trust you could check it.
- Explain why a document existing is not evidence that the work it describes was done.
- Treat undated evidence as ancient rather than fresh, and defend the asymmetry.
- Separate missing, weak and stale, because the remedy differs for each.
- Decide delivery on blocking requirements alone, while still reporting the rest.

## Prerequisites

- Days 358 to 365, the whole of week 52.
- Comfortable with Python dataclasses, enums and dates.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key, no network — the input is a written delivery manifest, and the gate deliberately does not execute the commands it records. See `security.md` for why.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/readiness.py        your work: seven stubbed tasks
examples/readiness.py       reference implementation
examples/readiness_demo.py  a capstone that feels finished, gated
tests/test_readiness.py     grouped by what the gate decides
tests/run_tests.sh          suite entry point
expected-output/            real captured output and measured values
requirements/               pinned dependency
```

## How to run

```bash
python3 examples/readiness_demo.py   # gate a delivery; exits 1 if not ready
bash tests/run_tests.sh              # run the suite
```

To work on the project, edit `starter/readiness.py`, then copy it over the reference:

```bash
cp starter/readiness.py examples/readiness.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/readiness_demo.py` gates ten requirements drawn from week 52 against a delivery in which nine of them have some evidence offered. It prints the verdict, the per-requirement table, and the findings — then exits 1, because the delivery is not ready.

`bash tests/run_tests.sh` runs `pytest` over twenty-four tests grouped by what the gate decides: evidence, age, picking the best evidence, sorting, blocking, and findings.

## Expected output

```text
--- delivery gate ---
  solid=4 weak=4 stale=1 missing=1  NOT READY (5 blocking)
--- by requirement ---
  solid   ! day 359  Deployed and reachable                 command
  stale   ! day 361  No secrets in repository history       command
  weak    ! day 359  A rollback that has been exercised     assertion
  weak    ! day 361  Security review completed              file
  missing ! day 360  A hard spend cap                       -
--- findings ---
  - NOT deliverable: 5 blocking requirement(s) of 10.
  - BLOCKING: 'A hard spend cap' (day 360) has no evidence at all.
  - BLOCKING: 'A rollback that has been exercised' (day 359) rests on an
    assertion. Replace it with a command, a URL or a measurement.
  - BLOCKING: 'No secrets in repository history' (day 361) was last verified
    78 days ago. Re-run it.
```

Nine of the ten requirements have *something* offered. The delivery is still not ready, and that gap is the whole point.

`expected-output/FIELDS.md` explains every field and where the line between checkable and not falls. `expected-output/measured-values.txt` records why each weak requirement is weak.

## Validation steps

1. `bash tests/run_tests.sh` reports `24 passed`.
2. The demo exits `1`. A gate that always exits 0 is not a gate.
3. Evidence with no `verified_on` must be treated as ancient. If undated claims come out fresh, the least verified evidence in the delivery passes silently.
4. A `COMMAND` with an empty detail must not count as checkable.
5. Listing the two pieces of `demo` evidence in the opposite order must not change the verdict — the best evidence wins, not the first.
6. An optional requirement with no evidence must still generate a finding and must not block delivery.

## Tests

Twenty-four tests in six groups:

- **evidence** — commands, URLs and measurements are checkable; assertions and bare files are not; a checkable kind with no detail is not.
- **age** — undated evidence is ancient; yesterday's is fresh; the staleness window is configurable.
- **picking the best** — the best evidence wins over the first listed; order does not change the verdict; another requirement's evidence does not count; an explicit `NONE` is the same as nothing.
- **sorting** — each requirement lands in exactly one category; missing is checked before weak and weak before stale.
- **blocking** — only blocking requirements stop delivery; one missing blocker is enough; blockers are ordered missing, weak, stale; a fully evidenced delivery is ready; no requirements is vacuously ready.
- **findings** — the verdict leads; a ready delivery gets one line; blocking and optional are marked differently; the weak evidence kind is named; staleness is reported in days.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: no network, no credentials, and the gate deliberately does not execute the commands it records — a delivery manifest is a document, and a tool that ran arbitrary strings out of one would be a code-execution vector.

## Extension exercises

1. **Write your own manifest.** List every requirement your capstone actually has, mark which are blocking, and record the honest evidence kind for each. Most people find two or three that are `assertion` and had felt finished.
2. **Add a `verify` command per requirement** and a runner that executes only an allowlisted set, in a sandbox, on a manifest you wrote yourself. Read `security.md` before you do.
3. **Make staleness per-requirement.** A deployment check goes stale in days; a threat model goes stale in months. One global window is a simplification the reference makes and your capstone probably should not.

## Navigation

- [Section README](../../README.md)
- Day 358 — Frontend and User Experience
- Day 365 — Graduation: Your AI Roadmap Going Forward
