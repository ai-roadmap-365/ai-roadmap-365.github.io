"""Grouped by what the control loop decides.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "examples"))

from reconcile import (  # noqa: E402
    Cluster,
    Deployment,
    Phase,
    Pod,
    apply,
    converge,
    reconcile,
    rollout_done,
    tick,
)


def dep(replicas=3, image="app:1.4", **kw):
    return Deployment("api", image, replicas, **kw)


def running(name, image="app:1.4", ready=True, node="node-b"):
    return Pod(name, image, Phase.RUNNING, ready, node)


# ------------------------------------------------------------------ serving


def test_a_pod_must_be_both_running_and_ready_to_serve():
    assert running("api-1").serving
    assert not Pod("api-2", "app:1.4", Phase.RUNNING, False).serving
    assert not Pod("api-3", "app:1.4", Phase.PENDING, True).serving


def test_a_failed_pod_never_serves():
    assert not Pod("api-4", "app:1.4", Phase.FAILED, True).serving


# ------------------------------------------------------------ first deploy


def test_an_empty_cluster_creates_every_replica():
    actions = reconcile(Cluster(), dep(replicas=3))
    assert [a.verb for a in actions] == ["create"] * 3


def test_a_satisfied_deployment_produces_no_actions():
    c = Cluster(pods=[running(f"api-{i}") for i in range(3)])
    assert reconcile(c, dep(replicas=3)) == []


def test_convergence_reaches_the_declared_replica_count():
    c = Cluster()
    d = dep(replicas=4)
    converge(c, d)
    assert len(c.serving(d)) == 4


# ----------------------------------------------------------------- healing


def test_a_failed_pod_is_reaped_and_replaced():
    c = Cluster(pods=[running("api-1"), Pod("api-2", "app:1.4", Phase.FAILED)])
    actions = reconcile(c, dep(replicas=2))
    assert any(a.verb == "delete" and a.pod == "api-2" for a in actions)
    assert any(a.verb == "create" for a in actions)


def test_a_pod_on_a_dead_node_is_reaped():
    c = Cluster(pods=[running("api-1", node="node-a")], dead_nodes={"node-a"})
    actions = reconcile(c, dep(replicas=1))
    assert any(a.verb == "delete" and "node-a" in a.reason for a in actions)


def test_a_manual_delete_is_simply_refilled():
    # The loop never asks how the gap appeared.
    c = Cluster(pods=[running("api-1"), running("api-2")])
    d = dep(replicas=3)
    actions = reconcile(c, d)
    assert [a.verb for a in actions] == ["create"]


def test_replacements_are_not_scheduled_onto_a_dead_node():
    # Without this the loop places a pod on the node that just died, reaps it
    # next step, and churns forever.
    c = Cluster(pods=[running("api-1", node="node-a")], dead_nodes={"node-a"})
    d = dep(replicas=2)
    converge(c, d)
    assert all(p.node not in c.dead_nodes for p in c.alive(d))


def test_a_cluster_with_no_live_node_cannot_schedule():
    c = Cluster(nodes=["node-a"], dead_nodes={"node-a"})
    with pytest.raises(RuntimeError):
        converge(c, dep(replicas=1))


# ----------------------------------------------------------------- scaling


def test_scaling_up_creates_the_difference_only():
    c = Cluster(pods=[running(f"api-{i}") for i in range(2)])
    assert len(reconcile(c, dep(replicas=5))) == 3


def test_scaling_to_zero_is_a_valid_desired_state():
    c = Cluster(pods=[running("api-1")])
    d = dep(replicas=0)
    assert reconcile(c, d) == []          # nothing to create
    assert rollout_done(c, d) is False    # and one pod too many still exists


# ----------------------------------------------------------------- rollout


def test_a_changed_image_starts_a_rollout():
    c = Cluster(pods=[running(f"api-{i}") for i in range(3)])
    actions = reconcile(c, dep(replicas=3, image="app:1.5"))
    assert any(a.verb == "delete" and "1.4" in a.reason for a in actions)


def test_a_rollout_never_exceeds_replicas_plus_surge():
    c = Cluster(pods=[running(f"api-{i}") for i in range(3)])
    d = dep(replicas=3, image="app:1.5", max_surge=1)
    for _ in range(8):
        if rollout_done(c, d):
            break
        apply(c, reconcile(c, d), d)
        tick(c)
        assert len(c.alive(d)) <= d.replicas + d.max_surge


def test_a_rollout_never_drops_below_the_unavailability_budget():
    # THE guarantee: max_unavailable is what keeps the service up.
    c = Cluster(pods=[running(f"api-{i}") for i in range(3)])
    d = dep(replicas=3, image="app:1.5", max_unavailable=1)
    floor = d.replicas - d.max_unavailable
    seen = []
    for _ in range(8):
        if rollout_done(c, d):
            break
        apply(c, reconcile(c, d), d)
        tick(c)
        seen.append(len(c.serving(d)))
    assert seen and min(seen) >= floor


def test_a_rollout_finishes_with_every_pod_on_the_new_image():
    c = Cluster(pods=[running(f"api-{i}") for i in range(3)])
    d = dep(replicas=3, image="app:1.5")
    converge(c, d)
    assert rollout_done(c, d)
    assert {p.image for p in c.alive(d)} == {"app:1.5"}


def test_no_actions_does_not_mean_the_rollout_is_finished():
    # A step can legitimately have nothing to do while old pods still run --
    # the controller is waiting for the new ones to pass their probe.
    c = Cluster(pods=[running(f"api-{i}") for i in range(3)])
    d = dep(replicas=3, image="app:1.5")
    apply(c, reconcile(c, d), d)
    tick(c)
    assert reconcile(c, d) == []
    assert not rollout_done(c, d)


# -------------------------------------------------------------- rollout_done


def test_rollout_done_requires_readiness_not_just_running():
    c = Cluster(pods=[Pod(f"api-{i}", "app:1.4", Phase.RUNNING, False) for i in range(3)])
    d = dep(replicas=3)
    assert reconcile(c, d) == []      # the spec is satisfied
    assert not rollout_done(c, d)     # and nothing is serving


def test_rollout_done_requires_the_full_replica_count():
    c = Cluster(pods=[running("api-1"), running("api-2")])
    assert not rollout_done(c, dep(replicas=3))
