"""Missing values, and the honest limits of the habit this lab is teaching.

Run from inside examples/:

    ../.venv/bin/python3 07_nan_and_when_not_to_vectorise.py

Two claims under test.

First: `nan` is not equal to itself, which sounds like a bug and is a rule, and
it is the reason `x == np.nan` never finds anything and `np.isnan(x)` does.

Second, and more important: vectorising is a trade, not an upgrade. There are
three situations where the loop is the better code, and this script measures
all three rather than asserting them.
"""

import math
import time

import numpy as np

import dataset
from vectorize import nan_aware_mean, roots_vec


def main() -> None:
    print("07_nan_and_when_not_to_vectorise.py")
    print("=" * 70)

    # -- 1. nan is not equal to itself ----------------------------------------
    print()
    print("1. The one comparison that surprises everybody")
    print("-" * 70)
    print(f"  np.nan == np.nan   ->  {np.nan == np.nan}")
    print(f"  np.nan != np.nan   ->  {np.nan != np.nan}")
    print(f"  np.nan  is np.nan  ->  {np.nan is np.nan}   (it is one object)")
    print()
    print("  Not a NumPy decision. IEEE-754 says nan compares unequal to")
    print("  everything including itself, because nan means 'not a number' --")
    print("  the result of 0/0, of sqrt of a negative, of a reading that was")
    print("  never taken. Two unknowns are not known to be the same unknown.")
    assert (np.nan == np.nan) is False
    assert (np.nan != np.nan) is True

    # -- 2. What that costs you -----------------------------------------------
    print()
    print("2. So this does not work")
    print("-" * 70)
    holed = dataset.WITH_A_HOLE
    print(f"  a = {holed}")
    a_eq = holed == np.nan
    print(f"  a == np.nan   ->  {a_eq}")
    print("  Every answer False, including for the element that IS nan. A")
    print("  filter written this way finds nothing and reports success.")
    print()
    print(f"  np.isnan(a)   ->  {np.isnan(holed)}")
    print(f"  np.isnan(a).sum()  ->  {int(np.isnan(holed).sum())}")
    print("  np.isnan asks about the bit pattern rather than about equality,")
    print("  which is the only question with a useful answer here.")
    assert not a_eq.any()
    assert np.isnan(holed).tolist() == [False, False, True, False]
    assert int(np.isnan(holed).sum()) == 1

    # -- 3. nan is contagious, and that is a feature --------------------------
    print()
    print("3. One hole poisons the aggregate, deliberately")
    print("-" * 70)
    print(f"  a.sum()        {holed.sum()}")
    print(f"  a.mean()       {holed.mean()}")
    print(f"  a.max()        {holed.max()}")
    print()
    print(f"  np.nansum(a)   {np.nansum(holed)}")
    print(f"  np.nanmean(a)  {np.nanmean(holed)}")
    print(f"  np.nanmax(a)   {np.nanmax(holed)}")
    print()
    print(f"  nan_aware_mean(a) = {nan_aware_mean(holed)}")
    print("  which is 7 / 3, the mean of the three readings that exist.")
    print()
    print("  The plain versions are not broken. They are telling you that a")
    print("  value is missing, loudly, at the point where it starts to matter.")
    print("  Reaching for the nan- version is a decision to ignore that, and")
    print("  it should be a decision rather than a reflex: the mean of the")
    print("  three you have is not the mean of the four you wanted.")
    assert math.isnan(float(holed.mean()))
    assert float(np.nansum(holed)) == 7.0
    assert nan_aware_mean(holed) == 7.0 / 3.0
    assert float(np.nanmax(holed)) == 4.0

    print()
    print("  Where a nan comes from in the first place:")
    with np.errstate(invalid="ignore", divide="ignore"):
        zero_over_zero = np.float64(0.0) / np.float64(0.0)
        root_of_negative = np.sqrt(np.array([-1.0]))[0]
        inf_minus_inf = np.float64(np.inf) - np.float64(np.inf)
    print(f"    0.0 / 0.0        {zero_over_zero}")
    print(f"    np.sqrt(-1.0)    {root_of_negative}")
    print(f"    inf - inf        {inf_minus_inf}")
    print("  Each of those emits a RuntimeWarning by default, which np.errstate")
    print("  is silencing here only because the point is the VALUE. In your")
    print("  own code, leave the warning on.")
    assert math.isnan(float(zero_over_zero))
    assert math.isnan(float(root_of_negative))
    assert math.isnan(float(inf_minus_inf))

    # -- 4. When NOT to vectorise: the array is small -------------------------
    print()
    print("4. When not to vectorise, case one: the array is small")
    print("-" * 70)
    small = [1.0, 2.0, 3.0, 4.0]
    reps = 20000

    start = time.perf_counter()
    for _ in range(reps):
        [math.sqrt(x) for x in small]
    loop_us = (time.perf_counter() - start) / reps * 1e6

    start = time.perf_counter()
    for _ in range(reps):
        np.sqrt(np.array(small))
    numpy_us = (time.perf_counter() - start) / reps * 1e6

    print(f"  four elements, {reps:,} repetitions, microseconds per call")
    print(f"    [math.sqrt(x) for x in xs]     {loop_us:7.3f} us")
    print(f"    np.sqrt(np.array(xs))          {numpy_us:7.3f} us")
    print(f"    the comprehension is           {numpy_us / loop_us:7.2f}x faster here")
    print()
    print("  Every NumPy call has a fixed cost -- work out the dtypes, work")
    print("  out the output shape, allocate it -- before any arithmetic")
    print("  happens. On four elements that setup is the whole bill. The")
    print("  crossover on this machine is in the low hundreds of elements.")
    print("  One machine, one day; measure yours rather than trusting this.")
    assert numpy_us > loop_us, "on four elements the NumPy call costs more here"

    # -- 5. When NOT to vectorise: the loop is clearer -------------------------
    print()
    print("5. When not to vectorise, case two: the loop is clearer")
    print("-" * 70)
    print("  A running balance where each step depends on the last one:")
    print()
    balances = [100.0]
    for change in (-30.0, 50.0, -200.0, 20.0):
        nxt = balances[-1] + change
        balances.append(max(nxt, 0.0))
    print(f"    start 100, changes -30, +50, -200, +20, floored at zero")
    print(f"    balances {balances}")
    print()
    print("  There is no one-line NumPy for that, because step four depends on")
    print("  the floor applied at step three. np.cumsum would give you the")
    print("  running total, and the floor would be wrong:")
    naive = 100.0 + np.cumsum([-30.0, 50.0, -200.0, 20.0])
    print(f"    np.cumsum route  {np.maximum(naive, 0.0).tolist()}")
    print(f"    the honest loop  {balances[1:]}")
    print("  Different answers, and the loop's is the right one. Sequential")
    print("  dependence is the clearest signal that the loop should stay.")
    assert balances == [100.0, 70.0, 120.0, 0.0, 20.0]
    assert np.maximum(naive, 0.0).tolist() != balances[1:]

    # -- 6. When NOT to vectorise: memory ------------------------------------
    print()
    print("6. When not to vectorise, case three: it will not fit")
    print("-" * 70)
    for n in (1_000, 10_000, 30_000, 100_000):
        gb = n * n * 8 / 1e9
        print(f"    all pairs of {n:>7,} points, float64 : {gb:>10.2f} GB")
    print()
    print("  The one-line distance matrix from section 2 of script 06 is")
    print("  `x[:, None] - x[None, :]`, and it allocates n squared elements")
    print("  whether you need them all or not. At a hundred thousand points")
    print("  that is 80 GB, and the elegant line is the reason the process")
    print("  died. The loop that processes a thousand at a time is slower and")
    print("  finishes.")
    print()
    print("  This is not hypothetical arithmetic -- here is the real allocation")
    print("  for a size that does fit:")
    x = np.arange(2000, dtype=np.float64)
    pairwise = x[:, None] - x[None, :]
    print(f"    2,000 points -> shape {pairwise.shape}, {pairwise.nbytes / 1e6:.1f} MB")
    print(f"    the input was {x.nbytes / 1e3:.0f} kB. The output is {pairwise.nbytes / x.nbytes:,.0f}x bigger.")
    assert pairwise.shape == (2000, 2000)
    assert pairwise.nbytes == 32_000_000
    del pairwise

    # -- 7. Same value, different operation -----------------------------------
    print()
    print("7. And a last honesty note about 'the same computation'")
    print("-" * 70)
    values = dataset.big_values()
    as_list = values.tolist()
    by_math = np.array([math.sqrt(x) for x in as_list])
    by_pow = np.array([x ** 0.5 for x in as_list])
    vec = roots_vec(values)
    math_matches = int(np.count_nonzero(by_math != vec))
    pow_matches = int(np.count_nonzero(by_pow != vec))
    print(f"  over {values.size:,} values, compared with np.sqrt:")
    print(f"    math.sqrt(x)  disagrees on {math_matches:>6,} of them")
    print(f"    x ** 0.5      disagrees on {pow_matches:>6,} of them")
    first = int(np.nonzero(by_pow != vec)[0][0])
    print()
    print(f"  the first disagreement, at index {first}:")
    print(f"    x           {as_list[first]!r}")
    print(f"    x ** 0.5    {float(by_pow[first])!r}")
    print(f"    np.sqrt(x)  {float(vec[first])!r}")
    print(f"    difference  {abs(by_pow[first] - vec[first]):.3e}")
    print()
    print("  One unit in the last place, on about one value in seven hundred.")
    print("  IEEE-754 requires square root to be correctly rounded and both")
    print("  math.sqrt and np.sqrt use the instruction that obeys that.")
    print("  pow(x, 0.5) is a general power routine and makes no such promise.")
    print()
    print("  So 'the vectorised version gives the same answer' is a claim about")
    print("  the OPERATION, not about anything that agrees in exact arithmetic.")
    print("  When a rewrite needs a tolerance it did not need before, that is")
    print("  worth reading rather than widening.")
    assert math_matches == 0
    assert pow_matches > 0
    assert abs(float(by_pow[first]) - float(vec[first])) < 1e-15

    print()
    print("=" * 70)
    print("07_nan_and_when_not_to_vectorise.py: every assertion held.")


if __name__ == "__main__":
    main()
