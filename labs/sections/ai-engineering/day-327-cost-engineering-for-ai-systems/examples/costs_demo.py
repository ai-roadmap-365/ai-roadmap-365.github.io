#!/usr/bin/env python3
"""Run a small workload four ways and compare what each lever saves."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from costs import BudgetExceeded, Pipeline, unit_economics

CONTEXT = [f"retrieved passage {i} " * 20 for i in range(6)]

PROMPTS = [
    "What is the refund window?",
    "What is the refund window?",          # exact repeat -> cache
    "Analyse why refunds spiked in March",  # reasoning -> large model
    "List the supported currencies",
    "What is the refund window?",          # repeat again
    "Compare the standard and premium tiers",
]


def run(label: str, *, budget: float, context_budget: int, use_cache: bool) -> None:
    pipe = Pipeline(budget=budget)
    for prompt in PROMPTS:
        if not use_cache:
            pipe.cache.clear()
        try:
            pipe.answer(prompt, CONTEXT, context_budget=context_budget)
        except BudgetExceeded as exc:
            print(f"{label:<22} STOPPED: {exc}")
            break
    econ = unit_economics(pipe.ledger, len(pipe.ledger.calls))
    models = ", ".join(f"{m}=${c:.4f}" for m, c in sorted(pipe.ledger.by_model().items()))
    print(f"{label:<22} {pipe.ledger.summary()}  per_request=${econ['per_request']:.5f}")
    print(f"{'':<22} by model: {models}")


def main() -> int:
    print("workload: 6 requests, 3 of them the same question")
    run("no cache, full ctx", budget=1.0, context_budget=10_000, use_cache=False)
    run("cache, full ctx", budget=1.0, context_budget=10_000, use_cache=True)
    run("cache, trimmed ctx", budget=1.0, context_budget=400, use_cache=True)
    run("tight budget", budget=0.0015, context_budget=10_000, use_cache=False)

    pipe = Pipeline(budget=1.0)
    for prompt in PROMPTS:
        pipe.answer(prompt, CONTEXT, context_budget=400)
    econ = unit_economics(pipe.ledger, len(PROMPTS))
    print(
        f"projection at 1M requests: ${econ['per_million_requests']:,.0f} "
        f"(from ${econ['per_request']:.5f} per request)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
