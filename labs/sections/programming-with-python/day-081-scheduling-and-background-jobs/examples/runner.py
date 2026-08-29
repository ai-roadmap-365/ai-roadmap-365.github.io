"""The part that makes a job survivable: lock, timeout, log, exit code, heartbeat.

Scheduling something is one line in a crontab. Everything that makes the
scheduled thing trustworthy lives here, and it is the same five concerns every
time:

1. **One at a time.** Take a lock; if someone else has it, exit immediately
   with a distinct code rather than doing the work twice.
2. **Bounded.** A job with no timeout can hang forever holding the lock, which
   means every later run is also skipped, which means the job silently stops.
   A hang is worse than a crash precisely because nothing reports it.
3. **Logged with context.** One structured line per run, with a run id, the
   status, the duration and the exit code. "It failed last Tuesday" is only
   answerable if the line exists.
4. **Honest exit codes.** The scheduler and any wrapper only see the number.
   0 means the work is done; anything else means look.
5. **A heartbeat.** Every success writes down when it succeeded. A separate
   watchdog reads that file. Without it, a job that stops being scheduled at
   all produces no failure and no output — and no alert.

Exit codes follow conventions that already exist rather than inventing new
numbers: 75 is ``EX_TEMPFAIL`` from the BSD ``sysexits.h`` list ("temporary
failure, try again later"), and 124 is the code GNU ``timeout`` uses when it
kills a command.
"""

from __future__ import annotations

import datetime as dt
import json
import signal
import sys
import traceback
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TextIO

from clock import Clock
from joblock import AlreadyRunning, job_lock

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_ALREADY_RUNNING = 75  # sysexits.h EX_TEMPFAIL
EXIT_TIMEOUT = 124  # the code GNU timeout(1) uses

EXIT_MEANINGS: dict[int, str] = {
    EXIT_OK: "the work is done (or was already done)",
    EXIT_FAILED: "the work raised an exception",
    EXIT_ALREADY_RUNNING: "another copy holds the lock; nothing was done",
    EXIT_TIMEOUT: "the work exceeded its timeout and was interrupted",
}


class JobTimeout(TimeoutError):
    """Raised inside the job when its time budget expires."""


@dataclass(frozen=True)
class JobRun:
    """The record of one invocation. Everything the log line is built from."""

    name: str
    run_id: str
    status: str  # "ok" | "skipped" | "failed" | "timeout" | "already-running"
    exit_code: int
    started_at: dt.datetime
    finished_at: dt.datetime
    duration_seconds: float
    detail: Mapping[str, Any] = field(default_factory=dict)

    def as_event(self) -> dict[str, Any]:
        return {
            "job": self.name,
            "run_id": self.run_id,
            "status": self.status,
            "exit_code": self.exit_code,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
            "duration_seconds": round(self.duration_seconds, 3),
            **dict(self.detail),
        }


Logger = Callable[[Mapping[str, Any]], None]


def jsonl_logger(path: str | Path) -> Logger:
    """Append one JSON object per line. Machine-readable, greppable, append-only.

    One line per event, never a multi-line traceback in the middle of the
    stream: a log you cannot process with ``grep`` and ``json.loads`` is a log
    nobody processes.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    def write(event: Mapping[str, Any]) -> None:
        with open(target, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(event), sort_keys=True) + "\n")

    return write


def stream_logger(stream: TextIO | None = None) -> Logger:
    """The same events, to standard output — which is where cron mails them from."""
    target = stream if stream is not None else sys.stdout

    def write(event: Mapping[str, Any]) -> None:
        print(json.dumps(dict(event), sort_keys=True), file=target)

    return write


def combined_logger(*loggers: Logger) -> Logger:
    def write(event: Mapping[str, Any]) -> None:
        for logger in loggers:
            logger(event)

    return write


def make_run_id(name: str, started: dt.datetime) -> str:
    """Deterministic under a frozen clock, which is what makes runs assertable."""
    return f"{name}-{started.strftime('%Y%m%dT%H%M%S%z')}"


def write_heartbeat(path: str | Path, run: JobRun) -> None:
    """Record the last success. This file is the dead man's switch."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "job": run.name,
                "run_id": run.run_id,
                "last_success": run.finished_at.isoformat(),
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def run_job(
    *,
    name: str,
    work: Callable[[], Mapping[str, Any]],
    clock: Clock,
    lock_path: str | Path,
    log: Logger,
    timeout_seconds: float | None = None,
    heartbeat_path: str | Path | None = None,
) -> JobRun:
    """Run ``work`` once, under a lock, under a time budget, and write it down.

    ``work`` is a zero-argument callable returning a mapping that is merged
    into the log event. Injecting it — instead of hard-coding the report
    generator here — is what lets the test suite check the lock, the timeout
    and the logging with a two-line fake job.
    """
    started = clock()
    run_id = make_run_id(name, started)

    def finish(
        status: str, exit_code: int, detail: Mapping[str, Any]
    ) -> JobRun:
        finished = clock()
        run = JobRun(
            name=name,
            run_id=run_id,
            status=status,
            exit_code=exit_code,
            started_at=started,
            finished_at=finished,
            duration_seconds=(finished - started).total_seconds(),
            detail=detail,
        )
        log(run.as_event())
        return run

    try:
        with job_lock(lock_path):
            with _time_budget(timeout_seconds):
                try:
                    detail = dict(work())
                except JobTimeout:
                    return finish(
                        "timeout",
                        EXIT_TIMEOUT,
                        {
                            "error": "JobTimeout",
                            "timeout_seconds": timeout_seconds,
                            "message": f"work exceeded {timeout_seconds}s and was interrupted",
                        },
                    )
                except Exception as exc:  # noqa: BLE001 - deliberate: log and exit non-zero
                    return finish(
                        "failed",
                        EXIT_FAILED,
                        {
                            "error": type(exc).__name__,
                            "message": str(exc),
                            "traceback": traceback.format_exc(limit=3).strip().splitlines()[-1],
                        },
                    )
    except AlreadyRunning as exc:
        return finish(
            "already-running",
            EXIT_ALREADY_RUNNING,
            {"lock_path": str(exc.path), "holder_pid": exc.holder_pid},
        )

    status = str(detail.pop("status", "ok"))
    run = finish(status, EXIT_OK, detail)
    if heartbeat_path is not None:
        write_heartbeat(heartbeat_path, run)
    return run


class _time_budget:
    """A wall-clock guard built on ``signal.setitimer`` and ``SIGALRM``.

    Honest limits, because they matter: this is POSIX-only, it works only in
    the main thread, and it interrupts Python at the next opportunity — a call
    blocked deep inside a C library may not notice. It is fine for the common
    cases (a sleep, a socket read, a loop) and it is not a substitute for
    supervising the job as a child process. ``supervise.py`` in this directory
    does the stronger version.
    """

    def __init__(self, seconds: float | None) -> None:
        self.seconds = seconds
        self._previous: Any = None

    def __enter__(self) -> _time_budget:
        if self.seconds is None:
            return self

        def on_alarm(signum: int, frame: Any) -> None:
            raise JobTimeout(f"exceeded {self.seconds}s")

        self._previous = signal.signal(signal.SIGALRM, on_alarm)
        signal.setitimer(signal.ITIMER_REAL, self.seconds)
        return self

    def __exit__(self, *exc_info: Any) -> None:
        if self.seconds is None:
            return
        signal.setitimer(signal.ITIMER_REAL, 0)
        if self._previous is not None:
            signal.signal(signal.SIGALRM, self._previous)
