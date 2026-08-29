#!/usr/bin/env python3
"""starter/triage.py — YOUR working file: rebuild the error strategy.

The program in examples/swallowing.py "works": it never crashes, it always
prints "done", and it always exits 0. It is also useless, because it hides
every failure — a missing file, a bad number, a missing field, all reported
as success. Your job is to give the same program a real strategy.

The design decisions are already made for you and written into the
docstrings below. Fill in the three numbered exercises so the program keeps
those promises. `main()` is provided complete — read it, do not edit it: it
shows where a boundary failure is handled and why `finally` is there.

Work in this order:

  Exercise 0  reproduce the three tracebacks (see starter/traceback-notes.md)
  Exercise 1  parse_record  — narrow handlers, `else`, and `raise ... from`
  Exercise 2  load_records  — try/finally, and logging.exception
  Exercise 3  retry         — a decorator with backoff that re-raises chained

Then run:  bash tests/run_tests.sh
"""

import json
import logging
import sys
import time

# Two custom exceptions, provided. A custom exception is just a class that
# inherits from Exception; this two-line form is the whole of it. Classes get
# their own lesson tomorrow (Day 67) — today you only USE these two.


class RecordError(Exception):
    """One intake record could not be admitted."""


class DispatchError(Exception):
    """Hand-off to the ward system failed after every retry."""


# ---------------------------------------------------------------- pure core


def parse_record(line, line_number):
    """Turn one line of JSON into a validated record dict.

    Returns {"id": <the id>, "severity": <int 1-5>}.
    Raises RecordError, chained from the underlying error, when the line
    cannot be used.
    """
    # Exercise 1: NARROW HANDLERS, `else`, AND CHAINING.
    #
    # 1. In a `try` block, decode and build the record:
    #        raw = json.loads(line)
    #        record = {"id": raw["id"], "severity": int(raw["severity"])}
    #
    # 2. Add FOUR except clauses, each catching one specific thing and
    #    re-raising RecordError with `from err` so the cause is preserved:
    #        except json.JSONDecodeError as err:
    #            raise RecordError(f"line {line_number}: not valid JSON") from err
    #        except TypeError as err:      -> "expected a JSON object"
    #        except KeyError as err:       -> f"missing field {err.args[0]!r}"
    #        except ValueError as err:     -> "severity is not a whole number"
    #
    #    ORDER MATTERS. Clauses are tried top to bottom and the first match
    #    wins, and json.JSONDecodeError is a SUBCLASS of ValueError — so if
    #    you put ValueError first it will shadow the JSON clause and every
    #    malformed line will be reported as a bad severity.
    #
    # 3. Add an `else:` block. Code that must run only when the try block
    #    raised NOTHING belongs there, not in the try:
    #        if not 1 <= record["severity"] <= 5:
    #            raise RecordError(f"line {line_number}: severity "
    #                              f"{record['severity']} is outside 1-5")
    #        return record
    #    (Note this one is raised WITHOUT `from`: there is no underlying
    #     error to chain — the value is simply out of range.)
    raise NotImplementedError("Exercise 1: implement parse_record")


def band(severity):
    """Map a 1-5 severity to a triage band. Pure; 1 is the most urgent."""
    if severity <= 2:
        return "immediate"
    if severity <= 4:
        return "urgent"
    return "routine"


def summarize(records):
    """Count records per triage band. Pure: a list in, a dict out."""
    counts = {"immediate": 0, "urgent": 0, "routine": 0}
    for record in records:
        counts[band(record["severity"])] += 1
    return counts


# ------------------------------------------------------- the retry helper


