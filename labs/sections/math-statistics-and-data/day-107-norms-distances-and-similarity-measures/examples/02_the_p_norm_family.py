"""The p-norm family, and the picture that makes it click: three unit balls.

Run from the `examples/` directory:

    ../.venv/bin/python3 02_the_p_norm_family.py

L1, L2 and L-infinity are not three unrelated ideas. They are one formula with
one dial turned to three settings, and the clearest way to see the difference
is to draw the set of points each one calls "distance 1 from the origin".
A diamond, a circle, a square.
"""

from __future__ import annotations

import math

import numpy as np

import catalogue
import measures
from measures import TOL

V = (3.0, 4.0)

print("=" * 74)
print("1. One formula, one dial")
print("=" * 74)
print()
print("    p_norm(v, p) = (sum of |x| ** p) ** (1 / p)")
print()
print(f"  On the vector v = {V}, which is the 3-4-5 triangle, so the")
print("  p = 2 answer is a whole number and you can check it in your head:")
print()
print(f"    {'p':>8}{'||v||_p':>14}   note")
print("    " + "-" * 52)
notes = {
    1: "sum of |x|: 3 + 4",
    2: "the one geometry gives you",
    math.inf: "the largest single component",
}
sweep = [1, 1.5, 2, 3, 4, 8, 16, 64, math.inf]
values = []
for p in sweep:
    n = measures.p_norm(V, p)
    values.append(n)
    label = "inf" if math.isinf(p) else f"{p:g}"
    print(f"    {label:>8}{n:>14.6f}   {notes.get(p, '')}".rstrip())
print()

assert measures.p_norm(V, 1) == 7.0
assert measures.p_norm(V, 2) == 5.0
assert measures.p_norm(V, math.inf) == 4.0

print("  The value falls as p rises, and never below the largest component.")
print("  That is not a coincidence: raising a bigger number to a bigger power")
print("  makes it dominate the sum, so in the limit only the biggest survives.")
print()
for earlier, later in zip(values, values[1:]):
    assert later <= earlier + TOL, (earlier, later)
assert all(v >= measures.linf_norm(V) - TOL for v in values)
assert abs(values[-1] - measures.linf_norm(V)) <= TOL
print("  checked: the sweep is non-increasing, and every value is at least")
print(f"  the L-infinity norm, {measures.linf_norm(V)}.")
print()
print("  p = 64 already gives "
      f"{measures.p_norm(V, 64):.9f}, which rounds to 4 at six")
print("  decimal places. The 'limit' arrives quickly in practice.")
print()

print("=" * 74)
print("2. The unit balls: the picture the whole family hangs on")
print("=" * 74)
print()
print("  Every point marked below is at distance 1.0 or less from the centre.")
print("  Same centre, same radius, three different meanings of 'radius'.")
print()
print("    #  inside the L1 ball        -- a DIAMOND")
print("    +  inside L2 but not L1      -- the ring out to the CIRCLE")
print("    .  inside L-inf but not L2   -- the corners of the SQUARE")
print()

WIDTH, HEIGHT = 61, 25
counts = {1: 0, 2: 0, "inf": 0}
for row in range(HEIGHT):
    y = 1.25 - 2.5 * row / (HEIGHT - 1)
    line = []
    for col in range(WIDTH):
        x = -1.25 + 2.5 * col / (WIDTH - 1)
        point = (x, y)
        if measures.p_norm(point, 1) <= 1.0:
            line.append("#")
            counts[1] += 1
            counts[2] += 1
            counts["inf"] += 1
        elif measures.p_norm(point, 2) <= 1.0:
            line.append("+")
            counts[2] += 1
            counts["inf"] += 1
        elif measures.p_norm(point, math.inf) <= 1.0:
            line.append(".")
            counts["inf"] += 1
        else:
            line.append(" ")
    print(("    " + "".join(line)).rstrip())
print()

assert counts[1] < counts[2] < counts["inf"]
print(f"  grid cells inside each ball: L1 {counts[1]}, L2 {counts[2]}, "
      f"L-inf {counts['inf']}")
print("  strictly nested, which is the same fact as the falling column above:")
print("  a bigger p is a more forgiving norm, so its ball is bigger.")
print()
cell_area = (2.5 / (WIDTH - 1)) * (2.5 / (HEIGHT - 1))
print("  Their true areas are 2, pi and 4. Counting cells on this coarse grid")
print(f"  estimates them as {counts[1] * cell_area:.3f}, "
      f"{counts[2] * cell_area:.3f} and {counts['inf'] * cell_area:.3f} --")
print("  close enough to recognise pi, and a good reminder that a picture")
print("  made of characters is an illustration and not a measurement.")
print()
assert abs(counts[2] * cell_area - math.pi) < 0.25

print("=" * 74)
print("3. What has to be true before you may call something a norm")
print("=" * 74)
print()
print("  Four requirements. Any function that satisfies all four is a norm;")
print("  any that misses one is not, whatever it is called.")
print()

v = catalogue.AXIOM_VECTOR
w = catalogue.TRIANGLE_TRIPLE[1]
k = catalogue.AXIOM_SCALAR
zero = (0.0, 0.0, 0.0)
print(f"    v = {v}      w = {w}      k = {k}")
print()

