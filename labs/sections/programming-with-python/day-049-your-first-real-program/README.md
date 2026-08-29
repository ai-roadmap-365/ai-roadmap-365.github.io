# Day 049 lab — Build a Complete Small Program

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Your First Real Program
- **Day number:** 49 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-049-your-first-real-program
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-049-your-first-real-program` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 49's lesson assembles a week of Python pieces into one whole. This lab
makes that concrete: you build a **temperature converter** — a genuinely
complete, small, real program that reads input from the command line,
validates it, does one useful job, prints clear output, and fails
gracefully on bad input. You build it from a starter, one exercise at a
time, then run an automated test suite that checks real behaviour. This is
the shape the Week 7 project (the Command-Line Calculator) is built on.

## Learning objectives

- Read and understand a complete, well-structured Python program.
- Write small named functions with docstrings and a `main()` that ties them
  together.
- Add the `if __name__ == "__main__":` guard and explain why it makes the
  program both runnable and importable (hence testable).
- Validate input at the boundary and report bad input with a clear message
  and a non-zero exit code.
- Test a program without a human: run it on known inputs and import a
  function to check its return value.

## Prerequisites

- The Day 49 lesson (read it first — it explains every part this lab
  builds).
- Days 43-48: a working Python 3 install plus variables, strings, numbers,
  input/output, and reading error messages.
- A text editor and a terminal. No programming experience beyond this week
  is assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python
  3.14).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python`
  for `python3` if that is how Python is exposed. The program itself is pure
  standard-library Python and behaves identically everywhere.

## Hardware requirements

Any computer that runs Python 3. The program does only arithmetic on two
numbers; it needs no special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — the `sys` module ships with Python. No packages to
  install. See [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. No account, API key, network access, or purchase is needed.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-049-your-first-real-program
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-049-your-first-real-program/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── converter.py                ← YOUR working file (5 numbered exercises)
│   └── program-worksheet.md        ← design the program before coding it
├── examples/
│   └── converter.py                ← complete reference implementation
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
# 1. See the finished program first, on good and bad input
python3 examples/converter.py 100 C
python3 examples/converter.py 32 F
python3 examples/converter.py hot C          # prints an error, exits non-zero

# 2. Your task: complete the five exercises in the starter, then run it
python3 starter/converter.py 212 F

# 3. Prove the module is importable (the payoff of the main guard)
python3 -c "import sys; sys.path.insert(0, 'examples'); from converter import celsius_to_fahrenheit; print(celsius_to_fahrenheit(100))"

# 4. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/converter.py 100 C` — runs the complete reference
  program: it reads the value and unit from the command line, validates
  them in `parse_args`, converts in `convert`, formats with `format_result`,
  and prints `100.0 C = 212.0 F`. Bad input (`hot C`, `100 K`, a missing
  argument, a temperature below absolute zero) prints a clear error to
  standard error and exits with code 1.
- `python3 starter/converter.py 212 F` — runs your version. The starter
  ships with five exercises stubbed out (each raising `NotImplementedError`
  until you finish it): write a conversion function, add the main guard,
  validate input, format output, and handle an edge case.
- `python3 -c "...celsius_to_fahrenheit..."` — imports one function from the
  module and calls it, without running the whole program. This works only
  because the main guard holds `main` back on import.
- `bash tests/run_tests.sh` — runs the reference on seven good and bad
  inputs (checking output *and* exit code), imports two functions to check
  their return values, and checks your starter (structurally until you
  finish, strictly afterwards). Exits 0 only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured run:

```text
$ python3 examples/converter.py 100 C
100.0 C = 212.0 F

$ python3 examples/converter.py hot C   ; echo "exit: $?"
error: 'hot' is not a number
usage: python3 converter.py <value> <unit>   (unit is C or F)
exit: 1
```

The conversion prints to standard output; the error prints to standard
error and sets exit code 1. The program is deterministic, so your numbers
will match exactly. [`expected-output/FIELDS.md`](expected-output/FIELDS.md)
lists the required behaviour for every input on every platform.

## Validation steps

1. Run `python3 examples/converter.py 100 C` — it must print
   `100.0 C = 212.0 F`.
2. Run `python3 examples/converter.py hot C; echo $?` — it must print an
   error and then `1`.
3. Complete the five exercises in `starter/converter.py`, then run it on the
   same inputs and confirm it matches the reference.
4. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `12 checks, 0
failure(s).` Once you complete all five starter exercises, six more checks
run your version through the same good/bad inputs plus the main-guard check,
giving `18 checks, 0 failure(s).` The command exits 0 on success and
non-zero on any failure, so it can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

Nothing to clean up: the program and tests read only their command-line
arguments and write nothing outside their own console output (no files, no
network, no settings). To reset your work, restore the starter from git:
`git checkout -- starter/converter.py`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `python` vs
`python3`, the deliberate `NotImplementedError` stubs, importing vs running,
keeping tests non-interactive, and exit-code checks.

## Security notes

See [security.md](security.md). Short version: the program makes no network
calls, writes no files, and needs no privileges. Its central lesson is to
**validate input and never `eval()` it** — turn text into numbers with
`float()`, which cannot execute code.

## Extension exercises

1. Write your own `tests/test_converter.py` that imports the conversion
   functions and asserts several known results, printing `all tests passed`
   only if every assertion holds; run it with `python3 tests/test_converter.py`.
2. Make the program self-documenting: running it with no arguments or
   `--help` should print the usage line and docstring and exit 0.
3. Run the program as a module with `python3 -m converter 100 C` (from the
   folder containing the file) and confirm it behaves identically to running
   it by path.

## Navigation

- **Previous day:** Day 48 — Reading Error Messages and Debugging
  (`labs/sections/programming-with-python/day-048-reading-error-messages-and-debugging/`).
- **Next day:** Day 50 — begins Week 8, Control Flow and Collections
  (`labs/sections/programming-with-python/day-050-.../`, to be written).
- **Week 7 project:** the Command-Line Calculator, which extends exactly this
  program shape — parse input, validate, compute, print clearly, fail
  gracefully.
