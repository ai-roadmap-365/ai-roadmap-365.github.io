# Day 106 lab — The Vectors That Keep Their Direction

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Eigenvalues and Eigenvectors, Intuitively
- **Day number:** 106 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-106-eigenvalues-and-eigenvectors-intuitively
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-106-eigenvalues-and-eigenvectors-intuitively` when the site is running.
<!-- generated-links:end -->

## Purpose

Apply a matrix to twenty-four directions spread evenly around the circle.
Twenty-two of them get knocked off their line. Two do not — they come back
pointing exactly where they started, merely longer.

Those two are the eigenvectors. How much longer is the eigenvalue. That is the
entire concept, and this lab arrives at it by **measurement** before a single
symbol appears.

The order of the work is the argument. You measure first: for each of twenty-four
directions, print where it points, where its output points, and the angle
between the two. One column dips to zero. Then you sweep 180,000 directions and
find a **second** line the coarse fan stepped straight over, at 116.565 degrees.
Only then does the algebra arrive, and it arrives as an explanation of something
you have already seen rather than as a definition to be accepted.

The algebra is derived, not quoted. `A v = lambda v` becomes
`(A - lambda I) v = 0`, which says some non-zero vector is sent to the origin —
and Day 102 already told you which matrices do that: the ones with determinant
zero. So `det(A - lambda I) = 0`, and for a 2x2 that is always
`lambda^2 - (trace) lambda + (determinant) = 0`. For this lab's matrix that is
`lambda^2 - 7 lambda + 10 = 0`, which factorises over the integers into 5 and 2,
and you can do the whole thing with a pencil in about a minute.

Then the standard transformations from Day 102, each one a different answer to
"how many directions survive?": a scaling keeps every direction, a shear keeps
exactly one, a projection keeps one and *collapses* another to nothing, and a
plane rotation keeps **none at all** — which is geometrically obvious the moment
you picture it, and which NumPy reports honestly as a pair of complex
eigenvalues rather than as an error.

Then the power method: multiply, normalise, repeat. It converges on this
matrix's dominant eigenvector in 25 iterations, and the rate at which it
converges — measured at `0.399999` — turns out to be the ratio of the two
eigenvalues, `2/5`. The algorithm tells you the second eigenvalue through the
speed at which it finds the first.

Then the payoff. **Principal component analysis is the eigenvectors of a
covariance matrix.** A 400-point cloud is built deliberately stretched along 30
degrees, and that number appears nowhere in the array handed to the code. From
800 coordinates and nothing else, the top eigenvector comes back at
**30.101134 degrees**. PCA, complete, in about fifteen lines.

One trap runs through the whole lab and is worth stating up front, because it
costs people hours. **An eigenvector is defined only up to sign and scale.** If
`A v = lambda v` then the same holds for `-v` and for `3.7 v`. NumPy returns
*a* unit eigenvector and the sign it picks is a detail of the LAPACK routine
underneath, not a fact about your matrix. So `numpy.allclose` will call a
perfectly correct answer wrong, roughly half the time. Every comparison in this
lab measures the **absolute cosine** instead, which asks the only question with
a determinate answer: do these two lie on the same *line*? Exercise 5f springs
that trap on purpose, on the PCA result, where it matters most.

Nothing is downloaded. The cloud is generated from `numpy.random.default_rng(2106)`,
so every digit in `expected-output/` is reproducible on your machine.

## Learning objectives

By the end of this lab you can:

1. Measure which directions a matrix leaves on their own line, by computing the
   angle between a vector and its image, and explain why the measurement uses
   the absolute cosine.
2. Derive the characteristic equation from `(A - lambda I) v = 0` and Day 102's
   zero determinant, rather than quoting it.
3. Solve a 2x2 by hand — trace, determinant, discriminant, quadratic formula,
   then one row of `A - lambda I` per eigenvector — and check the answer against
   `numpy.linalg.eig` to a stated tolerance.
4. Say how many eigendirections each of Day 102's standard transformations has,
   and why a plane rotation has none that are real.
5. Implement the power method with normalisation and sign alignment, report its
   iteration count to a stated tolerance, and predict its convergence rate from
   the eigenvalue ratio.
6. Compute a covariance matrix from scratch, take its eigenvectors, and
   recognise that as PCA.
7. Explain why comparing eigenvectors component by component is a bug, and
   compare directions instead.
8. Choose between `numpy.linalg.eig` and `numpy.linalg.eigh`, and say what
   `eigh` does when you hand it a matrix that is not symmetric.

## Prerequisites

- Day 099 (vectors), Day 100 (matrices), Day 101 (matrix multiplication as
  composition), Day 102 (linear transformations, determinants and inverses),
  Day 103 (dot products and cosine similarity), Day 104 (NumPy) and Day 105
  (transforming images).
- Day 043 for `python3 -m venv`, and Days 071–074 for pytest.
- Day 102 is the one that matters most. This lab leans on two of its results
  constantly: that a matrix is a transformation which moves the grid, and that
  a zero determinant means the transformation squashed the plane onto a line.

No mathematics beyond Week 15. The quadratic formula is used once and is
restated where it is used.

## Supported operating systems

- **macOS** — captured here on macOS 26.5.2, Apple Silicon (arm64).
- **Linux** — every command is identical.
- **Windows** — use WSL2 and follow the Linux instructions. Native PowerShell
  works too, with `python -m venv .venv` and `.venv\Scripts\python.exe` in
  place of `.venv/bin/python3`, but `tests/run_tests.sh` is a bash script and
  needs Git Bash or WSL. This was not run on Windows and the lab does not claim
  it was.

## Hardware requirements

Anything that runs Python. The largest matrix in the lab is 400 by 400 and it is
decomposed a handful of times; everything else is 2 by 2 or 3 by 3. The full
test suite finishes in well under a second. Roughly 60 MB of disk for the
virtual environment, almost all of it NumPy.

## Required software

| Software | Version used here | Notes |
| --- | --- | --- |
| Python | 3.14.0 | 3.11 or later is fine. |
| numpy | 2.5.2 | Holds the arrays and supplies the independent answers. |
| pytest | 9.1.1 | The test runner from Days 071–074. |
| bash | 3.2.57 | For `tests/run_tests.sh`. |

`requirements/README.md` explains why each is pinned, why the from-scratch code
deliberately does not call NumPy's eigensolvers, and why scikit-learn is not
installed even though this lab does PCA.

## Free and open-source options

Both packages are free and open source, need no account, no key and no signup,
and cost nothing for personal or commercial use. NumPy is BSD 3-Clause and
pytest is MIT.

There is no paid tier and nothing here is a trial. The deliberate
non-dependencies are worth naming: **scikit-learn** would do exercise 5's PCA
better than the fifteen lines here, and **SciPy** and **PyTorch** both offer the
same eigensolvers with more options. `examples/06_eig_against_eigh.py` describes
all four from their own documentation and **reproduces no output from any of
them**, because none is installed here. Use them for real work; write the
fifteen lines once so you know what they are doing.

## Installation

From this directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Expect `2.5.2`.

This needs the network **once**. Nothing else in the lab does.

If you would rather use an environment you already have, skip the venv and
point the harness at your own pytest:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## File structure

```
day-106-eigenvalues-and-eigenvectors-intuitively/
├── README.md                     this file
├── metadata.yml                  machine-readable lab record
├── security.md                   what this lab does and does not touch
├── troubleshooting.md            symptoms, causes and fixes
├── requirements/
│   ├── requirements.txt          numpy==2.5.2, pytest==9.1.1
│   └── README.md                 why those, why pinned, what is deliberately absent
├── starter/                      YOUR WORK GOES HERE
│   ├── 00_brief.md               the five exercises, in order
│   ├── eigen.py                  six functions to write
│   ├── answers.py                twenty-six predictions to make
│   ├── dataset.py                the matrices and the cloud (read, do not edit)
│   ├── conftest.py               import guard (do not edit)
│   └── test_starter.py           your running score
├── examples/                     THE REFERENCE — read after writing your own
│   ├── 01_the_fan_of_vectors.py           measure first, define later
│   ├── 02_by_hand_2x2.py                  the characteristic equation, derived
│   ├── 03_standard_transformations.py     how many directions survive each one
│   ├── 04_power_method.py                 iterate to the dominant eigenvector
│   ├── 05_pca_from_covariance.py          PCA in fifteen lines
│   ├── 06_eig_against_eigh.py             the routines, compared and measured
│   ├── eigen.py                           the reference implementation
│   ├── dataset.py                         the same data, fully documented
│   ├── conftest.py                        import guard (do not edit)
│   └── test_reference.py                  94 tests over every claim
├── expected-output/              CAPTURED from real runs, never fabricated
│   ├── 01..06-*.txt              one file per reference script
│   ├── reference-tests.txt       `94 passed`
│   ├── starter-progress.txt      `1 passed, 52 skipped`
│   ├── test-run.txt              the full harness output
│   └── FIELDS.md                 what may legitimately differ on your machine
└── tests/
    └── run_tests.sh              110 checks, exits 0 only if all pass
