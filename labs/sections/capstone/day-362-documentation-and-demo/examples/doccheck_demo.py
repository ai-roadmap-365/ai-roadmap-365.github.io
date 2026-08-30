#!/usr/bin/env python3
"""Check a good README and a drifted one against the same project."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from doccheck import review
from fixtures import DRIFTED_README, GOOD_README, PROJECT


def show(label: str, readme: str) -> None:
    report = review(readme, PROJECT)
    print(f"--- {label} ---")
    for issue in report.issues:
        print(issue.line())
    print(f"  => {report.summary()}")


def main() -> int:
    show("current README", GOOD_README)
    show("README after six months of drift", DRIFTED_README)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
