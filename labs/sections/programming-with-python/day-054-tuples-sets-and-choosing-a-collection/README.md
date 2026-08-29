# Day 054 lab — Choosing Collections

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Tuples, Sets, and Choosing a Collection
- **Day number:** 54 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-054-tuples-sets-and-choosing-a-collection
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-054-tuples-sets-and-choosing-a-collection` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 54's lesson teaches the last two core Python collections — **tuples** and
**sets** — and, just as importantly, how to *choose* among list, tuple, set,
and dict. This lab makes that concrete: you build a small, complete program
that **dedupes** items with a set, computes the **set algebra** between two
lists (common, only-in-A, only-in-B, symmetric difference), and returns the
results as **immutable tuple records**. Alongside the program you fill in a
short worksheet that has you justify a collection choice for eight real
scenarios. The result is a working tool and a decision habit you will reuse in
every data pipeline you build.

## Learning objectives

- Use a `set` to remove duplicates and to test membership in one fast step.
- Compute set algebra — intersection (`&`), difference (`-`), and symmetric
  difference (`^`) — between two collections.
- Return results as immutable `tuple` records (here, a `namedtuple`) that a
  caller cannot accidentally change.
- Choose the right collection (list / tuple / set / dict) by asking four
  questions: mutable? ordered? unique? fast lookup?
- Run and test a small program without a human: known inputs, checked output
  and exit code, and imported functions checked by return value.

## Prerequisites

- The Day 54 lesson (read it first — it explains tuples, sets, and the
  decision framework this lab applies).
- Day 52 (lists) and Day 53 (dictionaries), plus Day 49's program structure
  (functions, `main`, the main guard, input validation).
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

Any computer that runs Python 3. The program does only string splitting and
set arithmetic on small inputs; it needs no special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — `sys` and `collections.namedtuple` ship with Python.
  No packages to install. See [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. No account, API key, network access, or purchase is needed.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-054-tuples-sets-and-choosing-a-collection
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-054-tuples-sets-and-choosing-a-collection/
├── README.md                            ← you are here
├── metadata.yml                         ← machine-readable lab metadata
├── starter/
│   ├── collections_tool.py              ← YOUR working file (5 numbered exercises)
│   └── collection-choice-worksheet.md   ← choose a collection per scenario
├── examples/
│   └── collections_tool.py              ← complete reference implementation
├── tests/
│   └── run_tests.sh                     ← automated checks (dedupe, set algebra, imports)
├── expected-output/
│   ├── sample-run.txt                   ← real captured run of the reference
│   ├── test-run.txt                     ← real captured run of the test suite
│   └── FIELDS.md                        ← required behaviour on every platform
├── requirements/
│   └── README.md                        ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished program first, on good and bad input
python3 examples/collections_tool.py "apple,banana,apple,cherry" "banana,cherry,date,date"
python3 examples/collections_tool.py "banana" "banana,cherry"
python3 examples/collections_tool.py "apple,banana"          # prints an error, exits non-zero

# 2. Your task: complete the five exercises in the starter, then run it
python3 starter/collections_tool.py "apple,banana,apple" "banana,cherry"

# 3. Prove the module is importable (the payoff of the main guard)
python3 -c "import sys; sys.path.insert(0, 'examples'); from collections_tool import dedupe; print(dedupe(('a', 'a', 'b')))"

# 4. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/collections_tool.py "apple,banana,apple,cherry" "banana,cherry,date,date"`
  — runs the complete reference program: it parses each list into a tuple in
  `parse_items`, dedupes with a set, computes the set algebra in `compare`,
  formats with `format_report`, and prints a six-line report. Bad input (only
  one argument, or a list that is empty after cleaning) prints a clear error to
  standard error and exits with code 1.
- `python3 starter/collections_tool.py ...` — runs your version. The starter
  ships with five exercises stubbed out (each raising `NotImplementedError`
  until you finish it): return an immutable tuple, dedupe with a set, do the
  set algebra, format the report, and add the main guard.
- `python3 -c "...dedupe..."` — imports one function from the module and calls
  it, without running the whole program. This works only because the main
  guard holds `main` back on import.
- `bash tests/run_tests.sh` — runs the reference on good and bad inputs
  (checking output *and* exit code), imports `dedupe` and `compare` to check
  their return values (including that `dedupe` returns an immutable tuple), and
  checks your starter (structurally until you finish, strictly afterwards).
  Exits 0 only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured run:

```text
$ python3 examples/collections_tool.py "apple,banana,apple,cherry" "banana,cherry,date,date"
List A: 4 items read, 3 unique after dedupe
List B: 4 items read, 3 unique after dedupe
Common (A & B): banana, cherry
Only in A (A - B): apple
Only in B (B - A): date
Symmetric difference (A ^ B): apple, date
```

Every group is sorted before printing, so the program is deterministic and
your output will match exactly — even though a `set` itself is unordered.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the required
behaviour for every input on every platform.

## Validation steps

1. Run the first command above — it must print `List A: 4 items read, 3 unique
   after dedupe` and `Common (A & B): banana, cherry`.
2. Run `python3 examples/collections_tool.py "apple,banana"; echo $?` — it must
   print an error and then `1`.
3. Complete the five exercises in `starter/collections_tool.py`, then run it on
   the same inputs and confirm it matches the reference.
4. Fill in `starter/collection-choice-worksheet.md` — a collection choice and a
   one-sentence reason for each of the eight scenarios.
5. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `13 checks, 0
failure(s).` Once you complete all five starter exercises, seven more checks
run your version through the same good/bad inputs plus the main-guard check,
giving `20 checks, 0 failure(s).` The command exits 0 on success and non-zero
on any failure, so it can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

Nothing to clean up: the program and tests read only their command-line
arguments and write nothing outside their own console output (no files, no
network, no settings). To reset your work, restore the starter from git:
`git checkout -- starter/collections_tool.py`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `python` vs
`python3`, the deliberate `NotImplementedError` stubs, why output stays sorted,
the `unhashable type: 'list'` error, quoting your two lists, and importing vs
running.

## Security notes

See [security.md](security.md). Short version: the program makes no network
calls, writes no files, and needs no privileges. It turns text into **data**
(splits and sets), never into code — so it never touches `eval()`. Sets power
fast, correct membership checks, which are a real security primitive for
allow-lists and block-lists.

## Extension exercises

1. Add a `--sorted-by-length` style option: read a third argument and, when it
   is `len`, sort each output group by length then alphabetically. Keep the
   default (plain alphabetical) unchanged and keep the program deterministic.
2. Add a `union` line to the report using `a | b`, and confirm by hand that
   `len(union) == len(common) + len(symmetric)` for your inputs.
3. Write your own `tests/test_tool.py` that imports `dedupe` and `compare` and
   asserts several known results (including that `dedupe` returns a `tuple` and
   `compare` returns a `SetReport`), printing `all tests passed` only if every
   assertion holds; run it with `python3 tests/test_tool.py`.

## Navigation

- **Previous day:** Day 53 — Dictionaries: Key-Value Data
  (`labs/sections/programming-with-python/day-053-.../`).
- **Next day:** Day 55 — Comprehensions and Iterator Thinking
  (`labs/sections/programming-with-python/day-055-.../`, to be written).
- **Week 8 project:** builds on lists, dictionaries, tuples, and sets together
  — choosing the right collection for each part of a small data task.
