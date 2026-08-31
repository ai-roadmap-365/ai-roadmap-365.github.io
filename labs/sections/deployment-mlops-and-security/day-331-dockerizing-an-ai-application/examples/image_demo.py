#!/usr/bin/env python3
"""The same AI service packaged three ways."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from image_plan import (
    Component,
    ImagePlan,
    Purpose,
    Stage,
    compare,
    pull_seconds,
    review,
    rollout_seconds,
)

NODES = 20

RUNTIME = [
    Component("torch", Purpose.RUNTIME),
    Component("transformers", Purpose.RUNTIME),
    Component("fastapi", Purpose.RUNTIME),
    Component("app-code", Purpose.RUNTIME),
]

# 1. One stage, full base, build tools and weights all in the shipped image.
NAIVE = ImagePlan(
    stages=[
        Stage("final", "python-full", [
            Component("build-essential", Purpose.BUILD),
            Component("cuda-devel", Purpose.BUILD),
            *RUNTIME,
            Component("model-weights-7b", Purpose.DATA),
        ])
    ],
    final_stage="final",
)

# 2. Multi-stage: compile in a builder, ship a slim runtime. Weights still in.
STAGED = ImagePlan(
    stages=[
        Stage("builder", "python-full", [
            Component("build-essential", Purpose.BUILD),
            Component("cuda-devel", Purpose.BUILD),
        ]),
        Stage("final", "python-slim", [
            Component("cuda-runtime", Purpose.RUNTIME),
            *RUNTIME,
            Component("model-weights-7b", Purpose.DATA),
        ]),
    ],
    final_stage="final",
)

# 3. Same as 2, with the weights mounted at run time instead of baked in.
MOUNTED = ImagePlan(
    stages=[
        Stage("builder", "python-full", [
            Component("build-essential", Purpose.BUILD),
            Component("cuda-devel", Purpose.BUILD),
        ]),
        Stage("final", "python-slim", [
            Component("cuda-runtime", Purpose.RUNTIME),
            *RUNTIME,
        ]),
    ],
    final_stage="final",
)


def show(name: str, plan: ImagePlan) -> None:
    print(f"--- {name} ---")
    print(f"  image {plan.size_mb:>6} MB   one pull {pull_seconds(plan.size_mb):>7.1f}s"
          f"   rollout to {NODES} nodes {rollout_seconds(plan.size_mb, NODES):>8.1f}s")
    found = review(plan)
    for f in found:
        print(f"  [{f.rule}] saves {f.saves_mb} MB")
        print(f"      {f.message[:78]}")
    if not found:
        print("  no findings")


def main() -> int:
    show("1. single stage, full base, weights baked in", NAIVE)
    show("2. multi-stage, slim runtime, weights baked in", STAGED)
    show("3. multi-stage, slim runtime, weights mounted", MOUNTED)

    print("--- what each change bought ---")
    a = compare(NAIVE, STAGED, nodes=NODES)
    print(f"  multi-stage      {a['before_mb']:>6} -> {a['after_mb']:>6} MB  "
          f"({a['saved_mb']} MB, {a['ratio']}x)")
    b = compare(STAGED, MOUNTED, nodes=NODES)
    print(f"  mount the weights{b['before_mb']:>6} -> {b['after_mb']:>6} MB  "
          f"({b['saved_mb']} MB, {b['ratio']}x)")
    c = compare(NAIVE, MOUNTED, nodes=NODES)
    print(f"  both             {c['before_mb']:>6} -> {c['after_mb']:>6} MB  "
          f"({c['saved_mb']} MB, {c['ratio']}x)")
    print(f"  rollout to {NODES} nodes: {c['before_rollout_s']:.0f}s -> {c['after_rollout_s']:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
