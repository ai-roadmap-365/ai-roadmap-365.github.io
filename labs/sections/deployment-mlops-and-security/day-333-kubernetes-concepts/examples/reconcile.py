"""Kubernetes as one idea: a loop that moves actual state toward desired state.

Offline and standard-library only. No cluster is required, because the thing
worth understanding is not the YAML -- it is the control loop, and the loop is
about forty lines.

Everything else follows from it:

  you declare    3 replicas of image app:1.4
  the loop sees  2 running, 1 of them on a dead node
  the loop acts  delete the dead one, create two

It never asks how it got there. It compares what you asked for against what
exists and takes one step. That is why `kubectl delete pod` is not destructive
-- the loop simply notices the gap again and refills it -- and why a rolling
update is not a special operation but the same loop with a changed spec.

Readiness is the second idea. A pod that is Running is not necessarily able to
serve, and a Service routes only to pods that are READY. Yesterday's Compose
lesson had the same distinction; Kubernetes makes it explicit and continuous.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Phase(str, Enum):
    PENDING = "Pending"      # accepted, not yet running
    RUNNING = "Running"      # the container is up
    FAILED = "Failed"        # exited non-zero, or its node went away


@dataclass
class Pod:
    name: str
    image: str
    phase: Phase = Phase.PENDING
    ready: bool = False       # the readiness probe passes
    node: str = "node-a"

    @property
    def serving(self) -> bool:
        """A Service routes here only if the pod is BOTH running and ready."""
        return self.phase is Phase.RUNNING and self.ready


@dataclass
class Deployment:
    """The desired state. Note it says nothing about how to get there."""

    name: str
    image: str
    replicas: int
    max_unavailable: int = 1
    max_surge: int = 1


@dataclass
class Action:
    verb: str      # create | delete
    pod: str
    reason: str


@dataclass
class Cluster:
    pods: list[Pod] = field(default_factory=list)
    nodes: list[str] = field(default_factory=lambda: ["node-a", "node-b", "node-c"])
    dead_nodes: set[str] = field(default_factory=set)
    _seq: int = 0

    def schedule(self) -> str:
        """Pick a node for a new pod. Live nodes only.

        Without this the loop places replacements on the node that just died,
        reaps them next step, and churns forever -- which is a real failure
        mode when a scheduler's node filter is wrong, not an artefact.
        """
        live = [n for n in self.nodes if n not in self.dead_nodes]
        if not live:
            raise RuntimeError("no live node to schedule onto")
        counts = {n: sum(1 for p in self.pods if p.node == n) for n in live}
        return min(live, key=lambda n: (counts[n], n))

    def alive(self, deployment: Deployment) -> list[Pod]:
        """Pods belonging to this deployment that are not doomed."""
        return [
            p for p in self.pods
            if p.name.startswith(deployment.name + "-")
            and p.phase is not Phase.FAILED
            and p.node not in self.dead_nodes
        ]

    def owned(self, deployment: Deployment) -> list[Pod]:
        return [p for p in self.pods if p.name.startswith(deployment.name + "-")]

    def serving(self, deployment: Deployment) -> list[Pod]:
        """What a Service would actually route traffic to."""
        return [p for p in self.alive(deployment) if p.serving]

    def next_name(self, deployment: Deployment) -> str:
        self._seq += 1
        return f"{deployment.name}-{self._seq:03d}"


def reconcile(cluster: Cluster, deployment: Deployment) -> list[Action]:
    """One step of the loop. Compare, then act. Never ask how we got here.

    Deliberately returns a SINGLE step's worth of actions rather than looping
    to convergence -- the loop runs forever in a real cluster, and modelling one
    step is what makes the "it just notices again" behaviour visible.
    """
    actions: list[Action] = []

    # 1. Reap anything failed or stranded on a dead node.
    for pod in cluster.owned(deployment):
        if pod.phase is Phase.FAILED:
            actions.append(Action("delete", pod.name, "pod failed"))
        elif pod.node in cluster.dead_nodes:
            actions.append(Action("delete", pod.name, f"node {pod.node} is gone"))

    # 2. Anything running the wrong image is replaced, respecting the surge
    #    and unavailability budget so the service stays up during a rollout.
    healthy = [p for p in cluster.alive(deployment) if p.image == deployment.image]
    stale = [p for p in cluster.alive(deployment) if p.image != deployment.image]
    serving_now = len([p for p in cluster.alive(deployment) if p.serving])
    budget = max(0, serving_now - (deployment.replicas - deployment.max_unavailable))
    for pod in stale[:budget]:
        actions.append(Action("delete", pod.name, f"image {pod.image} != {deployment.image}"))

    # 3. Create what is missing, without exceeding the surge ceiling.
    #    Two limits apply at once and both matter: we need `replicas` pods on
    #    the new image eventually, and we may not hold more than
    #    replicas + max_surge pods at any moment during a rollout.
    kept = len(healthy) + max(0, len(stale) - budget)
    ceiling = deployment.replicas + (deployment.max_surge if stale else 0)
    wanted = min(deployment.replicas - len(healthy), ceiling - kept)
    for _ in range(max(0, wanted)):
        actions.append(
            Action("create", cluster.next_name(deployment),
                   f"{kept} of {deployment.replicas} replicas present")
        )
        kept += 1
    return actions


def apply(cluster: Cluster, actions: list[Action], deployment: Deployment) -> None:
    """Carry out one step's actions. New pods start Pending and not ready."""
    for act in actions:
        if act.verb == "delete":
            cluster.pods = [p for p in cluster.pods if p.name != act.pod]
        elif act.verb == "create":
            cluster.pods.append(
                Pod(act.pod, deployment.image, Phase.PENDING, False, cluster.schedule())
            )


def tick(cluster: Cluster) -> None:
    """Time passes: pending pods start, running pods pass their probe."""
    for pod in cluster.pods:
        if pod.phase is Phase.PENDING:
            pod.phase = Phase.RUNNING
        elif pod.phase is Phase.RUNNING and not pod.ready:
            pod.ready = True


def rollout_done(cluster: Cluster, deployment: Deployment) -> bool:
    """Whether every serving pod runs the desired image, at full replica count.

    Distinct from "reconcile returned no actions". A step can legitimately have
    nothing to do while old pods are still running -- the controller is waiting
    for the new ones to pass their readiness probe before it is allowed to
    retire any more. That pause is maxUnavailable doing its job.
    """
    pods = cluster.alive(deployment)
    return (
        len(pods) == deployment.replicas
        and all(p.image == deployment.image and p.serving for p in pods)
    )


def converge(cluster: Cluster, deployment: Deployment, *, max_steps: int = 20) -> int:
    """Run until the spec is satisfied AND every pod is serving.

    Two conditions, not one. A cluster with the right number of Running pods
    has satisfied the spec and may still be routing traffic to none of them,
    because readiness is a separate signal that arrives later.
    """
    for step in range(1, max_steps + 1):
        actions = reconcile(cluster, deployment)
        if not actions and rollout_done(cluster, deployment):
            return step - 1
        apply(cluster, actions, deployment)
        tick(cluster)
    raise RuntimeError("did not converge; the desired state may be unreachable")
