# Descent by Hand — nine exercises

Everything you write goes in `descent.py`, beside this file. `dataset.py`
holds every constant and helper you need — read it, do not change it. Check
yourself as you go:

```bash
.venv/bin/pytest starter -q
```

A skip means "not attempted yet". A failure means "attempted and wrong", and
prints your answer next to the correct one.

## 1. `numeric_gradient(f, x, h)`

The gradient by central differences — Day 108's definition, put to work
again. Must agree with the analytic gradient of a quadratic and of a
composed function (`sin(x**2)`) to a stated tolerance, and must handle both
a scalar `x` and a vector one.

## 2. `gradient_descent(grad, x0, lr, iters)`

The whole loop, in one function: `x <- x - lr * grad(x)`, repeated `iters`
times. Return the **whole path**, not just the final answer — every later
exercise inspects it.

## 3. The three regimes

`classify_regime(path, a, lr)` reads a path produced on `f(x) = 0.5*a*x**2`
and says which of four things happened: `monotone`, `exact`, `oscillating`,
`divergent`. With `a = 5` (so `1/a = 0.2`, `2/a = 0.4`), the four learning
rates in `dataset.py` are chosen to land one in each regime. This is the
exercise the whole day is built on — get the boundary conditions right and
the rest of the lab follows.

## 4. The measured contraction ratio

`per_step_ratios(path)` returns the list of `|x_{n+1} / x_n|`. For the
quadratic, this should equal `|1 - lr*a|` at every single step — a
prediction from Day 111's algebra, checked against real numbers rather than
trusted.

## 5. Ill-conditioning

`steps_to_tolerance(grad, x0, lr, tol, max_iters)` runs gradient descent
until `||grad(x)|| < tol` and reports how many steps it took. Run it on
`f(x, y) = 0.5*(x**2 + kappa*y**2)` for `kappa` in `{1, 5, 20, 100}`
(`dataset.bowl_grad` builds the gradient function; `dataset.kappa_lr` picks
the learning rate). The step count should never decrease as `kappa` grows,
and `kappa=100` should need at least ten times the steps of `kappa=1`.

## 6. Momentum

`gradient_descent_momentum(grad, x0, lr, beta, iters)` and
`steps_to_tolerance_momentum(...)` add one line to exercise 2 and 5's
shapes: a velocity `v <- beta*v + grad(x)`, and `x <- x - lr*v` in place of
`x <- x - lr*grad(x)`. On the `kappa=20` bowl, at the SAME learning rate
plain descent uses, momentum should need strictly fewer steps.

## 7. Gradient checking

`gradient_check(f, grad_fn, x, h, tol)` compares an analytic gradient
against `numeric_gradient` at `x`, component by component, and returns a
list of booleans. `dataset.py` supplies a function with a known-correct
gradient and a deliberately buggy one (one component's sign flipped) —
your check must pass the first and flag exactly the broken component of the
second.

## 8. Two minima

`minima_differ(final_a, final_b, margin)` is one line: are two converged
points farther apart than `margin`? Run `gradient_descent` from two
different starting points on `dataset.two_minima_grad` (the gradient of
`f(x) = (x**2 - 1)**2`, which has minima at `x = -1` and `x = +1`) and
confirm they land on opposite sides.

## 9. The stopping-criterion trap

`stopping_criteria_disagree(x, grad_fn, value_fn, lr, tol_grad, tol_f)`
takes one gradient-descent step and reports the gradient's magnitude, the
change in the function value, and whether the naive "the loss barely
changed, so we must be done" rule would fire while the gradient is still
well above its own tolerance. Run it on `dataset.PLATEAU_X0` with
`dataset.plateau_grad` and `dataset.plateau_value` — a point far from the
minimum of a very shallow bowl, where the slope is real but tiny.

## When you are done

```bash
.venv/bin/pytest starter -q -p no:cacheprovider
```

should report every test passing. Then read `examples/` — the reference
implementation and four narrated demonstration scripts that print their own
working and assert every claim they make.
