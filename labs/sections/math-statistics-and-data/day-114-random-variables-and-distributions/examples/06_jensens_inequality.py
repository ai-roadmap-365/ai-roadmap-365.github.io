"""Exercise 6 -- Jensen's inequality in its simplest form.

E[X^2] >= (E[X])^2, and the gap IS the variance -- two lines of algebra,
and it is exactly why E[g(X)] != g(E[X]) in general for a nonlinear g. Here
g(x) = x^2, applied to a single fair die.
"""

import dataset as D
import distributions as dist

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


outcomes = D.DIE_FACES
weight = D.ONE_DIE_WEIGHT

print("X = a single fair die, g(x) = x^2")
print("-" * 60)

E_X = dist.expectation_over(outcomes, weight, lambda x: x)
E_X_squared = dist.expectation_over(outcomes, weight, lambda x: x * x)
g_of_E_X = E_X**2
Var_X = dist.variance_over(outcomes, weight, lambda x: x)
gap = E_X_squared - g_of_E_X

print(f"  E[X]        = {E_X}  = {float(E_X)}")
print(f"  E[X^2]      = {E_X_squared}  = {float(E_X_squared):.6f}")
print(f"  (E[X])^2    = {g_of_E_X}  = {float(g_of_E_X):.4f}")
print(f"  gap         = E[X^2] - (E[X])^2 = {gap}  = {float(gap):.6f}")
print(f"  Var[X]      = {Var_X}  = {float(Var_X):.6f}")

check("E[X^2] is strictly greater than (E[X])^2", E_X_squared > g_of_E_X)
check("the gap EXACTLY equals Var[X]", gap == Var_X)

print()
print("  The two-line proof: Var[X] = E[(X - E[X])^2] = E[X^2] - 2*E[X]*E[X]")
print("  + (E[X])^2 = E[X^2] - (E[X])^2. Since a variance can never be")
print("  negative, E[X^2] - (E[X])^2 >= 0 always -- which IS Jensen's")
print("  inequality for g(x) = x^2, and it is strict here because X is not")
print("  a constant.")

print()
if all(ok for _, ok in checks_held):
    print(f"06_jensens_inequality.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
