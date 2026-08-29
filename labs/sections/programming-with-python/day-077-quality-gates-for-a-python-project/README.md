# Day 077 lab — One Command, Every Gate

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Quality Gates for a Python Project
- **Day number:** 77 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-077-quality-gates-for-a-python-project
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-077-quality-gates-for-a-python-project` when the site is running.
<!-- generated-links:end -->

## Purpose

Week 11 handed you five separate tools. Day 71 gave you pytest, Day 72 fixtures
and parametrization, Day 73 the discipline of writing the failing test first,
Day 74 mocking at the boundaries, Day 75 mypy, Day 76 Ruff. Each of them is a
command you can type. None of them is a gate.

A **quality gate** is one command that runs all of them and returns one exit
code meaning "this change is safe to merge". In this lab you build that command
— `check.sh` — stage by stage on a small pricing library, configure all five
stages in a single `pyproject.toml`, and then do the thing that most projects
never do: **prove the gate can actually fail**.

That proof is the heart of the lab. It is trivially easy to write a `check.sh`
that prints five green lines and exits 0 no matter what the code does, and such
a script is worse than having nothing, because everyone downstream believes it.
So the test suite takes a temporary copy of the finished project, introduces
one defect, and asserts the gate goes red — five times, once per stage: a
formatting violation, an unused import, a wrong type annotation, a broken
implementation, and a drop in coverage.

You also prove, mechanically, the most abused claim in the industry. A test
file in `examples/coverage-demo/` contains **zero assert statements**, calls a
function that is genuinely wrong, and produces a coverage report reading
**100%**. Coverage measures which lines executed. It has never measured whether
anything was checked.

Finally, the lab ships two files it does **not** run: a complete continuous
integration workflow and a pre-commit configuration. Both are shipped as
documented references, because running them needs a hosting service or a write
into your `.git` directory, and a lab that claimed output it never produced
would be teaching the opposite of what a gate is for.

## Learning objectives

- Assemble the week's separate tools into one command that runs identically on
  a laptop and on a build server and returns a single meaningful exit code.
- Order the stages by cost — format, lint, types, tests, coverage — and explain
  why the cheapest feedback must arrive first.
- Choose between fail-fast and report-everything, and say which context wants
  which.
- Configure pytest, mypy, Ruff and coverage.py entirely in one `pyproject.toml`,
  and explain what one configuration file buys over five dotfiles.
- Run `coverage.py` and `pytest-cov`, read a real branch-coverage report, and
  use the `Missing` column as a worklist.
- Demonstrate that 100% coverage proves execution and not verification, and use
  a coverage floor as a ratchet rather than a target.
- Prove a gate has teeth by breaking one thing at a time and watching exactly
  one stage go red.
- Read a complete continuous-integration workflow line by line: clean checkout,
  pinned interpreter, pinned dependencies, the one gate command, the build
  matrix, and the artifacts it keeps.
- Explain what each stage cannot prove, and why branch protection rather than a
  workflow file is what actually blocks a bad merge.

## Prerequisites

- The Day 77 lesson (read it first).
- Day 76: Ruff — `ruff format`, `ruff check`, and rule codes such as `F401`.
- Day 75: mypy and the difference between an annotation and a checked claim.
- Days 71–74: pytest, fixtures and parametrization, test-first development,
  and mocking at boundaries.
- Day 69: type hints and dataclasses; Day 70: value objects and invariants —
  the `pricekit` package under test is built from both.
- Day 43: `python3 -m venv` and installing into a virtual environment.
- A terminal, a text editor, and one network connection for the install.

## Supported operating systems

- **macOS** — fully supported (captures taken on macOS 26.5.1, Apple Silicon,
  Python 3.14.0, bash 3.2.57).
- **Linux** — fully supported (any distribution with Python 3.10+ and bash).
- **Windows** — use WSL and follow the Linux path. `check.sh` and
  `tests/run_tests.sh` are bash scripts, and a virtual environment on native
  Windows puts its executables in `.venv\Scripts\` rather than `.venv/bin/`.

## Hardware requirements

Any computer that runs Python 3.10 or newer. The library is under 150 lines,
the suite is 42 tests, and a full gate run finishes in well under a second on
the authoring machine. No GPU, no special memory, no disk of consequence.
Network access is needed once, for the install.

## Required software

- `python3` (3.10 or newer; captures taken on 3.14.0).
- `bash` for `check.sh` and the test runner (preinstalled on macOS and Linux).
- Five pinned packages — `ruff`, `mypy`, `pytest`, `coverage`, `pytest-cov` —
  listed with their exact versions and their reasons in
  [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Every tool in this lab is free and open source, and the whole gate runs on your
own machine at no cost. `ruff`, `mypy`, `pytest` and `pytest-cov` are MIT
licensed and `coverage` is Apache-2.0, each per its own project documentation
or package metadata.

The lesson's Alternatives section covers the wider field honestly: a plain
shell script or `Makefile` costs nothing and needs no dependencies at all and
is genuinely enough for many projects; `pre-commit`, `tox` and `nox` are free
and open source; hosted CI is free for public repositories and metered for
private ones; and hosted quality dashboards such as SonarQube/SonarCloud and
Codecov have free or open-source tiers alongside paid plans. None of the paid
options is needed here or anywhere in this course.

## Installation

```bash
cd labs/sections/programming-with-python/day-077-quality-gates-for-a-python-project
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
.venv/bin/coverage --version
```

The install needs the network once. Everything after it runs offline. `.venv/`
is ignored by version control and is never committed — it is a build product of
`requirements.txt`, which is the file that matters.

If you would rather not create a virtual environment here, point the scripts at
tools you already have:

```bash
RUFF=/path/to/ruff MYPY=/path/to/mypy COVERAGE=/path/to/coverage \
  PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## File structure

