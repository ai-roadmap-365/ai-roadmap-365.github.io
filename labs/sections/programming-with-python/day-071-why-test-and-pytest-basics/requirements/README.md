# Dependencies — Day 071 lab

This is the first lab in the course with a `requirements.txt`. Everything from
Day 43 to Day 70 ran on the standard library alone. Week 11 is *about* tools,
so this week the tools are the point.

## What is pinned

```text
pytest==9.1.1
```

One package, one exact version.

| Package | Version | Licence | What it is | Why this lab needs it |
| --- | --- | --- | --- | --- |
| pytest | 9.1.1 | MIT | A test runner: it finds your tests, runs them, and reports what failed | The whole lab is about reading its output and trusting its exit code |

The licence is not taken on trust. After installing, ask the package itself:

```bash
.venv/bin/pip show pytest
```

On the authoring machine that reports `Version: 9.1.1`,
`License-Expression: MIT`, and
`Requires: iniconfig, packaging, pluggy, pygments`.

The version is exact — `==`, not `>=`. A pinned version is why the captured
output in `expected-output/` matches what you see. Test-tool output changes
between releases, and a lab that says "you will see 19 passed" has to name the
version that says it.

## Why nothing else

Installing pytest also pulls in four small libraries it depends on —
`iniconfig` (reading `pytest.ini`), `packaging` (version comparisons),
`pluggy` (the plugin system) and `pygments` (syntax colouring in reports).
That is the whole tree; there is no framework underneath. Everything else this
lab uses — `unittest`, `doctest`, `re`, `math` — ships with Python.
The two standard-library runners are demonstrated deliberately: if you ever
land somewhere you cannot install a package, you can still write and run tests
that day.

## Free and open source

pytest is free and open source under the MIT licence, with no paid tier, no
account, and no telemetry. Installing it downloads from the Python Package
Index. That download is the only moment in this lab that touches the network;
once installed, every command runs fully offline.

## The one-time install

You met `python3 -m venv` on Day 43. Same idea, one directory per lab, so this
lab's pytest cannot collide with anything else on your machine:

```bash
cd labs/sections/programming-with-python/day-071-why-test-and-pytest-basics
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
```

The last command should print `pytest 9.1.1`.

`.venv/` is ignored by version control repository-wide. Never commit it: it is
a build artifact, it is large, and it is specific to your machine and Python
version.

## Running without a lab-local virtual environment

If you already have pytest 9.x somewhere — a system install, a shared
environment, an activated venv — you do not need a second copy. The test
runner resolves the tool in three steps: an explicit override, then this lab's
`.venv/bin/pytest`, then whatever `pytest` is on `PATH`. So both of these work:

```bash
bash tests/run_tests.sh                         # uses .venv or PATH
PYTEST=/path/to/pytest bash tests/run_tests.sh  # uses exactly what you name
```

If none of the three finds a pytest, the runner stops with the install
instructions rather than quietly reporting success on nothing — a test suite
that skips itself and exits 0 is the exact failure this lab teaches you to
distrust.

## Checking your Python

```bash
python3 --version
```

pytest 9.1.1 needs Python 3.9 or newer; this lab was authored and executed on
Python 3.14.0. Windows users: run everything inside WSL, or substitute
`.venv\Scripts\pytest` for `.venv/bin/pytest` and use `python` for `python3`.

## What Week 11 adds later

Day 075 adds `mypy` to this file and Day 076 adds `ruff`, so by Day 077 the
pinned set is three lines. All three are free and open source. Nothing else
gets added: a testing setup that needs a page of dependencies is a testing
setup nobody will run.
