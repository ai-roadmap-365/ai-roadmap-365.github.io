# What in the captured output may legitimately differ on your machine

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-16, offline, with numpy 2.5.2 and pytest 9.1.1 on
CPython 3.14.0. If your run differs in one of the ways listed here, nothing is
wrong. If it differs in any other way, something is.

## Will differ, and does not matter

| What | Where | Why |
| --- | --- | --- |
| Elapsed times, such as `80 passed in 0.08s` | `reference-tests.txt`, `starter-progress.txt`, `test-run.txt` | Wall-clock timing. Nothing in this lab asserts on a duration, deliberately: a test that asserts milliseconds is flaky on a slower machine. |
| The `platform` line, for example `macOS-26.5.2-arm64-arm-64bit-Mach-O` | `test-run.txt` section 1 | It reports your operating system, release and processor architecture. Linux prints something quite different, and that is expected. |
| The `python` and `pytest` version lines | `test-run.txt` section 1 | Only CPython 3.14.0 and pytest 9.1.1 were run here, so those are the only versions this lab can honestly claim. |
| The pass/skip glyph line, such as `.sssssss...` | `starter-progress.txt` | Its length tracks the number of collected tests. The counted summary underneath is the part to compare. |
| Your own progress score | `starter-progress.txt` | The captured file shows an untouched checkout: `1 passed, 53 skipped`. As you complete exercises, passes replace skips. That is the file changing because you changed, not because anything broke. |

## Must NOT differ

| What | Where | Why it is fixed |
| --- | --- | --- |
| Every matrix, point, area and determinant | all six `0*-*.txt` files | They are computed from a handful of small whole numbers with no randomness beyond one fixed seed, no clock and no file system involved. A different number means different arithmetic. |
| `80 passed` | `reference-tests.txt` | The reference suite has eighty tests. A different count means tests failed to collect. |
| `64 checks, 0 failure(s).` | `test-run.txt` | The harness runs a fixed number of checks. |
| The numpy version line `numpy    2.5.2` | `test-run.txt` section 1 | Pinned in `requirements/requirements.txt`, and section 1 compares the installed version against that file rather than trusting it. |
| `ValueError: operands` — absent | everywhere | This lab raises exactly one library exception on purpose, `numpy.linalg.LinAlgError: Singular matrix`, and asserts its class and its message. |

## The two numbers that look like errors and are not

**`6.123233995736766e-17`.** This is `cos(pi / 2)`, and it appears wherever a
quarter turn is printed raw — most visibly in
`02-building-the-transformations.txt` section 5. It is not a bug and it is not
a NumPy quirk: `pi` cannot be stored exactly in binary floating point, so the
value actually passed to `cos` is not quite pi/2, and its cosine is not quite
zero. Everything in this lab that compares a rotated coordinate uses a stated
tolerance of `1e-12` for exactly this reason, and one reference test asserts
the *inexactness itself*, so that if some future library ever made it exact the
suite would say so rather than keeping a comment that had quietly stopped being
true.

The same applies to `sin(30 degrees)`, which is `0.49999999999999994` rather
than `0.5`.

**`7.000000000000001`.** This is `numpy.linalg.det` on the matrix
`[[3, -1], [1, 2]]`, whose determinant is exactly 7 and which the lab's own
`determinant` function returns as exactly `7.0`. The difference is real and it
is explained in section 8 of `05-determinant-inverse-rank.txt`: the from-scratch
version computes `a*d - b*c` directly, which for four whole numbers is exact,
while `numpy.linalg.det` factorises the matrix first — the general routine that
also works at 500 by 500, where the direct formula is not an option — and that
factorisation rounds.

Neither is wrong. NumPy trades a last-bit error on a tiny input for a method
that stays usable on a large one, which is a good trade and worth knowing
about. It is also why you compare determinants with a tolerance rather than
with `==`. This difference was observed on this machine with numpy 2.5.2; no
claim is made about other versions or other processors, because none were run.

## The one place a wider tolerance is used, and why

`06-the-limit-of-linear.txt` compares twenty transformations applied one at a
time against the same twenty multiplied together first, and allows a relative
difference of `1e-9` rather than `1e-12`. The reason is stated in the script
itself: the entries are not small whole numbers, the two routes multiply them
in a different order, floating-point addition is not associative, and twenty
layers of rounding accumulate. Demanding the last bit there would be demanding
something arithmetic does not promise. The conclusion — that the stack collapses
to one matrix — does not depend on the last few digits.

## Reproducing these files

From the lab directory, after the one-time install:

```bash
cd examples && ../.venv/bin/python3 01_columns_are_landings.py; cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
.venv/bin/pytest starter -q -p no:cacheprovider
bash tests/run_tests.sh
```

The scripts in `examples/` are run from inside `examples/` because they import
`transforms.py` and `shapes.py` from beside themselves.
