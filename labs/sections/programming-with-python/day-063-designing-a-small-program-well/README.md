# Day 063 lab — Design It First

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Designing a Small Program Well
- **Day number:** 63 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-063-designing-a-small-program-well
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-063-designing-a-small-program-well` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 63 is the Week 9 capstone: it turns the week's pieces — functions,
scope, modules, the standard library, readable code, and recursion — into a
*way of designing* a small program well. This lab makes that concrete. From
a one-paragraph spec you build **summary**, a tiny numbers-summarizing tool,
deliberately split into two halves: a **pure functional core**
(`summary_core.py`, all logic, no I/O) and a **thin imperative shell**
(`summary.py`, all the I/O, no logic). You fill in the core from a starter
whose function signatures and docstrings are written first — docstring-driven
design — then run a test suite that exercises the pure core directly with
plain function calls, no fake files required. This is a smaller, self-contained
rehearsal for the Week 9 project, the **Flashcard Study App**, which uses the
same core/shell split scaled up to a multi-command program.

## Learning objectives

- Start from a spec and examples, then design function signatures (with
  docstrings) *before* writing any bodies.
- Split a program into a pure functional core (logic, no I/O) and a thin
  imperative shell (argv, files, stdout, exit code).
- Give each function a single responsibility and keep the core easy to test.
- Test the pure core directly with plain function calls, and the shell end
  to end through stdin, a file, and error cases.
- Practise incremental development and YAGNI: build the smallest working
  version first and leave out what the spec does not ask for.

## Prerequisites

- The Day 63 lesson (read it first — it walks this exact tool end to end).
- Days 57–62: functions and return values, scope and `*args`/`**kwargs`,
  modules and imports, the standard library, readable code, and recursion.
- Day 56: the shape of a data-driven program, and running a script from the
  terminal.
- A text editor and a terminal. No experience beyond this course is assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python
  3.14.0).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python`
  for `python3` if that is how Python is exposed. The tool is pure
  standard-library Python and behaves identically everywhere.

## Hardware requirements

