# Day 100 lab — The Same Numbers, Three Ways

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Matrices and What They Represent
- **Day number:** 100 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-100-matrices-and-what-they-represent
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-100-matrices-and-what-they-represent` when the site is running.
<!-- generated-links:end -->

## Purpose

Twelve numbers, arranged in three rows and four columns, are read three
different ways in this lab: as a **table** of data, as a **collection of
vectors**, and as a **transformation** that eats one vector and returns
another. Nothing about the numbers changes. What changes is the question, and
almost every confusing thing about matrices comes from two pieces of code
disagreeing about which of the three is meant.

You build a matrix from nothing but nested lists — shape, indexing, transpose,
addition, scalar multiplication — and check it against NumPy at every step.
Then you find the one thing your class cannot do, which is broadcasting, and
spend the rest of the lab on the two NumPy behaviours that surprise people:
broadcasting, which invents entries you never wrote down, and views, which
means two names can share one block of memory.

Every answer here is small enough to check on paper. That is deliberate. A
lab about shapes that you cannot verify by hand is a lab that teaches you to
trust output.

## Learning objectives

By the end you will be able to:

- Read a matrix as a table, as a set of row vectors, as a set of column
  vectors, and as a transformation, and say which reading an operation assumed.
- State a matrix's shape as `(rows, columns)`, index it from zero, and
  translate between that and the from-1 subscripts a paper would use.
- Implement shape, indexing, transpose, addition, scalar multiplication and
  the identity matrix from first principles, and assert them against NumPy.
- Recognise the zero, identity, diagonal and symmetric matrices on sight and
  say what each one does.
- Apply the broadcasting rule by hand, predict success or failure before
  running anything, and name the exception NumPy raises when it fails.
- Identify the case where broadcasting silently does the wrong thing, and
  state the check that catches it.
- Say whether a given operation returns a view or a copy, and prove it with
  `numpy.shares_memory` rather than by guessing.
- Choose between `axis=0` and `axis=1` correctly, from the rule that the axis
  you name is the axis that disappears.

## Prerequisites

- Day 99 — vectors: components, magnitude, the L2 and L1 norms, unit vectors
  and distance. This lab uses `numpy.linalg.norm` on rows and columns and
  assumes you know what the number means.
- Day 43 — `python3 -m venv` and installing a package with `pip`.
- Days 071–074 — running pytest and reading its output.
- Day 65 — reading a CSV file, which is where the table reading comes from.
- Day 85 — a database table, which is the same rectangle with names on it.
- No mathematics beyond school arithmetic. Every symbol used is defined where
  it first appears.

## Supported operating systems

- macOS — run and captured here (macOS 26.5.2, Apple Silicon, arm64).
- Linux — the same commands apply unchanged. Not run here.
- Windows — use the Windows Subsystem for Linux and follow the Linux
  instructions, or Git Bash with `.venv\Scripts\python.exe` in place of
  `.venv/bin/python3`. Not run here; see `troubleshooting.md`, which says so
  plainly rather than implying a test that did not happen.

## Hardware requirements

Anything that runs Python. The largest array in this lab holds sixteen
numbers. Roughly 60 MB of disk for the virtual environment, almost all of it
NumPy.

## Required software

- `python3` — 3.14.0 here.
- `numpy` 2.5.2 and `pytest` 9.1.1, installed into a lab-local virtual
  environment from `requirements/requirements.txt`.
- `bash` — 3.2.57 here, for the test harness.

## Free and open-source options

Both dependencies are free and open source and there is no paid tier of
anything in this lab. NumPy is distributed under the BSD 3-Clause licence and
pytest under the MIT licence. No account, no key, no signup, personally or
commercially.

If you cannot install anything at all, exercise 1 — building the matrix class
from nested lists — runs on a bare `python3` with the standard library only.
Everything after it compares against NumPy or demonstrates behaviour that
exists only because NumPy exists, and the lab does not pretend otherwise.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-100-matrices-and-what-they-represent
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Expect `2.5.2`. That is the only time this lab needs the network.

## File structure

```
.
├── README.md                      this file
├── metadata.yml                   how the lab was actually run, and when
├── requirements/
│   ├── README.md                  why each package is here, and its licence
│   └── requirements.txt           numpy==2.5.2, pytest==9.1.1
├── starter/                       your work goes here
│   ├── 00_brief.md                the five exercises, in order
│   ├── conftest.py                makes this directory's matrix.py the one its tests import
│   ├── matrix.py                  exercise 1 — six methods to write
│   ├── answers.py                 exercises 2 to 5 — predictions to make
│   └── test_starter.py            your running score; unattempted work skips
├── examples/                      the reference, to read after you have tried
│   ├── conftest.py                the same import guard
│   ├── matrix.py                  the finished from-scratch matrix class
│   ├── dataset.py                 the invented data, and the hand-worked answers
│   ├── 01_matrix_from_scratch.py  your class and NumPy, asserted equal
│   ├── 02_three_meanings.py       table, vectors, transformation
│   ├── 03_views_and_copies.py     reshape, slice, ravel, transpose — who shares memory
│   ├── 04_broadcasting.py         the rule, a success, a failure, and the silent trap
│   ├── 05_axes.py                 axis=0 against axis=1, settled
│   └── test_reference.py          41 tests over real values and real shapes
├── tests/
│   └── run_tests.sh               the bash harness: 41 checks, exits non-zero on any failure
├── expected-output/               captured from real runs on 2026-08-16
│   ├── FIELDS.md                  what may legitimately differ on your machine
│   ├── 01-matrix-from-scratch.txt
│   ├── 02-three-meanings.txt
│   ├── 03-views-and-copies.txt
│   ├── 04-broadcasting.txt
│   ├── 05-axes.txt
│   ├── reference-tests.txt
│   ├── starter-progress.txt
│   └── test-run.txt
├── troubleshooting.md
└── security.md
```

## How to run

Read `starter/00_brief.md` first. Then work, checking yourself as you go:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `1 passed, 32 skipped`. A skip means "not
attempted"; a failure means "attempted and wrong", and prints both your answer
and the real one. When it prints `33 passed`, you are finished.

Afterwards, read the reference — each script prints its working and asserts
every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_matrix_from_scratch.py
../.venv/bin/python3 02_three_meanings.py
../.venv/bin/python3 03_views_and_copies.py
../.venv/bin/python3 04_broadcasting.py
../.venv/bin/python3 05_axes.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `matrix.py` and
`dataset.py` from beside themselves.

Then the full harness:

```bash
bash tests/run_tests.sh
echo "exit=$?"
```

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 -m venv .venv` | Creates a virtual environment inside the lab, so nothing here can affect the rest of your machine. `rm -rf .venv` is a complete undo. |
| `.venv/bin/pip install -r requirements/requirements.txt` | Installs numpy 2.5.2 and pytest 9.1.1. The one command that uses the network. |
| `.venv/bin/pytest starter -q` | Your running score. Unattempted exercises skip; wrong answers fail with both values printed. |
| `01_matrix_from_scratch.py` | Runs the finished from-scratch class beside NumPy and asserts they agree on shape, indexing, transpose, addition, scalar multiplication and the identity — then shows the one thing the class cannot do. |
| `02_three_meanings.py` | Reads the same twelve numbers as a table, as row and column vectors with their norms, and as a transformation applied to the price vector. |
| `03_views_and_copies.py` | Proves a reshape is a view by writing through it, proves `.copy()` breaks that, and does the same for slices, `ravel`, `flatten`, fancy indexing and transpose. |
| `04_broadcasting.py` | Applies the broadcasting rule by hand, shows `(3, 4)` with `(4,)` succeeding and with `(3,)` failing, and demonstrates the square-matrix case where the wrong answer raises nothing at all. |
| `05_axes.py` | Computes every reduction along both axes on a matrix small enough to check on paper. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 41 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 41-check harness: versions, every script, both suites, sixteen individual values, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
41 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `41 passed`, and an untouched
starter with `1 passed, 32 skipped`.

