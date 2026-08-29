# Dependencies for the Day 100 lab

Two packages, both free and open source, both installed from the Python
Package Index with `pip`, both running entirely on your own machine.

| Package | Pinned version | Why this lab needs it |
| --- | --- | --- |
| `numpy` | `2.5.2` | The array library the lesson is about. It supplies `ndarray`, `.shape`, `.reshape`, broadcasting, the `axis` argument, and `numpy.shares_memory`, which is the tool the view-versus-copy exercise turns on. |
| `pytest` | `9.1.1` | The test runner from Days 071–074. Nothing new here except what it is pointed at. |

Nothing else is required. Both suites and all five reference scripts run on
those two packages plus the standard library.

## Why numpy is pinned and pytest almost need not be

NumPy 2.0 changed how a lone array element prints — `np.int64(36)` rather than
the bare `36` NumPy 1.x produced — and the captured files in
`../expected-output/` would not match across that boundary if the scripts
printed raw array elements. They do not: every printed array goes through
`.tolist()` first. The pin is still there because the version is *checked*
rather than assumed. Section 1 of `tests/run_tests.sh` reads the installed
version and compares it against `requirements.txt`, so a mismatch is reported
at the top of the run instead of surfacing later as a confusing diff.

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

Exercise 1 — the from-scratch matrix class — needs nothing but the standard
library, and you can complete it on a bare `python3`. Everything after it
compares your class against NumPy, or demonstrates something (views,
broadcasting, `axis`) that only exists because NumPy exists. Those parts
cannot be faked, and the lab does not pretend otherwise.
