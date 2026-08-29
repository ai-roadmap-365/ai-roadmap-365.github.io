#!/usr/bin/env python3
"""swallowing.py — the SAME reader, wrapped in a bare except. Do not copy this.

This is the "before" picture of the lab: a script that catches everything,
says nothing, and reports success no matter what happened. Run it on a file
that does not exist and it still prints "done" and exits 0 — the failure is
completely invisible to you and to any script that calls it.

    python3 examples/swallowing.py examples/samples/no-such-file.jsonl ; echo "exit: $?"
    python3 examples/swallowing.py examples/samples/bad-severity.jsonl ; echo "exit: $?"

Every line marked WRONG below is an anti-pattern the lesson names. Your job
in the lab is to rebuild this program's error strategy in starter/triage.py.
"""

import json
import sys

total = 0

try:
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            total += int(json.loads(line)["severity"])
except:  # WRONG: bare except catches everything, including KeyboardInterrupt
    pass  # WRONG: and then says nothing at all about it

print("total severity:", total)
print("done")
sys.exit(0)  # WRONG: reports success whatever happened
