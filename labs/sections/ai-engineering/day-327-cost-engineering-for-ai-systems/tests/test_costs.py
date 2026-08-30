"""Grouped by lever, so a failure names which control broke.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from costs import (  # noqa: E402
    PRICES,
    BudgetExceeded,
    Ledger,
    Pipeline,
    cost_of,
    estimate_tokens,
    route,
    trim_context,
    unit_economics,
)


# ---------------------------------------------------------------- accounting


def test_output_tokens_cost_more_than_input_tokens():
    # True of every major provider, and the reason "just send more context" is
    # cheaper than "just generate more".
    for model, (inp, out) in PRICES.items():
        assert out > inp, f"{model}: output should cost more than input"


def test_cost_scales_linearly_with_tokens():
    single = cost_of("small", 1000, 0)
    double = cost_of("small", 2000, 0)
    assert abs(double - 2 * single) < 1e-12


def test_large_model_costs_an_order_of_magnitude_more():
    small = cost_of("small", 1000, 1000)
    large = cost_of("large", 1000, 1000)
    assert large > small * 5


def test_unknown_model_raises_rather_than_costing_zero():
    # Silently pricing an unknown model at zero is how spend goes unnoticed.
    with pytest.raises(KeyError):
        cost_of("gpt-imaginary", 10, 10)


def test_token_estimate_is_never_zero():
    assert estimate_tokens("") >= 1
    assert estimate_tokens("a") >= 1


# --------------------------------------------------------------------- cache


def test_repeat_request_is_free_and_recorded():
    pipe = Pipeline(budget=1.0)
    pipe.answer("What is the refund window?")
    first = pipe.spent()

    pipe.answer("What is the refund window?")
    assert pipe.spent() == first, "a cache hit must not add cost"
    assert pipe.ledger.cache_hits == 1


def test_cache_hits_appear_in_the_ledger_not_hidden():
    # A hit is a zero-cost call rather than a skipped one, so the hit rate is
    # visible when attributing spend.
    pipe = Pipeline(budget=1.0)
    pipe.answer("same")
    pipe.answer("same")
    assert len(pipe.ledger.calls) == 2
    assert pipe.ledger.by_model()["cache"] == 0.0


def test_different_context_is_a_different_cache_key():
    pipe = Pipeline(budget=1.0)
    pipe.answer("question", ["context A"])
    before = pipe.spent()
    pipe.answer("question", ["context B"])
    assert pipe.spent() > before


# -------------------------------------------------------------------- router


def test_reasoning_prompts_route_to_the_large_model():
    assert route("Analyse why sales fell") == "large"
    assert route("Compare the two plans") == "large"


def test_simple_prompts_route_to_the_small_model():
    assert route("What is the refund window?") == "small"
    assert route("List supported currencies") == "small"


def test_very_long_prompts_route_to_the_large_model():
    assert route("word " * 500) == "large"


# ---------------------------------------------------------------------- trim


def test_trim_keeps_what_fits_in_priority_order():
    chunks = ["a" * 400, "b" * 400, "c" * 400]  # ~100 tokens each
    kept = trim_context(chunks, 250)
    assert kept == chunks[:2]


def test_trim_stops_rather_than_skipping_to_a_smaller_chunk():
    # Contiguity in relevance beats packing the budget full.
    chunks = ["a" * 4000, "b" * 40]
    assert trim_context(chunks, 100) == []


def test_trim_with_a_generous_budget_keeps_everything():
    chunks = ["a" * 40, "b" * 40]
    assert trim_context(chunks, 10_000) == chunks


# -------------------------------------------------------------------- budget


def test_budget_is_checked_before_spending_not_after():
    pipe = Pipeline(budget=0.0005)
    with pytest.raises(BudgetExceeded):
        for i in range(50):
            pipe.answer(f"Analyse question number {i}")
    assert pipe.spent() <= pipe.budget, "spend must never exceed the cap"


def test_degrades_to_the_cheap_model_before_refusing():
    # Past the threshold a large-model request is downgraded rather than
    # failed: a cheaper answer beats no answer for most workloads.
    pipe = Pipeline(budget=0.01, degrade_at=0.0)
    pipe.answer("Analyse the quarterly numbers")
    assert pipe.ledger.calls[-1].model == "small"


def test_remaining_never_goes_negative():
    pipe = Pipeline(budget=0.0)
    assert pipe.remaining() == 0.0


# ----------------------------------------------------------- unit economics


def test_unit_economics_scales_from_a_single_request():
    ledger = Ledger()
    pipe = Pipeline(budget=1.0, ledger=ledger)
    pipe.answer("What is the refund window?")

    econ = unit_economics(ledger, 1)
    assert econ["per_1k_requests"] == pytest.approx(econ["per_request"] * 1000)
    assert econ["per_million_requests"] == pytest.approx(econ["per_request"] * 1_000_000)


def test_unit_economics_of_zero_requests_is_zero_not_an_error():
    assert unit_economics(Ledger(), 0)["per_request"] == 0.0


def test_cost_attribution_splits_by_model():
    pipe = Pipeline(budget=1.0)
    pipe.answer("What is the refund window?")       # small
    pipe.answer("Analyse the refund spike")          # large
    by_model = pipe.ledger.by_model()
    assert set(by_model) == {"small", "large"}
    assert by_model["large"] > by_model["small"]
