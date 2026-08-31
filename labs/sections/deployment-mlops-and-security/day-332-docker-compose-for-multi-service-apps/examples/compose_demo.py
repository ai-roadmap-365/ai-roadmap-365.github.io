#!/usr/bin/env python3
"""One AI stack, wired two ways."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compose_graph import (
    Condition,
    Dependency,
    Service,
    find_cycles,
    ready_times,
    review,
    startup_order,
)


def stack(condition: Condition, healthchecks: bool) -> dict[str, Service]:
    """api -> (postgres, qdrant), worker -> (postgres, api)."""
    return {
        "postgres": Service(
            "postgres", "postgres:16", ports=[(5432, 5432)],
            healthcheck=healthchecks, start_seconds=0.4, ready_seconds=4.0,
        ),
        "qdrant": Service(
            "qdrant", "qdrant/qdrant:v1.12", ports=[(6333, 6333)],
            healthcheck=healthchecks, start_seconds=0.3, ready_seconds=2.0,
        ),
        "api": Service(
            "api", "app/api:1.4", ports=[(8000, 8000)],
            depends_on=[Dependency("postgres", condition), Dependency("qdrant", condition)],
            healthcheck=healthchecks, start_seconds=0.2, ready_seconds=0.6,
        ),
        "worker": Service(
            "worker", "app/worker:1.4",
            depends_on=[Dependency("postgres", condition), Dependency("api", condition)],
            start_seconds=0.2, ready_seconds=0.4,
        ),
    }


NAIVE = stack(Condition.STARTED, healthchecks=False)
CORRECT = stack(Condition.HEALTHY, healthchecks=True)

# A file nobody can start, plus a host port claimed twice.
BROKEN = {
    "api": Service("api", "app/api:1.4", ports=[(8000, 8000)],
                   depends_on=[Dependency("worker")]),
    "worker": Service("worker", "app/worker:1.4", ports=[(8000, 8080)],
                      depends_on=[Dependency("api")]),
    "ghost": Service("ghost", "app/ghost:1.0", depends_on=[Dependency("nowhere")]),
}


def show(name: str, services: dict[str, Service]) -> None:
    print(f"--- {name} ---")
    try:
        print(f"  start order  {' -> '.join(startup_order(services))}")
        times = ready_times(services)
        print("  usable at    " + "  ".join(f"{k} {v}s" for k, v in sorted(times.items())))
    except ValueError as exc:
        print(f"  cannot start: {exc}")
    found = review(services)
    for f in found:
        print(f"  [{f.rule}] {f.service}")
        print(f"      {f.message[:76]}")
    if not found:
        print("  no findings")


def main() -> int:
    show("depends_on with no condition", NAIVE)
    show("depends_on: service_healthy", CORRECT)
    show("a file that cannot start", BROKEN)

    n, c = ready_times(NAIVE), ready_times(CORRECT)
    print("--- what the condition changed ---")
    print(f"  api usable at    {n['api']}s  ->  {c['api']}s")
    print(f"  worker usable at {n['worker']}s  ->  {c['worker']}s")
    print(f"  premature starts {sum(1 for f in review(NAIVE) if f.rule == 'starts-before-ready')}"
          f"  ->  {sum(1 for f in review(CORRECT) if f.rule == 'starts-before-ready')}")
    print(f"  cycles in the broken file: {find_cycles(BROKEN)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
