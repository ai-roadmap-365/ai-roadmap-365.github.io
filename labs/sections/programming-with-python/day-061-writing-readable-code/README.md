# Day 061 lab — Refactor for Readability

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Writing Readable Code
- **Day number:** 61 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-061-writing-readable-code
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-061-writing-readable-code` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 61's lesson is about code that humans — and your future self — can read.
This lab makes it concrete. You start from `starter/messy.py`: a small program
that **works** (it prints a summary of the numbers you give it) but is painful
to read — one giant function called `d`, single-letter variables, no
docstrings, no type hints, a bare magic number, cramped formatting. Your job is
to refactor it into clean, documented, type-hinted, PEP 8 code **without
changing what it does** — proven by a test suite that passes before and after.
The finished `examples/report.py` is the target to compare against. This is the
exact discipline that keeps machine-learning experiments reviewable and
reproducible, and it is what AI coding assistants read best.

## Learning objectives

- Refactor a working script in small, safe steps, running tests after each so
  behaviour never changes.
- Replace poor names with meaningful, searchable ones and a magic number with a
  named constant.
- Decompose one giant function into small, single-purpose functions.
- Add docstrings that say *why*, and type hints that document and help tools.
- Run an optional formatter (Black) and linter (Ruff/flake8), and understand
  that a missing optional tool must degrade gracefully, never hard-fail.

## Prerequisites

- The Day 61 lesson (read it first — it explains PEP 8, PEP 257, PEP 20, type
  hints, and the tools).
- Days 57–60: functions, modules and imports, and the standard library.
- Day 49: the shape of a real program — named functions, a `main()`, and the
  `if __name__ == "__main__":` guard.
- A text editor and a terminal. No experience beyond this course is assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python
  3.14.0).
- **Linux** — fully supported (any distribution with Python 3.9+ and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python` for
  `python3` if that is how Python is exposed. The scripts are pure
  standard-library Python and behave identically everywhere.

## Hardware requirements

Any computer that runs Python 3. The scripts do a handful of arithmetic
operations on the numbers you pass; they need no special memory, disk, or GPU.

## Required software

