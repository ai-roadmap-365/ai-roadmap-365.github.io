# Day 052 lab — List Toolkit

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Lists in Depth
- **Day number:** 52 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-052-lists-in-depth
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-052-lists-in-depth` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 52's lesson teaches Python lists in depth: indexing and slicing, in-place
methods versus functions that return new lists, and the reference model that
makes list mutation surprising. This lab makes those ideas concrete. You build
a **List Toolkit** — five small, idiomatic functions that slice a list, sort
it with a key, remove duplicates while preserving order, flatten a nested
list, and safely copy a list before changing it — and you run a test suite
that *proves* the difference between mutating a list in place and returning a
new one. This is the exact skill that keeps datasets, batches, and token
sequences from being silently corrupted in the data and machine-learning code
later in the course.

## Learning objectives

- Slice a list with start, stop, and step, including negative indices.
- Sort with a `key=` function and rely on Python's stable sort.
- Tell in-place methods (`sort`, `append`) apart from functions that return a
  new list (`sorted`, a slice) — and know which one you called.
- Remove duplicates while preserving first-seen order, and flatten a nested
  list, each returning a new list.
- Copy a list before mutating it, and explain why aliasing makes the original
  change otherwise.

## Prerequisites

- The Day 52 lesson (read it first — it explains every part this lab builds).
- Days 49-51: a first real program with functions and a `main` guard,
  conditionals, and loops.
- A text editor and a terminal. No programming experience beyond these weeks
  is assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python
  3.14.0).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python` for
  `python3` if that is how Python is exposed. The program is pure
  standard-library Python and behaves identically everywhere.

## Hardware requirements

Any computer that runs Python 3. The program manipulates a handful of short
lists; it needs no special memory, disk, or GPU.

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
cd labs/sections/programming-with-python/day-052-lists-in-depth
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-052-lists-in-depth/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   └── toolkit.py                  ← YOUR working file (5 numbered exercises)
├── examples/
│   └── toolkit.py                  ← complete reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (pipeline, imports, in-place vs new)
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
# 1. See the finished toolkit's demo pipeline
python3 examples/toolkit.py

# 2. Call one function directly, without running the whole program
python3 -c "import sys; sys.path.insert(0, 'examples'); import toolkit; print(toolkit.dedupe([1, 1, 2, 1, 3]))"

# 3. Your task: complete the five exercises in the starter, then run it
python3 starter/toolkit.py

# 4. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/toolkit.py` — runs the complete reference program. It
  builds a list of scores, then prints the results of slicing it (top three,
  every other item, the last two), sorting words by length (stably), removing
  duplicates while keeping order, flattening a two-row matrix, and growing a
  copy while proving the original stays unchanged.
- `python3 -c "...toolkit.dedupe..."` — imports one function from the module
  and calls it, without running the whole program. This works because the main
  guard holds `main` back on import.
- `python3 starter/toolkit.py` — runs your version. The starter ships with
  five exercises stubbed out (each raising `NotImplementedError` until you
  finish it): dedupe, flatten, sort-by-length, top-n, and copy-before-mutate.
- `bash tests/run_tests.sh` — runs the reference through the demo pipeline,
  imports every function and checks its return value, and asserts the core
  lesson: `sorted()` returns a new list while `.sort()` mutates in place,
  assignment aliases a list while a slice copies it, and none of the toolkit
  functions change their input. Then it checks your starter (structurally
  until you finish, strictly afterwards). Exits 0 only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured run:

```text
$ python3 examples/toolkit.py
built:    [88, 72, 95, 72, 60, 95, 81]
top 3:    [95, 95, 88]
stride:   [88, 95, 60, 81]
last 2:   [95, 81]
by len:   ['fig', 'fig', 'pear', 'kiwi', 'plum', 'apple']
unique:   ['pear', 'fig', 'apple', 'kiwi', 'plum']
flat:     [1, 2, 3, 4, 5, 6]
grown:    [10, 20, 30, 40]
original: [10, 20, 30]
```

The last two lines are the payoff: `grown` gained a `40`, but `original` did
not, because `with_appended` copied the list before appending. The toolkit is
deterministic, so your numbers will match exactly.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the required
result for every operation on every platform.

## Validation steps

1. Run `python3 examples/toolkit.py` — the `original:` line must still read
   `[10, 20, 30]`, proving the copy protected it.
2. Run the import one-liner — it must print `[1, 2, 3]`.
3. Complete the five exercises in `starter/toolkit.py`, then run it and confirm
   its output matches the reference.
4. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `13 checks, 0
failure(s).` Once you complete all five starter exercises, seven more checks
run your version through the same pipeline plus the copy-safety check, giving
`20 checks, 0 failure(s).` The command exits 0 on success and non-zero on any
failure, so it can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

Nothing to clean up: the program and tests read no input and write nothing
outside their own console output (no files, no network, no settings). To reset
your work, restore the starter from git: `git checkout -- starter/toolkit.py`.
If a `__pycache__` folder appears after an import, remove it with
`rm -rf examples/__pycache__`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `python` vs
`python3`, the deliberate `NotImplementedError` stubs, importing vs running,
the `with_appended` mutation trap, and why `.sort()` returns `None`.

## Security notes

See [security.md](security.md). Short version: the program makes no network
calls, writes no files, and needs no privileges. Its central lesson is to
**copy before you mutate** — return a new list rather than changing the one you
were given, and reach for a deep copy when the data is nested.

## Extension exercises

1. Add a `deep_flatten(nested)` that flattens arbitrarily nested lists (a list
   inside a list inside a list), then compare it with the one-level `flatten`.
2. Add a `chunk(items, size)` that splits a list into a list of smaller lists
   of length `size` — the shape of turning a dataset into training batches.
3. Write a demonstration that uses `copy.deepcopy` on a matrix, mutates one
   inner list, and shows the deep copy is unaffected while a shallow `[:]` copy
   is not.

## Navigation

- **Previous day:** Day 51 — Loops: for, while, and Iteration Patterns
  (`labs/sections/programming-with-python/day-051-loops-for-while-and-iteration-patterns/`).
- **Next day:** Day 53 — Dictionaries in Depth
  (`labs/sections/programming-with-python/day-053-dictionaries-in-depth/`).
- **Week 8 project:** the Terminal Task Manager, a to-do CLI that stores tasks
  in a list (and dictionaries) — built directly on the list skills in this lab.
