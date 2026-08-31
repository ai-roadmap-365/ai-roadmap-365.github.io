"""Grouped by what the cost model decides.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import math
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "examples"))

from hosting_cost import (  # noqa: E402
    HOURS_PER_MONTH,
    Billing,
    Option,
    Workload,
    binding_constraint,
    cheapest,
    crossover,
    free_tier_ceiling,
    headroom,
    scale_workload,
)

BASE = Workload(requests=20_000, seconds_per_request=0.4,
                gb_out_per_request=0.00004, storage_gb=2.0)


def vm(hourly=0.01, **kw):
    return Option("vm", Billing.ALWAYS_ON, hourly_usd=hourly, **kw)


def serverless(**kw):
    return Option("srv", Billing.PER_REQUEST, per_gb_second_usd=0.000024, **kw)


# --------------------------------------------------------------- workload


def test_compute_seconds_is_requests_times_duration():
    assert BASE.compute_seconds == 8_000.0


def test_egress_is_requests_times_bytes_out():
    assert BASE.egress_gb == pytest.approx(0.8)


def test_scaling_multiplies_traffic_but_not_storage_proportionally():
    w = scale_workload(BASE, 10)
    assert w.requests == 200_000
    assert w.storage_gb < BASE.storage_gb * 10   # storage grows more slowly


def test_scaling_by_one_changes_nothing_material():
    w = scale_workload(BASE, 1.0)
    assert w.requests == BASE.requests and w.storage_gb == BASE.storage_gb


# ------------------------------------------------------------- always-on


def test_an_always_on_option_bills_by_the_hour_regardless_of_traffic():
    # The defining property: it costs the same at 3am with no users.
    o = vm(hourly=0.01)
    quiet = Workload(requests=1, seconds_per_request=0.1, gb_out_per_request=0.0)
    assert o.compute_usd(BASE) == o.compute_usd(quiet)
    assert o.compute_usd(BASE) == pytest.approx(0.01 * HOURS_PER_MONTH)


def test_an_always_on_option_costs_the_same_at_zero_traffic():
    o = vm(hourly=0.02)
    idle = Workload(requests=0, seconds_per_request=0.0, gb_out_per_request=0.0)
    assert o.compute_usd(idle) > 0


# ----------------------------------------------------------- per-request


def test_a_per_request_option_costs_nothing_at_zero_traffic():
    o = serverless(per_million_requests_usd=0.40)
    idle = Workload(requests=0, seconds_per_request=0.0, gb_out_per_request=0.0)
    assert o.compute_usd(idle) == 0.0


def test_free_compute_seconds_are_deducted_before_billing():
    o = serverless(free_compute_seconds=8_000.0)
    assert o.compute_usd(BASE) == 0.0


def test_free_requests_are_deducted_before_billing():
    # Isolate the per-request charge: give both options the same free seconds,
    # so the only difference between them is the request allowance.
    billed = serverless(per_million_requests_usd=1.0, free_compute_seconds=8_000)
    covered = serverless(per_million_requests_usd=1.0, free_compute_seconds=8_000,
                         free_requests=20_000)
    assert billed.compute_usd(BASE) == pytest.approx(0.02)
    assert covered.compute_usd(BASE) == 0.0


def test_usage_beyond_the_free_allowance_is_billed():
    o = serverless(free_compute_seconds=4_000.0)
    assert o.compute_usd(BASE) == pytest.approx(4_000.0 * 0.000024)


# --------------------------------------------------------------- egress


def test_egress_below_the_free_allowance_is_free():
    assert vm(free_egress_gb=1.0, egress_per_gb_usd=0.09).egress_usd(BASE) == 0.0


def test_only_the_excess_egress_is_billed():
    o = vm(free_egress_gb=0.5, egress_per_gb_usd=0.10)
    assert o.egress_usd(BASE) == pytest.approx(0.03)   # 0.3 GB over


def test_egress_is_frequently_the_dominant_cost_at_scale():
    o = vm(hourly=0.0104, free_egress_gb=100.0, egress_per_gb_usd=0.09)
    big = scale_workload(BASE, 1000)
    assert o.egress_usd(big) > o.compute_usd(big)


# -------------------------------------------------------------- headroom


def test_headroom_reports_a_multiple_per_dimension():
    o = serverless(free_compute_seconds=80_000, free_requests=2_000_000,
                   free_egress_gb=1.0, free_storage_gb=5.0)
    h = headroom(o, BASE)
    assert h["compute-seconds"] == pytest.approx(10.0)
    assert h["requests"] == pytest.approx(100.0)


def test_an_unused_dimension_has_infinite_headroom():
    w = Workload(requests=10, seconds_per_request=0.1, gb_out_per_request=0.0)
    assert math.isinf(headroom(serverless(free_egress_gb=5.0), w)["egress-gb"])


def test_the_binding_constraint_is_the_smallest_headroom():
    # THE finding: the advertised allowance is rarely the one that runs out.
    o = serverless(free_compute_seconds=180_000, free_requests=2_000_000,
                   free_egress_gb=1.0, free_storage_gb=5.0)
    which, at = binding_constraint(o, BASE)
    assert which == "egress-gb"
    assert at == pytest.approx(1.25, abs=0.01)
    assert headroom(o, BASE)["requests"] == pytest.approx(100.0)


def test_a_dimension_with_no_allowance_binds_immediately():
    which, at = binding_constraint(vm(), BASE)
    assert at == 0.0


# ------------------------------------------------------------- selection


def test_the_cheapest_option_is_chosen():
    a, b = vm(hourly=1.0), Option("b", Billing.ALWAYS_ON, hourly_usd=0.001)
    assert cheapest([a, b], BASE).name == "b"


def test_choosing_from_nothing_is_an_error():
    with pytest.raises(ValueError):
        cheapest([], BASE)


# ------------------------------------------------------------ crossover


def test_the_cheap_option_at_launch_can_lose_at_scale():
    # Serverless wins when idle and loses when busy. Finding WHERE is the point.
    srv = serverless(per_million_requests_usd=0.40, free_compute_seconds=180_000,
                     free_requests=2_000_000, free_egress_gb=1.0,
                     egress_per_gb_usd=0.12, storage_per_gb_usd=0.026, free_storage_gb=5.0)
    box = vm(hourly=0.0104, free_egress_gb=100.0, egress_per_gb_usd=0.09,
             storage_per_gb_usd=0.10)
    assert srv.monthly_usd(BASE) < box.monthly_usd(BASE)
    x = crossover(srv, box, BASE)
    assert x is not None and 1.0 < x < 1000.0
    at = scale_workload(BASE, x * 1.5)
    assert box.monthly_usd(at) < srv.monthly_usd(at)


def test_two_identically_priced_options_have_no_crossover():
    a = vm(hourly=0.01)
    b = Option("b2", Billing.ALWAYS_ON, hourly_usd=0.01)
    assert crossover(a, b, BASE) is None


def test_an_option_that_always_wins_has_no_crossover():
    cheap = vm(hourly=0.001)
    dear = Option("dear", Billing.ALWAYS_ON, hourly_usd=10.0)
    assert crossover(cheap, dear, BASE) is None


# --------------------------------------------------------- free ceiling


def test_the_free_ceiling_is_none_when_the_option_costs_money_at_launch():
    assert free_tier_ceiling(vm(hourly=0.01), BASE) is None


def test_the_free_ceiling_finds_where_a_free_tier_runs_out():
    o = serverless(free_compute_seconds=180_000, free_requests=2_000_000,
                   free_egress_gb=1.0, egress_per_gb_usd=0.12,
                   free_storage_gb=5.0, storage_per_gb_usd=0.026)
    assert o.is_free(BASE)
    ceiling = free_tier_ceiling(o, BASE)
    assert ceiling is not None and ceiling > 1.0
    assert not o.is_free(scale_workload(BASE, ceiling * 2))
