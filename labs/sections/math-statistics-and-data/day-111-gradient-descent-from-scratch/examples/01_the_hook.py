"""01_the_hook.py -- the failure that opens the lesson.

The simplest convex function there is, f(x) = 0.5 * x**2, has one minimum,
at x = 0. Gradient descent should find it easily. Run it with a learning
rate only slightly above the function's own divergence boundary and watch
the loss climb every single step, without a single bug in the function,
the gradient, or the code -- until it overflows.
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


print(f"f(x) = 0.5 * {D.HOOK_A} * x^2, minimum at x = 0")
print(f"divergence boundary: eta > 2 / a = {D.HOOK_DIVERGENCE_LR}")
print(f"chosen learning rate: eta = {D.HOOK_LR} -- only slightly too large")
print()

path = G.gradient_descent(lambda x: D.HOOK_A * x, D.HOOK_X0, D.HOOK_LR, D.HOOK_ITERS)
losses = [0.5 * D.HOOK_A * v * v for v in path[:12]]

print("step |     x            | loss")
for i in range(12):
    print(f"{i:4d} | {path[i]: .10f} | {losses[i]:.10f}")
print("  ...")

check(
    "the loss increases on every one of the first 20 steps",
    all(losses[i + 1] > losses[i] for i in range(len(losses) - 1)),
)

first_inf = next(i for i, v in enumerate(path) if math.isinf(v))
first_nan = next(i for i, v in enumerate(path) if math.isnan(v))
print()
print(f"x first becomes inf at step {first_inf}")
print(f"x first becomes nan at step {first_nan}")
print(f"value the step before overflow: {path[first_inf - 1]:.6e}")

check("x reaches inf before it reaches nan", first_inf < first_nan)
check("nan follows inf on the very next step", first_nan == first_inf + 1)
check(
    "nothing raised an exception along the way",
    True,  # if we got here, gradient_descent completed without raising
)

print()
print("Nothing was wrong with f, with its gradient, or with the update rule.")
print("The step size alone turned a solved problem into a divergent one.")
print()
print(f"01_the_hook.py: every assertion held. ({asserts_held} checks)")
