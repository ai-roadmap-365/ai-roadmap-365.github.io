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
    if model not in PRICES:
        raise KeyError(f"no price for model '{model}'")
    in_price, out_price = PRICES[model]
    return (input_tokens * in_price + output_tokens * out_price) / 1_000_000


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
    lowered = prompt.lower()
    if any(word in lowered for word in hard_words) or estimate_tokens(prompt) > 200:
        return "large"
    return "small"


def trim_context(chunks: list[str], budget_tokens: int) -> list[str]:
    """Keep the highest-priority chunks that fit a token budget.

    Chunks arrive in priority order. Stopping at the first one that does not
    fit -- rather than skipping it and trying the next -- keeps the context
    contiguous in relevance, which matters more than packing the budget full.
    """
    kept: list[str] = []
    used = 0
    for chunk in chunks:
        size = estimate_tokens(chunk)
        if used + size > budget_tokens:
            break
        kept.append(chunk)
        used += size
    return kept


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
        """Handle one request, respecting the cache, the router and the cap."""
        context = context or []
        kept = trim_context(context, context_budget)
        key = prompt + "||" + "|".join(kept)

        if key in self.cache:
            # A cache hit is recorded as a zero-cost call rather than skipped
            # entirely, so the hit rate is visible in the ledger.
            self.ledger.calls.append(
                Call(model="cache", input_tokens=0, output_tokens=0, cost=0.0, cached=True)
            )
            return self.cache[key]

        model = route(prompt)
        # Degrade before refusing: past the threshold, downgrade rather than
        # fail. A cheaper answer beats no answer for most workloads.
        if model == "large" and self.spent() >= self.budget * self.degrade_at:
            model = "small"

        input_tokens = estimate_tokens(prompt) + sum(estimate_tokens(c) for c in kept)
        output_tokens = 120
        cost = cost_of(model, input_tokens, output_tokens)

        # Check BEFORE spending. Estimating after the call is an audit, not a
        # control.
        if self.spent() + cost > self.budget:
            raise BudgetExceeded(
                f"request would cost ${cost:.4f}, only ${self.remaining():.4f} left"
            )

        answer = f"[{model}] answer to: {prompt[:40]}"
        self.cache[key] = answer
        self.ledger.calls.append(
            Call(model=model, input_tokens=input_tokens, output_tokens=output_tokens, cost=cost)
        )
        return answer


def unit_economics(ledger: Ledger, requests: int) -> dict[str, float]:
    """Cost per request and projected cost at scale.

    Totals are not decisions. Cost per request multiplied by expected volume is
    what tells you whether a feature is viable, and it is the number that
    should appear in a design document.
    """
    if requests <= 0:
        return {"per_request": 0.0, "per_1k_requests": 0.0, "per_million_requests": 0.0}
    per = ledger.total / requests
    return {
        "per_request": per,
        "per_1k_requests": per * 1_000,
        "per_million_requests": per * 1_000_000,
    }
