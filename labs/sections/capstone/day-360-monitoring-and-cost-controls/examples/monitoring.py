"""Windowed metrics, alert rules and cost anomaly detection for an AI service.

Offline and standard-library only. Requests are records with a logical
timestamp, so every percentile and every alert is exactly reproducible.

The shape of the problem is different from ordinary web monitoring in three
ways, and each drives something here:

  cost is per request      so spend is a first-class metric, not a monthly bill
  failure is often partial a request can succeed and still be useless
  latency is long-tailed   so the mean is actively misleading

Two principles run through the module:

  * Alert on SYMPTOMS a user would notice, not on causes. "p95 latency is
    above 4s" is actionable; "cache hit rate fell" may be entirely fine.
  * Compare against a BASELINE, not a fixed threshold, wherever normal varies.
    A fixed spend limit is either always breached or never useful.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    OK = "ok"
    WARN = "warn"
    PAGE = "page"


@dataclass(frozen=True)
class Request:
    """One served request."""

    at: int  # logical minute
    latency_ms: int
    ok: bool
    cost: float
    tokens: int
    grounded: bool = True  # did the answer cite retrieved context?


@dataclass
class Window:
    """Metrics over one slice of time."""

    start: int
    end: int
    requests: list[Request] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.requests)

    @property
    def error_rate(self) -> float:
        if not self.requests:
            return 0.0
        return sum(1 for r in self.requests if not r.ok) / len(self.requests)

    @property
    def ungrounded_rate(self) -> float:
        """Answers that cited nothing.

        A quality signal rather than an availability one. These requests
        succeeded -- they returned 200 and a fluent answer -- and are still a
        failure of the thing the system exists to do.
        """
        if not self.requests:
            return 0.0
        return sum(1 for r in self.requests if not r.grounded) / len(self.requests)

    @property
    def spend(self) -> float:
        return sum(r.cost for r in self.requests)

    def latency(self, p: float) -> int:
        return percentile([r.latency_ms for r in self.requests], p)

    def line(self) -> str:
        return (
            f"[{self.start:>3}-{self.end:<3}) n={self.count:<3} "
            f"p50={self.latency(50):<5} p95={self.latency(95):<6} "
            f"err={self.error_rate:.0%} ungrounded={self.ungrounded_rate:.0%} "
            f"spend=${self.spend:.4f}"
        )


def percentile(values: list[int], p: float) -> int:
    """Nearest-rank percentile. Zero for an empty input.

    `math.ceil`, not `round`: Python rounds halves to even, which puts the p50
    of a five-element list on the wrong observation.
    """
    if not values:
        return 0
    ordered = sorted(values)
    rank = max(1, min(len(ordered), math.ceil(p / 100 * len(ordered))))
    return ordered[rank - 1]


def windows(requests: list[Request], *, size: int = 5) -> list[Window]:
    """Bucket requests into fixed windows by their logical minute."""
    if not requests:
        return []
    lo = min(r.at for r in requests)
    hi = max(r.at for r in requests)
    out: list[Window] = []
    for start in range(lo, hi + 1, size):
        end = start + size
        out.append(
            Window(start, end, [r for r in requests if start <= r.at < end])
        )
    return out


@dataclass
class Alert:
    name: str
    severity: Severity
    detail: str

    def line(self) -> str:
        return f"  {self.severity.value.upper():<5} {self.name}: {self.detail}"


def evaluate(
    window: Window,
    *,
    baseline_spend: float | None = None,
    latency_slo_ms: int = 4000,
    error_budget: float = 0.02,
    ungrounded_budget: float = 0.10,
    spend_multiple: float = 3.0,
    min_sample: int = 10,
) -> list[Alert]:
    """Apply the alert rules to one window.

    `min_sample` matters more than it looks. On a small window a single failed
    request is a 20% error rate, and paging on that trains people to ignore
    pages -- which is worse than not alerting at all.
    """
    alerts: list[Alert] = []

    if window.count < min_sample:
        return [
            Alert(
                "insufficient_sample",
                Severity.OK,
                f"{window.count} requests is below the {min_sample} needed to judge",
            )
        ]

    p95 = window.latency(95)
    if p95 > latency_slo_ms:
        alerts.append(
            Alert("latency_slo", Severity.PAGE, f"p95 {p95}ms exceeds {latency_slo_ms}ms")
        )

    if window.error_rate > error_budget:
        alerts.append(
            Alert(
                "error_budget",
                Severity.PAGE,
                f"{window.error_rate:.0%} errors exceeds {error_budget:.0%}",
            )
        )

    # A quality symptom, not an availability one. These requests SUCCEEDED.
    if window.ungrounded_rate > ungrounded_budget:
        alerts.append(
            Alert(
                "ungrounded_answers",
                Severity.WARN,
                f"{window.ungrounded_rate:.0%} of answers cited nothing",
            )
        )

    # Spend is compared against what normal looked like, not a fixed cap.
    if baseline_spend is not None and baseline_spend > 0:
        ratio = window.spend / baseline_spend
        if ratio > spend_multiple:
            alerts.append(
                Alert(
                    "cost_anomaly",
                    Severity.PAGE,
                    f"spend ${window.spend:.4f} is {ratio:.1f}x the ${baseline_spend:.4f} baseline",
                )
            )

    return alerts or [Alert("healthy", Severity.OK, "all signals within budget")]


def worst(alerts: list[Alert]) -> Severity:
    order = {Severity.OK: 0, Severity.WARN: 1, Severity.PAGE: 2}
    return max((a.severity for a in alerts), key=lambda s: order[s], default=Severity.OK)


def rolling_baseline(history: list[Window], *, keep: int = 3) -> float | None:
    """Median spend of the last `keep` windows.

    Median rather than mean: one anomalous window should not raise the baseline
    enough to hide the next one, which is exactly how a spend alert stops
    firing after the first incident.
    """
    recent = [w.spend for w in history[-keep:] if w.count]
    if not recent:
        return None
    ordered = sorted(recent)
    return ordered[len(ordered) // 2]