```

## How to run

Work through `starter/00_brief.md`. Check yourself as often as you like:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `1 passed, 52 skipped`. A **skip** means
"not attempted yet", not "broken". When it says `53 passed`, you are finished.

Then read the reference, which prints the whole story with real numbers:

```bash
cd examples
../.venv/bin/python3 01_the_fan_of_vectors.py
../.venv/bin/python3 02_by_hand_2x2.py
../.venv/bin/python3 03_standard_transformations.py
../.venv/bin/python3 04_power_method.py
../.venv/bin/python3 05_pca_from_covariance.py
../.venv/bin/python3 06_eig_against_eigh.py
cd ..
```

And run everything:

```bash
bash tests/run_tests.sh
```

## What the commands do

| Command | What it does |
| --- | --- |
| `.venv/bin/pytest starter -q` | Your score. Skips are unattempted exercises; failures print your answer beside the real one. |
| `01_the_fan_of_vectors.py` | Applies `A` to 24 directions and prints the swing of each. Two come back at zero. Then sweeps 180,000 directions and finds the second line the fan missed. |
| `02_by_hand_2x2.py` | Derives the characteristic equation from `(A - lambda I) v = 0`, solves it with the quadratic formula, reads both eigenvectors out of the squashed matrix, and compares against `numpy.linalg.eig` — including the comparison that *fails* because of the sign. |
| `03_standard_transformations.py` | Every matrix from Day 102, with two independent answers each: what `eig` says and what a brute-force sweep measures. Where they seem to disagree, the disagreement is the lesson. |
| `04_power_method.py` | Iterates to the dominant eigenvector, prints the direction and Rayleigh quotient at each step, measures the convergence rate against the predicted `0.4`, and shows what un-normalised iteration does. |
| `05_pca_from_covariance.py` | Builds the cloud, centres it, computes the covariance from scratch, takes the eigenvectors, and recovers the elongation direction. Then shows what forgetting to centre costs. |
| `06_eig_against_eigh.py` | The four NumPy routines side by side, `eigh` on non-symmetric input, a timing comparison on a 400x400, and honest descriptions of SciPy, PyTorch and scikit-learn that were **not** run. |
| `bash tests/run_tests.sh` | 110 checks over all of the above, including a section that deliberately breaks one expectation to prove the harness can fail. |

## Expected output

Everything in `expected-output/` was captured from real runs on the authoring
machine on 17 August 2026. The last line of the harness is:

```
110 checks, 0 failure(s).
```

Some highlights you should see reproduced exactly:

```
   Directions that came back on their own line: [45, 225]
     a surviving line near   45.000000 degrees  (deviation 0.000e+00)
     a surviving line near  116.565000 degrees  (deviation 7.676e-05)

   eigenvalues  = [5.+0.j 2.+0.j]
   dtype        = complex128

       iterations         25
       eigenvalue         5.000000000045

       top component      [-0.86514150, -0.50152786]
       its direction      30.101134 degrees
       the truth          30.0 degrees
