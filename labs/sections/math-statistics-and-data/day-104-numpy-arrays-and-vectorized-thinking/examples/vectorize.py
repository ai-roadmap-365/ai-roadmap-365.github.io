"""The reference implementation: ten functions, each written twice or once.

This is the finished version of `starter/vectorize.py`. Read it after you have
tried, not before.

The organising idea of the whole module: **a vectorised expression is the same
computation as the loop, not a different one.** Where that is true, the two
results are compared with `==` and they are exactly equal. Where it is not
true, this module says so rather than reaching for a tolerance to paper over
the difference — see `roots_loop`, whose docstring records a real measured
disagreement between `x ** 0.5` and `numpy.sqrt`.

Three functions are implemented twice, once as an explicit Python loop and
once as a NumPy expression. Every one of the three pairs agrees bit for bit,
which is the claim `03_same_answer_faster.py` and the reference tests check.
"""

from __future__ import annotations

import math
import statistics
import sys
import time
from typing import Callable, Iterable, Sequence

import numpy as np

# ===========================================================================
# 1. The three operations, each implemented twice
# ===========================================================================


def scale_and_offset_loop(values: Sequence[float], m: float, c: float) -> list[float]:
    """`m * x + c` for every element, written as an explicit Python loop.

    This is the shape of code you have been writing for the last hundred days,
    and there is nothing wrong with it except its speed. It allocates the
    output list up front rather than appending, which is the fastest honest
    version of the loop -- comparing a slow loop against a fast array would be
    rigging the measurement.

    >>> scale_and_offset_loop([0.0, 1.0, 2.0], 2.5, 1.25)
    [1.25, 3.75, 6.25]
    """
    out = [0.0] * len(values)
    for i, x in enumerate(values):
        out[i] = m * x + c
    return out


def scale_and_offset_vec(a: np.ndarray, m: float, c: float) -> np.ndarray:
    """`m * x + c` for every element, written as one expression on the array.

    There is still a loop. It happens inside NumPy, compiled, over a
    contiguous block of float64 with no Python object in sight. What you have
    given up is the ability to put a `print` inside it.

    >>> scale_and_offset_vec(np.array([0.0, 1.0, 2.0]), 2.5, 1.25).tolist()
    [1.25, 3.75, 6.25]
    """
    return m * a + c


def roots_loop(values: Sequence[float]) -> list[float]:
    """The square root of every element, as a loop, using `math.sqrt`.

    `math.sqrt` and not `x ** 0.5`, and the difference is not pedantry. On
    this machine, with numpy 2.5.2 and CPython 3.14.0, `math.sqrt` agrees with
    `numpy.sqrt` on all one million values in this lab, while `x ** 0.5`
    disagrees on 1390 of them -- always by one unit in the last place. IEEE-754
    requires square root to be correctly rounded, and both `math.sqrt` and
    `numpy.sqrt` use the hardware instruction that obeys that requirement.
    `pow(x, 0.5)` is a general power routine with no such guarantee.

    So "the vectorised version gives the same answer" is true of the operation,
    not of anything that happens to compute the same value in exact
    arithmetic. `07_when_not_to_vectorise.py` measures the 1390 and prints one
    of them.

    >>> roots_loop([0.0, 1.0, 4.0])
    [0.0, 1.0, 2.0]
    """
    out = [0.0] * len(values)
    for i, x in enumerate(values):
        out[i] = math.sqrt(x)
    return out


def roots_vec(a: np.ndarray) -> np.ndarray:
    """The square root of every element, as one call to a universal function.

    `numpy.sqrt` is a *ufunc*: it applies elementwise to an array of any shape
    and returns an array of the same shape.

    >>> roots_vec(np.array([0.0, 1.0, 4.0])).tolist()
    [0.0, 1.0, 2.0]
    """
    return np.sqrt(a)


def clip_loop(values: Sequence[float], lo: float, hi: float) -> list[float]:
    """Pull every element back inside `[lo, hi]`, as a loop.

    >>> clip_loop([0.0, 0.5, 1.0], 0.25, 0.75)
    [0.25, 0.5, 0.75]
    """
    out = [0.0] * len(values)
    for i, x in enumerate(values):
        if x < lo:
            out[i] = lo
        elif x > hi:
            out[i] = hi
        else:
            out[i] = x
    return out


