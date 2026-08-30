"""Grouped by signal, so a failure names which alert stopped working.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from monitoring import (  # noqa: E402
    Request,
    Severity,
    Window,
    evaluate,
    percentile,
    rolling_baseline,
    windows,
    worst,
)


def reqs(n, *, latency=500, ok=True, cost=0.001, grounded=True, at=0):
    return [Request(at=at, latency_ms=latency, ok=ok, cost=cost, tokens=500,
                    grounded=grounded) for _ in range(n)]


def names(alerts):
    return {a.name for a in alerts}


# --------------------------------------------------------------- percentiles


def test_percentile_uses_nearest_rank_not_banker_rounding():
    # round(2.5) is 2 in Python, which would pick the wrong observation.
    assert percentile([1, 2, 3, 4, 100], 50) == 3
    assert percentile([1, 2, 3, 4, 100], 95) == 100


def test_percentile_of_nothing_is_zero():
    assert percentile([], 95) == 0


def test_p95_is_not_the_mean():
    # A tenth of requests are slow. The mean stays comfortable; p95 does not.
    values = [200] * 18 + [9000] * 2
    assert sum(values) / len(values) < 1100
    assert percentile(values, 95) == 9000


def test_p95_cannot_see_a_single_outlier_in_twenty_samples():
    # Worth knowing rather than discovering during an incident. Nearest rank
    # for p95 over 20 samples is the 19th value, so ONE slow request sits above
    # the percentile entirely and is invisible to it.
    values = [200] * 19 + [9000]
    assert percentile(values, 95) == 200
    # p99 over the same data is the 20th, which does see it.
    assert percentile(values, 99) == 9000
    # The general rule: a percentile can only see events more frequent than
    # 1 - p. Choose the percentile to match what you need to catch, and make
    # sure the window is large enough to contain them.


# ------------------------------------------------------------------ windows


def test_requests_are_bucketed_by_logical_minute():
    traffic = reqs(3, at=0) + reqs(3, at=6) + reqs(3, at=11)
    got = windows(traffic, size=5)
    assert [w.count for w in got] == [3, 3, 3]
    assert [(w.start, w.end) for w in got] == [(0, 5), (5, 10), (10, 15)]


def test_empty_traffic_produces_no_windows():
    assert windows([]) == []


def test_a_window_with_no_requests_reports_zero_not_an_error():
    w = Window(0, 5, [])
    assert w.error_rate == 0.0 and w.spend == 0.0 and w.latency(95) == 0


# ------------------------------------------------------------ small samples


def test_a_small_window_is_not_judged():
    # One failure in three requests is a 33% error rate. Paging on that trains
    # people to ignore pages, which is worse than not alerting.
    w = Window(0, 5, reqs(2, ok=False))
    alerts = evaluate(w)
    assert names(alerts) == {"insufficient_sample"}
    assert worst(alerts) is Severity.OK


def test_the_same_rate_alerts_once_the_sample_is_large_enough():
    w = Window(0, 5, reqs(10, ok=False))
    assert "error_budget" in names(evaluate(w))


# ------------------------------------------------------------------ latency


def test_latency_over_the_slo_pages():
    w = Window(0, 5, reqs(20, latency=9000))
    alerts = evaluate(w)
    assert "latency_slo" in names(alerts)
    assert worst(alerts) is Severity.PAGE


def test_latency_inside_the_slo_is_healthy():
    w = Window(0, 5, reqs(20, latency=900))
    assert names(evaluate(w)) == {"healthy"}


# ------------------------------------------------------------------- errors


def test_error_rate_over_budget_pages():
    w = Window(0, 5, reqs(10, ok=False) + reqs(10))
    assert "error_budget" in names(evaluate(w))


def test_error_rate_inside_budget_is_healthy():
    w = Window(0, 5, reqs(100))
    assert names(evaluate(w)) == {"healthy"}


# ------------------------------------------------------------------ quality


def test_ungrounded_answers_warn_even_though_every_request_succeeded():
    # The distinguishing case for an AI service: 100% availability, and the
    # answers cite nothing. Conventional monitoring reports this as healthy.
    w = Window(0, 5, reqs(10, grounded=False) + reqs(10))
    alerts = evaluate(w)
    assert w.error_rate == 0.0
    assert "ungrounded_answers" in names(alerts)
    assert worst(alerts) is Severity.WARN


def test_grounded_answers_do_not_warn():
    w = Window(0, 5, reqs(20, grounded=True))
    assert "ungrounded_answers" not in names(evaluate(w))


# --------------------------------------------------------------------- cost


def test_a_spend_spike_against_the_baseline_pages():
    w = Window(0, 5, reqs(20, cost=0.02))
    alerts = evaluate(w, baseline_spend=0.03)
    assert "cost_anomaly" in names(alerts)
    assert "13.3x" in next(a for a in alerts if a.name == "cost_anomaly").detail


def test_normal_spend_against_the_baseline_is_healthy():
    w = Window(0, 5, reqs(20, cost=0.0015))
    assert names(evaluate(w, baseline_spend=0.03)) == {"healthy"}


def test_no_baseline_means_no_cost_alert():
    # A first window has nothing to compare against, and inventing a fixed
    # threshold would be either always breached or never useful.
    w = Window(0, 5, reqs(20, cost=0.02))
    assert "cost_anomaly" not in names(evaluate(w, baseline_spend=None))


def test_baseline_is_a_median_so_one_spike_does_not_hide_the_next():
    normal = Window(0, 5, reqs(20, cost=0.0015))
    spike = Window(5, 10, reqs(20, cost=0.02))
    # Mean of these would be pulled up by the spike; the median is not.
    assert rolling_baseline([normal, normal, spike]) == normal.spend


def test_rolling_baseline_ignores_empty_windows():
    assert rolling_baseline([Window(0, 5, [])]) is None


# ------------------------------------------------------------------ severity


def test_worst_severity_wins():
    w = Window(0, 5, reqs(10, latency=9000, grounded=False) + reqs(10, latency=9000))
    alerts = evaluate(w)
    assert names(alerts) >= {"latency_slo", "ungrounded_answers"}
    assert worst(alerts) is Severity.PAGE


def test_worst_of_nothing_is_ok():
    assert worst([]) is Severity.OK
