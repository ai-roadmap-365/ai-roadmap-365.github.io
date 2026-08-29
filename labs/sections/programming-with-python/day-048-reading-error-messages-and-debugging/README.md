# Day 048 lab — Read the Traceback, Fix the Bug

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Reading Error Messages and Debugging
- **Day number:** 48 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-048-reading-error-messages-and-debugging
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-048-reading-error-messages-and-debugging` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 48's lesson teaches you to read a Python traceback bottom-up and to debug
methodically. This lab makes it concrete: you are handed three tiny Python
programs, each of which crashes with a **different** common exception. You run
each one, read its real traceback, diagnose the cause, and fix it — the exact
loop you will run thousands of times over your career.

## Learning objectives

- Trigger and read three real tracebacks, one each for `IndexError`, `KeyError`, and `TypeError`.
- Identify, from a traceback, the exception type, the culprit line number, and the failing line of code.
- Diagnose the underlying cause of each bug and apply a correct fix.
- Record your reasoning (type, line, cause, fix) in a structured worksheet.
- Run an automated test that confirms the buggy programs fail as expected and the fixed programs succeed.

## Prerequisites

- The Day 48 lesson (read it first — it explains how to read a traceback).
- Days 43–47: Python installed and comfort running small programs.
- A terminal and a text editor. No debugging experience required.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python 3.14.0).
- **Linux** — fully supported (any distribution with `python3` and `bash`).
- **Windows** — use `py` or `python` in place of `python3`; run the shell scripts inside WSL, or run the Python files directly. The exceptions and line numbers are identical.

## Hardware requirements

Any computer that can run Python. The programs are a few lines each and use no
meaningful memory, disk, or network.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0). Check with `python3 --version`.
- `bash` (for the walkthrough and test scripts — preinstalled on macOS and Linux).

## Free and open-source options

Everything here is free and built in: Python and bash ship with your system or
install for free. No account, API key, network access, or purchase is needed.

## Installation

None beyond Python itself (installed on Day 43). Clone the repository (or copy
this directory) and you are ready:

```bash
cd labs/sections/programming-with-python/day-048-reading-error-messages-and-debugging
```

## File structure

```text
day-048-reading-error-messages-and-debugging/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── average_scores.py           ← YOUR copy to fix (IndexError)
│   ├── lookup_capital.py           ← YOUR copy to fix (KeyError)
│   ├── total_price.py              ← YOUR copy to fix (TypeError)
│   └── debug-worksheet.md          ← record type, line, cause, and fix
├── examples/
│   ├── buggy/                      ← reference broken programs (keep them broken)
│   │   ├── average_scores.py
│   │   ├── lookup_capital.py
│   │   └── total_price.py
│   ├── fixed/                      ← reference working versions
│   │   ├── average_scores.py
│   │   ├── lookup_capital.py
│   │   └── total_price.py
│   └── debug_walkthrough.sh        ← reads each traceback, then runs the fixes
├── tests/
│   └── run_tests.sh                ← automated checks
├── expected-output/
│   ├── tracebacks.txt              ← the three real tracebacks
│   ├── walkthrough.txt             ← full walkthrough output
│   └── FIELDS.md                   ← what must be true on every platform
├── requirements/
│   └── README.md                   ← dependency statement (python3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See a real traceback with your own eyes
python3 examples/buggy/average_scores.py

# 2. Watch the guided walkthrough read all three, then run the fixes
bash examples/debug_walkthrough.sh

# 3. Your task: fix the three programs in starter/, filling in the worksheet
python3 starter/average_scores.py     # read the traceback, then edit the file
python3 starter/lookup_capital.py
python3 starter/total_price.py

# 4. Check your work (and confirm the samples still behave)
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/buggy/average_scores.py` — runs a deliberately broken program so you see a genuine traceback. It exits non-zero with an `IndexError`.
- `bash examples/debug_walkthrough.sh` — runs all three buggy programs, extracts each exception type and culprit line (reading the traceback bottom-up), then runs the three fixed versions to show they succeed.
- `python3 starter/<name>.py` — runs your copy; read the traceback, edit the line marked `BUG`, and re-run until it succeeds.
- `bash tests/run_tests.sh` — verifies each buggy program raises its expected exception (non-zero exit and the exception name in stderr) and each fixed program runs cleanly (exit 0). Exits 0 on success.

## Expected output

The three buggy programs produce these exceptions (see `expected-output/tracebacks.txt` for the full tracebacks):

```text
examples/buggy/average_scores.py → IndexError: list index out of range   (line 5)
examples/buggy/lookup_capital.py → KeyError: 'Germany'                    (line 6)
examples/buggy/total_price.py    → TypeError: can only concatenate str (not "int") to str   (line 4)
```

The walkthrough's full output is captured in `expected-output/walkthrough.txt`. The `File "..."` path in a traceback shows the path you ran on your own machine; only that wording differs from the captures.

## Validation steps

1. Run each buggy program and confirm it crashes with the exception above.
2. For each program, fill in the matching row of `starter/debug-worksheet.md` (type, line, cause, fix).
3. Edit each starter program so it runs without raising an exception.
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `9 checks, 0 failure(s).` (three buggy programs checked for the right exception, three fixed programs checked for a clean exit). The command exits 0 on success and non-zero on any failure, so it can run in CI. It makes no network calls.

## Cleanup

Nothing to clean up: the programs write no files and make no network calls. To reset your work and the reference samples, restore them from git:

```bash
git checkout -- starter examples/buggy
```

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (`python3` not found, a fix revealing a second bug, editing the wrong copy, locating the error line).

## Security notes

See [security.md](security.md). Short version: never run untrusted `.py` files; these samples are tiny, local, read no input, touch no network, and are safe to read and run.

## Extension exercises

1. Add `breakpoint()` before the loop in a broken copy of `average_scores.py`, run it, and use `p scores`, `p i`, and `n` to watch the index walk off the end.
2. Fix `lookup_capital.py` a different way — add `"Germany"` to the dictionary — and decide which fix is better for which situation.
3. Write a fourth buggy program that raises a `ValueError` (for example `int("hello")`), predict the traceback, then run it to check.

## Navigation

- **Previous day:** Day 47 — Input, Output, and f-strings (`labs/sections/programming-with-python/day-047-input-output-and-f-strings/`).
- **Next day:** Day 49 — Your First Real Program (`labs/sections/programming-with-python/day-049-your-first-real-program/`).
