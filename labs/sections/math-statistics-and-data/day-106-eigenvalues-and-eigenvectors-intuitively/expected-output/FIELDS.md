# What in the captured output may legitimately differ on your machine

Every file in this directory was captured from a real run on the authoring
machine on 17 August 2026:

```
python   3.14.0
numpy    2.5.2
pytest   9.1.1
platform macOS-26.5.2-arm64-arm-64bit-Mach-O
```

Most of what you see is arithmetic and will be identical everywhere. This file
names the parts that will not be, so you can tell a real difference from a
harmless one.

## Will differ, and does not matter

| Field | Where | Why |
| --- | --- | --- |
| `platform macOS-26.5.2-arm64-arm-64bit-Mach-O` | `test-run.txt` and `06-eig-against-eigh.txt`, section 1 | Your operating system, version and processor. |
| `python 3.14.0` | same | Whichever Python you installed the lab into. Anything from 3.11 up will work; the `from __future__ import annotations` and `X | None` type hints need 3.7 and 3.10 respectively. |
| `... in 0.14s` | `reference-tests.txt`, `starter-progress.txt`, `test-run.txt` | Timing. Nothing in this lab asserts a duration; the whole suite is well under a second because the largest matrix is 400 by 400 and it is touched once. |
| The four timings in `06-*.txt` section 3 | `06-eig-against-eigh.txt` | `eig 64.79 ms`, `eigh 6.19 ms`, `eigvals 17.77 ms`, `eigvalsh 3.69 ms`, and the `10.46x` ratio derived from them. See below — these are **not** asserted anywhere. |

## Must NOT differ

If any of these changes, something real has changed and the harness will say
so rather than passing quietly.

| Value | Where |
| --- | --- |
| `110 checks, 0 failure(s).` | `test-run.txt`, last line |
| `94 passed` | `reference-tests.txt` |
| `1 passed, 52 skipped` | `starter-progress.txt` (an untouched checkout) |
| Eigenvalues of `A` being exactly 5 and 2 | every file |
| trace 7, determinant 10, discriminant 9 | `02-*.txt`, `test-run.txt` |
| `[45, 225]` as the only surviving directions of the 24-direction fan | `01-*.txt`, `test-run.txt` |
| The second eigen-line at `116.56505117707799` degrees | `01-*.txt`, `test-run.txt` |
| A shear having **one** eigen-line while `eig` returns **two** columns | `03-*.txt`, `test-run.txt` |
| A plane rotation's sweep verdict being `none` | `03-*.txt`, `test-run.txt` |
| The power method taking **25** iterations to 1e-10 | `04-*.txt`, `test-run.txt` |
| **962** iterations for the eigenvalue ratio 0.98 | `04-*.txt`, `test-run.txt` |
| The measured convergence ratio `0.399999` at step 14 | `04-*.txt`, `test-run.txt` |
| PCA recovering `30.101134` degrees, and `0.9999984422` abs-cosine | `05-*.txt`, `test-run.txt` |
| The uncentred answer being `136.583965` degrees wrong | `05-*.txt`, `test-run.txt` |

Those PCA digits are exact rather than approximate because the cloud comes from
`numpy.random.default_rng(2106)`, and NumPy guarantees that generator is
reproducible across platforms for a given NumPy generation. On **NumPy 1.x**
the draws would differ and these digits would not match — the *claims* would
still hold, because the tests assert tolerances around the construction (top
component within 0.2 degrees of 30, `sqrt` of the top eigenvalue within 0.2 of
3.0), not the digits. Section 1 of the harness checks that NumPy's major
version is 2 or later, so you will be told rather than left guessing.

## The three that are genuinely machine-dependent, and how each is handled

**1. `numpy.linalg.eig` returning `complex128` on a real matrix with two real
eigenvalues.**

This is the measurement that contradicts its own documentation. The docstring
shipped with numpy 2.5.2 says the result "will be of complex type, unless the
imaginary part is zero in which case it will be cast to a real type". On this
version, on this machine, the imaginary part **is** zero and the cast does
**not** happen — for `A`, for `numpy.eye(2)`, for `numpy.diag([1., 2., 3.])`
and for the integer matrix `[[2, 0], [0, 3]]`.

The lab records what it measured. If a future NumPy performs the cast, the test
`test_numpy_eig_returns_complex_even_when_every_eigenvalue_is_real` will go red,
and **that is the correct outcome**: it means this file and the lesson text need
updating, not that the test needs relaxing. Exercise 3d asks you to predict the
dtype from the documentation first, precisely so you feel the gap.

**2. The `eig` versus `eigh` timings on a 400 by 400 symmetric matrix.**

`64.79 ms` against `6.19 ms`, a ratio of `10.46x`, best of five runs each. That
number is real and it is **one machine on one day**. It depends on your BLAS and
LAPACK build, your core count, your thermal state and what else is running.

Nothing asserts it. `06_eig_against_eigh.py` prints it and says so in the text
beside it. What *is* asserted is the part that is not a timing: that the two
routines' 400 eigenvalues agree to within `1.990e-13`. Expect your own ratio to
differ, possibly by a lot; expect `eigh` to still win, because it is solving an
easier problem.

**3. The sign of every eigenvector, everywhere.**

The one to internalise. `numpy.linalg.eig` returns `[-0.447, 0.894]` for the
`lambda = 2` eigen-line of `A`, and the hand method in `eigen.py` returns
`[0.447, -0.894]`. Both are correct. `numpy.allclose` between them returns
`False`.

Which sign LAPACK hands back is a detail of the routine's internal
normalisation, not a fact about the matrix, and it can differ between LAPACK
builds and between NumPy versions. **If a sign in your output is flipped
relative to a file here, nothing is wrong.** That is why every comparison in
this lab goes through `abs_cosine` and why the captured output prints the
absolute cosine beside the components rather than instead of them.

The same applies to the PCA result: the top component comes back as
`[-0.865, -0.502]` against a true direction of `[0.866, 0.500]`, pointing the
opposite way along the identical line, with an absolute cosine of
`0.9999984422`. `test_the_returned_top_component_points_the_other_way_along_that_line`
asserts the flip on this machine, and if your build flips it the other way that
one test is the honest place for the difference to surface.

## Reproducing the capture

```bash
cd labs/sections/math-statistics-and-data/day-106-eigenvalues-and-eigenvectors-intuitively
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
bash tests/run_tests.sh
```

Nothing in this directory was written by hand or edited after capture.
