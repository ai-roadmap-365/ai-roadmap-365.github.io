#!/usr/bin/env python3
"""Twenty-five minutes of traffic with three problems buried in it."""

from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitoring import Request, evaluate, rolling_baseline, windows


def build_traffic() -> list[Request]:
    """Five windows: two healthy, then latency, quality and cost problems."""
    rng = random.Random(11)
    out: list[Request] = []

    def batch(at_from: int, n: int, *, slow=False, errors=0.0, ungrounded=0.0, pricey=False):
        for i in range(n):
            at = at_from + i % 5
            latency = rng.randint(3800, 9000) if slow else rng.randint(300, 1500)
            out.append(
                Request(
                    at=at,
                    latency_ms=latency,
                    ok=rng.random() >= errors,
                    cost=(0.02 if pricey else 0.0015),
                    tokens=rng.randint(400, 900),
                    grounded=rng.random() >= ungrounded,
                )
            )

    batch(0, 20)                      # healthy
    batch(5, 20)                      # healthy
    batch(10, 20, slow=True)          # latency problem
    batch(15, 20, ungrounded=0.45)    # quality problem, all 200s
    batch(20, 20, pricey=True)        # cost problem
    return out


def main() -> int:
    traffic = build_traffic()
    history = []
    for window in windows(traffic, size=5):
        baseline = rolling_baseline(history)
        alerts = evaluate(window, baseline_spend=baseline)
        print(window.line())
        for alert in alerts:
            print(alert.line())
        history.append(window)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
