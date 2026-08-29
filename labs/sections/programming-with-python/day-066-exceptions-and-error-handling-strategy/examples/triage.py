#!/usr/bin/env python3
"""triage.py — the same intake reader, with a real error-handling strategy.

The strategy, stated in one place so you can check the code against it:

  * A record that cannot be read is an EXPECTED condition. It is rejected by
    name, logged with its full traceback, and the rest of the file is still
    processed. That is a decision the record loop can actually make.
  * A missing or unreadable intake FILE is a boundary failure. The loader
    does not catch it; it propagates to main(), which reports it and exits
    non-zero. Fail fast where the program can no longer do its job.
  * A transient dispatch failure is retried with backoff. When the retries
    are exhausted the helper raises DispatchError FROM the last underlying
    error, so the traceback keeps the real cause.
  * Nothing is ever caught and silently discarded.

    python3 examples/triage.py examples/samples/intake.jsonl
    python3 examples/triage.py examples/samples/bad-severity.jsonl
    python3 examples/triage.py examples/samples/no-such-file.jsonl ; echo "exit: $?"
"""

import json
import logging
import sys
import time

# Two custom exceptions. A custom exception is just a class that inherits
# from Exception; the two-line form below is the whole of it. Classes get
# their own lesson tomorrow (Day 67) — for today this minimal form is all
# you need, and all you should write.


class RecordError(Exception):
    """One intake record could not be admitted."""


class DispatchError(Exception):
    """Hand-off to the ward system failed after every retry."""


# ---------------------------------------------------------------- pure core


def parse_record(line, line_number):
    """Turn one line of JSON into a validated record dict.

    Returns {"id": str, "severity": int}. Raises RecordError — chained from
    the underlying error with `from` — when the line cannot be used.

    The except clauses are tried in order, so json.JSONDecodeError must come
    before ValueError: JSONDecodeError is a SUBCLASS of ValueError, and the
    broader clause would otherwise shadow it.
    """
    try:
        raw = json.loads(line)
        record = {"id": raw["id"], "severity": int(raw["severity"])}
    except json.JSONDecodeError as err:
        raise RecordError(f"line {line_number}: not valid JSON") from err
    except TypeError as err:
        raise RecordError(f"line {line_number}: expected a JSON object") from err
    except KeyError as err:
        raise RecordError(f"line {line_number}: missing field {err.args[0]!r}") from err
    except ValueError as err:
        raise RecordError(f"line {line_number}: severity is not a whole number") from err
    else:
        # The `else` block holds the code that must run ONLY when the try
        # block raised nothing. Keeping it out of `try` means a KeyError
        # raised by this range check can never be mistaken for a parse error.
        if not 1 <= record["severity"] <= 5:
            raise RecordError(
                f"line {line_number}: severity {record['severity']} is outside 1-5"
            )
        return record


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

    Only ConnectionError and TimeoutError are retried: they are the errors
    that a later attempt might genuinely survive. A ValueError would fail
    identically forever, so retrying it would only waste time.

    After `attempts` failures the last error is re-raised as DispatchError
    using `raise ... from err`, so the traceback still names the real cause.
    """

    def decorate(function):
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, attempts + 1):
                try:
                    return function(*args, **kwargs)
                except (ConnectionError, TimeoutError) as err:
                    last_error = err
                    if attempt == attempts:
                        break
                    delay = base_delay * (2 ** (attempt - 1))
                    print(
                        f"attempt {attempt} failed ({err}); retrying in {delay:.2f}s",
                        file=sys.stderr,
                    )
                    sleep(delay)
            raise DispatchError(
                f"{function.__name__} gave up after {attempts} attempts"
            ) from last_error

        wrapper.__name__ = function.__name__
        wrapper.__doc__ = function.__doc__
        return wrapper

    return decorate


# A deliberately flaky stand-in for a network call. It is DETERMINISTIC on
# purpose: a list records how many times it has been called in this process,
# so it fails exactly twice and then succeeds, every single run.
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

    Opens a file, so it is part of the shell, not the core. A bad RECORD is
    handled here because here we can do something about it: reject it, log
    it, and keep going. A bad PATH is NOT handled here — FileNotFoundError
    and PermissionError propagate to the caller, which is the only level
    that can decide the program is over.
    """
    records = []
    problems = []
    handle = open(path, "r", encoding="utf-8")
    try:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(parse_record(line, line_number))
            except RecordError as err:
                # logging.exception records the message AND the full chained
                # traceback, at ERROR level. Only ever call it from inside an
                # except block: it reads the exception currently being handled.
                logging.exception("rejected record on line %d", line_number)
                problems.append(str(err))
    finally:
        # finally runs whether the loop finished, returned, or raised, so the
        # file handle is closed on every path out of this function.
        handle.close()
    return records, problems


def main(argv):
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
        # Handled here, at the boundary, because here we can do something:
        # tell the operator which file, and stop with a non-zero exit code.
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
        # Runs even on the `return 1` above and even on an unhandled error.
        logging.shutdown()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
