"""Grouped by gate, so a failure names which one let a bad build through.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from release import (  # noqa: E402
    Build,
    DeployBlocked,
    Deployment,
    Health,
    Stage,
    deploy,
    preflight,
    rollback,
)


def fresh() -> Deployment:
    return Deployment(live_version="v1.0.0")


# ---------------------------------------------------------------- preflight


def test_a_clean_build_has_no_blockers():
    assert preflight(Build("v1.1.0")) == []


def test_failing_tests_block_the_deploy():
    assert "tests did not pass" in preflight(Build("v1", tests_passed=False))


def test_an_irreversible_migration_blocks_the_deploy():
    # The worst blocker, because it removes the rollback every other failure
    # depends on.
    assert "migration is not reversible" in preflight(Build("v1", migrations_reversible=False))


def test_an_unpinned_image_blocks_the_deploy():
    assert "not pinned" in " ".join(preflight(Build("v1", image_digest="latest")))


def test_blockers_accumulate_rather_than_stopping_at_the_first():
    problems = preflight(Build("v1", tests_passed=False, secrets_present=False))
    assert len(problems) == 2


def test_a_blocked_build_deploys_nothing():
    dep = fresh()
    with pytest.raises(DeployBlocked):
        deploy(dep, Build("v1.1.0", tests_passed=False))
    assert dep.live_version == "v1.0.0"
    assert dep.traffic_to_new == 0
    assert dep.stage is Stage.BLOCKED


# ------------------------------------------------------------------- health


def test_a_process_that_starts_but_cannot_serve_is_rolled_back():
    # Liveness is true, readiness is not. Conflating them is why a deployment
    # goes green while every request fails.
    dep = deploy(fresh(), Build("v1.1.0"), health=Health(readiness=False))
    assert dep.stage is Stage.ROLLED_BACK
    assert dep.live_version == "v1.0.0"
    assert "readiness" in dep.events[-1].detail


def test_an_unreachable_dependency_is_rolled_back():
    dep = deploy(fresh(), Build("v1.1.0"), health=Health(dependency_ok=False))
    assert dep.stage is Stage.ROLLED_BACK
    assert "dependency" in dep.events[-1].detail


def test_health_names_every_failing_signal():
    dep = deploy(fresh(), Build("v1.1.0"), health=Health(readiness=False, dependency_ok=False))
    detail = dep.events[-1].detail
    assert "readiness" in detail and "dependency" in detail


def test_a_failed_health_check_never_reaches_canary():
    dep = deploy(fresh(), Build("v1.1.0"), health=Health(readiness=False))
    assert Stage.CANARY not in [e.stage for e in dep.events]


# ------------------------------------------------------------------ canary


def test_a_healthy_release_is_promoted_through_canary():
    dep = deploy(fresh(), Build("v1.1.0"))
    stages = [e.stage for e in dep.events]
    assert stages == [Stage.DEPLOYING, Stage.CANARY, Stage.PROMOTED]
    assert dep.live_version == "v1.1.0"
    assert dep.traffic_to_new == 100


def test_a_canary_over_the_error_budget_is_rolled_back():
    dep = deploy(fresh(), Build("v1.1.0"), error_rate=0.09, error_budget=0.02)
    assert dep.stage is Stage.ROLLED_BACK
    assert dep.live_version == "v1.0.0"
    assert "9.0%" in dep.events[-1].detail


def test_a_canary_inside_the_error_budget_is_promoted():
    dep = deploy(fresh(), Build("v1.1.0"), error_rate=0.01, error_budget=0.02)
    assert dep.stage is Stage.PROMOTED


def test_canary_takes_only_a_fraction_of_traffic_before_the_decision():
    dep = fresh()
    deploy(dep, Build("v1.1.0"), canary_percent=5, error_rate=0.09)
    canary = next(e for e in dep.events if e.stage is Stage.CANARY)
    assert "5%" in canary.detail
    # And the failed canary leaves no traffic on the new version.
    assert dep.traffic_to_new == 0


# ---------------------------------------------------------------- rollback


def test_rollback_returns_to_the_previous_version():
    dep = deploy(fresh(), Build("v1.1.0"))
    assert dep.live_version == "v1.1.0"
    rollback(dep)
    assert dep.live_version == "v1.0.0"
    assert dep.traffic_to_new == 0


def test_rollback_is_reversible():
    # Swapping rather than discarding means a rollback can itself be undone,
    # which matters when the rollback was the mistake.
    dep = deploy(fresh(), Build("v1.1.0"))
    rollback(dep)
    rollback(dep)
    assert dep.live_version == "v1.1.0"


def test_rollback_with_no_previous_version_is_reported_not_crashed():
    dep = fresh()
    rollback(dep)
    assert dep.stage is Stage.ROLLED_BACK
    assert "no previous version" in dep.events[-1].detail
    assert dep.live_version == "v1.0.0"
