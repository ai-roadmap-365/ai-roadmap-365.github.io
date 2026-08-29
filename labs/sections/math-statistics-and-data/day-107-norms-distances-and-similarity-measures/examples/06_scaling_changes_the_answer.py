"""The units in your table decide your answer, and nobody voted on them.

Run from the `examples/` directory:

    ../.venv/bin/python3 06_scaling_changes_the_answer.py

Every distance in this lab sums contributions across features. Nothing in that
sum knows that one column is in metres and another in grams, so the column with
the bigger numbers wins the argument -- not by being more important, but by
being written down in smaller units.
"""

from __future__ import annotations

import numpy as np

import catalogue
import measures
from measures import TOL

B = catalogue.BEARINGS
Q = catalogue.BEARING_QUERY
ROWS = list(B.values())

print("=" * 74)
print("1. A bearing catalogue in the units the supplier used")
print("=" * 74)
print()
print(f"    {'part':<8}{catalogue.BEARING_FEATURES[0]:>22}"
      f"{catalogue.BEARING_FEATURES[1]:>14}")
print("    " + "-" * 44)
print(f"    {'WANTED':<8}{Q[0]:>22.3f}{Q[1]:>14.1f}")
print("    " + "-" * 44)
for name, row in B.items():
    print(f"    {name:<8}{row[0]:>22.3f}{row[1]:>14.1f}")
print()
print("  Bore diameter is recorded in METRES, so every number in that column")
print("  is about 0.02. Mass is in GRAMS, so every number in that one is in")
print("  the hundreds. Both columns matter to an engineer. Only one of them")
print("  is going to matter to a Euclidean distance.")
print()

print("=" * 74)
print("2. Rank on the raw numbers")
print("=" * 74)
print()
raw = measures.rank(Q, B, measures.l2_distance)
head2 = (f"    {'part':<8}{'distance':>14}{'bore term':>16}"
         f"{'mass term':>16}{'bore share':>13}")
print(head2)
print("    " + "-" * (len(head2) - 4))
for name, d in raw:
    bore = (Q[0] - B[name][0]) ** 2
    mass = (Q[1] - B[name][1]) ** 2
    share = bore / (bore + mass) if bore + mass else 0.0
    print(f"    {name:<8}{d:>14.6f}{bore:>16.2e}{mass:>16.2f}{share:>12.6%}")
print()
raw_winner = raw[0][0]
print(f"  Winner: {raw_winner}")
assert raw_winner == "R"
print()
print("  Look at the last column. The bore diameter contributes less than one")
print("  ten-thousandth of one per cent of every distance in the table. This")
print("  is not a ranking on two features. It is a ranking on mass, with a")
print("  rounding error attached.")
print()
print(f"  And R is unusable. The query wants a {Q[0] * 1000:.0f} mm bore; R has "
      f"a {B['R'][0] * 1000:.0f} mm bore,")
print("  60 per cent oversize, a part that will not fit the shaft. It wins")
print("  because it is 2 g from the target mass, and mass is the only thing")
print("  being measured.")
print()
print(f"  P has EXACTLY the bore asked for and comes "
      f"{[n for n, _ in raw].index('P') + 1} of {len(raw)}.")
print()

print("=" * 74)
print("3. The same ranking after standardising")
print("=" * 74)
print()
means = measures.column_means(ROWS)
stds = measures.column_stds(ROWS)
print(f"    column means               {[round(m, 6) for m in means]}")
print(f"    column standard deviations {[round(s, 6) for s in stds]}")
print()
print("  The query is standardised with the CATALOGUE's numbers, not its own.")
print("  Standardising a single row against itself gives a row of zeros, which")
print("  is a mistake with a long history in production retrieval systems.")
print()

q_std = measures.standardise([Q], means, stds)[0]
b_std = {name: measures.standardise([row], means, stds)[0]
         for name, row in B.items()}
print(f"    {'part':<8}{'bore (z)':>12}{'mass (z)':>12}{'distance':>14}")
print("    " + "-" * 46)
scaled = measures.rank(q_std, b_std, measures.l2_distance)
print(f"    {'WANTED':<8}{q_std[0]:>12.4f}{q_std[1]:>12.4f}")
for name, d in scaled:
    print(f"    {name:<8}{b_std[name][0]:>12.4f}{b_std[name][1]:>12.4f}"
          f"{d:>14.6f}")
