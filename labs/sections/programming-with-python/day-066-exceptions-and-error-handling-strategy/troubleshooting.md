# Troubleshooting — Day 066 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. Check with
`python3 --version`.

## `NotImplementedError: Exercise 1: implement parse_record`

Expected until you finish the exercises in `starter/triage.py`. Each
unfinished piece raises `NotImplementedError` on purpose so you cannot
mistake an empty function for a working one. Replace the placeholder with
the body described in the comment above it.

Notice that `NotImplementedError` reaches you as a *loud* traceback. If you
had wrapped the call in a bare `except:`, your own unfinished code would
have been silently swallowed too — which is exactly the failure mode this
lab is about.

## My traceback shows different file paths from `expected-output/`

That is correct and unavoidable. A traceback prints the absolute path of
every source file in the stack, so yours show wherever you cloned this
repository. The captured files replace the lab directory with `<lab>` to
stay readable. Compare the **exception type**, the **message**, the **order
of the frames**, and the **exit code** — never the paths.

## My traceback has no `~~~^^^` caret lines

You are on Python 3.10 or older. Fine-grained "which sub-expression raised"
carets arrived in Python 3.11. Everything else about the traceback is the
same and every test still passes.

## `ValueError` where I expected a JSON error

`json.JSONDecodeError` is a **subclass of `ValueError`**. Except clauses are
tried top to bottom and the first match wins, so if `except ValueError:`
appears above `except json.JSONDecodeError:`, the broad clause swallows the
narrow one and every malformed line is reported as a bad severity. Put the
most specific clause first.

## `RecordError` is raised but the traceback does not show the original cause

You wrote `raise RecordError(...)` inside the handler without `from err`.
Python still records the original as the *implicit context* and prints
"During handling of the above exception, another exception occurred" — but
`err.__cause__` is `None` and the relationship reads as an accident. Use
`raise RecordError(...) from err` to state that the original error is the
direct cause; then `__cause__` is set and the traceback says
"The above exception was the direct cause of the following exception". The
test `missing field -> RecordError chained from KeyError` checks exactly
this.

## Nothing appears in `triage.log`

Three usual causes:

1. `logging.basicConfig(...)` was never called, or was called *after* the
   first log record. `basicConfig` configures the root logger only once, and
   only if it has no handlers yet.
2. You called `logging.error(...)` instead of `logging.exception(...)`.
   `logging.exception` is the one that attaches the traceback, and it must
   be called from inside an `except` block.
3. You passed a log path in a directory that does not exist. The default is
   `triage.log` in the directory you ran the command from.

## `logging.exception` printed to my screen instead of the file

You called it outside `main()` — for example by importing `triage` and
calling `load_records` directly. Without `basicConfig`, the logging module
falls back to its "last resort" handler, which writes to standard error.
Run through `python3 examples/triage.py ...` to get file logging.

## The retry lines and the summary come out in a strange order

Standard output is block-buffered when it is redirected to a file or a pipe,
while standard error is not, so the two streams can be reordered in a
captured file. In a terminal they interleave correctly. Add `-u`
(`python3 -u examples/triage.py ...`) to make redirected output match, which
is how `expected-output/sample-run.txt` was captured.

## The retry demo takes a moment

`dispatch()` sleeps 0.05 s then 0.10 s before its third, successful attempt —
about 0.15 s in total, on purpose, so you can see backoff happening. The
delays are computed, not random, so they are identical on every run. The
tests replace `sleep` with a function that records the delay instead of
waiting, which is why the whole suite is fast.

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly: `bash tests/run_tests.sh`. You do not need to
`chmod +x` anything.

## The suite says "testing structure only"

`starter/triage.py` still contains `NotImplementedError`, so the runner
checks only that the three functions exist. Finish the exercises and the
suite holds your version to the same 19 behavioural checks as the reference
(29 checks becomes 48).

## `starter has no bare except left: FAIL`

You finished the `NotImplementedError` stubs but a bare `except:` is still
somewhere in `starter/triage.py`. Replace it with the specific exception
types you actually intend to handle.
