# Dependencies for the Day 106 lab

Two packages. Both free and open source, both installed from the Python Package
Index with `pip`, both running entirely on your own machine.

| Package | Pinned version | Why this lab needs it |
| --- | --- | --- |
| `numpy` | `2.5.2` | Holds the vectors and matrices, and supplies the independent answer every hand calculation is checked against: `numpy.linalg.eig`, `numpy.linalg.eigh`, `numpy.linalg.eigvals`, `numpy.linalg.eigvalsh`, `numpy.linalg.det`, `numpy.cov` and the seeded generator behind `numpy.random.default_rng`. |
| `pytest` | `9.1.1` | The test runner from Days 071–074. Nothing new here except what it is pointed at. |

That is the whole list. This lab needs no plotting library, no image library and
no machine-learning library, and that is deliberate — see below.

## Why the from-scratch code does not call NumPy's eigensolvers

`examples/eigen.py` and `starter/eigen.py` compute eigenvalues from the
characteristic equation with the school quadratic formula, find eigenvectors by
reading a row of `A - lambda*I`, and find the dominant eigenvector by repeated
multiplication. None of those functions calls `numpy.linalg.eig`.

If they did, checking them against `numpy.linalg.eig` would be checking NumPy
against itself, and would prove exactly nothing.

NumPy holds the **arrays** and does the **arithmetic** — dot products, norms,
matrix-vector products — because writing those by hand teaches nothing you did
not learn on Day 104. The **eigen-mathematics** is ours. That split is what
makes `examples/06_eig_against_eigh.py` mean something: two implementations
that share no eigen-code, agreeing on this lab's matrix to within 4.5e-11 on
the eigenvalue and to fifteen digits on the direction.

## Why `scikit-learn` is not here, even though this lab does PCA

Exercise 5 builds PCA from a covariance matrix and its eigenvectors in about
fifteen lines. `sklearn.decomposition.PCA` does the same job better — it uses a
singular value decomposition rather than an explicit covariance matrix, which
is more accurate on ill-conditioned data, and it hands you the centring, the
sorting, the variance ratios and a `transform` method for free.

**Use scikit-learn for real work.** The fifteen lines here exist so that when
you later call `PCA(n_components=50)` you know precisely what it did and why the
answer sometimes comes back with the sign flipped. Installing it would let you
run the tool without ever seeing the mechanism, which is the opposite of the
point.

`examples/06_eig_against_eigh.py` describes scikit-learn, SciPy and PyTorch from
their own documentation and reproduces **no output from any of them**, because
none of them is installed here.

## Why the versions are pinned

They are *checked* rather than assumed. Section 1 of `tests/run_tests.sh` reads
the installed versions and compares them against this file, so a mismatch is
reported at the top of the run rather than surfacing later as a confusing diff.

One place the version genuinely matters, and it is handled by measurement
rather than by trusting the pin:

**`numpy.linalg.eig` returns `complex128` on a real matrix with real
eigenvalues.** The docstring shipped with numpy 2.5.2 says the result "will be
of complex type, unless the imaginary part is zero in which case it will be
cast to a real type". On this version, on the authoring machine, the imaginary
part *is* zero and the cast does *not* happen — for `A`, for `numpy.eye(2)`,
and for every other real-eigenvalued matrix tried.

The lab measures that every run instead of asserting it from memory.
`test_numpy_eig_returns_complex_even_when_every_eigenvalue_is_real` will fail
loudly if a future version changes the behaviour, and that failure is the
**correct** outcome: it means the lesson text needs updating, not the test.

## Licences

NumPy is distributed under the BSD 3-Clause licence and pytest under the MIT
licence, each stated on that project's own documentation site. Both are
maintained in the open, cost nothing, and need no account, no key and no
signup — personally or commercially.

## One-time install

From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Expect `2.5.2`. Day 43 covered `python3 -m venv` in full; this is the same
pattern. The environment lives in `.venv/` inside the lab, is already excluded
from version control, and can be deleted at any time with `rm -rf .venv`.

## Network

Installing needs the network, once. **Nothing else in this lab does.**

In particular, the dataset is *generated in code*, not downloaded. A 400-point
cloud drawn from a seeded generator is reproducible on every machine, needs no
licence check, and cannot break on a train. `examples/dataset.py` builds it
from `numpy.random.default_rng(2106)` and every number in `expected-output/`
follows from that seed. Section 7 of `tests/run_tests.sh` greps every file under
`examples/` and `starter/` for the patterns that would indicate a socket being
opened.

## Running without a lab-local environment

If NumPy and pytest are already available in an environment you have activated,
the harness will find `pytest` on your `PATH`. You can also point it at a
specific binary:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The harness uses the `python3` that sits beside that `pytest`, because that is
the interpreter the packages are installed into. If NumPy is not importable
from it, the harness says so and stops rather than skipping checks quietly.

## What you would give up with an older NumPy

Very little, and the lab will tell you rather than guess.

`numpy.random.default_rng` needs NumPy 1.17 or later, `numpy.emath.sqrt` has
been there far longer, and every eigensolver used here is ancient by library
standards. Section 1 of the harness checks only that NumPy's major version is 2
or later.

What would change on an older version is the seeded cloud. `default_rng` is
guaranteed reproducible for a given NumPy generation, not across all of them,
so on NumPy 1.x the 400 points would differ and the PCA numbers in
`expected-output/05-pca-from-covariance.txt` would not match to the last digit.
The *claims* would still hold — the top component still lands within a fifth of
a degree of 30 — because the lab asserts tolerances around the construction
rather than the exact digits. `expected-output/FIELDS.md` says which is which.
