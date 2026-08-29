"""The data-quality gate: validate a whole batch, keep the good, report the bad.

The rule this module exists to enforce is simple to state and easy to get
wrong: **one bad record must not end the run.** A pipeline that raises on the
first malformed row processes nothing and tells you about one problem. A
pipeline with a gate processes everything it can, and hands back a report
naming every record it refused and exactly why.

Run it directly:

    python3 examples/gate.py
    python3 examples/gate.py --input data/raw-readings.json --out-dir out
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from models import Reading

LAB_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = LAB_DIR / "data" / "raw-readings.json"
DEFAULT_OUT_DIR = LAB_DIR / "out"


@dataclass(frozen=True)
class Rejection:
    """One record the gate refused, and every reason it refused it."""

    index: int
    reading_id: str | None
    errors: list[dict[str, Any]]

    def summary(self) -> str:
        parts = []
        for error in self.errors:
            where = ".".join(str(part) for part in error["loc"]) or "<record>"
            parts.append(f"{where} [{error['type']}]")
        label = self.reading_id or "<no id>"
        return f"record {self.index} ({label}): " + "; ".join(parts)


@dataclass
class GateResult:
    """What came out of the gate."""

    accepted: list[Reading] = field(default_factory=list)
    rejected: list[Rejection] = field(default_factory=list)

    @property
    def seen(self) -> int:
        return len(self.accepted) + len(self.rejected)

    @property
    def accepted_count(self) -> int:
        return len(self.accepted)

    @property
    def rejected_count(self) -> int:
        return len(self.rejected)

    def error_types(self) -> list[str]:
        return [error["type"] for rejection in self.rejected for error in rejection.errors]

    def as_report(self) -> dict[str, Any]:
        """A machine-readable report. Whoever owns the source data reads this."""
        return {
            "records_seen": self.seen,
            "records_accepted": self.accepted_count,
            "records_rejected": self.rejected_count,
            "rejections": [
                {
                    "index": rejection.index,
                    "reading_id": rejection.reading_id,
                    "errors": rejection.errors,
                }
                for rejection in self.rejected
            ],
        }


def _tidy(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep the four fields that matter and make ``loc`` JSON-friendly.

    ``msg`` is kept because a human has to read the report. It is deliberately
    the only one of the four that no test in this lab asserts on.
    """
    tidy = []
    for error in errors:
        tidy.append(
            {
                "loc": list(error["loc"]),
                "type": error["type"],
                "msg": error["msg"],
                "input": _jsonable(error.get("input")),
            }
        )
    return tidy


def _jsonable(value: Any) -> Any:
    try:
        json.dumps(value)
    except (TypeError, ValueError):
        return repr(value)
    return value


def load_records(path: Path = DEFAULT_INPUT) -> list[Any]:
    """Read the raw batch. Note what this does *not* do: it does not validate."""
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array of records")
    return data


def run_gate(records: list[Any]) -> GateResult:
    """Validate every record. Never raises for bad data — that is the whole point."""
    result = GateResult()
    seen_ids: dict[str, int] = {}

    for index, raw in enumerate(records):
        raw_id = raw.get("reading_id") if isinstance(raw, dict) else None
        label = raw_id if isinstance(raw_id, str) else None

        try:
            reading = Reading.model_validate(raw)
        except ValidationError as exc:
            result.rejected.append(
                Rejection(index=index, reading_id=label, errors=_tidy(exc.errors()))
            )
            continue

        # A batch-level rule. No per-record schema can express it, because
        # uniqueness is a property of the batch, not of the record.
        first_seen = seen_ids.get(reading.reading_id)
        if first_seen is not None:
            result.rejected.append(
                Rejection(
                    index=index,
                    reading_id=reading.reading_id,
                    errors=[
                        {
                            "loc": ["reading_id"],
                            "type": "duplicate_id",
                            "msg": f"reading_id already used by record {first_seen}",
                            "input": reading.reading_id,
                        }
                    ],
                )
            )
            continue

        seen_ids[reading.reading_id] = index
        result.accepted.append(reading)

    return result


def write_outputs(result: GateResult, out_dir: Path = DEFAULT_OUT_DIR) -> tuple[Path, Path]:
    """Emit the accepted records and the rejection report as two files."""
    out_dir.mkdir(parents=True, exist_ok=True)
    accepted_path = out_dir / "accepted.jsonl"
    report_path = out_dir / "rejects.json"

    with accepted_path.open("w", encoding="utf-8") as handle:
        for reading in result.accepted:
            handle.write(reading.model_dump_json() + "\n")

    report_path.write_text(
        json.dumps(result.as_report(), indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return accepted_path, report_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a batch of sensor readings.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument(
        "--fail-over",
        type=float,
        default=None,
        metavar="FRACTION",
        help="exit non-zero if more than this fraction of records were rejected",
    )
    args = parser.parse_args(argv)

    records = load_records(args.input)
    result = run_gate(records)
    accepted_path, report_path = write_outputs(result, args.out_dir)

    print(f"read      {result.seen} records from {args.input.name}")
    print(f"accepted  {result.accepted_count}")
    print(f"rejected  {result.rejected_count}")
    print()
    for rejection in result.rejected:
        print("  " + rejection.summary())
    print()
    try:
        shown = args.out_dir.resolve().relative_to(LAB_DIR)
    except ValueError:
        shown = args.out_dir
    print(f"wrote {accepted_path.name} and {report_path.name} to {shown}/")

    if args.fail_over is not None and result.seen:
        share = result.rejected_count / result.seen
        if share > args.fail_over:
            print(
                f"\nreject rate {share:.1%} exceeds the {args.fail_over:.0%} threshold",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
