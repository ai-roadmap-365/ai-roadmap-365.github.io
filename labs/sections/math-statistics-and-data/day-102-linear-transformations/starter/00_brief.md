# Day 102 lab — Where Do the Basis Vectors Land?

One idea holds this whole lab together:

> **A matrix IS a function, and its columns are where the basis vectors land.**

If you know where `(1, 0)` and `(0, 1)` go, you know where everything goes —
because every vector `(x, y)` is `x * (1, 0) + y * (0, 1)`, and a linear
transformation is precisely one that keeps that combination intact.

Everything below is a consequence of that sentence. Work in order; each
exercise uses the one before it.

Check yourself at any point, from the **lab directory** (the one above this
file):

```bash
.venv/bin/pytest starter -q
```

Unattempted work is **skipped**, not failed. On an untouched checkout you will
see `1 passed, 53 skipped`. When it says `54 passed`, you are finished.

---

## Exercise 1 — `transforms.py` (ten functions)

Write the ten functions marked `raise NotImplementedError`. Each docstring
gives the derivation and a worked example you can check on paper. Use only
`math` from the standard library in this file — NumPy appears in the tests,
where it checks your work, which is the right way round.

| Step | Function | What it must do |
| --- | --- | --- |
| 1.1 | `from_landings` | Two landing places in, one matrix out. The landings are the **columns**. |
| 1.2 | `columns_of` | The exact inverse of 1.1. |
| 1.3 | `apply` | `x` lots of the first column plus `y` lots of the second. |
| 1.4 | `scaling` | Derive it: where does one step right go when the plane stretches? |
| 1.5 | `reflection_in_x_axis` | Derive it: what happens to a point that is already **on** the mirror line? |
| 1.6 | `shear_x` | Derive it: the sideways push is proportional to the **height**. |
| 1.7 | `rotation` | Derive it from the unit circle. The docstring defines cosine and sine from scratch if you have not met them. |
| 1.8 | `compose` | Column 0 is where `(1, 0)` ends up after **both** steps. Mind the argument order. |
| 1.9 | `determinant` | `a*d - b*c`, computed directly so whole numbers stay exact. |
| 1.10 | `inverse` | The undo. Raise `SingularMatrix` when the determinant is 0. |

Three helpers are written for you at the bottom of the file — `identity`,
`transform_polygon`, `signed_area` and `rank`. Read them; the tests use them.

**The gotcha in 1.8.** `compose(second, first)` returns the matrix that does
`first` and then `second`, so the step that happens **first** is written on the
**right**. That is not an arbitrary convention: applying `first` and then
`second` to a vector `v` is `second @ (first @ v)`, and `first` is the one
standing next to the vector.

---

## Exercise 2 — read a matrix off a picture (`answers.py`)

There is no picture file. The drawing is described in words in `shapes.py`,
because the skill being trained is going from *where did the basis vectors
land* to *what is the matrix*, and looking at a picture would let you skip the
step.

The drawing shows two things and only two things:

```
the arrow (1, 0) redrawn ending at ( 3, 1)
the arrow (0, 1) redrawn ending at (-1, 2)
```

Write the matrix. Then say where `(2, 1)` lands, without drawing anything.

Exercise 2.3 asks which **row** of that matrix is a landing place. Read the
question carefully before answering; it is the single most common mistake with
transformation matrices.

---

## Exercise 3 — the four standard transformations

Predict where specific points land under scaling, reflection, shear and a
quarter turn. Each answer is one line of arithmetic.

Exercise 3.6 is the one worth slowing down for. On paper, a quarter turn sends
`(1, 0)` to exactly `(0, 1)`. In binary floating point, `cos(pi / 2)` comes out
as `6.123233995736766e-17`, because `pi` cannot be stored exactly and the
cosine of the stored value is not the cosine of pi. **That is why every float
comparison in this lab uses a tolerance of `1e-12` and none of them use `==`.**
The number is not arbitrary: it sits about five orders of magnitude above that
rounding error and about four below the smallest quantity the lab cares about.

Exercise 3.7 asks for the one point no matrix anywhere can move. Once you see
why, half of exercise 4 answers itself.

---

## Exercise 4 — linear, and not linear

*Linear* means exactly two things:

```
T(u + v) = T(u) + T(v)        it preserves addition
T(s * u) = s * T(u)           it preserves scalar multiplication
```

Both, for every `u`, `v` and `s`. Nothing else.

With `M = [[2, 0], [0, 3]]`, `b = (1, 1)`, `u = (1, 2)`, `v = (3, -1)`, `s = 5`,
you check both properties for `T(v) = M @ v` and for `f(v) = M @ v + b`.

`f` fails both. Compute the gap in 4.5 before you read any further explanation
— the size of the gap is a recognisable quantity, and recognising it is the
exercise.

This is not a curiosity. It is the reason a neural network layer is written
`X @ W + b` with the bias kept separate rather than folded into the matrix, and
the reason the word *affine* exists.

---

## Exercise 5 — composition and order

`A = shear_x(2)`, `B = rotation(pi / 2)`. You shear first, then rotate.

Which product is that? Write it out. Then decide whether the other order gives
the same matrix. It does not, and 5.3 wants you to have checked rather than
assumed.

5.4 is a freebie with a real consequence behind it: determinants multiply under
composition, so if any step in a pipeline has determinant 0, the whole pipeline
does, and nothing downstream can recover what that step destroyed.

---

## Exercise 6 — determinant, area, orientation, rank and the inverse

The determinant is introduced here the way it is actually useful: send the unit
square through the transformation and measure the area of what comes out. That
number, **with its sign**, is the determinant.

- 6.1–6.4: positive determinants, and one negative one. What does the sign say?
- 6.5–6.7: `[[1, 2], [2, 4]]`. Look at its two columns before predicting
  anything. Where does everything end up?
- 6.8: name the exception class `numpy.linalg.inv` raises on it. Give the class
  itself, not a string. `numpy` is already imported at the top of `answers.py`.
- 6.9–6.10: two inverses you can write down without the formula, if you think
  about what would undo each transformation.

---

## When you are done

Read the reference. Each script prints its working and asserts every claim it
makes, so nothing in it is decoration:

```bash
cd examples
../.venv/bin/python3 01_columns_are_landings.py
../.venv/bin/python3 02_building_the_transformations.py
../.venv/bin/python3 03_linear_or_not.py
../.venv/bin/python3 04_composition_and_order.py
../.venv/bin/python3 05_determinant_inverse_rank.py
../.venv/bin/python3 06_the_limit_of_linear.py
cd ..
```

Script 06 is the payoff, and it is worth reading even if you stop everything
else. It shows that a linear transformation always fixes the origin, always
sends straight lines to straight lines, and that a stack of twenty of them
collapses into a single 2 by 2 matrix. Depth bought nothing. That is the
concrete, measured reason a non-linear activation function sits between the
layers of a network — not a rule to memorise, a limitation you can watch
happening.