def clip_vec(a: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """Pull every element back inside `[lo, hi]`, as one call.

    The branch has not disappeared, it has moved: `numpy.clip` evaluates the
    same two comparisons per element in C. This is the pattern that replaces
    `if` inside a loop, and it is why `numpy.where` matters so much.

    >>> clip_vec(np.array([0.0, 0.5, 1.0]), 0.25, 0.75).tolist()
    [0.25, 0.5, 0.75]
    """
    return np.clip(a, lo, hi)


# ===========================================================================
# 2. Masking, selection and ranking
# ===========================================================================


def count_above(a: np.ndarray, threshold: float) -> int:
    """How many elements are strictly greater than `threshold`.

    `a > threshold` is a boolean array, and `True` counts as 1 when summed.
    That is the whole trick, and it replaces a counter variable.

    >>> count_above(np.array([1, 5, 9]), 4)
    2
    """
    return int((a > threshold).sum())


def mask_between(a: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """A boolean array that is True where `lo < x < hi`.

    The parentheses are not optional. `&` binds tighter than `<` in Python, so
    `a > lo & a < hi` parses as `a > (lo & a) < hi` and raises. Every NumPy
    user has written that line once.

    And it must be `&`, not `and`. `and` asks the left operand whether it is
    truthy, which for an array of more than one element raises
    ValueError: The truth value of an array with more than one element is
    ambiguous.

    >>> mask_between(np.array([1, 5, 9]), 2, 8).tolist()
    [False, True, False]
    """
    return (a > lo) & (a < hi)


def select(a: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """The elements where `mask` is True, as a new array.

    Indexing with a boolean array always returns a **copy**, never a view --
    it has to, because the selected elements are not evenly spaced and no
    stride can describe them.

    >>> select(np.array([1, 5, 9]), np.array([True, False, True])).tolist()
    [1, 9]
    """
    return a[mask]


def top_k_indices(scores: np.ndarray, k: int) -> np.ndarray:
    """The indices of the `k` largest scores, best first.

    `numpy.argsort` returns the indices that would sort the array, ascending.
    Reverse them and take the first `k`.

    The indices are the point. `numpy.sort` would give you the scores and lose
    which row each one came from, which is exactly the thing a search needs.

    >>> top_k_indices(np.array([0.1, 0.9, 0.5]), 2).tolist()
    [1, 2]
    """
    return np.argsort(scores)[::-1][:k]


def cosine_similarities(matrix: np.ndarray, query: np.ndarray) -> np.ndarray:
    """Cosine similarity between `query` and every row of `matrix`, at once.

    Day 103 computed these one row at a time. This is the same arithmetic with
    the loop moved into NumPy: one matrix-vector product for all the dot
    products, and `axis=1` to take one norm per row.

    `axis=1` means "collapse the columns, leaving one number per row". The rule
    worth memorising: **the axis you name is the one that disappears.** A 6 by
    4 array summed with `axis=1` gives 6 numbers, not 4.

    >>> m = np.array([[1.0, 0.0], [0.0, 1.0]])
    >>> cosine_similarities(m, np.array([1.0, 0.0])).tolist()
    [1.0, 0.0]
    """
    row_norms = np.linalg.norm(matrix, axis=1)
    return (matrix @ query) / (row_norms * np.linalg.norm(query))


# ===========================================================================
# 3. Memory, dtypes and missing values
# ===========================================================================


def list_bytes(values: list[int]) -> int:
    """An honest total for what a Python list of integers costs in memory.

    `sys.getsizeof(values)` on its own is **not** the answer, and reporting it
    as one is the mistake this function exists to avoid. It measures the list
    object: a header plus one 8-byte pointer per element. It does not measure
    the integers those pointers point at, because they are separate objects
    that the list does not own.

    So this adds the payload: every distinct integer object reachable from the
    list, counted once. CPython caches the small integers from -5 to 256, so
    those really are shared and counting them once is right rather than
    generous.

    On this machine `sys.getsizeof(list(range(1_000_000)))` is 8,000,056 bytes
    -- almost exactly the 8,000,000 an int64 array needs, which would make the
    two look equal. The truth is 36,000,056, because each of the million
    integers is a 28-byte object.

    >>> list_bytes([1, 2, 3]) > sys.getsizeof([1, 2, 3])
    True
    """
    by_identity = {id(x): x for x in values}
    payload = sum(sys.getsizeof(x) for x in by_identity.values())
    return sys.getsizeof(values) + payload


def array_bytes(a: np.ndarray) -> int:
    """What the array's data block costs: `a.nbytes`.

    This is `a.size * a.itemsize` and it is the whole story for the numbers.
    The ndarray object itself adds a small fixed header -- 112 bytes here --
    which `sys.getsizeof` includes and which stops mattering above a few
    hundred elements.

    >>> array_bytes(np.arange(3, dtype=np.int64))
    24
    """
    return int(a.nbytes)


def wrap_int8(value: int, added: int) -> int:
    """Add `added` to `value` inside an int8 array, and report what came out.

    An int8 holds -128 to 127. Adding 1 to 127 does not raise, does not
    promote to a larger type, and on numpy 2.5.2 does not even warn: it wraps
    to -128, silently. That is the single most surprising thing about dtypes,
    and the reason to state a dtype deliberately rather than let one be
    guessed.

    The addition is done with an int8 array on both sides so that NumPy 2's
    promotion rules cannot rescue it. Adding a plain Python `1` to an int8
    array wraps too, which is checked in `02_dtypes_and_overflow.py`.

    >>> wrap_int8(127, 1)
    -128
    """
    a = np.array([value], dtype=np.int8)
    b = np.array([added], dtype=np.int8)
    return int((a + b)[0])


def nan_aware_mean(a: np.ndarray) -> float:
    """The mean of the non-missing entries.

    `a.mean()` on an array containing nan returns nan, because nan propagates
    through every arithmetic operation it touches. That is correct and it is
    useful: it tells you loudly that a value is missing rather than quietly
    averaging over a hole.

    `numpy.nanmean` is the version that skips them, and choosing it should be
    a decision you make rather than a default you inherit.

    >>> nan_aware_mean(np.array([1.0, 2.0, np.nan, 4.0]))
    2.3333333333333335
    """
    return float(np.nanmean(a))


# ===========================================================================
# Helpers -- written for you. Read them; the tests use them.
# ===========================================================================


def time_call(fn: Callable[[], object], repeats: int = 5) -> list[float]:
    """Run `fn` `repeats` times and return every elapsed time in seconds.

    Every time, not the best one and not the average. A single timing is
    noise; a list of them lets the caller take a median and lets a reader see
    the spread. `time.perf_counter` is the right clock: monotonic and the
    highest resolution available.
    """
    times: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        times.append(time.perf_counter() - start)
    return times


def median_seconds(times: Iterable[float]) -> float:
    """The median of a list of timings.

    The median rather than the mean, because one unlucky run in which the
    operating system decided to do something else will drag a mean around and
    leave a median alone.
    """
    return statistics.median(times)


def speedup(loop_times: Iterable[float], vec_times: Iterable[float]) -> float:
    """How many times faster the vectorised version was, by median.

    Reported to be read, never asserted on exactly. The lab's tests assert
    that this is at least 20, which is a claim about the SHAPE of the gap and
    survives a slower machine. Asserting the actual figure would make the
    suite fail for everyone whose hardware is not this one.
    """
    return median_seconds(loop_times) / median_seconds(vec_times)


def describe(a: np.ndarray) -> str:
    """The four facts that distinguish an ndarray from a list, in one line."""
    return (
        f"shape={a.shape} dtype={a.dtype} itemsize={a.itemsize} "
        f"nbytes={a.nbytes} strides={a.strides} "
        f"c_contiguous={a.flags['C_CONTIGUOUS']}"
    )
