#!/usr/bin/env python3
"""EXERCISES 1-6 — the logging half. Your work goes here.

Check your progress at any time:

    bash starter/03_check.sh

Everything below either works already or raises NotImplementedError with the
exercise number in the message. Nothing is a stub: the two pieces that are
written for you are complete and worth reading, because they show the shape
the rest should take.

Standard library only. `logging` and `json` are already imported.
"""

from __future__ import annotations

import io
import json
import logging
import time
from typing import Any, Iterable

SECRET = "sk-live-9f2c4a7b1e63"  # invented for this lab; not a real credential

VALID_LABELS = {"neutral", "negative", "positive"}

RECORDS = [
    {"id": 1, "text": "the cat sat on the mat", "label": "neutral"},
    {"id": 2, "text": "", "label": "neutral"},
    {"id": 3, "text": "shipping was late and the box was crushed", "label": "negative"},
    {"id": 4, "text": "arrived early, works perfectly", "label": "positive"},
    {"id": 5, "text": "no opinion", "label": "unknown"},
    {"id": 6, "text": "great value for the price", "label": "positive"},
]


# ---------------------------------------------------------------------------
# WRITTEN FOR YOU — read this before starting. It is how the checker captures
# your log output, and it is how you should capture log output in a test.
# ---------------------------------------------------------------------------

