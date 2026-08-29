"""Your running score. Run from the LAB DIRECTORY:

    .venv/bin/pytest starter -q

Anything you have not written yet is SKIPPED, not failed. A skip means "not
attempted"; a failure means "attempted and wrong", and the failure prints both
your answer and the real one.

Every test that exercises your code runs its whole body inside `written(...)`,
so a test is skipped if ANY function it needs is still unwritten -- not just
the first one. Python evaluates arguments before the call, so gating on one
function while calling another inside the arguments would let a
NotImplementedError escape and be reported as a failure. It would say
"attempted and wrong" about work you had not attempted, which is precisely the
lie this suite exists to avoid.
"""

import math
import sys

import numpy as np
import pytest

import answers
import dataset
from vectorize import (
    array_bytes,
    clip_loop,
    clip_vec,
    cosine_similarities,
    count_above,
    list_bytes,
    mask_between,
    median_seconds,
    nan_aware_mean,
    roots_loop,
    roots_vec,
    scale_and_offset_loop,
    scale_and_offset_vec,
    select,
    speedup,
    time_call,
    top_k_indices,
    wrap_int8,
)

TOL = dataset.TOL


def written(fn, *args, **kwargs):
    """Run part of your work, or skip the test if it is not written yet."""
    try:
        return fn(*args, **kwargs)
    except NotImplementedError as exc:
        pytest.skip(f"not written yet: {exc}")


def predicted(name):
    """Read one prediction from answers.py, or skip if it is still None."""
    value = getattr(answers, name)
    if value is None:
        pytest.skip(f"answers.{name} is still unanswered")
    return value


# -- Exercise 0: the environment ---------------------------------------------


def test_0_the_environment_is_ready():
    """Always passes once the install worked. Everything below is your work."""
    assert int(np.__version__.split(".")[0]) >= 2, "numpy 2 or later is importable"
    assert dataset.small_readings().tolist() == dataset.SMALL_READINGS_EXPECTED, (
        "the seeded generator produces the documented twenty readings"
    )
    assert array_bytes(np.arange(3, dtype=np.int64)) == 24, "the helpers load"


# -- Exercise 1: your vectorize.py -------------------------------------------


def test_1_1_scale_and_offset_loop():
    got = written(lambda: scale_and_offset_loop([0.0, 1.0, 2.0], 2.5, 1.25))
    assert got == [1.25, 3.75, 6.25]


def test_1_1_scale_and_offset_loop_returns_a_plain_list():
    got = written(lambda: scale_and_offset_loop([0.0, 1.0], 2.0, 0.0))
    assert isinstance(got, list), "return a list, not an array"


def test_1_2_scale_and_offset_vec():
    got = written(lambda: scale_and_offset_vec(np.array([0.0, 1.0, 2.0]), 2.5, 1.25))
    assert got.tolist() == [1.25, 3.75, 6.25]


def test_1_2_scale_and_offset_vec_returns_an_array():
    got = written(lambda: scale_and_offset_vec(np.array([0.0, 1.0]), 2.0, 0.0))
    assert isinstance(got, np.ndarray), "return an array, not a list"


def test_1_1_and_1_2_agree_exactly_on_a_million_elements():
    """The claim the whole lab rests on: the SAME computation, not a similar
    one. Compared with ==, elementwise, over a million values."""
    values = dataset.big_values()

    def run():
        loop = scale_and_offset_loop(values.tolist(), dataset.SCALE_M, dataset.SCALE_C)
        vec = scale_and_offset_vec(values, dataset.SCALE_M, dataset.SCALE_C)
        return np.array(loop), vec

    loop, vec = written(run)
    assert np.array_equal(loop, vec), (
        "every one of the million elements must match bit for bit"
    )


def test_1_3_roots_loop():
    assert written(lambda: roots_loop([0.0, 1.0, 4.0])) == [0.0, 1.0, 2.0]


def test_1_4_roots_vec():
    assert written(lambda: roots_vec(np.array([0.0, 1.0, 4.0]))).tolist() == [
        0.0,
        1.0,
        2.0,
    ]


