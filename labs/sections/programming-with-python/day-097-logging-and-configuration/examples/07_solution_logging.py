#!/usr/bin/env python3
"""Reference answers to exercises 1-6. Read AFTER you have tried them.

This file has the same public names as `starter/01_logging.py`, so
`starter/03_check.sh` can be pointed at either one. The test suite uses that
to prove the checker is not vacuous: it runs the checker against this file and
requires 6 of 6, then against the untouched starter and requires 0 of 6.

The two classes are imported from `examples/applog.py` rather than written
twice, because they are the same code and a second copy would drift.
"""

from __future__ import annotations

import io
import logging
import sys
from pathlib import Path
from typing import Any, Iterable  # noqa: F401  (kept to mirror the starter)

sys.path.insert(0, str(Path(__file__).resolve().parent))

from applog import JsonFormatter, RedactingFilter, iso_utc  # noqa: E402,F401

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


def buffer_handler(level: int, formatter: logging.Formatter):
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler, stream


# --- EXERCISE 1 ------------------------------------------------------------
# getLogger, not Logger(). getLogger returns the SAME object for the same
# name every time, from a module-level registry, which is what makes
# configuring "myapp" configure "myapp.loader" too. Constructing a Logger
# directly bypasses that registry and the object is connected to nothing.
log = logging.getLogger(__name__)


# --- EXERCISE 2 ------------------------------------------------------------
def prepare(records: list[dict], logger: logging.Logger) -> list[dict]:
    logger.info("preparation starting: %d records", len(records))
    kept = []
    for record in records:
        logger.debug("processing record %s", record["id"])
        if not record["text"]:
            logger.warning("skipping record %s: empty text", record["id"])
            continue
        if record["label"] not in VALID_LABELS:
            logger.warning(
                "skipping record %s: unknown label %r", record["id"], record["label"]
            )
            continue
        kept.append(record)
    logger.info("preparation done: kept %d of %d", len(kept), len(records))
    return kept


# --- EXERCISE 3 ------------------------------------------------------------
def make_debug_logger(name: str, handler: logging.Handler) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.filters.clear()
    logger.setLevel(logging.DEBUG)     # gate one: the logger
    handler.setLevel(logging.DEBUG)    # gate two: the handler
    logger.addHandler(handler)
    logger.propagate = False
    return logger


# --- EXERCISE 4 ------------------------------------------------------------
def parse_batch_size(text: str) -> int:
    return int(text)


def log_parse_failure(text: str, logger: logging.Logger) -> bool:
    try:
        parse_batch_size(text)
    except ValueError:
        # exception() is error() with exc_info=True. It reads the exception
        # currently being handled out of the interpreter, so it takes no
        # argument — and it must be called inside the except block.
        logger.exception("could not parse batch size")
        return False
    return True


# --- EXERCISES 5 and 6 -----------------------------------------------------
# Both are in examples/applog.py, imported above and re-exported here under
# the names the checker looks for.
STANDARD_KEYS = frozenset(
    vars(
        logging.LogRecord(
            name="", level=0, pathname="", lineno=0, msg="", args=(), exc_info=None
        )
    )
) | {"message", "asctime", "taskName"}


def main() -> None:
    import json

    handler, stream = buffer_handler(logging.DEBUG, JsonFormatter({"run_id": "run-1"}))
    handler.addFilter(RedactingFilter([SECRET]))
    logger = make_debug_logger("scratch", handler)
    prepare(RECORDS, logger)
    log_parse_failure("sixty-four", logger)
    for line in stream.getvalue().splitlines():
        record = json.loads(line)
        record.pop("traceback", None)
        print(json.dumps(record))


if __name__ == "__main__":
    main()
