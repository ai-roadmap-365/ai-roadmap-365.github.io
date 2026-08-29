# Troubleshooting — Day 109

Every entry here was hit while building this lab, not imagined for the
document. They are in roughly the order you are likely to meet them.

---

## `ModuleNotFoundError: No module named 'gradients'`

You ran a reference script from the lab directory instead of from inside
`examples/`.

The scripts import `gradients` and `surfaces` from beside themselves, so Python
has to be started with `examples/` as the working directory:

```bash
cd examples
../.venv/bin/python3 03_steepest_ascent.py
cd ..
```

`pytest` is different — it puts the test file's own directory on `sys.path`
itself — so `.venv/bin/pytest examples -q` is run from the lab directory and
works.

---

## `ModuleNotFoundError: No module named 'numpy'`

You are running the system `python3` rather than the lab's. The install went
into `.venv`, and only `.venv/bin/python3` can see it:

```bash
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Expect `2.5.2`. If that fails too, the install did not happen — re-run the two
commands under "Installation" in `README.md`.

---

## Every partial derivative is exactly twice too big

You divided by `h` instead of by `2h`.

This is the most satisfying bug in the lab, because nothing looks obviously
wrong: the numbers are smooth, they scale correctly, they behave sensibly as
you move the point, and they are all wrong by the same factor. `df/dx` of
`x^2 + 3y^2` at `(2, 1)` comes out as `8.0` instead of `4.0`.

A central difference moves a total distance of `2h` — `h` up and `h` down — so
the rise is divided by `2h`. `test_1_1_partial_divides_by_two_h_not_by_h`
exists specifically to name this.

---

## The partials are right in `x` and nonsense in `y`, or vice versa

You modified the point in place instead of copying it, so the first call's
nudge is still there when the second one runs.

```python
base = np.asarray(point, dtype=float)
up = base.copy()      # both of these
down = base.copy()    # are copies
up[index] += h
down[index] -= h
```

Without the two `.copy()` calls, `up` and `down` are the same array, `f` is
evaluated at the same point twice, and the difference is zero.

A related symptom is that a test elsewhere starts failing for no reason: if you
mutated the caller's array, you changed a point that something else was still
using. `test_1_1_partial_does_not_mutate_the_point_it_was_given` catches it.

---

## `ValueError: the zero vector has no direction`

You asked for the unit vector of a gradient that is zero — which happens at
exactly the interesting points: the bottom of the bowl, the top of the dome,
the middle of the saddle.

This is the function working. A zero vector has no direction to preserve, and
returning `[nan, nan]` instead would push the failure somewhere much harder to
find. If you meet it while exploring, you have found a stationary point, and
`05_flat_ground_three_ways.py` section 3 is about what to do next: the gradient
has told you everything it knows, and what kind of point it is has to come from
somewhere else.

---

## A gradient assertion fails, but only far from the origin

Expected. This is script 05 section 1b, and it is a real limit rather than a
bug.

The gradient of `3x - 2y + 5` is `(3, -2)` everywhere. At `(1, 1)` the
numerical estimate is right to eleven decimal places. At `(1000, -1000)` it is
out by about `5e-8`, which breaks the lab's `1e-8` tolerance. At
`(10000000, -10000000)` it has lost its fourth decimal place.

Nothing about the calculus changed. `f` is worth fifty million at that last
point, each stored value carries a relative error of about one machine epsilon,
and dividing that absolute error by `2h = 2e-5` multiplies it by fifty
thousand. The bound is `eps * |f| / 2h`, and the lab measures it agreeing with
the observed error across seven orders of magnitude.

**Do not widen the tolerance to make it pass.** `security.md` explains why that
particular fix is worse than the failure. Scale your inputs, use a relative
tolerance, or accept that numerical differentiation has a working range.

---

## The steepest-ascent sweep misses the gradient bearing by 0.4349 degrees

Expected, and the number is not arbitrary.

The sweep samples 360 bearings, one per whole degree. The bowl's gradient at
`(1, 1)` is `(2, 6)`, whose bearing is `arctan(3) = 71.5651` degrees. The
nearest whole degree is 72. The gap is `0.4349`.

The sampling can never do better than half a degree, so a gap of up to 0.5 is
the correct behaviour and the lab's `ANGLE_TOL_DEGREES` is 1.0 to leave a
little room. If you want a smaller gap, sample more finely: `sweep_directions(f,
point, n=3600)` gets it under 0.05.

Five of the seven rows in that table show the *identical* 0.4349, which reads
like a copy-paste error and is not. `expected-output/FIELDS.md` explains it: all
five bearings are arctangents of ratios of the same small whole numbers and
differ by exact multiples of 45 degrees, so a whole-degree grid misses them all
by the same amount.

---

## A finer sweep gives exactly the same gap, not a smaller one

Also expected, and this one caught a test that had been written to assert the
wrong thing.

At `(1, 1)` on the bowl, a 60-direction sweep (every 6 degrees) and a
360-direction sweep (every 1 degree) both land on bearing 72, because 72 is a
multiple of both 6 and 1. So both leave exactly 0.4349 degrees.

Sampling more finely guarantees a smaller *bound*, not a smaller gap at any
particular bearing. The reference suite asserts the bound — that the gap never
exceeds half the sampling step — which is the claim that is actually true.

---

## The contour dot product is not zero

Expected, and the shrinking is the evidence rather than the smallness.

The gradient is perpendicular to the *tangent* of the contour. What the lab can
actually compute is a *chord* between two points a distance `delta` apart along
the contour, and a chord is tilted away from the tangent by an angle of roughly
`delta`. So the dot product is of order `delta`, not zero.

At `delta = 1e-2` it is about `4.7e-3`; at `1e-3` about `4.7e-4`; at `1e-4`
about `4.7e-5`. Divide the step by ten, divide the dot product by ten. That
first-order shrink is what "it goes to zero" looks like when every step you can
take is finite.

If you want an exact zero, use the exact tangent instead of a chord — section 4
of `04_perpendicular_to_the_contour.py` does, and gets `0.000e+00` with no
tolerance at all.

---

## `numpy.gradient` disagrees with your gradient at the edge of a grid

Expected, and worth knowing before it costs you an afternoon.

`numpy.gradient` uses a second-order central difference in the interior of the
array and, **by default**, a first-order one-sided formula at the boundary. On
a grid sampling `x^2 + 3y^2`, every interior value is exact and the corner
comes out `(0.5, 1.5)` where `(0, 0)` is correct.

Pass `edge_order=2` and the corner becomes exact.

More broadly, the two functions are answering different questions.
`numpy.gradient` differences an array you already have and cannot be asked for
a value between grid points; the lab's `gradient` differences a function it can
call anywhere and chooses its own step. On a cubic, NumPy's error is the grid
spacing squared — `0.25` here, because the spacing is `0.5` — and there is
nothing you can do about it without resampling.

---

## The starter suite says `1 passed, 205 skipped` and I have written things

Check which file you edited. A skip means the value is still `None` in
`answers.py`, or the function still raises `NotImplementedError` in
`gradients.py`. If you have written a function and its tests still skip, the
`raise NotImplementedError(...)` line is probably still there underneath your
code.

---

## Both suites pass, but the starter tests pass work I have not done

That would mean the import guard has been removed. Both `examples/` and
`starter/` contain modules called `gradients` and `surfaces`, and pytest puts
each test file's directory on `sys.path` — so a combined run could import the
reference `gradients` and hand it to the starter tests, which would then report
unwritten exercises as passing.

Each directory's `conftest.py` prevents that. Do not delete either one. Section
4 of `tests/run_tests.sh` proves the guard still works by comparing the skip
count from `pytest starter` against the skip count from a combined `pytest`;
they must be identical.

---

## `__pycache__` directories keep appearing

Set `PYTHONDONTWRITEBYTECODE=1` before running things by hand, as the harness
does, or clear them up afterwards:

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
```

Note the `-path ./.venv -prune`. NumPy and pytest ship hundreds of their own
`__pycache__` directories inside the virtual environment; those are theirs, not
mess this lab made, and deleting them would only slow your next import. Section
7 of the harness prunes `.venv` for the same reason, and includes a check that
the prune is genuinely in effect.

---

## Windows

Not run here, and the lab will not pretend otherwise.

The Windows Subsystem for Linux is the recommended route and the instructions
apply unchanged. Under Git Bash, replace `.venv/bin/python3` with
`.venv/Scripts/python.exe` and `.venv/bin/pytest` with
`.venv/Scripts/pytest.exe`. The bash harness needs a bash; PowerShell will not
run it.

Nothing in the lab is platform-specific — it is arithmetic — so the numbers
should be identical apart from the platform line and the roundoff digits noted
in `expected-output/FIELDS.md`.
