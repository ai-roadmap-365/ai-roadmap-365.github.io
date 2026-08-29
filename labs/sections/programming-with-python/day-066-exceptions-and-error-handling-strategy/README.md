# Day 066 lab — Failing Well

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Exceptions and Error Handling Strategy
- **Day number:** 66 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-066-exceptions-and-error-handling-strategy
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-066-exceptions-and-error-handling-strategy` when the site is running.
<!-- generated-links:end -->

## Purpose

You are handed a small file-processing script that never crashes — and that
is the problem. `examples/swallowing.py` wraps its whole body in a bare
`except:` and a `pass`, so a missing file, a bad number, and a missing field
all come out the same way: `done`, exit code 0, and a total that is quietly
wrong. In this lab you rebuild that program's **error strategy** from the
ground up.

You will reproduce and read three real tracebacks; replace the bare handler
with narrow ones plus `try`/`except`/`else`/`finally`; add a custom exception
and re-raise with `from` so the chained traceback keeps the original cause;
write a `@retry` decorator with exponential backoff against a deliberately
flaky operation; and log every failure with `logging.exception` so the full
traceback survives in a file even though the user only sees one clean line.

The whole lab is deterministic: no randomness, no network, no clock reading.
Run it twice and you get identical output both times.

## Learning objectives

- Read a traceback frame by frame and name the exception type, the message,
  and the line that raised it.
- Replace a bare `except:` with handlers that catch only what you can
  actually act on, ordered most-specific-first.
- Use `else` for the code that must run only when nothing raised, and
  `finally` for the cleanup that must run on every path out.
- Define a minimal custom exception and raise it with `raise ... from err`,
  and see the difference `__cause__` makes in the printed traceback.
- Decide *where* to handle: reject a bad record in the loop, let a missing
  file propagate to the boundary, and fail fast when the job cannot continue.
- Write a `@retry` decorator with backoff, retry only errors that a later
  attempt might survive, and give up with the cause preserved.
- Log an exception properly with `logging.exception` and verify what landed
  in the log file.

## Prerequisites

- The Day 66 lesson — read it first; it walks this exact program.
- Day 64 and Day 65: reading and writing files, and JSON in the real world.
- Day 58: functions returning functions (closures and decorators) — the
  `@retry` helper is a plain decorator factory.
- Day 63: designing a small program well (pure core, thin shell).
- A text editor and a terminal. Classes are **not** assumed: the two custom
  exceptions are provided, and the two-line `class MyError(Exception)` form
  is all this lab uses. Classes proper are tomorrow, Day 67.

## Supported operating systems

- **macOS** — fully supported (captured on macOS, Apple Silicon, Python
  3.14.0, bash 3.2.57).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path. Native Windows Python
  raises identical exceptions, but tracebacks print backslash paths and the
  test runner needs `bash`.

## Hardware requirements

Any computer that runs Python 3. The lab reads a few dozen bytes of JSON and
writes a small log file. No special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only: `json`, `logging`, `sys`, `time`, `traceback`.
  Nothing to install. See [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. Exception handling is a language feature and `logging` ships with
Python, so there is nothing to buy and no account to create. The lesson's
Alternatives section covers the paid hosted error-trackers you may meet at
work; none of them is needed here, and none is used.

## Installation

None beyond Python itself:

```bash
cd labs/sections/programming-with-python/day-066-exceptions-and-error-handling-strategy
python3 --version   # confirm Python 3.8+
```

## File structure

```text
day-066-exceptions-and-error-handling-strategy/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── triage.py                   ← YOUR working file (3 numbered exercises)
│   └── traceback-notes.md          ← Exercise 0: record and read three tracebacks
├── examples/
│   ├── raw_triage.py               ← no handling at all — the traceback generator
│   ├── swallowing.py               ← the bare-except anti-pattern (the "before")
│   ├── triage.py                   ← the reference strategy (the "after")
│   ├── dispatch_demo.py            ← @retry recovering, and giving up with chaining
│   └── samples/
│       ├── intake.jsonl            ← five clean records
│       ├── bad-severity.jsonl      ← one record whose severity is "high" (ValueError)
│       └── missing-field.jsonl     ← one record with no severity field (KeyError)
├── tests/
│   └── run_tests.sh                ← behaviour checks: types, chaining, exit codes, log
├── expected-output/
│   ├── tracebacks.txt              ← the three real tracebacks (paths shortened)
│   ├── sample-run.txt              ← a real captured session
│   ├── log-sample.txt              ← what logging.exception wrote
│   ├── test-run.txt                ← a real captured test run
│   └── FIELDS.md                   ← required behaviour on every platform
├── requirements/
│   └── README.md                   ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 0. Reproduce three real failures and read the tracebacks.
python3 examples/raw_triage.py examples/samples/intake.jsonl
python3 examples/raw_triage.py examples/samples/no-such-file.jsonl
python3 examples/raw_triage.py examples/samples/bad-severity.jsonl
python3 examples/raw_triage.py examples/samples/missing-field.jsonl

