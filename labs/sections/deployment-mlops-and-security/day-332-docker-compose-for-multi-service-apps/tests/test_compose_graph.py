"""Grouped by what the graph check decides.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "examples"))

from compose_graph import (  # noqa: E402
    Condition,
    Dependency,
    Service,
    find_cycles,
    missing_dependencies,
    port_conflicts,
    premature_starts,
    ready_times,
    review,
    startup_order,
)


def svc(name, deps=(), ports=(), healthcheck=False, start=0.5, ready=0.5):
    return Service(
        name, f"img/{name}:1",
        ports=list(ports),
        depends_on=[d if isinstance(d, Dependency) else Dependency(d) for d in deps],
        healthcheck=healthcheck, start_seconds=start, ready_seconds=ready,
    )


def graph(*services):
    return {s.name: s for s in services}


# ------------------------------------------------------------------- cycles


def test_a_simple_cycle_is_found():
    g = graph(svc("a", ["b"]), svc("b", ["a"]))
    assert find_cycles(g) == [["a", "b"]]


def test_a_longer_cycle_is_found():
    g = graph(svc("a", ["b"]), svc("b", ["c"]), svc("c", ["a"]))
    assert find_cycles(g) == [["a", "b", "c"]]


def test_a_cycle_is_reported_once_not_once_per_member():
    g = graph(svc("a", ["b"]), svc("b", ["c"]), svc("c", ["a"]))
    assert len(find_cycles(g)) == 1


def test_a_self_dependency_is_a_cycle():
    assert find_cycles(graph(svc("a", ["a"]))) == [["a"]]


def test_an_acyclic_graph_has_no_cycles():
    g = graph(svc("db"), svc("api", ["db"]), svc("worker", ["api", "db"]))
    assert find_cycles(g) == []


def test_a_diamond_is_not_a_cycle():
    g = graph(svc("db"), svc("a", ["db"]), svc("b", ["db"]), svc("top", ["a", "b"]))
    assert find_cycles(g) == []


# ------------------------------------------------------------ undefined deps


def test_a_dependency_on_an_undefined_service_is_reported():
    f = missing_dependencies(graph(svc("api", ["nowhere"])))
    assert len(f) == 1 and f[0].rule == "undefined-dependency"


def test_defined_dependencies_are_not_reported():
    assert missing_dependencies(graph(svc("db"), svc("api", ["db"]))) == []


# ------------------------------------------------------------------- ports


def test_two_services_claiming_one_host_port_conflict():
    g = graph(svc("a", ports=[(8000, 8000)]), svc("b", ports=[(8000, 8080)]))
    f = port_conflicts(g)
    assert len(f) == 1 and "8000" in f[0].message


def test_the_same_container_port_on_different_host_ports_is_fine():
    # Different network namespaces: only the host side can clash.
    g = graph(svc("a", ports=[(8000, 8080)]), svc("b", ports=[(8001, 8080)]))
    assert port_conflicts(g) == []


def test_services_publishing_nothing_never_conflict():
    assert port_conflicts(graph(svc("a"), svc("b"))) == []


# ------------------------------------------------------------------- order


def test_dependencies_start_before_their_dependants():
    g = graph(svc("db"), svc("api", ["db"]), svc("worker", ["api"]))
    order = startup_order(g)
    assert order.index("db") < order.index("api") < order.index("worker")


def test_the_order_is_stable_for_independent_services():
    g = graph(svc("zebra"), svc("alpha"), svc("middle"))
    assert startup_order(g) == ["alpha", "middle", "zebra"]


def test_a_cycle_has_no_valid_order():
    with pytest.raises(ValueError, match="cycle"):
        startup_order(graph(svc("a", ["b"]), svc("b", ["a"])))


def test_a_dependency_on_an_undefined_service_does_not_block_startup():
    # The file is wrong, but the service is not waiting on anything real.
    assert startup_order(graph(svc("api", ["nowhere"]))) == ["api"]


# -------------------------------------------------------------- readiness


def test_a_service_with_no_dependencies_is_ready_after_start_plus_ready():
    g = graph(svc("db", start=0.4, ready=4.0))
    assert ready_times(g)["db"] == 4.4


def test_service_started_does_not_wait_for_the_dependency_to_be_usable():
    # THE finding: the dependant is "up" while the dependency still cannot answer.
    g = graph(svc("db", start=0.4, ready=4.0), svc("api", ["db"], start=0.2, ready=0.6))
    t = ready_times(g)
    assert t["api"] < t["db"]


def test_service_healthy_does_wait():
    g = graph(
        svc("db", start=0.4, ready=4.0, healthcheck=True),
        svc("api", [Dependency("db", Condition.HEALTHY)], start=0.2, ready=0.6),
    )
    t = ready_times(g)
    assert t["api"] > t["db"]
    assert t["api"] == round(t["db"] + 0.2 + 0.6, 2)


def test_waiting_properly_is_slower_and_that_is_the_point():
    fast = ready_times(graph(svc("db", start=0.4, ready=4.0), svc("api", ["db"], start=0.2, ready=0.6)))
    slow = ready_times(graph(
        svc("db", start=0.4, ready=4.0, healthcheck=True),
        svc("api", [Dependency("db", Condition.HEALTHY)], start=0.2, ready=0.6),
    ))
    assert slow["api"] > fast["api"]


# -------------------------------------------------------- premature starts


def test_starting_before_a_dependency_can_answer_is_reported():
    g = graph(svc("db", start=0.4, ready=4.0), svc("api", ["db"], start=0.2, ready=0.6))
    f = premature_starts(g)
    assert len(f) == 1 and f[0].rule == "starts-before-ready"
    assert "4.0s" in f[0].message


def test_a_healthy_condition_produces_no_premature_start():
    g = graph(
        svc("db", start=0.4, ready=4.0, healthcheck=True),
        svc("api", [Dependency("db", Condition.HEALTHY)], start=0.2, ready=0.6),
    )
    assert premature_starts(g) == []


def test_a_dependency_that_is_ready_instantly_is_not_premature():
    g = graph(svc("db", start=0.1, ready=0.0), svc("api", ["db"], start=0.2, ready=0.6))
    assert premature_starts(g) == []


# ------------------------------------------------------------------ review


def test_review_finds_every_class_of_problem():
    g = graph(
        svc("a", ["b"], ports=[(80, 80)]),
        svc("b", ["a"], ports=[(80, 8080)]),
        svc("ghost", ["nowhere"]),
    )
    rules = {f.rule for f in review(g)}
    assert {"dependency-cycle", "port-conflict", "undefined-dependency"} <= rules


def test_a_cycle_suppresses_the_timing_findings():
    # There is no start order, so "starts too early" is not a meaningful claim.
    g = graph(svc("a", ["b"]), svc("b", ["a"]))
    assert not any(f.rule == "starts-before-ready" for f in review(g))


def test_waiting_for_health_on_a_service_with_no_healthcheck_is_reported():
    g = graph(
        svc("db", healthcheck=False),
        svc("api", [Dependency("db", Condition.HEALTHY)]),
    )
    assert "healthy-without-healthcheck" in {f.rule for f in review(g)}


def test_a_correctly_wired_stack_is_clean():
    g = graph(
        svc("db", ports=[(5432, 5432)], healthcheck=True, start=0.4, ready=4.0),
        svc("api", [Dependency("db", Condition.HEALTHY)], ports=[(8000, 8000)],
            healthcheck=True, start=0.2, ready=0.6),
    )
    assert review(g) == []
