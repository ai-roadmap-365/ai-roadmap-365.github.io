# Lab — Day 361: Security Review of Your Capstone

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Security Review of Your Capstone
- **Day number:** 361 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-361-security-review-of-your-capstone
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-361-security-review-of-your-capstone` when the site is running.
<!-- generated-links:end -->

## Purpose

Build a defensive security review for an AI application: seven checks over a described configuration, each producing a finding with a severity and a remediation.

Everything here describes a system and reports weaknesses so they can be fixed. There is no exploit code, and nothing attacks anything. The subject is a `Posture` — a flat description — so the review can run against a design document before any code exists, which is when changes are cheapest.

## Learning objectives

- Express a system's security decisions as a reviewable posture.
- Implement seven checks, each owning exactly one failure class.
- Weight severity by blast radius rather than sophistication.
- Attach a remediation to every finding.
- Prove the review can fail, by running it against a deliberately weak configuration.

## Prerequisites

- Day 360, "Monitoring and Cost Controls".
- Day 328, "Privacy in AI Systems", for the retention and redaction concepts.
- Comfortable with Python dataclasses and enums.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key, no network. The lesson points at the OWASP Top 10 for LLM Applications as the reference list, and at gitleaks, Trivy, Semgrep and Bandit as the tools worth adding to a real project.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/review.py         your work: the seven check functions
examples/review.py        reference review, plus a sound and a weak posture
examples/review_demo.py   reviews both, then changes one setting at a time
tests/test_review.py      grouped by check, plus "the review can fail"
tests/run_tests.sh        suite entry point
expected-output/          real captured output and measured values
requirements/             pinned dependency
```

## How to run

```bash
python3 examples/review_demo.py   # review both postures
bash tests/run_tests.sh           # run the suite
```

To work on the exercise, edit `starter/review.py`, then copy it over the reference:

```bash
cp starter/review.py examples/review.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/review_demo.py` runs all seven checks against a sound posture and a deliberately weak one, printing each finding with its remediation, then makes three single-setting changes to a sound posture to show each check firing in isolation.

`bash tests/run_tests.sh` runs `pytest` over eighteen tests in three groups: the sound baseline, one test per check catching its own flaw, and a group proving the review can fail.

## Expected output

```text
--- sound posture ---
  OK      untrusted_content_boundary: retrieved content is marked untrusted
  OK      output_handling: output is escaped and never executed
  ...
  => PASS high=0 medium=0 low=0
--- weak posture ---
  HIGH    tool_permissions: state-changing scopes granted without confirmation:
          write:tickets, delete:records
          fix: grant the narrowest scope the task needs, and require explicit
          confirmation for anything that writes, deletes or spends
  ...
  => FAIL high=6 medium=1 low=0
--- one change at a time ---
  drop the spend caps                    FAIL high=1   ['spend_bounds']
  grant delete without confirmation      FAIL high=1   ['tool_permissions']
  keep traces forever                    FAIL high=0 medium=1
```

`expected-output/FIELDS.md` explains each field and the severity scale.

## Validation steps

1. `bash tests/run_tests.sh` reports `18 passed`.
2. The sound posture must report zero findings and the weak one must trip **all seven** — precision as well as recall.
3. Each isolation run must produce exactly one finding. If changing one setting lights up several checks, they are reading overlapping fields and cannot be prioritised.
4. Every failing finding must carry a remediation.

## Tests

Eighteen tests in three groups:

- **the sound baseline** — a clean posture passes with no findings, and all seven checks run.
- **each check catches its own flaw** — one test per check, asserting the finding set is exactly that check.
- **severity and the ability to fail** — severity tracks blast radius, one missing cap is less severe than two, a confirmed destructive scope is only low, the weak posture fails loudly and trips every check, and failing findings carry remediations.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: this lab is entirely defensive, contains no exploit code, and its own subject is a fictional configuration.

## Extension exercises

1. **A rate-limiting check.** Add per-user and per-IP limits, and prove a posture with spend caps but no rate limits still fails — a cap bounds cost, not concurrency.
2. **A prioritised remediation plan.** Order findings by consequence per unit of effort rather than by severity alone.
3. **Review your own capstone.** Write its posture honestly, run the review, and record any finding you decide not to fix along with the reason.

## Navigation

- [Lesson](../../../../content/sections/capstone/day-361-security-review-of-your-capstone/README.md)
- Previous: Day 360 — Monitoring and Cost Controls
- Next: Day 362 — Documentation and Demo
