"""Three operations, each written twice. Same answer, different speed.

Run from inside examples/:

    ../.venv/bin/python3 03_same_answer_faster.py

The claim under test: a vectorised expression is the SAME computation as the
loop, not a different one. Every element goes through the same IEEE-754
operation in the same order; only the machinery around it changes. So the two
results are compared with `==`, elementwise, over a million elements -- not
with a tolerance, because a tolerance would hide the very thing being shown.

The timings are then measured, printed with their spread, and deliberately NOT
asserted on. One machine, one day. The test suite asserts the SHAPE of the gap
-- at least twenty times -- which is a claim that survives a slower laptop.
"""

import platform
import sys

import numpy as np

import dataset
from vectorize import (
    clip_loop,
    clip_vec,
    median_seconds,
    roots_loop,
    roots_vec,
    scale_and_offset_loop,
    scale_and_offset_vec,
    speedup,
    time_call,
)

REPEATS = 5


def report(name: str, loop_result, vec_result, loop_times, vec_times) -> float:
    """Print one operation's agreement and its two timings."""
    loop_array = np.array(loop_result)
    identical = bool(np.array_equal(loop_array, vec_result))
    factor = speedup(loop_times, vec_times)
    print(f"  {name}")
    print(f"    elementwise identical over {loop_array.size:,} elements : {identical}")
    print(f"    loop  ms  {[round(t * 1000, 2) for t in loop_times]}")
    print(f"    array ms  {[round(t * 1000, 3) for t in vec_times]}")
    print(f"    median loop {median_seconds(loop_times) * 1000:8.2f} ms")
    print(f"    median array{median_seconds(vec_times) * 1000:8.3f} ms")
    print(f"    speedup     {factor:8.1f}x")
    print()
    assert identical, f"{name}: the two routes must agree exactly"
    return factor


def main() -> None:
    print("03_same_answer_faster.py")
    print("=" * 70)

    # -- 1. The machine this was measured on ----------------------------------
    print()
    print("1. What this was measured on, so the numbers can be read honestly")
    print("-" * 70)
    print(f"  python    {platform.python_version()}")
    print(f"  numpy     {np.__version__}")
    print(f"  platform  {platform.platform()}")
    print(f"  machine   {platform.machine()}")
    print(f"  elements  {dataset.N_BIG:,}")
    print(f"  repeats   {REPEATS} per operation, median reported")
    print()
    print("  Your figures will differ. The ratio is the durable part; the")
    print("  milliseconds are one machine on one day.")

    values = dataset.big_values()
    as_list = values.tolist()
    assert len(as_list) == dataset.N_BIG

    # -- 2. The three operations ----------------------------------------------
    print()
    print("2. Three operations, each computed twice")
    print("-" * 70)
    print()

    factors = []

    factors.append(
        report(
            f"scale and offset:  {dataset.SCALE_M} * x + {dataset.SCALE_C}",
            scale_and_offset_loop(as_list, dataset.SCALE_M, dataset.SCALE_C),
            scale_and_offset_vec(values, dataset.SCALE_M, dataset.SCALE_C),
            time_call(
                lambda: scale_and_offset_loop(as_list, dataset.SCALE_M, dataset.SCALE_C),
                REPEATS,
            ),
            time_call(
                lambda: scale_and_offset_vec(values, dataset.SCALE_M, dataset.SCALE_C),
                REPEATS,
            ),
        )
    )

    factors.append(
        report(
            "square root:       math.sqrt(x)  vs  np.sqrt(a)",
            roots_loop(as_list),
            roots_vec(values),
            time_call(lambda: roots_loop(as_list), REPEATS),
            time_call(lambda: roots_vec(values), REPEATS),
        )
    )

    factors.append(
        report(
            f"clip:              hold x inside [{dataset.CLIP_LO}, {dataset.CLIP_HI}]",
            clip_loop(as_list, dataset.CLIP_LO, dataset.CLIP_HI),
            clip_vec(values, dataset.CLIP_LO, dataset.CLIP_HI),
            time_call(lambda: clip_loop(as_list, dataset.CLIP_LO, dataset.CLIP_HI), REPEATS),
            time_call(lambda: clip_vec(values, dataset.CLIP_LO, dataset.CLIP_HI), REPEATS),
        )
    )

    print(f"  slowest speedup measured here: {min(factors):.1f}x")
    print(f"  fastest speedup measured here: {max(factors):.1f}x")
    assert min(factors) > 20.0, (
        "the tests assert 20x, which is a claim about the shape of the gap"
    )

    # -- 3. Why identical rather than close -----------------------------------
    print()
    print("3. Why those comparisons used == and not a tolerance")
    print("-" * 70)
    print(f"  2.5  is exactly representable in binary: {2.5 == float.fromhex('0x1.4p+1')}")
    print(f"  1.25 is exactly representable in binary: {1.25 == float.fromhex('0x1.4p+0')}")
    print()
    print("  Each element goes through one multiply and one add, in the same")
    print("  order, on the same 64 bits, on the same processor. There is no")
    print("  room for a difference and so none appears. If a vectorised")
    print("  rewrite of yours needs a tolerance, that is worth a second look:")
    print("  it means the two versions are not doing the same arithmetic.")

    # -- 4. Where the loop's time actually goes -------------------------------
    print()
    print("4. What the loop spends its time on")
    print("-" * 70)
    one = as_list[0]
    print(f"  one element as a Python float object : {sys.getsizeof(one)} bytes")
    print(f"  one element inside the array         : {values.itemsize} bytes")
    print()
    print("  Per element, the loop does roughly this: fetch a pointer, follow")
    print("  it, check the object's type, unbox the double, multiply, add, box")
    print("  the result into a NEW float object, store a pointer to it. Seven")
    print("  operations of bookkeeping around one of arithmetic.")
    print()
    print("  The array version fetches eight bytes at a known offset,")
    print("  multiplies, adds, stores eight bytes. No type check, because the")
    print("  dtype already settled that question once for the whole array.")
    print("  THAT is what a dtype buys, and it is why the two facts -- fixed")
    print("  dtype and contiguous block -- are the same fact wearing two hats.")

    # -- 5. It is still a loop ------------------------------------------------
    print()
    print("5. The loop did not disappear")
    print("-" * 70)
    print("  np.sqrt(a) still visits every one of the million elements. The")
    print("  loop moved from CPython's bytecode interpreter into compiled C")
    print("  inside NumPy, where the processor can also work on several")
    print("  elements per instruction. Vectorised does not mean 'no loop', it")
    print("  means 'not YOUR loop'.")
    print()
    print("  Which is also the cost: you can no longer put a print, a")
    print("  breakpoint or an early exit inside it. Script 07 is about when")
    print("  that trade is a bad one.")

    print()
    print("=" * 70)
    print("03_same_answer_faster.py: every assertion held.")


if __name__ == "__main__":
    main()
