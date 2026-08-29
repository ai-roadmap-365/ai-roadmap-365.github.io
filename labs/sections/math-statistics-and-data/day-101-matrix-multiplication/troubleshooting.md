# Troubleshooting — Day 101 lab

Every problem below was met while building this lab, or is the documented
behaviour of a tool the lab uses. Nothing here is invented to fill a section.

## `ModuleNotFoundError: No module named 'numpy'`

The virtual environment either does not exist or is not the interpreter you are
running. From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Then use `.venv/bin/python3`, not a bare `python3`. The two are different
interpreters, and only one of them has NumPy.

## `ModuleNotFoundError: No module named 'matmul'` or `'dataset'`

You are running a reference script from the wrong directory. They import
`matmul.py` and `dataset.py` from beside themselves:

```bash
cd examples
../.venv/bin/python3 01_matmul_from_scratch.py
```

The pytest suites do not have this problem, because pytest puts each test
file's own directory on the import path for you.

## The starter tests all say `s` instead of passing

That is correct on an untouched checkout, and it is `1 passed, 56 skipped`.
`s` means **skipped**, which here means "not attempted": a function that still
raises `NotImplementedError`, or a prediction in `answers.py` that is still
`None`. As you fill them in the skips turn into passes.

Run `.venv/bin/pytest starter -q -rs` to see the reason for each skip.

## A starter test fails instead of skipping

That is the design. A skip means you have not attempted it; a **failure** means
you committed to an answer and it was wrong. The failure prints both your value
and the real one, which is the whole point — a wrong prediction you can see is
worth more than a right answer you copied.

## The two suites disagree about how many tests were skipped

This is the bug that shaped the lab, and it is worth understanding rather than
just avoiding.

Both `examples/` and `starter/` contain a module called `matmul`. pytest imports
a test file by putting that file's directory on `sys.path` — so when both suites
are collected in one run, whichever `matmul` is imported first gets cached in
`sys.modules` and **reused for the other suite**. The starter tests then import
the reference solution, and every unwritten exercise reports as *passing*.

That happened on the Day 100 lab, where eleven unwritten exercises passed
against the reference, and it was caught only because the skip count changed
between two runs that should have agreed. A wrong answer with a green tick on it
is the worst kind of test failure, because nothing tells you.

The fix is the `conftest.py` in each directory: it puts its own directory first
on the import path and evicts any `matmul`, `dataset` or `answers` that was
imported from somewhere else. Section 4 of `tests/run_tests.sh` asserts that the
skip count is identical whether the suites run separately or together, so the
same mistake cannot come back quietly.

If you ever see the counts disagree, do not ignore it. Check that both
`conftest.py` files are still present.

## `ValueError: matmul: Input operand 1 has a mismatch in its core dimension 0`

This is the shape error, and it is the most common error in the whole of applied
linear algebra. The full text on this machine:

```
ValueError: matmul: Input operand 1 has a mismatch in its core dimension 0,
with gufunc signature (n?,k),(k,m?)->(n?,m?) (size 2 is different from 3)
```

Ignore the gufunc signature the first time you read it. **Print the two shapes
and look only at the inner two numbers:**

```python
print(left.shape, right.shape)
```

An `(m, n) @ (n, p)` is legal only when the inner dimensions agree. Here they
were 3 and 2.

The repair is usually a transpose — but there are two of them and they are not
interchangeable. `X @ X.T` gives `(2, 2)` and compares examples with examples;
`X.T @ X` gives `(3, 3)` and compares features with features. Both make the
exception go away and only one answers your question. Decide which one you
meant rather than trying them until something runs.

## `ValueError: operands could not be broadcast together with shapes (2,2) (3,)`

A bias of the wrong length. There is one bias per **output unit**, not one per
example — so a layer two units wide takes exactly two numbers, however large the
batch is. This is the Day 100 broadcasting rule doing its job.

## My `matmul_loops` returns rows that are all identical

You built the result grid with `[[0] * p] * m`. That makes `m` references to
**one** list, so `C[0][0] = ...` writes into every row at once. Use:

```python
C = [[0] * p for _ in range(m)]
```

This is the Day 100 view-versus-copy lesson appearing in plain Python, with no
NumPy involved. `test_1_3_the_rows_of_the_result_are_independent_objects`
catches it and says so by name.

## `A @ B` gives the wrong answer, and swapping them fixes it

You have the composition order backwards, which is the single most common
conceptual error on this day. In `A @ B`, **B runs first** — it is the matrix
standing next to the vector in `A @ (B @ v)`. Matrices compose right to left,
like nested function calls `A(B(v))`.

English reads "A times B" left to right and the arithmetic does not. That
mismatch is the bug.

## `TypeError: unsupported operand type(s) for @`

You are using `@` on plain Python lists. `@` is NumPy's operator (strictly, it
calls `__matmul__`, which lists do not define). Either convert with
`np.array(...)` first, or call your own `matmul_loops`.

## The timing numbers are nothing like the captured ones

Expected, and fine. `expected-output/FIELDS.md` lists exactly which numbers are
machine-specific. No test in this lab asserts a duration; the assertions are
wide ratios, set far below what was measured.

If your **float64** result is not much faster than your **int64** result, that
is worth investigating: it suggests your NumPy is not reaching a BLAS library.
Section 3 of `05_cost_and_speed.py` prints what your build reports about itself.

## `bash tests/run_tests.sh` says pytest was not found

Either create the lab environment as above, or point the harness at an existing
one:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The harness uses the `python3` beside that `pytest`, because that is the
interpreter NumPy is installed into.

## Windows

**Not tested here.** This lab was run on macOS only, and no Windows output is
reproduced anywhere in it.

The commands are unchanged on Linux. On Windows, the documented `venv` layout
puts the interpreter at `.venv\Scripts\python.exe` rather than
`.venv/bin/python3`, so either use the Windows Subsystem for Linux and follow
the Linux instructions, or use Git Bash and substitute that path. The Python and
NumPy behaviour the lab actually teaches does not depend on the operating
system; only the paths do.
