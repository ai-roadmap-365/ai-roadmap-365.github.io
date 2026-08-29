# Troubleshooting — Day 105 lab

Every failure below is one that was actually hit while building this lab, or
one the tests were written specifically to catch. Each says what you will see,
what causes it, and how to confirm the fix.

---

## The whole image is half a pixel out

**You will see:** `test_1_11_halving_is_exactly_a_strided_slice` fails.
`warp_nearest` "nearly" works — a quarter turn looks right but is not exactly
`numpy.rot90` — and the Pillow comparison disagrees on most pixels rather than
none.

**Cause:** you left `SAMPLE_OFFSET` out of `warp_nearest_with_inverse`, or you
added it to one coordinate and not the other.

Every output pixel is a little square. Pixel `(x, y)` covers the region from
`(x, y)` to `(x + 1, y + 1)`, so its **centre** is at `(x + 0.5, y + 0.5)`, and
that centre is the point the transformation is evaluated at. Evaluate at the
corner instead and every result is displaced by half of whatever the
transformation does.

**Fix:**

```python
sx, sy = apply_point(inverse, (ox + SAMPLE_OFFSET, oy + SAMPLE_OFFSET))
```

**Confirm:** downscaling by exactly a half must equal `img[1::2, 1::2]` — note
the `1`, not `0`. Output pixel 0 has its centre at 0.5, which doubles to 1.0,
which floors to input pixel 1. If yours matches `img[0::2, 0::2]` instead, the
half is missing.

---

## `int()` or `round()` instead of `math.floor()`

**You will see:** most tests pass, but the Pillow comparison disagrees on a
scattering of pixels, and the disagreements cluster where source coordinates go
negative.

**Cause:** you want the input pixel whose *square contains* the sampled point.
That is `math.floor`.

- `int(-0.3)` is `0`. `math.floor(-0.3)` is `-1`. `int` truncates toward zero,
  so it maps two different half-pixel bands onto index 0 and silently duplicates
  a row and a column at the top-left edge.
- `round` is a different rule entirely — it snaps to the nearest *integer
  coordinate*, not to the containing pixel, and disagrees with `floor` on half
  of all inputs.

**Confirm:** `06_against_pillow.py` section 3 should report 510 of 510 matching
with 0 differing pixels. Anything else and one of these two is the cause.

---

## The picture moves the wrong way through Pillow

**You will see:** your own `warp_nearest` looks right, Pillow's output looks
like the mirror image of what you asked for, and translations go the opposite
direction.

**Cause:** Pillow's coefficients express the **output-to-input** map — the
inverse of the effect you see. Passing your matrix directly passes the inverse
of what you meant.

**Fix:** always go through `to_pillow_coefficients`, which inverts for you:

```python
coefficients = to_pillow_coefficients(matrix)   # NOT matrix's own six numbers
out = image.transform(size, Image.Transform.AFFINE, coefficients, ...)
```

**Confirm:** `to_pillow_coefficients(translation(1, 0))` must be
`(1.0, 0.0, -1.0, 0.0, 1.0, 0.0)`. The `c` is **negative one**. If yours is
`+1`, you skipped the inversion.

This is not a quirk to memorise; it is the whole reason the day exists. Pillow
needs the output-to-input direction because that is the only direction in which
every output pixel can be filled exactly once.

---

## Row 0 moved under a shear, and it should not have

**You will see:** you shear with a coefficient of 2.0, and the top row of the
image shifts by one pixel — but the mathematics says a shear multiplies by `y`,
and row 0 has `y = 0`.

**This is correct behaviour and not a bug.** Row 0's output pixels are sampled
at their centres, which are at `y = 0.5`, not `y = 0`. So the shear term
contributes `2.0 * 0.5 = 1.0`, and one whole pixel of shift is exactly right.

Day 102 noticed this and deliberately deferred it to this lab rather than
guessing at it. `06_against_pillow.py` section 2 settles it by measurement, and
Pillow does exactly the same thing.

**Confirm:** with `k = 0.5` and `k = 1.0`, row 0 does not move. With `k = 2.0`
it moves by 1. The rule is `shift = -floor(0.5 - k * 0.5)`.

---

## `pytest starter` reports failures instead of skips

**You will see:** `NotImplementedError` in the failure output rather than a
skip, or an import error.

**Two causes.**

1. **You deleted a `raise NotImplementedError` without writing a body.** The
   skip mechanism works by catching that exception; remove it and the test sees
   `None` returned and fails on the assertion instead. Either write the
   function or leave the `raise` in place.

2. **You ran pytest from inside `starter/`.** Run it from the **lab
   directory**:

   ```bash
   cd labs/sections/math-statistics-and-data/day-105-transforming-images-with-matrices
   .venv/bin/pytest starter -q
   ```

**Confirm:** an untouched checkout prints `1 passed, 53 skipped`.

---

## The starter tests pass work you have not written

