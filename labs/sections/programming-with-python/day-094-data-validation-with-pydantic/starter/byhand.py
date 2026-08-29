"""The "before" picture: boundary validation written entirely by hand.

Nothing in this file is broken. It runs, it is correct as far as it goes, and
it is roughly what every codebase grows before somebody reaches for a library.
Read it once and count the things it does not check — that count is the point.

Run it to see it work:

    python3 starter/byhand.py

All names, station codes and operator initials in the sample data are invented
for this lab. No real monitoring network, person or measurement is involved.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LAB_DIR = Path(__file__).resolve().parent.parent
BATCH = LAB_DIR / "data" / "raw-readings.json"


def validate_reading_by_hand(raw: Any) -> tuple[dict[str, Any] | None, list[str]]:
    """Check one record. Returns ``(clean_record, problems)``.

    Notice the shape of the code, not the detail: one ``if`` per field per rule,
    every message written out longhand, and the rules living nowhere except
    inside this function. Add a field and you edit here. Add a caller and you
    hope they remember to call this. Change a rule and you grep.
    """
    problems: list[str] = []

    if not isinstance(raw, dict):
        return None, ["record is not an object"]

    clean: dict[str, Any] = {}

    reading_id = raw.get("reading_id")
    if reading_id is None:
        problems.append("reading_id is missing")
    elif not isinstance(reading_id, str):
        problems.append("reading_id is not a string")
    else:
        clean["reading_id"] = reading_id

    station = raw.get("station")
    if station is None:
        problems.append("station is missing")
    elif not isinstance(station, dict):
        problems.append("station is not an object")
    else:
        code = station.get("code")
        if not isinstance(code, str):
            problems.append("station.code is missing or not a string")
        else:
            clean["station_code"] = code

    pm = raw.get("pm2_5")
    if pm is None:
        problems.append("pm2_5 is missing")
    else:
        try:
            clean["pm25"] = float(pm)
        except (TypeError, ValueError):
            problems.append("pm2_5 is not a number")

    humidity = raw.get("humidity_pct")
    if humidity is None:
        problems.append("humidity_pct is missing")
    else:
        try:
            clean["humidity_pct"] = int(humidity)
        except (TypeError, ValueError):
            problems.append("humidity_pct is not a whole number")

    if problems:
        return None, problems
    return clean, []


def main() -> int:
    with BATCH.open(encoding="utf-8") as handle:
        records = json.load(handle)

    accepted = 0
    rejected = 0
    for index, raw in enumerate(records):
        clean, problems = validate_reading_by_hand(raw)
        if problems:
            rejected += 1
            print(f"  record {index}: " + "; ".join(problems))
        else:
            accepted += 1

    print()
    print(f"by hand: accepted {accepted}, rejected {rejected} of {len(records)}")
    print()
    print("Four fields checked out of eight, no ranges, no patterns, no dates, no")
    print("nesting past one level, no cross-field rules, and the error messages are")
    print("prose a machine cannot act on. Every one of those is an exercise below.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
