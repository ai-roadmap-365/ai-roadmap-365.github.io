# Troubleshooting — Day 052 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old version.
Check with `python3 --version`.

## The starter raises `NotImplementedError` when I run it

That is expected until you finish the exercises. Each unfinished function
raises `NotImplementedError` on purpose so you cannot accidentally think an
empty function "works." Replace each `raise NotImplementedError(...)` line
with the real body described in the comment above it. Once all five exercises
are done, `python3 starter/toolkit.py` prints the same pipeline as the
reference.

## `ModuleNotFoundError: No module named 'toolkit'`

Python imports a module by looking on its search path (`sys.path`), which does
not include the `examples/` subfolder by default. The import one-liners in
this lab add it first:

```bash
python3 -c "import sys; sys.path.insert(0, 'examples'); import toolkit; print(toolkit.dedupe([1, 1, 2, 1, 3]))"
```

Run this from the lab directory (the folder that contains `examples/`), not
from inside `examples/` itself.

## My `with_appended` changed the original list

You appended to the input list directly instead of to a copy. The whole point
of the function is to leave the caller's list untouched: make a shallow copy
first with `result = items[:]` (or `list(items)`), append to `result`, and
return `result`. If you write `items.append(value)` you have created the exact
aliasing bug this lesson warns about — the caller's list grows behind their
back.

## `.sort()` returned `None`

`.sort()` sorts the list **in place** and returns `None` — that is correct
Python behaviour, not a bug. If you want a sorted result to assign to a new
name, use `sorted(items)`, which returns a new list and leaves the original
alone. Writing `items = items.sort()` is a classic mistake: it throws away
your list and replaces it with `None`.

## My dedupe or flatten result is in a surprising order

`dedupe` must keep the first occurrence of each item and drop later repeats,
so the order follows the input. `flatten` reads the matrix row by row, left to
right, so `[[1, 2], [3, 4]]` becomes `[1, 2, 3, 4]`. If your order is wrong,
check that you append inside the loops in reading order and never sort.

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly (as the README shows) rather than executing it
directly: `bash tests/run_tests.sh`. You do not need to `chmod +x` anything.

## The test suite writes `__pycache__`

It should not: the runner sets `PYTHONDONTWRITEBYTECODE=1` before importing.
If you import the module yourself and see a `__pycache__` folder appear, it is
harmless cached bytecode; delete it with `rm -rf examples/__pycache__` or set
the same variable in your shell.
