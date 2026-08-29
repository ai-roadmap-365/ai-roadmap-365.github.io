"""Section 5 — cosine distance is not a metric, and here is the counter-example.

"Distance" is a word with a technical meaning. A function d is a metric when it
satisfies four conditions:

    1. d(a, b) >= 0                        never negative
    2. d(a, b) = 0 exactly when a = b      identity of indiscernibles
    3. d(a, b) = d(b, a)                   symmetry
    4. d(a, c) <= d(a, b) + d(b, c)        the triangle inequality

Cosine distance satisfies 1, 3 and half of 2, and fails 4. It also fails the
other half of 2, because any two vectors pointing the same way — an article and
its doubled copy — are at distance 0 without being equal, which is exactly the
property that made it useful an hour ago.

The failure of 4 is the one that costs you something. A great deal of fast
search machinery — ball trees, KD-trees, metric indexes, anything that prunes
"this whole branch is too far away to contain the answer" — is built on the
triangle inequality. Feed it a function that fails the inequality and it will
still return answers, and some of them will be wrong, and nothing will say so.

This is not a reason to avoid cosine similarity. It is a reason to normalise
your vectors and hand the index Euclidean distance, which IS a metric, knowing
from section 4 that the ranking is identical.

Run from the examples directory:

    python3 05_not_a_metric.py
"""

from __future__ import annotations

import math

from catalogue import TRIANGLE_A, TRIANGLE_B, TRIANGLE_C
from similarity import (
    angle_degrees,
    cosine_distance,
    cosine_similarity,
    euclidean_distance,
    normalise,
)

TOL = 1e-12


def show_the_counter_example() -> None:
    a, b, c = TRIANGLE_A, TRIANGLE_B, TRIANGLE_C
    print("Three vectors, chosen so every number is exact on paper")
    print()
    print(f"  a = {a}   pointing straight along the first axis")
    print(f"  b = {b}   the bisector, 45 degrees from each")
    print(f"  c = {c}   pointing straight along the second axis")
    print()

    ab = cosine_distance(a, b)
    bc = cosine_distance(b, c)
    ac = cosine_distance(a, c)

    print("Their cosine distances")
    print()
    for label, first, second, value in (
        ("d(a, b)", a, b, ab),
        ("d(b, c)", b, c, bc),
        ("d(a, c)", a, c, ac),
    ):
        print(f"  {label} = 1 - cos = 1 - {cosine_similarity(first, second):.6f}"
              f" = {value:.6f}"
              f"   (angle {angle_degrees(first, second):.1f} degrees)")
    print()
    print(f"  a to b is 1 - 1/sqrt(2) = 1 - {1 / math.sqrt(2):.6f}"
          f" = {1 - 1 / math.sqrt(2):.6f}, and so is b to c.")
    print()

    print("The triangle inequality, tested")
    print()
    print(f"  going the long way round : d(a, b) + d(b, c) = {ab:.6f}"
          f" + {bc:.6f} = {ab + bc:.6f}")
    print(f"  going direct             : d(a, c)            = {ac:.6f}")
    print(f"  is direct <= long way?   : {ac <= ab + bc + TOL}")
    print()
    print(f"  The direct route is longer than the detour, by {ac - (ab + bc):.6f}.")
    print("  That is not a rounding artefact and it is not a bug in the code.")
    print("  It is what 'not a metric' means, in one line of arithmetic.")
    print()
    assert ac > ab + bc + TOL, "cosine distance must fail the triangle inequality here"


def show_euclidean_holds() -> None:
    a, b, c = TRIANGLE_A, TRIANGLE_B, TRIANGLE_C
    print("The same three points under Euclidean distance, which IS a metric")
    print()
    ua, ub, uc = normalise(a), normalise(b), normalise(c)
    print("  On the raw vectors:")
    print(f"    d(a, b) + d(b, c) = {euclidean_distance(a, b):.6f} +"
          f" {euclidean_distance(b, c):.6f} = "
          f"{euclidean_distance(a, b) + euclidean_distance(b, c):.6f}")
    print(f"    d(a, c)           = {euclidean_distance(a, c):.6f}")
    print(f"    holds?            = "
          f"{euclidean_distance(a, c) <= euclidean_distance(a, b) + euclidean_distance(b, c) + TOL}")
    print()
    print("  And on the normalised ones, which is the case that matters,")
    print("  because section 4 said to normalise and then use Euclidean:")
    print(f"    d(a, b) + d(b, c) = {euclidean_distance(ua, ub):.6f} +"
          f" {euclidean_distance(ub, uc):.6f} = "
          f"{euclidean_distance(ua, ub) + euclidean_distance(ub, uc):.6f}")
    print(f"    d(a, c)           = {euclidean_distance(ua, uc):.6f}")
    print(f"    holds?            = "
          f"{euclidean_distance(ua, uc) <= euclidean_distance(ua, ub) + euclidean_distance(ub, uc) + TOL}")
    print()
    assert euclidean_distance(a, c) <= euclidean_distance(a, b) + euclidean_distance(b, c) + TOL
    assert euclidean_distance(ua, uc) <= euclidean_distance(ua, ub) + euclidean_distance(ub, uc) + TOL


def show_the_angle_holds() -> None:
    a, b, c = TRIANGLE_A, TRIANGLE_B, TRIANGLE_C
    print("The angle itself, on the same triple")
    print()
    ab = angle_degrees(a, b)
    bc = angle_degrees(b, c)
    ac = angle_degrees(a, c)
    print(f"  angle(a, b) + angle(b, c) = {ab:.1f} + {bc:.1f} = {ab + bc:.1f} degrees")
    print(f"  angle(a, c)               = {ac:.1f} degrees")
    print(f"  holds, with equality?     = {abs((ab + bc) - ac) < 1e-9}")
    print()
    print("  It holds here, and it holds with equality, because b sits exactly")
    print("  on the shortest path from a to c — the three vectors are in one")
    print("  plane and b is the halfway point. That is the degenerate case of a")
    print("  triangle, a straight line, where the inequality becomes equality.")
    print()
    print("  Being careful about what this does and does not show: one triple")
    print("  where a rule holds is not a proof that it always holds. The angle")
    print("  between two vectors is arc length on the unit sphere, and great-")
    print("  circle distance on a sphere is known to be a metric — but that")
    print("  proof is not in this lab, and this run does not supply it. What")
    print("  this run does supply is the counter-example above, and one")
    print("  counter-example IS a proof, of the negative: cosine distance is")
    print("  not a metric, demonstrated, not asserted.")
    print()
    assert abs((ab + bc) - ac) < 1e-9


def show_the_identity_failure() -> None:
    print("The other condition it fails, and why you wanted it to")
    print()
    short = [9, 0, 1, 0]
    doubled = [18, 0, 2, 0]
    distance = cosine_distance(short, doubled)
    print(f"  d({short}, {doubled}) = {distance:.6f}")
    print(f"  are the two vectors equal? {short == doubled}")
    print()
    print("  A metric must have d(a, b) = 0 only when a and b are the same")
    print("  point. Cosine distance gives 0 for every pair on the same ray from")
    print("  the origin. That is a failure of the definition and the entire")
    print("  reason the measure is useful for text: 'same direction' and 'same")
    print("  vector' are different claims, and for documents you want the first")
    print("  one. The measure is not broken. It is answering the question you")
    print("  asked, and that question was never 'are these the same point'.")
    print()
    assert abs(distance) < TOL
    assert short != doubled


def main() -> int:
    show_the_counter_example()
    show_euclidean_holds()
    show_the_angle_holds()
    show_the_identity_failure()
    print("05_not_a_metric.py: every assertion held.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
