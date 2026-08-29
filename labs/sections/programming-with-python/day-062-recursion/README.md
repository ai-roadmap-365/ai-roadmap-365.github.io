# Day 062 lab — Recursive Thinking

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Recursion
- **Day number:** 62 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-062-recursion
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-062-recursion` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 62's lesson teaches recursion: a function that calls itself, built from a
**base case** (when to stop) and a **recursive case** (a smaller subproblem).
This lab makes that concrete. You implement five recursive functions from a
starter, one exercise at a time: `factorial`, a recursive `list_sum`, a
`flatten` of an arbitrarily nested list, a `tree_sum` that walks a nested
dict/list, and a naive `fib_naive` that counts its own calls. Then you run a
`fib` command that compares **naive recursion against an `lru_cache`-memoized
version and reports the call counts**, so the exponential blow-up of naive
Fibonacci — and the cure — are things you measure, not just read about. The
recursive shapes here (walking a tree, divide-and-conquer) are exactly the
ones you meet in AI: parse trees, decision trees, and nested JSON.

## Learning objectives

- Write a recursive function with a correct **base case** and **recursive
  case**, and explain why every call must move toward the base case.
- Use recursion where it genuinely fits — walking an arbitrarily nested list
  or dict/tree — rather than forcing a loop.
- Recognise **tree recursion** (Fibonacci) and why naive Fibonacci is
  exponential.
- Fix exponential recursion with **memoization** using
  `functools.lru_cache`, and measure the reduction in call count.
- Understand the **call stack**, `RecursionError`, and
  `sys.setrecursionlimit`, and know when a loop is the better choice.

## Prerequisites

- The Day 62 lesson (read it first — it explains every part this lab builds).
- Day 57: functions — definition, arguments, and return values. Recursion is
  just a function calling itself, so you must be comfortable with functions.
- Days 52–55: lists and dictionaries, which the nested-data exercises walk.
- A text editor and a terminal. No experience beyond this course is assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python
  3.14.0).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python`
  for `python3` if that is how Python is exposed. The code is pure
  standard-library Python and behaves identically everywhere.

## Hardware requirements

