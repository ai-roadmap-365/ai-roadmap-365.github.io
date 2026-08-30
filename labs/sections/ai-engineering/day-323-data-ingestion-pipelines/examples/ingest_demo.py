#!/usr/bin/env python3
"""Three consecutive runs over a source that changes between them.

Run 2 is the line worth reading: it scans nothing and embeds nothing, because
the cursor has not moved. Run 3 shows an edited document re-embedded and
upserted without changing the document count.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingest import Checkpoint, DeadLetter, Index, SourceRecord, run_once


def main() -> int:
    # doc-3 has no payload: it fails extraction on every attempt and must not
    # stop the other four documents from being indexed.
    source = [
        SourceRecord("doc-1", 1, "alpha " * 45),
        SourceRecord("doc-2", 2, "beta " * 80),
        SourceRecord("doc-3", 3, None),
        SourceRecord("doc-4", 4, "delta " * 30),
        SourceRecord("doc-5", 5, "epsilon " * 55),
    ]

    index = Index()
    checkpoint = Checkpoint()
    dead_letters: list[DeadLetter] = []

    stats1 = run_once(source, index, checkpoint, dead_letters)
    print(stats1.line("run 1"))

    # Nothing changed and the cursor has not moved.
    stats2 = run_once(source, index, checkpoint, dead_letters)
    print(stats2.line("run 2"))

    # An edited document arrives with a new sequence number.
    source.append(SourceRecord("doc-1", 6, "alpha revised " * 40))
    stats3 = run_once(source, index, checkpoint, dead_letters)
    print(stats3.line("run 3"))

    print(f"index: {len(index.chunks)} chunks across {len(index.doc_ids())} documents")
    detail = ", ".join(f"{dl.doc_id}: {dl.error}" for dl in dead_letters)
    print(f"dead letters: {len(dead_letters)} ({detail})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
