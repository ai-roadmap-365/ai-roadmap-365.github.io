# Day 105 lab — Rotate It Yourself

One idea holds this whole lab together:

> **An image is a matrix, so you transform its COORDINATES, not its pixels.**

Everything below is a consequence of that sentence. You will rotate, scale,
shear and flip a picture with matrices you wrote yourself, and then hand the
identical six numbers to Pillow and watch a library maintained since 2010 agree
with you pixel for pixel.

Work in order; each exercise uses the one before it.

Check yourself at any point, from the **lab directory** (the one above this
file):

```bash
.venv/bin/pytest starter -q
```

Unattempted work is **skipped**, not failed. On an untouched checkout you will
see `1 passed, 53 skipped`. When it says `54 passed`, you are finished.

---

## The picture

Nothing is downloaded. `pattern.py` builds the test image from arithmetic — a
capital F on a 9 by 9 greyscale grid:

```
.######..
.##......
.##......
.##......
.####....
.##......
.##......
.##......
.##.....o
```

`.` is 0, `#` is 255, `o` is 96. It is an F for one reason: an F is asymmetric
under every operation in this lab. A square survives a horizontal flip
unchanged, so a square would let a broken flip pass its own test. An F does not
survive anything.

Print your own results the same way at any time:

```python
import pattern
print(pattern.as_text(my_image))
```

Anything that is not one of the four known grey levels prints as `?`, which is
how an interpolation artefact announces itself.

---

## The two conventions, and the one that will trip you

**Rows are y, columns are x.** A NumPy array is indexed `img[row, column]`,
which is `img[y, x]`. All week a point has been written `(x, y)`. Those are the
same two numbers in the opposite order, and swapping them does not raise — it
silently reads the wrong pixel. This is the single most common source of
confusion in the subject.

**y grows downward.** Row 0 is the top of the picture. Day 102's graphs had y
growing upward. Nothing about the matrices changes, but a counter-clockwise
rotation matrix turns an image *clockwise* on screen. That is not a sign error
and you should not "fix" it.

---

## Exercise 1 — `warp.py` (twelve functions)

Write the twelve functions marked `raise NotImplementedError`. Each docstring
gives the derivation and a worked example you can check on paper. Use only
`math` for the matrix arithmetic; NumPy is fine for holding pixels, which is
what it is for.

| Step | Function | What it must do |
| --- | --- | --- |
| 1.1 | `translation` | The reason homogeneous coordinates exist. Add a constant by multiplying the third coordinate. |
| 1.2 | `scaling` | Derive it: where does one step right go when the picture stretches? |
| 1.3 | `rotation` | Day 102's matrix, dropped into the top-left of a 3 by 3. |
| 1.4 | `shear_x` | Derive it: the sideways push is proportional to the **height**. |
| 1.5 | `flip_horizontal` | A mirror **plus** a translation, in one matrix. Getting this wrong sends the picture off the left edge. |
| 1.6 | `matmul` | The 3 by 3 product, by hand. `compose` is written for you on top of it. |
| 1.7 | `apply_point` | The third coordinate is always 1, so you never build the triple. |
| 1.8 | `determinant` | The area factor. Compute it directly so whole numbers stay exact. |
| 1.9 | `invert` | Use the affine structure, not brute force. Raise `SingularTransform` at a determinant of 0. |
| 1.10 | `warp_forward` | Forward mapping, **done wrong on purpose**. Return the holes; do not patch them. |
| 1.11 | `warp_nearest_with_inverse` | The real one. Loop over the OUTPUT. |
| 1.12 | `to_pillow_coefficients` | Read the six numbers off the **inverse**. |

Seven helpers are written for you at the bottom of the file — `identity`,
`rotation_quarter_turns`, `shear_y`, `flip_vertical`, `about_centre`,
`matrices_close` and `coefficients_to_matrix`. Read them; the tests use them,
and `about_centre` in particular is worth understanding because it is three of
your matrices folded into one.

### The three places people lose an afternoon

**1.10 is meant to fail.** `warp_forward` leaves 22 of 81 output pixels
unwritten on a 30 degree rotation, including pixels punched through the middle
of solid ink. That is the correct answer. Do not add a second pass to fill
them; the whole point of 1.11 is that turning the loop inside out makes the
problem disappear rather than needing a patch.

**1.11 needs the half.** Every output pixel is a little square, and you sample
its **centre**, `(x + 0.5, y + 0.5)`, not its corner. `SAMPLE_OFFSET` is
already defined at the top of `warp.py`. Leave it out and every result is half
a pixel adrift — which looks like a mysterious blur rather than like an offset,
and which is exactly why `test_1_11_halving_is_exactly_a_strided_slice` exists.

**1.11 needs `math.floor`.** Not `round`, not `int`. You want the input pixel
whose *square contains* the point. `int` truncates toward zero, which is wrong
for negative coordinates; `round` is a different rule that will disagree with
Pillow on half the cases.

---

## Exercises 2 to 6 — `answers.py` (predictions)

Twenty-six predictions, every one of which can be reasoned out on paper before
you run anything. Replace each `None` with your answer. Anything still `None`
is skipped rather than failed, so your score only ever counts work you actually
attempted.

| Exercise | About |
| --- | --- |
| 2 | An image is a matrix, and the `(row, column)` versus `(x, y)` trap. |
| 3 | Why forward mapping leaves holes, and why the fill-valued pixels after inverse mapping are *not* holes. |
| 4 | Inverse mapping, and four results that are exactly checkable against NumPy. |
| 5 | Why no 2 by 2 matrix can translate, and what composition buys you. |
| 6 | Pillow's coefficient direction, and where exactly it takes its sample. |

Exercise 6 is the one to slow down on. Question 6.4 asks by how many pixels row
0 moves under a shear whose coefficient is 2.0. The mathematics says row 0 has
`y = 0` and therefore cannot move. Predict the number *before* you run
anything, then check it. Day 102 raised this question and deliberately left it
open; today you settle it.

---

## Finishing

```bash
bash tests/run_tests.sh
```

The harness runs the six reference scripts, both pytest suites, and a set of
checks that read real values rather than reading source. It prints
`N checks, 0 failure(s)` and exits 0 when everything holds.

If you want to see the finished versions, `examples/` has them — `warp.py`
there is the complete implementation and the six numbered scripts walk through
every result in this brief with the numbers printed. Read them **after** you
have attempted the exercises; reading them first turns a lab into a
transcription task.
