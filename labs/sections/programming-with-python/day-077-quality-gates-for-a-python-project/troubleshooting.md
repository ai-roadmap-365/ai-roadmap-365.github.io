# Troubleshooting — Day 077 lab

## `FAIL: ruff not found` (or mypy, or coverage)

The gate refuses to run a stage it cannot run. That refusal is deliberate: a
gate that silently skips a stage is worse than no gate, because everyone
downstream believes it ran.

Install the tools once:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Or point the scripts at tools you already have:

```bash
RUFF=/path/to/ruff MYPY=/path/to/mypy COVERAGE=/path/to/coverage bash check.sh
```

`check.sh` looks for each tool in this order: the environment override, this
project's `.venv/bin/`, the parent directory's `.venv/bin/`, then `PATH`.

## `ModuleNotFoundError: No module named 'pricekit'`

The tests import the package by name, so the project root has to be on
`sys.path`. The reference `pyproject.toml` handles this with
`pythonpath = ["."]` under `[tool.pytest.ini_options]`. If you are working in
`starter/` and have not written that line yet, add it — and notice the failure
mode it fixes: without it, `python -m pytest` works and plain `pytest` does
not, which is precisely the "works when I run it my way" difference a gate
exists to eliminate.

## `bash check.sh` prints `gate PASSED (with no stages)`

That is the shipped state of `starter/check.sh`. It has no stages, so it
approves everything. Start with exercise 1.

## The format stage fails on files you never touched

Almost always a missing `line-length` setting. Ruff's default is 88; the
reference project sets 100 in `[tool.ruff]`. Until exercise 1b is done, the
formatter judges `pricekit/money.py` and `pricekit/receipt.py` against the
default and wants to rewrap them. Add the `[tool.ruff]` table and they stop
being flagged.

Fix what remains with `ruff format .` — but only ever from your own hand, never
from inside the gate. `--check` exists so the gate reports rather than
rewrites: a gate that silently edits the code it is judging can never be
trusted to have judged the code you wrote.

## The lint stage reports `I001` about imports that look fine

`I001` is "import block is un-sorted or un-formatted". Ruff wants standard
library, third party and local imports in separate, alphabetised groups.
`ruff check --fix .` sorts them for you. This is a rule about consistency, not
correctness — which is exactly why mechanising it is worth it, because it is
the kind of thing a human reviewer should never spend attention on.

## The types stage fails with `[override]` on a dunder method

You changed the return annotation of a method that Python's own object model
already types. `__str__` must return `str`; annotating it `-> int` produces
both an `[override]` error (incompatible with `object.__str__`) and a
`[return-value]` error (the body returns a string). That is the defect the
test suite injects on purpose, so seeing it means the type stage is working.

## The tests stage fails but the coverage stage still passes

Expected, and worth understanding. `coverage run` records what executed
regardless of whether the assertions held; `coverage report` then judges that
record against `fail_under`. A run can be fully covered and completely wrong —
which is the whole argument of this lesson. In report-everything mode the gate
shows you both facts; the verdict at the bottom is what decides the merge.

## The coverage stage fails at 55% in the starter

Also expected. The starter ships tests for `pricekit/money.py` and none for
`pricekit/receipt.py`. Read the `Missing` column: each line range is a rule
nothing exercises. Write the tests, re-run, repeat. When you are done, read
what you wrote and ask whether each test would still fail if the function were
wrong — coverage will not ask that question for you.

## `coverage report` says `No data was collected`

You ran `coverage report` without a preceding `coverage run`, or the `source`
setting points at a package that was never imported. Check `[tool.coverage.run]`
names the package you are actually testing.

## `--include is ignored because --source is set`

A configuration conflict: `[tool.coverage.run] source` in `pyproject.toml`
wins over a `--include` flag on the command line. Either drop the flag or run
from a directory whose configuration you control — the `coverage-demo`
directory has no `pyproject.toml` for exactly this reason.

## The gate is slow

Measure before you optimise. `time bash check.sh` will usually show the type
and test stages dominating. Then decide honestly: a gate that takes ten
seconds gets run constantly; a gate that takes ten minutes gets run once, at
the end, by someone who has already moved on. If yours is slow, the fixes in
order of payoff are to run the fast stages first (already done here), to use
`--fail-fast` locally while leaving CI in report-everything mode, and to move
genuinely slow checks out of the per-commit gate into a scheduled run.

## The pre-commit hook keeps getting in the way

Then it is doing the wrong job. `examples/ci-reference/pre-commit-config.yaml`
deliberately holds only fast hooks. If yours runs the test suite, remove it —
a hook that makes `git commit` take twenty seconds will be bypassed with
`git commit --no-verify` within a week, and then you have neither the hook nor
the habit.

## A test passes locally and fails in continuous integration

That is the clean checkout earning its keep. The usual causes, in order of
frequency: a file you never committed, a package installed globally on your
machine but absent from `requirements.txt`, a test that depends on the order
the suite happens to run in, and a path or an environment variable that exists
only on your machine. Reproduce it by cloning the repository into a fresh
directory and running `check.sh` there.

## A test fails only sometimes

That is a flaky test, and it is the single most corrosive thing that can
happen to a suite — not because of the failures, but because a suite that
cries wolf teaches everyone to ignore it, including on the day it is right.
Do not add a retry. Find the cause (a real clock, a real network call, a
shared temporary file, dependence on dictionary or test ordering), fix it, and
if you cannot fix it, delete the test and record why. A deleted flaky test is
an honest gap; a retried flaky test is a lie with a green tick on it.

## Windows

Run everything inside WSL. `check.sh` and `tests/run_tests.sh` are bash
scripts, and a `.venv` on native Windows puts its executables in
`.venv\Scripts\` rather than `.venv/bin/`, which the resolver does not look
for.
