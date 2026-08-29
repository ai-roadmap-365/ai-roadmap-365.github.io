"""Which of these measures is a metric, and what it costs you when one is not.

Run from the `examples/` directory:

    ../.venv/bin/python3 03_metrics_and_non_metrics.py

"Metric" is not a compliment. It is a checklist of four properties, and the
reason to care is that indexes, clustering algorithms and proofs of correctness
are built on them. A measure that fails one is not banned -- cosine distance
fails one and is the most used measure in the field -- but you must know which
one it failed and what you were relying on.
"""

from __future__ import annotations

import itertools
import math

import catalogue
import measures
from measures import TOL

print("=" * 74)
print("1. The four axioms")
print("=" * 74)
print()
print("  A function d(x, y) is a METRIC when, for every x, y and z:")
print()
print("    1. non-negativity            d(x, y) >= 0")
print("    2. identity of indiscernibles")
print("                                 d(x, y) = 0 if and only if x = y")
print("    3. symmetry                  d(x, y) = d(y, x)")
print("    4. triangle inequality       d(x, z) <= d(x, y) + d(y, z)")
print()
print("  The fourth is the one with teeth. It says a detour can never be")
print("  shorter than going direct, and it is what lets an index skip whole")
print("  regions of a dataset without looking inside them -- if the query is")
print("  10 away from a cluster centre and the cluster has radius 2, nothing")
print("  in it can be closer than 8, so it need not be opened.")
print()

METRICS = {
    "L1 (Manhattan)": measures.l1_distance,
    "L2 (Euclidean)": measures.l2_distance,
    "L-inf (Chebyshev)": measures.linf_distance,
}

print("=" * 74)
print("2. L1, L2 and L-infinity pass all four")
print("=" * 74)
print()

x, y, z = catalogue.TRIANGLE_TRIPLE
print(f"    x = {x}")
print(f"    y = {y}")
print(f"    z = {z}")
print()

for name, d in METRICS.items():
    print(f"  {name}")
    assert d(x, y) >= 0.0 and d(y, z) >= 0.0 and d(x, z) >= 0.0
    print(f"    1. non-negativity   d(x,y) = {d(x, y):.6f}   >= 0")

    assert d(x, x) == 0.0 and d(x, y) > 0.0
    print(f"    2. zero iff equal   d(x,x) = {d(x, x):.6f}, "
          f"d(x,y) = {d(x, y):.6f}")

    assert abs(d(x, y) - d(y, x)) <= TOL
    print(f"    3. symmetry         d(x,y) = {d(x, y):.6f}"
          f" = d(y,x) = {d(y, x):.6f}")

    # Every one of the six orderings, not just the convenient one.
    worst_slack = math.inf
    for a, b, c in itertools.permutations((x, y, z)):
        slack = d(a, b) + d(b, c) - d(a, c)
        assert slack >= -TOL, (name, slack)
        worst_slack = min(worst_slack, slack)
    print(f"    4. triangle         all 6 orderings hold; tightest slack "
          f"{worst_slack:.6f}")
    print(f"       direct  d(x,z) = {d(x, z):.6f}")
    print(f"       via y            {d(x, y) + d(y, z):.6f}")
    print()

print("=" * 74)
print("3. Cosine distance is NOT a metric, with the counter-example")
print("=" * 74)
print()
print("  Day 103 proved this. Restated here with concrete numbers, because a")
print("  triple you can hold in your head outlasts a proof.")
print()

east, diagonal, north = catalogue.EAST, catalogue.DIAGONAL, catalogue.NORTH
print(f"    east     = {east}      pointing along x")
print(f"    diagonal = {diagonal}      45 degrees between them")
print(f"    north    = {north}      pointing along y")
print()

d_ed = measures.cosine_distance(east, diagonal)
d_dn = measures.cosine_distance(diagonal, north)
d_en = measures.cosine_distance(east, north)
print(f"    cosine_distance(east, diagonal)  = {d_ed:.6f}")
print(f"    cosine_distance(diagonal, north) = {d_dn:.6f}")
print("    ----------------------------------------------")
print(f"    going via the diagonal           = {d_ed + d_dn:.6f}")
print(f"    cosine_distance(east, north)     = {d_en:.6f}   <-- LONGER")
print()
assert d_ed + d_dn < d_en - TOL
print(f"  The direct route is {d_en - (d_ed + d_dn):.6f} longer than the detour.")
print("  No metric may ever allow that. Cosine distance does, so it is a")
print("  DISSIMILARITY and not a distance, whatever the function is called.")
print()
print("  It fails the second axiom too, and this one bites more often:")
print()
doubled = tuple(2 * c for c in east)
print(f"    cosine_distance({east}, {doubled}) = "
      f"{measures.cosine_distance(east, doubled):.6f}")
