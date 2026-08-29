# Day 101 lab — Multiply It Yourself

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Matrix Multiplication
- **Day number:** 101 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-101-matrix-multiplication
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-101-matrix-multiplication` when the site is running.
<!-- generated-links:end -->

## Purpose

Matrix multiplication looks like an arbitrary rule until you see what it is,
and then it is the only rule it could be. It is **composition**: doing one
transformation and then another. The inner dimensions have to match because the
second thing must accept what the first one produces. Nothing about it is a
convention to memorise.

You implement it three times — as three nested loops, as a list of dot products,
and as a weighted sum of the matrix's columns — and assert all three against
NumPy's `@` on six different shapes. Then you verify one output cell by hand,
watch `A @ B` and `B @ A` come out genuinely different, prove that `*` and `@`
are different operations on the same operands, trigger a shape error on purpose
and read it properly, and compute one layer of a neural network — `X @ W + b` —
with a pen.

That last one is the point of the day. One layer of a neural network is a matrix
multiply plus a vector add, and by the end of this lab you will have done that
operation by hand. It is where essentially all training compute goes.

Every answer here is small enough to check on paper. That is deliberate.

## Learning objectives

By the end you will be able to:

- Compute a dot product both ways — multiply pairwise and add, and the geometric
  statement about lengths and the angle between — and say why the two agree.
- Implement matrix multiplication from first principles three different ways and
  assert them equal to each other and to NumPy across six shapes.
- Read matrix-vector multiplication as a **linear combination of the matrix's
  columns**, and read a transformation matrix's columns as the images of the
  basis vectors.
- Derive the shape rule `(m, n) @ (n, p) -> (m, p)` from what the operation
  does, rather than recalling it.
- Demonstrate that multiplication is not commutative with a pair where both
  `A @ B` and `B @ A` are defined and different, and say which matrix acts first.
- Use associativity and distributivity correctly, and count the multiplications
  each association of a chain costs.
- State the difference between `*` and `@` precisely — `@` is `*` followed by a
  sum along the last axis — and predict both the shape and the values of each.
- Read a shape error by printing the two shapes first, and choose between the
  two transpose repairs on meaning rather than on which one runs.
- Compute one network layer by hand, with the bias broadcast across rows, and
  explain why two linear layers with no activation between them collapse into one.
- Explain why the Python loop loses to NumPy, and why the dtype decides whether
  BLAS is involved at all.

## Prerequisites

- Day 99 — vectors: components, magnitude, the L2 norm, and the dot product
  introduced geometrically. This lab computes it both ways and reconciles them.
- Day 100 — matrices: shape, transpose, broadcasting, views versus copies, and
  axis semantics. The bias add here is broadcasting doing its job, and the
  `[[0] * p] * m` trap is the view lesson in plain Python.
- Day 70 — floating point, which is why the associativity section states a
  tolerance instead of using `==`.
- Days 071–074 — running pytest and reading its output.
- Day 43 — `python3 -m venv` and installing a package with `pip`.
- No mathematics beyond school arithmetic. Every symbol is defined where it
  first appears.

## Supported operating systems

- macOS — run and captured here (macOS 26.5.2, Apple Silicon, arm64).
- Linux — the same commands apply unchanged. Not run here.
- Windows — use the Windows Subsystem for Linux and follow the Linux
  instructions, or Git Bash with `.venv\Scripts\python.exe` in place of
  `.venv/bin/python3`. Not run here; `troubleshooting.md` says so plainly rather
  than implying a test that did not happen.

## Hardware requirements

Anything that runs Python. The largest array in this lab is 200 by 200 float64,
which is 320 KB. Roughly 60 MB of disk for the virtual environment, almost all
of it NumPy. The timing script takes a few seconds.

## Required software

- `python3` — 3.14.0 here.
- `numpy` 2.5.2 and `pytest` 9.1.1, installed into a lab-local virtual
  environment from `requirements/requirements.txt`.
- `bash` — 3.2.57 here, for the test harness.

## Free and open-source options

Both dependencies are free and open source and there is no paid tier of anything
in this lab. NumPy is distributed under the BSD 3-Clause licence and pytest
under the MIT licence. No account, no key, no signup, personally or
commercially.

If you cannot install anything at all, **exercise 1 — the entire from-scratch
build, all nine functions — runs on a bare `python3` with the standard library
only.** That is most of the lab's work. Everything after it compares against
NumPy or demonstrates behaviour that exists only because NumPy exists, and the
lab does not pretend otherwise.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-101-matrix-multiplication
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
│   ├── README.md                  why each package is here, its licence, and the BLAS note
│   └── requirements.txt           numpy==2.5.2, pytest==9.1.1
├── starter/                       your work goes here
│   ├── 00_brief.md                the six exercises, in order
│   ├── conftest.py                makes this directory's matmul.py the one its tests import
│   ├── matmul.py                  exercise 1 — nine functions to write
│   ├── answers.py                 exercises 2 to 6 — predictions to make
│   └── test_starter.py            your running score; unattempted work skips
├── examples/                      the reference, to read after you have tried
│   ├── conftest.py                the same import guard
│   ├── matmul.py                  the finished from-scratch implementation, three ways
│   ├── dataset.py                 the invented data, with every answer worked by hand
│   ├── 01_matmul_from_scratch.py  three implementations and NumPy, asserted equal
│   ├── 02_composition.py          composition, non-commutativity, associativity, cost
│   ├── 03_star_versus_at.py       `*` against `@`, the shape error, both transpose repairs
│   ├── 04_network_layer.py        X @ W + b, worked by hand, and what it costs at scale
│   ├── 05_cost_and_speed.py       association cost, and the loop against NumPy
│   └── test_reference.py          71 tests over real values, shapes and exception types
├── tests/
│   └── run_tests.sh               the bash harness: 58 checks, exits non-zero on any failure
├── expected-output/               captured from real runs on 2026-08-16
│   ├── FIELDS.md                  what may legitimately differ on your machine
│   ├── 01-matmul-from-scratch.txt
│   ├── 02-composition.txt
│   ├── 03-star-versus-at.txt
│   ├── 04-network-layer.txt
│   ├── 05-cost-and-speed.txt
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

On an untouched checkout that prints `1 passed, 56 skipped`. A skip means "not
attempted"; a failure means "attempted and wrong", and prints both your answer
and the real one. When it prints `57 passed`, you are finished.

Afterwards, read the reference — each script prints its working and asserts
every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_matmul_from_scratch.py
../.venv/bin/python3 02_composition.py
../.venv/bin/python3 03_star_versus_at.py
../.venv/bin/python3 04_network_layer.py
../.venv/bin/python3 05_cost_and_speed.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `matmul.py` and
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
| `01_matmul_from_scratch.py` | The dot product, matrix-vector as a sum of columns, then three from-scratch implementations asserted equal to each other and to NumPy on six shapes, the identity matrix, and the shape rule broken on purpose. |
| `02_composition.py` | Two transformations of the plane applied in both orders with real coordinates, the single product matrix reaching the same point, `A @ B` against `B @ A`, associativity, distributivity, and what the association order costs. |
| `03_star_versus_at.py` | `*` and `@` on the same operands: same shape and different values, then different shapes. The three spellings `@`, `np.matmul` and `np.dot`. A deliberate shape error and both transpose repairs. |
| `04_network_layer.py` | One layer, `X @ W + b`, worked by hand; a wrong-length bias; growing the batch; two layers collapsing without an activation; and what one wide layer costs. |
| `05_cost_and_speed.py` | Both associations of a chain counted, then the Python loop timed against NumPy on int64 and on float64 — where the dtype turns out to matter more than expected. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 71 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 58-check harness: versions, every script, both suites, the import guard, thirty individual values, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
58 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `71 passed`, and an untouched starter
with `1 passed, 56 skipped`.

Four things worth recognising before you meet them. The highlighted output cell,
computed in full:

```
      row 1 of X    = [0, 1, 3]
      column 1 of W = [0, 1, 4]
      0*0 + 1*1 + 3*4 = 0 + 1 + 12 = 13