```text
day-077-quality-gates-for-a-python-project/
├── README.md                          ← you are here
├── metadata.yml
├── examples/                          ← the finished gate
│   ├── check.sh                       ← THE artefact: one command, five stages
│   ├── pyproject.toml                 ← one config file for all four tools
│   ├── pricekit/
│   │   ├── __init__.py
│   │   ├── money.py                   ← whole-cent Money value object
│   │   └── receipt.py                 ← pure receipt arithmetic
│   ├── tests/
│   │   ├── test_money.py              ← 22 tests
│   │   └── test_receipt.py            ← 20 tests
│   ├── coverage-demo/
│   │   ├── promo.py                   ← four lines, one real bug
│   │   ├── test_promo_no_assertions.py    ← 100% coverage, zero assertions
│   │   ├── test_promo_with_assertions.py  ← the same tests, one assertion each
│   │   └── test_executes_everything.py    ← the realistic version, on pricekit
│   └── ci-reference/
│       ├── quality-gate.yml           ← full CI workflow — REFERENCE, not run here
│       └── pre-commit-config.yaml     ← pre-commit hooks — REFERENCE, not run here
├── starter/                           ← YOUR work
│   ├── check.sh                       ← a gate with no stages (exercises 1–5)
│   ├── pyproject.toml                 ← skeleton config (exercises 1b–5b)
│   ├── pricekit/                      ← the same library, complete
│   └── tests/
│       └── test_money.py              ← deliberately incomplete: no receipt tests
├── tests/
│   ├── run_tests.sh                   ← 39 checks; proves the gate has teeth
│   └── fixtures/
│       └── untested_addition.py       ← the code injected to drop coverage
├── expected-output/
│   ├── gate-pass.txt
│   ├── gate-failures.txt              ← five defects, five red gates
│   ├── coverage-reports.txt
│   ├── starter-progress.txt
│   ├── test-run.txt
│   └── FIELDS.md
├── requirements/
│   ├── requirements.txt               ← five exact pins
│   └── README.md
├── troubleshooting.md
└── security.md
```

## How to run

From this directory, after the install:

