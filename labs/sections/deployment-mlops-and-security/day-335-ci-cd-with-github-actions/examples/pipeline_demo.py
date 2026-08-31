#!/usr/bin/env python3
"""One CI pipeline, read three ways: how long, how safe, how useful."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import (
    Job,
    Trigger,
    Workflow,
    critical_path,
    finish_times,
    review,
    savings_from_removing,
    total_minutes,
)

# A pipeline that grew one stage at a time, as they all do.
CURRENT = Workflow(
    "ci",
    triggers=[Trigger.PUSH, Trigger.PULL_REQUEST],
    jobs={
        "checkout":   Job("checkout", [], 0.3, caches=["git"], fails_per_100=0.1),
        "install":    Job("install", ["checkout"], 4.5, fails_per_100=0.4),
        "lint":       Job("lint", ["install"], 0.8, caches=["pip"], fails_per_100=6.0),
        "unit":       Job("unit", ["install"], 3.2, caches=["pip"], fails_per_100=9.0),
        "integration": Job("integration", ["install"], 6.5, caches=["pip"], fails_per_100=2.0),
        "licence-scan": Job("licence-scan", ["install"], 2.4, fails_per_100=0.0),
        "docs-build": Job("docs-build", ["install"], 3.1, fails_per_100=0.0),
        "deploy":     Job("deploy", ["unit", "integration", "lint"], 1.4,
                          uses_secrets=True, fails_per_100=0.6),
    },
)

# The same jobs, but triggered in the way that hands secrets to forks.
UNSAFE = Workflow(
    "ci-unsafe",
    triggers=[Trigger.PUSH, Trigger.PR_TARGET],
    jobs=CURRENT.jobs,
)


def show(label: str, wf: Workflow) -> None:
    path, wall = critical_path(wf)
    print(f"--- {label} ---")
    print(f"  wall clock   {wall} min   along {' -> '.join(path)}")
    print(f"  runner time  {total_minutes(wf)} min billed")
    print(f"  the gap      {round(total_minutes(wf) - wall, 2)} min of work happening in parallel")


def main() -> int:
    show("the pipeline as it stands", CURRENT)

    print("--- when each job finishes ---")
    for name, at in sorted(finish_times(CURRENT).items(), key=lambda kv: (kv[1], kv[0])):
        print(f"    {at:>5.1f} min  {name}")

    print("--- findings ---")
    for f in review(CURRENT):
        print(f"  [{f.rule}] {f.job}")
        print(f"      {f.message[:76]}")

    print("--- what removing each never-firing gate would buy ---")
    for name in ("licence-scan", "docs-build"):
        s = savings_from_removing(CURRENT, name)
        on = "on" if s["on_critical_path"] else "NOT on"
        print(f"  {name:<14} {on} the critical path   "
              f"wall {s['wall_before']} -> {s['wall_after']} (saves {s['wall_saved']})   "
              f"runner minutes saved {s['minutes_saved']}")

    print("--- what caching the install would buy instead ---")
    cached = Workflow(
        CURRENT.name, list(CURRENT.triggers),
        {n: (Job(j.name, list(j.needs), 0.8, j.uses_secrets, ["pip"], j.fails_per_100)
             if n == "install" else j)
         for n, j in CURRENT.jobs.items()},
    )
    _, before = critical_path(CURRENT)
    path_after, after = critical_path(cached)
    print(f"  install 4.5 -> 0.8 min (a dependency cache)")
    print(f"  wall {before} -> {after} min   saves {round(before - after, 2)} min per run")
    print(f"  new critical path: {' -> '.join(path_after)}")
    print(f"  deleting BOTH never-firing gates saved 0.0 min of wall clock;")
    print(f"  one cache on the critical path saves {round(before - after, 2)}.")

    print("--- the same jobs, triggered unsafely ---")
    unsafe = [f for f in review(UNSAFE) if f.rule == "secrets-exposed-to-forks"]
    for f in unsafe:
        print(f"  [{f.rule}] {f.job}")
        print(f"      {f.message[:76]}")
    print(f"  findings of this kind: {len(unsafe)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
