"""Exercise 6 -- the research log as a data structure.

The day's practical deliverable: a dated record of every question asked,
what was looked at, and what was found -- including the nothings. This
script re-runs exercise 1's forty-comparison scan, but this time logs
EVERY comparison as it happens rather than only the one that "won", and
proves the log's own length is the true comparison count -- the number
Bonferroni actually needs (exercise 5) and the number exercise 9's
handoff to the report stage requires.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta, timezone  # noqa: E402

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
import exploration as ex  # noqa: E402


def main() -> None:
    rng = np.random.default_rng(ds.NARRATIVE_SEED)
    df = ds.build_narrative_frame(rng)
    results = ex.scan_narrative_frame(df, ds.NARRATIVE_SUBSET_COLS, ds.NARRATIVE_OUTCOME_COLS)

    log = ex.ResearchLog()
    start = datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc)
    for i, r in enumerate(results):
        question = f"does {r['outcome']} differ by {r['subset']} ({r['cut']})?"
        look = "two-sample z-test, groupby split"
        outcome = None
        if r["significant"]:
            outcome = f"p={r['p']:.4f}, d={r['effect_size']:.3f} -- looked significant on this pass"
        log.record(question, look, outcome, timestamp=(start + timedelta(minutes=3 * i)).isoformat())

    print(f"Log entries: {log.comparison_count}")
    print(f"Entries with a null outcome (nothing found): {log.null_count}")
    print(f"Entries with a recorded finding: {len(log.findings())}")

    assert log.comparison_count == len(results), "the log must record every comparison actually run"
    assert all(e.timestamp for e in log.entries), "every entry must carry a timestamp"
    assert all(e.look for e in log.entries), "every entry must carry a description of the look"
    assert log.null_count + len(log.findings()) == log.comparison_count, "every outcome is either null or a finding"
    assert log.null_count > 0, "most looks should produce nothing -- that is the normal texture of the work"

    print("\nFirst three entries (illustrating that nulls are recorded, not discarded):")
    for e in log.entries[:3]:
        print(f"  [{e.timestamp}] {e.question}")
        print(f"    look: {e.look}")
        print(f"    outcome: {e.outcome!r}")

    print(
        f"\nOK: the log recorded all {log.comparison_count} comparisons, "
        f"{log.null_count} of them nothing and {len(log.findings())} of "
        "them a finding worth a second look. This is what turns "
        "'I only ran one test' from an unverifiable claim into a checkable "
        "one: the comparison count Bonferroni needs (exercise 5) and the "
        "handoff to Day 133 requires (exercise 9) is not remembered or "
        "estimated afterward -- it is exactly len(log.entries)."
    )


if __name__ == "__main__":
    main()
