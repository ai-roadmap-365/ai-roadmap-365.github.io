# Lab — Day 324: Document Processing at Scale

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Document Processing at Scale
- **Day number:** 324 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-324-document-processing-at-scale
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-324-document-processing-at-scale` when the site is running.
<!-- generated-links:end -->

## Purpose

Build a document processing pipeline that turns arbitrary files into clean text without silently corrupting anything. You implement byte-level format detection, a per-format extractor registry, a hard time budget enforced by a process you can actually kill, and a quality gate with three outcomes.

Everything runs offline against eight synthetic documents. Each one reproduces a real failure: a scan with no text layer, mojibake, a file that never returns, and an unknown format.

## Learning objectives

- Detect a document's real format from its leading bytes rather than its name.
- Dispatch to per-format extractors through a registry instead of a growing conditional.
- Enforce a per-document budget from the harness, and understand why a thread cannot provide one.
- Score extracted text on yield, alphabetic ratio and word length.
- Justify three outcomes — accepted, flagged, dead — over a binary decision.

## Prerequisites

- Day 323, "Data Ingestion Pipelines".
- Comfortable with Python dataclasses and exceptions.
- Aware of what `multiprocessing` does, though the lab supplies the harness.

## Supported operating systems

macOS, Linux and Windows (via WSL). The budget uses `multiprocessing`, which behaves consistently across all three; on Windows and macOS the child is spawned rather than forked, which the code accounts for.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU. Peak memory is a few megabytes.

## Required software

- Python 3.10 or newer (uses `X | None` type syntax).
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key, no hosted service. The lesson discusses Tesseract, pdfplumber and Docling as the real-world open-source options; none is required here.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/process.py         your work: detect, score, process_one
examples/process.py        reference implementation
examples/corpus.py         eight synthetic documents
examples/process_demo.py   runs the corpus and prints the table
tests/test_process.py      grouped by concern
tests/run_tests.sh         suite entry point
expected-output/           real captured output and measured values
requirements/              pinned dependency
```

## How to run

```bash
python3 examples/process_demo.py    # process the corpus
bash tests/run_tests.sh             # run the suite
```

To work on the exercise, edit `starter/process.py`, then copy it over the reference:

```bash
cp starter/process.py examples/process.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/process_demo.py` processes eight documents and prints one line each plus a summary. It takes about 2.4 seconds, almost all of which is `doc-06.slow` exhausting its 2-second budget before being terminated.

`bash tests/run_tests.sh` runs `pytest` over fourteen tests grouped by concern — detection, dispatch, budget, scoring and gating — so a failure names what is broken.

## Expected output

```text
doc-01.txt      accepted   yield=1.00 alpha=0.98 words=4.8
doc-02.pdf      accepted   yield=0.98 alpha=0.98 words=4.8
doc-03.scan     flagged    yield=0.02 alpha=0.81 words=3.2   low text yield
doc-04.bin      flagged    yield=1.00 alpha=0.00 words=600.0   low alphabetic ratio
doc-05.html     accepted   yield=0.61 alpha=0.98 words=5.3
doc-06.slow     dead       timeout after 2.00s
doc-07.xyz      dead       no extractor for format 'unknown'
doc-08.pdf      accepted   yield=0.96 alpha=0.98 words=4.8
summary: accepted=4 flagged=2 dead=2
```

The two flagged documents are caught by *different* signals: the scan by yield alone (its few characters are all letters), the mojibake by alphabetic ratio alone (every byte decoded, so its yield is perfect). `expected-output/FIELDS.md` explains every column.

## Validation steps

1. `bash tests/run_tests.sh` reports `14 passed`.
2. Time the demo: it must finish in roughly 2 to 3 seconds. If it takes 30, your budget is not being enforced — the pathological extractor sleeps for 30 seconds.
3. Confirm `doc-04.bin` is `flagged` and not `accepted`. Extraction "succeeded" for it, which is exactly why the gate exists.

## Tests

Fourteen tests in five groups:

- **detect** — content is read rather than the extension; a scan is distinguished from a born-digital PDF.
- **dispatch** — an unknown format is dead-lettered rather than raising.
- **budget** — the pathological document times out in well under five seconds, and the rest of the run still completes.
- **score** — empty text does not divide by zero; yield is a ratio; the alphabetic ratio counts only letters.
- **gate** — each flagged document is caught by the expected signal, flagged documents keep their text, and the summary counts all three outcomes.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md` for each failure this lab is designed to produce.

## Security notes

See `security.md`. In short: no network, no credentials, no API key, and extraction runs in a child process — which is also how you would contain a real parser handling untrusted input.

## Extension exercises

1. **A fifth signal.** Add a repetition ratio to catch a page header repeated once per page, which passes all four existing signals. Prove the gap first, then close it.
2. **Escalation.** Add a slow but capable second extractor and route only flagged documents to it. Measure how many documents were recovered and what it cost, and report the real numbers.
3. **Memory budget.** Add a memory ceiling alongside the time budget using `resource.setrlimit` in the child, and a document that would exceed it.

## Navigation

- [Lesson](../../../../content/sections/ai-engineering/day-324-document-processing-at-scale/README.md)
- Previous: Day 323 — Data Ingestion Pipelines
- Next: Day 325 — Keeping Indexes Fresh
