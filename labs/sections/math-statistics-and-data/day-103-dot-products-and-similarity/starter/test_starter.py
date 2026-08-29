"""Your running score. Run from the LAB DIRECTORY:

    .venv/bin/pytest starter -q

Anything you have not written yet is SKIPPED, not failed. A skip means "not
attempted"; a failure means "attempted and wrong", and the failure prints both
your answer and the real one.

Float comparisons use a tolerance of TOL, stated below, because floating-point
equality is a trap (Day 70) and because this lab measured three of six articles
missing exact 1.0 when compared with themselves.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

import answers
from similarity import (
    cosine_distance,
    cosine_similarity,
    dot,
    euclidean_distance,
    l2_norm,
    normalise,
    rank_by_cosine,
)

TOL = 1e-6

CATALOGUE = {
    "roast-chicken":      [9, 0, 1, 0],
    "slow-cooker-stew":   [8, 0, 2, 0],
    "marathon-plan":      [0, 9, 1, 2],
    "race-day-nutrition": [4, 6, 3, 0],
    "household-budget":   [1, 0, 9, 0],
    "storm-bulletin":     [0, 1, 0, 9],
}
LONG_ROAST_CHICKEN = [18, 0, 2, 0]

TRIANGLE_A = [1, 0]
TRIANGLE_B = [1, 1]
TRIANGLE_C = [0, 1]

QUERY_ROAST = [1, 0, 0, 0]
QUERY_TRAINING = [2, 5, 0, 0]


def written(fn, *args, **kwargs):
    """Run part of your toolkit, or skip the test if it is not written yet."""
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
    assert np.__version__, "numpy is importable"
    assert math.isclose(np.linalg.norm([3, 4]), 5.0), "numpy agrees that 3-4-5 works"


# -- Exercise 1: your similarity toolkit -------------------------------------


def test_1_1_dot_is_the_sum_of_products():
    assert written(dot, [1, 2, 3], [4, 5, 6]) == pytest.approx(32.0, abs=TOL)
    assert dot([9, 0, 1, 0], [8, 0, 2, 0]) == pytest.approx(74.0, abs=TOL)


def test_1_1_dot_matches_numpy_on_every_catalogue_pair():
    written(dot, [1], [1])
    for first, a in CATALOGUE.items():
        for second, b in CATALOGUE.items():
            assert dot(a, b) == pytest.approx(float(np.dot(a, b)), abs=TOL), (
                first,
                second,
            )


def test_1_1_dot_refuses_mismatched_lengths():
    written(dot, [1], [1])
    with pytest.raises(ValueError):
        dot([1, 2, 3], [1, 2])


def test_1_2_l2_norm():
    assert written(l2_norm, [3, 4]) == pytest.approx(5.0, abs=TOL)
    assert l2_norm([9, 0, 1, 0]) == pytest.approx(math.sqrt(82), abs=TOL)


def test_1_2_l2_norm_matches_numpy():
    written(l2_norm, [1])
    for label, vector in CATALOGUE.items():
        assert l2_norm(vector) == pytest.approx(
            float(np.linalg.norm(vector)), abs=TOL
        ), label


def test_1_3_normalise_gives_length_one():
    assert written(normalise, [3, 4]) == pytest.approx([0.6, 0.8], abs=TOL)
    for label, vector in CATALOGUE.items():
        assert l2_norm(normalise(vector)) == pytest.approx(1.0, abs=TOL), label


def test_1_3_normalise_does_not_modify_its_argument():
    vector = [3, 4]
    written(normalise, vector)
    assert vector == [3, 4], "normalise must return a NEW list"


def test_1_3_normalise_refuses_the_zero_vector():
    written(normalise, [3, 4])
    with pytest.raises(ValueError):
        normalise([0, 0, 0, 0])


def test_1_4_euclidean_distance():
    assert written(
        euclidean_distance, [9, 0, 1, 0], [8, 0, 2, 0]
    ) == pytest.approx(math.sqrt(2), abs=TOL)
    assert euclidean_distance([0, 0], [3, 4]) == pytest.approx(5.0, abs=TOL)


def test_1_4_euclidean_distance_matches_numpy():
    written(euclidean_distance, [1], [1])
    for first, a in CATALOGUE.items():
        for second, b in CATALOGUE.items():
            expected = float(np.linalg.norm(np.array(a) - np.array(b)))
            assert euclidean_distance(a, b) == pytest.approx(expected, abs=TOL), (
                first,
                second,
            )


def test_1_5_cosine_similarity_basic_cases():
    assert written(cosine_similarity, [1, 0], [1, 0]) == pytest.approx(1.0, abs=TOL)
    assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0, abs=TOL)
    assert cosine_similarity([1, 0], [-1, 0]) == pytest.approx(-1.0, abs=TOL)
    assert cosine_similarity([1, 0], [1, 1]) == pytest.approx(
        1 / math.sqrt(2), abs=TOL
    )


def test_1_5_cosine_similarity_matches_numpy():
    written(cosine_similarity, [1, 0], [1, 0])
    for first, a in CATALOGUE.items():
        for second, b in CATALOGUE.items():
            expected = float(
                np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
            )
            assert cosine_similarity(a, b) == pytest.approx(expected, abs=TOL), (
                first,
                second,
            )


@pytest.mark.parametrize("factor", [0.5, 2, 3, 100])
def test_1_5_cosine_ignores_magnitude(factor):
    a, b = CATALOGUE["roast-chicken"], CATALOGUE["race-day-nutrition"]
    base = written(cosine_similarity, a, b)
    assert cosine_similarity([factor * x for x in a], b) == pytest.approx(
        base, abs=TOL
    )
    assert cosine_similarity(a, [factor * x for x in b]) == pytest.approx(
        base, abs=TOL
    )


def test_1_5_cosine_refuses_the_zero_vector():
    written(cosine_similarity, [1, 0], [1, 0])
    with pytest.raises(ValueError):
        cosine_similarity([0, 0, 0, 0], CATALOGUE["roast-chicken"])


def test_1_5_cosine_is_clamped_so_acos_never_raises():
    """The clamp is load-bearing: without it this catalogue breaks acos."""
    written(cosine_similarity, [1, 0], [1, 0])
    for label, vector in CATALOGUE.items():
        value = cosine_similarity(vector, vector)
        assert -1.0 <= value <= 1.0, label
        math.acos(value)  # raises ValueError if the clamp is missing


def test_1_6_cosine_distance():
    assert written(cosine_distance, [1, 0], [1, 0]) == pytest.approx(0.0, abs=TOL)
    assert cosine_distance([1, 0], [0, 1]) == pytest.approx(1.0, abs=TOL)
    assert cosine_distance([1, 0], [-1, 0]) == pytest.approx(2.0, abs=TOL)


def test_1_7_rank_by_cosine_orders_best_first():
    ranked = written(rank_by_cosine, QUERY_ROAST, CATALOGUE)
    assert [label for label, _ in ranked][:2] == [
        "roast-chicken",
        "slow-cooker-stew",
    ]
    scores = [score for _, score in ranked]
    assert scores == sorted(scores, reverse=True)


def test_1_7_rank_by_cosine_breaks_ties_alphabetically():
    ranked = written(rank_by_cosine, QUERY_ROAST, CATALOGUE)
    zeros = [label for label, score in ranked if abs(score) < TOL]
    assert zeros == ["marathon-plan", "storm-bulletin"]


def test_1_7_rank_by_cosine_returns_every_item():
    ranked = written(rank_by_cosine, QUERY_TRAINING, CATALOGUE)
    assert sorted(label for label, _ in ranked) == sorted(CATALOGUE)


# -- Exercise 2: the length confound -----------------------------------------


def test_2_1_distance_to_the_doubled_copy():
    assert predicted("DISTANCE_TO_DOUBLED_COPY") == pytest.approx(
        math.sqrt(82), abs=1e-4
    )


def test_2_2_distance_to_race_day():
    assert predicted("DISTANCE_TO_RACE_DAY") == pytest.approx(math.sqrt(65), abs=1e-4)


def test_2_3_the_doubled_copy_really_is_further():
    assert predicted("DOUBLED_COPY_IS_FURTHER") is True


def test_2_4_cosine_to_the_doubled_copy():
    assert predicted("COSINE_TO_DOUBLED_COPY") == pytest.approx(1.0, abs=1e-4)


def test_2_5_the_general_fact():
    assert predicted("DISTANCE_BETWEEN_V_AND_2V") == "|v|"


def test_2_the_predictions_match_your_own_code():
    """Your predictions and your implementation must agree with each other."""
    written(euclidean_distance, [1], [1])
    written(cosine_similarity, [1, 0], [1, 0])
    short = CATALOGUE["roast-chicken"]
    assert euclidean_distance(short, LONG_ROAST_CHICKEN) == pytest.approx(
        predicted("DISTANCE_TO_DOUBLED_COPY"), abs=1e-4
    )
    assert cosine_similarity(short, LONG_ROAST_CHICKEN) == pytest.approx(
        predicted("COSINE_TO_DOUBLED_COPY"), abs=1e-4
    )


# -- Exercise 3: the sign ----------------------------------------------------


def test_3_1_same_direction():
    assert predicted("DOT_SAME_DIRECTION") == pytest.approx(18.0, abs=TOL)


def test_3_2_perpendicular():
    assert predicted("DOT_PERPENDICULAR") == pytest.approx(0.0, abs=TOL)


def test_3_3_opposite():
    assert predicted("DOT_OPPOSITE") == pytest.approx(-18.0, abs=TOL)


def test_3_4_the_45_degree_case():
    assert predicted("ANGLE_45_CASE") == pytest.approx(45.0, abs=0.5)


def test_3_5_orthogonal_to_storm_bulletin():
    assert predicted("ORTHOGONAL_TO_STORM_BULLETIN") == [
        "household-budget",
        "roast-chicken",
        "slow-cooker-stew",
    ]


# -- Exercise 4: not a metric ------------------------------------------------


def test_4_1_cosine_distance_a_to_b():
    assert predicted("D_A_TO_B") == pytest.approx(1 - 1 / math.sqrt(2), abs=1e-4)


def test_4_2_cosine_distance_a_to_c():
    assert predicted("D_A_TO_C") == pytest.approx(1.0, abs=1e-4)


def test_4_3_the_triangle_inequality_fails_for_cosine():
    assert predicted("TRIANGLE_HOLDS_FOR_COSINE") is False


def test_4_4_the_triangle_inequality_holds_for_euclidean():
    assert predicted("TRIANGLE_HOLDS_FOR_EUCLIDEAN") is True


def test_4_your_own_code_reproduces_the_failure():
    written(cosine_distance, [1, 0], [1, 0])
    ab = cosine_distance(TRIANGLE_A, TRIANGLE_B)
    bc = cosine_distance(TRIANGLE_B, TRIANGLE_C)
    ac = cosine_distance(TRIANGLE_A, TRIANGLE_C)
    assert ac > ab + bc, "cosine distance should fail the triangle inequality here"


# -- Exercise 5: the same ranking on the sphere ------------------------------


def test_5_1_the_identity():
    assert predicted("UNIT_DISTANCE_FORMULA") == "2 - 2cos"


def test_5_2_perpendicular_unit_vectors():
    assert predicted(
        "DISTANCE_BETWEEN_PERPENDICULAR_UNIT_VECTORS"
    ) == pytest.approx(math.sqrt(2), abs=1e-4)


def test_5_3_opposite_unit_vectors():
    assert predicted("DISTANCE_BETWEEN_OPPOSITE_UNIT_VECTORS") == pytest.approx(
        2.0, abs=1e-4
    )


def test_5_4_normalised_rankings_match():
    assert predicted("NORMALISED_RANKINGS_MATCH") is True


def test_5_5_raw_rankings_do_not():
    assert predicted("RAW_RANKINGS_MATCH") is False


def test_5_your_own_code_proves_the_ranking_equivalence():
    written(normalise, [3, 4])
    written(cosine_similarity, [1, 0], [1, 0])
    written(euclidean_distance, [1], [1])
    units = {label: normalise(v) for label, v in CATALOGUE.items()}
    query = units["roast-chicken"]
    by_cosine = sorted(units, key=lambda k: (-cosine_similarity(query, units[k]), k))
    by_euclid = sorted(units, key=lambda k: (euclidean_distance(query, units[k]), k))
    assert by_cosine == by_euclid


# -- Exercise 6: the search, and the curse -----------------------------------


def test_6_1_top_hit_for_the_cooking_note():
    assert predicted("TOP_HIT_FOR_ROAST_IT") == "roast-chicken"


def test_6_2_raw_euclidean_picks_a_different_article():
    assert predicted("NEAREST_BY_RAW_EUCLIDEAN_FOR_ROAST_IT") == "slow-cooker-stew"


def test_6_3_top_hit_for_the_training_query():
    assert predicted("TOP_HIT_FOR_TRAINING") == "race-day-nutrition"


def test_6_4_scaling_the_query_changes_nothing():
    assert predicted("SCALING_THE_QUERY_CHANGES_THE_RANKING") is False


def test_6_5_high_dimensional_cosine_tends_to_zero():
    assert predicted("MEAN_ABS_COSINE_TENDS_TOWARDS") == 0


def test_6_your_own_search_finds_the_predicted_articles():
    ranked = written(rank_by_cosine, QUERY_ROAST, CATALOGUE)
    assert ranked[0][0] == predicted("TOP_HIT_FOR_ROAST_IT")
    training = rank_by_cosine(QUERY_TRAINING, CATALOGUE)
    assert training[0][0] == predicted("TOP_HIT_FOR_TRAINING")


def test_6_your_own_code_measures_the_curse():
    """Generate random pairs at growing dimension and watch |cos| collapse."""
    written(cosine_similarity, [1, 0], [1, 0])
    rng = np.random.default_rng(103)
    previous = None
    for dimension in (2, 32, 512):
        values = [
            abs(
                cosine_similarity(
                    rng.standard_normal(dimension).tolist(),
                    rng.standard_normal(dimension).tolist(),
                )
            )
            for _ in range(200)
        ]
        mean = sum(values) / len(values)
        if previous is not None:
            assert mean < previous, dimension
        previous = mean
    assert previous < 0.1
