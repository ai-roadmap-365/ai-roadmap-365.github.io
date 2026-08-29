"""02_regimes_and_contraction.py -- exercises 1, 3 and 4.

The update rule for f(x) = 0.5 * a * x**2 is exact algebra:
    x_{n+1} = x_n * (1 - eta * a)
so the whole story of what a learning rate does to convergence lives in
one number, (1 - eta * a), and this script measures it rather than states
it.
"""

import math

import dataset as D
import descent as G

asserts_held = 0


def check(label, condition):
    global asserts_held
    assert condition, f"FAILED: {label}"
    asserts_held += 1
    print(f"  ok: {label}")


print(f"a = {D.A}   1/a = {1.0 / D.A}   2/a = {2.0 / D.A}")
print()

# -- exercise 1: numeric_gradient agrees with the analytic gradient --------
print("Exercise 1 -- numeric_gradient vs the analytic gradient")
f = lambda x: 0.5 * D.A * x * x
for x in (-2.0, 0.5, 3.0):
    analytic = D.A * x
    measured = G.numeric_gradient(f, x, D.NUMERIC_H)
    print(f"  x={x:+.2f}  analytic={analytic:+.6f}  numeric={measured:+.6f}  gap={abs(analytic - measured):.3e}")
    check(f"numeric_gradient agrees with a*x at x={x}", abs(analytic - measured) < D.NUMERIC_TOL)

g = lambda x: math.sin(x * x)
for x in (0.3, 1.5, -0.8):
    analytic = 2.0 * x * math.cos(x * x)
    measured = G.numeric_gradient(g, x, D.NUMERIC_H)
    print(f"  x={x:+.2f}  analytic={analytic:+.6f}  numeric={measured:+.6f}  gap={abs(analytic - measured):.3e}")
    check(f"numeric_gradient agrees with the composed function at x={x}", abs(analytic - measured) < D.NUMERIC_TOL)

# -- exercise 3: the three regimes ------------------------------------------
print()
print("Exercise 3 -- the three regimes")
regimes = {
    "monotone   (0 < eta < 1/a)": D.LR_MONOTONE,
    "exact      (eta = 1/a)": D.LR_EXACT,
    "oscillating(1/a < eta < 2/a)": D.LR_OSCILLATING,
    "divergent  (eta > 2/a)": D.LR_DIVERGENT,
}
expected = {
    "monotone   (0 < eta < 1/a)": "monotone",
    "exact      (eta = 1/a)": "exact",
    "oscillating(1/a < eta < 2/a)": "oscillating",
    "divergent  (eta > 2/a)": "divergent",
}
for label, lr in regimes.items():
    path = G.gradient_descent(lambda x: D.A * x, D.X0_1D, lr, D.REGIME_ITERS)
    regime = G.classify_regime(path, D.A, lr)
    print(f"  eta={lr:.2f}  {label}  first 4 steps: {[round(v, 4) for v in path[:4]]}  ...  classified: {regime}")
    check(f"eta={lr} classified as {expected[label]}", regime == expected[label])

# -- exercise 4: the contraction ratio --------------------------------------
print()
print("Exercise 4 -- the measured contraction ratio equals |1 - eta*a|")
for lr in (D.LR_MONOTONE, D.LR_OSCILLATING, D.LR_DIVERGENT):
    path = G.gradient_descent(lambda x: D.A * x, D.X0_1D, lr, 8)
    ratios = G.per_step_ratios(path)
    predicted = abs(1.0 - lr * D.A)
    print(f"  eta={lr:.2f}  predicted |1-eta*a|={predicted:.6f}  measured ratios={[round(r, 6) for r in ratios[:3]]}")
    check(f"contraction ratio matches prediction at eta={lr}", all(abs(r - predicted) < D.EXACT_TOL for r in ratios))

print()
print(f"02_regimes_and_contraction.py: every assertion held. ({asserts_held} checks)")
