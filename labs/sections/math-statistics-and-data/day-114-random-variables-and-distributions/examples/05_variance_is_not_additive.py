"""Exercise 5 -- variance is NOT additive for dependent variables.

Put directly beside exercise 4 so the asymmetry is unmissable: expectation
forgave dependence completely; variance does not. Var[X+Y] = Var[X] +
Var[Y] + 2*Cov(X,Y), and the covariance term does not vanish here, because
X and Y are dependent.
"""

import dataset as D
import distributions as dist

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


outcomes = D.TWO_DICE_SPACE
weight = D.TWO_DICE_WEIGHT
X = D.first_die
Y = D.dice_sum

print("The same dependent pair as exercise 4: X = first die, Y = sum")
print("-" * 60)

Var_X = dist.variance_over(outcomes, weight, X)
Var_Y = dist.variance_over(outcomes, weight, Y)
Var_X_plus_Y = dist.variance_over(outcomes, weight, lambda o: X(o) + Y(o))
Cov_XY = dist.covariance_over(outcomes, weight, X, Y)

print(f"  Var[X]        = {Var_X}")
print(f"  Var[Y]        = {Var_Y}")
print(f"  Var[X]+Var[Y] = {Var_X + Var_Y}")
print(f"  Cov(X, Y)     = {Cov_XY}")
print(f"  Var[X]+Var[Y]+2*Cov(X,Y) = {Var_X + Var_Y + 2 * Cov_XY}")
print(f"  Var[X+Y]      = {Var_X_plus_Y}   (computed directly)")

check("Var[X+Y] does NOT equal Var[X] + Var[Y]", Var_X_plus_Y != Var_X + Var_Y)
check(
    "Var[X+Y] EXACTLY equals Var[X] + Var[Y] + 2*Cov(X,Y)",
    Var_X_plus_Y == Var_X + Var_Y + 2 * Cov_XY,
)
check("the covariance term is non-zero, which is WHY the naive sum fails", Cov_XY != 0)

print()
print("  Beside exercise 4's result, the asymmetry is exact: expectation")
print("  distributes over a sum unconditionally. Variance only distributes")
print("  when the covariance term is zero -- which independence guarantees")
print("  and dependence, in general, does not.")

print()
if all(ok for _, ok in checks_held):
    print(f"05_variance_is_not_additive.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
