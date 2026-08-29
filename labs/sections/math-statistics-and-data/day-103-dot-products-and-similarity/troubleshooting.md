# Troubleshooting — Day 103 lab

Every symptom below was either produced deliberately while building this lab or
hit by accident during it. Nothing here is hypothetical.

## `ModuleNotFoundError: No module named 'numpy'`

You are running the system `python3` rather than the lab's environment. From
the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Then use `.venv/bin/python3` and `.venv/bin/pytest` rather than the bare
commands. If NumPy is already installed somewhere else you would rather use,
point the harness at it:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## `ModuleNotFoundError: No module named 'similarity'` when running a script

The scripts in `examples/` import `similarity.py` and `catalogue.py` from
beside themselves, so they must be run from inside `examples/`:

```bash
cd examples
../.venv/bin/python3 01_the_length_confound.py
cd ..
```

The pytest suites do not have this problem — pytest puts each test file's
directory on the import path for you.

## `NotImplementedError: write dot`

Expected, and not an error in the usual sense. It means you have not written
that function yet. The starter test suite catches it and turns it into a skip:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that reports `1 passed, 51 skipped`. A skip means "not
attempted". A failure means "attempted and wrong".

## `ZeroDivisionError: float division by zero` in your `normalise`

You handed it the zero vector, `[0, 0, 0, 0]`. Its length is 0 and the function
divides by that length. This is not a case to paper over with a small epsilon —
the zero vector genuinely has no direction, so "which way does it point" has no
answer. Raise `ValueError` with a message saying so. The test
`test_1_3_normalise_refuses_the_zero_vector` checks exactly this.

## `ValueError: math domain error` from `math.acos`

Or, on Python 3.14, the fuller message `expected a number in range from -1 up
to 1, got 1.0000000000000002`.

Your `cosine_similarity` is not clamping. Compare a vector with itself, and
floating-point rounding can put the result one unit in the last place above
1.0, which is outside `acos`'s domain. This is not a rare edge case: three of
this lab's six four-component integer articles miss exact 1.0 through the
unguarded formula, and `race-day-nutrition` is the one that overshoots. The fix
is one line before you return:

```python
return max(-1.0, min(1.0, value))
```

## `nan` appearing in a ranking

Something in your catalogue is the zero vector and your `cosine_similarity`
returned `NaN` instead of raising. Two things go wrong at once, which is why
the lab refuses the input rather than propagating it:

- `NaN` compares false against everything, including itself, so it sorts to an
  unpredictable position — Python's `sorted` will not error, it will just put
  it somewhere;
- any mean or total computed over the column becomes `NaN` too, so the damage
  spreads well beyond the one bad row.

Raise at the point of the bad input.

## `AssertionError` from `test_1_7_rank_by_cosine_breaks_ties_alphabetically`

Two articles — `marathon-plan` and `storm-bulletin` — score exactly 0.0 against
the query `[1, 0, 0, 0]`. Your sort is leaving them in an order that depends on
dictionary insertion or on the comparison's internal details. Sort with an
explicit tie-break:

```python
sorted(pairs, key=lambda pair: (-pair[1], pair[0]))
```

The negation sorts the score downwards while the label still sorts upwards.

## `pytest starter` reports passes for exercises you have not written

This is the failure mode Day 100 shipped and then fixed, and it is the worst
kind: a wrong answer with a green tick on it.

Both `examples/` and `starter/` contain a module called `similarity`. pytest
imports test files by putting their directory on `sys.path`, so a combined run
can import whichever `similarity` it saw first and reuse it for the other
suite — meaning the starter tests measure the reference solution.

Each directory has a `conftest.py` that prevents this by putting its own
directory first on the path and dropping any `similarity` imported from
elsewhere. If you have deleted or edited one of them, restore it. Section 4 of
`tests/run_tests.sh` checks that the guard still works, by comparing the skip
count from `pytest starter` against the skip count from a combined `pytest` run
and failing if they differ.

## Your dimensionality numbers differ from the captured ones

Check the seed first. `examples/07_curse_of_dimensionality.py` uses
`numpy.random.default_rng(103)`, and NumPy guarantees the same stream for the
same seed within a major version, not across one. If you are on a different
NumPy, expect the digits to move.

What must **not** change is the shape of the result: mean absolute cosine
falling monotonically as the dimension rises, and tracking the exact formula
`gamma(d/2) / (sqrt(pi) gamma((d+1)/2))` to within a few percent. The reference
suite asserts the shape, not the digits, for exactly this reason.

## The harness says `pytest not found`

It looked in three places, in order: the `PYTEST` environment variable, the
lab's own `.venv/bin/pytest`, and your `PATH`. None had it. Either install into
`.venv` as above, or set `PYTEST` to a binary that exists. The harness stops
rather than skipping checks silently, which is deliberate — a suite that
quietly runs zero checks and exits 0 is worse than one that fails.

## The harness says numpy is not importable from a python it found

It resolved `pytest`, then looked for `python3` next to it, and that
interpreter has no NumPy. This usually means `PYTEST` points at a pytest from
one environment while NumPy lives in another. Point `PYTEST` at the pytest
inside the environment that has NumPy.

## `__pycache__` directories left behind after a run

Section 7 of the harness fails if it finds any. The harness exports
`PYTHONDONTWRITEBYTECODE=1` for its own runs, but a script you ran by hand
without it will leave them. Remove them from the lab directory:

```bash
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
rm -rf .pytest_cache
```

## Windows

The lab is written for macOS and Linux and was run on macOS 26.5.2 (Apple
Silicon). On Windows, the Python and the pytest are the same; the shell is not.
`tests/run_tests.sh` is a bash script and needs bash — Windows Subsystem for
Linux or Git Bash both provide one, and inside WSL the instructions are the
Linux instructions unchanged. The paths also differ: `.venv\Scripts\python.exe`
rather than `.venv/bin/python3`. None of this was tested here, so it is
described rather than claimed.
