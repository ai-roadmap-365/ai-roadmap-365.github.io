"""A small, honest cron-expression parser.

Five fields, separated by whitespace:

    minute  hour  day-of-month  month  day-of-week
    0-59    0-23  1-31          1-12   0-6 (0 = Sunday, 7 also accepted)

Each field is ``*``, a number, a comma-separated list, an ``a-b`` range, or a
step written ``*/n`` or ``a-b/n``. This module implements exactly that, and
nothing it does not implement is silently accepted: an unparseable field
raises ``CronError`` rather than matching everything, because a schedule that
quietly means "every minute" is a bad way to find out you made a typo.

The one rule everybody gets wrong is in :func:`matches`. When BOTH the
day-of-month and the day-of-week fields are restricted, cron ORs them: the job
runs on days matching either. Everywhere else the fields are ANDed. This
module reproduces that rule and the test suite pins it.

Real cron implementations differ in extensions (``@daily``, ``L``, ``W``,
names like ``MON``, seconds fields in some libraries). This parser handles the
classic five numeric fields only, and says so rather than pretending.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


class CronError(ValueError):
    """Raised when an expression cannot be parsed."""


FIELD_RANGES: tuple[tuple[str, int, int], ...] = (
    ("minute", 0, 59),
    ("hour", 0, 23),
    ("day-of-month", 1, 31),
    ("month", 1, 12),
    ("day-of-week", 0, 7),
)


def _parse_field(spec: str, name: str, low: int, high: int) -> tuple[frozenset[int], bool]:
    """Return the set of matching values and whether the field is restricted."""
    restricted = spec.strip() != "*"
    values: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            raise CronError(f"{name}: empty item in {spec!r}")
        step = 1
        if "/" in part:
            part, _, step_text = part.partition("/")
            try:
                step = int(step_text)
            except ValueError:
                raise CronError(f"{name}: step {step_text!r} is not a number") from None
            if step < 1:
                raise CronError(f"{name}: step must be 1 or more, got {step}")
        if part == "*":
            start, end = low, high
        elif "-" in part.lstrip("-"):
            start_text, _, end_text = part.partition("-")
            start, end = _int(start_text, name), _int(end_text, name)
        else:
            start = end = _int(part, name)
        if start > end:
            raise CronError(f"{name}: range {part!r} runs backwards")
        if start < low or end > high:
            raise CronError(f"{name}: {part!r} is outside {low}-{high}")
        values.update(range(start, end + 1, step))
    if name == "day-of-week" and 7 in values:
        # Both 0 and 7 mean Sunday. Normalise so matching has one answer.
        values.discard(7)
        values.add(0)
    return frozenset(values), restricted


def _int(text: str, name: str) -> int:
    try:
        return int(text)
    except ValueError:
        raise CronError(f"{name}: {text!r} is not a number") from None


@dataclass(frozen=True)
class CronSchedule:
    """A parsed five-field cron expression."""

    expression: str
    minutes: frozenset[int]
    hours: frozenset[int]
    days_of_month: frozenset[int]
    months: frozenset[int]
    days_of_week: frozenset[int]
    dom_restricted: bool
    dow_restricted: bool

    def matches(self, moment: dt.datetime) -> bool:
        """Would cron fire at this minute?

        Seconds are ignored: cron's resolution is one minute.
        """
        if moment.minute not in self.minutes:
            return False
        if moment.hour not in self.hours:
            return False
        if moment.month not in self.months:
            return False
        # Python: Monday is 0 and Sunday is 6. Cron: Sunday is 0.
        dow = (moment.weekday() + 1) % 7
        dom_hit = moment.day in self.days_of_month
        dow_hit = dow in self.days_of_week
        if self.dom_restricted and self.dow_restricted:
            return dom_hit or dow_hit  # the OR-not-AND rule
        return dom_hit and dow_hit

    def next_run_after(self, moment: dt.datetime, *, horizon_days: int = 400) -> dt.datetime:
        """The first matching minute strictly after ``moment``.

        Walks forward a minute at a time. That is not clever, but for a
        schedule that fires at least once a year it is fast enough (a daily
        job is found within 1440 steps) and it is obviously correct, which
        matters more here than speed.
        """
        candidate = moment.replace(second=0, microsecond=0) + dt.timedelta(minutes=1)
        limit = candidate + dt.timedelta(days=horizon_days)
        while candidate < limit:
            if self.matches(candidate):
                return candidate
            candidate += dt.timedelta(minutes=1)
        raise CronError(
            f"{self.expression!r} has no run within {horizon_days} days of {moment.isoformat()}"
        )

    def describe(self) -> str:
        """A plain-English summary, so a generated line can be read back."""
        parts = [
            f"minute {_summarise(self.minutes)}",
            f"hour {_summarise(self.hours)}",
            f"day-of-month {'any' if not self.dom_restricted else _summarise(self.days_of_month)}",
            f"month {'any' if self.months == frozenset(range(1, 13)) else _summarise(self.months)}",
            f"day-of-week {'any' if not self.dow_restricted else _summarise(self.days_of_week)}",
        ]
        note = ""
        if self.dom_restricted and self.dow_restricted:
            note = "  (day-of-month OR day-of-week — cron ORs these two when both are set)"
        return " · ".join(parts) + note


def _summarise(values: frozenset[int]) -> str:
    ordered = sorted(values)
    if len(ordered) > 6:
        return f"{ordered[0]}..{ordered[-1]} ({len(ordered)} values)"
    return ",".join(str(v) for v in ordered)


def parse(expression: str) -> CronSchedule:
    """Parse a five-field cron expression, or raise :class:`CronError`."""
    fields = expression.split()
    if len(fields) != 5:
        raise CronError(
            f"expected 5 fields (minute hour day-of-month month day-of-week), "
            f"got {len(fields)} in {expression!r}"
        )
    parsed = [
        _parse_field(field, name, low, high)
        for field, (name, low, high) in zip(fields, FIELD_RANGES, strict=True)
    ]
    return CronSchedule(
        expression=expression,
        minutes=parsed[0][0],
        hours=parsed[1][0],
        days_of_month=parsed[2][0],
        months=parsed[3][0],
        days_of_week=parsed[4][0],
        dom_restricted=parsed[2][1],
        dow_restricted=parsed[4][1],
    )
