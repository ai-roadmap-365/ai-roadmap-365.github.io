# Troubleshooting — Day 102 lab

Every failure listed here was produced on the authoring machine while building
this lab, unless the entry says otherwise. Where a message is quoted, it is a
quote.

## `ModuleNotFoundError: No module named 'numpy'`

The lab-local environment has not been created, or you are running the system
`python3` instead of the one inside it.

```bash
cd labs/sections/math-statistics-and-data/day-102-linear-transformations
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Expect `2.5.2`. Note the `.venv/bin/` prefix on every command in this lab; that
is what selects the right interpreter.

## `ModuleNotFoundError: No module named 'transforms'` (or `'shapes'`)

You ran a reference script from the lab directory rather than from inside
`examples/`. The scripts import `transforms.py` and `shapes.py` from beside
themselves, so:

```bash
cd examples
../.venv/bin/python3 01_columns_are_landings.py
cd ..
```

The pytest commands are the other way round — run those from the **lab**
directory, because they name the directory to collect:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

## Unattempted exercises show as `s` rather than `.`

That is correct. `s` is a skip, and it means "not attempted". The starter suite
skips anything that still raises `NotImplementedError` or whose prediction in
`answers.py` is still `None`, so your score only ever counts work you actually
did. An untouched checkout prints `1 passed, 53 skipped`.

## A test failed with `NotImplementedError` instead of skipping

This happened while building the lab, and it is worth understanding rather than
just fixing. Python evaluates arguments **before** the call, so a test written
as

```python
written(compose, rotation(math.pi / 2), shear_x(2.0))
```

calls `rotation` and `shear_x` first — and if either is still unwritten, the
`NotImplementedError` escapes before `written` ever runs, and pytest reports a
failure. It would say "attempted and wrong" about work you had not attempted,
which is exactly the lie the skip mechanism exists to prevent. The fix, which
is now in the suite, is to pass a callable that does the whole thing:

```python
written(lambda: compose(rotation(math.pi / 2), shear_x(2.0)))
```

If you add tests of your own, follow that shape.

## The starter tests pass without me writing anything

Almost certainly you ran a bare `pytest` with no directory argument, and the
import guard is missing or has been edited. Both `examples/` and `starter/`
contain modules called `transforms` and `shapes`, and pytest puts a test file's
directory on `sys.path` to import it — so collecting both suites at once can
import the reference `transforms` and hand it to the starter tests, which then
pass against a solution you did not write.

Each directory's `conftest.py` prevents this by putting its own directory first
on the path and dropping any `transforms`, `shapes` or `answers` module that
was imported from elsewhere. Section 4 of `tests/run_tests.sh` proves the guard
still works by running both suites together and asserting the skip count did
not change.

If you have deleted a `conftest.py`, restore it with
`git checkout -- starter/conftest.py`.

## `cos(pi / 2)` prints `6.123233995736766e-17` — is that broken?

No, and one of the reference tests asserts that it happens. `pi` cannot be
represented exactly in binary floating point, so the value handed to `cos` is
not quite pi/2, and its cosine is not quite zero. `sin(30 degrees)` is likewise
`0.49999999999999994`.

This is why the lab compares floats with a stated tolerance of `1e-12` and
never with `==`. If you write your own check as `assert value == 0.0`, it will
fail on a correct answer. See `expected-output/FIELDS.md` for the full note.

## `numpy.linalg.det` gives `7.000000000000001` where I expect `7`

Also expected, also asserted. Section 8 of `05_determinant_inverse_rank.py`
explains it: the from-scratch `determinant` computes `a*d - b*c` directly,
which is exact on whole numbers, while `numpy.linalg.det` factorises the matrix
first — the general method that also works on a 500 by 500 matrix — and that
factorisation rounds. Compare determinants with a tolerance.

## `numpy.linalg.LinAlgError: Singular matrix`

The intended behaviour of exercise 6.8, not a fault. `numpy.linalg.inv` raises
it for `[[1, 2], [2, 4]]`, whose determinant is 0. The lab's own `inverse`
raises `SingularMatrix` for the same matrix with a longer message. Both are
catchable as `ValueError`, because `numpy.linalg.LinAlgError` is a subclass of
it:

```python
except ValueError:   # catches both
    ...
```

## `AssertionError` in my `rotation` with the two off-diagonal signs swapped

The commonest wrong answer, and it is a clockwise rotation rather than an
anticlockwise one. The check: `rotation(pi / 2)` must send `(1, 0)` to
`(0, 1)` — *up* — not to `(0, -1)`. If yours goes down, swap which entry
carries the minus sign. The minus belongs on the `-sin(theta)` in the top
right, which is the first coordinate of where `(0, 1)` lands.

## My `compose` gives the right matrix for the wrong reason

Check it against a case where the order matters, not against two rotations
(which commute and will agree either way). `shear_x(2)` and `rotation(pi / 2)`
are the pair the tests use precisely because `B @ A` and `A @ B` differ:

```
shear then rotate:  [[0, -1], [1, 2]]
rotate then shear:  [[2, -1], [1,  0]]
```

## `bash: tests/run_tests.sh: No such file or directory`

Run it from the lab directory, not from the repository root or from `tests/`:

```bash
cd labs/sections/math-statistics-and-data/day-102-linear-transformations
bash tests/run_tests.sh
```

## `FAIL: pytest not found.`

The harness looks for `pytest` in three places, in order: the `PYTEST`
environment variable, `.venv/bin/pytest` inside the lab, and your `PATH`. It
stops with instructions rather than skipping checks quietly. Either create the
environment as above, or point it at an existing one:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## `__pycache__` directories appearing

The lab's own commands set `PYTHONDONTWRITEBYTECODE=1` and pass
`-p no:cacheprovider`, so they leave nothing behind, and section 7 of the
harness fails if anything does. If you have run a script another way, clean up
with:

```bash
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
rm -rf .pytest_cache
```

## Windows

Not run here, and this file will not pretend otherwise. Use the Windows
Subsystem for Linux and follow the Linux instructions unchanged, or use Git
Bash with `.venv\Scripts\python.exe` and `.venv\Scripts\pytest.exe` in place of
the `.venv/bin/` paths. The Python and the arithmetic are identical; only the
path separators and the environment layout differ.
