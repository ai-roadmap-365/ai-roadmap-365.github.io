#!/usr/bin/env python3
"""Why the JSON state file stops being enough — measured, not asserted.

Week 12's toolkit kept its state in one JSON file, written atomically. That
was the right call then. This script shows, with real numbers on your own
machine, the four places it stops paying:

  1. A one-field change rewrites the whole file.
  2. Nothing stops a typo'd member id from being stored.
  3. Two writers who read, then write, silently lose one of the two updates.
  4. "Which loans are overdue?" costs a full load and a full scan.

Run it:  python3 json_pain.py

It writes and deletes files inside a temporary directory of its own and
leaves nothing behind.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

TODAY = "2026-08-16"  # written down, not looked up — see seed.sql


def make_loans(count: int) -> list[dict[str, object]]:
    """A loan list shaped exactly like the loans table, as plain dicts."""
    loans: list[dict[str, object]] = []
    for index in range(1, count + 1):
        loans.append(
            {
                "loan_id": index,
                "book_id": (index % 6) + 1,
                "member_id": (index % 4) + 1,
                "borrowed_on": "2026-06-01",
                "due_on": "2026-06-22",
                "returned_on": None if index % 3 else "2026-06-20",
            }
        )
    return loans


def atomic_write(path: Path, payload: str) -> int:
    """The Day 84 atomic write, unchanged. Returns bytes written."""
    encoded = payload.encode("utf-8")
    handle = tempfile.NamedTemporaryFile(
        dir=str(path.parent), delete=False, mode="wb", suffix=".tmp"
    )
    try:
        with handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(handle.name, path)
    except BaseException:
        Path(handle.name).unlink(missing_ok=True)
        raise
    return len(encoded)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="day085-json-") as tmp:
        root = Path(tmp)
        path = root / "loans.json"

        # ---------------------------------------------------------------
        print("1. A one-field change rewrites the whole file")
        for count in (10, 1_000, 50_000):
            loans = make_loans(count)
            payload = json.dumps({"loans": loans}, indent=2)
            written = atomic_write(path, payload)

            # Mark loan 1 as returned. One field. One row.
            loaded = json.loads(path.read_text(encoding="utf-8"))
            loaded["loans"][0]["returned_on"] = TODAY
            rewritten = atomic_write(
                path, json.dumps(loaded, indent=2)
            )
            changed_field = len(f'"returned_on": "{TODAY}"')
            print(
                f"   {count:>6,} loans: file {rewritten:>9,} bytes"
                f" | changed {changed_field:>3} bytes"
                f" | read+wrote {written + rewritten:>10,} bytes to do it"
            )
        print(
            "   The database rewrites the page that holds the row"
            " (4096 bytes here), not the file."
        )

        # ---------------------------------------------------------------
        print()
        print("2. Nothing stops a member id that does not exist")
        loans = make_loans(5)
        loans.append(
            {
                "loan_id": 6,
                "book_id": 3,
                "member_id": 999,  # there is no member 999
                "borrowed_on": "2026-08-01",
                "due_on": "2026-08-22",
                "returned_on": None,
            }
        )
        atomic_write(path, json.dumps({"loans": loans}, indent=2))
        stored = json.loads(path.read_text(encoding="utf-8"))["loans"][-1]
        print(f"   stored happily: member_id={stored['member_id']}")
        print("   json.dump has no opinion about what a member id means.")

        # ---------------------------------------------------------------
        print()
        print("3. Two writers, one lost update")
        atomic_write(path, json.dumps({"loans": make_loans(3)}, indent=2))
        # Writer A reads the whole file.
        writer_a = json.loads(path.read_text(encoding="utf-8"))
        # Writer B reads the same whole file, a millisecond later.
        writer_b = json.loads(path.read_text(encoding="utf-8"))
        # A returns loan 1. B adds loan 4. Both write the whole file back.
        writer_a["loans"][0]["returned_on"] = TODAY
        atomic_write(path, json.dumps(writer_a, indent=2))
        writer_b["loans"].append(
            {
                "loan_id": 4,
                "book_id": 1,
                "member_id": 2,
                "borrowed_on": TODAY,
                "due_on": "2026-09-06",
                "returned_on": None,
            }
        )
        atomic_write(path, json.dumps(writer_b, indent=2))
        final = json.loads(path.read_text(encoding="utf-8"))["loans"]
        print(f"   loans in the file afterwards: {len(final)}")
        print(f"   loan 1 returned_on: {final[0]['returned_on']!r}")
        print(
            "   Both writes 'succeeded' atomically. A's update is gone anyway:"
        )
        print(
            "   atomicity protects the FILE, not the two readers who raced"
            " over it."
        )

        # ---------------------------------------------------------------
        print()
        print("4. 'Which loans are overdue?' costs a full load and a full scan")
        loans = make_loans(50_000)
        atomic_write(path, json.dumps({"loans": loans}, indent=2))
        size = path.stat().st_size
        loaded = json.loads(path.read_text(encoding="utf-8"))["loans"]
        overdue = [
            row
            for row in loaded
            if row["returned_on"] is None and row["due_on"] < TODAY
        ]
        print(f"   parsed {size:,} bytes and examined {len(loaded):,} records")
        print(f"   to answer a question with {len(overdue):,} rows in it")
        print(
            "   There is no cheaper path. The file has no index, because a"
            " file has no idea what a due date is."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
