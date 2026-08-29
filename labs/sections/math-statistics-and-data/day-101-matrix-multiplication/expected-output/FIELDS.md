# What may legitimately differ on your machine

Every file in this directory was captured from a real run on the authoring
machine on **16 August 2026**: macOS 26.5.2 (Apple Silicon, arm64), Python
3.14.0, numpy 2.5.2, pytest 9.1.1, bash 3.2.57.

The rule for reading them: **every number that came out of arithmetic must
match exactly. Every number that came out of a clock may not.** There are only
two kinds of exception in this lab, and they are listed below.

## Must match exactly, on any machine

If any of these differ on yours, something is genuinely wrong and it is worth
finding out what.

- Every matrix, vector and product printed by `01`, `02`, `03` and `04`. They
  are integer arithmetic on small numbers; there is no floating point involved
  and no room for platform variation.
- The multiplication counts and the chain costs in `02` and `05`
  (`7,500` / `75,000`, and `67,108,864` / `17,314,086,912`, a ratio of exactly
  `258`). These are products of integers, not measurements.
- Every shape, every exception **type**, and the substring
  `size 2 is different from 3` in NumPy's shape-error message.
- `70 passed` from the reference suite, and `1 passed, 56 skipped` from an
  untouched starter.
- `58 checks, 0 failure(s).` from `tests/run_tests.sh`, and exit status `0`.

## Will differ, and is supposed to

### 1. The timings in `05-cost-and-speed.txt`

Sections 2 and 4 of that script print durations. **Yours will not match, and no
test in this lab asserts one.** What was captured here:

| Measurement (200 by 200) | Captured | What it is |
| --- | --- | --- |
| three nested Python loops | `0.1957 s` | 8,000,000 interpreted multiply-and-adds |
| NumPy `@` on `int64` | `0.002479 s` | NumPy's own compiled loop — **not** BLAS |
| NumPy `@` on `float64` | `0.000037 s` | handed to BLAS |
| loop against `float64` | `5,223x` | the headline ratio |
| `int64` against `float64` | `66x` | the evidence that BLAS is float-only |

The scaling table in section 4 captured ratios of `1,144x`, `3,325x` and
`6,073x` at n = 40, 80 and 160. The rise across that column is not the loop
getting worse; it is NumPy's fixed per-call overhead mattering less as the
matrices grow.

Expect your own ratios to land anywhere from the low hundreds to the tens of
thousands. What should hold everywhere:

- float64 beats the Python loop by a very large factor;
- float64 beats int64 by a substantial factor, because BLAS has no integer
  matrix-multiply routine;
- the loop-to-NumPy ratio does not *fall* as the matrices get bigger.

The tests assert only wide margins — `> 50x` in `test_the_gap_is_wide_not_marginal`
and in section 5 of the harness — chosen far below what was measured so that a
slow or busy machine still passes.

### 2. The BLAS name in `05-cost-and-speed.txt`

Section 3 prints what your NumPy reports about its own build:

```
      name              accelerate
      found             True
      detection method  system
```

`accelerate` is Apple's implementation and is what a macOS build reports here.
A Linux wheel from the Package Index will usually report `openblas`. Either is
fine and neither is claimed to be better. If your installation reports no BLAS
name at all, the script says so plainly instead of inventing one — and in that
case the int64-against-float64 gap may be much smaller, which would be a
consistent and honest result rather than a broken one.

### 3. The platform line

Section 1 of `test-run.txt` prints `platform macOS-26.5.2-arm64-arm-64bit-Mach-O`
and the running Python, numpy and pytest versions. Yours will name your own
operating system. The two version *checks* immediately after it must still pass.

### 4. Your own progress score

`starter-progress.txt` was captured on an untouched checkout, so it reads
`1 passed, 56 skipped`. As you work, the passes rise and the skips fall. At
`57 passed` you are finished. A **failure** at any point is different from a
skip: it means you committed to an answer and it was wrong, and the output
prints both your value and the real one.

### 5. Test durations

pytest prints something like `in 0.14s`. That is a clock reading and carries no
meaning here.

## Not captured, and why

Nothing in this lab was run on Linux or Windows during authoring, so no output
from those platforms is reproduced. The commands are the same on Linux; see
`../troubleshooting.md` for the Windows path, which is described from the
documented behaviour of `venv` and stated as untested rather than implied to
have been checked.
