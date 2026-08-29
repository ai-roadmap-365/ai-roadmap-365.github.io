# Watch the Slope Settle — the brief

Seven exercises. Do them in order; each one uses the one before.

Work from the LAB DIRECTORY (the one above this file) and check yourself as
often as you like:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `1 passed, 99 skipped`. A skip means "not
attempted". A failure means "attempted and wrong", and prints both your answer
and the real one. When it prints `100 passed`, you are finished.

**Do not read `examples/` until you have tried.** The reference is there for
afterwards, and reading it first turns a lab into a transcription exercise.

---

## Exercise 1 — average rates (`derivatives.py`, functions 1.1 and 1.2)

Write `average_rate` and `shrinking_slopes`.

`average_rate(f, a, b)` is rise over run and nothing more. The only interesting
decision is what to do when `a == b`: raise `ZeroDivisionError` with a message
containing the words "interval with width". Do not return 0.0 and do not return
nan. That question genuinely has no answer, and the whole day exists because it
does not.

`shrinking_slopes` is one line built on `average_rate`. Feed it widths that get
smaller and the returned numbers settle. That settling is the limit.

## Exercise 2 — the difference quotients (`derivatives.py`, 2.1 to 2.4)

Write `forward_difference`, `backward_difference`, `central_difference` and
`second_difference`.

Three warnings, all of which have a test named after them:

- The central difference divides by `2 * h`, not by `h`. Forgetting the 2
  doubles every answer you will ever get from it, and doubling is not obviously
  wrong when you do not already know the right value.
- The second difference divides by `h * h`, not by `h`.
- Do not differentiate anything symbolically. These functions may call `f` at
  points you choose and do arithmetic on what comes back, and nothing else.
  That is the honest situation you are in whenever the function is a model
  rather than an equation.

## Exercise 3 — the error curve (`derivatives.py`, 3.1 to 3.3)

Write `error_curve`, `best_step` and `is_u_shaped`.

`error_curve` takes a `rule` — one of your own functions above, passed in as a
value — and returns the absolute error against a slope you already know. It is
only usable when you know the right answer, which is exactly why the lab
measures it on `e**x`: you cannot see the shape of an error you cannot compute.

`is_u_shaped` must be deliberately tolerant. Rounding error near the bottom is a
random walk, not a smooth curve, and a test demanding a monotone descent would
be a test demanding something untrue.

Then run it on the real 27-point grid from `dataset.U_WIDTHS`, which spans
h = 1e-1 down to h = 1e-14, and look at where the bottom is. It is not at the
small end, and understanding why is the point of the day.

## Exercise 4 — flat points (`derivatives.py`, 4.1)

Write `classify_stationary_point`.

Four possible answers, and the fourth is the one that matters: `"undecided"`.
A zero first derivative says the ground is level. It does not say whether you
are at the bottom of a valley, the top of a hill, or on a flat step partway down
a slope. The second derivative resolves two of those three. When it is zero as
well, nothing here can separate `x**3` at 0 — a step — from `x**4` at 0, which
is a genuine minimum.

A test asserts that you return `"undecided"` for `x**4` at 0. Returning
`"minimum"` there would be right by accident, and the suite treats being right
by accident as being wrong.

## Exercises 2 to 7 — the predictions (`answers.py`)

Forty-two predictions, in `answers.py`. Work each one out **before** running
anything. Nearly all can be done on paper.

Two notes on format. Where an option is written across two lines in a comment,
it is one string with single spaces — type it on one line. And where a question
asks for an exception, give the class itself (`ZeroDivisionError`), not a string
naming it.

---

## Order that works

1. Write `average_rate` and `shrinking_slopes`, run the suite, watch nine skips
   turn into passes.
2. Answer exercise 2's predictions while the arithmetic is fresh.
3. Write the three first-difference rules and `second_difference`.
4. Answer exercises 3, 4 and 5.
5. Write `error_curve`, `best_step` and `is_u_shaped`, then run them on the real
   27-point grid and look at the numbers before answering exercise 6.
6. Write `classify_stationary_point` and answer exercise 7.
7. Only now, read `examples/`, run the seven scripts, and see what you would
   have written differently.

## When you are done

```bash
bash tests/run_tests.sh
```

97 checks, and section 6 of it deliberately breaks one expectation to prove the
harness can go red. A green suite proves nothing until you have watched it fail.