```bash
# 1. Run the finished gate. One command, five stages, one exit code.
cd examples
bash check.sh
echo "exit code: $?"

# 2. Watch the gate go red. Break one thing, run it again, put it back.
#    (This edits examples/ — the last command undoes it.)
python3 - <<'PY'
from pathlib import Path
p = Path('pricekit/money.py')
p.write_text(p.read_text().replace(
    'from dataclasses import dataclass',
    'from dataclasses import dataclass\nimport os',
))
PY
bash check.sh
git checkout -- pricekit/money.py

# 3. Compare the two modes on the same broken code.
bash check.sh --fail-fast

# 4. Read a coverage report properly.
coverage run -m pytest
coverage report
pytest --cov=pricekit --cov-branch --cov-report=term-missing

# 5. The demonstration that matters: 100% coverage, zero assertions,
#    one real bug.
cd coverage-demo
grep -cE '^[[:space:]]*assert ' test_promo_no_assertions.py
coverage run --branch --source=promo -m pytest test_promo_no_assertions.py -q
coverage report --show-missing --fail-under=0
pytest test_promo_with_assertions.py -q
cd ..

# 6. Read the two reference files. Neither is executed by this lab.
cat ci-reference/quality-gate.yml
cat ci-reference/pre-commit-config.yaml
cd ..

# 7. Your task: build the gate yourself, one stage at a time.
cd starter
bash check.sh          # a gate with no stages says yes to everything
# ... complete exercises 1-5 in check.sh and 1b-5b in pyproject.toml ...
cd ..

# 8. Check your work.
bash tests/run_tests.sh
```

Every command above uses the tools from `.venv/bin/` automatically if you
created one; otherwise prefix them, e.g. `.venv/bin/coverage report`.

## What the commands do

- `bash check.sh` — runs all five stages in cost order (format, lint, types,
  tests, coverage), prints `PASS:` or `FAIL:` for each, and exits 0 only if
  every stage passed. The tests stage runs pytest under `coverage run`, so the
  coverage stage costs nothing extra. Read the script: the tool resolution and
  the stage runner together are about forty lines, and that is the entire
  machinery.
- The `python3 - <<'PY'` block then `bash check.sh` — inserts a single unused
  `import os` into `pricekit/money.py` and shows the lint stage catching it
  with `F401` (and `I001`, because the import block is now out of order), while
  the other four stages stay green. `git checkout --` puts the file back. Note
  where the import goes: appended to the *end* of a file it would trip the
  formatter as well, and the point of this demonstration is one defect, one red
  stage.
- `bash check.sh --fail-fast` — the same gate, stopping at the first red stage.
  On broken code the difference is visible immediately: the later stage headers
  never print. Use fail-fast when you are iterating locally; use the default
  report-everything mode in CI, where one run should tell you everything that
  is wrong rather than making you fix and re-queue five times.
- `coverage run -m pytest` then `coverage report` — the two-command form.
  `run` records which lines and branches executed; `report` prints the table
  and exits non-zero when the total is below `fail_under`. Both read their
  settings from `[tool.coverage.*]` in `pyproject.toml`.
- `pytest --cov=pricekit --cov-branch --cov-report=term-missing` — the same
  measurement through the pytest-cov plugin, in one command instead of two. It
  also prints the floor verdict as a sentence: `Required test coverage of 95.0%
  reached. Total coverage: 100.00%`.
- The `coverage-demo` block — the sharpest fifteen seconds in the lab. The
  `grep` proves the test file has no assertions. The coverage report says 100%.
  Then `pytest test_promo_with_assertions.py` adds one assertion per test and
  the suite fails with `assert 100 == 900`, because `promo_price` charges
  members 10% of the price instead of taking 10% off it. Coverage never moved.
- `cat ci-reference/quality-gate.yml` — a complete, commented workflow: when it
  triggers, the clean throwaway machine it runs on, the pinned Python matrix,
  the pinned dependency install, the single `bash check.sh` line, and the
  artifacts it keeps. **It is not executed by this lab** and no run of it is
  claimed anywhere here; running it requires a hosting service, and this lab
  runs offline on your machine.
