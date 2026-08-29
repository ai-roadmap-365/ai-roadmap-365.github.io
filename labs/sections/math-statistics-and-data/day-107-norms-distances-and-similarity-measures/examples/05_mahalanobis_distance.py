"""Mahalanobis: Euclidean distance after accounting for how the data varies.

Run from the `examples/` directory:

    ../.venv/bin/python3 05_mahalanobis_distance.py

Euclidean distance treats every direction as equally surprising. Real data
does not: it has a grain, and moving along the grain is ordinary while moving
across it is an event. Mahalanobis distance is what you get when you measure in
the data's own units instead of the axes' units, and Day 106's eigenvectors of
the covariance matrix are exactly the directions it measures along.
"""

from __future__ import annotations

import math

import numpy as np

import catalogue
import measures
from measures import TOL

DATA = catalogue.SENSOR_READINGS

print("=" * 74)
print("1. Eight readings from two sensors that move together")
print("=" * 74)
print()
print("    reading   sensor A   sensor B")
print("    " + "-" * 30)
for i, (sa, sb) in enumerate(DATA, start=1):
    print(f"    {i:<10}{sa:>9.1f}{sb:>11.1f}")
print()

mean = measures.column_means(DATA)
print(f"  mean = {tuple(mean)}")
assert mean == [0.0, 0.0]
print()

# A picture of the grain, drawn from the data rather than described.
print("  Plotted, with the two probe points marked:")
print()
LO, HI = -5, 5
for row in range(HI, LO - 1, -1):
    line = []
    for col in range(LO, HI + 1):
        point = (float(col), float(row))
        if point == catalogue.PROBE_ALONG:
            line.append(" A")
        elif point == catalogue.PROBE_ACROSS:
            line.append(" X")
        elif point in DATA:
            line.append(" o")
        elif col == 0 and row == 0:
            line.append(" +")
        elif col == 0:
            line.append(" |")
        elif row == 0:
            line.append(" -")
        else:
            line.append(" .")
    print("      " + "".join(line))
print()
print("      o  a reading         +  the mean")
print(f"      A  probe {catalogue.PROBE_ALONG}, ALONG the grain")
print(f"      X  probe {catalogue.PROBE_ACROSS}, ACROSS it")
print()
print("  Every reading sits near the line B = A. The two sensors agree, all")
print("  day, and the eight points say so without anyone writing it down.")
print()

print("=" * 74)
print("2. The covariance matrix")
print("=" * 74)
print()
cov = measures.covariance_matrix(DATA)
print("    covariance = [[%.4f, %.4f]," % (cov[0][0], cov[0][1]))
print("                  [%.4f, %.4f]]" % (cov[1][0], cov[1][1]))
print()
assert cov == [[7.5, 7.0], [7.0, 7.5]]
print("  Exactly [[7.5, 7.0], [7.0, 7.5]], with no floating-point residue,")
print("  because the data was chosen so you can check it by hand:")
print()
print("    variance of A  = (16+9+4+1+1+4+9+16) / 8 = 60 / 8 = 7.5")
print("    covariance A,B = (12+12+2+2+2+2+12+12) / 8 = 56 / 8 = 7.0")
print()
corr = cov[0][1] / math.sqrt(cov[0][0] * cov[1][1])
print(f"  correlation = 7.0 / 7.5 = {corr:.6f}   -- very nearly 1")
assert abs(corr - 7.0 / 7.5) <= TOL
print()

cov_np = np.cov(np.asarray(DATA, dtype=float), rowvar=False, bias=True)
print("  NumPy computes the same matrix. `bias=True` is the population")
print("  divisor n, which is what measures.covariance_matrix uses and what")
print("  scikit-learn's StandardScaler uses; the default `bias=False` divides")
print("  by n - 1 and is a different, also-correct, answer to a different")
print("  question.")
print()
print(f"    numpy (bias=True)  = {cov_np.tolist()}")
print(f"    numpy (bias=False) = "
      f"{np.cov(np.asarray(DATA, dtype=float), rowvar=False).tolist()}")
