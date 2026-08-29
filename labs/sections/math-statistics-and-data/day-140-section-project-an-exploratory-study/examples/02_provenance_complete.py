"""Exercise 2 -- provenance complete: url, retrieval date, checksum, licence.

Day 134's four facts, mechanised. A study whose source record is missing any
one of them cannot be re-obtained by anyone, including its own author six
months later. The gate names which field is missing rather than saying
"provenance incomplete", because the first is a task and the second is an
investigation.

It also does the thing a surprising number of real pipelines skip: it VERIFIES
the checksum against the file the record points at. A checksum nobody checks
is a decoration.

Run:  ../.venv/bin/python3 02_provenance_complete.py
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import acceptance
import fixtures as fx


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        good = fx.worked_study(root)

        record = json.loads((good / "SOURCE.json").read_text())
        print("The worked study's source record:")
        for key in ("url", "retrieved", "licence", "path"):
            print(f"  {key:16} {record[key]}")
        print(f"  {'checksum_sha256':16} {record['checksum_sha256']}")
        print(f"  {'dictionary':16} {len(record['dictionary'])} columns described")
        print()

        gate = acceptance.check_study(good).gate("provenance_complete")
        assert gate.ok, gate.findings
        print("  gate provenance_complete -> PASS")

        # Drop all three at once: the gate must name all three, not the first.
        broken = fx.variant(good, root / "no-provenance", fx.break_provenance)
        result = acceptance.check_study(broken).gate("provenance_complete")
        assert not result.ok
        print()
        print("With url, retrieved and checksum_sha256 removed:")
        for finding in result.findings:
            print(f"  {finding}")
        for key in ("url", "retrieved", "checksum_sha256"):
            assert any(f.endswith(key) for f in result.findings), (key, result.findings)
        assert len(result.findings) == 3, result.findings

        # One field at a time, to prove the gate is not simply reporting all
        # four whenever anything is wrong.
        print()
        print("One field at a time:")
        for key in ("url", "retrieved", "checksum_sha256", "licence"):
            one = fx.variant(
                good,
                root / f"missing-{key}",
                lambda d, k=key: fx.break_provenance(d, drop=(k,)),
            )
            findings = acceptance.check_study(one).gate("provenance_complete").findings
            assert findings == (f"SOURCE.json is missing: {key}",), findings
            print(f"  drop {key:16} -> {findings[0]}")

        # And the checksum is really recomputed, not merely required.
        stale = fx.variant(good, root / "stale-checksum", fx.break_provenance_checksum)
        findings = acceptance.check_study(stale).gate("provenance_complete").findings
        assert len(findings) == 1 and "does not match" in findings[0], findings
        print()
        print("A checksum that no longer matches the file it describes:")
        print(f"  {findings[0]}")

    print()
    print("OK: the provenance gate names every missing field individually and")
    print("    recomputes the recorded checksum against the file on disk.")


if __name__ == "__main__":
    main()
