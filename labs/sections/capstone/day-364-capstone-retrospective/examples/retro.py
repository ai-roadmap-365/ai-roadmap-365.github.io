"""Turn a project's record into findings you can act on.

Offline and standard-library only. The input is a list of tasks with estimates
and actuals, plus the incidents that occurred, so nothing is fetched.

A retrospective usually produces feelings: "the API work took longer than
expected", "we should test more". Feelings do not transfer to the next project.
Numbers do, and three of them are computable from a record you already have:

  calibration    how wrong your estimates were, and IN WHICH DIRECTION
  bias by area   whether the error is uniform or concentrated somewhere
  detection      which incidents a gate caught, and which reached a user

The direction matters more than the magnitude. Being uniformly 2x over is a
multiplier you can apply. Being accurate on familiar work and 5x over on
unfamiliar work is a different problem with a different fix -- and the average
of the two hides both.

Nothing here judges whether the project was good. It measures what was
predictable and was not predicted, which is the only part that transfers.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum


class Caught(str, Enum):
    """Where an incident was detected. Ordered by how much it cost."""

    REVIEW = "review"  # before it ran anywhere
    TESTS = "tests"  # before it deployed
    STAGING = "staging"  # deployed, no user affected
    MONITORING = "monitoring"  # in production, found by a signal
    USER = "user"  # in production, found by a person


# How much later each stage is than the one before it. Not a cost in money --
# a rank, so "further right" is comparable across projects.
STAGE_RANK = {
    Caught.REVIEW: 0,
    Caught.TESTS: 1,
    Caught.STAGING: 2,
    Caught.MONITORING: 3,
    Caught.USER: 4,
}


@dataclass(frozen=True)
class Task:
    name: str
    area: str
    estimated_hours: float
    actual_hours: float

    @property
    def ratio(self) -> float:
        """Actual over estimated. 1.0 is perfect, 2.0 is twice as long."""
        return self.actual_hours / self.estimated_hours if self.estimated_hours else 0.0


@dataclass(frozen=True)
class Incident:
    what: str
    caught_at: Caught
    preventable_by: str = ""  # the gate that SHOULD have caught it, if any


@dataclass
class Calibration:
    median_ratio: float
    worst_area: str
    worst_area_ratio: float
    best_area: str
    best_area_ratio: float
    underestimated: int
    overestimated: int

    def line(self) -> str:
        return (
            f"median ratio {self.median_ratio:.2f}x  "
            f"under {self.underestimated} / over {self.overestimated}  "
            f"worst {self.worst_area} {self.worst_area_ratio:.2f}x  "
            f"best {self.best_area} {self.best_area_ratio:.2f}x"
        )


def median(values: list[float]) -> float:
    """Median rather than mean, because one task that ran 8x over would
    dominate an average and make the whole estimate look worse than it was."""
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def by_area(tasks: list[Task]) -> dict[str, float]:
    """Median ratio per area of work."""
    areas: dict[str, list[float]] = {}
    for task in tasks:
        areas.setdefault(task.area, []).append(task.ratio)
    return {area: median(ratios) for area, ratios in areas.items()}


def calibration(tasks: list[Task]) -> Calibration:
    """How wrong the estimates were, and where the error concentrates."""
    if not tasks:
        return Calibration(0.0, "", 0.0, "", 0.0, 0, 0)
    ratios = [t.ratio for t in tasks]
    areas = by_area(tasks)
    worst = max(areas, key=lambda a: (areas[a], a))
    best = min(areas, key=lambda a: (areas[a], a))
    return Calibration(
        median_ratio=median(ratios),
        worst_area=worst,
        worst_area_ratio=areas[worst],
        best_area=best,
        best_area_ratio=areas[best],
        underestimated=sum(1 for r in ratios if r > 1.0),
        overestimated=sum(1 for r in ratios if r < 1.0),
    )


def is_uniform(tasks: list[Task], *, spread: float = 1.5) -> bool:
    """Whether the estimation error is spread evenly across areas.

    A uniform error is a multiplier you can apply next time. A concentrated one
    means you estimate familiar work well and unfamiliar work badly, which
    needs a different fix -- and the overall median hides which you have.
    """
    areas = by_area(tasks)
    if len(areas) < 2:
        return True
    values = list(areas.values())
    lo, hi = min(values), max(values)
    return hi <= lo * spread if lo > 0 else False


def apply_multiplier(estimate: float, cal: Calibration) -> float:
    """What this estimate becomes once your own history is applied."""
    return round(estimate * cal.median_ratio, 1)


@dataclass
class DetectionReport:
    counts: dict[Caught, int] = field(default_factory=dict)
    escaped: list[Incident] = field(default_factory=list)
    preventable: list[Incident] = field(default_factory=list)

    @property
    def escape_rate(self) -> float:
        total = sum(self.counts.values())
        return len(self.escaped) / total if total else 0.0

    def summary(self) -> str:
        order = " ".join(f"{s.value}={self.counts.get(s, 0)}" for s in Caught)
        return f"{order}  escaped={len(self.escaped)} ({self.escape_rate:.0%})"


def detection(incidents: list[Incident]) -> DetectionReport:
    """Where problems were caught, and which ones reached a user.

    "Escaped" means monitoring or a person found it in production. Those are
    the incidents worth spending the next project's effort on, because they are
    the ones your gates did not see.
    """
    counts: dict[Caught, int] = {}
    for incident in incidents:
        counts[incident.caught_at] = counts.get(incident.caught_at, 0) + 1
    escaped = [i for i in incidents if STAGE_RANK[i.caught_at] >= STAGE_RANK[Caught.MONITORING]]
    preventable = [i for i in escaped if i.preventable_by]
    return DetectionReport(counts=counts, escaped=escaped, preventable=preventable)


def findings(tasks: list[Task], incidents: list[Incident]) -> list[str]:
    """The retrospective, as sentences that transfer to the next project."""
    out: list[str] = []
    cal = calibration(tasks)

    if cal.median_ratio > 1.0:
        out.append(
            f"Estimates ran {cal.median_ratio:.2f}x long at the median. "
            f"Multiply the next one by {cal.median_ratio:.2f} before committing to it."
        )
    elif cal.median_ratio and cal.median_ratio < 1.0:
        out.append(
            f"Estimates were {1 / cal.median_ratio:.2f}x conservative at the median — "
            "padding, which costs opportunities rather than deadlines."
        )

    if tasks and not is_uniform(tasks):
        out.append(
            f"The error is concentrated, not uniform: {cal.worst_area} ran "
            f"{cal.worst_area_ratio:.2f}x while {cal.best_area} ran {cal.best_area_ratio:.2f}x. "
            "A single multiplier will not fix this — estimate unfamiliar work differently."
        )

    report = detection(incidents)
    if report.escaped:
        out.append(
            f"{len(report.escaped)} of {sum(report.counts.values())} incidents reached production "
            f"({report.escape_rate:.0%})."
        )
    for incident in report.preventable:
        out.append(f"'{incident.what}' reached production and {incident.preventable_by} would have caught it.")

    if not out:
        out.append("No systematic pattern in the record. Keep the estimates and the gates as they are.")
    return out
