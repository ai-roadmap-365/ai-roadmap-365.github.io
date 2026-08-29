"""Exercise 3 -- the ingestion states a grain, and checks it.

"One row is one ___." Day 135's sentence, and the one every count downstream
silently depends on. The worked study's raw delivery VIOLATES its grain --
eight readings arrive twice, byte-identical -- and the record says so, names
the cleaning step that resolved it, and records the verified result for the
frame the study actually proceeds with.

That honesty is the point. A study that quietly de-duplicates and reports a
clean grain has hidden the most consequential thing that happened to its data.

Run:  ../.venv/bin/python3 03_grain_asserted.py
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import acceptance
import fixtures as fx
import study


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        good = fx.worked_study(root)

        record = json.loads((good / "INGEST.json").read_text())
        print("The worked study's ingestion contract:")
        print(f"  grain                       {record['grain']}")
        print(f"  grain_statement             {record['grain_statement']}")
        print(f"  grain_violations_on_arrival {record['grain_violations_on_arrival']}")
        print(f"  resolved_by                 {record['resolved_by']}")
        print(f"  grain_verified              {record['grain_verified']}")
        print(f"  rows_in / rows_out          {record['rows_in']} / {record['rows_out']}")
        print()

        assert record["grain"] == ["reading_id"]
        assert record["grain_violations_on_arrival"] == 8, record
        assert record["grain_verified"] is True
        assert record["rows_in"] - record["rows_out"] == 19, record

        gate = acceptance.check_study(good).gate("grain_asserted")
        assert gate.ok, gate.findings
        print("  gate grain_asserted -> PASS (a grain, stated and checked)")

        # An ingestion that never says what a row is.
        silent = fx.variant(good, root / "no-grain", fx.break_grain)
        findings = acceptance.check_study(silent).gate("grain_asserted").findings
        print()
        print("An ingestion with no grain declared at all:")
        for finding in findings:
            print(f"  {finding}")
        assert any("declares no row grain" in f for f in findings), findings

        # A grain declared and never checked. This is the subtler failure and
        # by far the commoner one: the schema says unique, nobody ran the test.
        hoped = fx.variant(good, root / "unverified-grain", fx.break_grain_unverified)
        findings = acceptance.check_study(hoped).gate("grain_asserted").findings
        print()
        print("A grain declared but never verified:")
        for finding in findings:
            print(f"  {finding}")
        assert len(findings) == 1 and "never checked against the data" in findings[0], findings

        # The check itself is real: re-run it against the raw frame and the
        # cleaned frame and confirm the two answers differ as recorded.
        raw = study.ds.load_source_csv(good / "data" / "observations.csv")
        on_arrival = study.ingest(raw)
        cleaned, _ = study.clean(on_arrival.frame)
        after = study.ingest(cleaned)
        print()
        print("Re-running the grain check directly, outside the harness:")
        print(f"  on arrival: verified={on_arrival.grain_verified} "
              f"violations={on_arrival.grain_violations}")
        print(f"  after cleaning: verified={after.grain_verified} "
              f"violations={after.grain_violations}")
        assert on_arrival.grain_verified is False and on_arrival.grain_violations == 8
        assert after.grain_verified is True and after.grain_violations == 0

    print()
    print("OK: the grain gate passes a stated-and-checked grain, and fails both")
    print("    a missing grain and one declared without a verification result.")


if __name__ == "__main__":
    main()
