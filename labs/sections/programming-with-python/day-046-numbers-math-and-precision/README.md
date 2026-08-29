# Day 046 lab — Precision and Money Math

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Numbers, Math, and Precision
- **Day number:** 46 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-046-numbers-math-and-precision
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-046-numbers-math-and-precision` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 46's lesson explains how Python stores numbers and where floating-point
precision quietly goes wrong. This lab makes it concrete: you run a small
program that reproduces the famous `0.1 + 0.2 != 0.3` trap, compares floats
the safe way, and shows the difference between adding up a shopping cart in
`float` (subtly wrong) and in `Decimal` (exactly right). You finish able to
choose the correct numeric type for a task instead of hoping the defaults work.

## Learning objectives

- Reproduce and explain the classic floating-point rounding error.
- Compare two computed floats safely with `math.isclose` instead of `==`.
- Compute an exact currency total with the `decimal` module.
- Use floor division (`//`) and modulo (`%`) to make change from whole cents.
- Call the everyday `math` functions (`sqrt`, `floor`, `ceil`).

## Prerequisites

- The Day 46 lesson (read it first — it explains every idea this lab exercises).
- Python 3 installed and runnable as `python3` (Day 43 set this up).
- A terminal and any text editor for completing the starter exercises.

## Supported operating systems

- **macOS** — fully supported (executed on macOS, Apple Silicon, Python 3.14).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — run the Python program directly with `python`; run the `.sh`
  test script under WSL or Git Bash. The program's output is identical on
  every platform because it is pure arithmetic.

## Hardware requirements

Any computer that can run Python 3. The program uses a trivial amount of CPU
and memory and touches neither disk nor network.

## Required software

- `python3` ≥ 3.8 (executed on 3.14). Standard library only — `decimal` and
  `math` ship with Python.
- `bash` to run the test script (preinstalled on macOS and Linux).

## Free and open-source options

Everything here is free and open-source: CPython and its standard library
carry no cost, no account, and no API key. There is nothing to install beyond
Python itself — the exact-money math uses the built-in `decimal` module, not a
paid library.

## Installation

None beyond Python. Confirm Python is present, then change into this directory:

```bash
python3 --version
cd labs/sections/programming-with-python/day-046-numbers-math-and-precision
```

## File structure

```text
day-046-numbers-math-and-precision/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── precision_demo.py           ← YOUR working file (5 exercises)
│   └── numbers-worksheet.md        ← record your observed values here
├── examples/
│   └── precision_demo.py           ← completed reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (exit 0 = pass)
├── expected-output/
│   ├── sample-run.txt              ← real captured run of the reference program
│   └── FIELDS.md                   ← the lines that must appear on every platform
├── requirements/
│   └── README.md                   ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
python3 examples/precision_demo.py

# 2. Your task: complete the five exercises in the starter, then run it
python3 starter/precision_demo.py

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/precision_demo.py` — runs the reference program: it prints
  the exact float value of `0.1 + 0.2`, shows `math.isclose` fixing the
  comparison, contrasts a `float` cart total with an exact `Decimal` total,
  makes change with `//` and `%`, and calls a few `math` functions.
- `python3 starter/precision_demo.py` — the same program with five values
  blanked out; each numbered exercise comment names the exact expression to
  fill in. Edit the file in any text editor and replace each marked line.
- `bash tests/run_tests.sh` — runs the reference program and a set of
  `python3 -c` assertions, checking that the float error is real, that
  `math.isclose` treats the sum as `0.3`, that the `Decimal` cart total is
  exactly `28.78`, and that `725 // 100 == 7` and `725 % 100 == 25`. Exits 0
  on success, non-zero on any failure.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured run. The opening section looks like this:

```text
============================================================
1. The float trap: 0.1 + 0.2 != 0.3
============================================================
0.1 + 0.2        = 0.30000000000000004
Is it exactly 0.3? False
0.1 stored as    = 0.1000000000000000055511151231257827021181583404541015625
0.1 + 0.2 stored = 0.3000000000000000444089209850062616169452667236328125
```

Because the program does pure arithmetic on fixed numbers, **your output will
match this exactly** on any standard Python build.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists every line that
must appear.

## Validation steps

1. Run `python3 examples/precision_demo.py` — it must finish without an error.
2. Confirm the float line reads `0.30000000000000004` and `Is it exactly 0.3?
   False`.
3. Confirm the cart section charges `$28.78` (the exact `Decimal` total).
4. Complete the five exercises in `starter/precision_demo.py`; running it
   should now print the same key values as the reference.
5. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `9 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in CI.

## Cleanup

Nothing to clean up: the program writes no files and changes no settings. To
reset your work, restore the starter from git:
`git checkout -- starter/precision_demo.py`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list — the `== 0.3`
"bug" that is not a bug, `Decimal(0.1)` vs `Decimal("0.1")`, `//` vs `/`,
missing `python3`, and Windows notes.

## Security notes

See [security.md](security.md). Short version: the program makes no network
calls and needs no privileges — and, importantly, Python's `random` module is
**not** cryptographically secure. Use the `secrets` module for tokens,
passwords, and anything that must be unguessable.

## Extension exercises

1. Add a line that sums `[Decimal("0.1")] * 10` and confirms it equals
   `Decimal("1.0")` exactly — then try the same with floats and watch it drift.
2. Import `fractions.Fraction` and show that `Fraction(1, 3) * 3 == 1` exactly,
   where `1/3 * 3` in float does not always round-trip.
3. Change the cart prices and the paid amount, and confirm the change-making
   loop still hands out the right coins with `//` and `%`.

## Navigation

- **Previous day:** Day 45 — Variables, Types, and Assignment
  (`labs/sections/programming-with-python/day-045-.../`).
- **Next day:** Day 47 — Input, Output, and f-strings
  (`labs/sections/programming-with-python/day-047-input-output-and-f-strings/`, to be written).