print(f"    and {east} is not {doubled}")
assert abs(measures.cosine_distance(east, doubled)) <= TOL
assert east != doubled
print()
print("  Distance zero between two things that are not the same thing. For")
print("  cosine that is the FEATURE -- length is what it was asked to ignore --")
print("  but it means cosine cannot tell a document from the same document")
print("  repeated twice, and any deduplication built on it will not either.")
print()
print("  Angular distance, arccos(similarity) / pi, IS a metric on the same")
print("  data and preserves the same ranking, so when an index demands a")
print("  metric that is the standard repair:")
print()
for pair, label in (((east, diagonal), "east / diagonal"),
                    ((diagonal, north), "diagonal / north"),
                    ((east, north), "east / north")):
    ang = math.acos(max(-1.0, min(1.0, measures.cosine_similarity(*pair)))) / math.pi
    print(f"    angular({label:<17}) = {ang:.6f}")
ang_ed = math.acos(measures.cosine_similarity(east, diagonal)) / math.pi
ang_dn = math.acos(measures.cosine_similarity(diagonal, north)) / math.pi
ang_en = math.acos(max(-1.0, min(1.0, measures.cosine_similarity(east, north)))) / math.pi
print(f"    via the diagonal          = {ang_ed + ang_dn:.6f}"
      f"   >=  direct {ang_en:.6f}")
assert ang_ed + ang_dn >= ang_en - TOL
print()

print("=" * 74)
print("4. Jaccard distance and Hamming distance ARE metrics")
print("=" * 74)
print()
print("  Not asserted from a textbook. Checked exhaustively on every triple.")
print()

universe = ("a", "b", "c", "d")
subsets = [frozenset(c)
           for r in range(len(universe) + 1)
           for c in itertools.combinations(universe, r)]
tightest = math.inf
triples = 0
for a, b, c in itertools.product(subsets, repeat=3):
    slack = (measures.jaccard_distance(a, b) + measures.jaccard_distance(b, c)
             - measures.jaccard_distance(a, c))
    assert slack >= -TOL, (a, b, c, slack)
    tightest = min(tightest, slack)
    triples += 1
print(f"  Jaccard distance over all {len(subsets)} subsets of a 4-element set:")
print(f"    {triples} triples checked, none violated the triangle inequality")
print(f"    tightest slack: {tightest:.6f} (0 means equality, which is allowed)")
assert triples == len(subsets) ** 3
print()

strings = list(itertools.product((0, 1), repeat=4))
tightest_h = math.inf
triples_h = 0
for a, b, c in itertools.product(strings, repeat=3):
    slack = (measures.hamming_distance(a, b) + measures.hamming_distance(b, c)
             - measures.hamming_distance(a, c))
    assert slack >= 0, (a, b, c, slack)
    tightest_h = min(tightest_h, slack)
    triples_h += 1
print(f"  Hamming distance over all {len(strings)} 4-bit strings:")
print(f"    {triples_h} triples checked, none violated the triangle inequality")
print(f"    tightest slack: {tightest_h}")
assert triples_h == len(strings) ** 3
print()

print("  The same sweep run on cosine distance finds violations immediately,")
print("  which is what makes the two results above worth having:")
print()
violations = 0
worst = 0.0
vectors = [v for v in itertools.product((0, 1), repeat=4) if any(v)]
for a, b, c in itertools.product(vectors, repeat=3):
    slack = (measures.cosine_distance(a, b) + measures.cosine_distance(b, c)
             - measures.cosine_distance(a, c))
    if slack < -TOL:
        violations += 1
        worst = min(worst, slack)
print(f"    cosine distance over all {len(vectors)} non-zero 4-bit vectors:")
print(f"    {violations} of {len(vectors) ** 3} triples VIOLATE the inequality")
print(f"    worst violation: {worst:.6f}")
assert violations > 0
print()

print("=" * 74)
print("5. What this actually costs")
print("=" * 74)
print()
print("  Metric  ->  ball trees, KD-trees, cover trees, metric-space pruning,")
print("              and the proof that k-medoids terminates.")
print()
print("  Not a metric  ->  none of those are valid. The usual workaround in")
print("              vector databases is to normalise every vector to length 1")
print("              on the way in; once every vector has length 1, cosine")
print("              similarity and Euclidean distance rank identically:")
print()
print("      ||u - v||^2 = 2 - 2 * cosine(u, v)   when ||u|| = ||v|| = 1")
print()
for pair in ((east, diagonal), (diagonal, north), (east, north)):
    u = [c / measures.l2_norm(pair[0]) for c in pair[0]]
    v = [c / measures.l2_norm(pair[1]) for c in pair[1]]
    lhs = measures.l2_distance(u, v) ** 2
    rhs = 2.0 - 2.0 * measures.cosine_similarity(u, v)
    print(f"      {lhs:.9f}  vs  {rhs:.9f}   difference {abs(lhs - rhs):.2e}")
    assert abs(lhs - rhs) <= 1e-9
print()
print("  So the practical advice is not 'avoid cosine'. It is: normalise on")
print("  the way in, then you get cosine's ranking AND a genuine metric, and")
print("  the index is allowed to prune again.")
print()

print("03_metrics_and_non_metrics.py: every assertion held.")
