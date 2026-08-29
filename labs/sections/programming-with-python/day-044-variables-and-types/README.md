# Day 044 lab — Explore Python Types

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Variables and Types
- **Day number:** 44 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-044-variables-and-types
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-044-variables-and-types` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 44's lesson explains what a Python variable really is — a name bound to an
object — and introduces the core built-in types. This lab makes it concrete:
you run a program that assigns a value of each core type and prints its
`type()`, demonstrates dynamic typing by re-binding a name, shows mutability
with `id()`, and converts types safely with `try`/`except`. Then you complete
a starter version yourself and fill in a short worksheet.

## Learning objectives

- Run a Python program from the terminal with `python3` and read its output.
- Identify the core built-in types (`int`, `float`, `bool`, `str`,
  `NoneType`, `list`) from a program's output.
- Use `type()` and `id()` to inspect an object's type and identity.
- Show that a list mutates in place (its id is unchanged) while a string
  "change" makes a new object (its id changes).
- Convert a string to an integer safely, handling `ValueError`.

## Prerequisites

- The Day 44 lesson (read it first — it explains every concept this lab uses).
- Day 43 completed: Python 3 installed and runnable as `python3`.
- A terminal and any text editor. No third-party packages, account, or
  network connection required.

## Supported operating systems

- **macOS** — fully supported (authored and tested on Apple Silicon, Python 3.14.0).
- **Linux** — fully supported (any distribution with Python 3.8+).
- **Windows** — supported; invoke the interpreter as `python` if `python3` is
  not found, or run the lab inside WSL for a Unix-style shell.

## Hardware requirements

Any computer that can run Python 3. The programs allocate a handful of small
objects and print text; they need no meaningful RAM, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0).
- `bash` (to run the test script) — preinstalled on macOS and Linux.

## Free and open-source options

Everything in this lab is free and open source: Python and bash ship with or
install freely on every supported OS, and the lab uses only the standard
language — no paid tools, no API keys, no accounts.

## Installation

None beyond Python itself (from Day 43). Change into this directory and you
are ready:

```bash
cd labs/sections/programming-with-python/day-044-variables-and-types
```

## File structure

```text
day-044-variables-and-types/
├── README.md                      ← you are here
├── metadata.yml                   ← machine-readable lab metadata
├── starter/
│   ├── types_demo.py              ← YOUR working file (4 exercises)
│   └── types-worksheet.md         ← worksheet for the practice assignment
├── examples/
│   └── types_demo.py              ← completed reference program
├── tests/
│   └── run_tests.sh               ← automated checks
├── expected-output/
│   ├── example-run.txt            ← real captured run of the example
│   ├── test-run.txt               ← real captured run of the tests
│   └── FIELDS.md                  ← what must appear on every platform
├── requirements/
│   └── README.md                  ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
python3 examples/types_demo.py

# 2. Your task: complete the four exercises in the starter, then run it
python3 starter/types_demo.py

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/types_demo.py` — runs the reference program: prints each
  core type with `type()`, re-binds a name to show dynamic typing, compares
  `id()` before and after a list append (same object) and a string
  concatenation (new object), and converts `"30"` and `"oops"` with a safe
  `int()` wrapped in `try`/`except ValueError`.
- `python3 starter/types_demo.py` — the same ideas as four numbered
  exercises for you to complete. Each `None` marked with an `# exercise`
  comment is a blank to fill; edit the file in any text editor.
- `bash tests/run_tests.sh` — runs the example program and checks its output
  for every core type name, the dynamic-typing marker, both mutability
  results, and both conversion outcomes; then runs an independent
  `python3 -c` assertion of the data model. Exits 0 on success, non-zero on
  any failure.

## Expected output

See [`expected-output/example-run.txt`](expected-output/example-run.txt) — a
real captured run:

```text
--- Core types ---
count      = 42            type = int
price      = 19.99         type = float
is_open    = True          type = bool
label      = widget        type = str
missing    = None          type = NoneType

--- Dynamic typing ---
thing = 100 (int)
thing = hello (str)   <- same name, different type

--- Mutability ---
list before: [1, 2, 3]  id unchanged after append: True
str  before: cat        id changed after '+': True

--- Safe conversion ---
'30'  -> 30 (int)
'oops' -> could not convert (ValueError handled)
```

The `id()` comparisons (`True`) are the point: the list keeps its identity
after `.append()`, while the string gets a new identity after `+`. Your own
run prints the same lines (identity numbers are internal and not shown).

## Validation steps

1. Run `python3 examples/types_demo.py` — it must exit without errors and
   print all four sections.
2. Complete the four exercises in `starter/types_demo.py` and run it — no
   line should still read `type = NoneType` for the exercise-1 values, and
   the mutability line should report `True`.
3. Confirm the safe conversion in exercise 2 prints `42` as an `int`.
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `12 checks, 0 failure(s).` The command exits 0 on
success and non-zero on any failure, so it can run in CI. The full captured
run is in [`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

Nothing to clean up: the programs write no files and change no settings. To
reset your work on the starter, restore it from git:
`git checkout -- starter/types_demo.py`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (`python3` not
found, Python 2 vs 3, `SyntaxError` from copied REPL prompts, `ValueError` on
conversion, indentation errors, differing `id()` numbers).

## Security notes

See [security.md](security.md). Short version: the programs make no network
calls, need no elevated privileges, read no input, and write no files — and
they deliberately use `int()`/`float()` with `try`/`except`, never `eval()`,
to convert text.

## Extension exercises

1. Add a `tuple` and a `dict` to the example's core-types section and print
   their types; confirm `tuple` is immutable and `dict` is mutable using
   `id()`.
2. Extend the starter to prove aliasing: bind `b = a` for a list, append
   through `b`, and show that `a` sees the change.
3. Add a type hint to a variable (`n: int = "hello"`), run the file to see
   Python ignore it, then read one page of the mypy documentation and note
   what a static checker would report.

## Navigation

- **Previous day:** Day 43 — Installing Python and Virtual Environments
  (`labs/sections/programming-with-python/day-043-installing-python-and-virtual-environments/`).
- **Next day:** Day 45 — Strings and Text Processing
  (`labs/sections/programming-with-python/day-045-strings-and-text-processing/`, to be written).
