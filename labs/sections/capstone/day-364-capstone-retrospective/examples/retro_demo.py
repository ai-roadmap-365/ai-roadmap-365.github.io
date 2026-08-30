#!/usr/bin/env python3
"""A capstone's record, turned into findings."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from retro import (
    Caught,
    Incident,
    Task,
    apply_multiplier,
    by_area,
    calibration,
    detection,
    findings,
    is_uniform,
)

TASKS = [
    Task("ingestion pipeline", "familiar", 8, 9),
    Task("chunking and index", "familiar", 6, 7),
    Task("retrieval endpoint", "familiar", 4, 4),
    Task("eval harness", "familiar", 5, 6),
    Task("agent tool calling", "unfamiliar", 6, 20),
    Task("streaming frontend", "unfamiliar", 8, 26),
    Task("deployment and rollback", "unfamiliar", 4, 15),
]

INCIDENTS = [
    Incident("chunk ids not stable, index doubled", Caught.TESTS),
    Incident("secret committed to the repository", Caught.REVIEW),
    Incident("readiness probe missing, served errors", Caught.STAGING),
    Incident("spend spike from a retry loop", Caught.MONITORING, preventable_by="a per-request cap"),
    Incident("answers citing nothing after an index rebuild", Caught.USER,
             preventable_by="a groundedness signal"),
]


def main() -> int:
    cal = calibration(TASKS)
    print("--- calibration ---")
    print(f"  {cal.line()}")
    print(f"  uniform across areas: {is_uniform(TASKS)}")
    print("  median ratio by area:")
    for area, ratio in sorted(by_area(TASKS).items()):
        print(f"    {area:<12} {ratio:.2f}x")

    print("--- what a future estimate becomes ---")
    for hours in (4, 10, 40):
        print(f"    {hours:>3}h estimated  ->  {apply_multiplier(hours, cal):>5}h expected")

    print("--- detection ---")
    print(f"  {detection(INCIDENTS).summary()}")

    print("--- findings ---")
    for finding in findings(TASKS, INCIDENTS):
        print(f"  - {finding}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
