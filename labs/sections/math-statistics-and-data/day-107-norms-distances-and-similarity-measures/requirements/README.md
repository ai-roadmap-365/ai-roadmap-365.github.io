# Dependencies for the Day 107 lab

Two packages, both free and open source, both installed from the Python Package
Index with `pip`, both running entirely on your own machine.

| Package | Pinned version | Why this lab needs it |
| --- | --- | --- |
| `numpy` | `2.5.2` | The independent answer. `numpy.linalg.norm(v, ord=p)` IS the p-norm family this lab implements by hand, `numpy.cov` is the covariance matrix, `numpy.linalg.inv` is the inverse, and `numpy.linalg.eigh` supplies Day 106's eigenvectors. It also provides the seeded generator for the one randomised demonstration. |
| `pytest` | `9.1.1` | The test runner from Days 071–074. Nothing new here except what it is pointed at. |

## Why the from-scratch code deliberately does not use NumPy

`examples/measures.py` and `starter/measures.py` compute every norm, distance,
similarity, mean, standard deviation, covariance and matrix inverse with
`abs`, `**`, `sum`, `max` and `math.sqrt`. Nothing in either file imports
NumPy, and section 7 of `tests/run_tests.sh` greps both files to check that it
stays that way.

That is not stylistic. The lab's central evidence is that a hand-written
`p_norm` agrees with `numpy.linalg.norm(v, ord=p)` to within 1e-12 across six
values of `p`, and that a hand-written Gauss-Jordan inverse agrees with
`numpy.linalg.inv`. If the hand-written version were built out of NumPy calls,
both comparisons would be NumPy checking itself, and would prove nothing.

The one place the two genuinely disagree is preserved rather than smoothed
over: the Mahalanobis distance across the grain of the sensor data comes out as
exactly `6.0` through Gauss-Jordan and `5.999999999999999` through LAPACK.
`expected-output/FIELDS.md` explains it.

## Why the versions are pinned

They are *checked* rather than assumed. Section 1 of `tests/run_tests.sh` reads
the installed version of each package and compares it against this file, so a
mismatch is reported at the top of the run instead of surfacing later as a
confusing difference in output.

Two places the version could genuinely matter, both handled honestly rather
than pinned to a last digit:

1. **The seeded sweep.** `numpy.random.default_rng(107)` produces a
   reproducible stream on a given NumPy build, and NumPy's own documentation
   declines to guarantee that the stream survives a version change. So the code
   asserts a *range* — the ranking winner changes in between 35 and 75 per cent
   of 2000 random catalogues — while the harness additionally records the exact
   observed figure of 1090. If only the exact figure moves, nothing is broken.

2. **Last-bit floating point.** The `5.999999999999999` above came out of this
   LAPACK build. A different one could produce `6.0`, or
   `6.000000000000001`. The lab asserts that both routes land within 1e-12 of
   6, which is the claim that actually matters, and prints both values so a
   reader can see them rather than take the claim on trust.

The versions were read from the installed packages rather than guessed:

```bash
.venv/bin/python3 -c "from importlib.metadata import version; print(version('numpy'), version('pytest'))"
```

On the authoring machine, on 17 August 2026, that printed `2.5.2 9.1.1`.

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

Every dataset is written out as a literal table in `catalogue.py`: four term
counts, six categorical records, two ingredient lists, eight sensor readings
and six bearings. That was a deliberate choice. A lab that downloads a dataset
is a lab that breaks on a train, depends on a URL serving the same bytes next
year, and hides its own test data behind a fetch so a reader cannot see what is
in it without running the code. Section 7 of `tests/run_tests.sh` greps every
file under `examples/` and `starter/` for the patterns that would indicate a
socket being opened, and also asserts that no data file exists anywhere under
the lab.

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

## What you would give up without NumPy

Less than on most days, and it is worth being precise about which half.

All seventeen functions in exercise 1 need only the standard library, and so do
all twenty-five predictions in exercise 2. Every claim the day makes about
*which measure wins* — three winners on one query, Chebyshev accepting the part
L1 rejects, Jaccard and cosine disagreeing on the same two sets, Mahalanobis
separating two Euclidean-identical points, standardising changing the ranking —
is computed entirely in `measures.py` and would still run.

What you lose is the *corroboration*: `numpy.linalg.norm(v, ord=p)` confirming
the p-norm family, `numpy.cov` confirming the covariance, `numpy.linalg.inv`
confirming the inverse, `numpy.linalg.eigh` connecting Mahalanobis back to Day
106's eigenvectors, and the seeded 2000-catalogue sweep showing the scaling
effect is not a property of six hand-picked rows. Those are the checks that
make the lab's numbers evidence rather than assertion, and the lab does not
pretend they are optional.
