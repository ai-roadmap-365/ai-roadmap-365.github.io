#!/usr/bin/env python3
"""raw_triage.py — the intake reader with NO error handling at all.

This script exists to be broken. It reads a JSON-lines intake file and adds
up the severity numbers. When anything goes wrong it does nothing about it,
so Python does the only thing it can: it unwinds the call stack and prints
a traceback. Reading those three tracebacks is Exercise 1 of the lab.

    python3 examples/raw_triage.py examples/samples/intake.jsonl
    python3 examples/raw_triage.py examples/samples/no-such-file.jsonl
    python3 examples/raw_triage.py examples/samples/bad-severity.jsonl
    python3 examples/raw_triage.py examples/samples/missing-field.jsonl
"""

import json
import sys


def read_severity(record):
    """Pull the severity out of one decoded record. Raises KeyError/ValueError."""
    return int(record["severity"])


def total_severity(path):
    """Open the file and add up every record's severity. Handles nothing."""
    total = 0
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            total += read_severity(json.loads(line))
    return total


def main(argv):
    if len(argv) < 2:
        print("usage: python3 raw_triage.py <records.jsonl>", file=sys.stderr)
        return 2
    print("total severity:", total_severity(argv[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
