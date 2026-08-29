"""Reusable logging pieces: a JSON formatter and a redacting filter.

This is the "from scratch" half of the day's logging material. Both classes
are small on purpose — the point is that the four objects the `logging`
module gives you (logger, handler, formatter, filter) are separate, and that
you extend the two of them that are meant to be extended.

Nothing here is clever. `JsonFormatter` overrides one method, `format`.
`RedactingFilter` overrides one method, `filter`. Everything else is
inherited.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Iterable

# Attributes the logging module puts on every LogRecord. Anything on a record
# that is NOT in this set was put there by the caller through `extra=`, which
# is exactly the material a structured log wants to carry.
#
# Built by asking the logging module rather than by hand-copying its
# documentation, so it cannot drift out of date with the interpreter you are
# actually running.
_STANDARD_RECORD_KEYS = frozenset(
    vars(
        logging.LogRecord(
            name="", level=0, pathname="", lineno=0, msg="", args=(), exc_info=None
        )
    )
) | {"message", "asctime", "taskName"}


def iso_utc(epoch_seconds: float) -> str:
    """Format an epoch timestamp as ISO 8601 in UTC, to milliseconds.

    Day 91 made the argument for this format in a database: fixed-width,
    most-significant-first, so text order is chronological order. A log file
    wants the same property, for the same reason — `sort` on a log file
    should put the lines in the order the events happened.
    """
    whole = int(epoch_seconds)
    millis = int(round((epoch_seconds - whole) * 1000))
    if millis == 1000:  # a rounding edge; roll it into the next second
        whole += 1
        millis = 0
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(whole)) + f".{millis:03d}Z"


class JsonFormatter(logging.Formatter):
    """Render a LogRecord as one JSON object on one line.

    Why one line: every log-shipping tool ever written reads a stream of
    lines. A multi-line JSON document is a parsing problem for the reader;
    a one-line JSON object is not.

    The fixed fields are the ones a person searching at 3 a.m. filters on:
    when, how bad, who said it, what happened. Everything passed through
    `extra=` is merged in beside them, so `log.info("step done",
    extra={"step": 3})` produces a `step` field you can query on rather than
    a number buried in prose.
    """

    def __init__(self, static_fields: dict[str, Any] | None = None) -> None:
        super().__init__()
        # Fields stamped onto every record — the run id belongs here, because
        # a value that must appear on every line should be attached once
        # rather than remembered at every call site.
        self.static_fields = dict(static_fields or {})

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": iso_utc(record.created),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        payload.update(self.static_fields)

        for key, value in vars(record).items():
            if key in _STANDARD_RECORD_KEYS or key.startswith("_"):
                continue
            payload[key] = value

        if record.exc_info:
            # formatException gives the same text `logging.exception` would
            # have printed. It goes in a field of its own rather than being
            # glued onto the message, so the parser does not have to guess
            # where the message ends and the traceback starts.
            payload["exc_type"] = record.exc_info[0].__name__
            payload["traceback"] = self.formatException(record.exc_info)

        # default=str so an unexpected object in `extra=` degrades to its
        # repr instead of raising inside the logging call. A logging call
        # that raises is a bug that only shows up when something is already
        # going wrong, which is the worst possible time.
        return json.dumps(payload, default=str, sort_keys=False)


class RedactingFilter(logging.Filter):
    """Replace known secret VALUES anywhere in a record with a placeholder.

    **Attach it to every HANDLER, not to a logger.** This is the single most
    important line in this file and it was learned the hard way while writing
    this lab. A filter attached to a logger runs only for records logged
    through *that logger object*. Records that arrive by propagation from a
    descendant logger — `app.loader` when the filter is on `app` — skip the
    ancestor's filters entirely; propagation consults the ancestors' HANDLERS,
    not their filters. So `logging.getLogger("app").addFilter(redactor)` looks
    like whole-application protection and is not: every `getLogger(__name__)`
    in every module is a descendant, and every one of them bypasses it.
    Demonstration 03 shows this happening. A filter on each handler sees
    everything that reaches that destination, which is what you actually want.

    The design decision worth arguing about: this redacts by value, not by
    key name. Key-name redaction ("hide anything called password") misses
    `log.info("calling %s", url_with_token)`, which is how secrets actually
    escape. Value redaction catches the secret wherever it appears — in the
    message, in the arguments, in an `extra` field.

    The honest limits, and they are real:

    * It only knows the values you hand it. A secret it has never been told
      about goes straight through.
    * It cannot see a secret that has been transformed — base64-encoded,
      truncated, or split across two log calls.
    * Values shorter than `min_length` are ignored, because redacting every
      occurrence of a two-character secret would destroy the log.

    A redacting filter is a seatbelt, not a reason to drive at a wall. The
    rule stays: do not log the secret.
    """

    PLACEHOLDER = "***redacted***"

    def __init__(self, secrets: Iterable[str], min_length: int = 6) -> None:
        super().__init__()
        self.min_length = min_length
        self.secrets = sorted(
            {s for s in secrets if s and len(s) >= min_length},
            key=len,
            reverse=True,  # longest first, so a secret containing another
        )                  # secret is not half-redacted into readability

    def scrub(self, text: str) -> str:
        for secret in self.secrets:
            if secret in text:
                text = text.replace(secret, self.PLACEHOLDER)
        return text

    def _scrub_value(self, value: Any) -> Any:
        if isinstance(value, str):
            return self.scrub(value)
        if isinstance(value, (list, tuple)):
            return type(value)(self._scrub_value(v) for v in value)
        if isinstance(value, dict):
            return {k: self._scrub_value(v) for k, v in value.items()}
        return value

    def filter(self, record: logging.LogRecord) -> bool:
        # A filter returns True to keep the record and False to drop it.
        # Mutating the record on the way through is explicitly allowed by the
        # logging documentation, and is what makes redaction possible at all.
        if isinstance(record.msg, str):
            record.msg = self.scrub(record.msg)
        if record.args:
            record.args = self._scrub_value(record.args)
        for key, value in list(vars(record).items()):
            if key in _STANDARD_RECORD_KEYS or key.startswith("_"):
                continue
            setattr(record, key, self._scrub_value(value))
        return True


def buffer_handler(
    level: int = logging.DEBUG, formatter: logging.Formatter | None = None
) -> tuple[logging.Handler, Any]:
    """A handler that writes into a StringIO, plus the StringIO itself.

    This is how the tests capture log output, and how you should capture it
    too. Scraping stdout means asserting on whatever else the program
    printed; a buffer handler receives exactly the records that reached this
    handler and nothing else.
    """
    import io

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    handler.setFormatter(formatter or JsonFormatter())
    return handler, stream
