# Day 107 lab — Choose Your Distance on Purpose

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Norms, Distances, and Similarity Measures
- **Day number:** 107 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-107-norms-distances-and-similarity-measures
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-107-norms-distances-and-similarity-measures` when the site is running.
<!-- generated-links:end -->

## Purpose

"Distance" is not one thing. It is a family, and picking a member is a
modelling decision that changes which answer you get.

This lab makes that concrete in the first thirty seconds. One query, three
candidate articles, four numbers each — and L1 picks the first, L2 picks the
second, cosine picks the third. No randomness, nothing to tune, nothing wrong
with any of them. They are answers to three different questions, and until
somebody decides which question is being asked, the top result is chosen by a
default nobody discussed.

Then you build the family yourself. Seventeen functions in pure Python:
the general p-norm and its L1, L2 and L-infinity special cases, Hamming for
categorical data, Jaccard for sets, covariance and Mahalanobis, standardisation,
and one ranking function that takes the measure as a parameter — so swapping
Manhattan for cosine is one argument and you can watch the rankings move.

Four results the lab establishes by measurement rather than assertion:

- **Cosine distance is not a metric.** Going from east to north *via* the
  diagonal costs 0.5858; going direct costs 1.0. The detour is shorter, which
  no metric may allow. The lab also sweeps all 3375 triples of non-zero 4-bit
  vectors and finds 326 violations — while Jaccard distance and Hamming
  distance survive all 4096 triples of their own sweeps.
- **Chebyshev accepts a part that L1 and L2 both rank as the worse one**,
  because "no dimension may be out by more than 0.05 mm" is an L-infinity ball
  and cannot be written as anything else.
- **Jaccard and cosine rank the same two sets in opposite orders.** An
  eleven-ingredient recipe containing all four things you asked for wins on
  cosine (0.6030 against 0.5774) and loses on Jaccard (0.3636 against 0.4000).
- **Standardising changes the winner.** With bore diameter in metres and mass
  in grams, the bore column contributes 0.0036 per cent of every distance in
  the table, and the winner is a bearing 60 per cent oversize on the dimension
  that matters. Divide both columns by their own standard deviations and the
  answer changes. Change nothing but the *unit* of one column and it changes
  too.

The Mahalanobis section ties the day back to Day 106. Two probe points sit the
same Euclidean distance from the mean of eight sensor readings — both
sqrt(18) = 4.2426 — and Mahalanobis puts one at 1.1142 and the other at exactly
6.0. The lab then decomposes both by hand along the covariance matrix's
eigenvectors and shows the two numbers falling out of the eigenvalues 0.5 and
14.5.

Nothing is downloaded. Every dataset is a literal table in `catalogue.py`,
small enough to check on paper.

## Learning objectives

By the end of this lab you can:

1. Compute L1, L2, L-infinity, Hamming, Jaccard, cosine and Mahalanobis from
   first principles, and say what question each one is answering.
2. Write the general p-norm, including the infinity case as a limit rather than
   as arithmetic, and explain why `p < 1` must be refused.
3. State the four norm axioms and the four metric axioms, check each
   numerically, and name the one that squared Euclidean distance breaks.
4. Produce a concrete counter-example showing cosine distance failing the
   triangle inequality, and give the standard repair.
5. Choose between Manhattan, Euclidean and Chebyshev by the shape of the
   problem rather than by habit.
6. Recognise categorical and set-valued data and reach for Hamming or Jaccard
   instead of encoding it as integers and pretending.
7. Build a covariance matrix, invert it, and use it to measure distance in the
   data's own directions.
8. Demonstrate that scaling silently decides a ranking, and pick between
   z-score, min-max and a measure that needs neither.

## Prerequisites

- Day 099 (vectors, the L1 and L2 norms, Euclidean distance), Day 100
  (matrices), Day 101 (matrix multiplication), Day 103 (dot products, cosine
  similarity and its failure of the triangle inequality), Day 104 (NumPy) and
  Day 106 (eigenvalues and eigenvectors, and the covariance matrix).
- Day 043 for `python3 -m venv`, and Days 071–074 for pytest.
- Day 070 for floating point, which is why every comparison here states a
  tolerance.

No statistics beyond a mean and a standard deviation is assumed; the lab builds
both.

## Supported operating systems

- **macOS** — captured here on macOS 26.5.2, Apple Silicon (arm64).
- **Linux** — every command is identical.
- **Windows** — use WSL2 and follow the Linux instructions. Native PowerShell
  works too, with `python -m venv .venv` and `.venv\Scripts\python.exe` in
  place of `.venv/bin/python3`, but `tests/run_tests.sh` is a bash script and
  needs Git Bash or WSL. This was not run on Windows and the lab does not claim
  it was.

## Hardware requirements

Anything that runs Python. The largest dataset in the lab has eight rows and
the largest sweep is 3375 triples of four-bit vectors; the entire suite
finishes in well under a second. Roughly 60 MB of disk for the virtual
environment, almost all of it NumPy.

## Required software

| Software | Version used here | Notes |
| --- | --- | --- |
| Python | 3.14.0 | 3.10 or later is fine. |
| numpy | 2.5.2 | The independent answer: `linalg.norm(ord=p)`, `cov`, `linalg.inv`, `linalg.eigh`, and one seeded generator. |
| pytest | 9.1.1 | The test runner from Days 071–074. |
| bash | 3.2.57 | For `tests/run_tests.sh`. |

`requirements/README.md` explains why each is pinned and what you would lose
without NumPy.

## Free and open-source options

Both packages are free and open source, need no account, no key and no signup,
and cost nothing for personal or commercial use. NumPy is BSD 3-Clause, pytest
is MIT.

There is no paid tier and nothing here is a trial. The one deliberate
non-dependency is worth naming: every dataset is written out in
`catalogue.py`, so the lab needs no data file, no data licence and no network
after the install.

Three other libraries do this same work and are described in the lesson but
are **not installed here and produce no output in this lab**:
`scipy.spatial.distance`, scikit-learn's `pairwise_distances`, and the distance
metrics that vector databases expose. Each is free and open source too. The
lesson says plainly which tools were run and which were not.

## Installation

From the lab directory:

```bash
cd labs/sections/math-statistics-and-data/day-107-norms-distances-and-similarity-measures
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Expect `2.5.2`. This is the only step that needs the network.

