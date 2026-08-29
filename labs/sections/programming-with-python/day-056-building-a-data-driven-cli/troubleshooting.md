# Troubleshooting — Day 056 lab

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

## `records.py: error: unrecognized arguments` when I pass `--store`

The global `--store` option must come **before** the subcommand, because it
belongs to the top-level parser, not to `add`/`list`/`find`/`delete`:

```bash
python3 examples/records.py --store demo.json add --name X --email x@example.com   # correct
python3 examples/records.py add --store demo.json --name X --email x@example.com   # wrong
```

This ordering — global options first, then the subcommand and its own
options — is standard for tools built on subcommands (think `git --version`
versus `git commit -m`).

## `error: the following arguments are required: --email` (exit code 2)

That message comes from argparse itself, not from your code: a required
option was missing. Argparse prints the usage line and exits with code
**2** for usage mistakes, which is different from the code **1** this
program uses for its own validation errors (a bad email, an empty name) and
data errors (a corrupt store). Two different failure codes, two different
causes.

## `find` printed nothing and `echo $?` shows `1`

That is correct behaviour, not a bug: `find` returns exit code 1 when
**nothing matches**, and prints the "no records match ..." line to standard
error. A script can use that exit code to decide what to do next. If you
expected a match, check the spelling of your query and which `--field` you
searched (`name` or `email`); the search is case-insensitive but matches a
substring, so `find --field name --query ada` finds "Ada Lovelace".

## `is not valid JSON` when I run any command

The store file exists but its contents are not valid JSON (perhaps you
edited it by hand and left a stray character). Either fix the JSON or delete
the file and start fresh: `rm -f demo.json`. A missing store is fine — the
tool treats it as empty and creates it on the first `add`.

## My edits to the store disappeared / two runs fought over the file

Each `add` and `delete` loads the whole file, changes the list in memory,
and writes the whole file back. If two processes do that at the same time,
the second write can overwrite the first. For this single-user lab that is
not a concern, but it is why real multi-user tools reach for a database — a
point the lesson makes.

## `ModuleNotFoundError: No module named 'records'` in the import check

Python looks for modules on its search path (`sys.path`), which does not
include the `examples/` subfolder by default. The import one-liners add it
first:

```bash
python3 -c "import sys; sys.path.insert(0, 'examples'); from records import next_id; print(next_id([]))"
```

Run it from the lab directory (the folder that contains `examples/`).

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly, as the README shows: `bash tests/run_tests.sh`.
You do not need to `chmod +x` anything.
