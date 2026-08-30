#!/usr/bin/env python3
"""Process the synthetic corpus and print one line per document."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from corpus import build_corpus
from process import format_line, process_all


def main() -> int:
    report = process_all(build_corpus())
    for result in report.results:
        print(format_line(result))
    print(report.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