print()
scaled_winner = scaled[0][0]
print(f"  Winner: {scaled_winner}")
assert scaled_winner == "P"
assert scaled_winner != raw_winner
print()
print(f"  The winner changed from {raw_winner} to {scaled_winner}. Same six")
print("  parts, same query, same Euclidean distance, same code. The only")
print("  thing that changed is that both columns now speak in standard")
print("  deviations of the catalogue, so a 12 mm bore error costs what a 12 mm")
print("  bore error is worth rather than what it looks like next to 40 grams.")
print()
print(f"    {'part':<8}{'raw rank':>11}{'standardised rank':>20}{'moved':>8}")
print("    " + "-" * 47)
raw_order = [n for n, _ in raw]
std_order = [n for n, _ in scaled]
moved = 0
for name in B:
    a, c = raw_order.index(name) + 1, std_order.index(name) + 1
    if a != c:
        moved += 1
    print(f"    {name:<8}{a:>11}{c:>20}{('yes' if a != c else '-'):>8}")
print()
print(f"  {moved} of the {len(B)} parts moved -- and they are the two the")
print("  decision is between. P and R swap places, first for third.")
assert moved == 2
assert (raw_order.index("P"), std_order.index("P")) == (2, 0)
assert (raw_order.index("R"), std_order.index("R")) == (0, 2)
print()

print("=" * 74)
print("4. It is the UNITS, not the standardising")
print("=" * 74)
print()
print("  The clearest proof that the raw ranking was an artefact: change no")
print("  data at all, only the unit the bore column is written in.")
print()
for label, factor in (("metres", 1.0), ("millimetres", 1e3),
                      ("micrometres", 1e6)):
    q_u = (Q[0] * factor, Q[1])
    b_u = {n: (v[0] * factor, v[1]) for n, v in B.items()}
    order = [n for n, _ in measures.rank(q_u, b_u, measures.l2_distance)]
    print(f"    bore in {label:<13} {order}")
    if label == "micrometres":
        assert order[0] == "P"
    if label == "metres":
        assert order[0] == "R"
print()
print("  In metres the answer is R. In micrometres the answer is P. The parts")
print("  did not change; a column header did. Any pipeline that does not")
print("  normalise is quietly letting whoever chose the units decide the")
print("  ranking, and that person was usually not thinking about distances.")
print()

print("=" * 74)
print("5. Standardising is not the only choice, and it is not free")
print("=" * 74)
print()
lo = [min(r[j] for r in ROWS) for j in range(len(ROWS[0]))]
hi = [max(r[j] for r in ROWS) for j in range(len(ROWS[0]))]


def min_max(row):
    return [(row[j] - lo[j]) / (hi[j] - lo[j]) for j in range(len(row))]


mm_order = [n for n, _ in measures.rank(
    min_max(Q), {n: min_max(v) for n, v in B.items()}, measures.l2_distance)]
print(f"    z-score (mean 0, sd 1)     {std_order}")
print(f"    min-max (squashed to 0-1) {mm_order}")
assert mm_order[0] == "P"
print()
print("  Both agree here, which will not always happen. The trade-off:")
print()
print("    z-score   assumes nothing about the range, so an outlier stretches")
print("              the standard deviation and squashes everything else")
print("              toward zero. Handles unbounded features.")
print()
print("    min-max   pins the range to 0-1 exactly, which is what an image")
print("              pipeline usually wants -- and one outlier now decides the")
print("              WHOLE scale, and a value outside the training range comes")
print("              out above 1 or below 0.")
print()
print("  There is a third answer that people forget: do not scale, and choose")
print("  a measure that does not need it. Mahalanobis divides by the data's")
print("  own spread as part of its definition, so it needs no scaling step at")
print("  all -- and it does NOT give the same answer, which is worth more than")
print("  if it had:")
print()
cov_inv = measures.inverse(measures.covariance_matrix(ROWS))
maha_order = [n for n, _ in measures.rank(
    Q, B, lambda a, b: measures.mahalanobis_distance(a, b, cov_inv))]
