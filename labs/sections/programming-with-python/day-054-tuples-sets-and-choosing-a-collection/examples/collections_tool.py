#!/usr/bin/env python3
"""Choosing Collections — dedupe items and compute set algebra between two lists.

A complete, small, real program: it reads two comma-separated lists from the
command line, removes duplicates with a set, computes the set algebra between
them (common / only-in-A / only-in-B / symmetric difference), and reports the
results as immutable tuple records.

Usage:
    python3 collections_tool.py "<list A>" "<list B>"

Each list is a comma-separated string of items.

Example:
    python3 collections_tool.py "apple,banana,apple,cherry" "banana,cherry,date,date"
"""
import sys
from collections import namedtuple

# An immutable record of one comparison. namedtuple gives named fields on top
# of a plain tuple: it cannot be changed after creation, so it is a safe
# return value that callers cannot accidentally mutate.
SetReport = namedtuple("SetReport", ["common", "only_in_a", "only_in_b", "symmetric"])


def parse_items(text):
    """Split a comma-separated string into a tuple of cleaned items.

    Returns an immutable tuple (a fixed record of what was read), dropping
    blank entries and trimming surrounding spaces.
    """
    return tuple(part.strip() for part in text.split(",") if part.strip())


def dedupe(items):
    """Return the unique items as a sorted tuple.

    Building a set removes duplicates in one step (membership is O(1)); we
    sort so the output is deterministic, and return a tuple so the result is
    an immutable record.
    """
    return tuple(sorted(set(items)))


def compare(a_items, b_items):
    """Compute set algebra between two item collections.

    Returns an immutable SetReport of sorted tuples:
      common     = A & B  (intersection: in both)
      only_in_a  = A - B  (difference: in A, not B)
      only_in_b  = B - A  (difference: in B, not A)
      symmetric  = A ^ B  (symmetric difference: in exactly one)
    """
    a = set(a_items)
    b = set(b_items)
    return SetReport(
        common=tuple(sorted(a & b)),
        only_in_a=tuple(sorted(a - b)),
        only_in_b=tuple(sorted(b - a)),
        symmetric=tuple(sorted(a ^ b)),
    )


def format_report(a_items, b_items, report):
    """Return the multi-line, human-readable report string."""

    def show(values):
        return ", ".join(values) if values else "(none)"

    lines = [
        f"List A: {len(a_items)} items read, {len(set(a_items))} unique after dedupe",
        f"List B: {len(b_items)} items read, {len(set(b_items))} unique after dedupe",
        f"Common (A & B): {show(report.common)}",
        f"Only in A (A - B): {show(report.only_in_a)}",
        f"Only in B (B - A): {show(report.only_in_b)}",
        f"Symmetric difference (A ^ B): {show(report.symmetric)}",
    ]
    return "\n".join(lines)


def main(argv):
    """Entry point. Returns an exit code: 0 on success, 1 on bad input."""
    if len(argv[1:]) != 2:
        print('error: expected 2 arguments: "<list A>" "<list B>"', file=sys.stderr)
        print('usage: python3 collections_tool.py "a,b,c" "b,c,d"', file=sys.stderr)
        return 1
    a_items = parse_items(argv[1])
    b_items = parse_items(argv[2])
    if not a_items or not b_items:
        print("error: each list must contain at least one item", file=sys.stderr)
        print('usage: python3 collections_tool.py "a,b,c" "b,c,d"', file=sys.stderr)
        return 1
    report = compare(a_items, b_items)
    print(format_report(a_items, b_items, report))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