## File structure

```
day-107-norms-distances-and-similarity-measures/
├── README.md
├── metadata.yml
├── troubleshooting.md
├── security.md
├── requirements/
│   ├── README.md              why each package, and what you lose without it
│   └── requirements.txt       numpy and pytest, both pinned
├── starter/                   YOUR WORK
│   ├── 00_brief.md            read this first
│   ├── measures.py            seventeen functions to write
│   ├── answers.py             twenty-five predictions to make
│   ├── catalogue.py           the datasets, written for you
│   ├── test_starter.py        your running score
│   └── conftest.py            the import guard (see below)
├── examples/                  THE REFERENCE, read after you attempt
│   ├── measures.py            the complete implementation, no NumPy anywhere
│   ├── catalogue.py           identical to the starter copy
│   ├── 01_three_measures_three_winners.py
│   ├── 02_the_p_norm_family.py
│   ├── 03_metrics_and_non_metrics.py
│   ├── 04_choosing_by_the_shape_of_the_data.py
│   ├── 05_mahalanobis_distance.py
│   ├── 06_scaling_changes_the_answer.py
│   ├── test_reference.py      105 tests over the reference implementation
│   └── conftest.py            the import guard
├── tests/
│   └── run_tests.sh           the harness: 98 checks
└── expected-output/           captured from real runs, never hand-written
    ├── 01-three-measures-three-winners.txt … 06-scaling-changes-the-answer.txt
    ├── reference-tests.txt
    ├── starter-progress.txt
    ├── test-run.txt
    └── FIELDS.md              what may legitimately differ on your machine
```

**About the two `conftest.py` files.** `examples/` and `starter/` both contain
modules called `measures` and `catalogue`. pytest imports a test file by
putting its directory on `sys.path`, so running `pytest` across both at once
would import whichever `measures` it saw first and reuse it for the other
suite — which would let the starter tests pass against the reference solution
and report unwritten exercises as done. Each `conftest.py` prevents that, and
section 4 of the harness proves it still works by checking that the skip count
is unchanged whether you run `pytest starter` or bare `pytest`.

## How to run

Read `starter/00_brief.md`, then work through `starter/measures.py` and
`starter/answers.py`. Check yourself at any point:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `1 passed, 71 skipped`. Unattempted work
is **skipped**, not failed. When it says `72 passed`, you are finished.

To see the finished versions — after you have attempted the exercises:

```bash
cd examples
../.venv/bin/python3 01_three_measures_three_winners.py
../.venv/bin/python3 02_the_p_norm_family.py
../.venv/bin/python3 03_metrics_and_non_metrics.py
../.venv/bin/python3 04_choosing_by_the_shape_of_the_data.py
../.venv/bin/python3 05_mahalanobis_distance.py
../.venv/bin/python3 06_scaling_changes_the_answer.py
cd ..
```

