# Day 057 lab — Function Library

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Functions: Definition, Arguments, and Return Values
- **Day number:** 57 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-057-functions-definition-arguments-and-return-values
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-057-functions-definition-arguments-and-return-values` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 57's lesson teaches functions from first principles: `def`, parameters
versus arguments, positional/keyword/default arguments, return values
(including returning a tuple of several results and the implicit `None`),
docstrings, the difference between returning a value and printing (pure
function versus side effect), the mutable-default-argument trap, and DRY. This
lab makes that concrete. You build **a small library of pure functions** —
tiny text and number utilities — each with a docstring, each taking its input
as arguments and handing back a return value, and none of them printing or
changing anything outside themselves. Then you run an automated suite that
calls each function and **asserts on what it returns**, because return values
are exactly what makes a pure function easy to test. This is the shape every
model call, metric, and data transform takes later: a named, documented,
testable function.

## Learning objectives

- Define functions with `def`, giving each a docstring whose first line says
  what the function returns.
- Use positional, keyword, and default arguments, and know the difference
  between a parameter (in the definition) and an argument (at the call).
- Return a value the caller uses — and return a **tuple** to hand back several
  results at once, which the caller unpacks.
- Write **pure** functions (input from arguments, a return value, no side
  effects) and explain why they are the easy ones to test.
- Avoid the mutable-default-argument trap by defaulting to `None` and building
  a fresh container inside.
- Factor repeated work into a function (DRY) and prove behaviour by asserting
  on return values, not by reading printed output.

## Prerequisites

- The Day 57 lesson (read it first — it explains every idea this lab builds).
- Days 50–56: conditionals and loops, lists, dictionaries, sets and tuples,
  comprehensions, and the shape of a script run from the terminal.
- A text editor and a terminal. No experience beyond this course is assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python
  3.14.0).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python`
  for `python3` if that is how Python is exposed. The code is pure
  standard-library Python and behaves identically everywhere.

## Hardware requirements

Any computer that runs Python 3. The functions do trivial text and number
work; they need no special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — no packages to install. See
  [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. No account, API key, network access, or purchase is needed. The
whole lab is ordinary Python function definitions.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-057-functions-definition-arguments-and-return-values
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-057-functions-definition-arguments-and-return-values/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── library.py                  ← YOUR working file (6 numbered exercises)
│   └── design-worksheet.md         ← design your own library before coding it
├── examples/
│   ├── library.py                  ← complete reference library of pure functions
│   └── demo.py                     ← calls the library and uses its return values
├── tests/
│   └── run_tests.sh                ← assert-based checks on return values and purity
├── expected-output/
│   ├── sample-run.txt              ← real captured run of examples/demo.py
│   ├── test-run.txt                ← real captured run of the test suite
│   └── FIELDS.md                   ← required return values on every platform
├── requirements/
│   └── README.md                   ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory.

```bash
# 1. See the finished library in action. demo.py imports it and uses what
#    each function returns — no function prints on its own.
python3 examples/demo.py

# 2. Call a function directly and use its return value. summarize returns a
#    tuple you can unpack.
python3 -c "import sys; sys.path.insert(0, 'examples'); from library import summarize; c, t, lo, hi, avg = summarize([7, 3, 9, 4, 6]); print('mean is', avg)"

# 3. Try default and keyword arguments on greet and clamp.
python3 -c "import sys; sys.path.insert(0, 'examples'); from library import greet, clamp; print(greet('Ada'), '|', greet('Ada', punctuation='.'), '|', clamp(42, high=100))"

# 4. Your task: complete the six exercises in the starter, then test it.
#    (Editing starter/library.py.)

# 5. Check your work — and the reference — with the assert-based suite.
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/demo.py` — imports the pure functions and prints how a
  caller uses their return values: composing calls, unpacking the tuple from
  `summarize`, and passing keyword arguments to `greet`. The functions
  themselves never print; the caller does.
- `python3 -c "...summarize..."` — imports one function and unpacks its
  returned tuple `(count, total, min, max, mean)`, showing that one call can
  hand back several results.
- `python3 -c "...greet, clamp..."` — shows default arguments (`greet('Ada')`
  uses `greeting="Hello"`) and keyword arguments (`clamp(42, high=100)`) at
  the call site.
- `bash tests/run_tests.sh` — imports the reference library and the starter,
  calls each function, and **asserts on the return value**: exact results, the
  returned tuple, default and keyword arguments, purity (same args → same
  result, inputs unmutated), the mutable-default trap avoided, raised errors,
  and that every public function has a docstring. Exits 0 only if every check
  passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured run of `python3 examples/demo.py`. Two lines from it:

```text
summarize([7, 3, 9, 4, 6]) ->
    count=5 total=29 min=3 max=9 mean=5.8
```

Every function is pure and deterministic, so your output will match exactly.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the required
return value for every function on every platform.

## Validation steps

1. `python3 examples/demo.py` prints the block shown above without error.
2. `python3 -c "import sys; sys.path.insert(0,'examples'); from library import word_count; print(word_count('the quick brown fox'))"`
   prints `4`.
3. `python3 -c "import sys; sys.path.insert(0,'examples'); from library import summarize; print(summarize([2,4,6]))"`
   prints the tuple `(3, 12, 2, 6, 4.0)`.
4. Complete the six exercises in `starter/library.py`; each function must
   `return` its value and carry a docstring.
5. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `30 checks, 0
failure(s).` — the reference library is fully tested and the starter is
checked structurally. Once you complete all six starter exercises, the suite
runs your library through the same assertions, giving `46 checks, 0
failure(s).` The command exits 0 on success and non-zero on any failure, so it
can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

The lab writes no data files. Python may create `__pycache__` folders when it
imports the module; remove them if you like:

```bash
find . -name __pycache__ -type d -prune -exec rm -rf {} +
```

To reset your work, restore the starter from version control (for example
`git restore starter/library.py` in the full repository).

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `python` vs
`python3`, the `NotImplementedError` stubs, `ModuleNotFoundError` and the
import path, "my function prints but the test fails" (return, do not print),
floats versus ints, the mutable-default trap in `tally`, and unpacking the
tuple from `summarize`.

## Security notes

See [security.md](security.md). Short version: the code makes no network
calls, needs no privileges, and writes no files. Pure functions have a tiny
contact with the world, which is a security property as well as good design;
never build behaviour out of `eval()`/`exec()`, and validate at the boundary
so bad input raises a clear error instead of a silently wrong number.

## Extension exercises

1. Add a `median(numbers)` function that returns the middle value (or the mean
   of the two middle values) of a sorted copy — without mutating the input,
   keeping it pure — and add asserts for it to the suite.
2. Add a `titlecase_words(text)` function and refactor any repeated
   split/join logic shared with `reverse_words` and `normalize_whitespace`
   into one small helper (DRY).
3. Extend `summarize` to also return the range (`max - min`) as a sixth tuple
   element, and update every caller and test that unpacks it — noticing how a
   changed return shape ripples out.
4. Write your own `tests/test_library.py` that imports the functions and uses
   `assert` statements directly, printing `all tests passed` only if every
   assertion holds, and confirm it exits 0.

## Navigation

- **Previous day:** Day 56 — Building a Data-Driven CLI
  (`labs/sections/programming-with-python/day-056-building-a-data-driven-cli/`).
- **Next day:** Day 58 — continues Week 9, Functions and Program Design
  (`labs/sections/programming-with-python/day-058-.../`, to be written).
- **This week (Week 9):** functions and program design — you build the named,
  documented, testable building blocks that every later data and model tool is
  assembled from.
