"""One query, three candidates, three measures -- and three different winners.

Run from the `examples/` directory:

    ../.venv/bin/python3 01_three_measures_three_winners.py

This is the disagreement the whole day is built on. None of the three answers
is a bug and none of them is wrong. They are answers to different questions,
and until you have decided which question you are asking, the ranking your
retrieval system returns is decided by whichever measure someone left in place.
"""

from __future__ import annotations

import catalogue
import measures
from measures import TOL

Q = catalogue.QUERY
A = catalogue.ARTICLES


def table(title: str, rows: list[tuple[str, str]]) -> None:
    print(f"  {title}")
    for left, right in rows:
        print(f"    {left:<14} {right}")
    print()


print("=" * 74)
print("1. The data")
print("=" * 74)
print()
print("  A help-centre search. Four terms, counted. The query is the reader's")
print("  own note; the three candidates are articles.")
print()
print(f"    {'':<12}" + "".join(f"{t:>10}" for t in catalogue.TERMS)
      + f"{'total':>10}")
print(f"    {'query':<12}" + "".join(f"{c:>10}" for c in Q)
      + f"{sum(Q):>10}")
for name, vec in A.items():
    print(f"    {name:<12}" + "".join(f"{c:>10}" for c in vec)
          + f"{sum(vec):>10}")
print()
print("  Cartogram is the query's exact profile at three times the length:")
print(f"    query * 3 = {tuple(3 * c for c in Q)} = {A['Cartogram']}")
assert tuple(3 * c for c in Q) == A["Cartogram"]
print()

print("=" * 74)
print("2. The three measures, computed")
print("=" * 74)
print()

l1 = {n: measures.l1_distance(Q, v) for n, v in A.items()}
l2 = {n: measures.l2_distance(Q, v) for n, v in A.items()}
linf = {n: measures.linf_distance(Q, v) for n, v in A.items()}
cos = {n: measures.cosine_similarity(Q, v) for n, v in A.items()}

header = f"    {'':<12}{'L1':>12}{'L2':>12}{'L-inf':>12}{'cosine':>12}"
print(header)
print("    " + "-" * (len(header) - 4))
for name in A:
    print(f"    {name:<12}{l1[name]:>12.4f}{l2[name]:>12.4f}"
          f"{linf[name]:>12.4f}{cos[name]:>12.4f}")
print()
print("  L1 and L2 and L-infinity are DISTANCES: smaller is better.")
print("  Cosine is a SIMILARITY: larger is better. Mixing the two up returns")
print("  the worst match with complete confidence and no error message.")
print()

print("=" * 74)
print("3. The winners")
print("=" * 74)
print()

winners = {
    "L1 (Manhattan)": measures.winner(Q, A, measures.l1_distance),
    "L2 (Euclidean)": measures.winner(Q, A, measures.l2_distance),
    "L-inf (Chebyshev)": measures.winner(Q, A, measures.linf_distance),
    "cosine similarity": measures.winner(Q, A, measures.cosine_similarity,
                                         higher_is_better=True),
}
for measure_name, best in winners.items():
    print(f"    {measure_name:<20} picks  {best}")
print()

assert winners["L1 (Manhattan)"] == "Aisle"
assert winners["L2 (Euclidean)"] == "Beacon"
assert winners["L-inf (Chebyshev)"] == "Beacon"
assert winners["cosine similarity"] == "Cartogram"
assert len({winners["L1 (Manhattan)"], winners["L2 (Euclidean)"],
            winners["cosine similarity"]}) == 3

print("  Three of the four measures name three different articles, on the")
print("  same four numbers, with no randomness and nothing to tune.")
print()

print("=" * 74)
print("4. Why each one is right, on its own terms")
print("=" * 74)
print()

table("L1 picks Aisle -- total disagreement is what it measures.", [
    ("Aisle", f"|4-4| + |3-3| + |2-2| + |1-6| = {l1['Aisle']:.0f}"),
    ("Beacon", f"|4-6| + |3-1| + |2-4| + |1-1| = {l1['Beacon']:.0f}"),
    ("", "5 is less than 6. Aisle wins, and it is a fair answer:"),
    ("", "there is genuinely less disagreement in total."),
])

table("L2 picks Beacon -- squaring punishes one BIG disagreement.", [
    ("Aisle", f"sqrt(0 + 0 + 0 + 25) = {l2['Aisle']:.4f}"),
    ("Beacon", f"sqrt(4 + 4 + 4 + 0)  = {l2['Beacon']:.4f}"),
    ("", "Aisle's single error of 5 costs 25. Beacon's three errors"),
    ("", "of 2 cost 4 each, 12 in total, even though they add to 6."),
])

table("L-infinity agrees with L2 here, for a different reason.", [
    ("Aisle", f"max(0, 0, 0, 5) = {linf['Aisle']:.0f}"),
    ("Beacon", f"max(2, 2, 2, 0) = {linf['Beacon']:.0f}"),
    ("", "It looks only at the worst single term and ignores the rest"),
    ("", "entirely. Beacon's worst is 2; Aisle's worst is 5."),
])

table("Cosine picks Cartogram -- it is scored on direction alone.", [
    ("Cartogram", f"cosine = {cos['Cartogram']:.6f}"),
    ("", "Exactly 1.0: same mix of terms, three times the length."),
    ("", f"Its L2 distance is {l2['Cartogram']:.4f}, the worst here by far,"),
    ("", "because length is the one thing cosine throws away."),
])

assert abs(cos["Cartogram"] - 1.0) <= TOL
assert l2["Cartogram"] == max(l2.values())
assert l1["Cartogram"] == max(l1.values())

print("=" * 74)
print("5. The same numbers, from NumPy")
print("=" * 74)
print()
print("  Nothing in measures.py uses NumPy. numpy.linalg.norm with an `ord`")
print("  argument IS the p-norm family, so it is an independent answer rather")
print("  than a restatement.")
print()

import numpy as np  # noqa: E402  (imported here to make the point above)

worst = 0.0
print(f"    {'':<12}{'ord=1':>12}{'ord=2':>12}{'ord=inf':>12}")
for name, vec in A.items():
    d = np.asarray(Q, dtype=float) - np.asarray(vec, dtype=float)
    row = [float(np.linalg.norm(d, ord=o)) for o in (1, 2, np.inf)]
    mine = [l1[name], l2[name], linf[name]]
    worst = max(worst, max(abs(x - y) for x, y in zip(row, mine)))
    print(f"    {name:<12}" + "".join(f"{v:>12.4f}" for v in row))
print()
print(f"  worst disagreement with measures.py: {worst:.3e}")
print(f"  stated tolerance:                    {TOL:.3e}")
assert worst <= TOL
print()

print("=" * 74)
print("6. The point")
print("=" * 74)
print()
print("  If this were a search box, the article at the top of the results is")
print("  decided by a single argument that nobody in the room has discussed.")
print()
print("  The right answer depends entirely on what you meant:")
print("    * 'closest counts overall'      -> L1  -> Aisle")
print("    * 'no single term badly wrong'  -> L2  -> Beacon")
print("    * 'same topic, any length'      -> cos -> Cartogram")
print()
print("  For text retrieval the third is almost always what you meant, which")
print("  is why cosine is the default in every vector database. The lesson to")
print("  keep is not 'use cosine'. It is that the default is a decision, and")
print("  somebody has to make it on purpose.")
print()
print("01_three_measures_three_winners.py: every assertion held.")
