#!/usr/bin/env python3
"""A plausible post-course plan, checked before week one."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plan import Commitment, findings, review

# Six commitments. Every one of them sounds modest on its own.
PLAN = [
    Commitment(
        topic="evaluation harness for my capstone",
        next_action="build a 50-question eval set and run it weekly",
        artifact="eval suite in the capstone repository",
        hours_per_week=3,
        weeks=8,
        priority=1,
    ),
    Commitment(
        topic="fine-tuning",
        next_action="learn how LoRA works",
        artifact="",
        hours_per_week=4,
        weeks=6,
        priority=3,
    ),
    Commitment(
        topic="open-source contribution",
        next_action="fix one documented issue in a retrieval library",
        artifact="a merged pull request",
        hours_per_week=2,
        weeks=12,
        priority=2,
    ),
    Commitment(
        topic="agent frameworks",
        next_action="explore the main agent frameworks",
        artifact="",
        hours_per_week=3,
        weeks=6,
        priority=4,
    ),
    Commitment(
        topic="writing about the work",
        next_action="publish one post on what the capstone retrospective found",
        artifact="a published post",
        hours_per_week=1,
        weeks=4,
        priority=2,
    ),
    Commitment(
        topic="systems and scaling",
        next_action="get better at distributed systems",
        artifact="",
        hours_per_week=4,
        weeks=10,
        priority=5,
    ),
]

AVAILABLE_HOURS = 5.0
MY_CALIBRATION = 1.20  # measured on day 364


def main() -> int:
    plain = review(PLAN, AVAILABLE_HOURS)
    print("--- as written ---")
    print(f"  {plain.load.line()}")
    print(f"  {plain.summary()}")

    costed = review(PLAN, AVAILABLE_HOURS, calibration=MY_CALIBRATION)
    print("--- in my own hours ---")
    print(f"  {costed.load.line()}")
    print(f"  {costed.summary()}")

    print("--- what survives ---")
    for c in costed.kept:
        print(f"  keep  p{c.priority}  {c.hours_per_week:>4.1f}h/wk  {c.topic}")
    for c in costed.cut:
        print(f"  cut   p{c.priority}  {c.hours_per_week:>4.1f}h/wk  {c.topic}")

    print("--- findings ---")
    for finding in findings(PLAN, AVAILABLE_HOURS, calibration=MY_CALIBRATION):
        print(f"  - {finding}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
