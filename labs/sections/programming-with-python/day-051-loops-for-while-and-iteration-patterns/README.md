# Day 051 lab — Iteration Patterns Workbench

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Loops: for, while, and Iteration Patterns
- **Day number:** 51 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-051-loops-for-while-and-iteration-patterns
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-051-loops-for-while-and-iteration-patterns` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 51's lesson teaches iteration from first principles. This lab makes the
five core loop patterns concrete in one small, real program — the
**Iteration Patterns Workbench**. It reads whole numbers from the command
line or standard input and demonstrates each pattern in turn: **accumulate**
a total and count, **filter** a sequence, **transform** each item, **search**
with an early `break`, and build a small text **histogram**. You complete it
from a starter, one pattern at a time, then run an automated test suite that
checks real behaviour — output *and* exit code. These are the exact patterns
that reappear in AI training loops, data-cleaning pipelines, and agent
step-loops.

## Learning objectives

- Write the five iteration patterns as `for` loops: accumulate, filter,
  transform, search, and (in the histogram) nested iteration.
- Use an early `break` (via an immediate `return`) to stop a search as soon
  as it succeeds, and measure the work saved.
- Use `enumerate` to get index and value together without a hand-managed
  counter.
- Validate input at the boundary so a bad token prints a clear error and
  exits non-zero, never a raw traceback.
- Read data from standard input so the program is non-interactive and
  testable.

## Prerequisites

- The Day 51 lesson (read it first — it explains every pattern this lab
  builds).
- Days 43-50: a working Python 3 install plus variables, strings, numbers,
  input/output, debugging, program structure, and conditionals.
- A text editor and a terminal. No programming experience beyond this week is
  assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python
  3.14.0).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python` for
  `python3` if that is how Python is exposed. The program is pure
  standard-library Python and behaves identically everywhere.

## Hardware requirements

Any computer that runs Python 3. The program does only small integer
arithmetic and list building; it needs no special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — the `sys` module ships with Python. No packages to
  install. See [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. No account, API key, network access, or purchase is needed.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-051-loops-for-while-and-iteration-patterns
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-051-loops-for-while-and-iteration-patterns/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── patterns.py                 ← YOUR working file (5 numbered exercises)
│   └── patterns-worksheet.md       ← design a sixth pattern before coding it
├── examples/
│   └── patterns.py                 ← complete reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (all patterns, good + bad input, imports)
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
# 1. See all five patterns at once on a built-in sample (no input needed)
python3 examples/patterns.py demo

# 2. Feed your own numbers to individual patterns via standard input
echo "3 1 4 1 5 9 2 6" | python3 examples/patterns.py total
echo "3 1 4 1 5 9 2 6" | python3 examples/patterns.py filter 4
echo "3 1 4 1 5 9 2 6" | python3 examples/patterns.py transform
echo "3 1 4 1 5 9 2 6" | python3 examples/patterns.py search 5
echo "1 2 2 3 3 3"     | python3 examples/patterns.py histogram

# 3. Your task: complete the five exercises in the starter, then run it
echo "3 1 4 1 5 9 2 6" | python3 starter/patterns.py total

# 4. Prove the module is importable (the payoff of the main guard)
python3 -c "import sys; sys.path.insert(0, 'examples'); from patterns import accumulate_total; print(accumulate_total([3,1,4,1,5,9,2,6]))"

# 5. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/patterns.py demo` — runs every pattern on the built-in
  sample list `[3, 1, 4, 1, 5, 9, 2, 6]` and prints a five-line report plus a
  histogram. It needs no input, so it is the quickest way to see the program.
- `echo "..." | python3 examples/patterns.py <command>` — pipes numbers to a
  single pattern. `total` accumulates a count and sum; `filter N` keeps items
  greater than `N`; `transform` squares each item; `search N` scans with an
  early `break` and reports how many comparisons it made; `histogram` counts
  each distinct value and prints a bar of `#`. Bad input (a non-number token,
  an unknown command, or a missing argument) prints a clear error to standard
  error and exits with code 1.
- `python3 starter/patterns.py ...` — runs your version. The starter ships
  with five pattern functions stubbed out (each raising `NotImplementedError`
  until you finish it): accumulate, filter, transform, search-with-break, and
  histogram.
- `python3 -c "...accumulate_total..."` — imports one function from the module
  and calls it without running the whole program. This works only because the
  main guard holds `main` back on import.
- `bash tests/run_tests.sh` — runs the reference on every pattern (good and
  bad inputs, checking output *and* exit code), imports two functions to
  check their return values, and checks your starter (structurally until you
  finish, strictly afterwards). Exits 0 only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured run:

```text
$ python3 examples/patterns.py demo
sample: [3, 1, 4, 1, 5, 9, 2, 6]
total    -> count=8 sum=31
filter>4 -> [5, 9, 6]
transform-> [9, 1, 16, 1, 25, 81, 4, 36]
search 5 -> found 5 at index 4 after 5 comparisons
histogram:
 1 | ##
 2 | #
 3 | #
 4 | #
 5 | #
 6 | #
 9 | #
```

The program is deterministic, so your numbers will match exactly.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the required
behaviour for every input on every platform.

## Validation steps

1. Run `python3 examples/patterns.py demo` — it must print the five-pattern
   report above.
2. Run `echo "3 1 4 1 5 9 2 6" | python3 examples/patterns.py search 7; echo $?`
   — it must print `7 not found after 8 comparisons` and then `1`.
3. Complete the five exercises in `starter/patterns.py`, then run it on the
   same inputs and confirm it matches the reference.
4. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `15 checks, 0
failure(s).` Once you complete all five starter exercises, ten more checks
run your version through the same good/bad inputs plus the main-guard check,
giving `24 checks, 0 failure(s).` The command exits 0 on success and non-zero
on any failure, so it can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

Nothing to clean up: the program and tests read only their command-line
arguments and standard input, and write nothing outside their own console
output (no files, no network, no settings). To reset your work, restore the
starter from git: `git checkout -- starter/patterns.py`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: the program
"hanging" while it waits on standard input, `python` vs `python3`, the
deliberate `NotImplementedError` stubs, non-number tokens, missing command
arguments, histogram alignment, exit codes, and interrupting an infinite
loop with Ctrl-C.

## Security notes

See [security.md](security.md). Short version: the program makes no network
calls, writes no files, and needs no privileges. Its central habits are to
**validate input and never `eval()` it** — turn text into numbers with
`int()`, which cannot execute code — and to **bound any loop fed by untrusted
input** so it cannot be pushed into running forever.

## Extension exercises

1. Add a sixth pattern using `starter/patterns-worksheet.md`: a running
   maximum and its position, a run-length summary, or a `zip`-based two-list
   merge. Give it its own function and subcommand, and validate its input.
2. Rewrite the `filter` and `transform` patterns as one-line list
   comprehensions (`[n for n in nums if n > t]`, `[n*n for n in nums]`) and
   confirm they produce identical output to the loops.
3. Generate a long input with
   `python3 -c "print(' '.join(str(i) for i in range(10000)))"` and pipe it to
   `search` for a value near the front and near the end; compare the
   comparison counts to see what the early `break` saves.

## Navigation

- **Previous day:** Day 50 — Conditionals and Boolean Logic
  (`labs/sections/programming-with-python/day-050-conditionals-and-boolean-logic/`).
- **Next day:** Day 52 — Lists in Depth
  (`labs/sections/programming-with-python/day-052-lists-in-depth/`, to be written).
- **Week 8 project:** the collections and control-flow miniproject, which
  reuses exactly these iteration patterns over richer data structures.
