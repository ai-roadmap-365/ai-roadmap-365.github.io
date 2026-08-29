#!/usr/bin/env python3
"""Summarise a list of numeric scores passed as command-line arguments.

This is the readable target of the Day 61 lab: the same behaviour as
``starter/messy.py``, but rewritten in small, named, type-hinted, documented
functions that follow PEP 8. It prints the count, mean, median, minimum,
maximum, population standard deviation, and the percentage of scores at or
above the pass mark.

All input comes from ``sys.argv``, so the tool can be scripted and tested
without a human at the keyboard:

    python3 report.py 70 85 90 55 60
"""
from __future__ import annotations

import sys

# A score at or above this mark counts as "passing". Naming the number gives
# it meaning and one place to change it, instead of a bare 60 in the code.
PASS_MARK = 60.0


def parse_scores(raw_values: list[str]) -> list[float]:
    """Convert the raw command-line strings into a list of floats."""
    return [float(value) for value in raw_values]


def mean(scores: list[float]) -> float:
    """Return the arithmetic mean of a non-empty list of scores."""
    return sum(scores) / len(scores)


def median(scores: list[float]) -> float:
    """Return the middle score, or the mean of the two middle scores."""
    ordered = sorted(scores)
    count = len(ordered)
    middle = count // 2
    if count % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def population_stdev(scores: list[float], average: float) -> float:
    """Return the population standard deviation around a known average."""
    variance = sum((score - average) ** 2 for score in scores) / len(scores)
    return variance ** 0.5


def passing_rate(scores: list[float]) -> float:
    """Return the percentage of scores at or above PASS_MARK."""
    passing = sum(1 for score in scores if score >= PASS_MARK)
    return 100 * passing / len(scores)


def format_report(scores: list[float]) -> str:
    """Build the multi-line summary report for a non-empty list of scores."""
    average = mean(scores)
    lines = [
        f"count: {len(scores)}",
        f"mean: {average:.2f}",
        f"median: {median(scores):.2f}",
        f"min: {min(scores):.2f}",
        f"max: {max(scores):.2f}",
        f"stdev: {population_stdev(scores, average):.2f}",
        f"passing: {passing_rate(scores):.1f}%",
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    """Parse scores from argv, print the report, and return an exit code."""
    scores = parse_scores(argv)
    if not scores:
        print("no data")
        return 1
    print(format_report(scores))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
