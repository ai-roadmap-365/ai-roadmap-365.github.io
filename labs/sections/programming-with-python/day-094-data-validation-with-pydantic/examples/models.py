"""The boundary schema for the air-quality feed, written with pydantic v2.

Every record that enters the pipeline is checked against ``Reading`` before any
other code is allowed to see it. If a record does not satisfy this file, it does
not exist as far as the rest of the program is concerned.

All names, station codes and operator initials in the sample data are invented
for this lab. No real monitoring network, person or measurement is involved.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
    model_validator,
)

__all__ = ["Reading", "Station", "StationCode", "Percent", "Micrograms"]


# --------------------------------------------------------------------------
# Annotated types: say what a constrained value *is*, once, then reuse it.
# --------------------------------------------------------------------------

StationCode = Annotated[str, StringConstraints(pattern=r"^ST-[A-Z]{3}$")]
"""A station code: the letters ``ST-`` and exactly three capitals, e.g. ST-KLM."""

Percent = Annotated[int, Field(ge=0, le=100)]
"""A whole percentage. 0 and 100 are both legal; 101 is not."""

Micrograms = Annotated[float, Field(ge=0.0, le=1000.0)]
"""Micrograms per cubic metre. Negative is impossible; 1000 is the sensor ceiling."""

ReadingId = Annotated[str, StringConstraints(pattern=r"^RD-\d{4}$")]
"""A reading id: ``RD-`` and exactly four digits."""


# --------------------------------------------------------------------------
# The models
# --------------------------------------------------------------------------


class Station(BaseModel):
    """Where a reading was taken. A nested model, validated in its own right."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        frozen=True,
    )

    code: StationCode
    name: str = Field(min_length=1, max_length=60, description="Human-readable site name")
    elevation_m: int = Field(ge=-500, le=9000, description="Metres above sea level")


class Reading(BaseModel):
    """One measurement from one station at one moment."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
        populate_by_name=True,
    )

    reading_id: ReadingId
    station: Station
    recorded_at: datetime = Field(description="ISO 8601 timestamp, timezone required")

    # The vendor's export writes ``pm2_5``; the rest of this codebase says
    # ``pm25``. The alias is where that difference is absorbed, once.
    pm25: Micrograms = Field(alias="pm2_5", description="PM2.5 concentration")

    temperature_c: float = Field(ge=-90.0, le=60.0)
    humidity_pct: Percent

    # Required, and may be null. Three different things live in these two lines:
    #   * ``operator`` is REQUIRED — the key must be present — and NULLABLE.
    #   * ``notes`` is OPTIONAL — it has a default — and also nullable.
    # A field can be optional and not nullable, or nullable and not optional.
    operator: str | None
    notes: str | None = None

    @field_validator("notes", mode="after")
    @classmethod
    def blank_note_is_no_note(cls, value: str | None) -> str | None:
        """An empty string is not a note. Normalise it away before it spreads."""
        if value is not None and value.strip() == "":
            return None
        return value

    @field_validator("recorded_at", mode="after")
    @classmethod
    def timestamp_must_carry_a_timezone(cls, value: datetime) -> datetime:
        """A naive timestamp is an ambiguity, not a time."""
        if value.tzinfo is None:
            raise ValueError("recorded_at must include a timezone offset")
        return value

    @model_validator(mode="after")
    def a_high_reading_must_be_explained(self) -> Reading:
        """A cross-field rule: no single-field constraint can express this.

        Above 500 micrograms the instrument is either witnessing something
        serious or misbehaving, and the difference is not in the number. The
        schema therefore demands that a human wrote down which it was.
        """
        if self.pm25 > 500.0 and not (self.notes and self.notes.strip()):
            raise ValueError("a pm25 reading above 500 requires a note explaining it")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def band(self) -> str:
        """A derived label. Stored nowhere, serialised everywhere."""
        if self.pm25 <= 12.0:
            return "good"
        if self.pm25 <= 35.4:
            return "moderate"
        if self.pm25 <= 55.4:
            return "unhealthy-for-sensitive-groups"
        if self.pm25 <= 150.4:
            return "unhealthy"
        return "hazardous"
