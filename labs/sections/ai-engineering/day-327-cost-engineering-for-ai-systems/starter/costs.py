"""Cost accounting, caching, tiering and budget enforcement for an AI pipeline.

Offline and standard-library only. Prices are a fixed table rather than a live
API, and "tokens" are counted with a crude word-based estimator -- both are
simulations. What is real is the accounting: where cost accumulates, which
levers move it, and what happens when a budget runs out.

The four levers, in the order they usually pay off:

  cache     an exact repeat costs nothing
  tier      route easy work to a cheaper model
  trim      send less context
  cap       refuse, or degrade, rather than overspend

The last one is the one teams skip, and it is the only one that bounds the
worst case. Without a cap, a retry loop against a paid API is unbounded spend.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Illustrative prices in dollars per million tokens. The shape is what
# matters: output costs several times more than input, and the gap between
# tiers is an order of magnitude rather than a few percent.
PRICES: dict[str, tuple[float, float]] = {
    "small": (0.25, 1.25),
    "large": (3.00, 15.00),
}


class BudgetExceeded(RuntimeError):
    """Raised when a request would push spend past its cap."""


def estimate_tokens(text: str) -> int:
    """Crude token estimate: roughly four characters per token.

    Real tokenisers are model-specific and this is not one. It is honest about
    being an estimate, which is the right posture for a pre-flight cost check --
    you cap on the estimate, then reconcile against the provider's reported
    usage afterwards.
    """
    return max(1, len(text) // 4)


def cost_of(model: str, input_tokens: int, output_tokens: int) -> float:
    """Dollar cost of one call, from the price table."""
    # TASK 1: dollar cost of one call from PRICES.
    # Prices are per MILLION tokens. Raise KeyError for an unknown model --
    # pricing it at zero is how a new model silently escapes accounting.
    raise NotImplementedError("implement cost_of")

@dataclass
class Call:
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    cached: bool = False


@dataclass
class Ledger:
    """Every call, so cost can be attributed rather than merely totalled."""

    calls: list[Call] = field(default_factory=list)

    @property
    def total(self) -> float:
        return sum(c.cost for c in self.calls)

    @property
    def cache_hits(self) -> int:
        return sum(1 for c in self.calls if c.cached)

    def by_model(self) -> dict[str, float]:
        out: dict[str, float] = {}
        for call in self.calls:
            out[call.model] = out.get(call.model, 0.0) + call.cost
        return out

    def summary(self) -> str:
        return (
            f"calls={len(self.calls)} cached={self.cache_hits} "
            f"total=${self.total:.4f}"
        )


def route(prompt: str, *, hard_words: tuple[str, ...] = ("analyse", "compare", "explain why")) -> str:
    """Pick the cheapest model that can plausibly do the job.

    A real router uses a classifier or a length heuristic; this one looks for
    words that signal reasoning. The mechanism matters less than the principle:
    most traffic does not need the expensive model, and sending all of it there
    is the single most common source of avoidable spend.
    """
    # TASK 2: return "small" or "large".
    # "large" when the lowered prompt contains any of hard_words, or when
    # estimate_tokens(prompt) > 200. Otherwise "small".
    raise NotImplementedError("implement route")

def trim_context(chunks: list[str], budget_tokens: int) -> list[str]:
    """Keep the highest-priority chunks that fit a token budget.

    Chunks arrive in priority order. Stopping at the first one that does not
    fit -- rather than skipping it and trying the next -- keeps the context
    contiguous in relevance, which matters more than packing the budget full.
    """
    # TASK 3: keep chunks in order while they fit budget_tokens.
    # STOP at the first chunk that does not fit rather than skipping ahead to
    # a smaller one -- contiguity in relevance beats filling the budget.
    raise NotImplementedError("implement trim_context")

@dataclass
class Pipeline:
    """A request pipeline with a cache, a router and a spend cap."""

    budget: float
    ledger: Ledger = field(default_factory=Ledger)
    cache: dict[str, str] = field(default_factory=dict)
    degrade_at: float = 0.8  # fraction of budget after which we downgrade

    def spent(self) -> float:
        return self.ledger.total

    def remaining(self) -> float:
        return max(0.0, self.budget - self.spent())

    def answer(self, prompt: str, context: list[str] | None = None, *, context_budget: int = 400) -> str:
        # TASK 5: handle one request.
        #   - trim the context, then build a cache key from prompt AND the
        #     kept chunks; a hit appends a zero-cost Call(cached=True) so
        #     the hit rate stays visible in the ledger, and returns
        #   - route; if the route is large and spent() has passed
        #     budget * degrade_at, downgrade to small rather than failing
        #   - estimate input tokens (prompt + kept chunks), assume 120
        #     output tokens, and price the call
        #   - raise BudgetExceeded BEFORE recording anything if
        #     spent() + cost would exceed the budget
        #   - otherwise cache the answer, append the Call, and return it
        raise NotImplementedError("implement Pipeline.answer")


def unit_economics(ledger: Ledger, requests: int) -> dict[str, float]:
    """Cost per request and projected cost at scale.

    Totals are not decisions. Cost per request multiplied by expected volume is
    what tells you whether a feature is viable, and it is the number that
    should appear in a design document.
    """
    # TASK 4: return per_request, per_1k_requests and per_million_requests.
    # Zero requests is a normal state on a fresh ledger: return zeros rather
    # than dividing.
    raise NotImplementedError("implement unit_economics")
