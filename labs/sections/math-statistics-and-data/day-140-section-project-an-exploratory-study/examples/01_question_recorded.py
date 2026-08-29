"""Exercise 1 -- a question recorded before the analysis.

The first seam. A study whose question was written down after the looking is
not a study; it is a search for whichever question the data answers well, and
nothing downstream can tell the difference. The harness cannot prove the
ordering, so it insists on the weaker thing it CAN check: the question exists,
it is not empty, and it is actually a question.

Run:  ../.venv/bin/python3 01_question_recorded.py
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

        verdict = acceptance.check_study(good)
        gate = verdict.gate("question_recorded")
        print("The worked study's question file:")
        print((good / "QUESTION.md").read_text().rstrip())
        print()
        print(f"  gate question_recorded -> {'PASS' if gate.ok else 'FAIL'}")
        assert gate.ok, gate.findings

        print()
        print("Three ways the same gate fails, and what each finding says:")
        for label, mutator in (
            ("the file is missing", fx.break_missing_question),
            ("the file is empty", fx.break_empty_question),
            ("a topic, not a question", fx.break_question_without_a_question),
        ):
            broken = fx.variant(good, root / f"q-{label.replace(' ', '-')}", mutator)
            result = acceptance.check_study(broken).gate("question_recorded")
            assert not result.ok, f"{label} should have failed the gate"
            assert len(result.findings) == 1, result.findings
            finding = result.findings[0]
            assert finding.startswith("QUESTION.md"), finding
            print(f"  {label:26} -> {finding}")

        # The finding always names the file. That is the difference between a
        # verdict you can act on and one you have to investigate.
        for mutator in (fx.break_missing_question, fx.break_empty_question):
            broken = fx.variant(good, root / "named", mutator)
            names = acceptance.check_study(broken).gate("question_recorded").findings
            assert all("QUESTION.md" in f for f in names), names

    print()
    print("OK: the question gate passes a written question and fails a missing,")
    print("    empty, or question-free file, naming QUESTION.md every time.")


if __name__ == "__main__":
    main()
