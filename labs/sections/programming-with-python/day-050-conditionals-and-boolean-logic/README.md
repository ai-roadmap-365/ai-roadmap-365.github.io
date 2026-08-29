# Day 050 lab — Build a Decision Engine

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Conditionals and Boolean Logic
- **Day number:** 50 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-050-conditionals-and-boolean-logic
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-050-conditionals-and-boolean-logic` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 50's lesson teaches how a program decides: booleans, comparison and logical
operators, short-circuit evaluation, `if`/`elif`/`else`, the ternary, and guard
clauses. This lab makes that concrete: you build a **decision engine**,
`triage.py`, that classifies a model prediction into `AUTO_ACCEPT`, `REVIEW`, or
`REJECT` from a confidence score and a verification status. It reads input from
the command line, validates it with a chained comparison, rejects low confidence
with a guard clause, admits confident-and-verified predictions with a
short-circuiting `and`, labels the confidence band with a nested ternary, and
fails gracefully on bad input. You build it from a starter, one exercise at a
time, then run an automated test suite that checks real behaviour. This is the
routing shape that sits in front of real model-serving endpoints.

## Learning objectives

- Read and understand a complete, well-structured decision program.
- Produce booleans with comparison operators and a chained comparison
  (`0.0 <= score <= 1.0`).
- Combine booleans with `and` and rely on short-circuit evaluation.
- Reject bad input early with a guard clause, and choose values with a nested
  conditional (ternary) expression.
- Validate input at the boundary and report bad input with a clear message and
  a non-zero exit code.

## Prerequisites

- The Day 50 lesson (read it first — it explains every part this lab builds).
- Days 43-49: a working Python 3 install plus variables, strings, numbers,
  input/output, error messages, and assembling a small program with functions
  and a `main()` guard.
- A text editor and a terminal. No programming experience beyond this week is
  assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python 3.14).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python` for
  `python3` if that is how Python is exposed. The program is pure
  standard-library Python and behaves identically everywhere.

## Hardware requirements

Any computer that runs Python 3. The program does only comparisons and
arithmetic on two values; it needs no special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — the `sys` module ships with Python. No packages to
  install. See [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard library.
No account, API key, network access, or purchase is needed. The lesson's
optional linters (Ruff, Pylint, flake8), type checker (mypy), and test framework
(pytest) are all free and open source too.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-050-conditionals-and-boolean-logic
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-050-conditionals-and-boolean-logic/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── triage.py                   ← YOUR working file (5 numbered exercises)
│   └── decision-worksheet.md       ← design a second engine before coding it
├── examples/
│   └── triage.py                   ← complete reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (good + bad inputs, imports)
├── expected-output/
│   ├── sample-run.txt              ← real captured run of the reference
│   ├── test-run.txt                ← real captured run of the test suite
│   └── FIELDS.md                   ← required behaviour on every platform
├── requirements/
│   └── README.md                   ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished decision engine on good and bad input
python3 examples/triage.py 0.95 verified
python3 examples/triage.py 0.95 unverified
python3 examples/triage.py 0.30 verified
python3 examples/triage.py 1.5 verified       # invalid: prints an error, exits non-zero

# 2. Your task: complete the five exercises in the starter, then run it
python3 starter/triage.py 0.70 verified

# 3. Prove the module is importable (the payoff of the main guard)
python3 -c "import sys; sys.path.insert(0, 'examples'); from triage import classify; print(classify(0.95, True))"

# 4. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/triage.py 0.95 verified` — runs the complete reference
  program: it reads the score and status from the command line, validates them
  in `parse_args`, decides in `classify`, labels the band in `confidence_band`,
  formats with `format_result`, and prints
  `score=0.95 verified=True  -> AUTO_ACCEPT (confidence: high)`. Bad input (a
  non-number, a score outside 0.0–1.0, an unknown status, a missing argument)
  prints a clear error to standard error and exits with code 2.
- `python3 starter/triage.py 0.70 verified` — runs your version. The starter
  ships with five exercises stubbed out (each raising `NotImplementedError`
  until you finish it): write the ternary band, write the classification
  ladder, validate input, format output, and add the main guard.
- `python3 -c "...classify..."` — imports one function from the module and calls
  it, without running the whole program. This works only because the main guard
  holds `main` back on import.
- `bash tests/run_tests.sh` — runs the reference on nine good and bad inputs
  (checking output *and* exit code), imports two functions to check their return
  values, and checks your starter (structurally until you finish, strictly
  afterwards). Exits 0 only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a real
captured run:

```text
$ python3 examples/triage.py 0.95 verified
score=0.95 verified=True  -> AUTO_ACCEPT (confidence: high)

$ python3 examples/triage.py 1.5 verified   ; echo "exit: $?"
error: score 1.5 is out of range (expected 0.0 to 1.0)
usage: python3 triage.py <score> <status>   (score 0.0-1.0, status verified|unverified)
exit: 2
```

The decision prints to standard output; the error prints to standard error and
sets exit code 2. The program is deterministic, so your numbers will match
exactly. [`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the
required behaviour for every input on every platform.

## Validation steps

1. Run `python3 examples/triage.py 0.95 verified` — it must print `AUTO_ACCEPT`.
2. Run `python3 examples/triage.py 1.5 verified; echo $?` — it must print an
   error and then `2`.
3. Complete the five exercises in `starter/triage.py`, then run it on the same
   inputs and confirm it matches the reference.
4. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `14 checks, 0
failure(s).` Once you complete all five starter exercises, more checks run your
version through the same good/bad inputs plus the main-guard check, giving
`22 checks, 0 failure(s).` The command exits 0 on success and non-zero on any
failure, so it can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

Nothing to clean up: the program and tests read only their command-line
arguments and write nothing outside their own console output (no files, no
network, no settings). To reset your work, restore the starter from git:
`git checkout -- starter/triage.py`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `python` vs
`python3`, the deliberate `NotImplementedError` stubs, `=` vs `==`, branch
ordering, boundary comparisons, and exit-code checks.

## Security notes

See [security.md](security.md). Short version: the program makes no network
calls, writes no files, and needs no privileges. Its central lesson is to
**validate input at the boundary and never `eval()` it** — turn text into
numbers with `float()`, which cannot execute code.

## Extension exercises

1. Add a `De Morgan` simplification: write a condition both ways in a comment
   (`not (verified and score >= 0.9)` and `not verified or score < 0.9`) and add
   a test that runs the function over a grid of scores and flags and asserts the
   two forms always agree.
2. Add a new outcome, `ESCALATE`, for a very high score that is still
   unverified, and update both `classify` and `tests/run_tests.sh` to cover it.
3. Write your own `tests/test_triage.py` that imports the functions and asserts
   several known results with `assert`, printing `all tests passed` only if
   every assertion holds; run it with `python3 tests/test_triage.py`.

## Navigation

- **Previous day:** Day 49 — Your First Real Program
  (`labs/sections/programming-with-python/day-049-your-first-real-program/`).
- **Next day:** Day 51 — continues Week 8, Control Flow and Collections
  (`labs/sections/programming-with-python/day-051-.../`, to be written).
- **Week 8 project:** a rule-driven classifier that extends exactly this
  shape — parse input, validate, decide with clear boolean logic, print
  clearly, fail gracefully.
