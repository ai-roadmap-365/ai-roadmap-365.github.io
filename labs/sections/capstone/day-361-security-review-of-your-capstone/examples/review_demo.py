#!/usr/bin/env python3
"""Review a sound posture and a deliberately weak one."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from review import SOUND, WEAK, Posture, Severity, review


def show(label: str, posture: Posture) -> None:
    report = review(posture)
    print(f"--- {label} ---")
    for finding in report.findings:
        print(finding.line())
    print(f"  => {report.summary()}")


def main() -> int:
    show("sound posture", SOUND)
    show("weak posture", WEAK)

    print("--- one change at a time ---")
    for label, posture in (
        ("drop the spend caps", Posture(per_request_cap=None, per_user_daily_cap=None)),
        ("grant delete without confirmation", Posture(tool_scopes=("read:docs", "delete:records"))),
        ("keep traces forever", Posture(trace_retention_days=None)),
    ):
        report = review(posture)
        highs = [f.check for f in report.at_least(Severity.HIGH)]
        print(f"  {label:<38} {report.summary():<32} {highs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