def test_1_3_and_1_4_agree_exactly_on_a_million_elements():
    """If this fails while 1.3 passes, check that roots_loop uses math.sqrt
    and not x ** 0.5. They are not the same operation; exercise 6.4 is about
    exactly this."""
    values = dataset.big_values()

    def run():
        return np.array(roots_loop(values.tolist())), roots_vec(values)

    loop, vec = written(run)
    differing = int(np.count_nonzero(loop != vec))
    assert differing == 0, (
        f"{differing} of {values.size} elements differ; math.sqrt agrees with "
        "numpy.sqrt bit for bit, and x ** 0.5 does not"
    )


def test_1_5_clip_loop():
    assert written(lambda: clip_loop([0.0, 0.5, 1.0], 0.25, 0.75)) == [0.25, 0.5, 0.75]


def test_1_5_clip_loop_leaves_interior_values_untouched():
    got = written(lambda: clip_loop([0.3, 0.4, 0.5], 0.25, 0.75))
    assert got == [0.3, 0.4, 0.5]


def test_1_6_clip_vec():
    got = written(lambda: clip_vec(np.array([0.0, 0.5, 1.0]), 0.25, 0.75))
    assert got.tolist() == [0.25, 0.5, 0.75]


def test_1_5_and_1_6_agree_exactly_on_a_million_elements():
    values = dataset.big_values()

    def run():
        loop = clip_loop(values.tolist(), dataset.CLIP_LO, dataset.CLIP_HI)
        return np.array(loop), clip_vec(values, dataset.CLIP_LO, dataset.CLIP_HI)

    loop, vec = written(run)
    assert np.array_equal(loop, vec)


def test_the_vectorised_versions_are_much_faster():
    """A claim about the SHAPE of the gap, never the figure. Twenty times
    survives a slow machine; the authoring machine measured over a hundred."""
    values = dataset.big_values()
    as_list = values.tolist()

    def run():
        scale_and_offset_loop(as_list, dataset.SCALE_M, dataset.SCALE_C)
        scale_and_offset_vec(values, dataset.SCALE_M, dataset.SCALE_C)
        loop = time_call(
            lambda: scale_and_offset_loop(as_list, dataset.SCALE_M, dataset.SCALE_C), 3
        )
        vec = time_call(
            lambda: scale_and_offset_vec(values, dataset.SCALE_M, dataset.SCALE_C), 3
        )
        return speedup(loop, vec)

    factor = written(run)
    assert factor > 20.0, f"measured {factor:.1f}x, which is below the 20x floor"


def test_1_7_count_above():
    assert written(lambda: count_above(np.array([1, 5, 9]), 4)) == 2


def test_1_7_count_above_returns_a_plain_int():
    got = written(lambda: count_above(np.array([1, 5, 9]), 4))
    assert type(got) is int, "wrap the sum in int()"


def test_1_7_count_above_on_the_twenty_readings():
    readings = dataset.small_readings()
    assert written(lambda: count_above(readings, 50)) == 9


def test_1_8_mask_between():
    got = written(lambda: mask_between(np.array([1, 5, 9]), 2, 8))
    assert got.tolist() == [False, True, False]


def test_1_8_mask_between_returns_a_boolean_array():
    got = written(lambda: mask_between(np.array([1, 5, 9]), 2, 8))
    assert got.dtype == np.bool_, "a mask is boolean, not integer"


def test_1_8_mask_between_is_strict_at_both_ends():
    got = written(lambda: mask_between(np.array([2, 5, 8]), 2, 8))
    assert got.tolist() == [False, True, False], "lo < x < hi, both strict"


def test_1_8_mask_between_on_the_twenty_readings():
    readings = dataset.small_readings()
    mask = written(lambda: mask_between(readings, 30, 70))
    assert readings[mask].tolist() == [34, 69, 65, 37, 37, 41, 64]


def test_1_9_top_k_indices():
    got = written(lambda: top_k_indices(np.array([0.1, 0.9, 0.5]), 2))
    assert list(got) == [1, 2]


def test_1_9_top_k_indices_returns_exactly_k():
    got = written(lambda: top_k_indices(np.array([0.1, 0.9, 0.5, 0.7]), 3))
    assert len(got) == 3


