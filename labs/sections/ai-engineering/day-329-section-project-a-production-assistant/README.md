# Lab — Day 329: Section Project: A Production Assistant

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Section Project: A Production Assistant
- **Day number:** 329 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-329-section-project-a-production-assistant
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-329-section-project-a-production-assistant` when the site is running.
<!-- generated-links:end -->

## Purpose

Build a conformance auditor for the three seams of a production assistant.

The week 47 project *builds* an assistant. This lab *checks* one — a different skill, and the one you need when reviewing someone else's system, or your own six months later. Each check targets an interaction no single stage's tests can reach.

The auditor is run against two assistants: one that conforms, and one deliberately broken in three specific ways. The second matters more, because an auditor that has never caught anything is not evidence of anything.

## Learning objectives

- Express a system property as an executable check rather than a review comment.
- Verify that redaction precedes indexing, by inspecting what actually reached the chunks.
- Verify that retrieval and generation share one ledger, so no paid path escapes the cap.
- Verify an erasure by reading back from every store rather than trusting the delete calls.
- Demonstrate that a checker catches real defects, and exactly those defects.

## Prerequisites

- Days 323 to 328 — each check corresponds to one of them.
- Comfortable with Python dataclasses, and able to read a `Protocol`.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key, no network.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/seam_audit.py         your work: the five check functions
examples/seam_audit.py        reference auditor plus two assistants to audit
examples/seam_audit_demo.py   audits both and prints the verdicts
tests/test_seam_audit.py      the auditor passes good, catches broken
tests/run_tests.sh            suite entry point
expected-output/              real captured output and measured values
requirements/                 pinned dependency
```

## How to run

```bash
python3 examples/seam_audit_demo.py   # audit both assistants
bash tests/run_tests.sh               # run the suite
```

To work on the exercise, edit `starter/seam_audit.py`, then copy it over the reference:

```bash
cp starter/seam_audit.py examples/seam_audit.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/seam_audit_demo.py` runs all five checks against `ConformantAssistant` and then against `BrokenAssistant`, printing a line per check and a verdict for each.

`bash tests/run_tests.sh` runs `pytest` over twelve tests in three groups: the auditor passes a conformant system, the auditor catches a broken one, and the reference assistant itself behaves correctly.

## Expected output

```text
--- conformant assistant ---
  PASS  redaction_before_indexing
  PASS  shared_budget
  PASS  erasure_is_complete
  PASS  cursor_advances_on_failure
  PASS  no_orphans_on_shrink
CONFORMANT (5/5 checks passed)
--- broken assistant ---
  FAIL  redaction_before_indexing -- 2 chunk(s) contain an address: ['policy::0', 'policy::1']
  FAIL  shared_budget -- retrieval is not charged to the request ledger
  FAIL  erasure_is_complete -- still present in: cache
  PASS  cursor_advances_on_failure
  PASS  no_orphans_on_shrink
NON-CONFORMANT (2/5 checks passed)
```

`expected-output/FIELDS.md` explains each field and why two assistants are audited.

## Validation steps

1. `bash tests/run_tests.sh` reports `12 passed`.
2. The conformant assistant must pass all five checks; the broken one must fail **exactly three** — the three planted defects and no others. An auditor that fails everything is as useless as one that fails nothing.
3. Every `FAIL` must carry a detail naming what was found. A failure without a detail is a bug report nobody can act on.

## Tests

Twelve tests in three groups:

- **the auditor passes good** — a conformant assistant is `CONFORMANT`, and all five checks actually run.
- **the auditor catches broken** — each of the three planted defects is detected with an informative detail, and the failure list is exactly those three.
- **the reference assistant** — idempotent ingest, cursor advances past a dead letter, erasure clears all three stores, a shrinking document leaves no orphans, and a cached answer is free and recorded.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: no network, no credentials, and the only identifier in the fixtures uses the reserved `example.com` domain.

## Extension exercises

1. **A fourth defect.** Add a `BrokenAssistant` variant that leaves orphans on shrink, and confirm the audit catches it without any change to the checks.
2. **Audit the week 47 project.** Point the auditor at the assistant you built for the project. It should be conformant — and if it is not, you have found something worth fixing.
3. **Severity.** Give each check a severity and make the verdict distinguish a warning from a blocker, so an audit can gate a deployment rather than only report.

## Navigation

- [Lesson](../../../../content/sections/ai-engineering/day-329-section-project-a-production-assistant/README.md)
- Previous: Day 328 — Privacy in AI Systems
- Next: Day 330 — Docker Fundamentals
