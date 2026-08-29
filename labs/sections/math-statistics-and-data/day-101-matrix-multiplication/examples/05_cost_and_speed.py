"""Association order, and the loop against NumPy at a size where it shows.

Run from inside this directory:

    ../.venv/bin/python3 05_cost_and_speed.py

READ THIS BEFORE READING THE NUMBERS. The durations printed below are from one
machine on one day, and yours will differ — possibly by a lot. They are printed
because a measurement you can see beats an assertion you have to trust, not
because the milliseconds mean anything. What matters, and what the tests
actually assert, is the SHAPE of the gap: a ratio in the hundreds or thousands,
growing with the size of the problem. No test in this lab asserts a duration.
"""

import time

import numpy as np

from dataset import BIG_CHAIN, BIG_LEFT_FIRST, BIG_RATIO, BIG_RIGHT_FIRST
from dataset import SMALL_CHAIN, SMALL_LEFT_FIRST, SMALL_RIGHT_FIRST
from matmul import chain_costs, matmul_loops, multiplication_count

print("=" * 74)
print("1. Where the brackets go changes the arithmetic, not the answer")
print("=" * 74)

for chain, expected in [(SMALL_CHAIN, (SMALL_LEFT_FIRST, SMALL_RIGHT_FIRST)),
                        (BIG_CHAIN, (BIG_LEFT_FIRST, BIG_RIGHT_FIRST))]:
    m, n, p, q = chain
    left_first, right_first = chain_costs(m, n, p, q)
    assert (left_first, right_first) == expected
    print(f"  ({m}, {n}) @ ({n}, {p}) @ ({p}, {q})")
    print(f"      (AB)C  = {m}*{n}*{p} + {m}*{p}*{q}")
    print(f"             = {multiplication_count(m, n, p):,} + {multiplication_count(m, p, q):,}"
          f" = {left_first:,}")
    print(f"      A(BC)  = {n}*{p}*{q} + {m}*{n}*{q}")
    print(f"             = {multiplication_count(n, p, q):,} + {multiplication_count(m, n, q):,}"
          f" = {right_first:,}")
    print(f"      ratio  = {right_first / left_first:,.0f}x")
    print()

assert BIG_RIGHT_FIRST // BIG_LEFT_FIRST == BIG_RATIO
print("  The second chain is a low-rank adapter: a 4096-wide layer with an 8-wide")
print("  detour through A and back out through B, on a batch of 1024. Multiplying")
print("  A and B together first builds a full (4096, 4096) matrix and then hits")
print(f"  the whole batch with it — {BIG_RATIO} times the work for the identical answer.")
print("  Associativity is what makes both spellings legal. Counting is what tells")
print("  you which one to write.")

print()
print("  And a proof, on small enough shapes to check, that the answers really")
print("  are identical rather than merely close:")
rng = np.random.default_rng(101)
A = rng.integers(-5, 6, size=(4, 7))
B = rng.integers(-5, 6, size=(7, 2))
C = rng.integers(-5, 6, size=(2, 6))
left = (A @ B) @ C
right = A @ (B @ C)
print(f"      (A @ B) @ C and A @ (B @ C), shapes {left.shape} and {right.shape}")
print(f"      identical in every entry: {np.array_equal(left, right)}")
assert np.array_equal(left, right)
print("      These are integers, so 'identical' is exact. With floating point")
print("      (Day 70) the two orders can differ in the last bits, because")
print("      addition is not associative in floating point even though matrix")
print("      multiplication is associative in mathematics. Worth knowing before")
print("      it surprises you in a test.")
fA = A.astype(np.float64) / 3
fleft = (fA @ B) @ C
fright = fA @ (B @ C)
print(f"      in float64, exactly equal: {np.array_equal(fleft, fright)}; "
      f"close within 1e-9: {np.allclose(fleft, fright, atol=1e-9)}")
assert np.allclose(fleft, fright, atol=1e-9)

print()
print("=" * 74)
print("2. The loop against NumPy")
print("=" * 74)

SIZE = 200
print(f"  Two {SIZE} by {SIZE} matrices. The nested loop's innermost line will run")
print(f"  {multiplication_count(SIZE, SIZE, SIZE):,} times.")
print()

rng = np.random.default_rng(2026)
ints_left = rng.integers(0, 10, size=(SIZE, SIZE))
ints_right = rng.integers(0, 10, size=(SIZE, SIZE))
floats_left = ints_left.astype(np.float64)
floats_right = ints_right.astype(np.float64)
left_lists = ints_left.tolist()
right_lists = ints_right.tolist()


def best_of(fn, repeats=5):
    """Fastest of several runs — the run least disturbed by everything else."""
    best = float("inf")
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = fn()
        best = min(best, time.perf_counter() - start)
    return best, result


start = time.perf_counter()
loop_answer = matmul_loops(left_lists, right_lists)
loop_seconds = time.perf_counter() - start

int_seconds, int_answer = best_of(lambda: ints_left @ ints_right)
float_seconds, float_answer = best_of(lambda: floats_left @ floats_right)

