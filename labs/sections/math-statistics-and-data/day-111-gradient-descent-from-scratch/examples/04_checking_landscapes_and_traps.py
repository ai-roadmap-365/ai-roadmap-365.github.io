"""04_checking_landscapes_and_traps.py -- exercises 7, 8 and 9.

Three separate ways a training run can look fine and be wrong: a gradient
with the wrong sign in one place, a landscape with more than one answer,
and a stopping rule that mistakes a flat approach for arrival.
"""

import dataset as D
import descent as G

asserts_held = 0


def check(label, condition):
    global asserts_held
    assert condition, f"FAILED: {label}"
    asserts_held += 1
    print(f"  ok: {label}")


print("Exercise 7 -- gradient checking catches a sign-error bug")
correct_flags = G.gradient_check(D.check_function, D.check_gradient_correct, D.CHECK_POINT, D.NUMERIC_H, D.CHECK_TOL)
buggy_flags = G.gradient_check(D.check_function, D.check_gradient_buggy, D.CHECK_POINT, D.NUMERIC_H, D.CHECK_TOL)
print(f"  point: {D.CHECK_POINT}")
print(f"  correct gradient, checked component by component: {correct_flags}")
print(f"  buggy gradient (component 1 sign-flipped):          {buggy_flags}")
check("the correct gradient passes on every component", all(correct_flags))
check("the buggy gradient fails on exactly component 1", buggy_flags == [True, False, True])

print()
print("Exercise 8 -- two initialisations, two different minima")
left = G.gradient_descent(D.two_minima_grad, D.TWO_MINIMA_LEFT_START, D.TWO_MINIMA_LR, D.TWO_MINIMA_ITERS)
right = G.gradient_descent(D.two_minima_grad, D.TWO_MINIMA_RIGHT_START, D.TWO_MINIMA_LR, D.TWO_MINIMA_ITERS)
print("  f(x) = (x^2 - 1)^2, minima at x = -1 and x = +1, local maximum at x = 0")
print(f"  start x0={D.TWO_MINIMA_LEFT_START}   ->  converged to {left[-1]:.6f}")
print(f"  start x0={D.TWO_MINIMA_RIGHT_START}   ->  converged to {right[-1]:.6f}")
check("the two runs converge to minima more than the margin apart", G.minima_differ(left[-1], right[-1], D.TWO_MINIMA_MARGIN))
check("the left run reaches -1", abs(left[-1] + 1.0) < 1e-3)
check("the right run reaches +1", abs(right[-1] - 1.0) < 1e-3)

print()
print("Exercise 9 -- the stopping-criterion trap")
result = G.stopping_criteria_disagree(
    D.PLATEAU_X0, D.plateau_grad, D.plateau_value, D.PLATEAU_LR, D.PLATEAU_GRAD_TOL, D.PLATEAU_DELTA_F_TOL
)
print(f"  a shallow bowl (a={D.PLATEAU_A}) at x={D.PLATEAU_X0}, far from its minimum at x=0")
print(f"  ||grad|| = {result['grad_norm']:.6f}   (tolerance: {D.PLATEAU_GRAD_TOL})")
print(f"  |delta f| = {result['delta_f']:.3e}   (tolerance: {D.PLATEAU_DELTA_F_TOL})")
print(f"  naive '|delta f| < tol, so we converged' would stop here: {result['naive_stops_early']}")
check("the gradient is still above its own tolerance", result["grad_norm"] >= D.PLATEAU_GRAD_TOL)
check("the loss barely moved, below its own tolerance", result["delta_f"] < D.PLATEAU_DELTA_F_TOL)
check("the naive criterion would stop early", result["naive_stops_early"] is True)

print()
print(f"04_checking_landscapes_and_traps.py: every assertion held. ({asserts_held} checks)")
