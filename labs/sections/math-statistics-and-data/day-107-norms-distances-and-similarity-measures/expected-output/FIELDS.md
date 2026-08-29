# What in the captured output may legitimately differ on your machine

Every file in this directory was captured from a real run on the authoring
machine on 17 August 2026:

```
python   3.14.0
numpy    2.5.2
pytest   9.1.1
platform macOS-26.5.2-arm64-arm-64bit-Mach-O
```

Almost everything you see is arithmetic on small integers and will be identical
everywhere. This file names the parts that may not be, so you can tell a real
difference from a harmless one.

## Will differ, and does not matter

| Field | Where | Why |
| --- | --- | --- |
| `platform macOS-26.5.2-arm64-arm-64bit-Mach-O` | `test-run.txt`, section 1 | Your operating system, version and processor. |
| `python 3.14.0` | `test-run.txt`, section 1 | Whichever Python you installed the lab into. Anything from 3.11 up works; the type-hint syntax in `measures.py` needs 3.10 or later. |
| `... in 0.14s` | `reference-tests.txt`, `starter-progress.txt`, `test-run.txt` | Timing. Nothing in this lab asserts a duration. The whole suite is well under a second, because the largest dataset has eight rows and the largest sweep is 3375 triples of four-bit vectors. |

## Must NOT differ

These are exact arithmetic on small numbers. If one of them changes, something
real has changed, and the harness will say so rather than passing quietly.

| Value | Where |
| --- | --- |
| `98 checks, 0 failure(s).` | `test-run.txt`, last line |
| `105 passed` | `reference-tests.txt` |
| `1 passed, 71 skipped` | `starter-progress.txt` (an untouched checkout) |
| L1 picks Aisle, L2 picks Beacon, cosine picks Cartogram | `01-*.txt`, `test-run.txt` |
| The p-norm of (3, 4): 7 at p = 1, 5 at p = 2, 4 at p = infinity | `02-*.txt` |
| 469, 723 and 931 grid cells inside the three unit balls | `02-*.txt` |
| Cosine distance violating the triangle inequality on 326 of 3375 triples | `03-*.txt`, `test-run.txt` |
| Jaccard and Hamming satisfying it on all 4096 triples | `03-*.txt` |
| 14, 10 and 8 for the warehouse displacement | `04-*.txt` |
| Hamming 1, 3 and 6 on the parts register | `04-*.txt` |
| Jaccard 4/11 and 2/5; cosine 4/sqrt(44) and 2/sqrt(12) | `04-*.txt` |
| The covariance `[[7.5, 7.0], [7.0, 7.5]]` and its determinant 7.25 | `05-*.txt` |
| Eigenvalues 0.5 and 14.5 | `05-*.txt` |
| Mahalanobis 1.114172 along the grain and 6.0 across it | `05-*.txt` |
| The raw bearing order `R, U, P, S, T, V` and the standardised order `P, U, R, S, T, V` | `06-*.txt` |

## The three that are genuinely environment-dependent

**1. `6.0` against `5.999999999999999`.**

The Mahalanobis distance from the mean of the sensor readings to `(3, -3)` is
exactly 6 in real arithmetic. This lab computes it two ways:

- through `measures.inverse`, the Gauss-Jordan elimination written out in the
  lab, which gives **exactly `6.0`**;
- through `numpy.linalg.inv`, which calls LAPACK, and gives
  **`5.999999999999999`**.

Neither is wrong and neither is more accurate. They add the same numbers in a
different order, and IEEE 754 addition is not associative. This is asserted
both ways, with a tolerance of 1e-12, and it is the clearest single reason this
lab states a tolerance on every float comparison rather than writing `==`.

Which side each route lands on could differ on a machine with a different
LAPACK build, or one that evaluates intermediates at extended precision. If
your two values are swapped, or both are exactly 6.0, nothing is broken — the
claim the harness asserts is that both are within 1e-12 of 6, not that one of
them is bit-for-bit a particular string. If you see a difference larger than
that, something real is wrong.

**2. `the winner changed after standardising in 1090 of them  (54.5%)`.**

Section 6 of `06_scaling_changes_the_answer.py` runs 2000 random catalogues
from `numpy.random.default_rng(107)`. The seed is fixed, so the number is
reproducible on this machine — but NumPy does not promise that a generator's
exact stream survives a version change, and it says so in its own
documentation.

So the assertion in the code is a **range**: between 35 and 75 per cent. The
harness additionally checks the exact figure of 1090, which is the observed
value on numpy 2.5.2 and which will move if the stream ever changes. If that
one check fails and the range check passes, your NumPy draws different numbers
and the lab's argument is untouched. Record what you saw.

Everything asserted to the last decimal place elsewhere in this lab comes from
the literal tables in `catalogue.py`, not from the generator.

**3. The eigenvector signs.**

`numpy.linalg.eigh` returns the eigenvector for eigenvalue 0.5 as
`(-0.707107, +0.707107)` on this machine. `(+0.707107, -0.707107)` is the same
line pointing the other way and is an equally correct answer. Nothing in the
lab depends on the sign, because every component is squared before it is used,
and `05_mahalanobis_distance.py` says so in the output rather than leaving it
to be discovered.

## Reproducing the capture

```bash
cd labs/sections/math-statistics-and-data/day-107-norms-distances-and-similarity-measures
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
bash tests/run_tests.sh
```

Nothing in this directory was written by hand or edited after capture.
