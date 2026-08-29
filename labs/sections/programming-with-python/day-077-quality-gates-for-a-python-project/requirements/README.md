# Dependencies — Day 077 lab

Five packages, one for each stage of the gate plus one convenience. All are
free and open source, all install with `pip`, and none needs an account, an
API key, or a paid plan. After the one-time install everything in this lab
runs completely offline.

```
pytest==9.1.1
mypy==2.3.0
ruff==0.15.22
coverage==7.15.2
pytest-cov==7.1.0
```

| Package | Stage it powers | What it does | Licence |
| --- | --- | --- | --- |
| `ruff` | 1 (format) and 2 (lint) | One binary doing both jobs: `ruff format --check .` reports layout deviations without rewriting anything, `ruff check .` reports rule violations such as an unused import (`F401`). Introduced on Day 76. | MIT, per the Ruff documentation |
| `mypy` | 3 (types) | Reads the annotations Day 69 taught you to write and proves the claims they make, which Python never checks at runtime. Introduced on Day 75. | MIT, per the mypy documentation |
| `pytest` | 4 (tests) | Runs the suite built across Days 71 to 74. | MIT, per the pytest documentation |
| `coverage` | 4 and 5 (measurement and floor) | `coverage run -m pytest` records which lines and branches executed; `coverage report` prints the table and exits non-zero when the total is under `fail_under`. | Apache-2.0, per the package metadata |
| `pytest-cov` | optional | A pytest plugin that wires coverage into pytest itself, so `pytest --cov=pricekit` does in one command what `coverage run` plus `coverage report` does in two. The gate uses the two-command form; this package is here so you can compare them. | MIT, per the package metadata |

## Why the versions are pinned exactly

A gate whose tools can change underneath it is not a gate. If `requirements.txt`
said `ruff` rather than `ruff==0.15.22`, then a release that adds a new lint
rule would turn every open change red overnight, on a morning nobody chose.
With an exact pin, upgrading a tool is a one-line commit that somebody reviews
and that has its own green run — which is how it should be.

The versions above were installed and verified on the authoring machine on
2026-07-19. `coverage` reported itself as
`Coverage.py, version 7.15.2 with C extension`.

## One-time install

```bash
cd labs/sections/programming-with-python/day-077-quality-gates-for-a-python-project
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
.venv/bin/coverage --version
```

You created a virtual environment for the first time on Day 43; this is the
same procedure. `.venv/` is ignored by version control and never committed —
it is a build product of `requirements.txt`, which is the file that matters.

Both `check.sh` scripts find these tools automatically: they look for an
explicit override first (`RUFF=/path/to/ruff bash check.sh`), then this lab's
`.venv/bin/`, then whatever is on your `PATH`. If none of those finds a tool
the script stops with instructions rather than skipping the stage — a gate
that silently does nothing is more dangerous than no gate at all, because
people trust it.

## Deliberately not installed

- **pre-commit** — a free, open-source hook manager. A reference configuration
  ships in `examples/ci-reference/pre-commit-config.yaml`, but installing it
  writes a hook into a repository's `.git` directory, which a lab has no
  business doing to yours.
- **tox** and **nox** — free, open-source multi-environment runners. Discussed
  in the lesson's Alternatives section; both need several Python versions
  installed to be worth running.

## Windows

Run everything inside WSL and follow the Linux path. The `.venv` layout
differs on native Windows (`.venv\Scripts\` rather than `.venv/bin/`), and
`check.sh` is a bash script, so WSL is the supported route.
