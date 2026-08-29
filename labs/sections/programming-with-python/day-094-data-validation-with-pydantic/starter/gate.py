"""Exercises 7-10 — the data-quality gate.

The rule this file exists to enforce is simple to state and easy to get wrong:
**one bad record must not end the run.** A pipeline that raises on the first
malformed row processes nothing and tells you about one problem. A pipeline
with a gate processes everything it can and hands back a report naming every
record it refused and exactly why.

This file runs as it stands and tells you what is still missing:

    python3 starter/gate.py

The reference answer is in `examples/gate.py`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LAB_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = LAB_DIR / "data" / "raw-readings.json"


def load_records(path: Path = DEFAULT_INPUT) -> list[Any]:
    """Read the raw batch. Note what this does *not* do: it does not validate.

    This one is written for you, because reading a file is not the lesson.
    """
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array of records")
    return data


# ---------------------------------------------------------------------------
# Exercise 7 — the two result types.
#
# Define a frozen dataclass `Rejection` with fields:
#     index: int
#     reading_id: str | None
#     errors: list[dict[str, Any]]
# and a `summary()` method returning a one-line human string such as
#     "record 4 (RD-0005): humidity_pct [less_than_equal]"
#
# Define a dataclass `GateResult` with `accepted: list` and
# `rejected: list[Rejection]` (use field(default_factory=list)), plus
# properties `seen`, `accepted_count`, `rejected_count`, a method
# `error_types()` returning every error type across all rejections, and
# `as_report()` returning a JSON-serialisable dict with keys
# records_seen / records_accepted / records_rejected / rejections.
#
# Keep `loc`, `type`, `msg` and `input` for each error. Three of those four are
# machine-readable; `msg` is the one for humans, and the one nothing asserts on.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Exercise 8 — run_gate(records) -> GateResult.
#
# For each record, in order:
#     try:  reading = Reading.model_validate(raw)
#     except ValidationError as exc:  record a Rejection built from
#         exc.errors(), then `continue` — do NOT re-raise.
#
# The `except` is the entire exercise. Everything else is bookkeeping. If you
# find yourself letting the exception out "just for now", stop: that is the
# behaviour this file exists to prevent.
#
# Tip: pull the raw id with raw.get("reading_id") BEFORE validating, so a
# record that fails validation can still be named in the report.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Exercise 9 — the batch-level rule the schema cannot express.
#
# Inside run_gate, keep a dict of {reading_id: first_index_seen}. If a record
# validates but its id has already been used, reject it with a hand-made error
# entry of type "duplicate_id" and loc ["reading_id"].
#
# Uniqueness is a property of the BATCH, not of the record. No per-record
# schema can see it, which is why a gate is a place and not just a model.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Exercise 10 — write the two outputs.
#
# write_outputs(result, out_dir) should create out_dir if needed and write:
#   * accepted.jsonl — one `reading.model_dump_json()` per line
#   * rejects.json   — json.dumps(result.as_report(), indent=2)
# returning the two paths.
#
# Then make main() print the counts and one line per rejection, and support a
# `--fail-over FRACTION` flag that exits 1 when the reject rate is too high.
# A gate that never fails the build is a log line, not a gate.
# ---------------------------------------------------------------------------


def _unfinished() -> list[str]:
    return [
        name
        for name in ("Rejection", "GateResult", "run_gate", "write_outputs")
        if name not in globals()
    ]


def main() -> int:
    missing = _unfinished()
    records = load_records()
    print(f"loaded {len(records)} raw records from {DEFAULT_INPUT.name}")
    if missing:
        print(f"gate not built yet: {', '.join(missing)} not defined.")
        print("Start at exercise 7.")
        return 0
    result = run_gate(records)  # noqa: F821 - defined by exercise 8
    print(f"accepted {result.accepted_count}, rejected {result.rejected_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
