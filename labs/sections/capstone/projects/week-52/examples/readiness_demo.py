#!/usr/bin/env python3
"""A capstone that feels finished, put through the delivery gate."""

from __future__ import annotations

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from readiness import Evidence, Kind, Requirement, assess, evidence_for, findings

TODAY = date(2026, 8, 31)

# Week 52, one requirement per day, plus the two that carry the most risk.
REQUIREMENTS = [
    Requirement("frontend", 358, "A usable interface"),
    Requirement("deployed", 359, "Deployed and reachable"),
    Requirement("rollback", 359, "A rollback that has been exercised"),
    Requirement("monitoring", 360, "Monitoring on latency and errors"),
    Requirement("spend-cap", 360, "A hard spend cap"),
    Requirement("security", 361, "Security review completed"),
    Requirement("secrets", 361, "No secrets in repository history"),
    Requirement("docs", 362, "Documentation somebody else can follow"),
    Requirement("demo", 362, "A demo that runs"),
    Requirement("portfolio", 363, "Claims a stranger can assess", False),
]

DELIVERY = [
    Evidence("frontend", Kind.URL, "https://example.com/capstone", date(2026, 8, 29)),
    Evidence("deployed", Kind.COMMAND, "curl -f $URL/healthz", date(2026, 8, 30)),
    Evidence("rollback", Kind.ASSERTION, "rollback is configured"),
    Evidence("monitoring", Kind.URL, "https://example.com/dashboard", date(2026, 8, 30)),
    # Nothing at all for spend-cap. It is the one nobody remembers.
    Evidence("security", Kind.FILE, "security-review.md"),
    Evidence("secrets", Kind.COMMAND, "gitleaks detect --no-git=false", date(2026, 6, 14)),
    Evidence("docs", Kind.FILE, "README.md"),
    # Two for the demo: the assertion should lose to the command.
    Evidence("demo", Kind.ASSERTION, "the demo works"),
    Evidence("demo", Kind.COMMAND, "bash scripts/demo.sh", date(2026, 8, 28)),
    Evidence("portfolio", Kind.ASSERTION, "portfolio updated"),
]


def main() -> int:
    report = assess(REQUIREMENTS, DELIVERY, TODAY)
    print("--- delivery gate ---")
    print(f"  {report.summary()}")

    print("--- by requirement ---")
    for group, label in (
        (report.solid, "solid  "),
        (report.stale, "stale  "),
        (report.weak, "weak   "),
        (report.missing, "missing"),
    ):
        for req in group:
            found = evidence_for(req, DELIVERY)
            kind = found.kind.value if found else "-"
            flag = "!" if req.blocking else " "
            print(f"  {label} {flag} day {req.day}  {req.title:<38} {kind}")

    print("--- findings ---")
    for finding in findings(REQUIREMENTS, DELIVERY, TODAY):
        print(f"  - {finding}")
    return 0 if report.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
