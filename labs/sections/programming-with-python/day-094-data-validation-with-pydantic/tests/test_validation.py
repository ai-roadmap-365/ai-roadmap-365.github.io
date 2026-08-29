"""The reference suite for Day 094 — the schema, the gate, and the toy.

Every assertion here is on an error's `type` or its `loc`, on a count, or on a
validated value. Not one of them reads `msg`. `type` and `loc` are the parts of
a `ValidationError` pydantic treats as an interface; `msg` is prose it is free
to reword between releases, exactly as a FastAPI 422 body's `msg` is (Day 082).
A suite that greps error text passes until the day somebody improves a sentence.

Run from the lab directory:

    "$PYTEST" tests -q

All names, station codes and operator initials in the fixtures are invented for
this lab. No real monitoring network, person or measurement is involved.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

LAB_DIR = Path(__file__).resolve().parent.parent
EXAMPLES = LAB_DIR / "examples"
BATCH = LAB_DIR / "data" / "raw-readings.json"

sys.path.insert(0, str(EXAMPLES))

from gate import GateResult, load_records, run_gate, write_outputs  # noqa: E402
from models import Reading, Station  # noqa: E402
from pydantic import TypeAdapter, ValidationError  # noqa: E402
from scratch_models import ScratchReading  # noqa: E402
from scratch_validator import validate as mini_validate  # noqa: E402

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


def problems(exc_info) -> set[tuple[tuple, str]]:
    """Every error as (loc, type) — the two stable parts."""
    return {(tuple(e["loc"]), e["type"]) for e in exc_info.value.errors()}


@pytest.fixture(scope="module")
def records() -> list[dict]:
    return load_records(BATCH)


@pytest.fixture(scope="module")
def result(records) -> GateResult:
    return run_gate(records)


# ---------------------------------------------------------------------------
# The schema
# ---------------------------------------------------------------------------


def test_a_clean_record_validates_into_a_typed_object():
    reading = Reading.model_validate(VALID)
    assert reading.reading_id == "RD-0042"
    assert isinstance(reading.station, Station)
    assert reading.recorded_at.tzinfo is not None
    assert reading.pm25 == pytest.approx(12.4)
    assert reading.band == "moderate"


def test_required_optional_and_nullable_are_three_different_things():
    required = set(Reading.model_json_schema()["required"])
    assert "operator" in required, "operator is required — the key must be present"
    assert "notes" not in required, "notes is optional — it has a default"

    assert Reading.model_validate({**VALID, "operator": None}).operator is None

    without_operator = {k: v for k, v in VALID.items() if k != "operator"}
    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate(without_operator)
    assert (("operator",), "missing") in problems(exc_info)

    without_notes = {k: v for k, v in VALID.items() if k != "notes"}
    assert Reading.model_validate(without_notes).notes is None


def test_a_misspelled_key_is_caught_rather_than_silently_dropped():
    typo = {k: v for k, v in VALID.items() if k != "humidity_pct"}
    typo["humidty_pct"] = 61
    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate(typo)
    found = problems(exc_info)
    assert (("humidty_pct",), "extra_forbidden") in found
    assert (("humidity_pct",), "missing") in found


def test_the_nested_model_reports_its_own_location():
    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate(
            {**VALID, "station": {"code": "ST-north", "name": "Northgate Yard", "elevation_m": 210}}
        )
    assert (("station", "code"), "string_pattern_mismatch") in problems(exc_info)


def test_an_out_of_range_value_is_refused_by_the_annotated_constraint():
    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate({**VALID, "humidity_pct": 118})
    assert (("humidity_pct",), "less_than_equal") in problems(exc_info)


def test_a_date_in_the_wrong_format_is_refused():
    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate({**VALID, "recorded_at": "15/08/2026 10:00"})
    assert (("recorded_at",), "datetime_from_date_parsing") in problems(exc_info)


def test_a_naive_timestamp_is_refused_by_the_field_validator():
    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate({**VALID, "recorded_at": "2026-08-15T06:00:00"})
    # A validator that raises ValueError surfaces as value_error at that field.
    assert (("recorded_at",), "value_error") in problems(exc_info)


def test_the_cross_field_rule_puts_its_error_on_the_whole_record():
    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate({**VALID, "pm2_5": 612.5, "notes": None})
    assert ((), "value_error") in problems(exc_info)

    explained = {
        **VALID,
        "pm2_5": 548.9,
        "notes": "smoke plume from the north, confirmed by the duty log",
    }
    assert Reading.model_validate(explained).band == "hazardous"


def test_a_blank_note_is_normalised_to_none():
    assert Reading.model_validate({**VALID, "notes": "   "}).notes is None
    assert Reading.model_validate({**VALID, "notes": "  routine sweep  "}).notes == "routine sweep"


def test_one_call_reports_every_problem_at_once():
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
    found = problems(exc_info)
    assert (("station", "elevation_m"), "int_parsing") in found
    assert (("pm2_5",), "float_parsing") in found
    assert (("humidity_pct",), "int_type") in found
    assert len(exc_info.value.errors()) == 3


def test_every_error_entry_carries_loc_type_msg_and_input():
    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate({**VALID, "humidity_pct": 118})
    entry = exc_info.value.errors()[0]
    assert set(entry) >= {"loc", "type", "msg", "input"}
    assert entry["input"] == 118, "input echoes back what you actually sent"


# ---------------------------------------------------------------------------
# Coercion: lax versus strict
# ---------------------------------------------------------------------------


def test_lax_mode_coerces_numeric_strings():
    stringy = {
        **VALID,
        "station": {"code": "ST-KLM", "name": "  Kalmar Ridge  ", "elevation_m": "340"},
        "pm2_5": "14.8",
        "temperature_c": "19",
        "humidity_pct": "58",
    }
    reading = Reading.model_validate(stringy)
    assert reading.station.elevation_m == 340
    assert reading.station.name == "Kalmar Ridge", "str_strip_whitespace trims on the way in"
    assert reading.pm25 == pytest.approx(14.8)
    assert reading.temperature_c == pytest.approx(19.0)
    assert reading.humidity_pct == 58


def test_strict_mode_refuses_the_same_strings():
    stringy = {**VALID, "pm2_5": "14.8", "humidity_pct": "58"}
    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate(stringy, strict=True)
    found = problems(exc_info)
    assert (("pm2_5",), "float_type") in found
    assert (("humidity_pct",), "int_type") in found


@pytest.mark.parametrize(
    ("value", "target", "expected"),
    [
        ("42", int, 42),
        ("42.0", int, 42),
        ("  42  ", int, 42),
        (42.0, int, 42),
        (True, int, 1),
        (3, float, 3.0),
        ("true", bool, True),
        ((1, 2), list[int], [1, 2]),
    ],
)
def test_the_conversions_lax_mode_really_performs(value, target, expected):
    assert TypeAdapter(target).validate_python(value) == expected


@pytest.mark.parametrize(
    ("value", "target", "error_type"),
    [
        ("forty-two", int, "int_parsing"),
        (42.7, int, "int_from_float"),
        (42, str, "string_type"),
        ("[1, 2]", list[int], "list_type"),
    ],
)
def test_the_conversions_lax_mode_refuses(value, target, error_type):
    with pytest.raises(ValidationError) as exc_info:
        TypeAdapter(target).validate_python(value)
    assert exc_info.value.errors()[0]["type"] == error_type


def test_int_to_float_is_the_one_conversion_strict_mode_still_allows():
    assert TypeAdapter(float).validate_python(3, strict=True) == pytest.approx(3.0)
    with pytest.raises(ValidationError):
        TypeAdapter(int).validate_python("42", strict=True)


# ---------------------------------------------------------------------------
# Assignment, immutability, serialization
# ---------------------------------------------------------------------------


def test_validate_assignment_keeps_the_object_legal_after_construction():
    reading = Reading.model_validate(VALID)
    with pytest.raises(ValidationError) as exc_info:
        reading.humidity_pct = 500
    assert (("humidity_pct",), "less_than_equal") in problems(exc_info)
    assert reading.humidity_pct == 61, "the rejected assignment did not land"


def test_a_frozen_model_refuses_assignment_outright():
    station = Reading.model_validate(VALID).station
    with pytest.raises(ValidationError) as exc_info:
        station.elevation_m = 1
    # Observed in pydantic 2.13.4: a whole-model `frozen=True` reports
    # `frozen_instance`, not the per-field `frozen_field`. The distinction is
    # exactly the sort of thing that makes asserting on `msg` a losing game.
    assert (("elevation_m",), "frozen_instance") in problems(exc_info)


def test_the_round_trip_is_not_symmetric_and_here_is_exactly_why():
    reading = Reading.model_validate(VALID)
    dumped = reading.model_dump()
    assert "band" in dumped, "a computed field is serialised"

    with pytest.raises(ValidationError) as exc_info:
        Reading.model_validate(dumped)
    assert (("band",), "extra_forbidden") in problems(exc_info)

    trimmed = reading.model_dump(by_alias=True, exclude={"band"})
    assert Reading.model_validate(trimmed) == reading


def test_the_alias_decides_the_key_on_both_sides():
    reading = Reading.model_validate(VALID)
    assert "pm25" in reading.model_dump()
    assert "pm2_5" in reading.model_dump(by_alias=True)
    assert "pm2_5" in json.loads(reading.model_dump_json(by_alias=True))


def test_model_dump_json_turns_the_datetime_into_iso_8601_text():
    reading = Reading.model_validate(VALID)
    assert json.loads(reading.model_dump_json())["recorded_at"] == "2026-08-15T06:00:00Z"


def test_type_adapter_validates_a_list_and_names_the_failing_index():
    adapter = TypeAdapter(list[Reading])
    assert len(adapter.validate_python([VALID])) == 1
    with pytest.raises(ValidationError) as exc_info:
        adapter.validate_python([VALID, {"reading_id": "RD-0100"}])
    first_loc = tuple(exc_info.value.errors()[0]["loc"])
    assert first_loc[0] == 1, "loc leads with the index of the offending element"


# ---------------------------------------------------------------------------
# The from-scratch validator
# ---------------------------------------------------------------------------


def test_the_miniature_validator_collects_every_error_rather_than_the_first():
    broken = {
        "reading_id": "RD-0099",
        "station": {"code": "ST-QQQ", "name": "Quarry Head", "elevation_m": "high"},
        "recorded_at": "2026-08-15T13:00:00Z",
        "pm2_5": "unreadable",
        "temperature_c": 20.0,
        "humidity_pct": None,
        "operator": "A. Invented",
    }
    value, errors = mini_validate(ScratchReading, broken)
    assert value is None
    found = {(tuple(e["loc"]), e["type"]) for e in errors}
    assert (("station", "elevation_m"), "int_parsing") in found
    assert (("pm2_5",), "float_parsing") in found
    assert (("humidity_pct",), "int_type") in found
    assert len(errors) == 3


def test_the_miniature_validator_distinguishes_absent_from_null():
    base = {
        "reading_id": "RD-0042",
        "station": {"code": "ST-KLM", "name": "Kalmar Ridge", "elevation_m": 340},
        "recorded_at": "2026-08-15T06:00:00Z",
        "pm2_5": 12.4,
        "temperature_c": 18.2,
        "humidity_pct": 61,
        "operator": "R. Nayar",
    }
    # `operator` present and null: legal, it is nullable.
    value, errors = mini_validate(ScratchReading, {**base, "operator": None})
    assert errors == [] and value is not None and value.operator is None

    # `operator` absent: not legal, it has no default.
    missing = {k: v for k, v in base.items() if k != "operator"}
    _, errors = mini_validate(ScratchReading, missing)
    assert (("operator",), "missing") in {(tuple(e["loc"]), e["type"]) for e in errors}


def test_the_miniature_validator_refuses_a_bool_where_an_int_was_asked_for():
    # bool is a subclass of int in Python. A validator that forgets this lets a
    # checkbox arrive where a count was wanted.
    base = {
        "reading_id": "RD-0042",
        "station": {"code": "ST-KLM", "name": "Kalmar Ridge", "elevation_m": True},
        "recorded_at": "2026-08-15T06:00:00Z",
        "pm2_5": 12.4,
        "temperature_c": 18.2,
        "humidity_pct": 61,
        "operator": "R. Nayar",
    }
    _, errors = mini_validate(ScratchReading, base)
    assert (("station", "elevation_m"), "int_type") in {
        (tuple(e["loc"]), e["type"]) for e in errors
    }


def test_the_toy_accepts_records_pydantic_refuses_because_it_has_no_such_rules(records):
    # Record 4 is humidity 118, record 6 is a malformed station code. The toy
    # checks types and presence and nothing else, so both pass it.
    for index in (4, 6):
        value, errors = mini_validate(ScratchReading, records[index])
        assert errors == [] and value is not None
        with pytest.raises(ValidationError):
            Reading.model_validate(records[index])


# ---------------------------------------------------------------------------
# The gate
# ---------------------------------------------------------------------------


def test_the_gate_completes_the_batch_with_a_non_zero_reject_count(records, result):
    # This is the assertion the whole lab exists for: run_gate RETURNS on a
    # batch that is two-thirds bad. If a ValidationError escaped, this test
    # would error rather than fail, and the gate would not be a gate.
    assert result.seen == len(records) == 12
    assert result.rejected_count == 8
    assert result.accepted_count == 4
    assert result.accepted_count + result.rejected_count == result.seen


def test_every_problem_the_brief_planted_is_actually_caught(result):
    types = set(result.error_types())
    for expected in (
        "missing",  # a required field absent
        "float_parsing",  # a value that is genuinely not a number
        "less_than_equal",  # an out-of-range value
        "extra_forbidden",  # a misspelled field name
        "string_pattern_mismatch",  # a nested object with its own error
        "duplicate_id",  # a batch rule no schema can express
        "datetime_from_date_parsing",  # a date in the wrong format
        "value_error",  # the cross-field rule
    ):
        assert expected in types, f"expected a {expected} somewhere in the batch"


def test_a_number_arriving_as_a_string_is_accepted_by_coercion(result):
    accepted = {reading.reading_id: reading for reading in result.accepted}
    assert "RD-0002" in accepted, "the all-strings record should be coerced, not rejected"
    coerced = accepted["RD-0002"]
    assert coerced.pm25 == pytest.approx(14.8)
    assert coerced.humidity_pct == 58
    assert coerced.station.elevation_m == 340


def test_the_duplicate_is_the_second_occurrence_not_the_first(result):
    accepted_ids = [reading.reading_id for reading in result.accepted]
    assert accepted_ids.count("RD-0001") == 1, "the first RD-0001 was kept"
    duplicates = [
        rejection
        for rejection in result.rejected
        if any(error["type"] == "duplicate_id" for error in rejection.errors)
    ]
    assert len(duplicates) == 1
    assert duplicates[0].index == 7, "the later record is the one rejected"


def test_every_rejection_names_a_location_and_a_type(result):
    for rejection in result.rejected:
        assert rejection.errors, "a rejection with no reasons is useless"
        for error in rejection.errors:
            assert isinstance(error["type"], str) and error["type"]
            assert isinstance(error["loc"], list)


def test_the_report_is_json_serialisable_and_counts_add_up(result):
    report = result.as_report()
    text = json.dumps(report)  # must not raise: `input` was made JSON-friendly
    assert json.loads(text) == report
    assert report["records_seen"] == report["records_accepted"] + report["records_rejected"]
    assert len(report["rejections"]) == report["records_rejected"]


def test_write_outputs_emits_the_accepted_records_and_the_report(tmp_path, result):
    accepted_path, report_path = write_outputs(result, tmp_path)
    lines = accepted_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == result.accepted_count
    assert json.loads(lines[0])["reading_id"] == "RD-0001"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["records_rejected"] == result.rejected_count


def test_the_gate_can_fail_the_build_when_the_reject_rate_is_too_high(tmp_path):
    import gate

    ok = gate.main(
        ["--input", str(BATCH), "--out-dir", str(tmp_path / "a"), "--fail-over", "0.9"]
    )
    assert ok == 0, "a 67% reject rate is under a 90% threshold"
    bad = gate.main(
        ["--input", str(BATCH), "--out-dir", str(tmp_path / "b"), "--fail-over", "0.1"]
    )
    assert bad == 1, "a 67% reject rate is over a 10% threshold"


# ---------------------------------------------------------------------------
# The scripts run
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("script", ["coercion.py", "scratch_demo.py", "serialize.py"])
def test_each_demo_script_exits_zero(script):
    done = subprocess.run(
        [sys.executable, script],
        cwd=EXAMPLES,
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"},
    )
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip(), "a demo that prints nothing teaches nothing"
