"""03_ill_conditioning_and_momentum.py -- exercises 5 and 6.

f(x, y) = 0.5 * (x**2 + kappa * y**2) has Hessian diag(1, kappa), so its
condition number IS kappa -- Day 106's ratio of eigenvalues, put to work.
The optimal fixed learning rate for this bowl is 2 / (1 + kappa); this
script measures how many steps that optimal rate needs as kappa grows, and
then shows what a beta*v running average of the gradient buys back.
"""

import numpy as np

import dataset as D
import descent as G

asserts_held = 0


def check(label, condition):
    global asserts_held
    assert condition, f"FAILED: {label}"
    asserts_held += 1
    print(f"  ok: {label}")


print("Exercise 5 -- steps to convergence grow with the condition number")
print(f"tolerance on ||grad||: {D.KAPPA_GRAD_TOL}")
print()
print("kappa |     eta = 2/(1+kappa)  | steps")
counts = []
for k in D.KAPPA_VALUES:
    lr = D.kappa_lr(k)
    steps = G.steps_to_tolerance(D.bowl_grad(k), np.array(D.KAPPA_START), lr, D.KAPPA_GRAD_TOL, D.KAPPA_MAX_ITERS)
    counts.append(steps)
    print(f"{k:5d} | {lr:22.6f} | {steps}")

check("steps are non-decreasing as kappa grows", all(counts[i] <= counts[i + 1] for i in range(len(counts) - 1)))
check(f"kappa={D.KAPPA_VALUES[-1]} needs at least 10x the steps of kappa={D.KAPPA_VALUES[0]}", counts[-1] >= 10 * max(counts[0], 1))
check("the isotropic bowl (kappa=1) converges in exactly one step", counts[0] == 1)

print()
print("Exercise 6 -- momentum on the kappa=20 bowl")
k = D.MOMENTUM_KAPPA
lr = D.kappa_lr(k)
plain_steps = G.steps_to_tolerance(D.bowl_grad(k), np.array(D.KAPPA_START), lr, D.KAPPA_GRAD_TOL, D.KAPPA_MAX_ITERS)
momentum_steps = G.steps_to_tolerance_momentum(
    D.bowl_grad(k), np.array(D.KAPPA_START), D.MOMENTUM_LR, D.MOMENTUM_BETA, D.KAPPA_GRAD_TOL, D.KAPPA_MAX_ITERS
)
print(f"  same learning rate for both: eta = {lr:.6f}")
print(f"  plain gradient descent:    {plain_steps} steps")
print(f"  momentum (beta={D.MOMENTUM_BETA}):        {momentum_steps} steps")
print(f"  speedup: {plain_steps / momentum_steps:.2f}x")
check("momentum needs strictly fewer steps than plain descent", momentum_steps < plain_steps)

print()
print(f"03_ill_conditioning_and_momentum.py: every assertion held. ({asserts_held} checks)")
