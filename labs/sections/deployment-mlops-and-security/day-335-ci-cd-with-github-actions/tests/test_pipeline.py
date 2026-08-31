"""Grouped by what the pipeline analysis decides.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "examples"))

from pipeline import (  # noqa: E402
    Job,
    Trigger,
    Workflow,
    critical_path,
    find_cycle,
    finish_times,
    missing_needs,
    review,
    savings_from_removing,
    total_minutes,
    without,
)


def wf(jobs, triggers=(Trigger.PUSH,)):
    return Workflow("ci", list(triggers), {j.name: j for j in jobs})


def job(name, needs=(), minutes=1.0, secrets=False, caches=(), fails=1.0):
    return Job(name, list(needs), minutes, secrets, list(caches), fails)


# ------------------------------------------------------------------ timing


def test_a_single_job_finishes_after_its_own_duration():
    assert finish_times(wf([job("a", minutes=2.5)])) == {"a": 2.5}


def test_dependent_jobs_add_up():
    t = finish_times(wf([job("a", minutes=2.0), job("b", ["a"], minutes=3.0)]))
    assert t["b"] == 5.0


def test_independent_jobs_run_in_parallel_not_in_sequence():
    # The whole reason wall clock and runner minutes differ.
    t = finish_times(wf([job("a", minutes=2.0), job("b", minutes=3.0)]))
    assert t["a"] == 2.0 and t["b"] == 3.0


def test_a_job_waits_for_its_slowest_dependency():
    t = finish_times(wf([
        job("fast", minutes=1.0), job("slow", minutes=5.0),
        job("after", ["fast", "slow"], minutes=1.0),
    ]))
    assert t["after"] == 6.0


def test_a_dependency_on_an_undefined_job_does_not_block_timing():
    t = finish_times(wf([job("a", ["nowhere"], minutes=2.0)]))
    assert t["a"] == 2.0


# ------------------------------------------------------------ critical path


def test_the_critical_path_is_the_longest_chain_not_the_sum():
    w = wf([job("a", minutes=2.0), job("b", ["a"], minutes=3.0), job("side", minutes=10.0)])
    path, wall = critical_path(w)
    assert wall == 10.0 and path == ["side"]
    assert total_minutes(w) == 15.0


def test_runner_minutes_exceed_wall_clock_when_work_is_parallel():
    w = wf([job("a", minutes=4.0), job("b", minutes=4.0), job("c", minutes=4.0)])
    _, wall = critical_path(w)
    assert wall == 4.0
    assert total_minutes(w) == 12.0


def test_the_critical_path_is_a_real_chain_of_dependencies():
    w = wf([job("a", minutes=1.0), job("b", ["a"], minutes=2.0), job("c", ["b"], minutes=3.0)])
    path, wall = critical_path(w)
    assert path == ["a", "b", "c"] and wall == 6.0


def test_an_empty_workflow_has_no_critical_path():
    assert critical_path(wf([])) == ([], 0.0)


# ------------------------------------------------------------------ graph


def test_a_cycle_is_detected():
    assert find_cycle(wf([job("a", ["b"]), job("b", ["a"])])) == ["a", "b"]


def test_an_acyclic_graph_has_no_cycle():
    assert find_cycle(wf([job("a"), job("b", ["a"])])) == []


def test_timing_a_cyclic_workflow_raises():
    with pytest.raises(ValueError, match="cycle"):
        finish_times(wf([job("a", ["b"]), job("b", ["a"])]))


def test_an_undefined_dependency_is_reported():
    assert missing_needs(wf([job("a", ["ghost"])])) == ["a needs 'ghost', which no job defines"]


# ------------------------------------------------------------------ review


def test_a_gate_that_has_never_failed_is_reported():
    w = wf([job("scan", minutes=2.0, fails=0.0)])
    assert "gate-never-fires" in {f.rule for f in review(w)}


def test_a_gate_that_does_fail_is_not_reported():
    w = wf([job("unit", minutes=2.0, caches=["pip"], fails=5.0)])
    assert "gate-never-fires" not in {f.rule for f in review(w)}


def test_a_slow_job_with_no_cache_is_reported():
    assert "no-cache" in {f.rule for f in review(wf([job("install", minutes=4.0)]))}


def test_a_slow_job_with_a_cache_is_not_reported():
    w = wf([job("install", minutes=4.0, caches=["pip"])])
    assert "no-cache" not in {f.rule for f in review(w)}


def test_a_quick_job_without_a_cache_is_left_alone():
    assert "no-cache" not in {f.rule for f in review(wf([job("tiny", minutes=0.5)]))}


def test_a_cycle_suppresses_the_other_findings():
    w = wf([job("a", ["b"], minutes=9.0, fails=0.0), job("b", ["a"], minutes=9.0, fails=0.0)])
    rules = {f.rule for f in review(w)}
    assert rules == {"dependency-cycle"}


# ---------------------------------------------------------------- secrets


def test_pull_request_target_with_secrets_is_reported():
    w = wf([job("deploy", minutes=1.0, secrets=True)],
           triggers=(Trigger.PUSH, Trigger.PR_TARGET))
    assert "secrets-exposed-to-forks" in {f.rule for f in review(w)}


def test_the_same_job_on_pull_request_is_not_reported():
    w = wf([job("deploy", minutes=1.0, secrets=True)],
           triggers=(Trigger.PUSH, Trigger.PULL_REQUEST))
    assert "secrets-exposed-to-forks" not in {f.rule for f in review(w)}


def test_pull_request_target_without_secrets_is_not_reported():
    w = wf([job("build", minutes=1.0, secrets=False)],
           triggers=(Trigger.PR_TARGET,))
    assert "secrets-exposed-to-forks" not in {f.rule for f in review(w)}


# ---------------------------------------------------------------- removal


def test_removing_a_job_drops_it():
    w = without(wf([job("a"), job("b")]), "a")
    assert set(w.jobs) == {"b"}


def test_removing_a_job_does_not_orphan_its_dependants():
    # b needed a, a needed checkout. Remove a and b must still wait for checkout.
    w = without(wf([job("checkout"), job("a", ["checkout"]), job("b", ["a"])]), "a")
    assert w.jobs["b"].needs == ["checkout"]


def test_removing_a_job_that_does_not_exist_is_an_error():
    with pytest.raises(KeyError):
        without(wf([job("a")]), "nope")


def test_removing_an_off_path_job_saves_runner_minutes_but_no_wall_clock():
    # THE finding: deleting a slow job that nothing waits for makes the
    # pipeline cheaper and not one second faster.
    w = wf([
        job("install", minutes=4.0),
        job("long", ["install"], minutes=6.0),
        job("side", ["install"], minutes=3.0, fails=0.0),
    ])
    s = savings_from_removing(w, "side")
    assert s["on_critical_path"] is False
    assert s["wall_saved"] == 0.0
    assert s["minutes_saved"] == 3.0


def test_removing_an_on_path_job_does_save_wall_clock():
    w = wf([job("install", minutes=4.0), job("long", ["install"], minutes=6.0)])
    s = savings_from_removing(w, "long")
    assert s["on_critical_path"] is True
    assert s["wall_saved"] == 6.0
