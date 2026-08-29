"""Exercise 6 -- uncertainty in the prose, not only in the notebook.

Days 117 and 118 built the interval. This exercise checks it survived the trip
into the report. It almost always does not: the analyst computes a 95% CI,
looks at it, decides the effect is real, and writes "roadside stations are
5.5 ug/m3 higher" -- which is a number wearing the costume of a fact.

The gate is a heuristic and says so out loud. A findings sentence carrying a
number AND an estimate word must also carry interval evidence: a CI, a
plus-or-minus, a bracketed range, a "x to y" or a "between x and y". It scans
the findings section only, because a methods paragraph mentioning a row count
is not a claim, and a checker that flags those trains you to ignore it.

Run:  ../.venv/bin/python3 06_uncertainty_in_the_prose.py
"""

from __future__ import annotations

import tempfile
import textwrap
from pathlib import Path

import acceptance
import fixtures as fx


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        good = fx.worked_study(root)

        block = acceptance.findings_section((good / "REPORT.md").read_text())
        print("The worked study's findings section:")
        for sentence in acceptance.sentences_of(block):
            print(textwrap.indent(textwrap.fill(sentence, 72), "  "))
            print()

        gate = acceptance.check_study(good).gate("uncertainty_reported")
        assert gate.ok, gate.findings
        print("  gate uncertainty_reported -> PASS")

        # Strip the interval; keep the point estimate.
        bare = fx.variant(good, root / "no-interval", fx.break_uncertainty)
        result = acceptance.check_study(bare).gate("uncertainty_reported")
        assert not result.ok
        print()
        print("The same finding with the interval removed:")
        for finding in result.findings:
            print(textwrap.indent(textwrap.fill(finding, 72), "  "))
        assert len(result.findings) == 1, result.findings
        assert "5.50 ug/m3 higher than park stations" in result.findings[0]

        # The gate names the SENTENCE, not the file. On a twelve-page report
        # that is the difference between a fix and a re-read.
        assert "estimate reported without an interval" in result.findings[0]

        # Which forms of interval evidence the gate accepts, checked one at a
        # time against the same sentence.
        print()
        print("Interval evidence the gate accepts, tested one form at a time:")
        forms = (
            "The mean difference was 5.50 ug/m3 (95% CI 3.80 to 7.21).",
            "The mean difference was 5.50 ug/m3, plus or minus 1.70 (±1.70).",
            "The mean difference was 5.50 ug/m3, interval [3.80, 7.21].",
            "The mean difference was anywhere between 3.80 and 7.21 ug/m3.",
            "The estimated mean difference was 3.80 to 7.21 ug/m3.",
        )
        for sentence in forms:
            def rewrite(study_dir: Path, s=sentence) -> None:
                path = Path(study_dir) / "REPORT.md"
                lines = path.read_text().splitlines()
                start = lines.index("## Findings")
                end = next(i for i in range(start + 1, len(lines))
                           if lines[i].startswith("## "))
                path.write_text(
                    "\n".join(lines[:start] + ["## Findings", "", s, ""] + lines[end:])
                    + "\n",
                    encoding="utf-8",
                )

            probe = fx.variant(good, root / "form", rewrite)
            ok = acceptance.check_study(probe).gate("uncertainty_reported").ok
            print(f"  {'accepted' if ok else 'REJECTED':9} {sentence}")
            assert ok, sentence

        # And a form it correctly rejects.
        def rewrite_bare(study_dir: Path) -> None:
            path = Path(study_dir) / "REPORT.md"
            lines = path.read_text().splitlines()
            start = lines.index("## Findings")
            end = next(i for i in range(start + 1, len(lines))
                       if lines[i].startswith("## "))
            path.write_text(
                "\n".join(
                    lines[:start]
                    + ["## Findings", "", "The mean difference was 5.50 ug/m3.", ""]
                    + lines[end:]
                )
                + "\n",
                encoding="utf-8",
            )

        probe = fx.variant(good, root / "bare-form", rewrite_bare)
        assert not acceptance.check_study(probe).gate("uncertainty_reported").ok
        print("  REJECTED  The mean difference was 5.50 ug/m3.")

    print()
    print("OK: the uncertainty gate accepts five forms of interval evidence, and")
    print("    names the exact sentence when an estimate stands without one.")


if __name__ == "__main__":
    main()
