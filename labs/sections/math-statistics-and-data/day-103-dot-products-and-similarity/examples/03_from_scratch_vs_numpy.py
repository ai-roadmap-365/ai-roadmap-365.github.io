"""Section 3 — fifteen lines of pure Python, checked against NumPy line by line.

Everything today's lesson claims comes out of three functions, and all three
fit on one screen:

    dot(a, b)               = sum(x*y for x, y in zip(a, b))
    cosine_similarity(a, b) = dot(a, b) / (l2_norm(a) * l2_norm(b))
    cosine_distance(a, b)   = 1 - cosine_similarity(a, b)

This script runs each of them against NumPy's own machinery on every pair in
the catalogue and asserts agreement to a stated tolerance, so that "my version
matches the library" is a measurement rather than a hope. It then shows the
three places where the from-scratch version and the library version genuinely
differ — which is worth more than the agreement, because those are the places
where a real implementation goes wrong.

Run from the examples directory:

    python3 03_from_scratch_vs_numpy.py
"""

from __future__ import annotations

import math

import numpy as np

from catalogue import CATALOGUE
from similarity import (
    angle_degrees,
    cosine_distance,
    cosine_similarity,
    dot,
    l2_norm,
    normalise,
)

TOL = 1e-12


def numpy_cosine(a, b) -> float:
    """The same formula in NumPy, written out rather than imported."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def show_every_pair_agrees() -> None:
    print("Every pair in the catalogue, mine against NumPy's")
    print()
    labels = list(CATALOGUE)
    header = (f"  {'pair':<40}{'dot':>8}{'mine':>12}{'numpy':>12}"
              f"{'difference':>14}")
    print(header)
    print("  " + "-" * (len(header) - 2))
    worst = 0.0
    pairs = 0
    for i, first in enumerate(labels):
        for second in labels[i + 1:]:
            a, b = CATALOGUE[first], CATALOGUE[second]
            mine = cosine_similarity(a, b)
            theirs = numpy_cosine(a, b)
            gap = abs(mine - theirs)
            worst = max(worst, gap)
            pairs += 1
            print(f"  {first + ' / ' + second:<40}{dot(a, b):>8.0f}"
                  f"{mine:>12.6f}{theirs:>12.6f}{gap:>14.2e}")
            assert gap < TOL, (first, second, mine, theirs)
    print()
    print(f"  {pairs} pairs, largest disagreement {worst:.2e}, tolerance {TOL:.0e}")
    print()
    print("  Note that this is agreement, not identity. The two implementations")
    print("  add the products up in the same order here, so they happen to")
    print("  produce bit-identical answers, but nothing guarantees that in")
    print("  general — NumPy is free to reorder a summation for speed, and")
    print("  floating-point addition is not associative (Day 70). Compare with")
    print("  a tolerance, always.")
    print()


def show_the_three_equivalent_routes() -> None:
    a = CATALOGUE["roast-chicken"]
    b = CATALOGUE["race-day-nutrition"]
    print("Three routes to the same cosine similarity")
    print()
    direct = dot(a, b) / (l2_norm(a) * l2_norm(b))
    via_units = dot(normalise(a), normalise(b))
    via_numpy = float(np.dot(normalise(a), normalise(b)))
    print(f"  divide the dot product by both lengths : {direct:.15f}")
    print(f"  dot product of the two UNIT vectors    : {via_units:.15f}")
    print(f"  the same, through numpy.dot            : {via_numpy:.15f}")
    print()
    assert abs(direct - via_units) < TOL
    assert abs(via_units - via_numpy) < TOL
    print("  The second route is the one that matters in practice. Normalise")
    print("  every vector ONCE when you store it, and every later comparison is")
    print("  a bare dot product with no square roots in it at all. That is what")
    print("  a vector index does, and it is why 'dot product' and 'cosine' are")
    print("  offered as separate options by systems that store embeddings: on")
    print("  already-normalised vectors they are the same thing, and the dot")
    print("  product is cheaper.")
    print()


def show_the_edges() -> None:
    print("Three places where the naive formula needs care")
    print()

    print("  1. The zero vector. It has no direction, so the angle to it does")
    print("     not exist, and the formula divides by zero.")
    zero = [0, 0, 0, 0]
    with np.errstate(invalid="ignore", divide="ignore"):
        naive = np.dot(zero, CATALOGUE["roast-chicken"]) / (
            np.linalg.norm(zero) * np.linalg.norm(CATALOGUE["roast-chicken"])
        )
    print(f"     written out in NumPy without a guard : {naive}")
    try:
        cosine_similarity(zero, CATALOGUE["roast-chicken"])
    except ValueError as exc:
        print(f"     this lab's version                   : ValueError: {exc}")
    else:  # pragma: no cover - the guard is asserted below
        raise AssertionError("cosine_similarity must refuse the zero vector")
    print("     A NaN sorts unpredictably and spreads through every average it")
    print("     touches. Raise instead. An empty document is a real thing that")
    print("     happens, and it should stop the pipeline, not poison it.")
    print()

    print("  2. Rounding past 1. Compare a vector with ITSELF and the answer")
    print("     should be exactly 1.0. Here is what it actually is, unclamped,")
    print("     for all six articles — plain integer counts, nothing exotic:")
    print()
    print(f"     {'article':<22}{'unclamped (a dot a) / (|a| |a|)':>36}")
    print("     " + "-" * 57)
    over = []
    under = []
    for label, vector in CATALOGUE.items():
        length = math.sqrt(sum(x * x for x in vector))
        unclamped = sum(x * y for x, y in zip(vector, vector)) / (length * length)
        print(f"     {label:<22}{unclamped!r:>36}")
        if unclamped > 1.0:
            over.append((label, unclamped))
        elif unclamped < 1.0:
            under.append((label, unclamped))
    print()
    print(f"     exactly 1.0 : {6 - len(over) - len(under)} of 6")
    print(f"     just under  : {len(under)} of 6")
    print(f"     just over   : {len(over)} of 6")
    print()
    assert over, "at least one article should round above 1.0"
    label, unclamped = over[0]
    print(f"     The one that rounds UP is {label}, at {unclamped!r},")
    print("     and that single bit of rounding is fatal downstream:")
    try:
        math.acos(unclamped)
    except ValueError as exc:
        print(f"       math.acos({unclamped!r}) -> ValueError: {exc}")
    else:  # pragma: no cover - the domain error is the point
        raise AssertionError("acos above 1.0 should raise")
    vector = CATALOGUE[label]
    print(f"       clamped, this lab gives {cosine_similarity(vector, vector)!r}")
    print(f"       and an angle of {angle_degrees(vector, vector):.1f} degrees")
    print()
    print("     Half a dozen four-component integer vectors were enough to")
    print("     produce this, which is the point: it is not an exotic case you")
    print("     will meet once. Any code that turns a similarity into an angle,")
    print("     or asserts a score is at most 1.0, clamps first. This lab")
    print("     clamps, and every reported similarity below is a clamped one.")
    assert unclamped > 1.0
    assert cosine_similarity(vector, vector) == 1.0
    print()

    print("  3. Mismatched lengths. Two vectors of different sizes cannot be")
    print("     compared, and the failure should be loud.")
    try:
        dot([1, 2, 3], [1, 2])
    except ValueError as exc:
        print(f"     this lab's version : ValueError: {exc}")
    else:  # pragma: no cover
        raise AssertionError("dot must refuse mismatched lengths")
    try:
        np.array([1, 2, 3]) @ np.array([1, 2])
    except ValueError as exc:
        print(f"     NumPy              : ValueError: {exc}")
    else:  # pragma: no cover
        raise AssertionError("numpy must refuse mismatched lengths")
    print("     Both raise ValueError, which is deliberate: one except clause")
    print("     catches either implementation.")
    print()


def show_cosine_distance() -> None:
    print("Cosine distance is just 1 minus the similarity")
    print()
    header = f"  {'pair':<40}{'similarity':>12}{'distance':>12}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    examples = [
        ("roast-chicken", "roast-chicken"),
        ("roast-chicken", "slow-cooker-stew"),
        ("roast-chicken", "race-day-nutrition"),
        ("roast-chicken", "storm-bulletin"),
    ]
    for first, second in examples:
        a, b = CATALOGUE[first], CATALOGUE[second]
        print(f"  {first + ' / ' + second:<40}{cosine_similarity(a, b):>12.6f}"
              f"{cosine_distance(a, b):>12.6f}")
    opposed = cosine_distance([1, 0], [-1, 0])
    print(f"  {'[1, 0] / [-1, 0] (opposite directions)':<40}"
          f"{cosine_similarity([1, 0], [-1, 0]):>12.6f}{opposed:>12.6f}")
    print()
    print("  The range is 0 to 2, not 0 to 1 — because similarity runs from 1")
    print("  down to -1. On count vectors, where nothing is ever negative, no")
    print("  pair can be more than 90 degrees apart, so the distance never")
    print("  exceeds 1 and 'orthogonal' is as far apart as two articles get.")
    print("  Embeddings from a trained model DO have negative components, and")
    print("  there the upper half of the range is reachable.")
    print()
    assert abs(opposed - 2.0) < TOL
    assert all(
        cosine_distance(CATALOGUE[a], CATALOGUE[b]) <= 1.0 + TOL
        for a in CATALOGUE
        for b in CATALOGUE
    )


def main() -> int:
    show_every_pair_agrees()
    show_the_three_equivalent_routes()
    show_the_edges()
    show_cosine_distance()
    print("03_from_scratch_vs_numpy.py: every assertion held.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
