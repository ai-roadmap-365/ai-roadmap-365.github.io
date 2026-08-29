"""A lock that stops two copies of one job running at once.

The failure this prevents is specific. A job scheduled every five minutes that
usually takes forty seconds is fine until the day it takes six minutes —
because then the scheduler starts the next copy while the first is still
working, and now two processes are writing the same file, counting the same
rows, or calling the same paid API. Cron will not stop that happening. Nothing
will, unless the job stops itself.

The mechanism here is ``fcntl.flock`` with ``LOCK_NB``: an advisory lock held
by the operating system on an open file descriptor. Two properties make it the
right tool:

* it is atomic — there is no window between "check" and "take" for a second
  process to slip through, which is exactly the bug in the obvious
  "if the lockfile exists, exit" implementation;
* the kernel releases it when the process exits, however it exits. A job
  killed with SIGKILL, or a machine that loses power, does not leave a stale
  lock that blocks every future run — which is the other failure of the
  naive version, and the more annoying one at three in the morning.

``fcntl`` is POSIX: macOS and Linux have it, Windows does not. The Windows
equivalent is ``msvcrt.locking`` or a named mutex; this lab runs on macOS and
Linux, and the README says so plainly.
"""

from __future__ import annotations

import contextlib
import fcntl
import os
from collections.abc import Iterator
from pathlib import Path


class AlreadyRunning(RuntimeError):
    """Raised when another process already holds the job's lock."""

    def __init__(self, path: Path, holder_pid: str) -> None:
        super().__init__(f"another run already holds {path} (pid {holder_pid})")
        self.path = path
        self.holder_pid = holder_pid


@contextlib.contextmanager
def job_lock(path: str | os.PathLike[str]) -> Iterator[Path]:
    """Hold an exclusive, non-blocking lock for the duration of the block.

    Raises :class:`AlreadyRunning` immediately if the lock is held elsewhere.
    Failing fast is deliberate: a scheduled job that *waits* for the lock just
    queues up copies of itself, and a queue of overdue jobs is how a slow
    Monday becomes an outage.

    The process id is written into the file purely so a human reading it later
    knows who to look for. It is not used for locking — the file descriptor is.
    """
    lock_path = Path(path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(lock_path, "a+")  # noqa: SIM115 - closed in the finally below
    try:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            handle.seek(0)
            holder = handle.read().strip() or "unknown"
            raise AlreadyRunning(lock_path, holder) from None
        handle.seek(0)
        handle.truncate()
        handle.write(f"{os.getpid()}\n")
        handle.flush()
        try:
            yield lock_path
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        handle.close()
