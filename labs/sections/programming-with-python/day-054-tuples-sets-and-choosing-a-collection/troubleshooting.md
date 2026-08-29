# Troubleshooting — Day 054 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old version.
Check with `python3 --version`.

## The starter raises `NotImplementedError` when I run it

That is expected until you finish the exercises. Each unfinished function
raises `NotImplementedError` on purpose so you cannot accidentally think an
empty function "works." Replace each `raise NotImplementedError(...)` line
with the real body described in the comment above it. Once all five exercises
are done, the file runs like the reference.

## My output items are in a different order

They should not be — every group is passed through `sorted()` before it is
printed, so the order is fixed and matches the captured output exactly. If
your order differs, you probably returned the raw `set` (which *is* unordered)
instead of `tuple(sorted(...))`. A set has no reliable order; sorting on the
way out is what makes the program deterministic and testable.

## `TypeError: unhashable type: 'list'`

A set (and a dict key) can only hold **hashable** values, and a `list` is not
hashable because it can change. If you try `set([["a"], ["b"]])` or use a list
as a dict key, you get this error. Use tuples for grouped keys — a tuple is
hashable as long as everything inside it is. This is exactly why the program
parses items into tuples.

## `AttributeError: 'tuple' object has no attribute 'common'`

Your `compare()` returned a plain tuple instead of a `SetReport`. Build and
return `SetReport(common=..., only_in_a=..., only_in_b=..., symmetric=...)` so
the caller can use the named fields (`report.common`).

## Quotes: my two lists got split into many arguments

Wrap each list in quotes so the shell passes it as a single argument:
`python3 examples/collections_tool.py "apple,banana" "banana,cherry"`. Without
quotes, a space inside a list would start a new argument and the program would
see the wrong number of arguments.

## Importing the file runs the whole program

This is exactly the problem the main guard prevents. If importing your module
prints a report or exits, you either forgot `if __name__ == "__main__":` or
wrote program-running code at the top level (outside any function). Only the
guarded `sys.exit(main(sys.argv))` should trigger execution — that is what
lets a test import `dedupe` and `compare` without running the report.

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly (as the README shows) rather than executing it
directly: `bash tests/run_tests.sh`. You do not need to `chmod +x` anything.
