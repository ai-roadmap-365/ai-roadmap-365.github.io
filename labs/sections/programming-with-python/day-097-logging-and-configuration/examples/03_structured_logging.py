#!/usr/bin/env python3
"""Structured logging as JSON, and a redacting filter that is actually tested.

    python3 examples/03_structured_logging.py

Two ideas, and the second one is the security lesson of the day.

**A log you cannot parse is a log nobody will query.** Free-text log lines are
readable by one person looking at one file. The moment there are ten thousand
of them across four machines, the question stops being "read this" and becomes
"count the ERRORs from run 4711 grouped by event", and that is a query. A query
needs fields. One JSON object per line gives you fields for the price of a
formatter subclass.

**A secret in a log line is a real incident.** Not a lint failure — an
incident, with a rotation, a disclosure conversation, and an audit of
everywhere that log was copied to. This script builds a filter that removes
known secret values, then proves the secret is absent from the captured output
rather than asserting that it should be.

Both pieces live in `examples/applog.py` so they can be imported. This file
demonstrates and explains them.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from applog import JsonFormatter, RedactingFilter, buffer_handler  # noqa: E402

LAB_DIR = Path(__file__).resolve().parent.parent
RUN_ID = "run-4711"
API_KEY = "sk-live-9f2c4a7b1e63"  # invented for this lab; not a real credential


def sanitize(text: str) -> str:
    """Rewrite this lab's absolute path to <lab> before PRINTING captured logs.

    A rendered traceback contains the absolute path of the file it came from,
    which is different on every machine. Only the printing is affected: the
    assertions in tests/run_tests.sh run against the unmodified text.
    """
    return text.replace(str(LAB_DIR), "<lab>")


def banner(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def build_logger(name: str, secrets: list[str] | None = None, on_logger: bool = False):
    """A logger with one JSON handler, and optionally a redacting filter.

    `on_logger` chooses where the filter is attached — on the handler (the
    correct answer) or on the logger (the answer that looks correct and has a
    hole in it). Demonstration 2 uses both, to show the difference.
    """
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.filters.clear()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    handler, stream = buffer_handler(
        logging.DEBUG, JsonFormatter(static_fields={"run_id": RUN_ID})
    )
    if secrets:
        if on_logger:
            logger.addFilter(RedactingFilter(secrets))
        else:
            handler.addFilter(RedactingFilter(secrets))
    logger.addHandler(handler)
    return logger, stream


def demo_json() -> None:
    banner("1. One JSON object per line, with fields you can query")

    log, stream = build_logger("json.demo")
    log.info("run started", extra={"model": "small-encoder", "seed": 7})
    log.info("batch complete", extra={"batch": 1, "records": 64, "kept": 61})
    log.info("batch complete", extra={"batch": 2, "records": 64, "kept": 64})
    log.warning("upstream slow", extra={"attempt": 2, "status": 429})
    try:
        int("sixty-four")
    except ValueError:
        log.exception("could not parse batch size", extra={"batch": 3})
    log.info("run finished", extra={"kept_total": 125})

    lines = [line for line in stream.getvalue().splitlines() if line.strip()]
    print(f"{len(lines)} lines of JSON. Here are the first two, pretty-printed")
    print("for reading only — the real output is one object per line:")
    for line in lines[:2]:
        print(json.dumps(json.loads(line), indent=2))

    print()
    print("Now the point. That is a queryable table, so query it — with the")
    print("standard library, no log platform involved:")
    records = [json.loads(line) for line in lines]

    kept = sum(r.get("kept", 0) for r in records if r["event"] == "batch complete")
    print(f"  records kept across all batches: {kept}")

    by_level: dict[str, int] = {}
    for record in records:
        by_level[record["level"]] = by_level.get(record["level"], 0) + 1
    print(f"  lines by level: {by_level}")

    failures = [r for r in records if r["level"] == "ERROR"]
    print(f"  the failure: event={failures[0]['event']!r} "
          f"exc_type={failures[0]['exc_type']!r} batch={failures[0]['batch']}")
    print(f"  every line carries run_id={records[0]['run_id']!r}, "
          f"so this run separates from every other run")

    print()
    print("Three things earned their place there. `event` is the unformatted")
    print("message, so 'batch complete' groups across every batch. `run_id` is")
    print("a static field on the formatter, so it is stamped on every line")
    print("without any call site remembering it. And the traceback is its own")
    print("field rather than being glued onto the message, so a parser does")
    print("not have to guess where one ends and the other begins.")

    print()
    print("What it costs, stated honestly: JSON logs are unpleasant to read")
    print("with your eyes. The usual answer is JSON to the file or the")
    print("collector and a human-readable formatter on the console — the same")
    print("records, two handlers, two formatters. Demonstration 05 does that.")


def demo_redaction() -> None:
    banner("2. The redacting filter, and the proof that it worked")

    print("First, without the filter. This is what a careless line does:")
    log, stream = build_logger("redact.without")
    log.info("calling upstream with key %s", API_KEY)
    leaked = stream.getvalue().strip()
    print(f"  {leaked}")
    print(f"  the secret appears in that line: {API_KEY in leaked}")

    print()
    print("Now with the filter attached to the logger, and four different")
    print("routes by which a secret tries to get out:")
    log, stream = build_logger("redact.with", secrets=[API_KEY])

    log.info("calling upstream with key %s", API_KEY)          # via an argument
    log.info(f"hard-coded into the message: {API_KEY}")        # via the message
    log.info("config loaded", extra={"api_key": API_KEY})      # via extra=
    log.info("headers built", extra={"headers": {"Authorization": f"Bearer {API_KEY}"}})
    try:
        raise RuntimeError(f"upstream rejected key {API_KEY}")
    except RuntimeError:
        log.exception("request failed")                        # via an exception

    text = stream.getvalue()
    for line in sanitize(text).splitlines():
        print(f"  {line}")

    print()
    appears = API_KEY in text
    print(f"  the secret appears anywhere in that output: {appears}")
    print(f"  the placeholder appears: {RedactingFilter.PLACEHOLDER in text}")

    print()
    print("Four of the five routes are closed. Read the fifth one carefully,")
    print("because it is the honest limit of this technique:")
    exc_lines = [json.loads(line) for line in text.splitlines()
                 if json.loads(line)["level"] == "ERROR"]
    still_there = API_KEY in json.dumps(exc_lines[0])
    print(f"  the secret survives inside the traceback field: {still_there}")
    print()
    print("The filter rewrites `record.msg`, `record.args` and the fields you")
    print("passed through `extra=`. It does NOT rewrite the traceback, because")
    print("the traceback is rendered later, by the FORMATTER, out of the")
    print("exc_info tuple — after every filter has already run. A secret that")
    print("is inside an exception message therefore walks straight past a")
    print("filter that only touches the record.")
    print()
    print("There are two fixes and one rule.")
    print("  Fix one: scrub in the formatter as well as the filter, so the")
    print("           rendered traceback is scrubbed too.")
    print("  Fix two: never put a credential in an exception message. This is")
    print("           the better fix, because it removes the secret from the")
    print("           exception object rather than from one of its renderings.")
    print("  The rule: a redacting filter is a seatbelt. It is not permission")
    print("           to drive at a wall. Do not log the secret.")


def demo_where_the_filter_goes() -> None:
    banner("2b. WHERE the filter goes, and the hole nobody expects")

    print("The filter above is attached to the HANDLER. The obvious")
    print("alternative is to attach it to the application's top logger and")
    print("let the whole tree inherit the protection. That does not work, and")
    print("here is the measurement rather than the claim.")
    print()

    log, stream = build_logger("leak.demo", secrets=[API_KEY], on_logger=True)
    log.info("logged directly on leak.demo: key=%s", API_KEY)
    child = logging.getLogger("leak.demo.loader")
    child.handlers.clear()
    child.filters.clear()
    child.setLevel(logging.NOTSET)
    child.propagate = True
    child.info("logged on the CHILD leak.demo.loader: key=%s", API_KEY)

    for line in sanitize(stream.getvalue()).splitlines():
        print(f"  {line}")
    print()
    lines = stream.getvalue().splitlines()
    print(f"  the direct line leaked: {API_KEY in lines[0]}")
    print(f"  the child's line leaked: {API_KEY in lines[1]}")
    print()
    print("A logger's filters run only for records logged through THAT logger")
    print("object. A record that arrives by propagation from a descendant")
    print("skips every ancestor's filters — propagation consults the")
    print("ancestors' HANDLERS, not their filters. Since every module in a")
    print("well-behaved application calls getLogger(__name__) and is therefore")
    print("a descendant, a filter on the top logger protects almost nothing")
    print("while looking like it protects everything.")
    print()
    print("Attach redaction to each HANDLER. A handler sees everything that")
    print("reaches its destination, from anywhere in the tree.")

    log, stream = build_logger("safe.demo", secrets=[API_KEY], on_logger=False)
    child = logging.getLogger("safe.demo.loader")
    child.handlers.clear()
    child.filters.clear()
    child.setLevel(logging.NOTSET)
    child.propagate = True
    child.info("logged on the CHILD safe.demo.loader: key=%s", API_KEY)
    print()
    print(f"  {sanitize(stream.getvalue()).strip()}")
    print(f"  the child's line leaked: {API_KEY in stream.getvalue()}")


def demo_formatter_scrubbing() -> None:
    banner("3. Closing the traceback hole: scrub in the formatter too")

    class ScrubbingJsonFormatter(JsonFormatter):
        """JsonFormatter that runs the redactor over the finished line.

        This is the belt to the filter's braces. It works because it happens
        last: by the time `format` returns, the traceback has already been
        rendered into text, so scrubbing the text catches it.
        """

        def __init__(self, secrets, **kwargs):
            super().__init__(**kwargs)
            self._redactor = RedactingFilter(secrets)

        def format(self, record: logging.LogRecord) -> str:
            return self._redactor.scrub(super().format(record))

    logger = logging.getLogger("redact.formatter")
    logger.handlers.clear()
    logger.filters.clear()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    handler, stream = buffer_handler(
        logging.DEBUG, ScrubbingJsonFormatter([API_KEY], static_fields={"run_id": RUN_ID})
    )
    logger.addHandler(handler)

    try:
        raise RuntimeError(f"upstream rejected key {API_KEY}")
    except RuntimeError:
        logger.exception("request failed")

    text = stream.getvalue()
    print(f"  the secret appears anywhere in that output: {API_KEY in text}")
    print(f"  the traceback is still there and still useful: "
          f"{'RuntimeError' in text}")
    print()
    print("  the first 200 characters of the line:")
    print(f"  {sanitize(text)[:200]}")
    print()
    print("Cost of this belt: every log line now runs a substring search per")
    print("known secret. That is cheap, and it is not free. The reason to do")
    print("it anyway is that the failure it prevents is not proportional to")
    print("its cost.")


def main() -> None:
    demo_json()
    demo_redaction()
    demo_where_the_filter_goes()
    demo_formatter_scrubbing()
    print()
    print("=" * 70)
    print("Structured logging demonstration complete.")


if __name__ == "__main__":
    main()
