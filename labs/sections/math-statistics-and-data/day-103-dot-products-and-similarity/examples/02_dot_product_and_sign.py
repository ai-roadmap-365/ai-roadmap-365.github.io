"""Section 2 — what the dot product IS, and what its sign tells you.

Day 101 computed dot products mechanically: multiply component by component,
add up the results. That is correct and it is not an explanation. Today the
same number gets its geometric meaning:

    a dot b = |a| |b| cos(theta)

Read that right to left and it says: the dot product is how much of one vector
lies along the other, scaled by both lengths. Read the sign alone and it says
something simpler and immediately useful — positive means the angle is under
90 degrees, zero means exactly 90, negative means over 90.

Run from the examples directory:

    python3 02_dot_product_and_sign.py
"""

from __future__ import annotations

import math

from catalogue import PROJECTION_A, PROJECTION_B, SIGN_CASES
from similarity import (
    angle_degrees,
    cosine_similarity,
    dot,
    l2_norm,
    scalar_projection,
    vector_projection,
)

TOL = 1e-9


def show_the_two_definitions_agree() -> None:
    a, b = PROJECTION_A, PROJECTION_B
    print("The algebraic definition and the geometric one are the same number")
    print()
    print(f"  a = {a}   |a| = {l2_norm(a):.4f}   (a 3-4-5 triangle, so exactly 5)")
    print(f"  b = {b}   |b| = {l2_norm(b):.4f}")
    print()
    products = [x * y for x, y in zip(a, b)]
    print("  Algebraic: multiply component by component, then add.")
    print(f"      {a[0]}*{b[0]} + {a[1]}*{b[1]} = {products[0]} + {products[1]}"
          f" = {dot(a, b):.0f}")
    print()
    theta = angle_degrees(a, b)
    cos_theta = cosine_similarity(a, b)
    print("  Geometric: |a| |b| cos(theta).")
    print(f"      theta = {theta:.4f} degrees, cos(theta) = {cos_theta:.4f}")
    print(f"      {l2_norm(a):.0f} * {l2_norm(b):.0f} * {cos_theta:.4f}"
          f" = {l2_norm(a) * l2_norm(b) * cos_theta:.4f}")
    print()
    assert abs(dot(a, b) - l2_norm(a) * l2_norm(b) * cos_theta) < TOL
    print("  Same number, reached two ways. The algebraic route is what a")
    print("  computer runs; the geometric route is what it means.")
    print()


def show_the_projection() -> None:
    a, b = PROJECTION_A, PROJECTION_B
    print("The projection picture: how much of b lies along a")
    print()
    shadow_length = scalar_projection(a, b)
    shadow = vector_projection(a, b)
    print("  Shine a light straight down onto a's direction. b casts a shadow.")
    print(f"      length of the shadow = (a dot b) / |a| = {dot(a, b):.0f} /"
          f" {l2_norm(a):.0f} = {shadow_length:.4f}")
    print(f"      the shadow as a vector = [{', '.join(f'{x:.4f}' for x in shadow)}]")
    print(f"      its length             = {l2_norm(shadow):.4f}")
    print()
    assert abs(l2_norm(shadow) - shadow_length) < TOL
    print(f"  Check it the other way: |b| cos(theta) = {l2_norm(b):.0f} *"
          f" {cosine_similarity(a, b):.4f} = {l2_norm(b) * cosine_similarity(a, b):.4f}")
    print()
    assert abs(l2_norm(b) * cosine_similarity(a, b) - shadow_length) < TOL

    other_way = scalar_projection(b, a)
    print("  The projection is NOT symmetric. Projecting a onto b instead:")
    print(f"      (b dot a) / |b| = {dot(b, a):.0f} / {l2_norm(b):.0f}"
          f" = {other_way:.4f}")
    print(f"  The dot product does not care about order — {dot(a, b):.0f} either")
    print("  way — but the shadow does, because you have chosen a different")
    print("  surface to cast it on.")
    print()
    assert abs(dot(a, b) - dot(b, a)) < TOL
    assert abs(other_way - shadow_length) > TOL

    print("  And the special case that ties Day 99 to today: project a onto")
    print("  itself and the shadow is the whole vector.")
    print(f"      (a dot a) / |a| = {dot(a, a):.0f} / {l2_norm(a):.0f}"
          f" = {scalar_projection(a, a):.4f} = |a|")
    print(f"      so |a| = sqrt(a dot a) = sqrt({dot(a, a):.0f}) = {l2_norm(a):.4f}")
    print()
    assert abs(scalar_projection(a, a) - l2_norm(a)) < TOL
    assert abs(math.sqrt(dot(a, a)) - l2_norm(a)) < TOL


def show_the_sign_cases() -> None:
    print("What the sign tells you, one worked example of each")
    print()
    header = (f"  {'case':<20}{'a':>10}{'b':>10}{'a.b':>8}"
              f"{'cos':>10}{'angle':>10}{'sign':>11}")
    print(header)
    print("  " + "-" * (len(header) - 2))
    for label, a, b, expected_sign in SIGN_CASES:
        value = dot(a, b)
        actual_sign = "positive" if value > 0 else ("zero" if value == 0 else "negative")
        assert actual_sign == expected_sign, (label, value, expected_sign)
        print(f"  {label:<20}{str(a):>10}{str(b):>10}{value:>8.0f}"
              f"{cosine_similarity(a, b):>10.4f}{angle_degrees(a, b):>10.2f}"
              f"{actual_sign:>11}")
    print()
    print("  Read the middle two columns together and the rule falls out:")
    print()
    print("    dot > 0  <->  cos > 0  <->  angle under 90 degrees   (agreeing)")
    print("    dot = 0  <->  cos = 0  <->  angle exactly 90 degrees (unrelated)")
    print("    dot < 0  <->  cos < 0  <->  angle over 90 degrees    (opposing)")
    print()
    print("  The sign of the dot product and the sign of the cosine are always")
    print("  the same, because the two lengths you divide by are never negative.")
    print("  So if all you need is the DIRECTION of the relationship, the raw")
    print("  dot product answers it and you can skip both square roots.")
    print()


def show_orthogonality_in_the_catalogue() -> None:
    from catalogue import CATALOGUE

    print("Orthogonality is not an abstraction: three pairs in the catalogue have it")
    print()
    labels = list(CATALOGUE)
    found = []
    for i, first in enumerate(labels):
        for second in labels[i + 1:]:
            value = dot(CATALOGUE[first], CATALOGUE[second])
            if value == 0:
                found.append((first, second))
    for first, second in found:
        print(f"  {first} . {second} = 0")
        pairs = " + ".join(
            f"{x}*{y}" for x, y in zip(CATALOGUE[first], CATALOGUE[second])
        )
        print(f"      {pairs} = 0")
        print(f"      cosine similarity {cosine_similarity(CATALOGUE[first], CATALOGUE[second]):.4f},"
              f" angle {angle_degrees(CATALOGUE[first], CATALOGUE[second]):.2f} degrees")
    print()
    assert ("roast-chicken", "storm-bulletin") in found
    print("  Every product in that sum is zero because wherever one article has")
    print("  a count the other has none. They share no vocabulary at all, and")
    print("  orthogonal is exactly what that means: not opposed, just entirely")
    print("  unrelated. Nothing you learn about one tells you anything about")
    print("  the other.")
    print()


def main() -> int:
    show_the_two_definitions_agree()
    show_the_projection()
    show_the_sign_cases()
    show_orthogonality_in_the_catalogue()
    print("02_dot_product_and_sign.py: every assertion held.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