Three lines worth recognising before you meet them. The transformation:

```
    Seedling: 2*10 + 4*2 + 1*5 + 3*1 = 36
   Container: 0*10 + 5*2 + 2*5 + 7*1 = 27
      Alpine: 6*10 + 1*2 + 4*5 + 2*1 = 84
```

The view proof:

```
  before: M[0, 0] = 2, flat[0] = 2
  flat[0] = 99
  after : M[0, 0] = 99, flat[0] = 99
  Nothing was assigned to M. M changed anyway.
```

And the broadcasting failure, whose exact type the tests assert:

```
  M + numpy.array([100, 200, 300]) raises
    ValueError: operands could not be broadcast together with shapes (3,4) (3,)
```

`expected-output/FIELDS.md` records exactly which parts of the captured output
may legitimately differ on your machine — timings, the platform line, and your
own progress score — and which parts may not.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `41 checks, 0 failure(s).`
   and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `41 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `33 passed` once
   you have finished, and never prints a failure you have not been shown.
4. Each of the five scripts ends with `every assertion held.`
5. `find . -type d -name '__pycache__' -o -type d -name '.pytest_cache'`
   prints nothing after a full run.

## Tests

`tests/run_tests.sh` runs 41 checks in seven sections:

1. **Versions** — reads the installed numpy and compares it against
   `requirements/requirements.txt`, and confirms it is NumPy 2 or later.
2. **The five reference scripts** — each must exit 0 and print that every one
   of its internal assertions held.
3. **The reference pytest suite** — must exit 0, report no failures, and have
   collected at least forty tests, so a collection error cannot pass as
   success.
4. **The starter suite** — must exit 0 on an untouched checkout with skips
   rather than failures; and collecting both suites at once must not turn any
   of those skips into passes, which is a real hazard here because both
   directories contain a module called `matrix`.
5. **Sixteen individual values** — shape, transpose, the three costs from both
   implementations, both axis totals with their shapes, keepdims, the view and
   copy behaviour of reshape, slice and fancy indexing, the successful
   broadcast, the failing one with its exception type, and the silent
   square-matrix trap.
6. **A deliberate failure** — the harness re-runs itself with one expectation
   swapped for the wrong axis answer, and asserts that the re-run exits
   non-zero and reports exactly one failure. A green suite proves nothing until
   you have watched it go red.
7. **A clean disk** — no `__pycache__`, no `.pytest_cache`, and no source file
   that opens a network connection.

## Cleanup

```bash
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: resets your work
```

The lab's own commands leave none of the first two behind; section 7 of the
harness fails if they appear.

## Troubleshooting

See `troubleshooting.md`. It covers the missing-numpy and wrong-directory
import errors, the exact text of the broadcasting and reshape failures, the
read-only `broadcast_to` result, why unattempted exercises show as `s`, and the
module-name collision between the two directories — which was found while
building this lab, not imagined for the document.

## Security notes

See `security.md`. In short: this lab computes and prints. It writes no files,
opens no connection after the one-time install, needs no credentials and no
`sudo`, and all the data is invented. The one point worth carrying away is in
that file's last section: a NumPy view handed to a function carries write
access with it, so "I only passed a view" is not the same as "I only let it
read".

## Extension exercises

1. **Column-major order.** `M.reshape(12, order='F')` reads the entries down
   the columns instead of across the rows. Predict its output for this matrix,
   then check. Then find out whether it is a view, and explain why.
2. **A shape-checking decorator.** Write a decorator that records the shape of
   every array going into a function and coming out, and prints them. Apply it
   to the square-matrix trap in `04_broadcasting.py` and see whether it would
   have caught the bug.
3. **Recreate the trap deliberately.** Take a `(50, 50)` array of random
   numbers, centre it wrongly with `S - S.mean(axis=1)`, and find a statistic
   that reveals the mistake without you already knowing what it was.
4. **Extend the from-scratch class.** Add `__sub__`, an `is_diagonal` check,
   and a `trace` method — the sum of the diagonal entries. Then add a
   `broadcast_add(self, row)` that accepts a plain list of length `n_cols` and
   adds it to every row, and note how much code the two-line NumPy version
   replaced.
5. **Three dimensions.** Everything here generalises: a `(2, 3, 4)` array has
   three axes and `axis=2` is legal. Predict the shapes of its sums along each
   of the three axes before running them, and confirm that the rule — the axis
   you name is the axis that disappears — still holds without amendment.

## Navigation

- Previous day: Day 99 — Vectors: Direction, Magnitude, and Meaning
- Next day: Day 101 — Matrix Multiplication
- Week 15: Linear Algebra I: Vectors and Matrices
- Section: Mathematics, Statistics and Data
