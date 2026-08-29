"""The reference suite: real values, real exceptions, real measurements.

Run from the LAB DIRECTORY:

    .venv/bin/pytest examples -q -p no:cacheprovider

Nothing here reads source code or checks that a file exists. Every test runs
something and looks at what came back.

Two rules this file follows deliberately:

  * Timings are asserted as SHAPES, never as figures. `test_speedup_is_large`
    asserts at least 20x. The authoring machine measured over 100x. A test
    that asserted 100x would fail on a slower laptop and teach the reader that
    the suite is unreliable rather than that their laptop is slower.

  * Where the loop and the vectorised version do the same operation, they are
    compared with `==` over a million elements rather than with a tolerance,
    because exactness is the claim under test.
"""

import math
import sys
import warnings

import numpy as np
import pytest

import dataset
from vectorize import (
    array_bytes,
    clip_loop,
    clip_vec,
    cosine_similarities,
    count_above,
    describe,
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

# One million-element array, built once for the whole module. Every test that
# uses it treats it as read-only; the two that mutate take a copy first.
BIG = dataset.big_values()
BIG_LIST = BIG.tolist()


# ===========================================================================
# The environment
# ===========================================================================


def test_numpy_is_version_two_or_later():
    assert int(np.__version__.split(".")[0]) >= 2


def test_the_seeded_generator_still_produces_the_documented_values():
    """If a future NumPy changed the generator, this says so rather than
    letting every hand-checked number in the lesson quietly become wrong."""
    assert dataset.small_readings().tolist() == dataset.SMALL_READINGS_EXPECTED


def test_the_big_array_is_the_documented_size_and_dtype():
    assert BIG.size == dataset.N_BIG
    assert BIG.dtype == np.float64
    assert BIG.nbytes == 8_000_000


def test_two_generators_with_the_same_seed_agree():
    first = np.random.default_rng(dataset.SEED).random(5)
    second = np.random.default_rng(dataset.SEED).random(5)
    assert np.array_equal(first, second)


def test_two_generators_with_different_seeds_do_not():
    first = np.random.default_rng(dataset.SEED).random(5)
    other = np.random.default_rng(dataset.SEED + 1).random(5)
    assert not np.array_equal(first, other)


# ===========================================================================
# Memory
# ===========================================================================


def test_the_naive_size_comparison_is_misleading():
    """sys.getsizeof on the list is within one percent of the array's nbytes,
    which is why this lab does not use it as the measurement."""
    values = list(range(dataset.N_BIG))
    array = np.arange(dataset.N_BIG, dtype=np.int64)
    ratio = sys.getsizeof(values) / array.nbytes
    assert 0.99 < ratio < 1.01


def test_the_honest_list_total_is_four_and_a_half_times_the_array():
    values = list(range(dataset.N_BIG))
    array = np.arange(dataset.N_BIG, dtype=np.int64)
    assert list_bytes(values) == 36_000_056
    assert array_bytes(array) == 8_000_000
    assert list_bytes(values) / array_bytes(array) == pytest.approx(4.5, abs=0.01)


def test_a_python_int_is_twenty_eight_bytes_here():
    assert sys.getsizeof(1_000_000) == 28


def test_an_int64_element_is_eight_bytes():
    assert np.arange(3, dtype=np.int64).itemsize == 8


def test_list_bytes_counts_a_shared_integer_once():
    """CPython caches -5 to 256, so a thousand references to 100 are one
    object and must be charged once."""
    hundreds = [int("100")] * 1000
    assert list_bytes(hundreds) == sys.getsizeof(hundreds) + sys.getsizeof(100)


def test_dtype_decides_the_bill():
    n = 1000
    assert np.zeros(n, dtype=np.int8).nbytes == 1000
    assert np.zeros(n, dtype=np.int16).nbytes == 2000
    assert np.zeros(n, dtype=np.float32).nbytes == 4000
    assert np.zeros(n, dtype=np.float64).nbytes == 8000


# ===========================================================================
# Shape, strides and contiguity
# ===========================================================================


def test_shape_dtype_and_strides_of_a_three_by_four():
    grid = np.arange(12).reshape(3, 4)
    assert grid.shape == (3, 4)
    assert grid.dtype == np.int64
    assert grid.strides == (32, 8)
    assert grid.flags["C_CONTIGUOUS"]


def test_describe_reports_all_six_facts():
    text = describe(np.arange(12).reshape(3, 4))
    for fragment in (
        "shape=(3, 4)",
        "dtype=int64",
        "itemsize=8",
        "nbytes=96",
        "strides=(32, 8)",
        "c_contiguous=True",
    ):
        assert fragment in text


def test_a_transpose_copies_nothing():
    grid = np.arange(12).reshape(3, 4)
    assert np.shares_memory(grid, grid.T)
    assert grid.T.strides == (8, 32)
    assert not grid.T.flags["C_CONTIGUOUS"]
    assert grid.T.flags["F_CONTIGUOUS"]


# ===========================================================================
# dtypes and overflow
# ===========================================================================


def test_int8_wraps_from_127_to_minus_128():
    assert wrap_int8(dataset.INT8_MAX, 1) == dataset.INT8_MIN


def test_the_wrap_is_silent_on_this_numpy():
    """Measured, not assumed. If a future NumPy started warning, this fails and
    the lesson gets corrected rather than left stale."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        wrap_int8(dataset.INT8_MAX, 1)
    assert [w.category.__name__ for w in caught] == []


def test_doubling_three_int8_values_wraps_two_of_them():
    doubled = np.array(dataset.INT8_DOUBLING_INPUT, dtype=np.int8) * np.int8(2)
    assert doubled.tolist() == [-16, -6, -2]
    assert doubled.dtype == np.int8


def test_a_python_scalar_does_not_widen_the_array():
    result = np.array([127], dtype=np.int8) + 1
    assert result.dtype == np.int8
    assert int(result[0]) == -128


def test_astype_widens_and_the_answer_is_right():
    result = np.array([127], dtype=np.int8).astype(np.int16) + 1
    assert result.dtype == np.int16
    assert int(result[0]) == 128


def test_int8_range_is_what_iinfo_says():
    info = np.iinfo(np.int8)
    assert (info.min, info.max) == (dataset.INT8_MIN, dataset.INT8_MAX)


def test_float32_cannot_tell_two_million_apart_at_its_blind_spot():
    blind = np.float32(dataset.FLOAT32_BLIND_SPOT)
    assert bool(blind + np.float32(1.0) == blind)


def test_float64_can():
    assert np.float64(dataset.FLOAT32_BLIND_SPOT) + 1.0 == 16777217.0


def test_float32_stores_a_worse_one_tenth_than_float64():
    assert float(np.float32(0.1)) != 0.1
    assert abs(float(np.float32(0.1)) - 0.1) > abs(0.1 - 0.1)


# ===========================================================================
# The three operations, twice each
# ===========================================================================


def test_scale_and_offset_agrees_exactly_over_a_million_elements():
    loop = np.array(scale_and_offset_loop(BIG_LIST, dataset.SCALE_M, dataset.SCALE_C))
    vec = scale_and_offset_vec(BIG, dataset.SCALE_M, dataset.SCALE_C)
    assert np.array_equal(loop, vec)


def test_roots_agree_exactly_over_a_million_elements():
    assert np.array_equal(np.array(roots_loop(BIG_LIST)), roots_vec(BIG))


def test_clip_agrees_exactly_over_a_million_elements():
    loop = np.array(clip_loop(BIG_LIST, dataset.CLIP_LO, dataset.CLIP_HI))
    vec = clip_vec(BIG, dataset.CLIP_LO, dataset.CLIP_HI)
    assert np.array_equal(loop, vec)


def test_the_hand_worked_examples_from_the_docstrings():
    assert scale_and_offset_loop([0.0, 1.0, 2.0], 2.5, 1.25) == [1.25, 3.75, 6.25]
    assert scale_and_offset_vec(np.array([0.0, 1.0, 2.0]), 2.5, 1.25).tolist() == [
        1.25,
        3.75,
        6.25,
    ]
    assert roots_loop([0.0, 1.0, 4.0]) == [0.0, 1.0, 2.0]
    assert roots_vec(np.array([0.0, 1.0, 4.0])).tolist() == [0.0, 1.0, 2.0]
    assert clip_loop([0.0, 0.5, 1.0], 0.25, 0.75) == [0.25, 0.5, 0.75]
    assert clip_vec(np.array([0.0, 0.5, 1.0]), 0.25, 0.75).tolist() == [0.25, 0.5, 0.75]


def test_clip_actually_clips():
    clipped = clip_vec(BIG, dataset.CLIP_LO, dataset.CLIP_HI)
    assert float(clipped.min()) == dataset.CLIP_LO
    assert float(clipped.max()) == dataset.CLIP_HI


def test_speedup_is_large_but_the_figure_is_not_asserted():
    """The SHAPE of the gap, not the figure. 20x survives a slow machine; the
    authoring machine measured over 100x on all three operations."""
    loop = time_call(
        lambda: scale_and_offset_loop(BIG_LIST, dataset.SCALE_M, dataset.SCALE_C), 3
    )
    vec = time_call(
        lambda: scale_and_offset_vec(BIG, dataset.SCALE_M, dataset.SCALE_C), 3
    )
    assert speedup(loop, vec) > 20.0


def test_median_seconds_is_the_middle_value():
    assert median_seconds([3.0, 1.0, 2.0]) == 2.0


def test_time_call_returns_one_timing_per_repeat():
    times = time_call(lambda: None, 4)
    assert len(times) == 4
    assert all(t >= 0.0 for t in times)


def test_x_to_the_half_is_not_the_same_operation_as_sqrt():
    """A measured disagreement, kept rather than tidied away: 1390 of a million
    values differ by one unit in the last place."""
    by_pow = np.array([x ** 0.5 for x in BIG_LIST])
    differing = int(np.count_nonzero(by_pow != roots_vec(BIG)))
    assert differing > 0
    assert differing < BIG.size // 100
    worst = float(np.max(np.abs(by_pow - roots_vec(BIG))))
    assert worst < 1e-15


def test_math_sqrt_is_the_same_operation_as_sqrt():
    by_math = np.array([math.sqrt(x) for x in BIG_LIST])
    assert int(np.count_nonzero(by_math != roots_vec(BIG))) == 0


# ===========================================================================
# Universal functions and creation
# ===========================================================================


def test_the_constructors_produce_the_documented_values():
    assert np.zeros(4).tolist() == [0.0] * 4
    assert np.ones((2, 3)).shape == (2, 3)
    assert np.full(3, 7).tolist() == [7, 7, 7]
    assert np.arange(0, 10, 2).tolist() == [0, 2, 4, 6, 8]
    assert np.linspace(0.0, 1.0, 5).tolist() == [0.0, 0.25, 0.5, 0.75, 1.0]
    assert np.eye(3).tolist() == [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ]


def test_arange_excludes_the_stop_and_linspace_includes_it():
    assert 10 not in np.arange(0, 10, 2).tolist()
    assert np.linspace(0.0, 1.0, 5)[-1] == 1.0


def test_full_takes_its_dtype_from_the_fill_value():
    assert np.full(3, 7).dtype == np.int64
    assert np.full(3, 7.0).dtype == np.float64


def test_a_ufunc_matches_the_comprehension():
    a = np.array([0.0, 1.0, 4.0, 9.0, 16.0])
    assert np.array_equal(np.sqrt(a), [math.sqrt(x) for x in a])


def test_math_sqrt_refuses_an_array():
    with pytest.raises(TypeError):
        math.sqrt(np.array([1.0, 2.0]))


def test_maximum_is_elementwise_and_max_is_a_reduction():
    small = np.array([-2.0, -0.5, 0.0, 0.5, 2.0])
    assert np.maximum(small, 0.0).tolist() == [0.0, 0.0, 0.0, 0.5, 2.0]
    assert float(np.max(small)) == 2.0


def test_star_is_elementwise_and_at_is_the_dot_product():
    left = np.array([1.0, 2.0, 3.0])
    right = np.array([10.0, 20.0, 30.0])
    assert (left * right).tolist() == [10.0, 40.0, 90.0]
    assert float(left @ right) == 140.0


def test_mismatched_shapes_raise_with_a_readable_message():
    with pytest.raises(ValueError) as excinfo:
        np.array([1.0, 2.0, 3.0]) + np.array([1.0, 2.0])
    assert "broadcast" in str(excinfo.value)


def test_a_scalar_broadcasts():
    assert (np.array([1.0, 2.0, 3.0]) + 100.0).tolist() == [101.0, 102.0, 103.0]


# ===========================================================================
# Masking and selection
# ===========================================================================


def test_a_comparison_returns_one_boolean_per_element():
    readings = dataset.small_readings()
    mask = readings > 50
    assert mask.dtype == np.bool_
    assert mask.shape == (dataset.N_SMALL,)


def test_counting_above_fifty():
    assert count_above(dataset.small_readings(), 50) == 9


def test_the_selected_values_are_the_documented_nine():
    readings = dataset.small_readings()
    assert select(readings, readings > 50).tolist() == [
        70, 83, 69, 65, 75, 73, 97, 64, 82
    ]


def test_the_selection_length_equals_the_count():
    readings = dataset.small_readings()
    mask = readings > 50
    assert select(readings, mask).size == int(mask.sum())


def test_any_all_and_mean_of_a_boolean_array():
    mask = dataset.small_readings() > 50
    assert bool(mask.any()) is True
    assert bool(mask.all()) is False
    assert float(mask.mean()) == 0.45


def test_mask_between_uses_ampersand_and_gives_the_documented_seven():
    readings = dataset.small_readings()
    mask = mask_between(readings, 30, 70)
    assert int(mask.sum()) == 7
    assert readings[mask].tolist() == [34, 69, 65, 37, 37, 41, 64]


def test_or_gives_the_documented_one():
    readings = dataset.small_readings()
    mask = (readings < 10) | (readings > 90)
    assert readings[mask].tolist() == [97]


def test_negating_a_mask():
    readings = dataset.small_readings()
    mask = mask_between(readings, 30, 70)
    assert int((~mask).sum()) == dataset.N_SMALL - int(mask.sum())


def test_and_raises_valueerror_with_the_ambiguous_truth_value_message():
    readings = dataset.small_readings()
    with pytest.raises(ValueError) as excinfo:
        (readings > 30) and (readings < 70)
    assert "truth value of an array with more than one element is ambiguous" in str(
        excinfo.value
    )


def test_or_the_keyword_raises_too():
    readings = dataset.small_readings()
    with pytest.raises(ValueError):
        (readings > 30) or (readings < 70)


def test_bool_of_a_multi_element_array_raises():
    with pytest.raises(ValueError):
        bool(dataset.small_readings() > 30)


def test_bool_of_a_one_element_array_does_not():
    """The message says "more than one element" and it means it."""
    assert bool(np.array([True])) is True


def test_the_missing_parentheses_raise_rather_than_giving_a_wrong_answer():
    readings = dataset.small_readings()
    with pytest.raises(ValueError):
        readings > 30 & readings < 70  # noqa: B015 - the exception is the point


def test_where_chooses_between_two_values():
    readings = dataset.small_readings()
    labels = np.where(readings > 50, 1, 0)
    assert labels.tolist() == (readings > 50).astype(int).tolist()
    assert int(labels.sum()) == 9


def test_where_accepts_an_array_on_either_branch():
    readings = dataset.small_readings()
    capped = np.where(readings > 50, 50, readings)
    assert int(capped.max()) == 50
    assert int(capped.min()) == int(readings.min())


def test_nonzero_gives_positions_rather_than_values():
    readings = dataset.small_readings()
    assert np.nonzero(readings > 50)[0].tolist() == [0, 1, 3, 8, 11, 13, 16, 17, 19]


def test_assigning_through_a_mask_changes_only_the_marked_elements():
    readings = dataset.small_readings()
    working = readings.copy()
    working[working > 90] = 90
    assert int(working.max()) == 90
    assert int(readings.max()) == 97
    assert int((working != readings).sum()) == 1


def test_fancy_indexing_takes_the_shape_of_the_index_and_allows_repeats():
    readings = dataset.small_readings()
    wanted = np.array([0, 5, 19, 5])
    assert readings[wanted].tolist() == [70, 21, 82, 21]
    assert readings[wanted].shape == wanted.shape


# ===========================================================================
# Axes and shapes
# ===========================================================================


def test_the_axis_you_name_disappears():
    grid = np.arange(12).reshape(3, 4)
    assert grid.sum(axis=0).shape == (4,)
    assert grid.sum(axis=1).shape == (3,)


def test_the_aggregate_values():
    grid = np.arange(12).reshape(3, 4)
    assert int(grid.sum()) == 66
    assert grid.sum(axis=0).tolist() == [12, 15, 18, 21]
    assert grid.sum(axis=1).tolist() == [6, 22, 38]
    assert grid.max(axis=1).tolist() == [3, 7, 11]
    assert grid.mean(axis=0).tolist() == [4.0, 5.0, 6.0, 7.0]


def test_keepdims_holds_the_shape_open():
    grid = np.arange(12).reshape(3, 4)
    assert grid.sum(axis=1, keepdims=True).shape == (3, 1)


def test_keepdims_is_what_lets_the_result_broadcast_back():
    grid = np.arange(1, 13, dtype=np.float64).reshape(3, 4)
    normalised = grid / grid.sum(axis=1, keepdims=True)
    assert np.allclose(normalised.sum(axis=1), 1.0, atol=dataset.TOL)


def test_newaxis_makes_a_column_and_a_row():
    v = np.array([1.0, 2.0, 3.0])
    assert v[:, np.newaxis].shape == (3, 1)
    assert v[np.newaxis, :].shape == (1, 3)


def test_a_column_against_a_row_broadcasts_to_every_pairing():
    v = np.array([1.0, 2.0, 3.0])
    table = v[:, np.newaxis] - v[np.newaxis, :]
    assert table.shape == (3, 3)
    assert table.tolist() == [[0.0, -1.0, -2.0], [1.0, 0.0, -1.0], [2.0, 1.0, 0.0]]


def test_reshape_minus_one_works_it_out():
    assert np.array([1.0, 2.0, 3.0]).reshape(-1, 1).shape == (3, 1)


def test_reshape_refuses_an_impossible_shape():
    with pytest.raises(ValueError):
        np.arange(12).reshape(5, 3)


# ===========================================================================
# Views and copies
# ===========================================================================


def test_a_row_slice_is_a_view_and_writing_to_it_writes_through():
    grid = np.arange(12).reshape(3, 4)
    row = grid[1]
    assert np.shares_memory(grid, row)
    row[0] = 999
    assert int(grid[1, 0]) == 999


def test_a_copy_breaks_the_link():
    grid = np.arange(12).reshape(3, 4)
    detached = grid[2].copy()
    detached[0] = -1
    assert int(grid[2, 0]) == 8
    assert not np.shares_memory(grid, detached)


def test_a_view_knows_its_owner_and_a_copy_does_not():
    grid = np.arange(12).reshape(3, 4)
    assert grid[1].base is not None
    assert grid[1].copy().base is None


@pytest.mark.parametrize(
    "make, expect_view",
    [
        (lambda a: a[1], True),
        (lambda a: a[:, 1], True),
        (lambda a: a[0:2, 1:3], True),
        (lambda a: a.T, True),
        (lambda a: a.reshape(4, 3), True),
        (lambda a: a.ravel(), True),
        (lambda a: a[a > 5], False),
        (lambda a: a[[0, 2]], False),
        (lambda a: a.copy(), False),
        (lambda a: a + 0, False),
        (lambda a: a.flatten(), False),
    ],
)
def test_which_operations_return_a_view(make, expect_view):
    grid = np.arange(12).reshape(3, 4)
    assert np.shares_memory(grid, make(grid)) is expect_view


def test_ravel_is_a_view_and_flatten_is_always_a_copy():
    """The pair that catches people: near-identical names, opposite behaviour."""
    grid = np.arange(12).reshape(3, 4)
    assert np.shares_memory(grid, grid.ravel())
    assert not np.shares_memory(grid, grid.flatten())


# ===========================================================================
# Sorting and ranking
# ===========================================================================


def test_np_sort_returns_a_new_array_and_leaves_the_original_alone():
    scores = np.array([5.0, 1.0, 9.0, 3.0])
    assert np.sort(scores).tolist() == [1.0, 3.0, 5.0, 9.0]
    assert scores.tolist() == [5.0, 1.0, 9.0, 3.0]


def test_the_sort_method_is_in_place_and_returns_none():
    scores = np.array([5.0, 1.0, 9.0, 3.0])
    assert scores.sort() is None
    assert scores.tolist() == [1.0, 3.0, 5.0, 9.0]


def test_argsort_gives_positions_and_reconstructs_the_sorted_values():
    scores = np.array([5.0, 1.0, 9.0, 3.0])
    order = np.argsort(scores)
    assert order.tolist() == [1, 3, 0, 2]
    assert scores[order].tolist() == np.sort(scores).tolist()


def test_top_k_indices_gives_the_best_first():
    assert top_k_indices(np.array([0.1, 0.9, 0.5]), 2).tolist() == [1, 2]


def test_top_k_asks_for_no_more_than_it_needs():
    assert top_k_indices(np.array([0.1, 0.9, 0.5]), 1).tolist() == [1]
    assert top_k_indices(np.array([0.1, 0.9, 0.5]), 3).tolist() == [1, 2, 0]


# ===========================================================================
# The Day 103 search, vectorised
# ===========================================================================


def test_the_catalogue_is_a_six_by_four_array():
    assert dataset.CATALOGUE.shape == (6, 4)
    assert len(dataset.ARTICLE_NAMES) == 6
    assert len(dataset.FEATURES) == 4


def test_cosine_similarities_returns_one_score_per_row():
    sims = cosine_similarities(dataset.CATALOGUE, dataset.QUERY)
    assert sims.shape == (6,)


def test_cosine_similarities_matches_the_one_row_at_a_time_version():
    """Day 103's loop, kept here as the thing the vectorised version replaced."""
    sims = cosine_similarities(dataset.CATALOGUE, dataset.QUERY)
    by_hand = []
    for row in dataset.CATALOGUE:
        dot = sum(float(x) * float(y) for x, y in zip(row, dataset.QUERY))
        left = math.sqrt(sum(float(x) * float(x) for x in row))
        right = math.sqrt(sum(float(y) * float(y) for y in dataset.QUERY))
        by_hand.append(dot / (left * right))
    assert np.allclose(sims, by_hand, atol=dataset.TOL)


def test_a_perfectly_aligned_row_scores_one():
    identity = np.array([[1.0, 0.0], [0.0, 1.0]])
    sims = cosine_similarities(identity, np.array([1.0, 0.0]))
    assert sims.tolist() == [1.0, 0.0]


def test_the_top_three_are_the_documented_articles_in_order():
    sims = cosine_similarities(dataset.CATALOGUE, dataset.QUERY)
    top = top_k_indices(sims, dataset.TOP_K)
    assert top.tolist() == [3, 2, 0]
    assert [dataset.ARTICLE_NAMES[i] for i in top] == [
        "race-day-nutrition",
        "marathon-plan",
        "roast-chicken",
    ]


def test_the_full_ranking_worst_first():
    sims = cosine_similarities(dataset.CATALOGUE, dataset.QUERY)
    assert np.argsort(sims).tolist() == [4, 5, 1, 0, 2, 3]


def test_the_margin_between_first_and_second_is_reported_as_small():
    sims = cosine_similarities(dataset.CATALOGUE, dataset.QUERY)
    top = top_k_indices(sims, 2)
    margin = float(sims[top[0]] - sims[top[1]])
    assert 0.0 < margin < 0.01


def test_argpartition_finds_the_same_top_three():
    sims = cosine_similarities(dataset.CATALOGUE, dataset.QUERY)
    partitioned = np.argpartition(-sims, dataset.TOP_K)[: dataset.TOP_K]
    ordered = partitioned[np.argsort(-sims[partitioned])]
    assert ordered.tolist() == top_k_indices(sims, dataset.TOP_K).tolist()


# ===========================================================================
# nan
# ===========================================================================


def test_nan_is_not_equal_to_itself():
    assert (np.nan == np.nan) is False
    assert (np.nan != np.nan) is True


def test_comparing_an_array_to_nan_finds_nothing():
    assert not (dataset.WITH_A_HOLE == np.nan).any()


def test_isnan_finds_it():
    assert np.isnan(dataset.WITH_A_HOLE).tolist() == [False, False, True, False]
    assert int(np.isnan(dataset.WITH_A_HOLE).sum()) == 1


def test_nan_propagates_through_every_plain_aggregation():
    holed = dataset.WITH_A_HOLE
    assert math.isnan(float(holed.sum()))
    assert math.isnan(float(holed.mean()))
    assert math.isnan(float(holed.max()))
    assert math.isnan(float(holed.min()))


def test_the_nan_aware_versions_skip_it():
    holed = dataset.WITH_A_HOLE
    assert float(np.nansum(holed)) == 7.0
    assert float(np.nanmax(holed)) == 4.0
    assert nan_aware_mean(holed) == 7.0 / 3.0


def test_nan_aware_mean_divides_by_the_count_that_exists():
    """Three readings, not four. Stated as arithmetic so the choice is visible."""
    assert nan_aware_mean(dataset.WITH_A_HOLE) == pytest.approx((1.0 + 2.0 + 4.0) / 3)


def test_where_a_nan_comes_from():
    with np.errstate(invalid="ignore", divide="ignore"):
        assert math.isnan(float(np.float64(0.0) / np.float64(0.0)))
        assert math.isnan(float(np.sqrt(np.array([-1.0]))[0]))
        assert math.isnan(float(np.float64(np.inf) - np.float64(np.inf)))


def test_nan_survives_a_sort_and_goes_to_the_end():
    """Worth knowing before an argsort-based top-k meets missing data."""
    holed = np.array([3.0, np.nan, 1.0, 2.0])
    order = np.argsort(holed)
    assert order.tolist()[-1] == 1
    assert math.isnan(float(holed[order][-1]))


# ===========================================================================
# When not to vectorise
# ===========================================================================


def test_on_four_elements_the_comprehension_wins():
    """A measurement, not a belief. If this ever stops being true on some
    machine the suite will say so."""
    small = [1.0, 2.0, 3.0, 4.0]
    loop = time_call(lambda: [math.sqrt(x) for x in small], 2000)
    vec = time_call(lambda: np.sqrt(np.array(small)), 2000)
    assert median_seconds(vec) > median_seconds(loop)


def test_a_sequential_dependence_has_no_one_line_equivalent():
    changes = [-30.0, 50.0, -200.0, 20.0]
    balances = [100.0]
    for change in changes:
        balances.append(max(balances[-1] + change, 0.0))
    naive = np.maximum(100.0 + np.cumsum(changes), 0.0)
    assert balances[1:] == [70.0, 120.0, 0.0, 20.0]
    assert naive.tolist() != balances[1:]


def test_the_pairwise_table_grows_with_the_square():
    x = np.arange(2000, dtype=np.float64)
    pairwise = x[:, None] - x[None, :]
    assert pairwise.shape == (2000, 2000)
    assert pairwise.nbytes == 32_000_000
    assert pairwise.nbytes == x.nbytes * 2000
