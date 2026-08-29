"""Section 4 — on normalised vectors the two measures rank identically.

This is the most useful fact in the day, and it is the one most often stated
without proof. Here it is proved twice: once with algebra you can follow with a
pen, and once by ranking the whole catalogue both ways and asserting the orders
match.

The algebra, for two UNIT vectors u and v:

    |u - v|^2 = (u - v) dot (u - v)
              = u dot u  -  2 (u dot v)  +  v dot v
              = 1 - 2 (u dot v) + 1
              = 2 - 2 cos(theta)

so                                    Euclidean distance = sqrt(2 - 2 cos)

Cosine goes up, the bracket goes down, the square root goes down. The distance
is a strictly decreasing function of the similarity, so sorting by one gives
exactly the reverse of sorting by the other. Not approximately. Exactly.

That is why a vector database normalises its vectors on the way in and then
uses whichever comparison its hardware runs fastest: on the unit sphere the
choice is a performance decision, not a semantic one.

Run from the examples directory:

    python3 04_same_ranking_on_the_sphere.py
"""

from __future__ import annotations

import math

from catalogue import CATALOGUE, LONG_ROAST_CHICKEN
from similarity import (
    cosine_similarity,
    euclidean_distance,
    normalise,
    normalise_all,
    rank_by_cosine,
    rank_by_euclidean,
)

TOL = 1e-12


def show_the_identity() -> None:
    print("The identity, checked on every pair in the catalogue")
    print()
    units = normalise_all(CATALOGUE)
    labels = list(units)
    header = (f"  {'pair':<40}{'cos':>10}{'sqrt(2-2cos)':>14}"
              f"{'|u - v|':>12}{'gap':>12}")
    print(header)
    print("  " + "-" * (len(header) - 2))
    worst = 0.0
    for i, first in enumerate(labels):
        for second in labels[i + 1:]:
            u, v = units[first], units[second]
            cos = cosine_similarity(u, v)
            predicted = math.sqrt(2 - 2 * cos)
            measured = euclidean_distance(u, v)
            gap = abs(predicted - measured)
            worst = max(worst, gap)
            print(f"  {first + ' / ' + second:<40}{cos:>10.6f}{predicted:>14.6f}"
                  f"{measured:>12.6f}{gap:>12.2e}")
            assert gap < TOL
    print()
    print(f"  Largest gap between the formula and the measurement: {worst:.2e}")
    print()


def show_the_rankings_match() -> None:
    print("Rank the catalogue both ways, from the same query, after normalising")
    print()
    query = CATALOGUE["roast-chicken"]
    unit_query = normalise(query)
    units = normalise_all(CATALOGUE)

    by_cosine = rank_by_cosine(unit_query, units)
    by_euclid = rank_by_euclidean(unit_query, units)

    header = (f"  {'rank':<6}{'by cosine (high first)':<26}{'sim':>10}   "
              f"{'by distance (low first)':<26}{'dist':>10}")
    print(header)
    print("  " + "-" * (len(header) - 2))
    for position, (left, right) in enumerate(zip(by_cosine, by_euclid), start=1):
        print(f"  {position:<6}{left[0]:<26}{left[1]:>10.6f}   "
              f"{right[0]:<26}{right[1]:>10.6f}")
    print()
    cosine_order = [label for label, _ in by_cosine]
    euclid_order = [label for label, _ in by_euclid]
    print(f"  the two orders are identical : {cosine_order == euclid_order}")
    print()
    assert cosine_order == euclid_order

    print("  Now the same comparison WITHOUT normalising, to show what the")
    print("  normalisation was doing. The doubled copy of roast-chicken is")
    print("  added so the length difference is real:")
    print()
    raw = dict(CATALOGUE)
    raw["roast-chicken (2x)"] = LONG_ROAST_CHICKEN
    raw_cosine = [label for label, _ in rank_by_cosine(query, raw)]
    raw_euclid = [label for label, _ in rank_by_euclidean(query, raw)]
    print(f"    by cosine   : {', '.join(raw_cosine)}")
    print(f"    by distance : {', '.join(raw_euclid)}")
    print(f"    identical?  : {raw_cosine == raw_euclid}")
    print()
    assert raw_cosine != raw_euclid
    print("  So the claim is precise and worth stating precisely: the two")
    print("  measures agree on NORMALISED vectors and can disagree on raw ones.")
    print("  Normalising is not a tidying step you do out of habit. It is the")
    print("  step that makes the two measures interchangeable, and if you skip")
    print("  it, which one you picked changes the answers.")
    print()


def show_the_monotone_curve() -> None:
    print("The curve behind the claim, sampled")
    print()
    print(f"  {'cosine':>10}{'distance on the unit sphere':>30}{'angle':>10}")
    print("  " + "-" * 48)
    previous = None
    for cos in (1.0, 0.9, 0.5, 0.0, -0.5, -0.9, -1.0):
        distance = math.sqrt(2 - 2 * cos)
        angle = math.degrees(math.acos(cos))
        print(f"  {cos:>10.1f}{distance:>30.6f}{angle:>10.1f}")
        if previous is not None:
            assert distance > previous, "distance must rise as cosine falls"
        previous = distance
    print()
    print("  Every step down in cosine is a step up in distance, with no")
    print("  exceptions and no flat stretches. Two unit vectors pointing the")
    print("  same way are 0 apart; perpendicular ones are sqrt(2) = 1.414214")
    print("  apart; opposite ones are 2 apart, which is the diameter of the")
    print("  sphere and the furthest two unit vectors can get.")
    print()
    print("  What this does NOT say: the two measures produce the same SCORES.")
    print("  They do not, and a threshold tuned for one is meaningless for the")
    print("  other. A cut-off of 'similarity above 0.9' is 'distance below")
    print(f"  {math.sqrt(2 - 2 * 0.9):.6f}', and nothing about the second number is")
    print("  guessable from the first. Only the ORDER is preserved.")
    print()


def main() -> int:
    show_the_identity()
    show_the_rankings_match()
    show_the_monotone_curve()
    print("04_same_ranking_on_the_sphere.py: every assertion held.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