And the whole thing at once:

```bash
bash tests/run_tests.sh
```

## What the commands do

| Command | What it does |
| --- | --- |
| `01_three_measures_three_winners.py` | The disagreement. Three candidates, four measures, three different winners, then why each one is right on its own terms. |
| `02_the_p_norm_family.py` | One formula, one dial. The p sweep from 1 to infinity, the three unit balls drawn on the same grid as a diamond, a circle and a square, all four norm axioms checked, and why squared Euclidean distance is not a norm. |
| `03_metrics_and_non_metrics.py` | The four metric axioms. Cosine distance failing two of them with concrete numbers, angular distance repairing it, and exhaustive triangle-inequality sweeps over 4096 triples for Jaccard and for Hamming. |
| `04_choosing_by_the_shape_of_the_data.py` | Four data shapes, four right answers. Grid movement, a tolerance check, categorical fields, and Jaccard against cosine on the same two sets. |
| `05_mahalanobis_distance.py` | Two points Euclidean cannot tell apart. The covariance matrix by hand, the pure-Python inverse against NumPy's, and the whole thing rebuilt from Day 106's eigenvectors. |
| `06_scaling_changes_the_answer.py` | Metres against grams. The ranking before and after standardising, a unit change alone flipping it, z-score against min-max against Mahalanobis, and a seeded 2000-catalogue sweep. |
| `pytest examples -q` | 105 tests over the reference implementation. |
| `pytest starter -q` | Your score. Skips what you have not written. |
| `bash tests/run_tests.sh` | 98 checks: versions, all six scripts, both suites, the import guard, every claim above re-measured, a deliberate self-failure, and a hygiene sweep. |

## Expected output

The final line of the harness on the authoring machine:

```
98 checks, 0 failure(s).
```

The disagreement the day is built on, from
`expected-output/01-three-measures-three-winners.txt`:

```
                          L1          L2       L-inf      cosine
    ------------------------------------------------------------
    Aisle             5.0000      5.0000      5.0000      0.7926
    Beacon            6.0000      3.4641      2.0000      0.8944
    Cartogram        20.0000     10.9545      8.0000      1.0000

    L1 (Manhattan)       picks  Aisle
    L2 (Euclidean)       picks  Beacon
    L-inf (Chebyshev)    picks  Beacon
    cosine similarity    picks  Cartogram
```

The three unit balls, from `expected-output/02-the-p-norm-family.txt` — `#` is
inside the L1 ball, `+` reaches out to the L2 circle, `.` fills the corners of
the L-infinity square:

```
          ................+++++++###+++++++................
          ...........+++++++++#########+++++++++...........
          ........++++++++++#############++++++++++........
          ......+++++++++###################+++++++++......
          ....+++++++++#######################+++++++++....
          ...+++++++#############################+++++++...
          ..++++++#################################++++++..
          .++++#######################################++++.
          .++###########################################++.
          #################################################
          .++###########################################++.
          .++++#######################################++++.
          ..++++++#################################++++++..
          ...+++++++#############################+++++++...
          ....+++++++++#######################+++++++++....
          ......+++++++++###################+++++++++......
          ........++++++++++#############++++++++++........
          ...........++++++++++#######++++++++++...........
          ................+++++++###+++++++................
```

Two points Euclidean cannot separate, from
`expected-output/05-mahalanobis-distance.txt`:

```
    probe            Euclidean   Mahalanobis
    ----------------------------------------
    (3.0, 3.0)        4.242641      1.114172
    (3.0, -3.0)       4.242641      6.000000
```

And the scaling result, from
`expected-output/06-scaling-changes-the-answer.txt`:

```
    part          distance       bore term       mass term   bore share
    -------------------------------------------------------------------
    R             2.000036        1.44e-04            4.00   0.003600%
    U            25.000001        3.60e-05          625.00   0.000006%
    P            40.000000        0.00e+00         1600.00   0.000000%
```

Everything in `expected-output/` was captured from real runs. `FIELDS.md` lists
what may legitimately differ on your machine and what must not.

## Validation steps

1. The install printed `2.5.2`.
2. `.venv/bin/pytest examples -q` prints `105 passed`.
3. `.venv/bin/pytest starter -q` prints `1 passed, 71 skipped` before you start
   and `72 passed` when you finish.
4. Each of the six reference scripts exits 0 and ends with
   `NN_name.py: every assertion held.`
