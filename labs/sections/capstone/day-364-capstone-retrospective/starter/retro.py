"""STARTER -- implement the eight tasks below, then run the tests.

Turn a project's record into findings you can act on.

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
        """Actual over estimated. 1.0 is perfect, 2.0 is twice as long.

        TASK 1. Guard the zero estimate -- a task nobody estimated is a real
        case in a real record, and it must not raise.
        """
        raise NotImplementedError("TASK 1: return actual over estimated, 0.0 if no estimate")


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
    raise NotImplementedError(
        "TASK 2: return the median. Even counts average the middle two; "
        "an empty list is 0.0. Do NOT use the mean."
    )


def by_area(tasks: list[Task]) -> dict[str, float]:
    """Median ratio per area of work."""
    raise NotImplementedError("TASK 3: group ratios by task.area, then median each group")


def calibration(tasks: list[Task]) -> Calibration:
    """How wrong the estimates were, and where the error concentrates."""
    raise NotImplementedError(
        "TASK 4: build a Calibration. Empty input returns an empty Calibration "
        "rather than raising. Count DIRECTION separately -- a task at exactly "
        "1.0 is neither under nor over."
    )


def is_uniform(tasks: list[Task], *, spread: float = 1.5) -> bool:
    """Whether the estimation error is spread evenly across areas.

    A uniform error is a multiplier you can apply next time. A concentrated one
    means you estimate familiar work well and unfamiliar work badly, which
    needs a different fix -- and the overall median hides which you have.
    """
    raise NotImplementedError(
        "TASK 5: compare the HIGHEST area against the LOWEST, not against the "
        "overall median. Fewer than two areas is trivially uniform."
    )


def apply_multiplier(estimate: float, cal: Calibration) -> float:
    """What this estimate becomes once your own history is applied."""
    raise NotImplementedError("TASK 6: apply the median ratio, rounded to one decimal")


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
    raise NotImplementedError(
        "TASK 7: count by stage, and collect the escapes. Use STAGE_RANK -- an "
        "incident caught in STAGING was deployed but reached nobody, so it is "
        "NOT an escape."
    )


def findings(tasks: list[Task], incidents: list[Incident]) -> list[str]:
    """The retrospective, as sentences that transfer to the next project."""
    raise NotImplementedError(
        "TASK 8: produce sentences, not scores. Cover (a) the multiplier when "
        "estimates ran long, or the padding when they ran short; (b) a "
        "concentrated error, naming both areas; (c) the escape count; (d) one "
        "line per preventable escape naming the gate. If none of those apply, "
        "say the record is clean rather than inventing a finding."
    )

