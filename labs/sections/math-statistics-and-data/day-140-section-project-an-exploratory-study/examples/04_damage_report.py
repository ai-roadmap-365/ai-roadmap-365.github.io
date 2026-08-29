"""Exercise 4 -- a damage report, not a changelog.

The distinction this exercise exists for:

    changelog     "dropped the fault-sentinel readings"
    damage report "rows carrying the -1.0 fault sentinel: before 6, after 0"

The first tells you what somebody did. The second tells you what it cost, and
only the second lets a reader decide whether the cleaning was proportionate.
Every number the study reports downstream was computed after these steps ran,
so a reader who cannot see the damage cannot audit anything that follows.

Run:  ../.venv/bin/python3 04_damage_report.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import acceptance
import fixtures as fx


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        good = fx.worked_study(root)

        text = (good / "CLEANING.md").read_text()
        steps = acceptance.cleaning_steps(text)
        print("The worked study's damage report, step by step:")
        print(f"  {'step':44} {'before':>8} {'after':>8} {'changed':>8}")
        for title, values in steps:
            print(f"  {title:44} {values['before']:8.0f} {values['after']:8.0f} "
                  f"{values['before'] - values['after']:8.0f}")
        print()

        assert len(steps) == 4, steps
        by_name = dict(steps)
        assert by_name["normalise station_type casing"] == {"before": 8.0, "after": 2.0}
        assert by_name["drop duplicate reading_id rows"] == {"before": 264.0, "after": 256.0}
        assert by_name["drop sensor fault sentinel readings"] == {"before": 6.0, "after": 0.0}
        assert by_name["drop rows with no pm25 reading"] == {"before": 5.0, "after": 0.0}

        gate = acceptance.check_study(good).gate("damage_report_quantified")
        assert gate.ok, gate.findings
        print("  gate damage_report_quantified -> PASS (four steps, all measured)")

        # Now turn ONE step back into a changelog entry and watch the gate
        # name that step specifically.
        broken = fx.variant(good, root / "changelog", fx.break_damage_report)
        result = acceptance.check_study(broken).gate("damage_report_quantified")
        assert not result.ok
        assert len(result.findings) == 1, result.findings
        print()
        print("With one step documented but not measured:")
        print(f"  {result.findings[0]}")
        assert fx.CHANGELOG_STEP in result.findings[0]
        assert "changelog entry, not a damage report" in result.findings[0]

        # The other three steps still pass: the gate is per-step, so a study
        # with one lapse gets one task, not a blanket rejection.
        still_measured = acceptance.cleaning_steps((broken / "CLEANING.md").read_text())
        measured = [t for t, v in still_measured if "before" in v and "after" in v]
        print(f"  steps still carrying measurements: {len(measured)} of {len(still_measured)}")
        assert len(measured) == 3, measured

    print()
    print("OK: the damage-report gate accepts four measured steps and rejects the")
    print("    one step reduced to a changelog entry, naming that step.")


if __name__ == "__main__":
    main()
