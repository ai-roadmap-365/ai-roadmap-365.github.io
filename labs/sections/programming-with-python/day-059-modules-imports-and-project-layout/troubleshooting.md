# Troubleshooting — Day 059 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old version.
Check with `python3 --version`.

## `No module named wordstats` when I run `python3 -m wordstats`

Python looks for the package on its search path (`sys.path`). When you run
`python3 -m wordstats`, the first entry on that path is the **current
directory**, so you must run the command from the directory that *contains*
the `wordstats/` folder — `examples/` for the reference, `starter/` for your
own version:

```bash
cd examples
python3 -m wordstats sample.txt   # correct: wordstats/ is right here
```

Running it from one level up (where `wordstats/` is not directly present)
gives this error. This is exactly the `sys.path` search the lesson describes.

## The starter raises `NotImplementedError`

That is expected until you finish the exercises. Each unfinished function
raises `NotImplementedError` on purpose so you cannot mistake an empty function
for a working one. Replace each `raise NotImplementedError(...)` line with the
real body described in the comment above it, and uncomment the two imports in
`starter/wordstats/__init__.py` (Exercise 5). Once all six exercises are done,
the package behaves like the reference.

## `ImportError: attempted relative import with no known parent package`

You tried to run a module *inside* the package directly, for example
`python3 wordstats/__main__.py`. A relative import like `from .tokens import
tokenize` only works when the file is imported *as part of the package*. Run
the package instead:

```bash
python3 -m wordstats sample.txt   # right: -m runs it as a package
```

The `-m` form gives the module its parent-package context, so the leading-dot
imports resolve.

## `from wordstats import tokenize` fails with `ImportError`

Until Exercise 5 is done, `starter/wordstats/__init__.py` does not re-export
the submodule names, so the package root exposes nothing to import. Uncomment
the two relative imports in that file. Importing straight from the submodule
(`from wordstats.tokens import tokenize`) works even before Exercise 5, because
that reaches the function in its own module directly.

## A circular-import error mentioning `wordstats`

If you make `tokens.py` import `stats.py` *and* `stats.py` import `tokens.py`,
Python cannot finish loading either one — a circular import. In this design
neither responsibility module imports the other; only `__main__.py` and
`__init__.py` import them. Keep the dependencies pointing one way (entry point
-> responsibility modules), never in a loop.

## `__pycache__` folders appeared

Importing a module makes Python cache a compiled `.pyc` inside `__pycache__`.
The test runner sets `PYTHONDONTWRITEBYTECODE=1` to avoid this; if you imported
by hand and want them gone, delete them: `find . -name __pycache__ -exec rm -rf
{} +`. They are harmless and are normally left out of version control.

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly, as the README shows: `bash tests/run_tests.sh`.
You do not need to `chmod +x` anything.
