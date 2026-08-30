#!/usr/bin/env python3
"""Sweep nprobe and show what recall costs."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from retrieval import make_vectors, sweep_nprobe


def main() -> int:
    vectors = make_vectors(2000, dim=32, seed=7, clusters=8)
    queries = make_vectors(20, dim=32, seed=99, clusters=8)

    sweep = sweep_nprobe(vectors, queries, k=10, nlist=8)
    print(f"corpus=2000 dim=32 queries=20 k=10 nlist=8")
    print(f"exact search cost: {sweep.baseline_comparisons} comparisons")
    for row in sweep.rows:
        print(row.line(sweep.baseline_comparisons))

    for target in (0.90, 0.95, 0.99):
        row = sweep.cheapest_meeting(target)
        if row is None:
            print(f"recall>={target:.2f}: not reached at any nprobe")
        else:
            speedup = sweep.baseline_comparisons / row.comparisons
            print(
                f"recall>={target:.2f}: nprobe={row.nprobe} "
                f"({speedup:.1f}x cheaper than exact)"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
