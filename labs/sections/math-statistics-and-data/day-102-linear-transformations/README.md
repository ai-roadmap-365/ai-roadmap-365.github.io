# Day 102 lab — Where Do the Basis Vectors Land?

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Linear Transformations
- **Day number:** 102 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-102-linear-transformations
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-102-linear-transformations` when the site is running.
<!-- generated-links:end -->

## Purpose

A matrix is a function. Its columns are where the basis vectors land. If you
know where `(1, 0)` and `(0, 1)` go, you know where every vector goes — because
every vector is a combination of those two, and a linear transformation is
exactly one that keeps combinations intact.

This lab makes that sentence do work. You read a matrix off a described picture
and check its columns. You derive scaling, reflection, shear and rotation
rather than memorising them, each from the single question "where do the two
arrows land". You test the definition of *linear* on a matrix, where it holds,
and on "matrix plus a constant", where it fails — and measure the failure,
which turns out to be exactly the constant. You compose two transformations,
discover that `B @ A` means A first, and confirm that the product does in one
step what the sequence did in two. You meet the determinant as a measured area
rather than a formula, including a negative one and a zero one. And you watch
`numpy.linalg.inv` refuse to invert the zero case.

The last script is the payoff, and it is the reason the day exists: a linear
transformation always fixes the origin and always sends straight lines to
straight lines, so a stack of twenty of them collapses into one 2 by 2 matrix
and can draw no curve at all. That is the concrete, measured reason activation
functions exist.

Every answer here is small enough to check on paper. That is deliberate. A lab
about transformations whose numbers you cannot verify by hand is a lab that
teaches you to trust output.

## Learning objectives

By the end you will be able to:

- Read a transformation matrix off the landing places of the basis vectors, and
  read the landing places back off a matrix — and say why a row is not one.
- Derive the scaling, reflection, shear and rotation matrices from first
  principles, including deriving the rotation matrix from the unit circle.
- State the two conditions that define a linear transformation, test both, and
  demonstrate a function that fails both — quantifying the failure.
- Explain why a neural network layer keeps the bias separate as `X @ W + b`.
- Compose two transformations into one matrix, and get the order right.
- Interpret the determinant geometrically: as an area factor, with a sign that
  reports orientation and a zero that reports collapse.
- Say when an inverse exists, and name the exception NumPy raises when it does
  not.
- Explain rank in plain language and read it off a 2 by 2 matrix by eye.
- State, and demonstrate, why no stack of linear layers can separate data that
  needs a curve.
- Compare floats with a stated tolerance and give the reason for the number.

## Prerequisites

- Day 99 — vectors: components, magnitude, and what an arrow with coordinates
  means.
- Day 100 — matrices, and the three ways to read one. This lab lives entirely
  inside the third reading.
- Day 101 — matrix multiplication as composition. The order rule here is that
  rule, applied.
- Day 70 — floating point, which is why every comparison in this lab declares a
  tolerance.
- Day 43 — `python3 -m venv` and installing a package with `pip`.
- Days 071–074 — running pytest and reading its output.
- No mathematics beyond school arithmetic. Cosine and sine are defined from the
  unit circle where they first appear; radians are defined in the same place.

## Supported operating systems

- macOS — run and captured here (macOS 26.5.2, Apple Silicon, arm64).
- Linux — the same commands apply unchanged. Not run here.
- Windows — use the Windows Subsystem for Linux and follow the Linux
  instructions, or Git Bash with `.venv\Scripts\python.exe` in place of
  `.venv/bin/python3`. Not run here; `troubleshooting.md` says so plainly
  rather than implying a test that did not happen.

## Hardware requirements

Anything that runs Python. The largest object in this lab is a 2 by 2 matrix.
Roughly 60 MB of disk for the virtual environment, almost all of it NumPy.

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

If you cannot install anything at all, exercise 1 — all ten transformation
functions — runs on a bare `python3` with `math` and nothing else. What you
lose is every cross-check against NumPy and the exercise on the exception a
singular matrix raises. `requirements/README.md` says exactly what that costs.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-102-linear-transformations
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Expect `2.5.2`. That is the only time this lab needs the network.

## File structure

```
.
├── README.md                            this file
├── metadata.yml                         how the lab was actually run, and when
├── requirements/
│   ├── README.md                        why each package is here, and its licence
│   └── requirements.txt                 numpy==2.5.2, pytest==9.1.1
├── starter/                             your work goes here
│   ├── 00_brief.md                      the six exercises, in order
│   ├── conftest.py                      makes this directory's transforms.py the one its tests import
│   ├── shapes.py                        the invented data — read it, do not change it
│   ├── transforms.py                    exercise 1 — ten functions to write
│   ├── answers.py                       exercises 2 to 6 — thirty-one predictions
│   └── test_starter.py                  your running score; unattempted work skips
├── examples/                            the reference, to read after you have tried
│   ├── conftest.py                      the same import guard
│   ├── shapes.py                        the data, plus every answer worked by hand
│   ├── transforms.py                    the finished from-scratch module
│   ├── 01_columns_are_landings.py       a matrix off a picture, and a picture off a matrix
│   ├── 02_building_the_transformations.py  scaling, reflection, shear, rotation — derived
│   ├── 03_linear_or_not.py              both linearity tests, passed and failed
│   ├── 04_composition_and_order.py      one matrix for two steps, and the order gotcha
│   ├── 05_determinant_inverse_rank.py   area, orientation, collapse, inverse, rank
│   ├── 06_the_limit_of_linear.py        why activation functions are not optional
│   └── test_reference.py                80 tests over real values and real exceptions
├── tests/
│   └── run_tests.sh                     the bash harness: 64 checks, exits non-zero on any failure
├── expected-output/                     captured from real runs on 2026-08-16
│   ├── FIELDS.md                        what may legitimately differ on your machine
│   ├── 01-columns-are-landings.txt
│   ├── 02-building-the-transformations.txt
│   ├── 03-linear-or-not.txt
│   ├── 04-composition-and-order.txt
│   ├── 05-determinant-inverse-rank.txt
│   ├── 06-the-limit-of-linear.txt
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

