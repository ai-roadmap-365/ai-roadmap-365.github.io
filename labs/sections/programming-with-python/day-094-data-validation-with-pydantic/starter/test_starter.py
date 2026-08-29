"""The starter suite. One test passes today; nine are waiting for you.

Delete the `@pytest.mark.skip(...)` line above a test as soon as the matching
exercise is done, then run the suite again:

    "$PYTEST" starter -q

Every assertion below is on an error's `type` or its `loc`. Not one of them
looks at `msg`. That is deliberate and it is the habit worth taking away from
today: `type` and `loc` are the machine-readable contract, and `msg` is prose
the library is free to reword in any release. The same argument applied to a
FastAPI 422 body on Day 082; it is the same body.

All names, station codes and operator initials here are invented for this lab.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

LAB_DIR = Path(__file__).resolve().parent.parent
BATCH = LAB_DIR / "data" / "raw-readings.json"


def load_batch() -> list[dict]:
    with BATCH.open(encoding="utf-8") as handle:
        return json.load(handle)


def locs_and_types(exc_info) -> set[tuple[tuple, str]]:
    """Every problem as (loc, type). The only two things worth asserting on."""
    return {(tuple(e["loc"]), e["type"]) for e in exc_info.value.errors()}


VALID = {
    "reading_id": "RD-0042",
    "station": {"code": "ST-KLM", "name": "Kalmar Ridge", "elevation_m": 340},
    "recorded_at": "2026-08-15T06:00:00Z",
    "pm2_5": 12.4,
    "temperature_c": 18.2,
    "humidity_pct": 61,
    "operator": "R. Nayar",
    "notes": None,
}


# ---------------------------------------------------------------------------
# This one passes right now. It is the "before" picture, tested.
# ---------------------------------------------------------------------------


def test_the_hand_written_validator_catches_a_bad_number_and_misses_a_bad_range():
    from byhand import validate_reading_by_hand

    records = load_batch()

    # Record 3 has pm2_5 = "not-measured". float() refuses it, so the hand
    # written check does too.
    _, problems = validate_reading_by_hand(records[3])
    assert problems, "the hand-written validator should reject a non-numeric pm2_5"

    # Record 4 has humidity_pct = 118. There is no range rule anywhere in
    # byhand.py, so it sails through. This assertion documents a hole.
    clean, problems = validate_reading_by_hand(records[4])
    assert problems == []
    assert clean["humidity_pct"] == 118


# ---------------------------------------------------------------------------
# Exercise 2
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="Exercise 2: define Station in starter/models.py")
def test_station_rejects_a_code_that_does_not_match_the_pattern():
    from models import Station
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        Station(code="ST-north", name="Northgate Yard", elevation_m=210)
    assert (("code",), "string_pattern_mismatch") in locs_and_types(exc_info)


@pytest.mark.skip(reason="Exercise 2: set extra='forbid' on Station")
def test_station_refuses_an_unexpected_key():
    from models import Station
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        Station(code="ST-KLM", name="Kalmar Ridge", elevation_m=340, elevaton_m=340)
    assert (("elevaton_m",), "extra_forbidden") in locs_and_types(exc_info)


# ---------------------------------------------------------------------------
# Exercise 3
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="Exercise 3: required, optional and nullable are three things")
def test_required_optional_and_nullable_are_three_different_things():
    from models import Reading
    from pydantic import ValidationError

    required = set(Reading.model_json_schema()["required"])
    # operator is REQUIRED (the key must be present) and NULLABLE (may be null).
    assert "operator" in required
    # notes is OPTIONAL (it has a default) and also nullable.
    assert "notes" not in required

    # Nullable: an explicit null is fine.
    assert Reading.model_validate({**VALID, "operator": None}).operator is None

    # Required: leaving the key out is not.
    without_operator = {k: v for k, v in VALID.items() if k != "operator"}
    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate(without_operator)
    assert (("operator",), "missing") in locs_and_types(exc_info)

    # Optional: leaving `notes` out is fine, and the default arrives.
    without_notes = {k: v for k, v in VALID.items() if k != "notes"}
    assert Reading.model_validate(without_notes).notes is None


@pytest.mark.skip(reason="Exercise 3: give pm25 the alias 'pm2_5'")
def test_the_alias_is_the_name_on_the_wire_and_the_name_in_the_error():
    from models import Reading
    from pydantic import ValidationError

    reading = Reading.model_validate(VALID)
    assert reading.pm25 == pytest.approx(12.4)

    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate({**VALID, "pm2_5": "not-measured"})
    # The error names the key the caller actually sent, which is what makes the
    # report usable by whoever owns the source file.
    assert (("pm2_5",), "float_parsing") in locs_and_types(exc_info)


@pytest.mark.skip(reason="Exercise 3: lax mode coerces, strict mode does not")
def test_lax_mode_coerces_numeric_strings_and_strict_mode_refuses_them():
    from models import Reading
    from pydantic import ValidationError

    stringy = {
        **VALID,
        "station": {"code": "ST-KLM", "name": "  Kalmar Ridge  ", "elevation_m": "340"},
        "pm2_5": "14.8",
        "temperature_c": "19",
        "humidity_pct": "58",
    }

    lax = Reading.model_validate(stringy)
    assert lax.station.elevation_m == 340
    assert lax.pm25 == pytest.approx(14.8)
    assert lax.humidity_pct == 58
    # str_strip_whitespace is on, so the padded name arrives trimmed.
    assert lax.station.name == "Kalmar Ridge"

    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate(stringy, strict=True)
    found = locs_and_types(exc_info)
    assert (("pm2_5",), "float_type") in found
    assert (("humidity_pct",), "int_type") in found


# ---------------------------------------------------------------------------
# Exercise 4 and 5
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="Exercise 4: constrain humidity_pct to 0-100")
def test_an_out_of_range_percentage_is_refused_with_a_range_error_type():
    from models import Reading
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate({**VALID, "humidity_pct": 118})
    assert (("humidity_pct",), "less_than_equal") in locs_and_types(exc_info)


@pytest.mark.skip(reason="Exercise 5: the cross-field model_validator")
def test_a_high_reading_needs_a_note_and_the_error_sits_on_the_whole_record():
    from models import Reading
    from pydantic import ValidationError

    hot = {**VALID, "pm2_5": 612.5, "notes": None}
    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate(hot)
    # loc is empty: no single field is at fault, the combination is.
    assert ((), "value_error") in locs_and_types(exc_info)

    explained = {**hot, "notes": "smoke plume from the north, confirmed by the duty log"}
    assert Reading.model_validate(explained).pm25 == pytest.approx(612.5)


@pytest.mark.skip(reason="Exercises 2-5: a ValidationError reports everything at once")
def test_one_call_reports_every_problem_rather_than_the_first():
    from models import Reading
    from pydantic import ValidationError

    broken = {
        "reading_id": "RD-0099",
        "station": {"code": "ST-QQQ", "name": "Quarry Head", "elevation_m": "high"},
        "recorded_at": "2026-08-15T13:00:00Z",
        "pm2_5": "unreadable",
        "temperature_c": 20.0,
        "humidity_pct": None,
        "operator": "A. Invented",
    }
    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate(broken)

    found = locs_and_types(exc_info)
    assert (("station", "elevation_m"), "int_parsing") in found
    assert (("pm2_5",), "float_parsing") in found
    assert (("humidity_pct",), "int_type") in found
    # Three problems, one exception, one round trip to fix them all.
    assert len(exc_info.value.errors()) == 3


# ---------------------------------------------------------------------------
# Exercises 7-10
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="Exercises 7-9: build the gate in starter/gate.py")
def test_the_gate_finishes_the_whole_batch_with_a_non_zero_reject_count():
    import gate

    records = gate.load_records(BATCH)
    # The whole point: this call must RETURN, not raise, on a batch that is
    # two-thirds bad. If a ValidationError escapes here, the gate is not a gate.
    result = gate.run_gate(records)

    assert result.seen == len(records)
    assert result.rejected_count > 0
    assert result.accepted_count + result.rejected_count == result.seen

    types = set(result.error_types())
    for expected in (
        "missing",
        "float_parsing",
        "less_than_equal",
        "extra_forbidden",
        "string_pattern_mismatch",
        "duplicate_id",
        "datetime_from_date_parsing",
        "value_error",
    ):
        assert expected in types, f"the batch should have produced a {expected}"

    # Every rejection can name itself well enough to fix the source.
    for rejection in result.rejected:
        assert rejection.errors
        for error in rejection.errors:
            assert isinstance(error["type"], str) and error["type"]
            assert isinstance(list(error["loc"]), list)
