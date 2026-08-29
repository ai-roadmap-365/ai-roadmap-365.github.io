# Dependencies for the Day 103 lab

Two packages, both free and open source, both installed from the Python
Package Index with `pip`, both running entirely on your own machine.

| Package | Pinned version | Why this lab needs it |
| --- | --- | --- |
| `numpy` | `2.5.2` | Two jobs. It is the independent check that your from-scratch dot product and cosine similarity are right — `numpy.dot` and `numpy.linalg.norm` computed the same values by a different route. And it supplies `numpy.random.default_rng`, the seeded generator that makes the curse-of-dimensionality measurement reproducible. |
| `pytest` | `9.1.1` | The test runner from Days 071–074. Nothing new here except what it is pointed at. |

Nothing else is required. Both suites and all seven reference scripts run on
those two packages plus the standard library. The functions you write in
`starter/similarity.py` use nothing but `math`.

## Why numpy is pinned

Two reasons, and only the second is about correctness.

The measurement in `examples/07_curse_of_dimensionality.py` draws random
numbers. It is seeded with `numpy.random.default_rng(103)`, and NumPy
guarantees that a given generator with a given seed produces the same stream —
a guarantee that holds within a major version and is not promised across one.
The captured numbers in `../expected-output/07-curse-of-dimensionality.txt`
therefore belong to numpy 2.5.2 specifically. On a different version the
*shape* of the result will be identical (mean absolute cosine falling towards
zero as the dimension grows, tracking the exact formula) and individual digits
may move.

The second reason is that the version is *checked* rather than assumed.
Section 1 of `tests/run_tests.sh` reads the installed version and compares it
against `requirements.txt`, so a mismatch is reported at the top of the run
instead of surfacing later as a confusing diff.

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

If you are offline and already have NumPy available somewhere, you do not need
the install at all — see the next section.

## Running without a lab-local environment

If NumPy and pytest are already available in an environment you have
activated, the harness will find `pytest` on your `PATH`. You can also point it
at a specific binary:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The harness uses the `python3` that sits beside that `pytest`, because that is
the interpreter NumPy is installed into. If NumPy is not importable from it,
the harness says so and stops rather than skipping checks quietly.

## What you would give up without NumPy

Exercise 1 — the seven functions in `starter/similarity.py` — needs nothing but
the standard library, and you can complete every one of them on a bare
`python3`. What you lose is the checking: the tests compare your answers
against `numpy.dot` and `numpy.linalg.norm`, and "my implementation agrees with
an independent one" is a much stronger statement than "my implementation
returns a number". You would also lose the dimensionality measurement in
section 7, which needs to draw and compare thousands of high-dimensional
vectors quickly. A pure-Python version of that runs, but it takes long enough
to be annoying, which is itself a fair demonstration of why NumPy exists.

## A package this lab describes but does NOT install

`scipy.spatial.distance` provides `cosine`, `euclidean` and about twenty other
distance functions, and it is the tool you would reach for in real work rather
than writing your own. It is **not** in `requirements.txt` and it was **not**
run here, so this lab reproduces no output from it and makes no claim about
its numbers. The lesson describes it from its own documentation and says
plainly that nothing was executed. SciPy is BSD-licensed and free, and
installing it is one line if you want to compare — but then the comparison is
yours, not this lab's.
