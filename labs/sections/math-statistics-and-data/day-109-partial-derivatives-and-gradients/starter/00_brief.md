# Which Way Is Uphill? — the eight exercises, in order

Work through these in order. Check yourself at any point from the **lab
directory** (the one above this file):

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `1 passed, 205 skipped`. A skip means
"not attempted"; a failure means "attempted and wrong", and prints both your
answer and the right one. When it prints `206 passed`, you are finished.

Do not open `examples/` until you have tried. It is the answer key, and it is
worth reading afterwards — every script there prints its working — but reading
it first turns a lab into a tutorial.

---

## Exercise 1 — the machinery (`starter/gradients.py`)

Eight functions. The first two are the day; the rest are built out of them.

| # | Function | What it does |
| --- | --- | --- |
| 1.1 | `partial(f, point, index, h)` | Nudge ONE coordinate up and down by `h`, hold the rest still, divide by `2h`. |
| 1.2 | `gradient(f, point, h)` | One partial per input, collected into a vector. |
| 1.3 | `magnitude(vector)` | Day 99's Euclidean norm. |
| 1.4 | `unit(vector)` | The same direction at length 1; `ValueError` on the zero vector. |
| 1.5 | `directional_derivative(f, point, direction, h)` | Dot the gradient with the unit direction. |
| 1.6 | `directional_derivative_direct(...)` | The same number, measured along the direction, with no gradient involved. |
| 1.7 | `sweep_directions(f, point, n, h)` | `n` bearings round the circle, each one's rate of change. |
| 1.8 | `forward_partial(...)` | The one-sided version, for the comparison in exercise 6. |

Write 1.1 first and get its tests green before anything else. Everything below
it inherits its errors, and three of its tests exist to catch the three
specific ways it goes wrong: dividing by `h` instead of `2h`, letting a second
coordinate move, and mutating the caller's point.

1.5 and 1.6 compute the same quantity by completely different routes. The test
that compares them is the most important one in the lab: it is the evidence
that dotting the gradient with a direction really does answer "how fast does
`f` change if I walk that way", rather than being a rule you were told.

Once all eight are written, a further thirty-two tests run automatically. They are
the two facts the day exists for — that the gradient wins a sweep of 360
directions, and that it is perpendicular to a contour — plus the plane's
constant gradient, the bowl's outward-pointing one, the three zero gradients,
the `h^2` law and the U-curve. You do not write anything more for those; they
use the functions you already wrote.

## Exercises 2 to 8 — the predictions (`starter/answers.py`)

Fifty-one predictions. Replace each `None`. Almost every one can be done on
paper, and the ones that cannot are asking you to reason about a shape rather
than compute a number.

| # | Topic | What you are asked for |
| --- | --- | --- |
| 2 | Partial derivatives by hand | Eight: `df/dx` and `df/dy` for three surfaces, plus what the rounded `d` is for. |
| 3 | The gradient as a vector | Six: assembling it, its length, how many components it has, and what the length means. |
| 4 | Directional derivatives | Seven: rates along given bearings, the largest and smallest available, and which trigonometric function relates them. |
| 5 | Contours | Six: the shape of the contours, the angle to the gradient, and why the lab refuses to derive a contour direction by rotating a gradient. |
| 6 | Step size | Seven: the `h^2` law, the two error sources, and the best `h` for each of the two methods. |
| 7 | The zero gradient | Eight: three identical zero gradients, what they cannot distinguish, and what object you would need instead. |
| 8 | Models and cost | Nine: a three-parameter loss and its gradient by hand, the cost of a numerical gradient, and what autodiff changes. |

Work them out before running anything. A lab about derivatives whose answers
you can only get by running it is a lab that teaches you to trust output.

Two of these deserve a warning:

- **2.3** asks for `df/dx` of `xy` at the point `(1, 0)`. The answer is
  surprising, and 2.5 asks you what it does and does not imply.
- **4.6** asks whether a sweep of 360 directions will find *exactly* the
  largest possible rate of change. Think about what "360 directions" means
  before answering.

## What the numbers mean when you run it

```
206 passed                      finished
1 passed, 205 skipped           untouched
150 passed, 56 skipped          two thirds done, nothing wrong
149 passed, 1 failed, 56 skipped   one thing attempted and wrong
```

A failure is information, not a scolding. It prints your value and the correct
one side by side, and the assertion message usually names the specific mistake.
