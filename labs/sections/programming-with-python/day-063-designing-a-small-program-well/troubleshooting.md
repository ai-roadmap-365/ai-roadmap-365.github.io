# Troubleshooting — Day 063 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old version.
Check with `python3 --version`.

## The starter raises `NotImplementedError` when I run it

That is expected until you finish the three exercises in
`starter/summary_core.py`. Each unfinished function raises
`NotImplementedError` on purpose so you cannot mistake an empty function for
a working one. Replace each `raise NotImplementedError(...)` line with the
real body described in the comment above it. Once all three exercises are
done, the tool runs and the test suite holds your core to the same strict
standard as the reference.

## `ModuleNotFoundError: No module named 'summary_core'`

The shell (`summary.py`) imports the core (`summary_core.py`) that sits
next to it. When you run `python3 examples/summary.py`, Python puts the
`examples/` directory on its import path automatically, so the import
works. This error usually means you moved one file without the other, or
tried to import the core from a directory that has no `summary_core.py`.
Keep the core and its shell in the same directory, and run the shell by its
path (`python3 examples/summary.py`, `python3 starter/summary.py`).

To call the core directly from another directory, put its folder on the
path yourself:

```bash
PYTHONPATH=examples python3 -c "import summary_core as c; print(c.summarize([1, 2, 3]))"
```

## `find`... wait, this tool has no subcommands

Correct — this is deliberately smaller than the Day 56 Records CLI. It has
no `argparse` and no subcommands; it reads one stream of numbers and prints
one summary. The lesson is about *design*, so the tool is kept minimal on
purpose (that is YAGNI in action). The Week 9 project, the Flashcard Study
App, is where you scale this same core/shell split up to a multi-command
program.

## `error: 'x' is not a number`

One of the tokens in your input is not a number. `parse_numbers` rejects
the first non-numeric token by name and the shell exits with code 1. Check
the input for stray words, letters, or symbols. Commas, spaces, tabs, and
newlines are all fine as separators; anything that is not a number between
them is not.

## `error: cannot summarize an empty list of numbers`

You gave the tool no numbers at all (an empty file, or you pressed
Ctrl-D on an empty standard input). A summary of nothing has no meaning, so
the core raises `ValueError` and the shell exits 1. Provide at least one
number.

## The summary shows `mean       5.00` but I expected `5`

Real-valued statistics (total, mean, minimum, maximum) are formatted to two
decimal places with `:.2f`, so a whole number shows as `5.00`. The counts
(count, above mean) are integers and print with no decimals. This is a
formatting choice in `format_summary`; change the format string there if
you want different precision (a good refactor exercise).

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly, as the README shows: `bash tests/run_tests.sh`.
You do not need to `chmod +x` anything.
