"""STARTER -- implement the eight tasks below, then run the tests.

Check whether a post-course learning plan is a plan or a wish list.

Offline and standard-library only. The input is a list of written commitments,
so nothing is fetched.

Almost every plan made at the end of a course dies in about week three, and it
usually dies for one of two reasons that are visible in the plan itself before
it starts:

  not actionable   "get better at evals" names a topic, not a next action
  not affordable   the hours it needs exceed the hours you actually have

The second is the one that kills plans, and it is the one nobody checks. Six
commitments that each sound modest can add up to three times the time you have,
and the failure arrives as a vague sense of falling behind rather than as an
arithmetic error -- which is why it is never diagnosed and never fixed.

So this module does the arithmetic. It also applies your OWN calibration from
day 364, because a plan costed in optimistic hours is not costed at all.

Nothing here judges whether your goals are worthwhile. It checks whether the
plan is one you could actually execute, which is a different question and the
one that decides the outcome.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Verbs that name a topic rather than an action. Each one describes a state you
# would like to be in, and none of them tells you what to do on Monday.
TOPIC_VERBS = (
    "learn",
    "study",
    "explore",
    "understand",
    "get better at",
    "get familiar with",
    "read about",
    "look into",
    "dive into",
    "master",
    "improve my",
    "brush up",
)

# A next action starts with something you could begin within the hour.
ACTION_VERB = re.compile(
    r"^\s*(build|write|ship|deploy|measure|benchmark|implement|port|replace|"
    r"instrument|profile|reproduce|publish|contribute|review|refactor|migrate|"
    r"automate|test|add|fix|extend|compare|run)\b",
    re.I,
)


@dataclass(frozen=True)
class Commitment:
    topic: str
    next_action: str
    artifact: str  # what exists afterwards that did not exist before
    hours_per_week: float
    weeks: int
    priority: int = 3  # 1 is highest

    @property
    def total_hours(self) -> float:
        return self.hours_per_week * self.weeks


@dataclass
class Load:
    weekly: float
    available: float

    @property
    def ratio(self) -> float:
        """How many times over budget the plan is. 1.0 exactly fits."""
        return self.weekly / self.available if self.available else 0.0

    @property
    def fits(self) -> bool:
        return self.weekly <= self.available

    def line(self) -> str:
        return (
            f"needs {self.weekly:.1f}h/week  have {self.available:.1f}h/week  "
            f"{self.ratio:.2f}x  {'fits' if self.fits else 'OVER'}"
        )


def topic_verbs_in(text: str) -> list[str]:
    lowered = text.lower()
    return sorted(v for v in TOPIC_VERBS if lowered.startswith(v) or f" {v}" in lowered)


def is_actionable(next_action: str) -> bool:
    """Whether this is something you could start within the hour.

    Two conditions, and both are needed. A topic verb disqualifies it even when
    an action verb appears later in the sentence, because "build up my
    understanding of evals" is a topic wearing an action's clothes.
    """
    raise NotImplementedError(
        "TASK 1: empty is not actionable; a topic verb anywhere disqualifies it "
        "even when an action verb also appears; otherwise require an action verb "
        "at the START of the sentence."
    )


def has_artifact(commitment: Commitment) -> bool:
    """Whether something exists afterwards that did not exist before.

    This is what makes a commitment checkable by anyone, including future you.
    "Confidence with agents" is not an artifact. A repository is.
    """
    raise NotImplementedError("TASK 2: whitespace is not an artifact")


def weekly_load(commitments: list[Commitment], available: float) -> Load:
    raise NotImplementedError("TASK 3: sum the weekly hours into a Load")


def with_calibration(commitments: list[Commitment], ratio: float) -> list[Commitment]:
    """Re-cost the plan in YOUR hours rather than optimistic ones.

    Day 364 measured how wrong your estimates are. A plan costed without that
    correction is costed in hours belonging to somebody who does not exist.
    """
    raise NotImplementedError(
        "TASK 4: scale hours_per_week by the ratio, rounded to 2 decimals, and "
        "change NOTHING else. A ratio of zero or less is nonsense -- return the "
        "plan unchanged rather than zeroing it."
    )


def trim_to_fit(commitments: list[Commitment], available: float) -> list[Commitment]:
    """What actually survives the hours you have, highest priority first.

    Deliberately not proportional. Halving the hours on six commitments gives
    you six things done badly; keeping two gives you two things done. The plan
    that fits is the plan that happens.
    """
    raise NotImplementedError(
        "TASK 5: highest priority first, keeping each commitment that still "
        "fits. SKIP past one that does not and carry on -- stopping would waste "
        "every remaining hour."
    )


def dropped(commitments: list[Commitment], available: float) -> list[Commitment]:
    """What the trim removed. Worth naming, so the choice is made rather than
    discovered in week three."""
    raise NotImplementedError(
        "TASK 6: everything the trim removed. Careful -- two identical "
        "commitments are EQUAL as dataclasses, so a value-based membership test "
        "drops both."
    )


@dataclass
class PlanReport:
    load: Load
    not_actionable: list[Commitment] = field(default_factory=list)
    no_artifact: list[Commitment] = field(default_factory=list)
    kept: list[Commitment] = field(default_factory=list)
    cut: list[Commitment] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"{len(self.kept)} kept / {len(self.cut)} cut  "
            f"not-actionable={len(self.not_actionable)} no-artifact={len(self.no_artifact)}"
        )


def review(commitments: list[Commitment], available: float, *, calibration: float = 1.0) -> PlanReport:
    """The whole check, in your own hours."""
    raise NotImplementedError(
        "TASK 7: apply the calibration FIRST, then measure everything against "
        "the re-costed plan rather than the optimistic one."
    )


def findings(commitments: list[Commitment], available: float, *, calibration: float = 1.0) -> list[str]:
    """The review, as sentences you can act on before week one."""
    raise NotImplementedError(
        "TASK 8: sentences, not scores. Cover (a) that calibration was applied, "
        "when it was; (b) how far over the plan is, or that it fits; (c) how "
        "many commitments survive, and one line naming each cut; (d) one line "
        "per commitment that names a topic rather than an action, quoting the "
        "wording to rewrite; (e) one per commitment with no artifact."
    )
