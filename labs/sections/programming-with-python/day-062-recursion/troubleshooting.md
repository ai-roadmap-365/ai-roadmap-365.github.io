# Troubleshooting — Day 062 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old version.
Check with `python3 --version`.

## The starter raises `NotImplementedError` when I run it

That is expected until you finish the exercises. Each unfinished function
raises `NotImplementedError` on purpose so you cannot mistake an empty
function for a working one. Replace each `raise NotImplementedError(...)`
line with the real body described in the comment above it. Once all five
exercises are done, the file behaves like the reference.

## `RecursionError: maximum recursion depth exceeded`

This is the single most important error to understand in this lab. It means a
function called itself so many times that it filled the **call stack** — the
memory the interpreter uses to remember every unfinished call. There are two
common causes:

1. **A missing or wrong base case.** If `factorial` never hits `n <= 1`, or
   `list_sum` never hits the empty list, the calls never stop and the stack
   overflows. Check that every recursive call moves *toward* the base case
   (smaller `n`, a shorter list).
2. **Genuinely very deep input.** Even a correct function can exceed Python's
   default limit (about 1000 frames) on input nested thousands of levels
   deep. The tool catches this and prints a clear message with exit code 1.
   You can raise the ceiling with `sys.setrecursionlimit(10000)`, but for very
   deep data an iterative solution (a loop with an explicit stack) is usually
   the better fix — Python does not optimize deep recursion away.

## `fib --n 40` seems to hang

That is the lesson made visible: **naive** Fibonacci is exponential.
`fib_naive(40)` makes over 300 million calls, which takes a long time. The
memoized version returns instantly. If you want a large Fibonacci number, that
gap is exactly why memoization exists — press Ctrl+C to stop, and try a
smaller `n` (say 30) to see the call-count report.

## `find`/`flatten` printed `error: --data is not valid JSON`

The `--data` you passed is not valid JSON. Common causes: an unclosed bracket
(`[1, 2`), single quotes instead of double quotes inside the JSON, or the
shell eating your quotes. Wrap the whole JSON value in single quotes so the
shell passes it through unchanged:

```bash
python3 examples/recursion.py treesum --data '{"a": 1, "b": [2, 3]}'
```

## `sum --values` rejects my input

`--values` must be a comma-separated list of integers, e.g. `1,2,3,4`. Spaces
inside the list, or non-numbers (`1,x,3`), are rejected with a clear message
and exit code 1. Quote the value if it contains spaces.

## `error: the following arguments are required: --n` (exit code 2)

That message comes from argparse itself, not from the recursive code: a
required option was missing. Argparse prints the usage line and exits with
code **2** for usage mistakes, which is different from the code **1** this
program uses for its own validation errors (a negative factorial, bad JSON).

## `ModuleNotFoundError: No module named 'recursion'` in the import check

Python looks for modules on its search path (`sys.path`), which does not
include the `examples/` subfolder by default. The import one-liners add it
first:

```bash
python3 -c "import sys; sys.path.insert(0, 'examples'); from recursion import factorial; print(factorial(5))"
```

Run it from the lab directory (the folder that contains `examples/`).

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly, as the README shows: `bash tests/run_tests.sh`.
You do not need to `chmod +x` anything.
