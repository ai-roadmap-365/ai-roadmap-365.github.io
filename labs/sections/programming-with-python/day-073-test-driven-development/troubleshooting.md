# Troubleshooting — Day 073 lab

## `FAIL: pytest not found.`

The runner looked in three places and found nothing. Create the environment:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Or point it at a pytest you already have:
`PYTEST=/path/to/pytest bash tests/run_tests.sh`.

## `ModuleNotFoundError: No module named 'bowling'`

You ran pytest from the wrong directory, or you moved the test file away from
the module it imports. pytest puts the test file's own directory at the front
of the import path, so `starter/test_bowling.py` finds `starter/bowling.py` and
`examples/test_bowling.py` finds `examples/bowling.py`. Run from the lab
directory:

```bash
.venv/bin/pytest starter/test_bowling.py
```

## `import file mismatch` when you run both suites at once

`.venv/bin/pytest` with no arguments collects `starter/test_bowling.py` *and*
`examples/test_bowling.py`, two files with the same module name and no package
around them. pytest cannot import both. Name the one you want:

```bash
.venv/bin/pytest starter/test_bowling.py     # your work
.venv/bin/pytest examples/test_bowling.py    # the reference
```

## `no tests ran in 0.01s` and an exit code of 5

Expected, before cycle 1. `starter/test_bowling.py` has no test functions yet,
and pytest reserves exit code 5 for "nothing to run". Write the cycle 1 test
and it becomes a proper failure.

## `AttributeError: module 'bowling' has no attribute 'score'`

The correct first red of the whole kata. Your test asked for a name your module
has not got. Cycle 5 produces the same message for `ScoringError`, for the same
good reason.

## `Failed: DID NOT RAISE ScoringError`

pytest's way of saying the code inside `pytest.raises(...)` finished normally
when you expected a refusal. In cycle 6 that is the red you are looking for. If
you see it *after* writing the check, the check is in the wrong branch — a
strike never reaches the open-frame path where the twelve-pin test lives.

## `IndexError: list index out of range` inside `score`

The cycle 7 red, and worth pausing over. The failure is real, but it is your
implementation crashing rather than refusing. The whole purpose of cycle 7 is
to turn that crash into a stated `ScoringError`.

## My cycle 5 test kills the whole file instead of one test

You wrote `from bowling import score, ScoringError` at the top. A missing name
in a `from ... import` fails at collection time and takes every test in the
file with it, so the summary line says `1 error` rather than
`1 failed, 4 passed`. Use `import bowling` and reach for `bowling.score` and
`bowling.ScoringError` inside the tests, as `starter/test_bowling.py` does.

## The perfect-game test passed on the first run and I do not trust it

Correct instinct — that is cycle 8. Copy `bowling.py` to a temporary
directory, replace `if _is_strike(rolls, roll):` with `if False:`, run the
suite against the copy, and watch the test go red. Then put the good file back.
A test you have never seen fail is a test you have no evidence about.

## `cycle N RED shows the N-1 earlier cycles still green` failed

The runner is reading `examples/cycles/`, not your work, so this can only mean
a capture file in that directory was edited or replaced. Restore it with
`git checkout -- examples/cycles/`.

## My own RED block shows two failing tests

You added two test functions in one cycle. Delete one, re-run, and record the
cycle properly. One test per cycle is the entire discipline being practised;
two tests at once is how people end up writing code that no single test
actually pins down.

## My own GREEN block shows fewer passing tests than the cycle number

You deleted or renamed an earlier test, or an earlier one has started failing
because of the code you just wrote. The second case is the more interesting
one: your new code broke old behaviour, which is exactly the event a regression
suite exists to report. Fix it before moving on; never comment out a red test
to get to the next cycle.

## `sed: 1: "...": bad flag in substitute command`

You are on macOS, where `sed -i` needs an explicit backup suffix
(`sed -i ''`). The test runner never edits in place — it writes the mutated
copy to a temporary directory — so this only bites if you are experimenting on
your own.

## `__pycache__` directories appeared

Python's bytecode cache. Harmless, ignored by version control, and removable:

```bash
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
```

The test runner sets `PYTHONDONTWRITEBYTECODE=1` so its own runs leave none.