# 1. See what the bare except costs: the same failures, reported as success.
python3 examples/swallowing.py examples/samples/no-such-file.jsonl ; echo "exit: $?"
python3 examples/swallowing.py examples/samples/bad-severity.jsonl ; echo "exit: $?"

# 2. Now the rebuilt program. Clean input, then each dirty input.
python3 examples/triage.py examples/samples/intake.jsonl        ; echo "exit: $?"
python3 examples/triage.py examples/samples/missing-field.jsonl ; echo "exit: $?"
python3 examples/triage.py examples/samples/no-such-file.jsonl  ; echo "exit: $?"

# 3. Read the log the run left behind: one clean line for the user,
#    the whole chained traceback for you.
python3 examples/triage.py examples/samples/bad-severity.jsonl triage.log
cat triage.log

# 4. Watch @retry back off and recover, then exhaust its attempts
#    and re-raise with the cause preserved.
python3 examples/dispatch_demo.py

# 5. Your turn: fill in starter/traceback-notes.md, then the three
#    exercises in starter/triage.py, then run your version.
python3 starter/triage.py examples/samples/missing-field.jsonl

# 6. Check your work.
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/raw_triage.py <file>` — a reader with no handling
  whatsoever. On a good file it prints a total; on each bad file it lets the
  exception escape, so Python unwinds the stack and prints a real traceback.
  The three files were chosen to raise `FileNotFoundError`, `ValueError`, and
  `KeyError` respectively.
- `python3 examples/swallowing.py <file>` — the same work wrapped in
  `except: pass`. It always prints `done` and always exits 0, even for a file
  that does not exist. `echo "exit: $?"` shows you the exit code so you can
  see the lie.
- `python3 examples/triage.py <file> [logfile]` — the rebuilt program. A bad
  *record* is rejected by name and logged, and the rest of the file is still
  processed (exit 0). A bad *path* is not handled in the loader at all; it
  propagates to `main()`, which reports it and exits 1. With no argument it
  prints usage and exits 2.
- `cat triage.log` — the log `logging.exception` wrote: the message, the full
  traceback, and the chaining line that connects the `RecordError` you raised
  to the `ValueError` that caused it.
- `python3 examples/dispatch_demo.py` — calls a flaky operation that fails
  twice and succeeds on the third attempt (you see the 0.05 s and 0.10 s
  backoff), then an operation that never succeeds, so `@retry` gives up and
  raises `DispatchError` **from** the last `ConnectionError`.
- `bash tests/run_tests.sh` — 29 checks (48 once your starter is complete):
  exception types, `__cause__` chaining, band counting, retry behaviour and
  its delays, end-to-end exit codes, and the contents of the log file. Exits
  0 only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) and
[`expected-output/tracebacks.txt`](expected-output/tracebacks.txt) — real
captured runs. The rebuilt program on a file with a missing field:

```text
$ python3 -u examples/triage.py examples/samples/missing-field.jsonl ; echo "exit: $?"
admitted 2 record(s), rejected 1
immediate  1
urgent     1
routine    0
rejected: line 2: missing field 'severity'
attempt 1 failed (ward system unavailable (call 1)); retrying in 0.05s
attempt 2 failed (ward system unavailable (call 2)); retrying in 0.10s
dispatched 2 record(s) to the ward system
exit: 0
```

And the same program on a file that is not there:

```text
$ python3 -u examples/triage.py examples/samples/no-such-file.jsonl ; echo "exit: $?"
error: no such intake file: examples/samples/no-such-file.jsonl
exit: 1
```

**Your tracebacks will not match ours character for character, and they are
not meant to.** A traceback prints the absolute path of every file in the
stack, so yours show wherever you cloned this repository; the captured files
shorten the lab directory to `<lab>` for readability. What must match is the
exception type, the message, the order of the frames, and the exit code.
`expected-output/FIELDS.md` states exactly that required behaviour, and also
explains the `python3 -u` used when capturing (it keeps stdout and stderr in
terminal order when output is redirected to a file).

## Validation steps

1. `python3 examples/raw_triage.py examples/samples/no-such-file.jsonl`
   ends with `FileNotFoundError: [Errno 2] No such file or directory: ...`
   and exits 1.
2. The same command on `bad-severity.jsonl` ends with
   `ValueError: invalid literal for int() with base 10: 'high'`; on
   `missing-field.jsonl` it ends with `KeyError: 'severity'`.
3. `python3 examples/swallowing.py examples/samples/no-such-file.jsonl; echo $?`
   prints `done` and then `0` — the failure you just saw, made invisible.
4. `python3 examples/triage.py examples/samples/intake.jsonl` prints
   `admitted 5 record(s), rejected 0` and exits 0.
5. `python3 examples/triage.py examples/samples/missing-field.jsonl; echo $?`
   prints `rejected: line 2: missing field 'severity'` to standard error,
   still summarizes the other two records, and exits `0`.
6. `python3 examples/triage.py examples/samples/no-such-file.jsonl; echo $?`
   prints `error: no such intake file: ...` and exits `1`.
7. `python3 examples/triage.py examples/samples/bad-severity.jsonl triage.log`
   then `cat triage.log` shows `ERROR: rejected record on line 2`, a full
   traceback, the line `The above exception was the direct cause of the
   following exception`, and the original `ValueError`.
8. `python3 examples/dispatch_demo.py` shows two backoff lines
   (`0.05s`, `0.10s`), then a success, then a chained `DispatchError`.
9. `starter/traceback-notes.md` is filled in: three tracebacks pasted and
   all the questions answered.
10. Your completed `starter/triage.py` behaves identically to the reference.
11. `bash tests/run_tests.sh` ends with `0 failure(s).` and exits `0`.

## Tests

```bash
bash tests/run_tests.sh
```

While the starter is unfinished the suite tests the reference strictly and
your starter structurally, ending in `29 checks, 0 failure(s).` Once you have
completed all three exercises (no `NotImplementedError` and no bare `except:`
left), it runs your version through the same behavioural checks as the
reference and ends in `48 checks, 0 failure(s).` The command exits 0 on
success and non-zero on any failure, so it can run unattended. A full
captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

The checks test behaviour, not file existence: that the right exception type
comes out of the right input, that `__cause__` carries the original error,
that an out-of-range value raises *without* a cause, that a bad record is
rejected while the rest of the file still processes, that a missing file
exits non-zero, that `retry` sleeps `0.05` then `0.10` and does **not** retry
a `ValueError`, and that the log file really received a chained traceback.

## Cleanup

The lab writes exactly one file, the log:

```bash
rm -f triage.log
```

To reset your work: `git checkout -- starter/triage.py`. The test runner
creates its log files with `mktemp` and removes them itself.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: unfinished
exercises, why your paths differ from the captured ones, missing `~~~^^^`
caret lines on older Pythons, `json.JSONDecodeError` being a subclass of
`ValueError`, a chained traceback that lost its cause, an empty log file,
stdout/stderr ordering, and the test runner's two starter states.

## Security notes

See [security.md](security.md). Short version: the lab makes no network
calls and needs no privileges. Its central point is a security one — a
swallowed exception hides the events you most need to see (a permission
denial, a failed integrity check), a bare `except:` even traps Ctrl-C, an
uncapped retry loop is a load attack on someone else's service, tracebacks in
logs can carry sensitive values, and `assert` is not a validation mechanism
because `-O` deletes it.

## Extension exercises

1. Add a `--strict` mode: a second run mode in which the first `RecordError`
   aborts the whole run with exit 1 instead of being logged and skipped.
   Decide where that decision belongs — the parser, the loop, or `main()` —
   and write one sentence justifying it.
2. Add a `retry_on` parameter to the decorator so the caller passes the tuple
   of exception types to retry, defaulting to
   `(ConnectionError, TimeoutError)`. Add a test proving a type outside the
   tuple propagates on the first attempt.
3. Add jitter to the backoff — a small deterministic offset derived from the
   attempt number, *not* from `random` — and explain in a comment why real
   retry policies randomize delays (to stop many clients retrying in lockstep)
   and why this lab cannot.
4. Replace the two `print(..., file=sys.stderr)` calls in `main()` with
   `logging.error(...)` plus a `logging.StreamHandler`, so one configuration
   controls both the file and the screen. Confirm the tests still pass.
5. Write `tests/test_handlers.py` that imports `triage` and asserts the same
   chaining behaviour with plain `assert` statements, prints
   `all tests passed`, and exits 0 — then explain why those `assert`s are
   fine in a test file but would be wrong as input validation in
   `parse_record`.

## Navigation

- **Previous day:** Day 65 — CSV and JSON in the Real World
  (`labs/sections/programming-with-python/day-065-csv-and-json-in-the-real/`).
- **Next day:** Day 67 — Classes and Objects
  (`labs/sections/programming-with-python/day-067-classes-and-objects/`),
  where the two-line custom exception you used today becomes a class you
  understand completely.
- **Week 10 project:** the Expense Tracker — CSV import/export, category
  handling, and monthly summary reports, where every parse and every file
  read needs exactly the strategy you built here.
