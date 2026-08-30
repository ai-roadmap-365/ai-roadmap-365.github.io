# Lab — Day 328: Privacy in AI Systems

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Privacy in AI Systems
- **Day number:** 328 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-328-privacy-in-ai-systems
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-328-privacy-in-ai-systems` when the site is running.
<!-- generated-links:end -->

## Purpose

Build the three controls that keep personal data manageable in a retrieval system: redaction at the boundary, a data-flow record, and erasure that is verified rather than assumed.

Everything runs offline against synthetic identifiers that are invalid by construction — `example.com` is a reserved domain, `192.0.2.0/24` is the reserved TEST-NET-1 range, and the card number fails the Luhn check.

This lab is defensive throughout: the detectors exist to find personal data so it can be removed, and the audit exists to prove a deletion landed.

## Learning objectives

- Detect and pseudonymise identifiers before data fans out into derived stores.
- Order detectors so a shorter pattern cannot partially consume a longer identifier.
- Produce stable, salted, non-reversible pseudonyms.
- Track which stores hold data for which subject.
- Verify an erasure by reading back, and report the stores that still hold the subject.

## Prerequisites

- Day 327, "Cost Engineering for AI Systems".
- Day 325, "Keeping Indexes Fresh" — deletion propagation is the same problem seen from a different angle.
- Comfortable with Python regular expressions, dataclasses and sets.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key, no hosted service — nothing leaves the machine, which is the correct property for a lab about personal data. The lesson discusses Microsoft Presidio (MIT), spaCy (MIT) and scrubadub (Apache-2.0) as the real-world options.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/privacy.py         your work: pseudonym, redact, erase, minimise
examples/privacy.py        reference implementation
examples/privacy_demo.py   redacts a ticket, tracks flow, verifies erasure
tests/test_privacy.py      grouped by control
tests/run_tests.sh         suite entry point
expected-output/           real captured output and measured values
requirements/              pinned dependency
```

## How to run

```bash
python3 examples/privacy_demo.py   # redact, track, erase
bash tests/run_tests.sh            # run the suite
```

To work on the exercise, edit `starter/privacy.py`, then copy it over the reference:

```bash
cp starter/privacy.py examples/privacy.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/privacy_demo.py` redacts a synthetic support ticket containing five categories of identifier, shows that pseudonyms are stable across records, records a subject into four stores, then runs an erasure twice — first against the two stores someone would remember, then against all of them.

`bash tests/run_tests.sh` runs `pytest` over nineteen tests grouped by control: detection, pseudonyms, data flow, erasure and minimisation.

## Expected output

```text
--- redacted ---
From: [email:c4e2790ada]
Phone: [phone:749f96d705]
Card ending [card:1442489716] was charged twice.
Reported from [ip:555fff71c9]. Reference SSN [national_id:8975e0fdf2].
findings: card=1 email=1 ip=1 national_id=1 phone=1
pseudonym stable across records: True
--- data flow ---
subject-42 present in: ['audit_log', 'database', 'response_cache', 'vector_index']
--- erasure, first attempt (the stores someone remembered) ---
INCOMPLETE deleted_from=2 still_present=audit_log,response_cache
--- erasure, complete ---
COMPLETE deleted_from=2 still_present=none
--- minimisation ---
kept: {'tier': 'pro'}
```

The `INCOMPLETE` line is the reason the lab exists. `expected-output/FIELDS.md` explains each part.

## Validation steps

1. `bash tests/run_tests.sh` reports `19 passed`.
2. Confirm no fragment of any original identifier survives the redaction — including the leading `+` on the phone number, which a naive word-boundary pattern leaves behind.
3. Run an erasure against a subset of stores and confirm it reports `INCOMPLETE` and names the stores still holding the subject. If it reports success, you are reporting from the delete calls rather than a read-back.

## Tests

Nineteen tests in five groups:

- **detection** — every category is found, nothing of the original survives, the leading `+` is consumed, clean text is untouched, and a card is not partly eaten by the phone detector.
- **pseudonyms** — stable for the same value, different for different values, salted, and containing nothing of the original.
- **data flow** — records every store, is per subject, and does not duplicate.
- **erasure** — a partial run reports `INCOMPLETE` and names what remains; a full run is verified; an unknown subject is harmless.
- **minimisation** — keeps only named fields, tolerates absent ones, and can keep nothing.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md` for each failure this lab is designed to produce, including the hexadecimal false alarm that can make a correct redactor look broken.

## Security notes

See `security.md`. In short: nothing leaves the machine, every fixture identifier is invalid by construction, and the salt is treated as the secret it is.

## Extension exercises

1. **Retention policy.** Give each store a maximum age and report subjects held past it — and report a store with *no* declared policy as a finding rather than treating it as unlimited.
2. **Re-identification risk.** Score quasi-identifier combinations and flag records that are unique or near-unique, demonstrating Sweeney's result on your own fixture.
3. **Redaction recall.** Add free-text names, which patterns cannot catch, and measure what fraction of identifiers the detectors miss. The gap is the argument for entity recognition.

## Navigation

- [Lesson](../../../../content/sections/ai-engineering/day-328-privacy-in-ai-systems/README.md)
- Previous: Day 327 — Cost Engineering for AI Systems
- Next: Day 329 — Section Project: A Production Assistant