assert loop_answer == int_answer.tolist(), "the two answers must be identical"
assert np.array_equal(float_answer, int_answer.astype(np.float64))
print("  All three answers are identical, entry for entry. Only the time differs.")
print()
print(f"      three nested loops in Python  : {loop_seconds:9.4f} s")
print(f"      NumPy @ on int64  (best of 5) : {int_seconds:9.6f} s"
      f"   {loop_seconds / int_seconds:>9,.0f}x faster than the loop")
print(f"      NumPy @ on float64 (best of 5): {float_seconds:9.6f} s"
      f"   {loop_seconds / float_seconds:>9,.0f}x faster than the loop")
print()
print("  Those durations are from one machine on one day and yours will differ.")
print("  The ratios are the part that travels, and even they vary with hardware")
print("  and with how your NumPy was built. No test in this lab asserts a time.")
assert loop_seconds / int_seconds > 10, "int64 should still beat the loop comfortably"
assert loop_seconds / float_seconds > 200, "float64 should beat the loop enormously"

print()
print("=" * 74)
print("3. The surprise in that table, and what it tells you")
print("=" * 74)
print("  The two NumPy rows are not the same speed, and the difference is not")
print("  small. On this machine, on this run:")
print()
print(f"      int64 divided by float64: {int_seconds / float_seconds:,.0f}x")
print()
print("  Same shapes, same values, same operator, same library. The only thing")
print("  that changed was the dtype, and the float version was dramatically")
print("  faster. That is not a quirk to file away. It is the single best piece")
print("  of evidence for what NumPy is actually doing:")
print()
print("  **BLAS only handles floating point.** BLAS — Basic Linear Algebra")
print("  Subprograms — is a decades-old interface with several competing")
print("  implementations, all compiled, all tuned to the exact processor they run")
print("  on, using vector instructions and cache-aware blocking and often several")
print("  cores. Its matrix-multiply routines are defined for float and complex")
print("  types and nothing else. So a float64 `@` is handed straight to BLAS,")
print("  while an int64 `@` falls back to NumPy's own compiled C loop — still far")
print("  better than interpreted Python, and still nowhere near BLAS.")
print()
print("  This is why the answer to 'why is NumPy fast?' is not 'because it is C'.")
print("  The int64 row IS C, and it is the slow NumPy row. NumPy is fast because")
print("  for the types that matter it stops being NumPy too, and calls out to a")
print("  library that people have been optimising since the 1970s.")
print()
config = np.__config__.show(mode="dicts") if hasattr(np.__config__, "show") else None
blas = {}
if isinstance(config, dict):
    blas = config.get("Build Dependencies", {}).get("blas", {}) or {}
if blas.get("name"):
    print("  This installation reports its own BLAS, read from the build config")
    print("  rather than assumed:")
    for key in ("name", "found", "detection method"):
        if key in blas:
            print(f"      {key:<17} {blas[key]}")
else:  # pragma: no cover - depends entirely on how NumPy was built
    print("  This installation did not report a BLAS name in its build config,")
    print("  so none is claimed here. That is a gap in what can be shown, not")
    print("  evidence that no BLAS is present.")
print()
print("  The practical consequence, and it is worth carrying: if a matrix")
print("  multiply is slower than you expected, check the dtype before you check")
print("  anything else. This is also why every framework you will meet stores")
print("  weights as float32 or a smaller float and never as integers.")

print()
print("=" * 74)
print("4. Does the gap hold as the problem grows?")
print("=" * 74)
print("  Both implementations do work proportional to n cubed, so the RATIO")
print("  should stay in the same broad range as n grows — the loop's overhead is")
print("  per operation, not per call. Whether it actually does is a measurement,")
print("  not a deduction, so here it is:")
print()
header = f"  {'n':>5}  {'operations':>14}  {'loop (s)':>10}  {'float64 (s)':>12}  {'ratio':>10}"
print(header)
ratios = []
for n in (40, 80, 160):
    a = rng.integers(0, 10, size=(n, n)).astype(np.float64)
    b = rng.integers(0, 10, size=(n, n)).astype(np.float64)
    al, bl = a.tolist(), b.tolist()
    start = time.perf_counter()
    matmul_loops(al, bl)
    t_loop = time.perf_counter() - start
    t_np, _ = best_of(lambda: a @ b)
    ratios.append(t_loop / t_np)
    print(f"  {n:>5}  {multiplication_count(n, n, n):>14,}  {t_loop:>10.4f}  "
          f"{t_np:>12.6f}  {t_loop / t_np:>9,.0f}x")

print()
print("  Read the ratio column, not the two before it. At the smallest size the")
print("  ratio is held down by NumPy's own fixed per-call overhead, which is a")
print("  real cost that simply stops mattering once the matrices are big enough.")
print("  If your machine shows something else, believe your machine — and then")
print("  work out why, which is a better exercise than the one this script set.")
assert all(r > 20 for r in ratios), "even the smallest size should show a wide gap"

print()
print("05_cost_and_speed.py: every assertion held.")
