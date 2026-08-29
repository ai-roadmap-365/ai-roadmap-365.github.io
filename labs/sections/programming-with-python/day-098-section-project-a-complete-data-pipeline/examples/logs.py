"""Stage 5, part two: one structured log line per stage, with a run id.

Two decisions carry this module, and both come from Day 97.

**Structured, not prose.** ``logging`` in the standard library formats records
through a Formatter; this one emits a single JSON object per line. The reason is
not fashion. A prose line has to be parsed with a regular expression that breaks
the first time somebody adds a word; a JSON line is queryable on the day you
need it, which is always the day something is on fire.

**Redaction is a filter, not a discipline.** Never logging a secret by hand
works right up until an upstream service echoes it back inside an error body —
which the fixture server does on purpose, because real ones do. So the logger
scans every string it is about to emit for every known secret and replaces it.
The check belongs in one place that cannot be forgotten.

The clock is injected. The pipeline passes the real one; the demo and the tests
pass a fixed one, which is what makes the captured logs comparable byte for
byte. A module that reads the clock itself cannot be tested on its output.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, TextIO

LEVELS = {"debug": 10, "info": 20, "warning": 30, "error": 40}
REDACTED = "***redacted***"


def utc_clock() -> str:
    """The real clock, as ISO 8601 in UTC with a Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fixed_clock(start: str = "2026-08-16T12:00:00Z", step_seconds: int = 1) -> Callable[[], str]:
    """A clock that starts at ``start`` and advances one step per call.

    Deterministic, so a run's log can be compared against a stored capture.
    """
    moment = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    state = {"n": 0}

    def tick() -> str:
        from datetime import timedelta

        value = moment + timedelta(seconds=step_seconds * state["n"])
        state["n"] += 1
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")

    return tick


def redact(value: Any, secrets: tuple[str, ...]) -> Any:
    """Replace every occurrence of every secret, at any depth."""
    if not secrets:
        return value
    if isinstance(value, str):
        for secret in secrets:
            if secret and secret in value:
                value = value.replace(secret, REDACTED)
        return value
    if isinstance(value, dict):
        return {key: redact(item, secrets) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(item, secrets) for item in value]
    return value


class RunLogger:
    """Emits one JSON object per line, every line carrying the same run id."""

    def __init__(
        self,
        run_id: str,
        *,
        stream: TextIO | None = None,
        clock: Callable[[], str] = utc_clock,
        level: str = "info",
        secrets: tuple[str, ...] = (),
    ) -> None:
        self.run_id = run_id
        self.stream = stream if stream is not None else sys.stderr
        self.clock = clock
        self.threshold = LEVELS[level]
        self.secrets = tuple(s for s in secrets if s)
        self.emitted: list[dict[str, Any]] = []

    def event(self, event: str, level: str = "info", **fields: Any) -> dict[str, Any] | None:
        if LEVELS[level] < self.threshold:
            return None
        record: dict[str, Any] = {
            "ts": self.clock(),
            "level": level,
            "run_id": self.run_id,
            "event": event,
        }
        record.update(redact(fields, self.secrets))
        self.emitted.append(record)
        self.stream.write(json.dumps(record) + "\n")
        self.stream.flush()
        return record

    def events_named(self, event: str) -> list[dict[str, Any]]:
        return [record for record in self.emitted if record["event"] == event]