for label, fn in (("L1", measures.l1_norm),
                  ("L2", measures.l2_norm),
                  ("L-infinity", measures.linf_norm)):
    print(f"  {label}")
    nv, nw, nz = fn(v), fn(w), fn(zero)
    print(f"    1. non-negativity        ||v|| = {nv:.6f}  >= 0")
    assert nv >= 0.0 and nw >= 0.0

    print(f"    2. zero only at zero     ||0|| = {nz:.6f}, and ||v|| != 0")
    assert nz == 0.0 and nv > 0.0

    scaled = fn([k * x for x in v])
    print(f"    3. absolute homogeneity  ||{k}v|| = {scaled:.6f}"
          f"  =  |{k}| * ||v|| = {abs(k) * nv:.6f}")
    assert abs(scaled - abs(k) * nv) <= TOL

    summed = fn([a + b for a, b in zip(v, w)])
    print(f"    4. triangle inequality   ||v+w|| = {summed:.6f}"
          f"  <=  ||v|| + ||w|| = {nv + nw:.6f}")
    assert summed <= nv + nw + TOL
    print()

print("  The third is the one people forget. It says doubling a vector must")
print("  exactly double its size -- so 'squared Euclidean distance', which is")
print("  everywhere in machine learning because it avoids a square root, is")
print("  NOT a norm and not a metric. Doubling a vector quadruples it.")
print()
squared = sum(x * x for x in v)
squared_doubled = sum((2 * x) ** 2 for x in v)
print(f"    squared L2 of v      = {squared:.1f}")
print(f"    squared L2 of 2v     = {squared_doubled:.1f}"
      f"   = {squared_doubled / squared:.0f} times, not 2")
assert abs(squared_doubled - 4 * squared) <= TOL
print()
print("  That does not make it useless -- it ranks identically to L2, because")
print("  squaring is monotonic on non-negative numbers, and it is cheaper. It")
print("  makes it useless as a DISTANCE, so never feed it to anything that")
print("  assumes the triangle inequality, such as a ball tree index.")
print()

order_l2 = measures.rank(catalogue.QUERY, catalogue.ARTICLES,
                         measures.l2_distance)
order_sq = measures.rank(
    catalogue.QUERY, catalogue.ARTICLES,
    lambda a, b: sum((x - y) ** 2 for x, y in zip(a, b)))
print(f"    L2 ranking          {[n for n, _ in order_l2]}")
print(f"    squared L2 ranking  {[n for n, _ in order_sq]}")
assert [n for n, _ in order_l2] == [n for n, _ in order_sq]
print("    identical, as promised.")
print()

print("=" * 74)
print("4. numpy.linalg.norm(v, ord=p) IS this family")
print("=" * 74)
print()
print("  `ord` is p. Agreement here is a real check, because measures.py")
print("  computes with `abs`, `**` and `sum` and never calls NumPy.")
print()
print(f"    {'ord':>8}{'measures.py':>16}{'numpy':>16}{'difference':>14}")
print("    " + "-" * 54)
worst = 0.0
for p in (1, 1.5, 2, 3, 8, np.inf):
    mine = measures.p_norm(V, math.inf if np.isinf(p) else p)
    theirs = float(np.linalg.norm(np.asarray(V), ord=p))
    worst = max(worst, abs(mine - theirs))
    label = "inf" if np.isinf(p) else f"{p:g}"
    print(f"    {label:>8}{mine:>16.9f}{theirs:>16.9f}"
          f"{abs(mine - theirs):>14.2e}")
print()
print(f"  worst difference: {worst:.3e}, against a stated tolerance of {TOL:.0e}")
assert worst <= TOL
print()
print("  One difference worth knowing: numpy.linalg.norm accepts ord=0 and")
print("  ord=-1, and neither is a norm. ord=0 counts the non-zero entries,")
print("  which fails absolute homogeneity outright -- doubling a vector does")
print("  not change how many entries are non-zero.")
print()
sparse_values = (0.0, 3.0, 0.0, -7.0)
sparse = np.array(sparse_values)
zero_norm = float(np.linalg.norm(sparse, ord=0))
zero_norm_doubled = float(np.linalg.norm(2 * sparse, ord=0))
print(f"    numpy.linalg.norm({sparse_values}, ord=0) = {zero_norm}")
print(f"    the same vector doubled                        = "
      f"{zero_norm_doubled}")
assert zero_norm == zero_norm_doubled == 2.0
print()
print("  It is still useful -- 'the L0 norm' is how sparsity is counted in")
print("  compressed sensing and in pruning -- and it is still not a norm.")
print("  measures.p_norm refuses p < 1 rather than returning a number:")
print()
try:
    measures.p_norm(V, 0.5)
except ValueError as exc:
    print(f"    p_norm(v, 0.5) -> ValueError: {exc}")
else:  # pragma: no cover - the call above must raise
    raise AssertionError("p_norm should refuse p < 1")
print()

print("02_the_p_norm_family.py: every assertion held.")