def test_1_9_top_k_indices_gives_positions_not_values():
    got = written(lambda: top_k_indices(np.array([10.0, 30.0, 20.0]), 1))
    assert list(got) == [1], "index 1, not the value 30.0"


def test_1_10_cosine_similarities():
    identity = np.array([[1.0, 0.0], [0.0, 1.0]])
    got = written(lambda: cosine_similarities(identity, np.array([1.0, 0.0])))
    assert got.tolist() == [1.0, 0.0]


def test_1_10_cosine_similarities_gives_one_score_per_row():
    got = written(lambda: cosine_similarities(dataset.CATALOGUE, dataset.QUERY))
    assert got.shape == (6,), "axis=1 collapses the columns, leaving one per row"


def test_1_10_cosine_similarities_matches_day_103_row_by_row():
    got = written(lambda: cosine_similarities(dataset.CATALOGUE, dataset.QUERY))
    by_hand = []
    for row in dataset.CATALOGUE:
        dot = sum(float(x) * float(y) for x, y in zip(row, dataset.QUERY))
        left = math.sqrt(sum(float(x) * float(x) for x in row))
        right = math.sqrt(sum(float(y) * float(y) for y in dataset.QUERY))
        by_hand.append(dot / (left * right))
    assert np.allclose(got, by_hand, atol=TOL)


def test_1_9_and_1_10_together_rank_the_catalogue():
    def run():
        sims = cosine_similarities(dataset.CATALOGUE, dataset.QUERY)
        return top_k_indices(sims, dataset.TOP_K)

    top = written(run)
    assert [dataset.ARTICLE_NAMES[i] for i in top] == [
        "race-day-nutrition",
        "marathon-plan",
        "roast-chicken",
    ]


# -- Exercise 2: what an array actually is ------------------------------------


def test_2_1_memory_ratio():
    guess = predicted("LIST_TO_ARRAY_MEMORY_RATIO")
    values = list(range(dataset.N_BIG))
    real = list_bytes(values) / np.arange(dataset.N_BIG, dtype=np.int64).nbytes
    assert abs(guess - real) < 1.0, f"measured {real:.2f}"


def test_2_2_bytes_per_python_int():
    assert predicted("BYTES_PER_PYTHON_INT") == sys.getsizeof(1_000_000)


def test_2_3_bytes_per_int64_element():
    assert predicted("BYTES_PER_INT64_ELEMENT") == np.zeros(1, dtype=np.int64).itemsize


def test_2_4_why_getsizeof_misleads():
    assert (
        predicted("WHY_GETSIZEOF_MISLEADS")
        == "getsizeof measures only the pointers, not the integers"
    )


def test_2_5_strides():
    assert tuple(predicted("STRIDES_OF_A_THREE_BY_FOUR")) == np.arange(12).reshape(
        3, 4
    ).strides


def test_2_6_transpose_copies_nothing():
    grid = np.arange(12).reshape(3, 4)
    shares = bool(np.shares_memory(grid, grid.T))
    assert predicted("TRANSPOSE_COPIES_DATA") is not shares
    assert shares is True, "a transpose is a view; nothing was copied"


# -- Exercise 3: dtypes -------------------------------------------------------


def test_3_1_int8_overflow_value():
    assert predicted("INT8_127_PLUS_1") == wrap_int8(127, 1)


def test_3_2_int8_overflow_does_not_raise():
    assert predicted("INT8_OVERFLOW_RAISES") is False


def test_3_3_int8_overflow_does_not_warn_on_this_numpy():
    import warnings

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        wrap_int8(127, 1)
    assert predicted("INT8_OVERFLOW_WARNS") is (len(caught) > 0)


def test_3_4_int8_doubled():
    real = (np.array(dataset.INT8_DOUBLING_INPUT, dtype=np.int8) * np.int8(2)).tolist()
    assert list(predicted("INT8_DOUBLED")) == real


def test_3_5_dtype_of_int8_plus_python_int():
    real = (np.array([127], dtype=np.int8) + 1).dtype
    assert np.dtype(predicted("DTYPE_OF_INT8_PLUS_PYTHON_INT")) == real


