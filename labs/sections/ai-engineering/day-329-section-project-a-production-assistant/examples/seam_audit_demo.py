#!/usr/bin/env python3
"""Audit two assistants: one that conforms, one that does not."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from seam_audit import BrokenAssistant, ConformantAssistant, audit


def main() -> int:
    for label, factory in (
        ("conformant assistant", ConformantAssistant),
        ("broken assistant", BrokenAssistant),
    ):
        report = audit(factory)
        print(f"--- {label} ---")
        for check in report.checks:
            print(check.line())
        print(report.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