assert np.allclose(cov_np, np.asarray(cov), atol=TOL)
print()

print("=" * 74)
print("3. The inverse, in pure Python, checked against NumPy")
print("=" * 74)
print()
inv = measures.inverse(cov)
det = cov[0][0] * cov[1][1] - cov[0][1] * cov[1][0]
print(f"    determinant = 7.5*7.5 - 7.0*7.0 = {det}")
print("    inverse     = [[%.6f, %.6f]," % (inv[0][0], inv[0][1]))
print("                   [%.6f, %.6f]]" % (inv[1][0], inv[1][1]))
print()
inv_np = np.linalg.inv(np.asarray(cov))
worst = float(np.max(np.abs(np.asarray(inv) - inv_np)))
print(f"    numpy.linalg.inv agrees to {worst:.3e}, tolerance {TOL:.0e}")
assert worst <= TOL
print()
print("  measures.inverse is Gauss-Jordan elimination written out by hand, so")
print("  the Mahalanobis numbers below owe nothing to NumPy and agreeing with")
print("  NumPy means something.")
print()
product = measures.matmul(cov, inv)
print(f"    covariance * inverse = {[[round(x, 12) for x in r] for r in product]}")
assert abs(product[0][0] - 1) <= TOL and abs(product[1][1] - 1) <= TOL
assert abs(product[0][1]) <= TOL and abs(product[1][0]) <= TOL
print()

print("=" * 74)
print("4. Two points Euclidean cannot tell apart")
print("=" * 74)
print()
along, across = catalogue.PROBE_ALONG, catalogue.PROBE_ACROSS
eu_along = measures.l2_distance(along, mean)
eu_across = measures.l2_distance(across, mean)
ma_along = measures.mahalanobis_distance(along, mean, inv)
ma_across = measures.mahalanobis_distance(across, mean, inv)

print(f"    {'probe':<14}{'Euclidean':>12}{'Mahalanobis':>14}")
print("    " + "-" * 40)
print(f"    {str(along):<14}{eu_along:>12.6f}{ma_along:>14.6f}")
print(f"    {str(across):<14}{eu_across:>12.6f}{ma_across:>14.6f}")
print()
assert abs(eu_along - eu_across) <= TOL
assert abs(eu_along - math.sqrt(18.0)) <= TOL
print(f"  Euclidean: identical, both sqrt(18) = {eu_along:.6f}. It has no way")
print("  to distinguish them, because it does not know the data exists.")
print()
assert ma_across > ma_along
print(f"  Mahalanobis: {ma_along:.6f} against {ma_across:.6f}, a factor of "
      f"{ma_across / ma_along:.4f}.")
print("  Both sensors reading 3 together is a perfectly ordinary Tuesday. One")
print("  reading +3 while the other reads -3 has never happened in this")
print("  dataset, and the number says so.")
print()
print("  The second value is 6, and here is why every comparison in this lab")
print("  states a tolerance. Two correct implementations of the same inverse")
print("  disagree in the last bit, and it survives all the way to the answer:")
print()
ma_np = float(math.sqrt(
    np.asarray(across) @ inv_np @ np.asarray(across)))
print(f"    via measures.inverse   (Gauss-Jordan)  {ma_across!r}")
print(f"    via numpy.linalg.inv   (LAPACK)        {ma_np!r}")
print(f"    difference                             {abs(ma_across - ma_np):.3e}")
assert abs(ma_across - 6.0) <= TOL
assert abs(ma_np - 6.0) <= TOL
print()
print("  Neither is wrong and neither is 'more accurate'. `== 6.0` would pass")
print("  for one and fail for the other, which is the entire argument against")
print("  writing `==` between two floats you did not personally construct.")
print()
print("  That is the whole argument for the measure. An anomaly detector built")
print("  on Euclidean distance has to score these two the same. One of them is")
print("  a sensor fault.")
print()

print("=" * 74)
print("5. Where the numbers come from: Day 106's eigenvectors")
print("=" * 74)
print()
values, vectors = np.linalg.eigh(np.asarray(cov))
print("  Eigen-decomposition of the covariance matrix:")
for value, vector in zip(values, vectors.T):
    print(f"    eigenvalue {value:8.4f}   eigenvector "
          f"({vector[0]:+.6f}, {vector[1]:+.6f})")
