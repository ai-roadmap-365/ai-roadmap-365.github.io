# Lab — Day 362: Documentation and Demo

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Documentation and Demo
- **Day number:** 362 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-362-documentation-and-demo
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-362-documentation-and-demo` when the site is running.
<!-- generated-links:end -->

## Purpose

Build a checker that verifies documentation still describes the system it documents — required sections, commands that exist, outputs that match reality, no placeholder text, and known limitations actually stated.

The subject is a README plus a small description of the project, so the check runs without executing anything.

## Learning objectives

- Extract commands and claimed outputs from Markdown, distinguishing instructions from output.
- Verify every documented command exists and every claimed output matches a real capture.
- Enforce a required-section list and reject placeholder text.
- Check known limitations are stated rather than merely known.
- Justify treating incompleteness as a warning and wrongness as a failure.

## Prerequisites

- Day 361, "Security Review of Your Capstone".
- Comfortable with Python regular expressions and dataclasses.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key, no network. The lesson discusses MkDocs, Sphinx, Docusaurus, Vale and asciinema as the real tooling, all free and open source.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/doccheck.py          your work: extraction plus three checks
examples/doccheck.py         reference implementation
examples/fixtures.py         a project, a good README and a drifted one
examples/doccheck_demo.py    checks both READMEs
tests/test_doccheck.py       grouped by check, plus extraction tests
tests/run_tests.sh           suite entry point
expected-output/             real captured output and measured values
requirements/                pinned dependency
```

## How to run

```bash
python3 examples/doccheck_demo.py   # check a good README and a drifted one
bash tests/run_tests.sh             # run the suite
```

To work on the exercise, edit `starter/doccheck.py`, then copy it over the reference:

```bash
cp starter/doccheck.py examples/doccheck.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/doccheck_demo.py` runs all six checks against a current README and one that has drifted over six months, printing each finding and a verdict for both.

`bash tests/run_tests.sh` runs `pytest` over sixteen tests: four on the extraction functions, one on the clean case, seven covering each check independently, and four on the drifted README.

## Expected output

```text
--- current README ---
  OK    sections: all required sections present
  OK    commands: 3 documented command(s) all exist
  OK    undocumented_commands: every provided command is documented
  OK    outputs: claimed outputs match captured output
  OK    placeholders: no placeholder text
  OK    limitations: every known limitation is stated
  => PASS fail=0 warn=0
--- README after six months of drift ---
  FAIL  sections: missing: Limitations
  FAIL  commands: documented but not provided: make setup, make serve
  WARN  undocumented_commands: provided but undocumented: make install, make run, make test
  FAIL  outputs: make run (differs from captured)
  FAIL  placeholders: unfinished text: to be written, under construction
  FAIL  limitations: known but unstated: English only, no multi-tenant isolation
  => FAIL fail=5 warn=1
```

`expected-output/FIELDS.md` explains the fields and the warn-versus-fail distinction.

## Validation steps

1. `bash tests/run_tests.sh` reports `16 passed`.
2. The current README must produce **zero** findings. If it reports its own examples as unknown commands, your extractor is treating output blocks as instructions.
3. A project with one extra undocumented command must still pass — a warning alone does not fail.
4. Every claimed output must resolve to a captured one. If they all report "no captured output", your output pattern is matching across newlines.

## Tests

Sixteen tests in four groups:

- **extraction** — only shell-tagged blocks are commands; prompts and comments are stripped; a claimed output matches one command rather than the whole document; sections are read in order.
- **the good case** — a current README passes with no findings.
- **each check on its own** — missing sections, a renamed command, an undocumented command (warn only), a changed output, an output with nothing captured, placeholder text, an unstated limitation, and no limitations recorded.
- **the drift** — the drifted README fails on five checks, names all six, and a warning alone does not fail.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`, including the two extraction bugs this lab had before its own tests caught them.

## Security notes

See `security.md`. In short: no network, no credentials — and the lesson covers documentation as a disclosure surface.

## Extension exercises

1. **Link checking.** Verify relative links point at paths the project contains, skipping external `http` links so the gate does not need the network.
2. **Executable checks.** Run each documented command and compare live output, then measure how many false failures that produces over ten runs before deciding whether it belongs in a pipeline.
3. **Staleness.** Record when each section was last edited and warn when a section has not changed while the code it describes has.

## Navigation

- [Lesson](../../../../content/sections/capstone/day-362-documentation-and-demo/README.md)
- Previous: Day 361 — Security Review of Your Capstone
- Next: Day 363 — Portfolio, Resume, and Sharing Your Work
