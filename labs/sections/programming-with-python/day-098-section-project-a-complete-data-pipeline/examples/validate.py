"""Stage 2 — Validate.

**The promise:** nothing enters the store that the store's own constraints would
have to argue with, every bad record is reported well enough to fix the source,
and one bad record does not end the run.

This is Day 94's gate at a boundary, with one addition that matters more than
the model itself: ``collect``. The obvious implementation raises on the first
failure, and it is wrong for a pipeline. If a source starts sending 400 bad
records out of 10,000, "the first one failed" is a bug report you cannot act on.
"3,942 records rejected, 3,940 of them because humidity_pct exceeded 100, first
offender b-4471 at 2026-08-16T04:15:00Z" is a message you can forward to
whoever owns the sensor.

``Reading`` is deliberately strict:

* ``extra="forbid"`` — an unexpected field is a signal that the source changed
  shape, and silently ignoring it is how a schema drift goes unnoticed for a
  quarter.
* ``observed_at`` must be timezone-aware (Day 95). A naive timestamp is not an
  instant; it is an instant plus an assumption, and the assumption is usually
  the assumption of whoever wrote the code, not whoever ran it.
* The ranges are physical, not arbitrary: humidity is a percentage, and the
  recorded temperature extremes on Earth sit inside -90 to 60 Celsius.

Note what the gate can*not* catch, because the lab has a record for it: bravo's
b-4 reports 41.3 Celsius five minutes after 15.0 Celsius. Every field is legal.
Only a rule about the *sequence* sees it, and that rule lives in the report.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class Reading(BaseModel):
    """One sensor reading, as it is allowed to exist inside this pipeline."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    station_id: str = Field(min_length=1, max_length=32)
    reading_id: str = Field(min_length=1, max_length=64)
    observed_at: datetime
    temperature_c: float = Field(ge=-90.0, le=60.0)
    humidity_pct: int = Field(ge=0, le=100)

    @field_validator("observed_at")
    @classmethod
    def must_be_absolute(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("observed_at must carry a UTC offset (it is an instant, not a date)")
        return value.astimezone(timezone.utc)

    @property
    def temperature_dc(self) -> int:
        """Deci-Celsius. The store keeps an integer; see store.py for why."""
        return round(self.temperature_c * 10)

    @property
    def observed_at_text(self) -> str:
        return self.observed_at.strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class Rejection:
    """One record that did not get in, and enough detail to fix its source."""

    source: str
    index: int
    reading_id: str
    problems: tuple[str, ...]

    def __str__(self) -> str:
        return f"{self.source}[{self.index}] {self.reading_id}: " + "; ".join(self.problems)


@dataclass(frozen=True)
class ValidationOutcome:
    accepted: list[Reading]
    rejected: list[Rejection]

    @property
    def considered(self) -> int:
        return len(self.accepted) + len(self.rejected)

    def reasons(self) -> dict[str, int]:
        """How many rejections per distinct problem, worst first."""
        counts: dict[str, int] = {}
        for rejection in self.rejected:
            for problem in rejection.problems:
                field_name = problem.split(":", 1)[0]
                counts[field_name] = counts.get(field_name, 0) + 1
        return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _problems(error: ValidationError) -> tuple[str, ...]:
    out = []
    for detail in error.errors():
        location = ".".join(str(part) for part in detail["loc"]) or "<record>"
        out.append(f"{location}: {detail['msg']}")
    return tuple(out)


def validate_records(source: str, raw_records: list[dict]) -> ValidationOutcome:
    """Validate every record. Collect the failures; never raise."""
    accepted: list[Reading] = []
    rejected: list[Rejection] = []
    for index, raw in enumerate(raw_records):
        try:
            accepted.append(Reading.model_validate(raw))
        except ValidationError as error:
            identifier = str(raw.get("reading_id", "<no reading_id>")) if isinstance(raw, dict) else "<not an object>"
            rejected.append(
                Rejection(
                    source=source,
                    index=index,
                    reading_id=identifier,
                    problems=_problems(error),
                )
            )
    return ValidationOutcome(accepted=accepted, rejected=rejected)


def validate_all(fetched: dict[str, list[dict]]) -> ValidationOutcome:
    """Run the gate across every source's records, in source order."""
    accepted: list[Reading] = []
    rejected: list[Rejection] = []
    for source, records in fetched.items():
        outcome = validate_records(source, records)
        accepted.extend(outcome.accepted)
        rejected.extend(outcome.rejected)
    return ValidationOutcome(accepted=accepted, rejected=rejected)