print()
assert abs(sorted(values)[0] - 0.5) <= 1e-12
assert abs(sorted(values)[1] - 14.5) <= 1e-12
print("  0.5 and 14.5. The large one belongs to the (1, 1) direction -- along")
print("  the grain, where the data spreads a lot -- and the small one to")
print("  (1, -1), across it, where the data barely spreads at all. An")
print("  eigenvector's SIGN is arbitrary, which is why NumPy prints the small")
print("  one as (-0.707107, +0.707107): that is the same line as (1, -1),")
print("  pointing the other way, and no distance below can tell the")
print("  difference because every component is squared.")
print()
print("  Mahalanobis distance is Euclidean distance measured in those")
print("  directions, with each one divided by the square root of its own")
print("  eigenvalue. Worked by hand for both probes:")
print()
axis_along = (1 / math.sqrt(2), 1 / math.sqrt(2))
axis_across = (1 / math.sqrt(2), -1 / math.sqrt(2))
for label, probe in (("along  (3, 3)", along), ("across (3, -3)", across)):
    c_big = measures.dot(probe, axis_along)
    c_small = measures.dot(probe, axis_across)
    by_hand = math.sqrt(c_big ** 2 / 14.5 + c_small ** 2 / 0.5)
    direct = measures.mahalanobis_distance(probe, mean, inv)
    print(f"    {label}")
    print(f"      component along  (1, 1)/sqrt(2) = {c_big:+.6f}"
          f"   / sqrt(14.5) = {c_big / math.sqrt(14.5):+.6f}")
    print(f"      component across (1,-1)/sqrt(2) = {c_small:+.6f}"
          f"   / sqrt( 0.5) = {c_small / math.sqrt(0.5):+.6f}")
    print(f"      hypotenuse of those two         = {by_hand:.6f}")
    print(f"      mahalanobis_distance says       = {direct:.6f}")
    assert abs(by_hand - direct) <= 1e-9
    print()
print("  So Mahalanobis is not a new kind of distance at all. It is Euclidean")
print("  distance in a coordinate system the data chose for itself, and the")
print("  eigenvectors Day 106 built are the axes of that system.")
print()

print("=" * 74)
print("6. Substituting the identity gives back Euclidean, exactly")
print("=" * 74)
print()
identity = [[1.0, 0.0], [0.0, 1.0]]
worst = 0.0
for probe in (along, across, (1.0, 0.0), (-2.5, 4.75), (0.0, 0.0)):
    a_val = measures.mahalanobis_distance(probe, mean, identity)
    b_val = measures.l2_distance(probe, mean)
    worst = max(worst, abs(a_val - b_val))
    print(f"    probe {str(probe):<14} mahalanobis {a_val:>10.6f}"
          f"   euclidean {b_val:>10.6f}")
print()
print(f"  worst difference: {worst:.3e}")
assert worst <= TOL
print()
print("  Which is the cleanest way to see what the covariance is doing: it is")
print("  the thing that would be the identity if every feature had variance 1")
print("  and no feature had anything to do with any other. Real data is never")
print("  that, and Euclidean distance quietly assumes it always is.")
print()
print("  The cost is real and worth stating. Mahalanobis needs an invertible")
print("  covariance matrix, which needs more rows than columns and no two")
print("  features that are exact duplicates -- and it needs re-estimating when")
print("  the data drifts. A singular covariance raises here rather than")
print("  returning a plausible number:")
print()
duplicate_feature = [(1.0, 2.0), (2.0, 4.0), (3.0, 6.0), (4.0, 8.0)]
try:
    measures.inverse(measures.covariance_matrix(duplicate_feature))
except ValueError as exc:
    print(f"    second feature = 2 * first  ->  ValueError: {exc}")
else:  # pragma: no cover - the call above must raise
    raise AssertionError("a singular covariance should refuse to invert")
print()

print("05_mahalanobis_distance.py: every assertion held.")