Any computer that runs Python 3. The tool reads a little text and prints a
few lines; it needs no special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — the shell uses `sys`; the pure core uses no
  imports at all. No packages to install. See
  [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. No account, API key, network access, or purchase is needed.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-063-designing-a-small-program-well
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-063-designing-a-small-program-well/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── summary_core.py             ← YOUR working file (3 numbered exercises: the pure core)
│   ├── summary.py                  ← the shell, provided complete (do not edit)
│   └── design-worksheet.md         ← design a second program before coding it
├── examples/
│   ├── summary_core.py             ← complete reference core (pure logic, no I/O)
│   └── summary.py                  ← complete reference shell (all the I/O)
├── tests/
│   └── run_tests.sh                ← core tests (direct calls) + shell tests (end to end)
├── expected-output/
│   ├── sample-run.txt              ← real captured session with the reference
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
# 1. See the finished tool first. Feed it numbers on standard input.
echo "10 20 30 40" | python3 examples/summary.py

# 2. Or summarize numbers from a file.
printf "5, 7, 9, 11\n" > scores.txt
python3 examples/summary.py scores.txt
rm -f scores.txt

# 3. Watch the error paths (they exit with code 1).
echo "1 two 3" | python3 examples/summary.py ; echo "exit: $?"
printf "" | python3 examples/summary.py       ; echo "exit: $?"

# 4. Call the PURE CORE directly — no files, no shell — the payoff of the split.
PYTHONPATH=examples python3 -c "import summary_core as c; print(c.summarize([2, 4, 6, 8]))"

# 5. Your task: complete the three exercises in starter/summary_core.py, then run it.
echo "3 6 9" | python3 starter/summary.py

# 6. Check your work.
bash tests/run_tests.sh
```

## What the commands do

- `echo "..." | python3 examples/summary.py` — the shell reads the numbers
  from standard input, calls the pure core to parse and summarize them, and
  prints the six-line summary to standard output.
- `python3 examples/summary.py scores.txt` — the same, but the shell reads
  the numbers from the file you name instead of standard input.
- `echo "1 two 3" | ...` and `printf "" | ...` — the error paths: a
  non-numeric token and empty input each print a message to standard error
  and exit with code 1, so a script can detect the failure.
- `PYTHONPATH=examples python3 -c "...summarize..."` — calls a core function
  directly with a plain Python list. This works with no files and no shell
  because the core is pure — the whole point of the design.
- `bash tests/run_tests.sh` — runs the pure core through direct function-call
  checks (parse, summarize, format, and their error cases), then runs the
  shell end to end through stdin, a file, and error inputs, then checks your
  starter. Exits 0 only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured session:

```text
$ echo "10 20 30 40" | python3 examples/summary.py
count      4
total      100.00
mean       25.00
minimum    10.00
maximum    40.00
above mean 2

$ echo "1 two 3" | python3 examples/summary.py   ; echo "exit: $?"
error: 'two' is not a number
exit: 1
```

Successful results print to standard output; errors print to standard error
and set a non-zero exit code. The tool is deterministic, so your output will
match. [`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the
required behaviour of the core and the shell on every platform.

## Validation steps

1. `echo "10 20 30 40" | python3 examples/summary.py` prints a six-line
   summary ending in `above mean 2` and exits 0.
2. `echo "1 two 3" | python3 examples/summary.py; echo $?` prints
   `error: 'two' is not a number` to standard error and then `1`.
3. `printf "" | python3 examples/summary.py; echo $?` prints
   `error: cannot summarize an empty list of numbers` and then `1`.
4. `PYTHONPATH=examples python3 -c "import summary_core as c; print(c.summarize([2,4,6,8])['above_mean'])"`
   prints `2` — the core called directly, with no I/O.
5. Complete the three exercises in `starter/summary_core.py`, run
   `echo "3 6 9" | python3 starter/summary.py`, and confirm it matches the
   reference.
6. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `15 checks, 0
failure(s).` Once you complete all three starter exercises, the suite runs
your core through the same direct checks plus the shell end to end, giving
`23 checks, 0 failure(s).` The command exits 0 on success and non-zero on any
failure, so it can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

The tool writes nothing on its own. Remove any input file you created:

```bash
rm -f scores.txt
```

To reset your work, restore the starter from git:
`git checkout -- starter/summary_core.py`. The test runner cleans up its own
temporary input file automatically.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `python` vs
`python3`, `ModuleNotFoundError` for the core, why the tool has no
subcommands (YAGNI), the two error messages, decimal formatting, and
permissions.

## Security notes

See [security.md](security.md). Short version: the tool makes no network
calls and needs no privileges; the pure core writes nothing at all and the
shell only reads. Its central habit is to **validate input at the boundary
with `float()`, never `eval()` it** — and to keep every side effect in the
one small, readable shell.

## Extension exercises

1. Add a `median` to the summary. Decide first: does it belong in the pure
   core or the shell? (The core — it is logic.) Write its signature and
   docstring before its body, and add a direct test for it.
2. Add a `--round N` idea without `argparse`: let the shell read an optional
   second argument for the number of decimal places and pass it into a
   changed `format_summary(summary, places=2)`. Keep `format_summary` pure.
3. Refactor `format_summary` so the label/width list is defined once instead
   of repeated per line, and confirm the tests still pass — proof that a
   good test suite lets you refactor without fear.
4. Write your own `tests/test_core.py` that imports `parse_numbers`,
   `summarize`, and `format_summary` and asserts their behaviour, printing
   `all tests passed` only if every assertion holds, and confirm it exits 0.

## Navigation

- **Previous day:** Day 62 — Recursion
  (`labs/sections/programming-with-python/day-062-recursion/`).
- **Next day:** Day 64 — begins Week 10, Python in Practice
  (`labs/sections/programming-with-python/day-064-.../`, to be written).
- **Week 9 project:** the Flashcard Study App, a spaced-repetition flashcard
  CLI organized into clean modules with documented functions — the same
  functional-core / imperative-shell design you rehearse here, scaled up to a
  multi-command program.
