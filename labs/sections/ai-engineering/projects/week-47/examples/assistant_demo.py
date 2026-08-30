#!/usr/bin/env python3
"""Run the assembled assistant end to end."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from assistant import Assistant, BudgetExceeded, SourceDoc

CORPUS = [
    SourceDoc("sla", 1, "Enterprise uptime guarantee is 99.99 percent per calendar month. "
                        "Credits apply when uptime falls below the guarantee. " * 2),
    SourceDoc("refunds", 2, "The refund window is thirty days from purchase. Refund requests "
                            "outside the refund window need approval. Contact billing at "
                            "ada@example.com or +44 7700 900123. " * 2),
    SourceDoc("tiers", 3, "Standard and premium tiers differ in support response times "
                          "and included seats. Premium adds priority routing. " * 2),
    SourceDoc("broken", 4, None),
    SourceDoc("garbled", 5, "=?# " * 60),
]


def main() -> int:
    bot = Assistant(budget=0.05)

    print("--- ingest ---")
    print(bot.ingest(CORPUS).line())
    print(f"dead letters: {bot.dead_letters}")

    print("--- re-ingest, nothing changed ---")
    print(bot.ingest(CORPUS).line())

    print("--- edited document ---")
    edited = CORPUS + [
        SourceDoc("refunds", 6, "The refund window is now sixty days from purchase. " * 3)
    ]
    print(bot.ingest(edited).line())

    print("--- answers ---")
    for question in (
        "What is the refund window?",
        "What is the refund window?",
        "Compare the standard and premium tiers",
    ):
        print(bot.answer(question))

    print("--- cost ---")
    stages = ", ".join(f"{k}=${v:.5f}" for k, v in sorted(bot.ledger.by_stage().items()))
    print(f"total=${bot.ledger.total:.5f}  by stage: {stages}")

    print("--- budget enforcement ---")
    small = Assistant(budget=0.000005)
    small.ingest(CORPUS)
    try:
        small.answer("What is the refund window?")
    except BudgetExceeded as exc:
        print(f"refused: {exc}")

    print("--- erasure ---")
    print(f"chunks before: {len(bot.chunks)}")
    print(f"verified: {bot.erase('refunds')}")
    print(f"chunks after: {len(bot.chunks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
