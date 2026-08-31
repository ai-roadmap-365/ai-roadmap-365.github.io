#!/usr/bin/env python3
"""The same loop handles a first deploy, a lost node, a manual delete, and a rollout."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reconcile import (
    Cluster, Deployment, Phase, Pod, apply, converge, reconcile, rollout_done, tick,
)


def line(cluster: Cluster, dep: Deployment) -> str:
    alive = cluster.alive(dep)
    return (f"{len(alive)} alive, {len(cluster.serving(dep))} serving  "
            + " ".join(f"{p.name}({p.image.split(':')[-1]})" for p in alive))


def step(cluster: Cluster, dep: Deployment, label: str) -> None:
    actions = reconcile(cluster, dep)
    print(f"  {label}")
    for a in actions:
        print(f"      {a.verb:<6} {a.pod:<12} {a.reason}")
    if not actions:
        print("      (nothing to do — actual state matches desired)")
    apply(cluster, actions, dep)
    tick(cluster)
    print(f"      -> {line(cluster, dep)}")


def main() -> int:
    dep = Deployment("api", "app:1.4", replicas=3)
    cluster = Cluster()

    print("--- 1. first deploy: nothing exists yet ---")
    steps = converge(cluster, dep)
    print(f"  converged in {steps} steps -> {line(cluster, dep)}")

    print("--- 2. a node dies, taking one pod with it ---")
    cluster.dead_nodes.add("node-a")
    cluster.pods[0].node = "node-a"
    for p in cluster.pods[1:]:
        p.node = "node-b"
    step(cluster, dep, "the loop compares and acts:")
    print(f"  converged in {converge(cluster, dep)} more steps -> {line(cluster, dep)}")

    print("--- 3. somebody deletes a pod by hand ---")
    removed = cluster.pods[0].name
    cluster.pods = cluster.pods[1:]
    print(f"  deleted {removed} manually")
    step(cluster, dep, "the loop does not care how it happened:")
    print(f"  converged in {converge(cluster, dep)} more steps -> {line(cluster, dep)}")

    print("--- 4. a rolling update to app:1.5 ---")
    dep.image = "app:1.5"
    served = []
    for i in range(1, 10):
        if rollout_done(cluster, dep):
            print(f"  step {i}: rollout complete — every pod on {dep.image}")
            break
        actions = reconcile(cluster, dep)
        apply(cluster, actions, dep)
        tick(cluster)
        n = len(cluster.serving(dep))
        served.append(n)
        note = "" if actions else "  (no action — waiting for the new pods to become ready)"
        print(f"  step {i}: {len(actions)} action(s)  -> {line(cluster, dep)}{note}")
    print(f"  serving during rollout: {served}  minimum {min(served) if served else 0}")
    print(f"  never dropped below max_unavailable allows: "
          f"{dep.replicas - dep.max_unavailable} required, {min(served) if served else 0} observed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