```

`expected-output/FIELDS.md` names precisely what may legitimately differ on your
machine — the timings, the platform string, and **the sign of any eigenvector**.

## Validation steps

1. `bash tests/run_tests.sh` ends with `0 failure(s).` and exits 0.
2. `.venv/bin/pytest examples -q` reports `94 passed`.
3. `.venv/bin/pytest starter -q` reports `1 passed, 52 skipped` before you start
   and `53 passed` when you are done.
4. All six reference scripts exit 0 and print `every assertion held.`
5. Diff your own output against `expected-output/`, then read `FIELDS.md` before
   worrying about any difference you find. A flipped sign is not a difference.

Check the exit status of the harness directly, not of a pipeline:

```bash
bash tests/run_tests.sh; echo "exit=$?"
```

## Tests

`tests/run_tests.sh` runs 110 checks in seven sections:

1. **Versions** — the installed numpy and pytest match `requirements.txt`.
2. **Scripts** — all six reference scripts exit 0 and report every assertion
   holding.
3. **Reference suite** — `pytest examples` passes, with at least 90 tests.
4. **Starter suite** — passes with skips rather than failures, *and* the skip
   count is unchanged when both suites are collected together. That second
   check matters: both directories contain modules called `eigen` and `dataset`,
   and without each directory's `conftest.py` a bare `pytest` would let the
   starter tests import the **reference** solution and report unwritten
   exercises as passing. A wrong answer with a green tick on it is the worst
   kind, so it is checked rather than assumed.
5. **Claims** — 60-odd individual values, each one read from a real computation:
   the surviving directions, the trace and determinant, the `complex128` dtype,
   the shear's one line against `eig`'s two columns, the rotation's verdict of
   `none`, the 25 iterations, the 962 iterations at ratio 0.98, the recovered
   30.101134 degrees, the 136.583965-degree cost of forgetting to centre.
6. **The harness can fail** — re-runs the whole script with one expectation
   swapped for the naive belief that a shear has two eigendirections because
   `eig` returns two columns, and asserts that the re-run names the failure and
   exits non-zero. A green suite proves nothing until you have watched it go red.
7. **Cleanliness** — no `__pycache__`, no `.pytest_cache`, no data file, and no
   source that opens a socket.

Section 7's `find` commands prune `.venv` first, deliberately. This README tells
you to create a lab-local virtual environment, so `.venv` is the documented
setup rather than litter — and NumPy ships 113 `__pycache__` directories and
several data files inside it. Without the prune, the lab would fail you for
following its own installation instructions.

## Cleanup

```bash
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: resets your work
```

The lab sets `PYTHONDONTWRITEBYTECODE=1` while it runs, so in practice there is
usually nothing to clean. Nothing is written outside this directory.

## Troubleshooting

`troubleshooting.md` covers the full list. The three that catch nearly everyone:

**"My eigenvector doesn't match and I can't see why."** Check whether it is the
exact negative of the expected one. If it is, both answers are correct and the
comparison is the bug. Use the absolute cosine.

**"`numpy.sqrt` gave me `nan` on the rotation."** A rotation's discriminant is
negative. `numpy.sqrt(-4.0)` returns `nan` and warns; `numpy.emath.sqrt(-4.0)`
returns `2j`, which is the answer. This is the difference between "no real
eigenvalues, and here is why" and "something went wrong".

**"My power method never converges."** Almost always the sign alignment. If the
dominant eigenvalue is negative, the iterate flips direction every single step,
so the distance between successive vectors never shrinks — even though the
*answer* settled several rounds ago. Negate `w` when `numpy.dot(w, v) < 0`.

## Security notes

`security.md` has the detail. In short: this lab needs the network exactly once,
to install two packages from PyPI. After that it is entirely offline. It binds
no port, reads no file it did not generate, writes nothing outside its own
directory, needs no key, no account and no `sudo`, and processes no personal
data — the only dataset is 400 points drawn from a seeded random generator.

## Extension exercises

1. **Find the *smallest* eigenvalue with the power method.** Run it on
   `numpy.linalg.inv(A)` instead. The dominant eigenvector of the inverse is the
   *least* dominant eigenvector of `A`, because inverting a matrix inverts its
   eigenvalues and leaves its eigenvectors alone. Verify that claim first, then
   use it. This is the inverse power method.
2. **Deflation.** Once you have the dominant eigenpair `(lambda1, v1)` of a
   symmetric matrix, subtract `lambda1 * numpy.outer(v1, v1)` from it and run the
   power method again. You should get the *second* eigenvector. Try it on
   `SYMMETRIC_3X3` and check all three against `numpy.linalg.eigh`. Then try it
   on the non-symmetric `A` and work out why it does not work there.
3. **PCA on something real.** Replace the invented cloud with any table you have
   — three or four numeric columns from a spreadsheet. Standardise each column
   to zero mean and unit variance first, then take the eigenvectors. Read the
   top one as a set of weights: which columns does it lean on? That is the
   normal way to interpret a principal component, and it is why standardising
   matters, since without it the column with the largest units dominates.
4. **Break the power method on purpose.** Build a 2x2 whose two eigenvalues have
   the *same magnitude* but opposite signs, such as `numpy.diag([3.0, -3.0])`.
   Predict what the iteration does, then watch it. There is no single dominant
   direction, and the honest outcome is that it never converges.
5. **Complex eigenvectors are real objects.** `numpy.linalg.eig` on a rotation
   returns complex eigenvectors as well as complex eigenvalues. Verify that
   `A v = lambda v` still holds exactly for those complex pairs, then work out
   what the real and imaginary parts of the eigenvector mean geometrically. They
   span the plane the rotation is happening in.

## Navigation

- Lab index: [`../README.md`](../README.md)
- Section labs: [`../README.md`](../README.md)
- Previous lab: [`../day-105-transforming-images-with-matrices/`](../day-105-transforming-images-with-matrices/)
