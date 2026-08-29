# Troubleshooting — Day 044 lab

## `python3: command not found`

Python 3 is not installed or not on your PATH. Revisit the Day 43 lesson
("Installing Python and Virtual Environments"). On some systems — notably
Windows — the command is `python`, not `python3`. Check which one reports a
3.x version:

```bash
python3 --version    # try this first
python --version     # fall back to this on Windows
```

Use whichever prints `Python 3.x`. This lab was authored on Python 3.14.0,
but any Python 3.8+ produces the same results.

## `python` runs Python 2 (prints `Python 2.x`)

On older machines the bare `python` command may be Python 2, whose `print`
and integer division differ. Always use `python3` for this course. If only
Python 2 is available, install Python 3 (see Day 43).

## `SyntaxError` after copying lines from the lesson

The lesson shows REPL sessions with `>>>` prompts. Those prompts are *not*
part of the code. In a `.py` file, write only the code — no `>>>` and no
expected-output lines.

## `ValueError: invalid literal for int() with base 10`

This is `int()` correctly refusing a string that is not a whole number (for
example `int("3.5")` or `int("oops")`). It is expected behaviour, not a bug.
In the exercises, make sure such conversions sit inside the `try` block so
the `except ValueError` handles them.

## `IndentationError` or `TabError`

Python uses indentation to define blocks, and mixing tabs and spaces breaks
it. Indent with spaces (four per level is the convention) and keep it
consistent. Most editors can "convert tabs to spaces" in their settings.

## The `id()` numbers in my run differ from the captured output

That is correct and expected — identities reflect memory addresses and change
every run and every machine. Only the *comparisons* (`True`/`False`) are
stable; those are what the tests check.

## `bash: tests/run_tests.sh: No such file or directory`

Run the command from the lab directory itself, not from a parent folder:

```bash
cd labs/sections/programming-with-python/day-044-variables-and-types
bash tests/run_tests.sh
```