Any computer that runs Python 3. The exercises do a little arithmetic and
walk small data structures; they need no special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — `functools`, `argparse`, `json`, and `sys` all ship
  with Python. No packages to install. See
  [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. No account, API key, network access, or purchase is needed. The
`functools.lru_cache` decorator and the `json` module are part of Python
itself.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-062-recursion
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-062-recursion/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── recursion.py                ← YOUR working file (5 numbered exercises)
│   └── thinking-worksheet.md       ← name the base/recursive case before coding
├── examples/
│   └── recursion.py                ← complete reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (output, exit codes, call counts)
├── expected-output/
│   ├── sample-run.txt              ← real captured session with the reference
│   ├── test-run.txt                ← real captured run of the test suite
│   └── FIELDS.md                   ← required behaviour + the fib call-count table
├── requirements/
│   └── README.md                   ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished tool first — every subcommand is one recursive idea.
python3 examples/recursion.py factorial --n 5
python3 examples/recursion.py sum --values 1,2,3,4,5
python3 examples/recursion.py flatten --data "[1, [2, [3, 4]], 5]"
python3 examples/recursion.py treesum --data '{"a": 1, "b": {"c": 2, "d": [3, 4]}}'

# 2. Watch the exponential blow-up of naive recursion, and the cure.
python3 examples/recursion.py fib --n 10
python3 examples/recursion.py fib --n 30

# 3. Your task: complete the five exercises in the starter, then run it.
python3 starter/recursion.py factorial --n 6

# 4. Prove a function is importable (the payoff of the main guard).
python3 -c "import sys; sys.path.insert(0, 'examples'); from recursion import flatten; print(flatten([1, [2, [3]]]))"

# 5. Check your work.
bash tests/run_tests.sh
```

## What the commands do

- `factorial --n 5` — computes 5! by recursion: base case `n <= 1` returns 1,
  recursive case returns `n * factorial(n - 1)`.
- `sum --values 1,2,3,4,5` — adds a list by recursion: base case empty list
  returns 0, recursive case is `first + list_sum(rest)`.
- `flatten --data "[1, [2, [3, 4]], 5]"` — flattens an arbitrarily nested
  list; the function recurses into each sublist until it reaches leaf values.
- `treesum --data '{...}'` — walks a nested dict/list tree and adds every
  number in it; numbers are the base case, lists and dicts are the recursive
  case. Non-numbers are ignored.
- `fib --n 30` — computes the 30th Fibonacci number two ways and prints the
  **call counts**: the naive version's exponential number of calls and the
  `lru_cache`-memoized version's linear number of computations. This is the
  headline comparison of the lab.
- `python3 -c "...flatten..."` — imports one function and calls it without
  running the whole tool, which works only because the main guard holds
  `main` back on import.
- `bash tests/run_tests.sh` — drives the reference module through every
  subcommand (good and bad input), checks output and exit codes, imports the
  pure functions to check return values, and asserts the memoized Fibonacci
  makes far fewer calls than the naive one. Exits 0 only if every check
  passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured session:

```text
$ python3 examples/recursion.py fib --n 10
fib(10) = 55
naive recursion: 177 calls
memoized (lru_cache): 11 computations, 8 cache hits
the naive version made 16x more calls than the memoized version computed
```

The call counts are fixed mathematics, so your output will match exactly.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the required
behaviour for every input and the full fib call-count table.

## Validation steps

1. `python3 examples/recursion.py factorial --n 5` prints
   `factorial(5) = 120`; `factorial --n 0` prints `factorial(0) = 1` (the base
   case).
2. `python3 examples/recursion.py flatten --data "[1, [2, [3, 4]], 5]"` prints
   `flatten -> [1, 2, 3, 4, 5]`.
3. `python3 examples/recursion.py treesum --data '{"a": 1, "b": [2, 3]}'`
   prints `treesum -> 6`.
4. `python3 examples/recursion.py fib --n 10` prints `fib(10) = 55` and a
   `naive recursion: 177 calls` line with far more calls than the memoized
   computations.
5. `python3 examples/recursion.py factorial --n -3; echo $?` is rejected with
   a clear error and exits `1`.
6. Complete the five exercises in `starter/recursion.py`, run it on the same
   inputs, and confirm it matches the reference.
7. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `20 checks, 0
failure(s).` Once you complete all five starter exercises, the suite runs
your version through the same inputs plus the main-guard check, giving `31
checks, 0 failure(s).` The command exits 0 on success and non-zero on any
failure, so it can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

The tool writes no files, so there is nothing to delete. To reset your work,
restore the starter from git: `git checkout -- starter/recursion.py`. The
test runner leaves nothing behind.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `python` vs
`python3`, the all-important `RecursionError` (missing base case vs
genuinely deep input) and `sys.setrecursionlimit`, why `fib --n 40` seems to
hang (naive recursion is exponential), JSON quoting for `--data`, argparse's
exit code 2 versus the tool's exit code 1, importing vs running, and
permissions.

## Security notes

See [security.md](security.md). Short version: the tool makes no network
calls, needs no privileges, and reads and writes no files. It parses `--data`
with `json`, never `eval()`, and the recursion-depth limit is a safety
feature that turns runaway or maliciously deep input into a clean error
instead of an exhausted machine.

## Extension exercises

1. Add a `depth` subcommand that returns the maximum nesting depth of a JSON
   structure by recursion (base case: a non-container is depth 0; recursive
   case: 1 + the max depth of the children).
2. Rewrite `factorial` and `list_sum` as plain loops, keep both versions, and
   write a comment explaining which you would ship and why (hint: Python has
   no tail-call optimization, so deep recursion risks `RecursionError`).
3. Add your own memoized function — for example a recursive `count_paths`
   through a grid — with `@lru_cache`, and print `cache_info()` to show the
   hits and misses.
4. Write your own `tests/test_recursion.py` that imports `factorial`,
   `flatten`, and `tree_sum` and asserts their behaviour, printing
   `all tests passed` only if every assertion holds.

## Navigation

- **Previous day:** Day 61 — Writing Readable Code
  (`labs/sections/programming-with-python/day-061-writing-readable-code/`).
- **Next day:** Day 63 — Designing a Small Program Well
  (`labs/sections/programming-with-python/day-063-designing-a-small-program-well/`).
- **This week (Week 9):** Functions and program design — functions,
  scope, modules, the standard library, readable code, recursion, and a
  capstone on designing a small program well.