On an untouched checkout that prints `1 passed, 53 skipped`. A skip means "not
attempted"; a failure means "attempted and wrong", and prints both your answer
and the real one. When it prints `54 passed`, you are finished.

Afterwards, read the reference — each script prints its working and asserts
every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_columns_are_landings.py
../.venv/bin/python3 02_building_the_transformations.py
../.venv/bin/python3 03_linear_or_not.py
../.venv/bin/python3 04_composition_and_order.py
../.venv/bin/python3 05_determinant_inverse_rank.py
../.venv/bin/python3 06_the_limit_of_linear.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `transforms.py` and
`shapes.py` from beside themselves.

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
| `01_columns_are_landings.py` | Builds a matrix from two described landing places, reads the landings back off the columns, sends `(2, 1)` through it by hand and by NumPy, and shows the identity as the do-nothing case. |
| `02_building_the_transformations.py` | Derives scaling, reflection, shear and rotation from where the basis vectors go, checks each against NumPy, applies all four to a lopsided flag, and shows every one of them leaving the origin exactly where it was. |
| `03_linear_or_not.py` | Tests both halves of the definition of linear on `M @ v`, where they hold, and on `M @ v + b`, where they fail — measuring the gap as exactly `b` and exactly `(s - 1) * b`. |
| `04_composition_and_order.py` | Shears then rotates the flag step by step, builds the single matrix that does both, confirms every corner agrees, and shows that the other order is a different transformation. |
| `05_determinant_inverse_rank.py` | Measures the transformed unit square's area for a positive, a negative and a zero determinant; shows the collapse putting the whole plane on the line `y = 2x`; computes ranks against NumPy; inverts what can be inverted, and shows both refusals for what cannot. |
| `06_the_limit_of_linear.py` | Shows the origin fixed, straight lines staying straight, twenty stacked layers collapsing to one 2 by 2 matrix, the exclusive-or arrangement no straight line separates, and a ReLU breaking linearity so that depth starts to buy something. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 80 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 64-check harness: versions, every script, both suites, thirty-seven individual values, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
64 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `80 passed`, and an untouched
starter with `1 passed, 53 skipped`.

Four blocks worth recognising before you meet them. The determinant as a
measured area:

```
  transformation      measured area   determinant   by hand
  scaling(2, 3)                 6.0           6.0       6.0
  shear_x(2)                    1.0           1.0       1.0
  reflection in x              -1.0          -1.0      -1.0
  collapse                      0.0           0.0       0.0
```

The collapse, sending two different points to one place:

```
  Two different starting points now share a landing place:
    (2, 0) -> (2.0, 4.0)
    (0, 1) -> (2.0, 4.0)
```

The refusal:

```
  numpy.linalg.inv raises LinAlgError: Singular matrix
```

And the quarter turn, which is the reason every float check here states a
tolerance:

