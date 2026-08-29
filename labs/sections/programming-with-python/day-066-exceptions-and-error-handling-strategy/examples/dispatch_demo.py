#!/usr/bin/env python3
"""dispatch_demo.py — the @retry helper shown both ways.

Run it from the lab directory:

    python3 examples/dispatch_demo.py

First it calls dispatch(), which fails twice and then succeeds, so you see
backoff working. Then it calls dispatch_offline(), which never succeeds, so
you see the retries exhausted and DispatchError raised FROM the underlying
ConnectionError — the chained traceback with its
"The above exception was the direct cause of the following exception" line.

Both operations are deterministic: no randomness, no network, no clock
reading. The same run produces the same output every time.
"""

import traceback

import triage

COUNTS = {"immediate": 2, "urgent": 2, "routine": 1}

print("--- dispatch(): flaky, recovers on the third attempt ---")
print(triage.dispatch(COUNTS))

print()
print("--- dispatch_offline(): never recovers, gives up with chaining ---")
try:
    triage.dispatch_offline(COUNTS)
except triage.DispatchError:
    traceback.print_exc()
