# Troubleshooting — Day 060 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old version.
Check with `python3 --version`.

## `No such file or directory` for `sample-data`

Run the commands from the lab directory — the folder that contains
`examples/`, `starter/`, and `sample-data/`. If you are in the repository
root, `cd` into the lab first:

```bash
cd labs/sections/programming-with-python/day-060-a-tour-of-the-standard-library
python3 examples/toolkit.py --dir sample-data
```

## The starter raises `NotImplementedError` when I run it

That is expected until you finish the exercises. Each unfinished function
raises `NotImplementedError` on purpose so you cannot mistake an empty
function for a working one. Replace each `raise NotImplementedError(...)`
line with the real body described in the comment above it. Once all four
exercises are done, the file behaves like the reference.

## `toolkit.py: error: the following arguments are required: --dir`

That message comes from `argparse` itself: `--dir` is required, so you must
say which directory to audit. Argparse prints the usage line and exits with
code **2**, its own convention for usage errors. Add `--dir sample-data`.

## The `generated_at` timestamp is different every time I run it

That is correct, not a bug: `datetime.now()` returns the current moment, so
`generated_at` changes on every run. This is exactly why the tests ignore it
and check only the stable fields (`total_files`, `by_extension`,
`directory`). When you compare two reports, ignore this field or compare the
tallies directly.

## `.CSV` and `.csv` are counted as two different types

You are tallying the suffix without lowercasing it. Use
`Path(item).suffix.lower()` so `.CSV`, `.Csv`, and `.csv` all count together.
The reference does this, and the test suite checks it with a deliberately
uppercase `.CSV` file.

## A file with no extension disappears from the tally

`Path("README").suffix` is an empty string `""`, and an empty key is easy to
lose. Map the empty suffix to a visible label — the reference uses
`Path(item).suffix.lower() or "(none)"` — so files without an extension are
still counted.

## `ModuleNotFoundError: No module named 'toolkit'` in the import check

Python looks for modules on its search path (`sys.path`), which does not
include the `examples/` subfolder by default. The import one-liner adds it
first:

```bash
python3 -c "import sys; sys.path.insert(0, 'examples'); from toolkit import tally_extensions; print(tally_extensions(['a.csv', 'b.csv']))"
```

Run it from the lab directory (the folder that contains `examples/`).

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly, as the README shows: `bash tests/run_tests.sh`.
You do not need to `chmod +x` anything.
