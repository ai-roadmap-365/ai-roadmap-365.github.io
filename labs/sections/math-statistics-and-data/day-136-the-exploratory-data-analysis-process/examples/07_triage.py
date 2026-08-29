"""Exercise 7 -- triage: deciding which questions are worth pursuing.

Not every question deserves the same amount of exploration time. This
script scores a set of candidate questions on three things -- expected
information (how much the answer could change what you believe), cost
(analyst-hours to answer it), and decision relevance (how much the answer
could change what anyone actually does, Day 119's framing) -- and ranks
them. The comments beside each candidate justify its numbers; the point of
the exercise is that the ranking these numbers produce matches what a
practising analyst would actually choose, not that the numbers themselves
are precise.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import exploration as ex  # noqa: E402


def main() -> None:
    candidates = [
        # Cheap, and the answer would directly change which plan tier gets
        # marketing spend next quarter -- high decision relevance.
        ex.Candidate("does churn differ by plan tier?", expected_information=0.8, cost_hours=2, decision_relevance=0.9),
        # Cheap and informative in the narrow sense (you would learn
        # something), but nobody has proposed changing the button, so the
        # answer would not move any decision currently on the table.
        ex.Candidate("does button color affect clicks?", expected_information=0.6, cost_hours=1, decision_relevance=0.1),
        # Would answer many questions at once (high information) but costs
        # 40 analyst-hours -- a full audit of the tracking pipeline -- for a
        # decision that is only moderately live right now.
        ex.Candidate("full re-audit of tracking pipeline", expected_information=0.9, cost_hours=40, decision_relevance=0.5),
        # Moderate cost, moderate information, but tied to a pricing
        # decision that is being finalized this week -- high relevance.
        ex.Candidate("does the new pricing page change conversion?", expected_information=0.7, cost_hours=6, decision_relevance=0.85),
    ]

    ranked = ex.rank_candidates(candidates)
    print("Ranked by (expected_information * decision_relevance) / cost_hours:\n")
    for c in ranked:
        score = ex.triage_score(c)
        print(f"  {score:.4f}  {c.name}")
        print(f"           info={c.expected_information}  cost={c.cost_hours}h  relevance={c.decision_relevance}")

    names_in_order = [c.name for c in ranked]
    assert names_in_order[0] == "does churn differ by plan tier?", (
        f"expected the cheap, high-relevance churn question to rank first, ranking was {names_in_order}"
    )
    assert names_in_order[-1] == "full re-audit of tracking pipeline", (
        f"expected the expensive, moderate-relevance audit to rank last, ranking was {names_in_order}"
    )
    # The button-color question has real info but near-zero decision
    # relevance, and should therefore rank behind the pricing question,
    # which costs more but is tied to a live decision.
    button_rank = names_in_order.index("does button color affect clicks?")
    pricing_rank = names_in_order.index("does the new pricing page change conversion?")
    assert pricing_rank < button_rank, "a question tied to a live decision should outrank one that is not, even at higher cost"

    print(
        "\nOK: cheap and decision-relevant beats expensive and merely "
        "informative. The button-color question would teach you something "
        "real, but nothing is currently decided by the answer, so it sinks "
        "below a costlier question that is. This is Day 119's framing "
        "applied before any data is touched: ask first whether the answer "
        "would change a decision, not only whether it would be interesting."
    )


if __name__ == "__main__":
    main()
