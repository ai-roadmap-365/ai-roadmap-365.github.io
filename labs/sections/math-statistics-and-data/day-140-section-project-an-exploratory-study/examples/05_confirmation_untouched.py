"""Exercise 5 -- was the confirmation set actually untouched?

This is the hardest seam in the whole arc, because it leaves no trace in the
finished report. A study that peeked at its held-out half during exploration
and a study that did not produce IDENTICAL-looking reports: same interval,
same p-value, same figures. The only difference is the ORDER things happened
in, and the only record of order is the research log.

So the gate reads the log as a sequence and asks one question: does the first
use of the confirmation split come after the entry where the hypothesis was
declared? If it does not, the confirmation half was part of the exploration
and its p-value means nothing.

Run:  ../.venv/bin/python3 05_confirmation_untouched.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import acceptance
import fixtures as fx


def show(rows) -> None:
    print(f"  {'seq':>3}  {'split':<12} {'activity'}")
    for row in rows:
        print(f"  {row['seq']:>3}  {row['split']:<12} {row['activity']}")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        good = fx.worked_study(root)

        rows = acceptance.research_log_rows((good / "RESEARCH_LOG.md").read_text())
        print("The worked study's research log, in order:")
        show(rows)
        print()

        splits = [row["split"] for row in rows]
        hypothesis_at = splits.index("none")
        confirmation_at = splits.index("confirmation")
        print(f"  hypothesis declared at entry {hypothesis_at + 1}")
        print(f"  confirmation split first used at entry {confirmation_at + 1}")
        assert confirmation_at > hypothesis_at
        assert splits.count("confirmation") == 1
        assert splits.count("exploration") == 4

        gate = acceptance.check_study(good).gate("confirmation_untouched")
        assert gate.ok, gate.findings
        print("  gate confirmation_untouched -> PASS")

        # The same study, same numbers, same figures -- but the log shows the
        # held-out half was opened at entry 2, before any hypothesis existed.
        peeked = fx.variant(good, root / "peeked", fx.break_confirmation_peeked)
        print()
        print("A study whose log shows the held-out half was opened early:")
        show(acceptance.research_log_rows((peeked / "RESEARCH_LOG.md").read_text()))
        result = acceptance.check_study(peeked).gate("confirmation_untouched")
        assert not result.ok
        print()
        for finding in result.findings:
            print(f"  {finding}")
        assert any("before the hypothesis was declared" in f for f in result.findings)
        assert any("used 2 times" in f for f in result.findings)

        # Note what did NOT change. The report, the figures and the interval
        # are byte-identical between the two studies. The peek is invisible
        # everywhere except the log.
        for name in ("REPORT.md", "FIGURES.json"):
            assert (good / name).read_bytes() == (peeked / name).read_bytes(), name
        print()
        print("  REPORT.md and FIGURES.json are byte-identical in both studies:")
        print("  the peek is visible in the log and nowhere else.")

        # A log with no confirmation entry at all fails differently, and
        # should: nothing was confirmed.
        def strip_confirmation(study_dir: Path) -> None:
            path = Path(study_dir) / "RESEARCH_LOG.md"
            kept = [
                line
                for line in path.read_text().splitlines()
                if "| confirmation |" not in line
            ]
            path.write_text("\n".join(kept) + "\n", encoding="utf-8")

        never = fx.variant(good, root / "never-confirmed", strip_confirmation)
        findings = acceptance.check_study(never).gate("confirmation_untouched").findings
        print()
        print("A log that never uses the confirmation split at all:")
        print(f"  {findings[0]}")
        assert "never used" in findings[0], findings

    print()
    print("OK: the confirmation gate reads the log's ordering, catches a split")
    print("    used before the hypothesis existed, and catches one never used.")


if __name__ == "__main__":
    main()