def buffer_handler(level: int, formatter: logging.Formatter) -> tuple[logging.Handler, io.StringIO]:
    """A handler that writes into a StringIO, plus the StringIO itself."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler, stream


def iso_utc(epoch_seconds: float) -> str:
    """ISO 8601 in UTC to milliseconds. Written for you; exercise 5 uses it."""
    whole = int(epoch_seconds)
    millis = int(round((epoch_seconds - whole) * 1000))
    if millis == 1000:
        whole += 1
        millis = 0
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(whole)) + f".{millis:03d}Z"


# ---------------------------------------------------------------------------
# EXERCISE 1 — a module-level logger
#
# Replace the None below with the one-line idiom every module in every Python
# program should use to obtain its logger. It must be:
#
#   * obtained from the logging module rather than constructed
#   * named after THIS module, so that the dotted hierarchy works and
#     configuring the parent name configures everything beneath it
#
# The checker asserts that `log.name` equals this module's __name__ and that
# `log` is the same object `logging.getLogger` returns for that name.
# ---------------------------------------------------------------------------

log = None  # EXERCISE 1: one line, and the answer is in the paragraph above


# ---------------------------------------------------------------------------
# EXERCISE 2 — convert the print-based function
#
# `examples/01_prints.py` has the original. Rewrite it here using `logger`
# instead of print, with these severities and no others:
#
#   * "preparation starting: N records"          -> INFO
#   * "processing record N"                      -> DEBUG   (per-record noise)
#   * "skipping record N: empty text"            -> WARNING (survivable)
#   * "skipping record N: unknown label 'x'"     -> WARNING
#   * "preparation done: kept M of N"            -> INFO
#
# Two requirements the checker enforces:
#
#   * use LAZY formatting — logger.info("kept %d of %d", m, n) — and NOT an
#     f-string. The checker inspects `record.msg` and fails if the number has
#     already been baked into the template.
#   * RETURN the kept records. The result of the function is not log output.
#
# The API key must not appear anywhere in this function. It never was the
# log's business.
# ---------------------------------------------------------------------------

def prepare(records: list[dict], logger: logging.Logger) -> list[dict]:
    raise NotImplementedError(
        "EXERCISE 2: convert examples/01_prints.py's prepare() to logging calls"
    )


# ---------------------------------------------------------------------------
# EXERCISE 3 — the two-level trap
#
# Return a logger set up so that a DEBUG call actually comes out.
#
# The trap: a record must pass the LOGGER's level AND then the HANDLER's
# level, and they are two different objects. Setting the logger to DEBUG and
# leaving the handler at WARNING drops every debug line with no error, and
# is the most common logging question there is.
#
# Build a logger named `name` that:
#   * accepts DEBUG at the logger
#   * has exactly one handler, which also accepts DEBUG
#   * does NOT propagate, so the checker's buffer is the only destination
#   * uses the handler and formatter you are given
#
# Return the logger. The caller keeps the stream.
# ---------------------------------------------------------------------------

def make_debug_logger(name: str, handler: logging.Handler) -> logging.Logger:
    raise NotImplementedError(
        "EXERCISE 3: both the logger's level AND the handler's level must pass"
    )


# ---------------------------------------------------------------------------
# EXERCISE 4 — log a failure so somebody can fix it
#
# Call `parse_batch_size(text)` inside a try block. When it raises ValueError,
# log it at ERROR with the message "could not parse batch size" AND the
# traceback attached.
#
# `logger.error(str(error))` loses the traceback, which is the whole value:
# it is the only thing that says which line, in which function, called with
# what. There is a one-word method that does the right thing inside an
# except block, and it takes no exception argument.
#
# Return True if the parse succeeded, False if it was logged as a failure.
# The checker asserts record.exc_info is not None and that the formatted
# output contains the word "Traceback".
# ---------------------------------------------------------------------------

def parse_batch_size(text: str) -> int:
    """Written for you. It raises ValueError on anything that is not an int."""
    return int(text)


def log_parse_failure(text: str, logger: logging.Logger) -> bool:
    raise NotImplementedError(
        "EXERCISE 4: use the method that attaches the traceback automatically"
    )


# ---------------------------------------------------------------------------
# EXERCISE 5 — a JSON formatter
#
# Fill in `format` so each record becomes ONE line of JSON with these keys:
#
#   ts      iso_utc(record.created)   — the helper above does the formatting
#   level   the level NAME, not the number
#   logger  the logger's name
#   event   the FORMATTED message (there is a record method for this; using
#           record.msg would give you the template with %s still in it)
#
# then every key from `self.static_fields`, then every attribute the caller
# added through `extra=`. `STANDARD_KEYS` below tells you which attributes
# the logging module put there itself, so anything NOT in it came from the
# caller and belongs in the output.
#
# The checker parses your lines with json.loads and asserts on the values,
# so key order does not matter and whitespace does not matter.
# ---------------------------------------------------------------------------

STANDARD_KEYS = frozenset(
    vars(
        logging.LogRecord(
            name="", level=0, pathname="", lineno=0, msg="", args=(), exc_info=None
        )
    )
) | {"message", "asctime", "taskName"}


class JsonFormatter(logging.Formatter):
    def __init__(self, static_fields: dict[str, Any] | None = None) -> None:
        super().__init__()
        self.static_fields = dict(static_fields or {})

    def format(self, record: logging.LogRecord) -> str:
        raise NotImplementedError(
            "EXERCISE 5: return one line of JSON with ts, level, logger, event, "
            "the static fields, and everything passed through extra="
        )


# ---------------------------------------------------------------------------
# EXERCISE 6 — a redacting filter
#
# Fill in `filter` so that no known secret VALUE survives on the record.
#
# A filter returns True to keep the record and False to drop it. Mutating the
# record on the way through is allowed, and is what makes redaction possible.
# Three places a secret hides, and the checker tests all three:
#
#   * record.msg      — the message itself, when somebody used an f-string
#   * record.args     — the arguments of a lazy-formatted call
#   * the attributes the caller added through extra=, INCLUDING values nested
#     inside a dict, because {"headers": {"Authorization": "Bearer sk-..."}}
#     is exactly how this happens in real code
#
# Replace each occurrence with self.PLACEHOLDER. Return True.
#
# Where this filter gets ATTACHED matters more than how it is written, and
# the answer is not the obvious one — attach it to each HANDLER. See
# examples/03_structured_logging.py demonstration 2b for the measurement.
# ---------------------------------------------------------------------------

class RedactingFilter(logging.Filter):
    PLACEHOLDER = "***redacted***"

    def __init__(self, secrets: Iterable[str]) -> None:
        super().__init__()
        self.secrets = [s for s in secrets if s]

    def filter(self, record: logging.LogRecord) -> bool:
        raise NotImplementedError(
            "EXERCISE 6: scrub record.msg, record.args and every extra= field, "
            "including values nested inside a dict"
        )


# ---------------------------------------------------------------------------
# A place to try things out. `python3 starter/01_logging.py` runs this.
# ---------------------------------------------------------------------------

def main() -> None:
    handler, stream = buffer_handler(logging.DEBUG, JsonFormatter({"run_id": "run-1"}))
    handler.addFilter(RedactingFilter([SECRET]))
    logger = make_debug_logger("scratch", handler)
    prepare(RECORDS, logger)
    log_parse_failure("sixty-four", logger)
    for line in stream.getvalue().splitlines():
        print(json.dumps(json.loads(line), indent=2))


if __name__ == "__main__":
    main()
