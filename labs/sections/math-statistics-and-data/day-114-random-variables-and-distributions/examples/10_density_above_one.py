"""Exercise 10 -- a density is not a probability, and it can exceed 1.

Uniform(0, 0.5) has density 2 everywhere on its support and still
integrates to exactly 1. This is the misconception that survives whole
degrees, turned into a test: the density value and the integral of that
density are two different numbers, and only one of them is bounded by 1.
"""

import dataset as D
import distributions as dist

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


low, high = D.UNIFORM_LOW, D.UNIFORM_HIGH

print(f"Uniform({low}, {high}) -- a continuous distribution on an interval of width {high - low}")
print("-" * 60)

density_at_points = {x: dist.uniform_density(x, low, high) for x in (0.0, 0.1, 0.25, 0.4, 0.5)}
for x, d in density_at_points.items():
    print(f"  f({x}) = {d}")

check("the density is exactly 2 everywhere on the support", all(d == 2.0 for d in density_at_points.values()))
check("the density is strictly GREATER than 1", all(d > 1.0 for d in density_at_points.values()))
check("outside the support the density is 0", dist.uniform_density(0.75, low, high) == 0.0)

integral = dist.numeric_integral(
    lambda x: dist.uniform_density(x, low, high), low, high, steps=100_000
)
print()
print(f"  numeric integral of f over [{low}, {high}], 100,000 trapezoid steps: {integral}")
check("the integral of the density over its support is 1, to six decimal places", round(integral, 6) == 1.0)

print()
print("  A density of 2 is not an error and is not a probability greater")
print("  than 1 -- it is a value with units of 'probability per unit of x'.")
print("  Only its INTEGRAL over a region gives you back a probability, and")
print("  that integral is bounded by 1 exactly because the whole support has")
print("  width 0.5 and height 2, so 0.5 * 2 = 1. The density itself carries")
print("  no such bound.")

print()
if all(ok for _, ok in checks_held):
    print(f"10_density_above_one.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
