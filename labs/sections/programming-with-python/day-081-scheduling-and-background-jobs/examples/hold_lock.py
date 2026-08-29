"""Hold the job lock for a fixed number of seconds, then let go and exit.

This exists so the test suite can prove the overlap protection without racing:
start this, wait for it to say READY, run the real job, and assert the job
exits 75 having done nothing.

It always exits on its own. The test suite also waits for it explicitly, so
nothing is left running after the lab — that rule is not negotiable here.

    python3 examples/hold_lock.py /tmp/reports/daily-report.lock 2
"""

from __future__ import annotations

import sys
import time

from joblock import AlreadyRunning, job_lock


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: hold_lock.py <lock-path> <seconds>", file=sys.stderr)
        return 2
    path, seconds = argv[1], float(argv[2])
    try:
        with job_lock(path):
            print("READY", flush=True)
            time.sleep(seconds)
    except AlreadyRunning as exc:
        print(f"could not take the lock: {exc}", file=sys.stderr)
        return 75
    print("RELEASED", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
