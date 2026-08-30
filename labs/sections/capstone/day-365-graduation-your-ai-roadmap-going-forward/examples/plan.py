"""Check whether a post-course learning plan is a plan or a wish list.

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
    if not next_action.strip():
        return False
    if topic_verbs_in(next_action):
        return False
    return ACTION_VERB.search(next_action) is not None


def has_artifact(commitment: Commitment) -> bool:
    """Whether something exists afterwards that did not exist before.

    This is what makes a commitment checkable by anyone, including future you.
    "Confidence with agents" is not an artifact. A repository is.
    """
    return bool(commitment.artifact.strip())


def weekly_load(commitments: list[Commitment], available: float) -> Load:
    return Load(weekly=sum(c.hours_per_week for c in commitments), available=available)


def with_calibration(commitments: list[Commitment], ratio: float) -> list[Commitment]:
    """Re-cost the plan in YOUR hours rather than optimistic ones.

    Day 364 measured how wrong your estimates are. A plan costed without that
    correction is costed in hours belonging to somebody who does not exist.
    """
    if ratio <= 0:
        return list(commitments)
    return [
        Commitment(
            topic=c.topic,
            next_action=c.next_action,
            artifact=c.artifact,
            hours_per_week=round(c.hours_per_week * ratio, 2),
            weeks=c.weeks,
            priority=c.priority,
        )
        for c in commitments
    ]


def trim_to_fit(commitments: list[Commitment], available: float) -> list[Commitment]:
    """What actually survives the hours you have, highest priority first.

    Deliberately not proportional. Halving the hours on six commitments gives
    you six things done badly; keeping two gives you two things done. The plan
    that fits is the plan that happens.
    """
    kept: list[Commitment] = []
    spent = 0.0
    for c in sorted(commitments, key=lambda c: (c.priority, -c.hours_per_week, c.topic)):
        if spent + c.hours_per_week <= available:
            kept.append(c)
            spent += c.hours_per_week
    return kept


def dropped(commitments: list[Commitment], available: float) -> list[Commitment]:
    """What the trim removed. Worth naming, so the choice is made rather than
    discovered in week three."""
    kept = {id(c) for c in trim_to_fit(commitments, available)}
    return [c for c in commitments if id(c) not in kept]


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
    costed = with_calibration(commitments, calibration)
    return PlanReport(
        load=weekly_load(costed, available),
        not_actionable=[c for c in costed if not is_actionable(c.next_action)],
        no_artifact=[c for c in costed if not has_artifact(c)],
        kept=trim_to_fit(costed, available),
        cut=dropped(costed, available),
    )


def findings(commitments: list[Commitment], available: float, *, calibration: float = 1.0) -> list[str]:
    """The review, as sentences you can act on before week one."""
    out: list[str] = []
    report = review(commitments, available, calibration=calibration)

    if calibration > 1.0:
        out.append(
            f"Costed at your measured {calibration:.2f}x rather than in optimistic hours."
        )

    if not report.load.fits:
        out.append(
            f"The plan needs {report.load.weekly:.1f}h/week and you have "
            f"{report.load.available:.1f}h — it is {report.load.ratio:.2f}x over before it starts."
        )
        out.append(
            f"{len(report.kept)} of {len(commitments)} commitments fit. Cut the rest now, "
            "deliberately, rather than in week three by attrition."
        )
        for c in report.cut:
            out.append(f"cut: {c.topic} (priority {c.priority}, {c.hours_per_week:.1f}h/week)")
    else:
        out.append(
            f"The plan fits: {report.load.weekly:.1f}h/week against {report.load.available:.1f}h "
            "available. Rare, and worth not filling."
        )

    for c in report.not_actionable:
        out.append(f"'{c.topic}' names a topic, not a next action — rewrite '{c.next_action}'.")
    for c in report.no_artifact:
        out.append(f"'{c.topic}' produces nothing checkable. Name what will exist afterwards.")

    return out