def test_3_6_float32_blind_spot():
    blind = np.float32(dataset.FLOAT32_BLIND_SPOT)
    assert predicted("FLOAT32_CANNOT_ADD_ONE") is bool(blind + np.float32(1.0) == blind)


def test_3_7_dtypes_of_full():
    guessed = predicted("DTYPES_OF_FULL")
    assert np.dtype(guessed[0]) == np.full(3, 7).dtype
    assert np.dtype(guessed[1]) == np.full(3, 7.0).dtype


# -- Exercise 4: masking ------------------------------------------------------


def test_4_1_count_above_50():
    readings = dataset.small_readings()
    assert predicted("COUNT_ABOVE_50") == int((readings > 50).sum())


def test_4_2_values_above_50():
    readings = dataset.small_readings()
    assert list(predicted("VALUES_ABOVE_50")) == readings[readings > 50].tolist()


def test_4_3_count_between_30_and_70():
    readings = dataset.small_readings()
    real = int(((readings > 30) & (readings < 70)).sum())
    assert predicted("COUNT_BETWEEN_30_AND_70") == real


def test_4_4_shape_of_a_mask():
    readings = dataset.small_readings()
    assert tuple(predicted("SHAPE_OF_A_MASK")) == (readings > 50).shape


def test_4_5_dtype_of_a_mask():
    readings = dataset.small_readings()
    assert np.dtype(predicted("DTYPE_OF_A_MASK")) == (readings > 50).dtype


def test_4_6_exception_from_keyword_and():
    readings = dataset.small_readings()
    guess = predicted("EXCEPTION_FROM_KEYWORD_AND")
    with pytest.raises(guess):
        (readings > 30) and (readings < 70)


def test_4_7_why_and_fails():
    assert (
        predicted("WHY_AND_FAILS")
        == "and is a keyword, so it asks the array for a single True or False"
    )


def test_4_8_mean_of_the_mask():
    readings = dataset.small_readings()
    assert predicted("MEAN_OF_THE_MASK") == float((readings > 50).mean())


def test_4_9_fancy_index_result():
    readings = dataset.small_readings()
    real = readings[np.array([0, 5, 19, 5])].tolist()
    assert list(predicted("FANCY_INDEX_RESULT")) == real


# -- Exercise 5: axes, views and copies ---------------------------------------


def test_5_1_shape_after_sum_axis_0():
    assert tuple(predicted("SHAPE_AFTER_SUM_AXIS_0")) == np.arange(12).reshape(
        3, 4
    ).sum(axis=0).shape


def test_5_2_shape_after_sum_axis_1():
    assert tuple(predicted("SHAPE_AFTER_SUM_AXIS_1")) == np.arange(12).reshape(
        3, 4
    ).sum(axis=1).shape


def test_5_3_values_of_sum_axis_1():
    real = np.arange(12).reshape(3, 4).sum(axis=1).tolist()
    assert list(predicted("VALUES_OF_SUM_AXIS_1")) == real


def test_5_4_shape_of_a_column():
    v = np.array([1.0, 2.0, 3.0])
    assert tuple(predicted("SHAPE_OF_A_COLUMN")) == v[:, np.newaxis].shape


def test_5_5_writing_through_a_slice():
    grid = np.arange(12).reshape(3, 4)
    row = grid[1]
    row[0] = 999
    assert predicted("GRID_AFTER_WRITING_THROUGH_A_SLICE") == int(grid[1, 0])


def test_5_6_writing_through_a_copy():
    grid = np.arange(12).reshape(3, 4)
    row = grid[1].copy()
    row[0] = 999
    assert predicted("GRID_AFTER_WRITING_THROUGH_A_COPY") == int(grid[1, 0])


def test_5_7_which_are_views():
    grid = np.arange(12).reshape(3, 4)
    real = [
        label
        for label, result in (
            ("row slice", grid[1]),
            ("column slice", grid[:, 1]),
            ("transpose", grid.T),
            ("reshape", grid.reshape(4, 3)),
            ("boolean mask", grid[grid > 5]),
            ("fancy index", grid[[0, 2]]),
        )
        if np.shares_memory(grid, result)
    ]
    assert sorted(predicted("WHICH_ARE_VIEWS")) == sorted(real)


