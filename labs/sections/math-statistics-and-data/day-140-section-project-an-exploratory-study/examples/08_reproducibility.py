"""Exercise 8 -- the study regenerates byte for byte, and the harness notices
when it does not.

Two separate claims, and they need separate evidence.

The first is about the worked study: built twice, into two different
directories, it produces identical bytes -- every Markdown file, every JSON
record, and both PNG figures. That is not luck. It is the direct consequence
of four decisions in `study.py`: the as-of date is a parameter rather than a
clock reading, the split is a seeded permutation, the report is wrapped by
`textwrap.fill` rather than by hand, and the figures are saved with their
PNG `Software` metadata suppressed. Remove any one of them and this exercise
fails.

The second is about the harness: given a study whose outputs have moved since
its manifest was written, it says so and names the file.

Run:  ../.venv/bin/python3 08_reproducibility.py
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import acceptance
import fixtures as fx
import study


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        first = root / "run-1"
        second = root / "run-2"
        summary_a = study.build_study(first)
        summary_b = study.build_study(second)

        assert summary_a == summary_b, "two runs measured different numbers"

        markdown = sorted(p.name for p in first.glob("*.md"))
        print("Two independent builds, Markdown compared byte for byte:")
        for name in markdown:
            a, b = digest(first / name), digest(second / name)
            print(f"  {name:20} {a[:16]}  {'identical' if a == b else 'DIFFERENT'}")
            assert a == b, name
        assert markdown == ["CLEANING.md", "QUESTION.md", "REPORT.md", "RESEARCH_LOG.md"]

        print()
        print("And every other generated file, including the figures:")
        for rel in study.manifest_targets(first) + [study.MANIFEST_NAME]:
            a, b = digest(first / rel), digest(second / rel)
            status = "identical" if a == b else "DIFFERENT"
            print(f"  {rel:44} {status}")
            assert a == b, rel

        gate = acceptance.check_study(first).gate("outputs_reproducible")
        assert gate.ok, gate.findings
        print()
        print("  gate outputs_reproducible -> PASS on a fresh build")

        # Now the harness's side of the claim. A study whose report changed
        # after the manifest was written -- which is exactly what a pipeline
        # that stamps a timestamp into its output looks like from outside.
        drifted = fx.variant(
            first, root / "drifted", fx.break_reproducibility, rewrite_manifest=False
        )
        result = acceptance.check_study(drifted).gate("outputs_reproducible")
        assert not result.ok
        print()
        print("A study whose output moved after its manifest was written:")
        for finding in result.findings:
            print(f"  {finding}")
        assert len(result.findings) == 1, result.findings
        assert "REPORT.md" in result.findings[0]
        assert "the output changed since the manifest was written" in result.findings[0]

        # Rebuilding with a different as-of date moves several outputs at once,
        # and the harness lists every one of them rather than stopping at the
        # first -- the verdict is a task list, not an exception.
        rebuilt = root / "rebuilt"
        study.build_study(rebuilt, as_of="2026-07-15")
        stale_manifest = json.loads((first / "MANIFEST.json").read_text())
        (rebuilt / "MANIFEST.json").write_text(
            json.dumps(stale_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        result = acceptance.check_study(rebuilt).gate("outputs_reproducible")
        moved = [f.split(" does not match")[0] for f in result.findings]
        print()
        print("A rebuild with a different as-of date, checked against the old manifest:")
        for name in moved:
            print(f"  moved: {name}")
        assert sorted(moved) == ["REPORT.md", "SOURCE.json"], moved

        # An output nobody put in the manifest is caught too.
        def add_untracked(study_dir: Path) -> None:
            (Path(study_dir) / "scratch-notes.md").write_text(
                "# Scratch\n\nnumbers from the third attempt\n", encoding="utf-8"
            )

        untracked = fx.variant(
            first, root / "untracked", add_untracked, rewrite_manifest=False
        )
        findings = acceptance.check_study(untracked).gate("outputs_reproducible").findings
        assert len(findings) == 1 and "not covered by MANIFEST.json" in findings[0]
        print()
        print("An output file the manifest never heard of:")
        print(f"  {findings[0]}")

    print()
    print("OK: the worked study rebuilds byte-identically, and the harness names")
    print("    every output that moved, went missing, or was never tracked.")


if __name__ == "__main__":
    main()
