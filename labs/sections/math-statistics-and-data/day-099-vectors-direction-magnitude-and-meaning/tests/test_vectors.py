"""The reference suite for the Day 099 lab.

Two rules run through every test in this file.

1. **No float is ever compared with `==`.** Every numeric assertion goes
   through `math.isclose` or `numpy.allclose` with the tolerance stated at the
   top of the file. Where a value happens to come out exact, the test still
   uses a tolerance, because "it was exact on this machine today" is not a
   property you can rely on.

2. **Agreement with NumPy is proved, not assumed.** Every operation the lab
   implements by hand is run again through NumPy on the same inputs, and the
   two results are asserted equal to tolerance. If the loop is wrong, this
   suite says so.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))

import vectors as pure  # noqa: E402
from embeddings import CATALOGUE  # noqa: E402

# The tolerance used by every numeric assertion in this file. Stated once, in
# one place, so that a reader can see exactly how much slack the suite allows.
REL_TOL = 1e-9
ABS_TOL = 1e-12


def close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=REL_TOL, abs_tol=ABS_TOL)


def allclose(a, b) -> bool:
    return bool(np.allclose(a, b, rtol=REL_TOL, atol=ABS_TOL))


# ---------------------------------------------------------------------------
# 1. The operations do what the definitions say
# ---------------------------------------------------------------------------


def test_addition_is_componentwise():
    assert allclose(pure.add([1, 2, 3], [10, 20, 30]), [11, 22, 33])


def test_addition_is_commutative():
    u, v = [3, -4, 0.5], [1, 7, -2]
    assert allclose(pure.add(u, v), pure.add(v, u))


def test_subtraction_is_addition_of_the_negation():
    u, v = [3, 4], [1, -2]
    assert allclose(pure.subtract(u, v), pure.add(u, pure.negate(v)))


def test_subtracting_a_vector_from_itself_gives_the_zero_vector():
    v = [7, -1, 4]
    assert allclose(pure.subtract(v, v), pure.zero(3))


def test_the_zero_vector_is_the_additive_identity():
    v = [7, -1, 4]
    assert allclose(pure.add(v, pure.zero(3)), v)


def test_scaling_by_one_changes_nothing_and_by_zero_gives_the_zero_vector():
    v = [2, -5, 9]
    assert allclose(pure.scale(1, v), v)
    assert allclose(pure.scale(0, v), pure.zero(3))


def test_scaling_multiplies_the_magnitude_by_the_absolute_value_of_the_scalar():
    v = [3, 4]
    for k in (2, 0.5, -3, 1000):
        assert close(pure.l2_norm(pure.scale(k, v)), abs(k) * pure.l2_norm(v))


def test_a_positive_scalar_leaves_the_direction_alone():
    """Same direction means the same unit vector."""
    v = [3, 4]
    assert allclose(pure.normalise(pure.scale(7, v)), pure.normalise(v))


def test_a_negative_scalar_reverses_the_direction():
    v = [3, 4]
    assert allclose(
        pure.normalise(pure.scale(-7, v)), pure.negate(pure.normalise(v))
    )


def test_dot_product_returns_one_number_not_a_vector():
    result = pure.dot([1, 2, 3], [4, 5, 6])
    assert isinstance(result, float)
    # 1*4 + 2*5 + 3*6 = 4 + 10 + 18 = 32
    assert close(result, 32)


def test_dot_product_of_perpendicular_vectors_is_zero():
    assert close(pure.dot([1, 0], [0, 1]), 0)
    assert close(pure.dot([3, 4], [-4, 3]), 0)


def test_dot_of_a_vector_with_itself_is_its_magnitude_squared():
    v = [3, 4, 12]
    assert close(pure.dot(v, v), pure.l2_norm(v) ** 2)


# ---------------------------------------------------------------------------
# 2. Magnitude, checked against answers a human can get on paper
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "vector,expected",
    [
        ([3, 4], 5),  # 9 + 16 = 25
        ([6, 8], 10),  # 36 + 64 = 100
        ([2, 3, 6], 7),  # 4 + 9 + 36 = 49
        ([1, 2, 2], 3),  # 1 + 4 + 4 = 9
        ([3, 4, 12], 13),  # 9 + 16 + 144 = 169
        ([7, 1, 5, 3, 9, 2], 13),  # 49 + 1 + 25 + 9 + 81 + 4 = 169
        ([0, 0, 0], 0),
        ([-3, -4], 5),  # squaring removes the signs
    ],
)
def test_l2_norm_matches_the_hand_computed_answer(vector, expected):
    assert close(pure.l2_norm(vector), expected)


@pytest.mark.parametrize(
    "vector,expected",
    [
        ([3, 4], 7),
        ([1, 2, 2], 5),
        ([-3, -4], 7),
        ([0, 0, 0], 0),
        ([4, 0, 0], 4),
        ([2, 2, 2], 6),
    ],
)
def test_l1_norm_matches_the_hand_computed_answer(vector, expected):
    assert close(pure.l1_norm(vector), expected)


def test_the_norm_of_a_unit_axis_vector_is_one_in_any_dimension():
    for dimension in (1, 2, 3, 10, 300):
        basis = pure.zero(dimension)
        basis[0] = 1.0
        assert close(pure.l2_norm(basis), 1.0)


def test_l1_is_never_smaller_than_l2():
    """A real inequality, not a coincidence: squaring shrinks the small parts."""
    for vector in ([3, 4], [1, 2, 2], [2, 2, 2], [4, 0, 0], [0.5, -0.25, 7]):
        assert pure.l1_norm(vector) >= pure.l2_norm(vector) - ABS_TOL


# ---------------------------------------------------------------------------
# 3. Distance is the magnitude of the difference
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "u,v,expected",
    [
        ([1, 2], [4, 6], 5),  # difference (-3, -4)
        ([0, 0, 0], [2, 3, 6], 7),
        ([1, 1, 1], [2, 3, 3], 3),
        ([10, 10], [10, 10], 0),
    ],
)
def test_distance_matches_the_hand_computed_answer(u, v, expected):
    assert close(pure.distance(u, v), expected)


def test_distance_is_the_norm_of_the_difference_by_construction():
    u, v = [9, 0, 1, 0], [1, 0, 9, 0]
    assert close(pure.distance(u, v), pure.l2_norm(pure.subtract(u, v)))


def test_distance_is_symmetric():
    u, v = [9, 0, 1, 0], [0, 9, 1, 2]
    assert close(pure.distance(u, v), pure.distance(v, u))


def test_distance_from_a_point_to_itself_is_zero():
    for vector in CATALOGUE.values():
        assert close(pure.distance(vector, vector), 0)


def test_the_triangle_inequality_holds():
    """Going via a third point is never shorter than going direct."""
    a, b, c = [1, 2], [7, 1], [4, 9]
    assert pure.distance(a, c) <= pure.distance(a, b) + pure.distance(b, c) + ABS_TOL


# ---------------------------------------------------------------------------
# 4. Normalisation, and the float trap it hides
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "vector",
    [[3, 4], [1, 2, 2], [1, 1], [1, 1, 1], [0.1, 0.2, 0.3], [2, 3, 6], [-5, 12]],
)
def test_a_normalised_vector_has_magnitude_one_to_tolerance(vector):
    assert close(pure.l2_norm(pure.normalise(vector)), 1.0)
    assert pure.is_unit(pure.normalise(vector), rel_tol=REL_TOL, abs_tol=ABS_TOL)


def test_normalising_preserves_direction_but_not_magnitude():
    v = [3, 4]
    unit = pure.normalise(v)
    # Direction preserved: unit is v scaled by a positive number, so scaling it
    # back up by the original magnitude recovers v exactly to tolerance.
    assert allclose(pure.scale(pure.l2_norm(v), unit), v)
    # Magnitude changed: 5 became 1.
    assert not close(pure.l2_norm(unit), pure.l2_norm(v))


def test_comparing_a_normalised_norm_with_exact_equality_really_does_fail():
    """The bug this lab exists to teach, demonstrated rather than asserted.

    At least one of these vectors normalises to a magnitude that is not
    exactly 1.0, so a suite written with `==` would fail on it. If this test
    ever stops finding such a vector, the lesson's claim needs re-checking on
    the machine in question — not silently deleting.
    """
    cases = [[3, 4], [1, 2, 2], [1, 1], [1, 1, 1], [0.1, 0.2, 0.3], [2, 3, 6]]
    norms = [pure.l2_norm(pure.normalise(v)) for v in cases]
    assert all(close(n, 1.0) for n in norms), "every case is 1.0 to tolerance"
    assert any(n != 1.0 for n in norms), (
        "no case departed from exactly 1.0 on this machine; the == trap did "
        "not reproduce here and the lesson's numbers must be re-verified"
    )


def test_the_zero_vector_cannot_be_normalised():
    with pytest.raises(ValueError, match="zero vector"):
        pure.normalise([0, 0, 0])


def test_normalising_an_already_unit_vector_is_a_no_op():
    unit = pure.normalise([3, 4])
    assert allclose(pure.normalise(unit), unit)


# ---------------------------------------------------------------------------
# 5. Dimension mismatches are refused, not silently truncated
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "operation",
    [pure.add, pure.subtract, pure.dot, pure.distance, pure.l1_distance],
)
def test_operations_refuse_vectors_of_different_dimension(operation):
    with pytest.raises(ValueError, match="dimension mismatch"):
        operation([1, 2], [1, 2, 3])


def test_zero_refuses_a_negative_dimension():
    with pytest.raises(ValueError):
        pure.zero(-1)


# ---------------------------------------------------------------------------
# 6. NumPy agrees — proved on the same inputs, not assumed
# ---------------------------------------------------------------------------

U = [3, 4, 12]
V = [1, -2, 5]


def test_numpy_agrees_on_addition_and_subtraction():
    assert allclose(pure.add(U, V), np.array(U) + np.array(V))
    assert allclose(pure.subtract(U, V), np.array(U) - np.array(V))


def test_numpy_agrees_on_scaling():
    assert allclose(pure.scale(2.5, U), 2.5 * np.array(U))


def test_numpy_agrees_on_the_dot_product():
    assert close(pure.dot(U, V), float(np.dot(U, V)))


def test_numpy_agrees_on_the_l2_norm():
    assert close(pure.l2_norm(U), float(np.linalg.norm(U)))


def test_numpy_agrees_on_the_l1_norm():
    assert close(pure.l1_norm(U), float(np.linalg.norm(U, ord=1)))


def test_numpy_agrees_on_distance():
    assert close(
        pure.distance(U, V), float(np.linalg.norm(np.array(U) - np.array(V)))
    )


def test_numpy_agrees_on_normalisation():
    assert allclose(pure.normalise(U), np.array(U) / np.linalg.norm(U))


def test_numpy_agrees_on_every_catalogue_norm_at_once():
    labels = list(CATALOGUE)
    matrix = np.array([CATALOGUE[label] for label in labels], dtype=float)
    assert allclose(
        np.linalg.norm(matrix, axis=1),
        [pure.l2_norm(CATALOGUE[label]) for label in labels],
    )


def test_numpy_agrees_on_every_pairwise_distance():
    labels = list(CATALOGUE)
    matrix = np.array([CATALOGUE[label] for label in labels], dtype=float)
    for i, a in enumerate(labels):
        row = np.linalg.norm(matrix - matrix[i], axis=1)
        expected = [pure.distance(CATALOGUE[a], CATALOGUE[b]) for b in labels]
        assert allclose(row, expected)


# ---------------------------------------------------------------------------
# 7. The embedding: which item is nearest to which
# ---------------------------------------------------------------------------


def test_the_two_cooking_articles_are_the_closest_pair_in_the_catalogue():
    labels = list(CATALOGUE)
    pairs = [
        (pure.distance(CATALOGUE[a], CATALOGUE[b]), a, b)
        for i, a in enumerate(labels)
        for b in labels[i + 1 :]
    ]
    score, a, b = min(pairs)
    assert {a, b} == {"roast-chicken", "slow-cooker-stew"}
    # (9,0,1,0) - (8,0,2,0) = (1,0,-1,0); 1 + 1 = 2; sqrt(2)
    assert close(score, math.sqrt(2))


@pytest.mark.parametrize(
    "item,expected_neighbour",
    [
        ("roast-chicken", "slow-cooker-stew"),
        ("slow-cooker-stew", "roast-chicken"),
        ("marathon-plan", "race-day-nutrition"),
        ("race-day-nutrition", "marathon-plan"),
        ("household-budget", "race-day-nutrition"),
        ("storm-bulletin", "marathon-plan"),
    ],
)
def test_each_article_has_the_expected_nearest_neighbour(item, expected_neighbour):
    winner, _score = pure.nearest(CATALOGUE[item], CATALOGUE, exclude=item)
    assert winner == expected_neighbour


def test_the_budget_to_race_day_distance_is_exactly_nine():
    # (1,0,9,0) - (4,6,3,0) = (-3,-6,6,0); 9 + 36 + 36 = 81; sqrt(81) = 9
    assert close(
        pure.distance(CATALOGUE["household-budget"], CATALOGUE["race-day-nutrition"]),
        9,
    )


def test_nearest_without_exclude_returns_the_item_itself_at_zero():
    winner, score = pure.nearest(CATALOGUE["roast-chicken"], CATALOGUE)
    assert winner == "roast-chicken"
    assert close(score, 0)


def test_nearest_raises_when_there_is_nothing_to_compare_against():
    with pytest.raises(ValueError):
        pure.nearest([1, 2], {}, exclude=None)


def test_pairwise_distances_covers_every_unordered_pair_once():
    result = pure.pairwise_distances(CATALOGUE)
    n = len(CATALOGUE)
    assert len(result) == n * (n - 1) // 2


# ---------------------------------------------------------------------------
# 8. L1 and L2 rank the same candidates differently
# ---------------------------------------------------------------------------


def test_l1_and_l2_disagree_about_which_candidate_is_nearest():
    query = [0, 0, 0]
    candidates = {"spike": [4, 0, 0], "spread": [2, 2, 2]}

    l2_winner, l2_score = pure.nearest(query, candidates, metric=pure.distance)
    l1_winner, l1_score = pure.nearest(query, candidates, metric=pure.l1_distance)

    assert l2_winner == "spread"
    assert close(l2_score, math.sqrt(12))
    assert l1_winner == "spike"
    assert close(l1_score, 4)
    assert l2_winner != l1_winner


def test_the_disagreement_survives_moving_away_from_the_origin():
    """It is the shape of the difference that matters, not the position."""
    query = [10, 10, 10]
    candidates = {"spike": [14, 10, 10], "spread": [12, 12, 12]}
    assert pure.nearest(query, candidates, metric=pure.distance)[0] == "spread"
    assert pure.nearest(query, candidates, metric=pure.l1_distance)[0] == "spike"


def test_numpy_agrees_about_the_disagreement():
    query = np.zeros(3)
    spike = np.array([4.0, 0.0, 0.0])
    spread = np.array([2.0, 2.0, 2.0])
    assert float(np.linalg.norm(spread - query)) < float(
        np.linalg.norm(spike - query)
    )
    assert float(np.linalg.norm(spike - query, ord=1)) < float(
        np.linalg.norm(spread - query, ord=1)
    )


# ---------------------------------------------------------------------------
# 9. Normalising changes which article wins
# ---------------------------------------------------------------------------


def test_normalising_changes_the_nearest_article_for_a_short_query():
    query = [1, 0, 0, 0]
    unit_catalogue = {k: pure.normalise(v) for k, v in CATALOGUE.items()}

    raw_winner, _ = pure.nearest(query, CATALOGUE)
    unit_winner, _ = pure.nearest(pure.normalise(query), unit_catalogue)

    assert raw_winner == "slow-cooker-stew"
    assert unit_winner == "roast-chicken"
    assert raw_winner != unit_winner


def test_a_longer_copy_of_the_same_article_is_identical_once_normalised():
    short = CATALOGUE["roast-chicken"]
    long_version = pure.scale(3, short)
    assert pure.distance(short, long_version) > 1.0
    assert close(pure.distance(pure.normalise(short), pure.normalise(long_version)), 0)


def test_articles_with_no_cooking_component_are_perpendicular_to_a_cooking_query():
    """Dot product zero means perpendicular, and it shows up as distance sqrt(2)."""
    query_unit = pure.normalise([1, 0, 0, 0])
    for label in ("marathon-plan", "storm-bulletin"):
        item_unit = pure.normalise(CATALOGUE[label])
        assert close(pure.dot(query_unit, item_unit), 0)
        assert close(pure.distance(query_unit, item_unit), math.sqrt(2))