def test_5_8_always_a_copy():
    grid = np.arange(12).reshape(3, 4)
    assert not np.shares_memory(grid, grid.flatten())
    assert np.shares_memory(grid, grid.ravel())
    assert predicted("ALWAYS_A_COPY") == "flatten"


# -- Exercise 6: sorting, ranking and speed -----------------------------------


def test_6_1_argsort_of_the_scores():
    scores = np.array([5.0, 1.0, 9.0, 3.0])
    assert list(predicted("ARGSORT_OF_THE_SCORES")) == np.argsort(scores).tolist()


def test_6_2_np_sort_does_not_mutate():
    scores = np.array([5.0, 1.0, 9.0, 3.0])
    before = scores.tolist()
    np.sort(scores)
    assert predicted("NP_SORT_MUTATES") is (scores.tolist() != before)


def test_6_3_the_sort_method_does_mutate():
    scores = np.array([5.0, 1.0, 9.0, 3.0])
    before = scores.tolist()
    scores.sort()
    assert predicted("SORT_METHOD_MUTATES") is (scores.tolist() != before)


def test_6_4_the_odd_one_out():
    """Measured on a hundred values rather than a million, so this test stays
    quick. The effect is the same one script 07 measures at full size."""
    sample = dataset.big_values()[:100_000]
    by_math = np.array([math.sqrt(x) for x in sample.tolist()])
    by_pow = np.array([x ** 0.5 for x in sample.tolist()])
    vec = np.sqrt(sample)
    assert np.array_equal(by_math, vec)
    assert not np.array_equal(by_pow, vec)
    assert predicted("THE_ODD_ONE_OUT") == "x ** 0.5"


def test_6_5_rough_speedup():
    assert predicted("ROUGH_SPEEDUP") == "about 100x"


def test_6_6_faster_on_four_elements():
    small = [1.0, 2.0, 3.0, 4.0]
    loop = median_seconds(time_call(lambda: [math.sqrt(x) for x in small], 2000))
    vec = median_seconds(time_call(lambda: np.sqrt(np.array(small)), 2000))
    real = "comprehension" if loop < vec else "numpy"
    assert predicted("FASTER_ON_FOUR_ELEMENTS") == real


# -- Exercise 7: nan ----------------------------------------------------------


def test_7_1_nan_equals_itself():
    assert predicted("NAN_EQUALS_ITSELF") is (np.nan == np.nan)


def test_7_2_comparing_to_nan_finds_nothing():
    real = int((dataset.WITH_A_HOLE == np.nan).sum())
    assert predicted("COUNT_FROM_COMPARING_TO_NAN") == real


def test_7_3_isnan_finds_it():
    assert predicted("COUNT_FROM_ISNAN") == int(np.isnan(dataset.WITH_A_HOLE).sum())


def test_7_4_mean_of_the_holed_array():
    assert predicted("MEAN_OF_THE_HOLED_ARRAY") == "nan"
    assert math.isnan(float(dataset.WITH_A_HOLE.mean()))


def test_7_5_nanmean_of_the_holed_array():
    guess = predicted("NANMEAN_OF_THE_HOLED_ARRAY")
    assert abs(guess - nan_aware_mean(dataset.WITH_A_HOLE)) <= TOL


def test_7_6_nan_propagation_is_not_a_bug():
    assert predicted("NAN_PROPAGATION_IS_A_BUG") is False


# -- A final check that uses your work end to end ------------------------------


def test_the_whole_pipeline_on_the_twenty_readings():
    """Mask, count, select, rank -- all four of your functions in one go."""
    readings = dataset.small_readings()

    def run():
        mask = mask_between(readings, 30, 70)
        chosen = select(readings, mask)
        return count_above(readings, 50), chosen, top_k_indices(chosen.astype(float), 3)

    count, chosen, top = written(run)
    assert count == 9
    assert chosen.tolist() == [34, 69, 65, 37, 37, 41, 64]
    assert chosen[top].tolist() == [69, 65, 64]
