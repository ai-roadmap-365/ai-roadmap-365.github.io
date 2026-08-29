# Day 047 lab — A Friendly CLI Greeter/Calculator

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Input, Output, and f-strings
- **Day number:** 47 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-047-input-output-and-f-strings
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-047-input-output-and-f-strings` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 47's lesson explains how a program talks to people and to pipes. This lab
makes it concrete: you build `io_demo.py`, a small command-line tool that reads
two numbers **either** from a command-line argument **or** from standard input,
converts them safely, and prints a neatly f-string-formatted, aligned report —
sending errors to standard error and exiting non-zero on bad input. It is a
miniature of every well-behaved Unix command-line tool.

## Learning objectives

- Read input from `sys.argv` and from `sys.stdin`, and choose which fits.
- Convert text input to numbers safely with `float()`, and see why `input()`
  returning a string matters.
- Format numbers into aligned, fixed-decimal columns with f-string format specs.
- Route results to standard output and errors to standard error, and exit with a
  non-zero code on failure.
- Test a non-interactive program by driving it with pipes and arguments.

## Prerequisites

- The Day 47 lesson (read it first — it explains every concept this lab uses).
- Days 43–46: a working Python 3, variables, strings, and numbers.
- Day 10: the shell and pipes.
- A terminal: Terminal.app (macOS), any terminal (Linux), or PowerShell/WSL
  (Windows).

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Python 3.14).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — run the Python program directly in PowerShell
  (`python examples\io_demo.py 5 7`), or run everything unmodified inside WSL.

## Hardware requirements

Any computer that runs Python 3. The lab does only trivial arithmetic and text
formatting; it needs no particular RAM, disk, or GPU.

## Required software

- `python3` 3.6 or newer (f-strings and their format specs). Check with
  `python3 --version`.
- `bash` to run the test script (preinstalled on macOS and Linux).

## Free and open-source options

Everything in this lab is free and open source: Python and its standard library,
bash, and the standard shell utilities the tests use. No account, API key, or
purchase is needed, and nothing runs over the network.

## Installation

None beyond Python itself. Clone the repository (or copy this directory) and
change into it:

```bash
cd labs/sections/programming-with-python/day-047-input-output-and-f-strings
```

If `python3 --version` prints a version, you are ready. If not, see
`requirements/README.md`.

## File structure

```text
day-047-input-output-and-f-strings/
├── README.md                     ← you are here
├── metadata.yml                  ← machine-readable lab metadata
├── starter/
│   ├── io_demo.py                ← YOUR working file (5 numbered exercises)
│   └── io-worksheet.md           ← worksheet for the practice assignment
├── examples/
│   └── io_demo.py                ← completed reference implementation
├── tests/
│   └── run_tests.sh              ← automated, non-interactive checks
├── expected-output/
│   ├── sample-run.txt            ← real captured run (macOS, Python 3.14)
│   └── FIELDS.md                 ← required output fields on every platform
├── requirements/
│   └── README.md                 ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first — both input paths
python3 examples/io_demo.py 5 7
echo "5 7" | python3 examples/io_demo.py

# 2. Your task: complete the five exercises in the starter, then run it
python3 starter/io_demo.py 8 3
echo "8 3" | python3 starter/io_demo.py

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/io_demo.py 5 7` — runs the reference in **argument mode**:
  it joins the command-line arguments, splits them into two numbers, converts
  with `float()`, and prints the aligned report.
- `echo "5 7" | python3 examples/io_demo.py` — runs the same program in **stdin
  mode**: with no arguments it reads the piped text from `sys.stdin`. The output
  is byte-for-byte identical to argument mode.
- `python3 starter/io_demo.py 8 3` — runs your in-progress version; until you
  finish the exercises it still contains `FILL_ME_IN` placeholders.
- `bash tests/run_tests.sh` — runs concept checks (`python3 -c`), then drives the
  reference program with pipes and arguments to verify aligned output, and
  confirms bad input goes to stderr with a non-zero exit. It checks your starter
  strictly once every `FILL_ME_IN` is gone, and structurally before that.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a real
captured run. Good input prints an aligned report to standard output:

```text
Input values
  a            5.00
  b            7.00
Results
  sum         12.00
  product     35.00
  mean         6.00
```

Bad input prints nothing to stdout, writes an `error:` line to standard error,
and exits with code 1. [`expected-output/FIELDS.md`](expected-output/FIELDS.md)
lists exactly which fields must appear.

## Validation steps

1. Run `python3 examples/io_demo.py 5 7` and confirm the aligned report above.
2. Run `echo "5 7" | python3 examples/io_demo.py` and confirm identical output.
3. Run `echo "5 hello" | python3 examples/io_demo.py; echo $?` and confirm an
   `error:` line and an exit code of `1`.
4. Complete `starter/io_demo.py` (replace every `FILL_ME_IN`) so it matches the
   reference, then run the tests.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `19 checks, 0 failure(s).` while the starter is unfinished
(4 concept checks, 11 strict checks on the reference, 4 structural checks on the
starter), rising to `26 checks, 0 failure(s).` once your starter passes strict
mode. The command exits 0 on success and non-zero on any failure, so it can run
in CI. It is fully non-interactive — every input is supplied via a pipe or an
argument.

## Cleanup

Nothing to clean up: the program writes no files and makes no network calls. To
reset your work, restore the starter from git:
`git checkout -- starter/io_demo.py`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (string-vs-number
conversion, the hanging-`input()` trap, testing interactive programs via pipes,
stderr routing, exit codes, ragged columns, Windows notes).

## Security notes

See [security.md](security.md). Short version: never `eval()` input, validate and
convert everything, and think before printing sensitive values. The scripts make
no network calls, write no files, and need no elevated privileges.

## Extension exercises

1. Make `io_demo.py` a streaming filter: read `sys.stdin` line by line, treat
   each line as one `a b` pair, and print one formatted result row per line so
   `printf '5 7\n2 3\n' | python3 io_demo.py` prints two rows.
2. Add a `,` thousands separator to the sum column so `1000000 2000000` prints
   its sum as `3,000,000.00`.
3. Make a malformed line print a warning to stderr and be skipped, without
   aborting the whole run — one bad line should not lose the good ones.

## Navigation

- **Previous day:** Day 46 — Numbers, Math, and Precision
  (`labs/sections/programming-with-python/day-046-numbers-math-and-precision/`).
- **Next day:** Day 48 — Reading Error Messages and Debugging
  (`labs/sections/programming-with-python/day-048-reading-error-messages-and-debugging/`, to be written).
