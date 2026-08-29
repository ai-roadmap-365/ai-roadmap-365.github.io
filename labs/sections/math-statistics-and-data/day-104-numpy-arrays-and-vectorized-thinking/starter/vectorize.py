"""Exercise 1 -- ten functions to write. Your work goes here.

Each function raises NotImplementedError until you write it, and the test
suite SKIPS anything still unwritten rather than failing it. So your score
only ever counts work you actually attempted.

Check yourself from the LAB DIRECTORY (the one above this file):

    .venv/bin/pytest starter -q

Read each docstring before you write the body. Every one of them gives the
derivation and a worked example small enough to check on paper.

Three of these are implemented TWICE -- once as an explicit Python loop and
once as a NumPy expression. That is the spine of the whole lab: a vectorised
expression is the SAME computation as the loop, not a different one, and the
tests prove it by comparing a million elements with `==` rather than with a
tolerance.

The helpers at the bottom of this file are written for you. Read them; the
tests use them.
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
    """1.1 -- `m * x + c` for every element, as an explicit Python loop.

    Return a NEW list. Do not use NumPy in this function; the whole point is
    that this is the code you have been writing for a hundred days.

    Allocate the output up front with `[0.0] * len(values)` and assign into it
    rather than appending. Appending would be a slower loop, and comparing a
    slow loop against a fast array would be rigging the measurement.

    >>> scale_and_offset_loop([0.0, 1.0, 2.0], 2.5, 1.25)
    [1.25, 3.75, 6.25]
    """
    raise NotImplementedError("scale_and_offset_loop")


def scale_and_offset_vec(a: np.ndarray, m: float, c: float) -> np.ndarray:
    """1.2 -- the same thing as one expression on the whole array.

    One line. No loop, no comprehension, no `for` anywhere.

    >>> scale_and_offset_vec(np.array([0.0, 1.0, 2.0]), 2.5, 1.25).tolist()
    [1.25, 3.75, 6.25]
    """
    raise NotImplementedError("scale_and_offset_vec")


def roots_loop(values: Sequence[float]) -> list[float]:
    """1.3 -- the square root of every element, as a loop.

    Use `math.sqrt(x)` and NOT `x ** 0.5`, and the difference is not pedantry.
    IEEE-754 requires square root to be correctly rounded, and `math.sqrt`
    uses the hardware instruction that obeys that requirement -- so it agrees
    with `numpy.sqrt` bit for bit. `pow(x, 0.5)` is a general power routine
    with no such guarantee, and on this machine it disagrees on 1390 of the
    lab's million values. Exercise 6.4 asks you to predict that.

    >>> roots_loop([0.0, 1.0, 4.0])
    [0.0, 1.0, 2.0]
    """
    raise NotImplementedError("roots_loop")


def roots_vec(a: np.ndarray) -> np.ndarray:
    """1.4 -- the same thing as one call to a universal function.

    >>> roots_vec(np.array([0.0, 1.0, 4.0])).tolist()
    [0.0, 1.0, 2.0]
    """
    raise NotImplementedError("roots_vec")


def clip_loop(values: Sequence[float], lo: float, hi: float) -> list[float]:
    """1.5 -- pull every element back inside `[lo, hi]`, as a loop.

    Anything below `lo` becomes `lo`, anything above `hi` becomes `hi`, and
    everything else is left exactly as it was.

    >>> clip_loop([0.0, 0.5, 1.0], 0.25, 0.75)
    [0.25, 0.5, 0.75]
    """
    raise NotImplementedError("clip_loop")


def clip_vec(a: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """1.6 -- the same thing in one call.

    There is a NumPy function named after exactly this operation. The branch
    has not disappeared, it has moved into C.

    >>> clip_vec(np.array([0.0, 0.5, 1.0]), 0.25, 0.75).tolist()
    [0.25, 0.5, 0.75]
    """
    raise NotImplementedError("clip_vec")


# ===========================================================================
# 2. Masking, selection and ranking
# ===========================================================================


def count_above(a: np.ndarray, threshold: float) -> int:
    """1.7 -- how many elements are strictly greater than `threshold`.

    No loop and no counter variable. `a > threshold` gives you one boolean per
    element, and `True` counts as 1 when a boolean array is summed. Wrap the
    result in `int()` so the return type is a plain Python integer.

    >>> count_above(np.array([1, 5, 9]), 4)
    2
    """
    raise NotImplementedError("count_above")


def mask_between(a: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """1.8 -- a boolean array that is True where `lo < x < hi`.

    Two things will bite you here and both are worth meeting now.

    `and` does not work. It is a control-flow keyword, not an operator, so
    NumPy cannot redefine it; Python asks the left operand "are you true?" and
    an array of twenty answers raises
    `ValueError: The truth value of an array with more than one element is
    ambiguous`. Use `&`, which IS an operator and which NumPy defines to mean
    elementwise-and.

    The parentheses around each comparison are not optional either. `&` binds
    tighter than `<`, so `a > lo & a < hi` parses as `a > (lo & a) < hi`.

    >>> mask_between(np.array([1, 5, 9]), 2, 8).tolist()
    [False, True, False]
    """
    raise NotImplementedError("mask_between")


def top_k_indices(scores: np.ndarray, k: int) -> np.ndarray:
    """1.9 -- the INDICES of the `k` largest scores, best first.

    `numpy.argsort` returns the indices that would sort the array, smallest
    first. You want the other end, and you want only `k` of them.

    The indices are the point. `numpy.sort` would hand you the scores and lose
    which row each one came from, which is exactly the thing a search needs to
    know. This is the function that turns Day 103's similarity scores into an
    answer.

    >>> top_k_indices(np.array([0.1, 0.9, 0.5]), 2).tolist()
    [1, 2]
    """
    raise NotImplementedError("top_k_indices")


def cosine_similarities(matrix: np.ndarray, query: np.ndarray) -> np.ndarray:
    """1.10 -- cosine similarity between `query` and EVERY row of `matrix`.

    Day 103 did this one row at a time. Do it in one expression, with no loop
    over rows.

    Two pieces:

      * all the dot products at once. `matrix @ query` gives one number per
        row -- a 6 by 4 matrix times a 4-vector is a 6-vector.
      * one length per row. `numpy.linalg.norm(matrix, axis=1)` gives six
        numbers, because **the axis you name is the one that disappears**: a
        (6, 4) array reduced along axis 1 leaves shape (6,).

    Then divide, elementwise, by those row lengths times the query's length.

    >>> m = np.array([[1.0, 0.0], [0.0, 1.0]])
    >>> cosine_similarities(m, np.array([1.0, 0.0])).tolist()
    [1.0, 0.0]
    """
    raise NotImplementedError("cosine_similarities")


# ===========================================================================
# Helpers -- written for you. Read them; the tests use them.
# ===========================================================================


def list_bytes(values: list[int]) -> int:
    """An honest total for what a Python list of integers costs in memory.

    `sys.getsizeof(values)` on its own is NOT the answer. It measures the list
    object -- a header plus one 8-byte pointer per element -- and not the
    integers those pointers point at, because the list does not own them.

    On this machine `sys.getsizeof(list(range(1_000_000)))` is 8,000,056
    bytes, almost exactly the 8,000,000 an int64 array needs, which would make
    the two look equal. The truth is 36,000,056: each of the million integers
    is a separate 28-byte object.

    So this adds the payload, counting each DISTINCT integer object once --
    CPython caches -5 through 256, so those really are shared.
    """
    by_identity = {id(x): x for x in values}
    payload = sum(sys.getsizeof(x) for x in by_identity.values())
    return sys.getsizeof(values) + payload


def array_bytes(a: np.ndarray) -> int:
    """What the array's data block costs: `a.nbytes`, which is size x itemsize."""
    return int(a.nbytes)