5. `bash tests/run_tests.sh` prints `98 checks, 0 failure(s).` and exits 0.
   Check the exit status directly, not through a pipe:

   ```bash
   bash tests/run_tests.sh; echo "exit=$?"
   ```

6. Your own output matches `expected-output/`, allowing for the
   machine-dependent fields named in `FIELDS.md`.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints `N checks, M
failure(s)`, exits 0 only when `M` is 0, and reads **real values** rather than
reading source — every claim in this README is re-measured there.

Section 6 is the one worth reading. A green test suite proves nothing until you
have watched it go red, so the harness re-runs itself with one expectation
deliberately swapped for the naive belief that cosine distance satisfies the
triangle inequality, and asserts that the re-run names the failing check and
exits non-zero with exactly one failure. If section 6 passes, section 5 is not
decorative.

Section 7 also greps both copies of `measures.py` to confirm that neither
imports NumPy. That check is what makes agreement with
`numpy.linalg.norm(v, ord=p)` evidence rather than a tautology.

Every float comparison in the lab states a tolerance, `1e-12` unless a test
says otherwise and says why. The lab contains a worked demonstration of why:
the same Mahalanobis distance comes out as `6.0` through the hand-written
Gauss-Jordan inverse and `5.999999999999999` through `numpy.linalg.inv`.

## Cleanup

The lab writes nothing outside its own directory, and in fact writes nothing at
all — there is no output file, no cache and no temporary artefact. The harness
asserts that no data file exists anywhere under the lab.

```bash
find . -name '.venv' -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the virtual environment
git checkout -- starter/   # optional: resets your work
```

Note the `-name '.venv' -prune`. NumPy ships 113 `__pycache__` directories of
its own inside the virtual environment, and deleting them would break the
install.

## Troubleshooting

`troubleshooting.md` covers the failures people actually hit. The four shortest
answers:

- **`p_norm` returns `inf` at `p = math.inf`** — you computed the limit as
  arithmetic. `x ** math.inf` overflows; return the largest absolute component
  instead.
- **Every standardised value came out zero** — you standardised the query
  against itself. Compute means and standard deviations from the catalogue and
  pass them in.
- **`column_stds` is about 9 per cent off NumPy's** — you divided by `n - 1`.
  This lab uses the population divisor `n`, which is what `numpy.std` and
  scikit-learn's `StandardScaler` both use.
- **The ranking is upside down** — `higher_is_better` was left at its default
  for a similarity. Nothing crashes; the worst match simply arrives at the top.

## Security notes

`security.md` has the detail. In short: the lab needs the network exactly once,
to install two packages from PyPI. Nothing else opens a socket, reads a URL or
contacts a service — including the data, which is written out in
`catalogue.py` precisely so that it does not need to be fetched. Nothing needs
`sudo`, nothing needs a key, nothing binds a port, and nothing writes outside
the lab directory.

`security.md` also covers the security-shaped consequence of the day's actual
subject: a distance function is an access-control decision in disguise whenever
it is used for matching, and it inherits whatever the measure was told to
ignore.

## Extension exercises

1. **Draw the balls for fractional p.** `p_norm` refuses `p < 1`, and the
   reason is visible: relax the guard in a copy, render the "unit ball" for
   `p = 0.5` on the grid from script 02, and find the triple that breaks the
   triangle inequality on the star shape you get.
2. **Find your own Jaccard-against-cosine reversal.** Sweep query and candidate
   set sizes and count how often the two disagree. Then work out algebraically
   when it can happen — the condition is simpler than it looks.
3. **Poison a covariance.** Add rows to `SENSOR_READINGS` that lie across the
   grain, recompute the covariance, and watch the Mahalanobis distance of
   `(3, -3)` fall. How many injected rows does it take to make the anomaly look
   normal? That is the number a security review would want.
4. **Weight the features instead of standardising.** A diagonal weight matrix
   in the Mahalanobis formula is exactly a per-feature weighting. Set the
   weights by hand to encode "bore diameter matters ten times as much as mass",
   and compare the ranking with the standardised one.
5. **Measure the curse.** Day 103 raised it; make it concrete here. Generate
   random points in 2, 10, 100 and 1000 dimensions, and plot the ratio of the
   nearest to the farthest distance under L1, L2 and cosine. One of the three
   degrades much more slowly than the others, and the reason is the reason
   high-dimensional retrieval uses it.

## Navigation

- Previous: Day 106 — Eigenvalues and eigenvectors, intuitively
- Next: Day 108 — Derivatives: rates of change
- Section: `labs/sections/math-statistics-and-data/`
