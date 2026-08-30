#!/usr/bin/env python3
"""Redact a support ticket, track where it flows, then verify an erasure."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from privacy import Category, DataFlow, erase, minimise, redact

# Synthetic and invalid by construction: example.com is reserved, and the card
# number fails the Luhn check.
TICKET = (
    "From: ada@example.com\n"
    "Phone: +44 7700 900123\n"
    "Card ending 4111 1111 1111 1111 was charged twice.\n"
    "Reported from 192.0.2.44. Reference SSN 123-45-6789."
)


def main() -> int:
    result = redact(TICKET)
    print("--- redacted ---")
    print(result.text)
    print(f"findings: {result.summary()}")

    stable = redact("contact ada@example.com again")
    same = result.findings[0].token == stable.findings[0].token
    print(f"pseudonym stable across records: {same}")

    print("--- data flow ---")
    flow = DataFlow()
    for store in ("database", "vector_index", "response_cache", "audit_log"):
        flow.record(store, "subject-42")
    print(f"subject-42 present in: {sorted(flow.where('subject-42'))}")

    print("--- erasure, first attempt (the stores someone remembered) ---")
    partial = erase(flow, "subject-42", stores=["database", "vector_index"])
    print(partial.summary())

    print("--- erasure, complete ---")
    full = erase(flow, "subject-42")
    print(full.summary())

    print("--- minimisation ---")
    record = {"name": "Ada", "email": "ada@example.com", "tier": "pro", "note": "vip"}
    print(f"kept: {minimise(record, {'tier'})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