**You will see:** `pytest` (with no argument) reports far fewer skips than
`pytest starter` does — possibly `0 skipped`.

**Cause:** a missing or edited `conftest.py`. `examples/` and `starter/` both
contain modules named `warp` and `pattern`. pytest imports test files by
putting their directory on `sys.path`, so collecting both suites at once lets
whichever `warp` was imported first serve both — and your unwritten exercises
then "pass" against the reference solution. A wrong answer with a green tick on
it is the worst kind of test result.

**Fix:** restore both `conftest.py` files.

```bash
git checkout -- starter/conftest.py examples/conftest.py
```

**Confirm:** section 4 of `tests/run_tests.sh` checks exactly this — the skip
count must be identical whether you run `pytest starter` or bare `pytest`.

---

## `pytest not found` from the harness

**You will see:**

```
FAIL: pytest not found.
```

**Cause:** the virtual environment was never created, or you are running the
harness from somewhere else.

**Fix:** either install into `.venv` inside the lab:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

or point the harness at an existing pytest:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The harness uses the `python3` sitting beside that `pytest`, because that is
the interpreter NumPy and Pillow are installed into. If either is not
importable from it, the harness stops and says so rather than quietly skipping
checks.

---

## `numpy is not importable` or `PIL is not importable`

**Cause:** you installed the packages into a different interpreter from the one
that owns the `pytest` being used — most often by running `pip install` with a
system `pip` while the harness found `.venv/bin/pytest`, or the reverse.

**Fix:**

```bash
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy, PIL; print(numpy.__version__, PIL.__version__)"
```

Note that the package is installed as `pillow` and imported as `PIL`. That is
historical — Pillow is a fork of the original Python Imaging Library and kept
the import name for compatibility — and it is not a typo in this lab.

---

## The versions do not match `requirements.txt`

**You will see, in section 1 of the harness:**

```
FAIL: installed pillow matches requirements.txt (expected [12.3.0], got [11.2.1])
```

**This is the harness doing its job**, not a failure of your work. It reads the
installed version rather than assuming it, so a mismatch is reported at the top
of the run instead of surfacing later as a confusing diff.

**Fix:** `.venv/bin/pip install -r requirements/requirements.txt` again, or
accept the difference knowingly. Read `expected-output/FIELDS.md` first — one
of the lab's measured results, the list of eight disagreeing rotation angles,
is genuinely tied to this Pillow build.

---

## My eight disagreeing angles are different from the lab's

**You will see:** section 5 of the harness fails on
`8 of the 360 whole-degree rotations DO disagree, and they are named`.

**This may not be your fault, and the lab says so.** Which side of an exact
floating-point tie you land on depends on the order the additions happen in,
which depends on the compiler and the build of Pillow. The list
`[30, 60, 120, 150, 210, 240, 300, 330]` was measured on the authoring machine
with Pillow 12.3.0.

The claim that actually matters is the check beside it: **every** disagreeing
sample must land within 1e-9 of a pixel boundary. If that check passes and only
the angle list differs, nothing is broken — your build breaks ties slightly
differently. Record what you observed; `expected-output/FIELDS.md` explains the
distinction between the two claims.

If the boundary check *also* fails, something real is wrong — most likely
`floor` versus `round`, above.

---

## The forward-mapping holes look wrong

**You will see:** `test_1_10_forward_mapping_leaves_22_holes_on_a_30_degree_rotation`
fails with some other number.

**Do not "fix" the holes.** They are the exercise. Common causes of the wrong
*count*:

- You returned `written` instead of `~written`. The mask must be True where
  nothing was written.
- You wrote from the input pixel's corner rather than its centre. Use
  `(x + SAMPLE_OFFSET, y + SAMPLE_OFFSET)` here too — the same half, in the
  same place, for the same reason.
- You added a second pass to fill the gaps. That is the instinct the exercise
  exists to argue against; inverse mapping removes the problem instead of
  patching it.

---

## `SingularTransform` raised on a transformation that looks fine

**Cause:** the determinant of the linear part is zero, meaning the
transformation flattens the picture onto a line. `scaling(2, 0)` is the usual
accident.

Inverse mapping *needs* the inverse, so such a transformation cannot be applied
at all — the error arrives before any pixel is touched, which is the right time
for it. `SingularTransform` subclasses `ValueError`, matching
`numpy.linalg.LinAlgError`, so an existing `except ValueError` catches it.

---

## Something is left behind after a run

Section 7 of the harness checks for `__pycache__`, `.pytest_cache` and any
image file anywhere under the lab. If it reports one:

```bash
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
rm -rf .pytest_cache
```

The harness exports `PYTHONDONTWRITEBYTECODE=1` and passes `-p no:cacheprovider`
to pytest, so a normal run leaves nothing. An image file appearing under the
lab means either something was committed by mistake or a script wrote one and
did not clean up — the lab's own PNG round trip uses
`tempfile.TemporaryDirectory` and cannot leave a file behind.