def wrap_int8(value: int, added: int) -> int:
    """Add `added` to `value` inside an int8 array and report what came out.

    An int8 holds -128 to 127. Adding 1 to 127 does not raise, does not
    promote, and on numpy 2.5.2 does not warn. Exercise 3 asks you what it
    gives instead.
    """
    a = np.array([value], dtype=np.int8)
    b = np.array([added], dtype=np.int8)
    return int((a + b)[0])


def nan_aware_mean(a: np.ndarray) -> float:
    """The mean of the non-missing entries, via numpy.nanmean."""
    return float(np.nanmean(a))


def select(a: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """The elements where `mask` is True, as a new array.

    Boolean indexing always returns a COPY -- it has to, because the selected
    elements are not evenly spaced and no stride can describe them.
    """
    return a[mask]


def time_call(fn: Callable[[], object], repeats: int = 5) -> list[float]:
    """Run `fn` `repeats` times and return every elapsed time in seconds.

    Every time, not the best and not the average: a single timing is noise.
    """
    times: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        times.append(time.perf_counter() - start)
    return times


def median_seconds(times: Iterable[float]) -> float:
    """The median of a list of timings, which one unlucky run cannot drag."""
    return statistics.median(times)


def speedup(loop_times: Iterable[float], vec_times: Iterable[float]) -> float:
    """How many times faster the vectorised version was, by median.

    To be read, never asserted on exactly. The tests assert at least 20x,
    which is a claim about the shape of the gap and survives a slower machine.
    """
    return median_seconds(loop_times) / median_seconds(vec_times)


def describe(a: np.ndarray) -> str:
    """The facts that distinguish an ndarray from a list, in one line."""
    return (
        f"shape={a.shape} dtype={a.dtype} itemsize={a.itemsize} "
        f"nbytes={a.nbytes} strides={a.strides} "
        f"c_contiguous={a.flags['C_CONTIGUOUS']}"
    )


# `math` is imported for you because exercise 1.3 needs math.sqrt.
_ = math
