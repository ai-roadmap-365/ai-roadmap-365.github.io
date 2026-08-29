# Troubleshooting — Day 100 lab

Every message below was produced on the authoring machine while building this
lab, or is reproduced from the exact text NumPy emits. Nothing here is
invented.

## `ModuleNotFoundError: No module named 'numpy'`

The interpreter you ran does not have NumPy. Either you skipped the install,
or you ran the system `python3` instead of the one inside `.venv`.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Use `.venv/bin/python3` and `.venv/bin/pytest` explicitly, exactly as the
README writes them, and the question of which interpreter you got never comes
up.

## `ModuleNotFoundError: No module named 'matrix'` or `'dataset'`

You ran a script in `examples/` from the wrong directory. Those scripts import
`matrix.py` and `dataset.py` from beside themselves, so run them from inside
`examples/`:

```bash
cd examples
../.venv/bin/python3 02_three_meanings.py
cd ..
```

The pytest suites do not have this problem — pytest puts the test file's own
directory on the import path — which is why `.venv/bin/pytest examples` works
from the lab directory.

## `FAIL: pytest not found.`

The harness looked in three places and found nothing: the `PYTEST` environment
variable, `.venv/bin/pytest` inside the lab, and your `PATH`. Do the install
above, or point it at a pytest you already have:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

It stops rather than skipping the checks quietly, which is deliberate: a test
suite that reports success because it ran nothing is worse than one that
fails.

## `FAIL: installed numpy matches requirements.txt (expected [2.5.2], got [...])`

Your NumPy is a different version from the one this lab was captured on.
Nothing is broken and the tests will very likely still pass — none of them
depend on version-specific behaviour — but the harness reports the difference
rather than letting you find it later in a confusing diff against
`expected-output/`. To match exactly:

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

## `ValueError: operands could not be broadcast together with shapes (3,4) (3,)`

This is the lesson, not a fault. NumPy lined the two shapes up from the right,
found 4 against 3, and stopped, because 4 and 3 are neither equal nor 1. You
almost certainly meant one value per row, which is written as a column:

```python
per_row.reshape(3, 1)          # shape (3, 1), broadcasts down the rows
M.mean(axis=1, keepdims=True)  # the same idea, from a reduction
```

## `ValueError: cannot reshape array of size 12 into shape (5,3)`

Reshaping never invents or discards entries, so the new shape's dimensions
must multiply to the same total. 5 times 3 is 15 and the array holds 12. Use
`-1` for one dimension and let NumPy work it out: `M.reshape(6, -1)`.

## `TypeError: index a Matrix with a (row, column) pair`

You wrote `m[0]` on the from-scratch class, which supports only `m[0, 2]`.
NumPy accepts both, and `M[0]` there means the whole of row 0. The from-scratch
class refuses on purpose: one syntax, one meaning, no guessing.

## `ValueError: assignment destination is read-only`

You tried to write into the result of `numpy.broadcast_to`. That array is a
fiction — three rows all pointing at the same twelve bytes — so a single write
would appear in three places at once. NumPy marks it read-only rather than
allow that. Call `.copy()` on it if you genuinely want a real array of that
shape.

## The tests pass but my numbers do not match `expected-output/`

Read `expected-output/FIELDS.md` first: timings and the platform line are
expected to differ, and `starter-progress.txt` changes as you complete
exercises. Every actual number is fixed and must match; there is no randomness,
no clock and no file system anywhere in this lab.

## My starter tests all say `s` and none say `.`

That is correct on an untouched checkout. `s` means skipped, which here means
"not attempted yet". As you fill in `matrix.py` and `answers.py`, the `s`
characters become `.` characters. On a fresh checkout the summary reads
`1 passed, 32 skipped`; when you are finished it reads `33 passed`.

## A test says `answers.X is still unanswered`

You left that constant as `None`. The tests skip rather than fail on `None`
specifically so that an unanswered question is visibly different from a wrong
one.

## Running `pytest` with no argument — why there is a `conftest.py`

Running `.venv/bin/pytest` from the lab directory collects both suites at
once, and `examples/` and `starter/` each contain a module called `matrix`.
pytest imports a test file by putting that file's directory on `sys.path`, and
a module name that is already in `sys.modules` is not imported again — so
without intervention the starter tests would import the *reference* solution,
and eleven exercises you have not written would report as passing.

That failure mode was observed while this lab was being built, which is why
each directory carries a small `conftest.py` that puts its own directory first
on the import path and drops any `matrix` or `dataset` module loaded from
elsewhere. With it in place, the combined run reports `42 passed, 32 skipped`
on an untouched checkout — 41 reference tests, one starter environment check,
and your thirty-two exercises correctly skipped. Section 4 of
`tests/run_tests.sh` asserts exactly that, so the guard cannot rot unnoticed.

You can still run one suite at a time, and every command in this lab does:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

## A `__pycache__` or `.pytest_cache` directory appeared

The lab's own commands set `PYTHONDONTWRITEBYTECODE=1` and pass
`-p no:cacheprovider`, so they leave nothing behind — section 7 of the harness
fails if they do. A directory that appears anyway came from a command you ran
yourself without those settings. Remove it:

```bash
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
rm -rf .pytest_cache
```

## Windows

The commands here are written for macOS and Linux. On Windows the interpreter
inside a virtual environment lives at `.venv\Scripts\python.exe` rather than
`.venv/bin/python3`, and `bash tests/run_tests.sh` needs a bash — Git Bash or
the Windows Subsystem for Linux. Under WSL the Linux instructions apply
unchanged. **The harness has not been run on Windows for this lab**, so that
paragraph is guidance from the platform's documented layout rather than
something reproduced here.
