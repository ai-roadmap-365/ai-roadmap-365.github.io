#!/usr/bin/env python3
"""Assess a set of portfolio claims, then show the same claim rewritten."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claims import Claim, review, rewrite_hint

CLAIMS = [
    Claim("Built a state-of-the-art RAG system with blazing performance."),
    Claim("Significantly improved retrieval quality."),
    Claim("Reduced answer latency to 840ms.", "https://example.com/writeup"),
    Claim(
        "I cut p95 answer latency from 4.2s to 840ms by adding an IVF index, "
        "while the team migrated the ingestion pipeline.",
        "https://example.com/capstone",
    ),
    Claim("We shipped a support assistant used by 200 people.", "http://127.0.0.1:8080"),
]

WEAK_THEN_STRONG = (
    Claim("Significantly improved retrieval quality."),
    Claim(
        "I raised recall@10 from 0.71 to 0.94 by adding a reranking stage, "
        "measured over 200 held-out questions.",
        "https://example.com/eval",
    ),
)


def main() -> int:
    report = review(CLAIMS)
    print("--- claims as written ---")
    for assessment in report.assessments:
        print(assessment.line())
    print(f"  => {report.summary()}")

    print("--- what each weak claim needs ---")
    for claim in CLAIMS:
        hint = rewrite_hint(claim)
        if hint != "nothing to add":
            print(f"  {claim.text[:44]:<46} {hint}")

    print("--- the same claim, before and after ---")
    for claim in WEAK_THEN_STRONG:
        a = review([claim]).assessments[0]
        print(f"  {a.grade.value.upper():<7} {claim.text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
