"""Run the miniature validator over the real batch, then compare it to pydantic.

The from-scratch validator in ``scratch_validator.py`` is about two hundred
lines and does five things: it finds the fields, it decides what "present"
means, it applies a small coercion policy, it recurses into nested models, and
it collects **every** error instead of raising on the first. That last one is
the part that looks easy and is not.

What this script exists to show is the gap. The toy and ``models.py`` describe
the same twelve records. The toy waves through nine of them; the pydantic
schema keeps five. (The gate in ``gate.py`` then drops one more, because a
duplicate id is a property of the batch and no per-record schema can see it.)
The difference is not that pydantic is stricter by temperament — it is that
ranges, patterns, timestamps, aliases and cross-field rules are things the toy
has no vocabulary for, and each one would have to be hand-written per field.
That is what "hand-written validation rots" means in practice.

Run it directly:

    python3 examples/scratch_demo.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models import Reading
from pydantic import ValidationError
from scratch_models import ScratchReading
from scratch_validator import ValidationReport, format_report, validate

LAB_DIR = Path(__file__).resolve().parent.parent
BATCH = LAB_DIR / "data" / "raw-readings.json"


def load() -> list[Any]:
    with BATCH.open(encoding="utf-8") as handle:
        return json.load(handle)


def scratch_pass(records: list[Any]) -> tuple[int, list[tuple[int, list[dict[str, Any]]]]]:
    """Validate the batch with the hand-rolled validator. Returns (accepted, rejected)."""
    accepted = 0
    rejected: list[tuple[int, list[dict[str, Any]]]] = []
    for index, raw in enumerate(records):
        value, errors = validate(ScratchReading, raw)
        if errors:
            rejected.append((index, errors))
        else:
            accepted += 1
    return accepted, rejected


def pydantic_pass(records: list[Any]) -> tuple[int, list[tuple[int, list[dict[str, Any]]]]]:
    """The same batch through ``Reading``. Note it never raises out of this loop."""
    accepted = 0
    rejected: list[tuple[int, list[dict[str, Any]]]] = []
    for index, raw in enumerate(records):
        try:
            Reading.model_validate(raw)
        except ValidationError as exc:
            rejected.append((index, exc.errors()))
        else:
            accepted += 1
    return accepted, rejected


def _locs(errors: list[dict[str, Any]]) -> str:
    return ", ".join(
        f"{'.'.join(str(p) for p in error['loc']) or '<record>'} [{error['type']}]"
        for error in errors
    )


def main() -> int:
    records = load()

    print("=" * 74)
    print("1. One record, many problems at once")
    print("=" * 74)
    print()
    print("A validator that raises on the first bad field makes you fix a file one")
    print("round trip at a time. Both of these report everything they found.")
    print()

    # Deliberately broken in four separate ways, so the collecting behaviour is
    # visible rather than asserted. Every value here is invented for this lab.
    broken = {
        "reading_id": "RD-0099",
        "station": {"code": "ST-QQQ", "name": "Quarry Head", "elevation_m": "high"},
        "recorded_at": "2026-08-15T13:00:00Z",
        "pm2_5": "unreadable",
        "temperature_c": 20.0,
        "humidity_pct": None,
        "operator": "A. Invented",
    }

    _, scratch_errors = validate(ScratchReading, broken)
    print("from scratch:")
    print(format_report(scratch_errors))
    print()

    try:
        Reading.model_validate(broken)
    except ValidationError as exc:
        pydantic_errors = exc.errors()
    else:  # pragma: no cover - the record above cannot validate
        pydantic_errors = []
    print(f"pydantic: {len(pydantic_errors)} validation error(s)")
    for error in pydantic_errors:
        where = ".".join(str(part) for part in error["loc"]) or "<record>"
        print(f"  {where}")
        print(f"    type={error['type']} input={error['input']!r}")
    print()

    report = ValidationReport(scratch_errors)
    print(f"the toy's report answers questions: {len(report)} errors, types {report.types()}")
    print()

    print("=" * 74)
    print("2. The same twelve records through both")
    print("=" * 74)
    print()

    scratch_ok, scratch_bad = scratch_pass(records)
    pyd_ok, pyd_bad = pydantic_pass(records)

    print(f"from scratch : accepted {scratch_ok}, rejected {len(scratch_bad)}")
    for index, errors in scratch_bad:
        print(f"    record {index}: {_locs(errors)}")
    print()
    print(f"pydantic     : accepted {pyd_ok}, rejected {len(pyd_bad)}")
    for index, errors in pyd_bad:
        print(f"    record {index}: {_locs(errors)}")
    print()

    print("=" * 74)
    print("3. What the toy let through, and why")
    print("=" * 74)
    print()
    scratch_rejected = {index for index, _ in scratch_bad}
    for index, errors in pyd_bad:
        if index in scratch_rejected:
            continue
        reasons = ", ".join(sorted({error["type"] for error in errors}))
        print(f"  record {index}: pydantic says {reasons}; the toy has no rule for it")
    print()
    print("None of those are exotic. They are a range, a pattern, a date format and")
    print("a rule that spans two fields — and each one is a function the toy would")
    print("need hand-written, per field, and kept correct forever.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
