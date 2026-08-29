# Day 110 lab — the brief

Nine exercises, in order. Work top to bottom; each one leans on the one before.

Check yourself at any point:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `2 passed, 163 skipped`. A **skip** means
"not attempted". A **failure** means "attempted and wrong", and it prints your
answer beside the real one. When it prints `165 passed`, you are finished.

Predict before you run. Exercises 5 to 9 are predictions on purpose, and two of
them are traps that only catch you if you commit to an answer first.

---

## Exercise 1 — `chainrule.py`, fourteen functions

The plumbing. None of it is hard and all of it is used later.

| Function | The thing to get right |
| --- | --- |
| `product` | The empty product is `1.0`, not `0.0` |
| `gear_ratio` | One line, calling `product` |
| `central_difference` | Divide by `2h`, not `h`. Raise `ValueError` on a non-positive step |
| `partial_difference` | Nudge one coordinate, hold the rest still |
| `compose` | Returns a **function**, not a number |
| `chain_rule` | Evaluate the outer derivative at `u = inner(x)`, not at `x` |
| `chain_values` | `n` stages give `n + 1` values, starting with `x` itself |
| `chain_local_rates` | Rate `i` is evaluated at the value **arriving** at stage `i` |
| `chain_derivative` | One line, calling `product` |
| `chain_function` | Returns a function, like `compose` |
| `running_products` | Entry `i` is the product of `rates[i:]`, in stage order |
| `path_contributions` | One product per path |
| `total_derivative` | **Add** across paths. This is the whole day |
| `repeated_product` | A loop, not `**`. `ValueError` on a negative count |
| `order_of_magnitude` | `floor(log10(abs(v)))`. `ValueError` on zero |

## Exercise 2 — `autodiff.py`, the engine

The most valuable thing in the calculus arc. Roughly seventy lines when you are
done, and it is the core of what every deep-learning framework does.

- **2a `__add__`** — the shape of all three operations. The approach block in
  the docstring is written out in full, because it is worth having one to copy
  from.
- **2b `__mul__`** — each input's local rate is the *other* input's value.
- **2c `tanh`** — slope is `1 - tanh²`. Compute the tanh once and reuse it.
- **2d `topological_order`** — iterative, not recursive. A ten-thousand-node
  graph is a test.
- **2e `backward`** — zero the gradients, seed the output with `1.0`, walk the
  order in reverse.
- **2f `Dual`** — forward mode, for the cost comparison in exercise 3.

**Use `+=` in every backward step, never `=`.** That one character is the
multivariable chain rule. The engine will run either way, look sensible either
way, and be wrong on every graph where anything is used twice.

## Exercise 3 — the two modes and their cost

`reverse_mode_gradient`, `forward_mode_gradient` and `numeric_gradient`. Each
returns its gradients **and the number of passes it needed**. The counts are
the point: 1, `n`, and `2n` for a function of `n` inputs. Training a model is
`n` in the millions and one scalar out.

## Exercise 4 — `network.py`, backpropagation by hand

Two inputs, two tanh hidden units, one linear output, squared-error loss, nine
parameters. Every quantity in both passes is exact in float64, so you can check
the whole thing with a pen.

- **4a `hand_gradients`** — sixteen gradients, by your own arithmetic. Work
  backwards from `d(loss)/d(loss) = 1`.
- **4b `engine_gradients`** — the same sixteen from one backward pass. If 2 is
  right these match 4a *exactly*, not approximately.
- **4c `numeric_parameter_gradients`** — central differences, which will not
  match exactly and should not.

Two of the sixteen deserve thought before you write them. `vA` multiplies an
activation of exactly zero. And `x1` and `x2` each reach the loss through
**both** hidden units, so each of those gradients is a sum of two products.

## Exercises 5 to 9 — `answers.py`, forty-two predictions

Fill in every `None`. Grouped as:

- **5** rates multiply (4 predictions)
- **6** composition and the one-variable chain rule (7)
- **7** depth, and the sum over paths (12)
- **8** the engine, and the network (12)
- **9** cost, collapse, and one honest surprise (7)

Two of these are designed to catch you:

**7.8** asks for the correct `df/dx` when a variable reaches the output twice.
The two contributions are 24 and 12. It is not 24, not 12, and not 288.

**9.6** asks whether `1.0 + 0.5**50 == 1.0`. `0.5**50` is about `8.88e-16` and
float64's epsilon is about `2.22e-16`, so the obvious guess is `True`. Work out
how many epsilons `8.88e-16` actually is before you answer.

---

## When you are done

Read the reference. Every script prints its working and asserts every claim it
makes:

```bash
cd examples
../.venv/bin/python3 01_gears_and_rates.py
../.venv/bin/python3 02_composition_and_the_chain_rule.py
../.venv/bin/python3 03_deeper_chains.py
../.venv/bin/python3 04_two_paths_add.py
../.venv/bin/python3 05_the_value_engine.py
../.venv/bin/python3 06_backprop_by_hand.py
../.venv/bin/python3 07_vanishing_and_exploding.py
cd ..
```

Section 6 of script 07 is the one to read even if you read nothing else: it
measures a case where the standard story about vanishing gradients is wrong by
ten orders of magnitude, and explains why.