- `cat ci-reference/pre-commit-config.yaml` — a hook configuration holding only
  fast checks, with the test suite deliberately absent and the reason written
  out. Also a reference, not executed here.
- `bash tests/run_tests.sh` — 39 checks. Eight on the clean reference gate,
  five defect checks proving each stage can fail, two on fail-fast versus
  report-everything, three on the coverage demonstration, seven on the shipped
  reference files and the single-config-file claim, and the rest on the
  starter.

## Expected output

The clean gate, in full — a real captured run (see
[`expected-output/gate-pass.txt`](expected-output/gate-pass.txt)):

```text
$ bash check.sh
=== format ===
5 files already formatted
PASS: format

=== lint ===
All checks passed!
PASS: lint

=== types ===
Success: no issues found in 3 source files
PASS: types

=== tests ===
..........................................                               [100%]
42 passed in 0.02s
PASS: tests

=== coverage ===
Name                   Stmts   Miss Branch BrPart  Cover   Missing
------------------------------------------------------------------
pricekit/__init__.py       3      0      0      0   100%
pricekit/money.py         28      0     12      0   100%
pricekit/receipt.py       35      0     14      0   100%
------------------------------------------------------------------
TOTAL                     66      0     26      0   100%
PASS: coverage

=== gate PASSED ===
all 5 stages green — this change is safe to merge
exit: 0
```

And the demonstration the lesson is really about
([`expected-output/coverage-reports.txt`](expected-output/coverage-reports.txt)):

```text
$ grep -cE '^[[:space:]]*assert ' test_promo_no_assertions.py
0

$ coverage run --branch --source=promo -m pytest test_promo_no_assertions.py -q
..                                                                       [100%]

$ coverage report --show-missing --fail-under=0
Name       Stmts   Miss Branch BrPart  Cover   Missing
------------------------------------------------------
promo.py       4      0      2      0   100%
------------------------------------------------------
TOTAL          4      0      2      0   100%

$ pytest test_promo_with_assertions.py -q
F.                                                                       [100%]
>       assert promo_price(1000, True) == 900
E       assert 100 == 900
```

[`expected-output/gate-failures.txt`](expected-output/gate-failures.txt) holds
the five defect runs in full — the evidence that each stage is wired in.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) states the required
behaviour of the gate, the coverage demonstration and the starter on every
platform.

## Validation steps

1. `bash check.sh` in `examples/` prints five `PASS:` lines and `gate PASSED`,
   and `echo $?` shows `0`.
2. `coverage report` in `examples/` shows `TOTAL 66 0 26 0 100%`.
3. Inserting `import os` into the import block of `pricekit/money.py` makes the
   gate fail at the **lint** stage only, with `F401` and `I001`, and exit 1.
   Undo it with `git checkout -- pricekit/money.py`.
4. `bash check.sh --fail-fast` on that same broken file never prints
   `=== types ===`; the default mode does.
5. `grep -cE '^[[:space:]]*assert ' examples/coverage-demo/test_promo_no_assertions.py`
   prints `0`, and the coverage report for `promo.py` still reads `100%`.
6. `pytest examples/coverage-demo/test_promo_with_assertions.py -q` fails with
   `assert 100 == 900` — the bug 100% coverage did not notice.
7. In `starter/`, `bash check.sh` as shipped prints
   `gate PASSED (with no stages)`. After exercise 5 it fails on coverage at
   55% until you write tests for `pricekit/receipt.py`.
8. `examples/` contains no `.flake8`, `setup.cfg`, `mypy.ini`, `pytest.ini`,
   `.isort.cfg` or `.coveragerc` — every tool reads `pyproject.toml`. The test
   suite checks this too.
