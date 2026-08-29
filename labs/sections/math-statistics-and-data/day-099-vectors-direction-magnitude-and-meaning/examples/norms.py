"""Where L1 and L2 disagree — and why that is a decision, not a detail.

Two candidate documents are compared against the same query. Under the L2
(Euclidean) norm one of them is nearer. Under the L1 (taxicab) norm the *other*
one is. Both answers are arithmetically correct. "Nearest" is only a
well-defined question once you have named a norm.

The numbers are chosen so you can do them in your head:

    query      = (0, 0, 0)
    candidate  spike   = (4, 0, 0)      one big component
    candidate  spread  = (2, 2, 2)      three small ones

    L1: |4| + |0| + |0| = 4      vs  |2| + |2| + |2| = 6      -> spike is nearer
    L2: sqrt(16 + 0 + 0) = 4     vs  sqrt(4 + 4 + 4) = sqrt(12) = 3.4641...
                                                              -> spread is nearer

Squaring is what does it. L2 squares each component before adding, so a single
component of 4 contributes 16 while three components of 2 contribute 4 each.
L1 never squares, so it counts every unit of difference at face value and one
big deviation costs exactly as much as the same total spread thinly.

Run from the examples directory:

    python3 norms.py
"""

from __future__ import annotations

from vectors import l1_distance, l1_norm, l2_norm, distance

QUERY = [0, 0, 0]
CANDIDATES = {
    "spike": [4, 0, 0],
    "spread": [2, 2, 2],
}

# A second pair, translated away from the origin, to show that the effect is
# about the shape of the difference and not about sitting at zero.
BASE = [10, 10, 10]
SHIFTED = {
    "spike": [14, 10, 10],
    "spread": [12, 12, 12],
}


def rank(query, candidates, metric) -> list[tuple[str, float]]:
    scored = [(label, metric(query, vec)) for label, vec in candidates.items()]
    return sorted(scored, key=lambda pair: (pair[1], pair[0]))


def report(title, query, candidates) -> tuple[str, str]:
    print(title)
    print(f"  query = {query}")
    for label, vec in candidates.items():
        diff = [b - a for a, b in zip(query, vec)]
        squares = " + ".join(str(d * d) for d in diff)
        abses = " + ".join(str(abs(d)) for d in diff)
        print(f"  {label:<8} = {vec}   difference = {diff}")
        print(f"           L1 = {abses} = {l1_norm(diff):.4f}")
        print(f"           L2 = sqrt({squares}) = {l2_norm(diff):.4f}")

    l2_rank = rank(query, candidates, distance)
    l1_rank = rank(query, candidates, l1_distance)
    print(f"  L2 ranking: {[f'{n} {s:.4f}' for n, s in l2_rank]}")
    print(f"  L1 ranking: {[f'{n} {s:.4f}' for n, s in l1_rank]}")
    print(f"  nearest under L2: {l2_rank[0][0]}")
    print(f"  nearest under L1: {l1_rank[0][0]}")
    print(f"  the two norms disagree: {l2_rank[0][0] != l1_rank[0][0]}")
    print()
    return l2_rank[0][0], l1_rank[0][0]


def main() -> int:
    print("L1 and L2 ranking the same two candidates in opposite orders")
    print()
    a = report("Case 1 — query at the origin", QUERY, CANDIDATES)
    b = report("Case 2 — the same shapes, moved away from the origin", BASE, SHIFTED)

    disagreed = a[0] != a[1] and b[0] != b[1]
    print("Both cases produced a disagreement:", disagreed)
    print()
    print("Neither answer is wrong. L2 is the default because it matches the")
    print("everyday meaning of distance and because squaring makes it smooth")
    print("to work with. L1 is chosen when one large deviation should not be")
    print("allowed to dominate a lot of small ones. The norm is a modelling")
    print("choice, and it belongs in the write-up next to the result.")
    return 0 if disagreed else 1


if __name__ == "__main__":
    raise SystemExit(main())
