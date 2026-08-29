"""Exercise 9 -- the whole harness on the worked study, and on a broken one.

A harness that has only ever passed is an untested harness. So this script
does two things.

First it runs all eight gates against the complete worked study and asserts a
clean verdict -- which is the day's claim that the arc holds together, made by
running it rather than by saying it.

Then it removes ONE required element from that same study -- the
`checksum_sha256` field in SOURCE.json, a single line -- and asserts the
harness catches it, names it, and fails exactly one gate. That is the proof
that matters: the harness can fail on a real study, not only on a fixture
built to fail.

Finally it removes three elements at once and confirms the verdict is a task
list rather than a first exception.

Run:  ../.venv/bin/python3 09_whole_harness.py
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import acceptance
import fixtures as fx


def remove_checksum(study_dir: Path) -> None:
    """Delete one required element from an otherwise complete study."""
    path = Path(study_dir) / "SOURCE.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    del payload["checksum_sha256"]
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def remove_three(study_dir: Path) -> None:
    fx.break_missing_question(study_dir)
    fx.break_grain(study_dir)
    fx.break_figure_label(study_dir, index=1, key="claim")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        good = fx.worked_study(root)

        verdict = acceptance.check_study(good)
        print(verdict.summary())
        print()
        assert verdict.ok, verdict.findings
        assert len(verdict.gates) == 8
        assert tuple(g.name for g in verdict.gates) == acceptance.GATE_NAMES
        assert verdict.findings == ()
        print(f"  all {len(verdict.gates)} gates pass on the worked study")

        # One required element removed from a real, complete study.
        broken = fx.variant(good, root / "one-element-removed", remove_checksum)
        verdict = acceptance.check_study(broken)
        print()
        print("The same study with SOURCE.json's checksum_sha256 deleted:")
        print(verdict.summary())
        assert not verdict.ok
        assert verdict.failed_gates == ("provenance_complete",), verdict.failed_gates
        assert verdict.findings == ("SOURCE.json is missing: checksum_sha256",)

        # Three at once: every gate still runs, and the verdict lists all of it.
        several = fx.variant(good, root / "three-elements-removed", remove_three)
        verdict = acceptance.check_study(several)
        print()
        print("Three elements removed at once -- the verdict is a task list:")
        for finding in verdict.findings:
            print(f"  - {finding}")
        assert set(verdict.failed_gates) == {
            "question_recorded",
            "grain_asserted",
            "figures_documented",
        }, verdict.failed_gates
        assert len(verdict.findings) == 4, verdict.findings

        # A directory that is not a study at all.
        empty = root / "empty"
        empty.mkdir()
        verdict = acceptance.check_study(empty)
        assert not verdict.ok
        assert len(verdict.failed_gates) == 8, verdict.failed_gates
        print()
        print(f"  an empty directory fails all {len(verdict.failed_gates)} gates")

        # And a path that does not exist raises rather than quietly passing.
        try:
            acceptance.check_study(root / "nowhere")
        except FileNotFoundError as exc:
            print(f"  a missing path raises FileNotFoundError: {str(exc)[:44]}...")
        else:  # pragma: no cover - only reached if the harness is wrong
            raise AssertionError("a missing study directory must raise")

    print()
    print("OK: eight gates pass on the worked study, one deleted field fails")
    print("    exactly one gate by name, and three failures come back as three.")


if __name__ == "__main__":
    main()
