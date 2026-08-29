"""Alerting on silence: the check that catches a job which simply stopped.

Every alert most people write fires on failure. Failure is the easy case: the
job ran, something went wrong, it exited non-zero, and something noticed.

The case that actually bites is the opposite. Somebody edits the crontab and
drops a line. A machine is rebuilt and the timer is not re-enabled. A lock file
on a network share is never released and every run exits 75 — quietly, because
75 is not a crash. In all three the job produces no error, because it produces
nothing at all, and a monitor watching for errors sees a clean, quiet,
completely broken system. Teams discover this months later, usually by
noticing that a number stopped moving.

The fix is a **dead man's switch**: the job writes down each success, and a
separate check alerts when that record gets too old. It inverts the question
from "did anything fail?" to "did the thing that should have happened, happen?"
— and only the second question has an answer when the job is gone.

The check itself is fifteen lines and takes the clock as a parameter, so
"what does this report the morning after a job stops?" is a test, not a wait.
"""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path

from clock import Clock

OK = "ok"
STALE = "stale"
MISSING = "missing"
UNREADABLE = "unreadable"


@dataclass(frozen=True)
class WatchdogVerdict:
    """What the watchdog concluded, and why — in words a pager can carry."""

    state: str
    message: str
    last_success: dt.datetime | None = None
    age_seconds: float | None = None

    @property
    def alerting(self) -> bool:
        return self.state != OK


def check_heartbeat(
    *,
    heartbeat_path: str | Path,
    clock: Clock,
    max_age: dt.timedelta,
) -> WatchdogVerdict:
    """Alert if the last recorded success is older than ``max_age``.

    Choose ``max_age`` as roughly two intervals plus the job's normal runtime.
    Too tight and one slow run pages somebody at 4 a.m.; too loose and a job
    can be dead for a day before anyone hears about it. Two intervals is the
    usual compromise: it tolerates exactly one missed run and no more.
    """
    path = Path(heartbeat_path)
    now = clock()
    if not path.exists():
        return WatchdogVerdict(
            MISSING,
            f"no heartbeat at {path.name}: the job has never recorded a success",
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        last_success = dt.datetime.fromisoformat(payload["last_success"])
    except (json.JSONDecodeError, KeyError, ValueError, UnicodeDecodeError) as exc:
        return WatchdogVerdict(
            UNREADABLE, f"heartbeat at {path.name} could not be read: {type(exc).__name__}"
        )
    if last_success.tzinfo is None:
        return WatchdogVerdict(
            UNREADABLE,
            f"heartbeat at {path.name} holds a naive timestamp; it cannot be compared safely",
        )
    age = (now - last_success).total_seconds()
    if age > max_age.total_seconds():
        return WatchdogVerdict(
            STALE,
            (
                f"last success was {_humanise(age)} ago "
                f"(budget {_humanise(max_age.total_seconds())}) — the job has stopped running"
            ),
            last_success,
            age,
        )
    return WatchdogVerdict(
        OK, f"last success {_humanise(age)} ago, within budget", last_success, age
    )


def _humanise(seconds: float) -> str:
    seconds = float(seconds)
    if seconds < 90:
        return f"{seconds:.0f}s"
    if seconds < 5400:
        return f"{seconds / 60:.0f}m"
    if seconds < 172800:
        return f"{seconds / 3600:.1f}h"
    return f"{seconds / 86400:.1f}d"
