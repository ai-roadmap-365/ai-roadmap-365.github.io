"""Exercises 1-6 — replace `byhand.py` with a schema.

This file runs as it stands. It just does not do anything yet, and it says so
when you run it:

    python3 starter/models.py

Work through the numbered exercises in order. After each one, run:

    PYTEST=/path/to/pytest  # or use the lab's .venv
    "$PYTEST" starter -q

and delete the matching `@pytest.mark.skip` line in `starter/test_starter.py`
as each exercise starts passing. The reference answer for every exercise is in
`examples/models.py`; open it after you have tried, not before.

All names, station codes and operator initials in the sample data are invented
for this lab. No real monitoring network, person or measurement is involved.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Exercise 1 — the imports and the two Annotated types.
#
#   from datetime import datetime
#   from typing import Annotated
#   from pydantic import (
#       BaseModel, ConfigDict, Field, StringConstraints,
#       computed_field, field_validator, model_validator,
#   )
#
# Then declare the constrained types ONCE, so no field has to repeat them:
#
#   StationCode = Annotated[str, StringConstraints(pattern=r"^ST-[A-Z]{3}$")]
#   ReadingId   = Annotated[str, StringConstraints(pattern=r"^RD-\d{4}$")]
#   Percent     = Annotated[int, Field(ge=0, le=100)]
#   Micrograms  = Annotated[float, Field(ge=0.0, le=1000.0)]
#
# Check it: python3 -c "from pydantic import TypeAdapter; ..."  or just move on
# to exercise 2 — the tests will tell you.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Exercise 2 — the nested model.
#
# Define `class Station(BaseModel)` with:
#   * model_config = ConfigDict(extra="forbid", str_strip_whitespace=True,
#                               frozen=True)
#   * code: StationCode
#   * name: str, at least 1 and at most 60 characters (Field(min_length=...))
#   * elevation_m: int between -500 and 9000
#
# `extra="forbid"` is the one that catches a misspelled key. Without it, a
# record with `humidty_pct` validates happily and loses the field in silence.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Exercise 3 — the record model, and three words that are not synonyms.
#
# Define `class Reading(BaseModel)` with model_config = ConfigDict(
#     extra="forbid", str_strip_whitespace=True,
#     validate_assignment=True, populate_by_name=True)
#
# Fields:
#   reading_id: ReadingId
#   station: Station                      <- a nested model, validated in turn
#   recorded_at: datetime
#   pm25: Micrograms = Field(alias="pm2_5")   <- the vendor's name on the wire
#   temperature_c: float between -90.0 and 60.0
#   humidity_pct: Percent
#   operator: str | None                  <- REQUIRED and NULLABLE: the key must
#                                            be there; its value may be null
#   notes: str | None = None              <- OPTIONAL and nullable: it has a
#                                            default, so the key may be absent
#
# Required, optional and nullable are three separate facts. `operator` and
# `notes` differ only in that one has a default, and that difference is the
# whole distinction. Prove it to yourself: after this exercise,
# `Reading.model_json_schema()["required"]` should list `operator` and not
# `notes`.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Exercise 4 — two field validators.
#
# Add to Reading, each decorated @field_validator("<name>", mode="after") and
# @classmethod underneath it (order matters — field_validator goes on top):
#
#   * blank_note_is_no_note("notes"): if the value is a string that strips to
#     empty, return None instead. An empty string is not a note.
#   * timestamp_must_carry_a_timezone("recorded_at"): if value.tzinfo is None,
#     raise ValueError(...). A naive timestamp is an ambiguity, not a time.
#
# Raise plain ValueError inside a validator. pydantic catches it and folds it
# into the ValidationError with type "value_error" — you never raise
# ValidationError yourself.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Exercise 5 — the cross-field rule.
#
# Add @model_validator(mode="after") named a_high_reading_must_be_explained.
# It takes `self` (mode="after" runs on the built object) and returns `self`.
#
# The rule: if self.pm25 > 500.0 and there is no non-blank self.notes, raise
# ValueError. Above 500 the instrument is either witnessing something serious
# or misbehaving, and the difference is not in the number — so the schema
# demands a human wrote down which it was.
#
# No single-field constraint can express this, because it depends on two
# fields at once. That is exactly when you reach for model_validator.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Exercise 6 — a computed field.
#
# Add a `band` property decorated with @computed_field on top of @property,
# returning "good" (<=12.0), "moderate" (<=35.4),
# "unhealthy-for-sensitive-groups" (<=55.4), "unhealthy" (<=150.4), else
# "hazardous", based on self.pm25.
#
# Then run examples/serialize.py and notice what it does to the round trip.
# ---------------------------------------------------------------------------


def _unfinished() -> str:
    missing = [name for name in ("Station", "Reading") if name not in globals()]
    if not missing:
        return "Station and Reading are defined. Run the starter tests."
    return f"No schema yet: {', '.join(missing)} not defined. Start at exercise 1."


if __name__ == "__main__":
    print(_unfinished())
