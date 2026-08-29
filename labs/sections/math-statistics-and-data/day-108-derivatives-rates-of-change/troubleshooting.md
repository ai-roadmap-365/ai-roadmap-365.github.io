# Troubleshooting

Every entry here was hit while building this lab, or is a mistake the test
suite is specifically written to catch. Nothing is invented for the sake of
having a document.

## `ModuleNotFoundError: No module named 'derivatives'`

You ran a script in `examples/` from the lab directory instead of from inside
`examples/`. The scripts import `derivatives.py` and `dataset.py` from beside
themselves.

```bash
cd examples
../.venv/bin/python3 05_the_u_shaped_error.py
cd ..
```

`pytest`, by contrast, is run from the lab directory — `.venv/bin/pytest
examples -q` — because each directory's `conftest.py` puts that directory on
the import path for its own tests.

## `ModuleNotFoundError: No module named 'numpy'`

You ran with the system `python3` rather than the lab's virtual environment.
Use `.venv/bin/python3`, not `python3`. If `.venv` does not exist yet, the
Installation section of the README creates it.

## `pytest: command not found`, or the harness refuses to start

`tests/run_tests.sh` looks for pytest in three places, in order: the `PYTEST`
environment variable, `.venv/bin/pytest` inside the lab, and your `PATH`. If it
finds none it prints the install commands and exits 1 rather than silently
skipping the checks that need it. Either create the `.venv`, or point it at an
existing pytest:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## Every one of my derivative answers is exactly double the right one

You divided by `h` in `central_difference` instead of by `2 * h`. This is the
single most common bug in the topic and it is genuinely hard to spot, because
doubling does not look wrong when you do not already know the answer.

`test_2_3_central_difference_did_not_forget_the_two` exists precisely to name
this: it checks that your value is *not* 12.0 before checking that it is 6.0,
so the failure message points at the cause rather than at the symptom.

The same trap has a second-derivative version: dividing by `h` instead of
`h * h` in `second_difference` gives 0.02 where 2.0 was wanted, at h = 0.01.
There is a test for that too.

## My U-shaped error curve does not bottom out where the README says

It very probably should not, and the lab does not assert that it does.

`expected-output/FIELDS.md` has the full account. In short: the authoring
machine's central-difference minimum was at h = 3.16e-6, the balance of the two
error terms predicts 8.7e-6, the assertion is only that it lands somewhere in
`1e-7` to `1e-4`, and the noise near the bottom is real — the error at h = 1e-6
is *worse* than at h = 3.16e-6 on the captured run.

Something IS wrong if your minimum sits at either end of the grid, or if the
error falls monotonically all the way to h = 1e-14.

## The error is huge and I made h very small to be careful

That is the backwards intuition the whole lab is about. Below roughly 1e-8 the
subtraction `f(x + h) - f(x - h)` cancels away most of the digits the two values
had in common, and dividing by a tiny `h` multiplies what is left. At h = 1e-300
you get exactly `0.0`, with no warning of any kind.

For float64: aim for about 1e-5 to 1e-6 with the central difference, and about
1e-8 with the forward difference. Script 05 measures both.

## My numerical derivative disagrees with a framework's gradient at exactly one point

Check whether that point is a corner. `|x|` at 0 and `max(x, 0)` at 0 have no
derivative, and the central difference returns 0.0 and 0.5 respectively — both
of them confident, neither of them meaningful, and 0.5 is not a value any
framework would report.

The cheapest test costs nothing you have not already computed: compare the
forward and backward differences. If they disagree by more than your tolerance,
the central value between them is an average rather than a slope. Script 07
ends on exactly that check.

## `classify_stationary_point` returns "undecided" and I expected "minimum"

If the point is x⁴ at 0, that is correct and the test asserts it. x⁴ at 0 IS a
minimum, and the second derivative there is zero, so nothing this function can
see distinguishes it from x³ at 0, which is not a minimum. Returning "minimum"
would be a lie you happened to get away with on one of the two.

If the point is something else, check that your `tol` comparison is on the
second difference's *sign* and not its magnitude, and that you test the first
derivative before the second.

## `pytest starter` reports failures on an untouched checkout

It should report `1 passed, 99 skipped` and nothing else. If you see failures,
something in `starter/` was edited in a way that raises an exception other than
`NotImplementedError` — a syntax error, or a partly written function that raises
`TypeError` instead. The suite only skips on `NotImplementedError`; anything
else it treats, correctly, as "attempted and wrong".

`git checkout -- starter/` resets your work if you want a clean start.

## `pytest` at the lab root turns my skips into passes

It should not, and section 4 of the harness checks that it does not. Both
`examples/` and `starter/` contain modules called `derivatives` and `dataset`,
and pytest imports test files by putting their directory on `sys.path` — so
without the two `conftest.py` files, the starter tests would import the
reference solution and report unwritten exercises as passing. If you delete
either `conftest.py`, that is what will happen, and it is the worst possible
failure mode: a wrong answer with a green tick on it.

## The harness says a `__pycache__` was left behind

The lab's own commands do not leave one. Two things cause it: running a script
without `PYTHONDONTWRITEBYTECODE=1` and without `-p no:cacheprovider`, or
importing a lab module from your own script elsewhere.

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

Note the `-path ./.venv -prune`. The virtual environment ships NumPy's and
pytest's own precompiled bytecode — hundreds of `__pycache__` directories that
came with the packages and say nothing about whether this lab tidied up. The
harness prunes `.venv` from both of its clean-disk searches for the same reason,
and `.venv` is not treated as a stray file anywhere: the README tells you to
create it.

## Windows

Not run here, and this file will not pretend otherwise. Use the Windows
Subsystem for Linux and follow the Linux instructions unchanged, or use Git Bash
with `.venv\Scripts\python.exe` in place of `.venv/bin/python3`. The bash
harness needs a bash; PowerShell will not run it.

## A number in `expected-output/` does not match mine

Read `expected-output/FIELDS.md` before assuming anything is broken. It lists,
line by line, which captured values may legitimately differ on your machine —
elapsed times, the platform string, your own progress score, the exact position
of the bottom of the U, and every error below about 1e-10 — and which may not.
