# Requirements for the Day 076 lab

Two dependencies, both free and open source, both pinned to an exact
version so that your output matches the captures in `expected-output/`.

| Package | Pinned version | Why this lab needs it |
| --- | --- | --- |
| `ruff` | `0.15.22` | The subject of the lesson: a linter and a formatter in one binary. Provides `ruff check`, `ruff format` and `ruff rule`. |
| `pytest` | `9.1.1` | The evidence. The whole argument of this lab is that the tools change how code reads without changing what it does, and a green test suite before and after is how you prove that. Introduced on Day 71. |

Both projects are distributed under the MIT licence. Ruff is developed by
Astral; its documentation is at `https://docs.astral.sh/ruff/`. pytest is
developed by the pytest project; its documentation is at
`https://docs.pytest.org/en/stable/`. Neither asks for an account, a
licence key, or a paid tier to do anything in this lab.

## One-time install

From the lab directory:

```bash
cd labs/sections/programming-with-python/day-076-linting-and-formatting-with-ruff
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/ruff --version
.venv/bin/pytest --version
```

You should see `ruff 0.15.22` and `pytest 9.1.1`.

`python3 -m venv` is the tool from Day 43. `.venv/` is ignored by this
repository's `.gitignore` and must never be committed.

## Network

Installing needs the network, once. After that the lab runs entirely
offline: neither Ruff nor pytest contacts anything, and `ruff rule <code>`
prints rule documentation that is compiled into the binary rather than
fetched.

## If you would rather not create a virtual environment

The test suite resolves its tools in this order: an explicit environment
variable, then `.venv/bin/` inside this lab, then whatever is on your
`PATH`. So if you already have Ruff and pytest installed somewhere, either
of these works:

```bash
bash tests/run_tests.sh                                   # uses PATH
RUFF=/path/to/ruff PYTEST=/path/to/pytest bash tests/run_tests.sh
```

If neither is found the suite stops with an install message rather than
quietly reporting success on checks it never ran.

## Caches

Ruff writes a `.ruff_cache/` directory next to the files it checks, and
pytest can write `__pycache__/` and `.pytest_cache/`. All three are ignored
by this repository. The `## Cleanup` section of the lab README removes
them.
