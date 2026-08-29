# Troubleshooting — Day 080 lab

## `NotImplementedError: EXERCISE 3: add the storage group ...`

Working as designed. Each unfinished exercise raises this the moment its code
would have run, so you always know exactly which one you are on. The test
suite counts the remaining ones and tells you:

```text
..  6 exercise(s) still unfinished — the behavioural battery
    will run against starter/notes.py once they are done.
```

Six raises cover eight exercises, because exercises 4, 5 and 6 all live inside
`build_parser` and share one.

## `AttributeError: 'Namespace' object has no attribute 'func'`

You forgot `set_defaults(func=...)` on a subparser, or the user ran a command
with no subcommand at all and your `add_subparsers` call is missing
`required=True`.

The second case is the interesting one. Without `required=True`, running plain
`notes` parses successfully — argparse is happy, there simply is no
subcommand — and then `args.func` explodes. With it, argparse refuses the
command line, prints usage on standard error, and exits 2, which is what a
user deserves. One keyword turns a crash into a usage message.

## `argparse.ArgumentError: argument -h/--help: conflicting option string`

Your parent parser was built without `add_help=False`. A parser gets `-h` by
default; when it is used as a parent, the child inherits that `-h` and then
tries to add its own. Fix it in one place:

```python
parent = argparse.ArgumentParser(add_help=False)
```

## `error: unrecognized arguments: --store /some/path`

You put a shared option before the subcommand — `notes --store x add "hi"` —
but the option is defined on the parent, which the *subparsers* inherit, not
on the root parser. In this lab's design, shared options go after the
subcommand: `notes add "hi" --store x`.

This is a real design decision, not a bug in argparse, and both conventions
exist in the wild (`git --no-pager log` versus `docker run --rm`). Pick one
and be consistent. If you want an option to work in both positions, add it to
the root parser *and* the parent — and be aware that the later one wins, which
surprises people.

## The `--on` value arrives as a string, not a date

You passed `type=iso_date` as a *string*: `type="iso_date"`. It must be the
function object itself, with no quotes and no call parentheses:

```python
add.add_argument("--on", type=iso_date)      # right
add.add_argument("--on", type=iso_date())    # wrong: calls it immediately
add.add_argument("--on", type="iso_date")    # wrong: argparse cannot use a string
```

## My error message shows a full Python traceback

You raised `ValueError` (or let one escape) instead of
`argparse.ArgumentTypeError`. Only `ArgumentTypeError` — and `TypeError` and
`ValueError` raised *inside* a `type=` callable — get converted into a usage
message. An exception raised in your *handler* is not converted at all: catch
it and turn it into a `NotesError`, which `main()` already renders as one
tidy line on standard error with exit 1.

## `notes add -` just sits there doing nothing

Standard input is a terminal and the program is waiting for you to type. Press
Ctrl-D (on a line of its own) to signal end-of-file, or Ctrl-C to give up.

That hang is exactly what exercise 7's terminal detection prevents. Once it is
implemented, `notes add -` with nothing piped in exits 2 with a message
instead of hanging. Try both:

```bash
notes add -                      # detected: exits 2 with an explanation
echo "piped in" | notes add -    # reads from the pipe, exits 0
```

## `--dry-run` prints the right thing but the test still fails

Read the failing check's name. There are two different ones:

- *"leaves the store BYTE-IDENTICAL"* — your code fell through to
  `save_store`. A dry run must `return 0` before the write. Re-indent, or add
  the missing `return`.
- *"puts the ids on stdout, where they can be piped"* — you wrote both lines
  to the same stream. The ids are a result (standard output); the summary is a
  diagnostic (standard error).

## The dry-run and real-remove output arrive in the wrong order

You wrote to standard output and standard error without flushing in between.
When standard output is a terminal Python line-buffers it, so the order looks
right; the moment you redirect to a file it becomes block-buffered and the
unbuffered standard error overtakes it. Call `streams.stdout.flush()` before
writing the diagnostic. This is not cosmetic — it is why captured logs from
build servers so often look scrambled.

## `pytest: command not found`

The suite tells you what to do, but for completeness:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Or point it at an installation you already have:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## `ModuleNotFoundError: No module named 'notes'` from pytest

`tests/conftest.py` puts the right directory on `sys.path`, chosen by the
`NOTES_DIR` environment variable. Run pytest from the **lab directory**, not
from inside `tests/`:

```bash
cd labs/sections/programming-with-python/day-080-building-clis-with-argparse
NOTES_DIR=examples pytest tests -q     # the reference
NOTES_DIR=starter  pytest tests -q     # your work
```

## `notes list --format json | head -2` prints a BrokenPipeError

`head` closes the pipe as soon as it has its two lines, and the writer finds
out the hard way. `main()` already catches `BrokenPipeError` and returns 0,
because a downstream program deciding it has seen enough is not your program's
failure. If you are writing your own tool and see this, catch it in the same
place — do not sprinkle try/except through the renderers.

## Everything passes but the counts differ from `expected-output/test-run.txt`

`test-run.txt` was captured with the starter unfinished: **76 checks**. With
all eight exercises done the battery runs a second time against your file and
the total is **133 checks**. Both are correct; only `0 failure(s).` matters.
