"""The stronger timeout: run the job as a child process and kill the group.

``runner.py`` guards the work with ``SIGALRM``, which is simple and enough for
most jobs. It has two holes worth knowing about: it cannot interrupt a call
that is blocked inside a C library, and it cannot do anything at all about a
grandchild process the job started.

Supervising the job as a child closes both. ``subprocess.run(..., timeout=n)``
raises ``TimeoutExpired`` and kills the child — but only the child. A job that
launched its own helpers leaves them orphaned and still running, which is
exactly the "no background process left behind" rule this lab cares about. The
fix is ``start_new_session=True``, which puts the child in its own process
group, and ``os.killpg`` to signal the whole group.

The escalation is the usual one: ask politely with SIGTERM, wait a moment, and
only then use SIGKILL, which cannot be caught or ignored.

Run it directly to watch a hung command die on schedule:

    python3 examples/supervise.py --timeout 1 -- sleep 30
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Supervised:
    exit_code: int
    timed_out: bool
    stdout: str
    stderr: str


def run_supervised(
    argv: list[str],
    *,
    timeout: float,
    grace: float = 0.5,
) -> Supervised:
    """Run ``argv``, killing the whole process group if it overruns."""
    process = subprocess.Popen(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,  # its own process group, so killpg reaches helpers
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        return Supervised(process.returncode, False, stdout, stderr)
    except subprocess.TimeoutExpired:
        _terminate_group(process, grace)
        stdout, stderr = process.communicate()
        return Supervised(124, True, stdout, stderr)


def _terminate_group(process: subprocess.Popen[str], grace: float) -> None:
    """SIGTERM the group, wait ``grace`` seconds, then SIGKILL what is left."""
    try:
        group = os.getpgid(process.pid)
    except ProcessLookupError:
        return
    for sig, wait in ((signal.SIGTERM, grace), (signal.SIGKILL, 0.0)):
        try:
            os.killpg(group, sig)
        except ProcessLookupError:
            return
        deadline = time.monotonic() + wait
        while time.monotonic() < deadline:
            if process.poll() is not None:
                return
            time.sleep(0.02)
        if process.poll() is not None:
            return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="supervise.py",
        description="Run a command with a hard wall-clock timeout on its whole process group.",
    )
    parser.add_argument("--timeout", type=float, required=True, help="seconds before the kill")
    parser.add_argument("--grace", type=float, default=0.5, help="seconds between TERM and KILL")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="the command, after --")
    args = parser.parse_args(argv)

    command = [c for c in args.command if c != "--"]
    if not command:
        parser.error("no command given; put it after --")

    result = run_supervised(command, timeout=args.timeout, grace=args.grace)
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    if result.timed_out:
        print(
            f"supervise: killed after {args.timeout}s -> exit 124",
            file=sys.stderr,
        )
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
