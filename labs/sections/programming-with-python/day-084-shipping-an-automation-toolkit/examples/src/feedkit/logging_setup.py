"""Structured logging — the thing that makes an unattended run debuggable.

Two decisions are baked in here, and both are worth arguing rather than
copying.

**One JSON object per line, on stdout.** A line of prose is readable by you at
your desk; a line of JSON is readable by you AND by `grep`, `jq`, a log
shipper, and whatever the supervisor writes it into. Writing to stdout rather
than opening a log file means the program does not have to know about log
rotation, permissions, or where the operator wants their logs — cron mails it,
systemd hands it to the journal, launchd redirects it, and a human running the
command by hand simply sees it. Fewer decisions inside the program is the
point.

**Every record carries the run id and, where it applies, the item.** An
unattended failure is a message you read hours later with no memory of the
context. "Timeout" tells you nothing. "run 8f2c1a: source=papers attempt=3
timeout after 5.0s" tells you which run, which item, how hard it tried, and
what the limit was.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any, Iterable, TextIO

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

#: Extra keys that the formatter promotes to top-level JSON fields.
CONTEXT_KEYS = ("source", "attempt", "status", "count", "path", "elapsed_ms", "url")


class RedactingFilter(logging.Filter):
    """Replace known secret values with a placeholder, everywhere.

    This is a seatbelt, not a licence. The right habit is to never put a token
    into a log call in the first place; this filter exists because one day
    somebody will log a whole request object, or an exception message that
    happens to quote a URL with a token in the query string, and the difference
    between a bad afternoon and a credential rotation is whether that string
    reached the log.
    """

    PLACEHOLDER = "***REDACTED***"

    def __init__(self, secrets: Iterable[str] = ()) -> None:
        super().__init__()
        # Very short strings would redact half the alphabet; ignore them.
        self.secrets = tuple(secret for secret in secrets if secret and len(secret) >= 6)

    def _scrub(self, value: Any) -> Any:
        if isinstance(value, str):
            for secret in self.secrets:
                value = value.replace(secret, self.PLACEHOLDER)
            return value
        if isinstance(value, (list, tuple)):
            return type(value)(self._scrub(item) for item in value)
        if isinstance(value, dict):
            return {key: self._scrub(item) for key, item in value.items()}
        return value

    def filter(self, record: logging.LogRecord) -> bool:
        if not self.secrets:
            return True
        record.msg = self._scrub(record.msg)
        if record.args:
            record.args = self._scrub(record.args)
        for key in CONTEXT_KEYS:
            if hasattr(record, key):
                setattr(record, key, self._scrub(getattr(record, key)))
        if record.exc_info:
            # An exception's own text is the most common accidental leak.
            exc = record.exc_info[1]
            if exc is not None and exc.args:
                exc.args = tuple(self._scrub(arg) for arg in exc.args)
        return True


class JsonFormatter(logging.Formatter):
    """One JSON object per line, with a stable field order."""

    def __init__(self, run_id: str) -> None:
        super().__init__()
        self.run_id = run_id

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname.lower(),
            "run_id": self.run_id,
            "event": record.getMessage(),
        }
        for key in CONTEXT_KEYS:
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["error"] = str(record.exc_info[1])
        # ensure_ascii=False keeps the log readable to a human. Escaping every
        # non-ASCII character is the default and is nearly always wrong for a
        # file somebody has to read at three in the morning.
        return json.dumps(payload, sort_keys=False, ensure_ascii=False)


def configure(
    level: str,
    run_id: str,
    secrets: Iterable[str] = (),
    stream: TextIO | None = None,
) -> logging.Logger:
    """Build the toolkit's logger. Called once, at the start of a run."""
    logger = logging.getLogger("feedkit")
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(LEVELS.get(level.lower(), logging.INFO))

    handler = logging.StreamHandler(stream if stream is not None else sys.stdout)
    handler.setFormatter(JsonFormatter(run_id))
    handler.addFilter(RedactingFilter(secrets))
    logger.addHandler(handler)
    return logger
