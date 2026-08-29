"""The state file, and the atomic write that keeps it trustworthy.

State is what makes a job idempotent: it is the record of what has already been
processed, so a second run does not do the work twice. That makes it the single
most valuable file the toolkit owns, and losing it is worse than a failed run —
a failed run is visible, a corrupted state file quietly re-processes or
silently skips.

So the write is atomic, exactly as Days 64 and 65 described. Write the whole
new document to a temporary file in the SAME directory, flush it, ask the
operating system to put it on the disk, then `os.replace` it over the old name.
`os.replace` is atomic on POSIX and on Windows: any reader sees either the
complete old file or the complete new one, never a half-written mixture. If the
machine loses power between the write and the replace, the previous state is
still there and the temporary file is garbage that the next run cleans up.

The naive version — `open(path, "w")` then `json.dump` — truncates the real
file first. Interrupt it and the record of everything you have ever processed
is a zero-byte file.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Mapping

from .core import empty_state


class StateError(RuntimeError):
    """The state file exists but cannot be used. Never guess; stop."""


def load(path: Path) -> dict[str, Any]:
    """Read the state file, or return a fresh empty state if there is none."""
    if not path.is_file():
        return empty_state()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StateError(
            f"{path} is not valid JSON ({exc}). Refusing to overwrite it. "
            f"Move it aside to start fresh."
        ) from exc
    if not isinstance(data, dict) or "version" not in data:
        raise StateError(f"{path} does not look like a feedkit state file")
    return data


def write_atomic(
    path: Path,
    state: Mapping[str, Any],
    crash_hook: Callable[[], None] | None = None,
) -> None:
    """Write state so that an interruption leaves the previous file intact.

    `crash_hook` exists purely so the lab can prove the property. The test
    passes a function that raises, standing in for the power cut, and then
    asserts the old file is byte-identical. Production code passes nothing.
    """
    # Exercise 5 — the atomic write.
    #
    # Steps, in this exact order:
    #   1. make sure path.parent exists;
    #   2. serialise `state` to JSON (indent=2, sort_keys=True, trailing
    #      newline — a stable byte-for-byte rendering is what makes the
    #      dry-run test possible at all);
    #   3. write it to a NamedTemporaryFile in the SAME directory as `path`
    #      with delete=False. The same directory matters: os.replace is only
    #      atomic within one filesystem, and /tmp is often a different one;
    #   4. flush the handle and os.fsync its file descriptor;
    #   5. if crash_hook is not None, call it — this is where the lab injects
    #      the simulated power cut;
    #   6. os.replace(tmp_path, path);
    #   7. on ANY exception, delete the temporary file and re-raise. Catch
    #      BaseException, not Exception, so a KeyboardInterrupt still cleans up.
    #
    # What you must NOT write is open(path, "w") followed by json.dump. That
    # truncates the real file first, and an interruption there destroys the
    # record of everything you have ever processed.
    #
    # Check it with:  pytest tests/test_toolkit.py -k interrupted
    raise NotImplementedError("Exercise 5: implement write_atomic in state.py")


class LockHeld(RuntimeError):
    """Another run of this toolkit is already in progress."""


class Lock:
    """A lock file, so two scheduled runs never overlap.

    Created with O_CREAT | O_EXCL, which the operating system guarantees will
    succeed for exactly one caller. The file holds the process id, which is
    what lets a human decide whether a lock left behind by a crash is stale.

    This is deliberately the simplest thing that works on one machine. It is
    not a distributed lock and must not be used as one.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self._acquired = False

    def __enter__(self) -> "Lock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            holder = ""
            try:
                holder = self.path.read_text(encoding="utf-8").strip()
            except OSError:
                pass
            raise LockHeld(
                f"{self.path} exists (held by pid {holder or 'unknown'}). "
                f"Another run is in progress, or a previous run was killed. "
                f"Delete the file only after checking that no such process exists."
            ) from exc
        with os.fdopen(fd, "w") as handle:
            handle.write(str(os.getpid()))
        self._acquired = True
        return self

    def __exit__(self, *exc_info: object) -> None:
        if self._acquired:
            self.path.unlink(missing_ok=True)
            self._acquired = False
