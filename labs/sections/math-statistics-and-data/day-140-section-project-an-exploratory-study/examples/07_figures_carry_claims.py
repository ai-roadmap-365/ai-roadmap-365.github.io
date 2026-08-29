"""Exercise 7 -- every figure carries a question and a claim (Day 133).

Day 133's rule, mechanised. A figure exists to answer a question and to
support a claim. A figure with neither is decoration, and decoration in a
report is where a reader's attention goes to die -- worse, it is where a
reader's TRUST goes, because a chart that says nothing still looks like
evidence.

The gate checks both directions, which matters more than it sounds:

  * every documented figure has a file that exists, a question and a claim;
  * every figure file on disk is documented.

The second catches the chart that survived three drafts because nobody
remembered what it was for.

Run:  ../.venv/bin/python3 07_figures_carry_claims.py
"""

from __future__ import annotations

import json
import tempfile
import textwrap
from pathlib import Path

import acceptance
import fixtures as fx


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        good = fx.worked_study(root)

        records = json.loads((good / "FIGURES.json").read_text())
        print("The worked study's figure records:")
        for record in records:
            print(f"  {record['file']}")
            print(f"    chart:    {record['chart']}")
            print(f"    baseline: {record['baseline']}")
            print(textwrap.indent(textwrap.fill(f"question: {record['question']}", 68), "    "))
            print(textwrap.indent(textwrap.fill(f"claim:    {record['claim']}", 68), "    "))
            print()
            assert (good / record["file"]).is_file()

        gate = acceptance.check_study(good).gate("figures_documented")
        assert gate.ok, gate.findings
        print("  gate figures_documented -> PASS (two figures, both documented)")

        # A figure with no claim.
        for key in ("claim", "question"):
            broken = fx.variant(
                good,
                root / f"no-{key}",
                lambda d, k=key: fx.break_figure_label(d, index=0, key=k),
            )
            findings = acceptance.check_study(broken).gate("figures_documented").findings
            assert len(findings) == 1, findings
            assert findings[0].endswith(f"carries no {key}"), findings
            assert "fig-01-pm25-by-station-type.png" in findings[0]
            print(f"  remove {key:8} -> {findings[0]}")

        # A figure file nobody documented.
        stray = fx.variant(good, root / "stray-figure", fx.break_figure_undocumented)
        findings = acceptance.check_study(stray).gate("figures_documented").findings
        assert len(findings) == 1, findings
        assert "fig-99-leftover.png" in findings[0] and "undocumented" in findings[0]
        print(f"  stray file      -> {findings[0]}")

        # A record pointing at a figure that was never rendered.
        def dangling(study_dir: Path) -> None:
            path = Path(study_dir) / "FIGURES.json"
            payload = json.loads(path.read_text())
            payload[1]["file"] = "figures/fig-03-never-rendered.png"
            path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
            (Path(study_dir) / "figures" / "fig-02-pm25-distribution.png").unlink()

        missing = fx.variant(good, root / "dangling", dangling)
        findings = acceptance.check_study(missing).gate("figures_documented").findings
        assert any("does not exist" in f for f in findings), findings
        print(f"  dangling record -> {findings[0]}")

    print()
    print("OK: the figures gate passes documented figures and fails an entry with")
    print("    no question or claim, a stray file, and a record with no file.")


if __name__ == "__main__":
    main()
