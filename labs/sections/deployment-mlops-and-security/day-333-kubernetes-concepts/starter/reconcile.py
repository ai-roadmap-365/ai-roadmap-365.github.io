"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.

Kubernetes as one idea: a loop that moves actual state toward desired state.

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
    PENDING = 'Pending'
    RUNNING = 'Running'
    FAILED = 'Failed'

@dataclass
class Pod:
    name: str
    image: str
    phase: Phase = Phase.PENDING
    ready: bool = False
    node: str = 'node-a'

    @property
    def serving(self) -> bool:
        """A Service routes here only if the pod is BOTH running and ready."""
        raise NotImplementedError('TASK 1: implement serving. A Service routes here only if the pod is BOTH running and ready.')

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
    verb: str
    pod: str
    reason: str

@dataclass
class Cluster:
    pods: list[Pod] = field(default_factory=list)
    nodes: list[str] = field(default_factory=lambda: ['node-a', 'node-b', 'node-c'])
    dead_nodes: set[str] = field(default_factory=set)
    _seq: int = 0

    def schedule(self) -> str:
        """Pick a node for a new pod. Live nodes only.

        Without this the loop places replacements on the node that just died,
        reaps them next step, and churns forever -- which is a real failure
        mode when a scheduler's node filter is wrong, not an artefact.
        """
        raise NotImplementedError('TASK 2: implement schedule. Pick a node for a new pod. Live nodes only.')

    def alive(self, deployment: Deployment) -> list[Pod]:
        """Pods belonging to this deployment that are not doomed."""
        raise NotImplementedError('TASK 3: implement alive. Pods belonging to this deployment that are not doomed.')

    def owned(self, deployment: Deployment) -> list[Pod]:
        raise NotImplementedError('TASK 4: implement owned.')

    def serving(self, deployment: Deployment) -> list[Pod]:
        """What a Service would actually route traffic to."""
        raise NotImplementedError('TASK 5: implement serving. What a Service would actually route traffic to.')

    def next_name(self, deployment: Deployment) -> str:
        raise NotImplementedError('TASK 6: implement next_name.')

def reconcile(cluster: Cluster, deployment: Deployment) -> list[Action]:
    """One step of the loop. Compare, then act. Never ask how we got here.

    Deliberately returns a SINGLE step's worth of actions rather than looping
    to convergence -- the loop runs forever in a real cluster, and modelling one
    step is what makes the "it just notices again" behaviour visible.
    """
    raise NotImplementedError('TASK 7: implement reconcile. One step of the loop. Compare, then act. Never ask how we got here.')

def apply(cluster: Cluster, actions: list[Action], deployment: Deployment) -> None:
    """Carry out one step's actions. New pods start Pending and not ready."""
    raise NotImplementedError("TASK 8: implement apply. Carry out one step's actions. New pods start Pending and not ready.")

def tick(cluster: Cluster) -> None:
    """Time passes: pending pods start, running pods pass their probe."""
    raise NotImplementedError('TASK 9: implement tick. Time passes: pending pods start, running pods pass their probe.')

def rollout_done(cluster: Cluster, deployment: Deployment) -> bool:
    """Whether every serving pod runs the desired image, at full replica count.

    Distinct from "reconcile returned no actions". A step can legitimately have
    nothing to do while old pods are still running -- the controller is waiting
    for the new ones to pass their readiness probe before it is allowed to
    retire any more. That pause is maxUnavailable doing its job.
    """
    raise NotImplementedError('TASK 10: implement rollout_done. Whether every serving pod runs the desired image, at full replica count.')

def converge(cluster: Cluster, deployment: Deployment, *, max_steps: int=20) -> int:
    """Run until the spec is satisfied AND every pod is serving.

    Two conditions, not one. A cluster with the right number of Running pods
    has satisfied the spec and may still be routing traffic to none of them,
    because readiness is a separate signal that arrives later.
    """
    raise NotImplementedError('TASK 11: implement converge. Run until the spec is satisfied AND every pod is serving.')
