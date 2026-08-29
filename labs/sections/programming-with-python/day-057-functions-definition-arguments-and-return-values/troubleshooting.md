# Troubleshooting — Day 057 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old version.
Check with `python3 --version`.

## The starter raises `NotImplementedError` when I import or test it

That is expected until you finish the exercises. Each unfinished function
raises `NotImplementedError` on purpose so you cannot mistake an empty
function for a working one. Replace each `raise NotImplementedError(...)`
line with the real body described in the comment above it. Once all six
exercises are done, the file behaves like the reference and the test suite
holds it to the full standard.

## `ModuleNotFoundError: No module named 'library'`

Python looks for modules on its search path (`sys.path`), which does not
include the `examples/` or `starter/` subfolder by default. Import checks add
it first, exactly as the tests and `demo.py` do:

```bash
python3 -c "import sys; sys.path.insert(0, 'examples'); import library; print(library.word_count('a b c'))"
```

Run it from the lab directory (the folder that contains `examples/`).

## My function prints the answer but the test still fails

A test calls your function and checks its **return value** — it never reads
what you print. A function that `print`s but does not `return` hands back
`None`, so `word_count("a b") == 2` is `None == 2`, which is false. Fix:
`return` the value; let the *caller* (like `demo.py`) do the printing. This
is the whole point of the "return a value, do not print" rule.

## `celsius_to_fahrenheit(100)` gives `212` but the test wants `212.0`

Both are equal in Python (`212 == 212.0` is `True`), so the test passes. The
reference returns a float because the formula divides by 5; if you wrote
`* 9 // 5` (floor division) you would get a wrong integer. Use `* 9 / 5 + 32`.

## `tally` remembers items from a previous call

You almost certainly wrote `def tally(items, counts={})`. That empty dict is
created **once**, when the function is defined, and is shared by every call,
so it accumulates across calls — the mutable-default-argument trap. Fix: use
`def tally(items, counts=None)` and build a fresh dict inside the body, as
Exercise 6 describes.

## `summarize` returns five separate things and I cannot capture them

`summarize` returns one object — a **tuple** of five values. Capture it whole
(`result = summarize(data)`) or unpack it in one line:

```bash
python3 -c "import sys; sys.path.insert(0,'examples'); from library import summarize; c,t,lo,hi,avg = summarize([2,4,6]); print(c, t, lo, hi, avg)"
```

The number of names on the left must match the length of the tuple, or Python
raises `ValueError: too many values to unpack`.

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly, as the README shows: `bash tests/run_tests.sh`.
You do not need to `chmod +x` anything.