```

Composition arriving at the same point two ways:

```
      B @ v          = [3, -1]      (reflected: y flipped sign)
      A @ (B @ v)    = [1, 3]      (then turned a quarter anticlockwise)
      A @ B          = [[0, 1], [1, 0]]
      (A @ B) @ v    = [1, 3]
```

Order mattering, with both products fully computed:

```
  A @ B = [[0, 1], [1, 0]]   reflection in the line y = x
  B @ A = [[0, -1], [-1, 0]]   reflection in the line y = -x
```

And the timing, whose **ratios** are the point and whose durations are not:

```
      three nested loops in Python  :    0.1957 s
      NumPy @ on int64  (best of 5) :  0.002479 s          79x faster than the loop
      NumPy @ on float64 (best of 5):  0.000037 s       5,223x faster than the loop
```

That third line is not a typo, and the gap between the two NumPy rows is the
most interesting number in the lab. `expected-output/FIELDS.md` records exactly
which parts of the captured output may legitimately differ on your machine and
which may not.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `58 checks, 0 failure(s).`
   and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `71 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `57 passed` once you
   have finished, and never prints a failure you have not been shown.
4. Each of the five scripts ends with `every assertion held.`
5. `find . -type d -name '__pycache__' -o -type d -name '.pytest_cache'` prints
   nothing after a full run.

