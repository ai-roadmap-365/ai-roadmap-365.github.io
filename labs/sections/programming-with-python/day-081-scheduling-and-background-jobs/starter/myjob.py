"""YOUR WORKING FILE — exercises 1 to 4.

Five functions, each one an operational property a scheduled job needs. They
are ordered the way you would add them to a real job, and each one is worth
the few lines it costs.

Run your work with:

    .venv/bin/pytest starter -q

Every exercise is marked `@pytest.mark.skip` in `starter/test_myjob.py`.
Delete the skip line for the exercise you are attempting, then make it pass.
The finished versions live in `examples/` — read them after you have tried,
not before, because the whole value here is in getting the lock wrong once.
"""

from __future__ import annotations

import contextlib
import datetime as dt
import json
import os
import tempfile
from collections.abc import Callable, Iterator, Mapping
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Exercise 1 — idempotence
# ---------------------------------------------------------------------------
# Running a job twice must produce one result. Retries, catch-up runs, and an
# operator typing the command a second time all mean "run it twice", and all
# three happen.
#
# Two functions. `output_written` answers "has a COMPLETE result already been
# produced for this day?" — complete meaning the file parses as JSON and
# carries the right `report_date`, so a half-written file from a crashed run
# is retried rather than mistaken for a success. `write_atomically` writes to
# a temporary name in the SAME directory and then `os.replace`s it into place,
# which is atomic on POSIX. Same directory matters: os.replace is only atomic
# within one filesystem.
#
# Prove it with: pytest starter -q -k "idempot or partial"


def output_path(output_dir: Path, report_date: dt.date) -> Path:
    """The output name IS the idempotence key: one day, one file, one name."""
    return Path(output_dir) / f"report-{report_date.isoformat()}.json"


def output_written(output_dir: Path, report_date: dt.date) -> bool:
    """Return True only if a COMPLETE result already exists for this date."""
    raise NotImplementedError("Exercise 1a: check the file exists, parses, and matches the date")


def write_atomically(payload: Mapping[str, Any], output_dir: Path, report_date: dt.date) -> Path:
    """Write JSON via a temporary file in the same directory, then os.replace."""
    raise NotImplementedError("Exercise 1b: tempfile.NamedTemporaryFile(dir=...) then os.replace")


# ---------------------------------------------------------------------------
# Exercise 2 — the lock
# ---------------------------------------------------------------------------
# A job that takes longer than its interval will eventually be started while
# the previous copy is still running. Two copies writing one file is a
# corrupted file; two copies calling a paid API is a doubled bill.
#
# Use `fcntl.flock` with `LOCK_EX | LOCK_NB`. Do NOT write
# "if the lock file exists: exit" — there is a window between the check and
# the create where a second process slips through, and a stale file from a
# killed process blocks every run afterwards. flock has neither problem: it is
# atomic, and the kernel releases it when the process dies, however it dies.
#
# Raise AlreadyRunning when the lock is held. Release it in a finally, so a
# job that raises does not leave the lock held.
#
# Prove it with: pytest starter -q -k lock


class AlreadyRunning(RuntimeError):
    """Raised when another process already holds the job's lock."""


@contextlib.contextmanager
def my_job_lock(path: str | os.PathLike[str]) -> Iterator[Path]:
    """Hold an exclusive non-blocking lock for the block; raise AlreadyRunning if taken."""
    raise NotImplementedError("Exercise 2: fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)")
    yield Path(path)  # noqa: B901 - keeps this a generator function for the contextmanager


# ---------------------------------------------------------------------------
# Exercise 3 — the timeout
# ---------------------------------------------------------------------------
# A job with no time budget can hang forever holding the lock, which silently
# stops every later run. A hang is worse than a crash: a crash is reported.
#
# Use `signal.signal(signal.SIGALRM, handler)` and
# `signal.setitimer(signal.ITIMER_REAL, seconds)`. The handler raises
# JobTimeout. Cancel the timer in a finally — an alarm left armed fires
# somewhere unrelated later, which is a genuinely confusing bug.
#
# `seconds is None` must mean "no limit" rather than "zero".
#
# Prove it with: pytest starter -q -k timeout


class JobTimeout(TimeoutError):
    """Raised inside the job when its time budget expires."""


@contextlib.contextmanager
def time_budget(seconds: float | None) -> Iterator[None]:
    """Raise JobTimeout if the block runs longer than `seconds`."""
    raise NotImplementedError("Exercise 3: SIGALRM + setitimer, cancelled in a finally")
    yield  # noqa: B901 - keeps this a generator function for the contextmanager


# ---------------------------------------------------------------------------
# Exercise 4 — structured logging
# ---------------------------------------------------------------------------
# You will not be watching when this fails. The log line is the entire record
# of what happened, so it needs enough context to answer "which run, when, how
# long, what happened, what did it exit with" without any other evidence.
#
# Write ONE JSON object per line, appended. One line per event means the file
# can be processed with grep and json.loads; a multi-line traceback in the
# middle of the stream means it cannot.
#
# Include at least: job, run_id, status, exit_code, started_at, finished_at,
# duration_seconds. Timestamps come from the injected clock, never from
# datetime.now() — that is what makes the log assertable in a test.
#
# Prove it with: pytest starter -q -k log


def make_event(
    *,
    job: str,
    status: str,
    exit_code: int,
    started_at: dt.datetime,
    finished_at: dt.datetime,
    **extra: Any,
) -> dict[str, Any]:
    """Build the log event. run_id must be derived from the name and start time."""
    raise NotImplementedError("Exercise 4a: build the dict, including run_id and duration_seconds")


def append_jsonl(path: str | Path, event: Mapping[str, Any]) -> None:
    """Append exactly one JSON object, on one line, to `path`."""
    raise NotImplementedError("Exercise 4b: open(path, 'a') and write json.dumps(event) + newline")


# ---------------------------------------------------------------------------
# Provided, so you can concentrate on the four exercises above.
# ---------------------------------------------------------------------------


def frozen_clock(moment: dt.datetime) -> Callable[[], dt.datetime]:
    if moment.tzinfo is None:
        raise ValueError("use an aware datetime")
    return lambda: moment


def sample_payload(report_date: dt.date, generated_at: dt.datetime) -> dict[str, Any]:
    return {
        "report_date": report_date.isoformat(),
        "generated_at": generated_at.isoformat(),
        "reading_count": 6,
    }


__all__ = [
    "AlreadyRunning",
    "JobTimeout",
    "append_jsonl",
    "frozen_clock",
    "make_event",
    "my_job_lock",
    "output_path",
    "output_written",
    "sample_payload",
    "time_budget",
    "write_atomically",
]

# Silence unused-import warnings while the exercises are unfinished; the
# finished versions use every one of these.
_UNUSED = (json, tempfile)