print(f"    Mahalanobis on the RAW numbers  {maha_order}")
print(f"    z-score then Euclidean          {std_order}")
print(f"    raw Euclidean                   {raw_order}")
assert maha_order[0] == "U"
assert maha_order[1] == "P"
assert maha_order.index("R") == 4
print()
print("  Both cures demote the unusable part: R falls from 1st to 3rd under")
print("  standardising and to 5th under Mahalanobis. They disagree at the top,")
print("  where Mahalanobis prefers U and standardising prefers P.")
print()
print("  The disagreement is not noise, and it is the reason to know both.")
print("  In this catalogue bore and mass are correlated -- bigger bearings are")
print("  heavier -- and Mahalanobis removes that shared movement before")
print("  measuring, while standardising only rescales each column separately.")
print()
cov_raw = measures.covariance_matrix(ROWS)
corr = cov_raw[0][1] / (stds[0] * stds[1])
print(f"    correlation between bore and mass: {corr:+.4f}")
assert corr > 0.7
print()
print("  P is close to the query in bore and 40 g heavy. Once you know that")
print("  heavier goes with wider in this catalogue, being wide-for-its-mass or")
print("  heavy-for-its-bore is the surprising thing, and U -- which is smaller")
print("  and lighter TOGETHER, along the grain -- reads as the nearer part.")
print("  Whether you want that is a modelling decision, which is the day's")
print("  entire subject.")
print()

print("=" * 74)
print("6. Is this catalogue cherry-picked? A seeded sweep says no")
print("=" * 74)
print()
print("  Six parts and one query were chosen by hand to make the point")
print("  legible. Here is the same experiment on random catalogues, drawn")
print("  from numpy.random.default_rng(107) -- a SEEDED generator, so this")
print("  run reproduces on this machine, and the claim asserted below is a")
print("  RANGE rather than an exact count, because NumPy does not promise")
print("  that a generator's stream survives a version change.")
print()
rng = np.random.default_rng(107)
TRIALS = 2000
spread = np.array([0.04, 500.0])
flips = 0
for _ in range(TRIALS):
    cat = rng.random((6, 2)) * spread
    query = rng.random(2) * spread
    raw_best = int(np.argmin(np.linalg.norm(cat - query, axis=1)))
    mu, sd = cat.mean(axis=0), cat.std(axis=0)
    std_best = int(np.argmin(
        np.linalg.norm((cat - mu) / sd - (query - mu) / sd, axis=1)))
    flips += raw_best != std_best
print(f"    {TRIALS} random catalogues, same two units")
print(f"    the winner changed after standardising in {flips} of them"
      f"  ({flips / TRIALS:.1%})")
print()
assert 0.35 <= flips / TRIALS <= 0.75, flips
print("  Between a third and three quarters, every time this has been run.")
print("  Standardising is not a tweak that occasionally matters. On features")
print("  in mismatched units it decides the answer about half the time.")
print()

print("=" * 74)
print("7. Where cosine sits in this")
print("=" * 74)
print()
print("  Cosine similarity is often described as 'scale invariant', and that")
print("  is true of the wrong scale. It ignores the length of a VECTOR. It")
print("  does not ignore the units of a COLUMN, and it cannot, because")
print("  changing one column's units rotates every vector in the table.")
print()
for label, factor in (("metres", 1.0), ("micrometres", 1e6)):
    q_u = (Q[0] * factor, Q[1])
    b_u = {n: (v[0] * factor, v[1]) for n, v in B.items()}
    order = [n for n, _ in measures.rank(q_u, b_u, measures.cosine_similarity,
                                         higher_is_better=True)]
    print(f"    cosine, bore in {label:<13} {order}")
    if label == "metres":
        cosine_metres = order
    else:
        cosine_micro = order
assert cosine_metres != cosine_micro
print()
print("  Different order, same data. 'Scale invariant' is a claim about")
print("  multiplying a whole vector by a constant, and it is worth knowing")
print("  exactly that much and no more.")
print()
doubled = {n: tuple(2 * c for c in v) for n, v in B.items()}
same = measures.rank(Q, doubled, measures.cosine_similarity,
                     higher_is_better=True)
assert [n for n, _ in same] == cosine_metres
print("  What it IS invariant to, checked: doubling every candidate vector")
print("  leaves the cosine ranking untouched.")
print()
worst = max(abs(measures.cosine_similarity(Q, doubled[n])
                - measures.cosine_similarity(Q, B[n])) for n in B)
print(f"    largest change in any cosine score: {worst:.3e}"
      f"   (tolerance {TOL:.0e})")
assert worst <= TOL
print()

print("06_scaling_changes_the_answer.py: every assertion held.")