## Tests

`tests/run_tests.sh` runs 58 checks in seven sections:

1. **Versions** — reads the installed numpy, compares it against
   `requirements/requirements.txt`, and confirms it is NumPy 2 or later.
2. **The five reference scripts** — each must exit 0 and print that every one of
   its internal assertions held.
3. **The reference pytest suite** — must exit 0, report no failures, and have
   collected at least sixty tests, so a collection error cannot pass as success.
4. **The starter suite** — must exit 0 on an untouched checkout with skips
   rather than failures; and collecting both suites at once must not turn any of
   those skips into passes, which is a real hazard here because both directories
   contain a module called `matmul`.
5. **Thirty individual values** — the dot product three ways, all three
   implementations against NumPy, the hand-checked output cell, the column
   reading, the shape rule and both its error types, both transpose repairs,
   non-commutativity on two different pairs, composition in one step and two,
   associativity, `*` against `@` in both the same-shape and different-shape
   cases, the identity, the network layer from both implementations, the
   wrong-length bias, the layer collapse, all four cost counts, and the timing
   ratio.
6. **A deliberate failure** — the harness re-runs itself with the layer output
   swapped for a wrong one, and asserts that the re-run exits non-zero and
   reports exactly one failure. A green suite proves nothing until you have
   watched it go red.
7. **A clean disk** — no `__pycache__`, no `.pytest_cache`, and no source file
   that opens a network connection.

No test in this lab asserts a duration. The one performance claim is a wide
ratio, set far below what was measured, so a slow or busy machine still passes.

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

See `troubleshooting.md`. It covers the missing-numpy and wrong-directory import
errors, the exact text of NumPy's shape error and how to read it, the two
transpose repairs and why picking one at random is a bad habit, the
`[[0] * p] * m` aliasing bug, the composition-order mistake, why unattempted
exercises show as `s`, and the module-name collision between the two
directories — which was found while building the Day 100 lab, not imagined for
the document.

## Security notes

See `security.md`. In short: this lab computes and prints. It writes no files,
opens no connection after the one-time install, needs no credentials and no
`sudo`, and all the data is invented. Two points are worth carrying away: NumPy
integer matrix products **overflow silently** with no warning at all, shown
there with real numbers from a real run; and floating-point addition is not
associative, so the two association orders of a chain agree to a tolerance and
not bit-for-bit.

## Extension exercises

1. **The angle, computed.** Add a function that returns the angle between two
   vectors in degrees, from `cos(theta) = (u . v) / (|u| |v|)`. Check it on the
   pairs in `dataset.py`: `[2, 0]` and `[1, 1]` should give exactly 45, and
   `[3, 4]` and `[-4, 3]` exactly 90. Then feed it two vectors of length 300 and
   see what angle random high-dimensional vectors tend to make with each other.
   The answer is surprising and it matters for embeddings.
2. **Find the crossover.** `matmul_loops` beats NumPy at some very small size,
   because NumPy has a fixed per-call overhead. Find the size where they cross
   on your machine by doubling. Then explain why the crossover moves when you
   switch the arrays between `int64` and `float64`.
3. **Optimal chain order.** Given a list of shapes `[(10, 100), (100, 5),
   (5, 50), (50, 2)]`, write a function that tries every bracketing and returns
   the cheapest. Four matrices have five bracketings; six have forty-two. Look
   up how fast that count grows before you try ten.
4. **Strassen's algorithm.** Two 2 by 2 matrices can be multiplied with seven
   multiplications instead of eight. Implement it for the 2 by 2 case and check
   it against your own `matmul_loops`. Then work out why that saving matters
   enormously in theory and rarely in practice.
5. **The backward pass.** If a layer computes `Y = X @ W`, then the gradient
   flowing back to `X` is `G @ W.T` and the gradient for `W` is `X.T @ G`, where
   `G` has the shape of `Y`. Do not take that on trust — check that the shapes
   work out for the `X` and `W` in this lab, and notice that both transposes you
   met in exercise 4 have now turned up doing real work.
6. **Make the overflow bite.** Take the silent-overflow example from
   `security.md` and find the smallest square matrix of identical positive
   integers whose product overflows `int64`. Then check whether casting to
   `float64` gives you the right answer, the wrong answer, or a warning.

## Navigation

- Previous day: Day 100 — Matrices and What They Represent
- Next day: Day 102 — Linear Transformations
- Week 15: Linear Algebra I: Vectors and Matrices
- Section: Mathematics, Statistics and Data