- `python3` (3.9 or newer; tested on 3.14.0).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — just `sys`. No packages to install. See
  [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. The **optional** style tools introduced in the lesson — Black
(formatter) and Ruff or flake8 (linter) — are also free and open source, but
they are not required: the test suite skips their checks cleanly when they are
absent. No account, API key, network access, or purchase is needed.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-061-writing-readable-code
python3 --version   # confirm Python 3.9+ is available
```

Optionally, to try the style tools: `python3 -m pip install black ruff`.

## File structure

```text
day-061-writing-readable-code/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── messy.py                    ← YOUR working file — refactor it for readability
│   └── refactor-worksheet.md       ← the five numbered refactoring steps + notes
├── examples/
│   └── report.py                   ← the clean, readable target (same behaviour)
├── tests/
│   └── run_tests.sh                ← behaviour + readability checks (optional style tools skipped cleanly)
├── expected-output/
│   ├── sample-run.txt              ← real captured runs (messy == clean, byte for byte)
│   ├── test-run.txt                ← real captured test-suite run
│   └── FIELDS.md                   ← required behaviour on every platform
├── requirements/
│   └── README.md                   ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See that the messy starter already works.
python3 starter/messy.py 70 85 90 55 60

# 2. See the clean target — and prove it behaves identically.
python3 examples/report.py 70 85 90 55 60
diff <(python3 starter/messy.py 70 85 90 55 60) <(python3 examples/report.py 70 85 90 55 60) && echo IDENTICAL

# 3. Establish the safety net BEFORE you touch anything.
bash tests/run_tests.sh

# 4. Refactor starter/messy.py, one step at a time (see the worksheet),
#    running the tests after each step.

# 5. Optional: if you installed them, auto-format and lint.
black starter/messy.py       # skips gracefully if not installed
ruff check starter/messy.py  # or: flake8 starter/messy.py

# 6. Confirm behaviour is unchanged and readability now passes too.
bash tests/run_tests.sh
```

## What the commands do

- `python3 starter/messy.py 70 85 90 55 60` — runs the messy-but-working
  program: it parses the numbers, then prints count, mean, median, min, max,
  population standard deviation, and the percentage passing (≥ 60).
- `python3 examples/report.py 70 85 90 55 60` — runs the clean reference, which
  produces the *same* output from small, named, typed, documented functions.
- `diff <(...) <(...) && echo IDENTICAL` — proves the two versions are
  byte-for-byte identical: refactoring changed readability, not behaviour.
- `bash tests/run_tests.sh` — characterises the behaviour with a golden output,
  asserts both the starter and the reference match it (and the empty-input and
  even-count-median paths), checks the reference for readability markers (type
  hints, docstrings, ≥ 4 functions, no single-letter function names), and —
  once your starter is refactored — holds it to the same standard. If Black or
  Ruff/flake8 are installed it runs them as a bonus; if not, it **skips** those
  checks. Exits 0 only if every non-skipped check passes.
- `black` / `ruff` — the optional formatter and linter from the lesson; both
  skip gracefully when not installed.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a real
captured session. For the input `70 85 90 55 60` both versions print:

```text
count: 5
mean: 72.00
median: 70.00
min: 55.00
max: 90.00
stdev: 13.64
passing: 80.0%
```

The tool is deterministic, so your output will match.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the required
behaviour for every input on every platform.

## Validation steps

1. `python3 starter/messy.py 70 85 90 55 60` prints the seven summary lines
   above and exits 0.
2. `diff <(python3 starter/messy.py 70 85 90 55 60) <(python3 examples/report.py 70 85 90 55 60)`
   prints nothing (the two are identical), and the `&& echo IDENTICAL` fires.
3. `bash tests/run_tests.sh` reports `10 checks, 0 failure(s), 2 skipped.`
   before you refactor.
4. Refactor `starter/messy.py` following the worksheet, testing after each
   step; behaviour must stay identical the whole way.
5. `bash tests/run_tests.sh` now reports `14 checks, 0 failure(s), 2 skipped.`
   — the readability checks now apply to your cleaned-up starter too.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is still messy: `10 checks, 0
failure(s), 2 skipped.` Once you complete the refactor, the suite additionally
holds your starter to the readability standard, giving `14 checks, 0
failure(s), 2 skipped.` The two skips are the optional Black and Ruff/flake8
checks, which are not installed by default; they never turn the suite red. The
command exits 0 on success and non-zero on any real failure, so it can run in
CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

The scripts write no files, so there is nothing to delete. To reset your
refactor and start over, restore the starter from git:

```bash
git checkout -- starter/messy.py
```

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `python` vs
`python3`, tests going red mid-refactor, the golden output not matching (sample
vs population standard deviation), old-Python `list[float]` syntax, why the
style-tool checks say "skip", the module import path, and permissions.

## Security notes

See [security.md](security.md). Short version: the tool makes no network calls,
needs no privileges, and writes no files. It parses numbers with `float()`,
never `eval()`. And readable code is safer code — a reviewer can only catch
what they can see, which is exactly why names, small functions, docstrings, and
type hints matter.

## Extension exercises

1. Add a **sample** standard deviation function (`divide by n - 1`) alongside
   the population one, with a clear name and docstring explaining the
   difference — and a test that pins its value so it never drifts.
2. Add a `--help`-style usage line printed to standard error (and exit 2) when
   a value cannot be parsed as a number, instead of letting `float()` raise —
   turning a crash into a readable error message.
3. Install Black and Ruff and run them on both files; read Ruff's output,
   understand each rule it flags, and fix or justify each one in a comment.
4. Write a short `tests/test_report.py` that imports `mean`, `median`, and
   `population_stdev` from the reference and asserts their values on a known
   list, printing `all tests passed` only if every assertion holds.

## Navigation

- **Previous day:** Day 60 — A Tour of the Standard Library
  (`labs/sections/programming-with-python/day-060-a-tour-of-the-standard-library/`).
- **Next day:** Day 62 — Recursion
  (`labs/sections/programming-with-python/day-062-recursion/`, to be written).
- **Week 9 theme:** Functions and Program Design — writing code that is not
  just correct but clear, reusable, and ready for review.