```
  (1, 0) lands at (6.123233995736766e-17, 1.0)
  (0, 1) lands at (-1.0, 6.123233995736766e-17)
```

`expected-output/FIELDS.md` records exactly which parts of the captured output
may legitimately differ on your machine — timings, the platform line, and your
own progress score — and which parts may not. It also explains the two numbers
above that look like errors and are not.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `64 checks, 0 failure(s).`
   and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `80 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `54 passed` once you
   have finished, and never prints a failure you have not been shown.
4. Each of the six scripts ends with `every assertion held.`
5. `find . -type d -name '__pycache__' -o -type d -name '.pytest_cache'` prints
   nothing after a full run.

## Tests

`tests/run_tests.sh` runs 64 checks in seven sections:

1. **Versions** — reads the installed numpy and compares it against
   `requirements/requirements.txt`, and confirms it is NumPy 2 or later.
2. **The six reference scripts** — each must exit 0 and print that every one of
   its internal assertions held.
3. **The reference pytest suite** — must exit 0, report no failures, and have
   collected at least seventy-five tests, so a collection error cannot pass as
   success.
4. **The starter suite** — must exit 0 on an untouched checkout with skips
   rather than failures; and collecting both suites at once must not turn any
   of those skips into passes, which is a real hazard here because both
   directories contain modules called `transforms` and `shapes`.
5. **Thirty-seven individual values** — the columns and the landing places, the
   four derived matrices, the quarter turn's inexactness, both linearity
   failures and their exact sizes, both composition orders, four measured
   areas against four determinants, the collapse and its rank, the inverse of a
   shear, both singular-matrix refusals with NumPy's exact class and message,
   and the twenty-layer collapse.
6. **A deliberate failure** — the harness re-runs itself with one expectation
   swapped for the naive belief that `cos(pi / 2)` is exactly `0.0`, and asserts
   that the re-run exits non-zero and reports exactly one failure. A green suite
   proves nothing until you have watched it go red.
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
import errors, why `cos(pi / 2)` is not zero and why `numpy.linalg.det` returns
`7.000000000000001`, the singular-matrix exception, the commonest wrong
rotation (the two signs swapped, which turns clockwise), the module-name
collision between the two directories, and the argument-evaluation trap that
made an unattempted test report as a failure — all found while building this
lab rather than imagined for the document.

## Security notes

See `security.md`. In short: this lab computes and prints. It writes no files,
opens no connection after the one-time install, needs no credentials and no
`sudo`, and all the data is invented. The point worth carrying away is in that
file's last section: a transformation with determinant zero destroys
information, which is sometimes exactly the property you want and sometimes
exactly the assumption that is wrong when someone claims a step is
irreversible.

## Extension exercises

1. **Reflection in an arbitrary line.** Derive the matrix that mirrors the
   plane in the line at angle `theta` to the horizontal, by working out where
   `(1, 0)` and `(0, 1)` land. Check that its determinant is `-1` for every
   `theta`, and explain why it has to be.
2. **Projection.** Build the matrix that flattens every point onto the x axis.
   Predict its determinant and its rank before computing them. Then answer the
   question that matters: what did the plane lose, and can you name two points
   that became indistinguishable?
3. **A rotation that is not about the origin.** Turn the flag a quarter turn
   about the point `(1, 1)` rather than about the origin. You cannot do it with
   one matrix — prove that to yourself first — so do it as translate, rotate,
   translate back, and note that the middle step is the only linear one.
4. **Three dimensions.** Extend `from_landings`, `apply` and `compose` to 3 by 3
   matrices with three basis vectors. Nothing about the idea changes. Then
   build a rotation about the z axis and check that it leaves `(0, 0, 1)` alone.
5. **Eigenvectors, by hand.** Some vectors come out of a transformation pointing
   the same way they went in, only longer or shorter. For `shear_x(2)`, find
   every such direction — there is exactly one, and finding it by trying
   candidates tells you more than the formula would. Day 106 names them.
6. **Make the determinant lie.** Find a 2 by 2 matrix of small decimals whose
   true determinant is 0 but for which `numpy.linalg.det` returns something
   other than `0.0`. Then decide what tolerance you would use in production
   code to call a matrix singular, and what could go wrong with each choice.

## Navigation

- Previous day: Day 101 — Matrix Multiplication
- Next day: Day 103 — Dot Products and Similarity
- Week 15: Linear Algebra I: Vectors and Matrices
- Section: Mathematics, Statistics and Data
