"""The whole idea, in plain Python, before any database is involved.

    python3 scan_vs_bisect.py

An index is a second, sorted copy of some values that lets you find a row
by halving the search space instead of walking it. You do not need SQLite
to see what that buys — you need a list.

Two functions find the same value in the same data:

  * `scan`   walks from the front, comparing every element until it hits
             the one it wants. This is what a table scan is.
  * `seek`   uses `bisect`, the standard library's binary search, which
             halves the remaining range on every comparison. This is what
             an index seek is.

Both answer identically. Every lookup below is checked against the other
implementation and the script exits non-zero if they ever disagree, so
what follows is a difference in COST and never in ANSWER — which is the
single most important property of an index.

Two kinds of number are printed, and they are not equally trustworthy:

  * STEPS are counted, not timed. They are the same on every machine, in
    every year, in any language. This is the shape.
  * MICROSECONDS are measured on whatever computer you are sitting at.
    They will not match mine and are not supposed to.

Watch the steps column. Ten times the data costs the scan ten times the
work and costs the binary search about three more comparisons, because
three comparisons is what it takes to halve something ten times over.
"""

from __future__ import annotations

import bisect
import math
import random
import sys
import time

SEED = 20260816
SIZES = [
    (1_000, 2_000),
    (10_000, 500),
    (100_000, 100),
    (1_000_000, 20),
]


def scan(data, target):
    """A table scan: look at every element until you find it."""
    for position, value in enumerate(data):
        if value == target:
            return position
    return -1


def seek(data, target):
    """An index seek: binary search over the same values, kept sorted."""
    position = bisect.bisect_left(data, target)
    if position < len(data) and data[position] == target:
        return position
    return -1


def scan_steps(data, target):
    """How many comparisons the scan actually performed."""
    steps = 0
    for value in data:
        steps += 1
        if value == target:
            break
    return steps


def seek_steps(data, target):
    """How many comparisons a binary search performs. Hand-written so the
    count is visible rather than hidden inside bisect."""
    low, high, steps = 0, len(data), 0
    while low < high:
        steps += 1
        middle = (low + high) // 2
        if data[middle] < target:
            low = middle + 1
        else:
            high = middle
    return steps


def measure(size, lookups):
    data = list(range(0, size * 3, 3))  # sorted, with gaps, no duplicates
    rng = random.Random(SEED)
    targets = [data[rng.randrange(size)] for _ in range(lookups)]

    started = time.perf_counter()
    scan_answers = [scan(data, target) for target in targets]
    scan_us = (time.perf_counter() - started) / lookups * 1e6

    started = time.perf_counter()
    seek_answers = [seek(data, target) for target in targets]
    seek_us = (time.perf_counter() - started) / lookups * 1e6

    if scan_answers != seek_answers:
        raise AssertionError("scan and seek disagreed — an index changed an answer")

    return {
        "size": size,
        "lookups": lookups,
        "scan_us": scan_us,
        "seek_us": seek_us,
        "scan_steps": sum(scan_steps(data, t) for t in targets) / lookups,
        "seek_steps": sum(seek_steps(data, t) for t in targets) / lookups,
    }


def main() -> int:
    print("Finding one value among n, two ways. Same answers, different cost.")
    print(f"Seeded with {SEED}, so the targets are the same on every run.")
    print()
    header = (
        f"{'n':>11} | {'scan us':>9} | {'bisect us':>9} | {'faster':>8} |"
        f" {'scan steps':>11} | {'bisect steps':>12} | {'log2(n)':>7}"
    )
    print(header)
    print("-" * len(header))

    results = []
    for size, lookups in SIZES:
        row = measure(size, lookups)
        results.append(row)
        print(
            f"{row['size']:>11,} | {row['scan_us']:>9.2f} | {row['seek_us']:>9.3f} |"
            f" {row['scan_us'] / row['seek_us']:>7.0f}x |"
            f" {row['scan_steps']:>11,.0f} | {row['seek_steps']:>12.1f} |"
            f" {math.log2(row['size']):>7.1f}"
        )

    print()
    first, last = results[0], results[-1]
    growth = last["size"] / first["size"]
    print(f"The data grew {growth:,.0f}x between the first row and the last.")
    print(
        f"  scan steps grew   {last['scan_steps'] / first['scan_steps']:>8,.0f}x"
        "   — the same shape as the data. This is O(n)."
    )
    print(
        f"  bisect steps grew {last['seek_steps'] / first['seek_steps']:>8,.1f}x"
        "   — ten comparisons became twenty. This is O(log n)."
    )
    print()
    print("Every scan answer matched every bisect answer. Sorting the data")
    print("changed the work and not the result. That is what an index is.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