9. `bash tests/run_tests.sh` ends with `39 checks, 0 failure(s).` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `39 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure.

Read the suite before you run it. Two blocks explain the whole lab. The first
is `expect_gate_fails`, which copies the reference project into a temporary
directory, applies one defect, and asserts both that the gate exited non-zero
**and** that the named stage is the one that complained — asserting only the
exit code would pass even if the wrong stage failed for the wrong reason. The
second is the coverage block, which asserts mechanically that a file with zero
`assert` statements produces `promo.py 4 0 2 0 100%`, and that adding one
assertion turns the same tests red.

A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

```bash
rm -f examples/.coverage examples/coverage-demo/.coverage starter/.coverage
rm -rf examples/.mypy_cache examples/.ruff_cache examples/.pytest_cache
rm -rf starter/.mypy_cache starter/.ruff_cache starter/.pytest_cache
```

To reset your work: `git checkout -- starter/`. To remove the tools as well:
`rm -rf .venv`. The test runner makes its own temporary directories with
`mktemp -d` and removes each one as that check finishes, so a completed run
leaves nothing behind.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md). The ones you are most likely to
meet: `FAIL: ruff not found`, which means the install has not run and the gate
is refusing to skip a stage silently; `ModuleNotFoundError: No module named
'pricekit'`, which means `pythonpath = ["."]` is missing from
`[tool.pytest.ini_options]`; a format stage that flags files you never touched,
which is a missing `line-length` setting; a coverage stage stuck at 55% in the
starter, which is the floor doing its job; and the two entries worth reading
even if nothing is broken — what to do about a slow gate, and what to do about
a flaky test.

## Security notes

See [security.md](security.md). Short version: pinned tool versions are a
security control, because they stop the software that judges your code from
changing without review. A gate is not a security scanner — the table in that
file states exactly what each of the five stages can and cannot prove. The
shipped CI workflow is a reference and is not executed here; if you adopt it,
keep secrets in the hosting service's secret store, never in the workflow file
or a fixture, and remember that a workflow triggered by a fork is running a
stranger's configuration. The lab itself needs no credentials and handles no
personal data.

## Extension exercises

1. **Add a sixth stage.** Add a `build` stage that runs `python -m build` (or,
   with no packaging tooling, `python -c "import pricekit"` from a directory
   that is not the project root). Put it last, and say in one sentence what it
   proves that the other five do not.
2. **Measure the cost of every stage.** Wrap `run_stage` so it prints the
   elapsed time per stage, then run the gate ten times and look at the spread.
   Now argue the ordering from your own numbers rather than from this lab's
   claim, and decide whether you would still put types before tests.
3. **Ratchet the floor.** Raise `fail_under` to 100, run the gate, and see it
   pass. Then delete one test and watch it fail. Write down, in the file, the
   rule your team would follow for changing that number — and note that a rule
   which allows lowering it silently is the same as having no floor.
4. **Break the gate on purpose, five ways.** Reproduce by hand each of the five
   defects the test suite injects, and confirm that exactly one stage goes red
   each time. If two stages go red for one defect, you have found an overlap
   worth understanding.
5. **Make a stage lie.** Change the tests stage to `"${coverage_bin}" run -m
   pytest || true`. The gate now passes on broken code. Run
   `bash tests/run_tests.sh` and watch the defect check catch it. This is the
   single most valuable minute in the lab: it shows that the suite is testing
   the gate, not the library.
6. **Write the workflow for a different service.** Using
   `ci-reference/quality-gate.yml` as the model, write the equivalent for
   another CI provider. The shape will be the same — trigger, clean machine,
   install pinned dependencies, run `bash check.sh` — and discovering that the
   shape is the same is the point of the exercise.

## Navigation

- **Previous day:** Day 76 — Ruff
  (`labs/sections/programming-with-python/day-076-linting-and-formatting-with-ruff/`).
- **Next day:** Day 78 — the first day of Week 12, Python for Automation and
  the Web (`labs/sections/programming-with-python/`).
- **Week 11 project:** the Tested Utility Library
  (`labs/sections/programming-with-python/projects/week-11/`). It builds
  directly on this lab: the library grows, and the gate you wrote today is what
  keeps it honest while it does.
