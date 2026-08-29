# Dependencies for the Day 102 lab

Two packages, both free and open source, both installed from the Python
Package Index with `pip`, both running entirely on your own machine.

| Package | Pinned version | Why this lab needs it |
| --- | --- | --- |
| `numpy` | `2.5.2` | The library your from-scratch transformations are checked against: the `@` operator for matrix products, `numpy.linalg.det`, `numpy.linalg.inv`, `numpy.linalg.matrix_rank`, and the `LinAlgError` a singular matrix raises. |
| `pytest` | `9.1.1` | The test runner from Days 071–074. Nothing new here except what it is pointed at. |

Nothing else is required. Both suites and all six reference scripts run on
those two packages plus the standard library — and the from-scratch module
itself imports nothing but `math`.

## Why the from-scratch code deliberately does not use NumPy

`examples/transforms.py` and `starter/transforms.py` are written with plain
lists and tuples on purpose. If your `rotation` function returned a NumPy array
built by a NumPy helper, then checking it against NumPy would be checking NumPy
against itself. Writing the arithmetic yourself and *then* having a mature
library agree with you is worth more than either half alone.

## Why numpy is pinned

The version is *checked* rather than assumed. Section 1 of `tests/run_tests.sh`
reads the installed version and compares it against `requirements.txt`, so a
mismatch is reported at the top of the run instead of surfacing later as a
confusing diff.

There is one place where the version could matter. `numpy.linalg.det` on the
matrix `[[3, -1], [1, 2]]` returns `7.000000000000001` on this machine with
this version — one bit away from the exact 7 the direct formula gives. That is
a property of the factorisation it uses and of the underlying linear algebra
library, and it is not guaranteed to be identical everywhere. The lab handles
this honestly: it asserts that NumPy's answer is *within 1e-14 of 7* and that
the from-scratch answer is *exactly 7*, rather than pinning NumPy's last digit.

The version was read from the installed package rather than guessed:

```bash
.venv/bin/python3 -c "from importlib.metadata import version; print(version('numpy'))"
```

On the authoring machine, on 16 August 2026, that printed `2.5.2`.

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

Installing needs the network, once. **Nothing else in this lab does.** No
script opens a socket, reads a URL or contacts a service, and section 7 of
`tests/run_tests.sh` greps every file under `examples/` and `starter/` for the
patterns that would indicate otherwise.

## Running without a lab-local environment

If NumPy and pytest are already available in an environment you have activated,
the harness will find `pytest` on your `PATH`. You can also point it at a
specific binary:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The harness uses the `python3` that sits beside that `pytest`, because that is
the interpreter NumPy is installed into. If NumPy is not importable from it,
the harness says so and stops rather than skipping checks quietly.

## What you would give up without NumPy

More than you might expect, and less than you might fear. Exercise 1 — writing
all ten transformation functions — needs nothing but `math` from the standard
library, and you can complete the whole of it on a bare `python3`. What you
lose is every cross-check: the tests that confirm your `compose` matches `@`,
your `inverse` matches `numpy.linalg.inv`, and your `rank` matches
`numpy.linalg.matrix_rank`, plus the exercise on the exception a singular
matrix raises. Those parts cannot be faked and the lab does not pretend
otherwise.
