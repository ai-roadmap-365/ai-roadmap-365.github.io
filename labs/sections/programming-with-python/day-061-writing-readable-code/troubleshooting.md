# Troubleshooting — Day 061 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and most
Linux systems, bare `python` may be missing or point to an old version. Check
with `python3 --version` (you want 3.9 or newer for the `list[float]` hints).

## The tests failed after I renamed something

That is the safety net doing its job — you changed behaviour, not just a name.
Undo the last single change and run `bash tests/run_tests.sh` again to get back
to green, then redo it more carefully. The most common causes are a typo that
renamed one use of a variable but not another, or accidentally changing the
order of operations while "tidying" an expression. Refactor in the smallest
steps you can, testing after each.

## The golden output does not match after my refactor

The tool must print exactly the seven lines in
`expected-output/FIELDS.md` for the input `70 85 90 55 60`. Watch for changes
that alter numbers or formatting: switching population standard deviation
(divide by `n`) to sample standard deviation (divide by `n - 1`) changes
`stdev`; changing the pass mark changes `passing`; using `round()` instead of
`:.2f` formatting can differ at the last digit. Readability refactoring keeps
all of these identical — only the names and structure change.

## `SyntaxError` mentioning `list[float]`

You are on a Python older than 3.9. Either upgrade, or write the hints as
`from typing import List` and `List[float]`. The reference targets 3.9+, where
the built-in `list[...]` form works directly.

## The `black` / `ruff` checks say "skip"

That is expected and fine — those tools are optional and are not installed by
default. The suite skips them cleanly and still passes. If you *want* them, run
`python3 -m pip install black ruff`; if `pip` is restricted on your machine,
ignore this entirely, as nothing the lab asserts depends on them.

## `ModuleNotFoundError: No module named 'report'` in the import check

Python looks for modules on its search path (`sys.path`), which does not
include the `examples/` subfolder by default. The import one-liner adds it
first:

```bash
python3 -c "import sys; sys.path.insert(0,'examples'); from report import median; print(median([1,2,3,4]))"
```

Run it from the lab directory (the folder that contains `examples/`).

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly, as the README shows: `bash tests/run_tests.sh`.
You do not need to `chmod +x` anything.

## The starter still prints `NotImplementedError` — no, it does not

Unlike some labs, this starter is a **complete, working** program from the
start — the exercise is to *refactor* it, not to fill in blanks. If it ever
raises an error, you introduced it during the refactor; restore the original
with `git checkout -- starter/messy.py` and begin again in smaller steps.