def retry(attempts=3, base_delay=0.05, sleep=time.sleep):
    """Return a decorator that retries a callable with exponential backoff.

    After `attempts` failures, raise DispatchError FROM the last error.
    """
    # Exercise 3: A RETRY DECORATOR (a plain decorator factory — Day 58).
    #
    # def decorate(function):
    #     def wrapper(*args, **kwargs):
    #         last_error = None
    #         for attempt in range(1, attempts + 1):
    #             try:
    #                 return function(*args, **kwargs)
    #             except (ConnectionError, TimeoutError) as err:
    #                 # Retry ONLY errors a later attempt might survive.
    #                 # A ValueError would fail identically forever.
    #                 last_error = err
    #                 if attempt == attempts:
    #                     break
    #                 delay = base_delay * (2 ** (attempt - 1))
    #                 print(f"attempt {attempt} failed ({err}); "
    #                       f"retrying in {delay:.2f}s", file=sys.stderr)
    #                 sleep(delay)
    #         raise DispatchError(
    #             f"{function.__name__} gave up after {attempts} attempts"
    #         ) from last_error
    #     wrapper.__name__ = function.__name__
    #     wrapper.__doc__ = function.__doc__
    #     return wrapper
    # return decorate
    #
    # Type it out rather than pasting it: the shape (factory -> decorate ->
    # wrapper) is the part worth remembering.
    #
    # Replace the placeholder below with your version.
    def decorate(function):
        def wrapper(*args, **kwargs):
            raise NotImplementedError("Exercise 3: implement the retry decorator")

        return wrapper

    return decorate


# Deterministic stand-ins for a network call: a list counts the calls made in
# this process, so dispatch() fails exactly twice and then succeeds, and
# dispatch_offline() never succeeds. No randomness, so output never varies.
_DISPATCH_CALLS = []


@retry(attempts=3, base_delay=0.05)
def dispatch(counts):
    """Hand the summary to the ward system. Fails twice, then succeeds."""
    _DISPATCH_CALLS.append(1)
    if len(_DISPATCH_CALLS) < 3:
        raise ConnectionError(f"ward system unavailable (call {len(_DISPATCH_CALLS)})")
    return f"dispatched {sum(counts.values())} record(s) to the ward system"


@retry(attempts=3, base_delay=0.05)
def dispatch_offline(counts):
    """A ward system that is simply down. Every attempt fails."""
    raise ConnectionError("offline ward system never answers")


# ------------------------------------------------------ imperative shell


def load_records(path):
    """Read every line of `path`; return (records, problems).

    A bad RECORD is handled here, because here we can do something about it:
    reject it, log it, and carry on with the rest of the file. A bad PATH is
    NOT handled here — it must propagate to main(), the only level that can
    decide the whole run is over.
    """
    records = []
    problems = []
    handle = open(path, "r", encoding="utf-8")
    # Exercise 2: try/finally AND logging.exception.
    #
    # 1. Wrap the loop below in `try:` ... `finally: handle.close()` so the
    #    file is closed on every path out of this function — normal end,
    #    early return, or an exception on the way through.
    #
    # 2. Inside the loop, wrap the parse_record call in its own try/except
    #    that catches ONLY RecordError (never a bare except, never
    #    `except Exception`), and in the handler:
    #        logging.exception("rejected record on line %d", line_number)
    #        problems.append(str(err))
    #    logging.exception writes the message AND the full chained traceback
    #    at ERROR level. Call it only from inside an except block — it reads
    #    the exception currently being handled.
    #
    # Replace the loop below with your version.
    for line_number, line in enumerate(handle, start=1):
        line = line.strip()
        if not line:
            continue
        records.append(parse_record(line, line_number))
    handle.close()
    return records, problems


def main(argv):
    """Provided complete — read it, do not edit it."""
    if len(argv) < 2:
        print("usage: python3 triage.py <records.jsonl> [logfile]", file=sys.stderr)
        return 2
    path = argv[1]
    log_path = argv[2] if len(argv) > 2 else "triage.log"
    logging.basicConfig(
        filename=log_path,
        filemode="w",
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    try:
        records, problems = load_records(path)
    except FileNotFoundError as err:
        print(f"error: no such intake file: {err.filename}", file=sys.stderr)
        logging.exception("intake file missing")
        return 1
    except PermissionError as err:
        print(f"error: cannot read intake file: {err.filename}", file=sys.stderr)
        logging.exception("intake file unreadable")
        return 1
    else:
        counts = summarize(records)
        print(f"admitted {len(records)} record(s), rejected {len(problems)}")
        for name in ("immediate", "urgent", "routine"):
            print(f"{name:<10} {counts[name]}")
        for problem in problems:
            print(f"rejected: {problem}", file=sys.stderr)
        try:
            print(dispatch(counts))
        except DispatchError as err:
            print(f"error: {err}", file=sys.stderr)
            logging.exception("dispatch failed")
            return 1
        logging.info("run complete: %d admitted, %d rejected", len(records), len(problems))
        return 0
    finally:
        logging.shutdown()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
