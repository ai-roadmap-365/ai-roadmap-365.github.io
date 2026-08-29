"""The reference suite: every claim the lesson makes, asserted on real values.

Run from the LAB DIRECTORY:

    .venv/bin/pytest examples -q

Every float comparison declares a tolerance. TOL is 1e-12 for arithmetic that
should agree to the last few bits, and a looser, named tolerance is used where
sampling noise is involved and said so.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from catalogue import (
    CATALOGUE,
    LONG_ROAST_CHICKEN,
    PROJECTION_A,
    PROJECTION_B,
    QUERIES,
    SIGN_CASES,
    TRIANGLE_A,
    TRIANGLE_B,
    TRIANGLE_C,
)
from similarity import (
    angle_degrees,
    cosine_distance,
    cosine_similarity,
    dot,
    euclidean_distance,
    l2_norm,
    mean_absolute_cosine,
    normalise,
    normalise_all,
    rank_by_cosine,
    rank_by_euclidean,
    scalar_projection,
    vector_projection,
)

TOL = 1e-12
SAMPLING_TOL = 0.05  # 5%: the dimensionality section samples, so it has noise


# -- The dot product itself --------------------------------------------------


def test_dot_is_the_sum_of_products():
    assert dot([1, 2, 3], [4, 5, 6]) == 32.0  # 4 + 10 + 18


def test_dot_matches_numpy_on_every_catalogue_pair():
    for first, a in CATALOGUE.items():
        for second, b in CATALOGUE.items():
            assert dot(a, b) == pytest.approx(float(np.dot(a, b)), abs=TOL), (
                first,
                second,
            )


def test_dot_is_symmetric():
    a, b = CATALOGUE["roast-chicken"], CATALOGUE["marathon-plan"]
    assert dot(a, b) == dot(b, a)


def test_dot_of_a_vector_with_itself_is_its_length_squared():
    for label, vector in CATALOGUE.items():
        assert dot(vector, vector) == pytest.approx(l2_norm(vector) ** 2, abs=1e-9), label


def test_dot_refuses_mismatched_lengths():
    with pytest.raises(ValueError):
        dot([1, 2, 3], [1, 2])


def test_the_geometric_and_algebraic_definitions_agree():
    a, b = PROJECTION_A, PROJECTION_B
    geometric = l2_norm(a) * l2_norm(b) * cosine_similarity(a, b)
    assert dot(a, b) == pytest.approx(geometric, abs=1e-9)


def test_the_projection_triangle_is_three_four_five():
    assert l2_norm(PROJECTION_A) == pytest.approx(5.0, abs=TOL)
    assert l2_norm(PROJECTION_B) == pytest.approx(10.0, abs=TOL)
    assert dot(PROJECTION_A, PROJECTION_B) == pytest.approx(30.0, abs=TOL)


def test_scalar_projection_is_the_shadow_length():
    assert scalar_projection(PROJECTION_A, PROJECTION_B) == pytest.approx(6.0, abs=1e-9)


def test_the_shadow_vector_has_the_shadow_length():
    shadow = vector_projection(PROJECTION_A, PROJECTION_B)
    assert l2_norm(shadow) == pytest.approx(6.0, abs=1e-9)
    assert shadow == pytest.approx([3.6, 4.8], abs=1e-9)


def test_projection_is_not_symmetric_even_though_dot_is():
    onto_a = scalar_projection(PROJECTION_A, PROJECTION_B)
    onto_b = scalar_projection(PROJECTION_B, PROJECTION_A)
    assert onto_a == pytest.approx(6.0, abs=1e-9)
    assert onto_b == pytest.approx(3.0, abs=1e-9)
    assert dot(PROJECTION_A, PROJECTION_B) == dot(PROJECTION_B, PROJECTION_A)


def test_projecting_a_vector_onto_itself_gives_its_length():
    for label, vector in CATALOGUE.items():
        assert scalar_projection(vector, vector) == pytest.approx(
            l2_norm(vector), abs=1e-9
        ), label


# -- The sign of the dot product ---------------------------------------------


@pytest.mark.parametrize("label,a,b,expected", SIGN_CASES)
def test_the_sign_cases(label, a, b, expected):
    value = dot(a, b)
    sign = "positive" if value > 0 else ("zero" if value == 0 else "negative")
    assert sign == expected, label


@pytest.mark.parametrize("label,a,b,expected", SIGN_CASES)
def test_the_sign_of_the_cosine_matches_the_sign_of_the_dot(label, a, b, expected):
    value = dot(a, b)
    cos = cosine_similarity(a, b)
    assert (value > 0) == (cos > 0), label
    assert (value == 0) == (abs(cos) < TOL), label


def test_the_five_angles_are_the_expected_ones():
    expected = [0.0, 45.0, 90.0, 135.0, 180.0]
    measured = [angle_degrees(a, b) for _, a, b, _ in SIGN_CASES]
    assert measured == pytest.approx(expected, abs=1e-9)


def test_perpendicular_vectors_have_a_zero_dot_product():
    assert dot([3, 0], [0, 5]) == 0.0
    assert cosine_similarity([3, 0], [0, 5]) == pytest.approx(0.0, abs=TOL)


def test_three_pairs_in_the_catalogue_are_exactly_orthogonal():
    orthogonal = {
        (first, second)
        for i, first in enumerate(CATALOGUE)
        for second in list(CATALOGUE)[i + 1:]
        if dot(CATALOGUE[first], CATALOGUE[second]) == 0
    }
    assert orthogonal == {
        ("roast-chicken", "storm-bulletin"),
        ("slow-cooker-stew", "storm-bulletin"),
        ("household-budget", "storm-bulletin"),
    }


# -- The length confound -----------------------------------------------------


def test_the_doubled_copy_is_every_count_doubled():
    assert LONG_ROAST_CHICKEN == [2 * n for n in CATALOGUE["roast-chicken"]]


def test_euclidean_distance_to_the_doubled_copy_is_the_articles_own_length():
    short = CATALOGUE["roast-chicken"]
    assert euclidean_distance(short, LONG_ROAST_CHICKEN) == pytest.approx(
        l2_norm(short), abs=1e-9
    )
    assert euclidean_distance(short, LONG_ROAST_CHICKEN) == pytest.approx(
        math.sqrt(82), abs=1e-9
    )


def test_euclidean_calls_the_doubled_copy_further_than_a_different_article():
    short = CATALOGUE["roast-chicken"]
    to_copy = euclidean_distance(short, LONG_ROAST_CHICKEN)
    to_rival = euclidean_distance(short, CATALOGUE["race-day-nutrition"])
    assert to_copy > to_rival
    assert to_copy == pytest.approx(9.055385, abs=1e-6)
    assert to_rival == pytest.approx(8.062258, abs=1e-6)


def test_cosine_calls_the_doubled_copy_identical():
    short = CATALOGUE["roast-chicken"]
    assert cosine_similarity(short, LONG_ROAST_CHICKEN) == pytest.approx(1.0, abs=TOL)
    assert cosine_distance(short, LONG_ROAST_CHICKEN) == pytest.approx(0.0, abs=TOL)


@pytest.mark.parametrize("factor", [0.5, 2, 3, 10, 1000])
def test_scaling_either_vector_by_any_positive_number_leaves_cosine_unchanged(factor):
    a, b = CATALOGUE["roast-chicken"], CATALOGUE["race-day-nutrition"]
    base = cosine_similarity(a, b)
    assert cosine_similarity([factor * x for x in a], b) == pytest.approx(base, abs=TOL)
    assert cosine_similarity(a, [factor * x for x in b]) == pytest.approx(base, abs=TOL)


def test_scaling_by_a_negative_number_flips_the_sign():
    a, b = CATALOGUE["roast-chicken"], CATALOGUE["race-day-nutrition"]
    base = cosine_similarity(a, b)
    flipped = cosine_similarity([-x for x in a], b)
    assert flipped == pytest.approx(-base, abs=TOL)


# -- Cosine similarity against NumPy -----------------------------------------


def numpy_cosine(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def test_cosine_matches_numpy_on_every_catalogue_pair():
    for first, a in CATALOGUE.items():
        for second, b in CATALOGUE.items():
            assert cosine_similarity(a, b) == pytest.approx(
                numpy_cosine(a, b), abs=TOL
            ), (first, second)


def test_cosine_is_the_dot_product_of_the_unit_vectors():
    for first, a in CATALOGUE.items():
        for second, b in CATALOGUE.items():
            assert cosine_similarity(a, b) == pytest.approx(
                dot(normalise(a), normalise(b)), abs=TOL
            ), (first, second)


def test_every_cosine_lands_inside_minus_one_to_one():
    for a in CATALOGUE.values():
        for b in CATALOGUE.values():
            value = cosine_similarity(a, b)
            assert -1.0 <= value <= 1.0


def test_a_vector_compared_with_itself_is_exactly_one_after_clamping():
    for label, vector in CATALOGUE.items():
        assert cosine_similarity(vector, vector) == pytest.approx(1.0, abs=1e-12), label
        assert cosine_similarity(vector, vector) <= 1.0, label


def test_the_unclamped_formula_really_does_miss_one_on_this_catalogue():
    """The clamp is not defensive decoration: three of six articles miss.

    Measured on the authoring machine with Python 3.14.0. The exact set of
    articles that miss could differ on another platform's floating point, so
    the test asserts the shape of the finding — at least one below and at
    least one above — rather than naming them.
    """
    below, above, exact = [], [], []
    for label, vector in CATALOGUE.items():
        length = math.sqrt(sum(x * x for x in vector))
        raw = sum(x * y for x, y in zip(vector, vector)) / (length * length)
        (below if raw < 1.0 else above if raw > 1.0 else exact).append(label)
    assert below, "expected at least one article to round below 1.0"
    assert above, "expected at least one article to round above 1.0"
    assert len(below) + len(above) + len(exact) == len(CATALOGUE)
    for label in above:
        vector = CATALOGUE[label]
        length = math.sqrt(sum(x * x for x in vector))
        raw = sum(x * y for x, y in zip(vector, vector)) / (length * length)
        with pytest.raises(ValueError):
            math.acos(raw)


def test_cosine_refuses_the_zero_vector():
    with pytest.raises(ValueError):
        cosine_similarity([0, 0, 0, 0], CATALOGUE["roast-chicken"])


def test_normalise_refuses_the_zero_vector():
    with pytest.raises(ValueError):
        normalise([0, 0])


def test_the_clamp_keeps_acos_in_its_domain():
    # race-day-nutrition compared with itself gives 1.0000000000000002 through
    # the unguarded formula, which math.acos refuses. Not invented: found by
    # this suite failing while the lab was being written.
    vector = CATALOGUE["race-day-nutrition"]
    length = math.sqrt(sum(x * x for x in vector))
    unclamped = sum(x * y for x, y in zip(vector, vector)) / (length * length)
    assert unclamped > 1.0
    with pytest.raises(ValueError):
        math.acos(unclamped)
    assert cosine_similarity(vector, vector) == 1.0
    assert angle_degrees(vector, vector) == pytest.approx(0.0, abs=1e-9)


def test_normalised_vectors_all_have_length_one():
    for label, unit in normalise_all(CATALOGUE).items():
        assert l2_norm(unit) == pytest.approx(1.0, abs=TOL), label


# -- Cosine distance and the metric conditions -------------------------------


def test_cosine_distance_is_one_minus_similarity():
    for a in CATALOGUE.values():
        for b in CATALOGUE.values():
            assert cosine_distance(a, b) == pytest.approx(
                1.0 - cosine_similarity(a, b), abs=TOL
            )


def test_cosine_distance_runs_from_zero_to_two():
    assert cosine_distance([1, 0], [1, 0]) == pytest.approx(0.0, abs=TOL)
    assert cosine_distance([1, 0], [0, 1]) == pytest.approx(1.0, abs=TOL)
    assert cosine_distance([1, 0], [-1, 0]) == pytest.approx(2.0, abs=TOL)


def test_no_pair_of_count_vectors_exceeds_distance_one():
    for a in CATALOGUE.values():
        for b in CATALOGUE.values():
            assert cosine_distance(a, b) <= 1.0 + TOL


def test_cosine_distance_fails_the_triangle_inequality():
    ab = cosine_distance(TRIANGLE_A, TRIANGLE_B)
    bc = cosine_distance(TRIANGLE_B, TRIANGLE_C)
    ac = cosine_distance(TRIANGLE_A, TRIANGLE_C)
    assert ab == pytest.approx(1 - 1 / math.sqrt(2), abs=1e-9)
    assert bc == pytest.approx(1 - 1 / math.sqrt(2), abs=1e-9)
    assert ac == pytest.approx(1.0, abs=1e-9)
    assert ac > ab + bc  # the failure, asserted


def test_euclidean_distance_holds_the_triangle_inequality_on_the_same_triple():
    for a, b, c in ((TRIANGLE_A, TRIANGLE_B, TRIANGLE_C),):
        assert euclidean_distance(a, c) <= euclidean_distance(a, b) + euclidean_distance(
            b, c
        ) + TOL
        ua, ub, uc = normalise(a), normalise(b), normalise(c)
        assert euclidean_distance(ua, uc) <= euclidean_distance(
            ua, ub
        ) + euclidean_distance(ub, uc) + TOL


def test_cosine_distance_is_zero_for_vectors_that_are_not_equal():
    # It fails the identity condition too, and that failure is the useful part.
    assert cosine_distance(CATALOGUE["roast-chicken"], LONG_ROAST_CHICKEN) == (
        pytest.approx(0.0, abs=TOL)
    )
    assert CATALOGUE["roast-chicken"] != LONG_ROAST_CHICKEN


def test_cosine_distance_is_symmetric():
    for a in CATALOGUE.values():
        for b in CATALOGUE.values():
            assert cosine_distance(a, b) == pytest.approx(cosine_distance(b, a), abs=TOL)


# -- The ranking equivalence on the unit sphere ------------------------------


def test_the_unit_sphere_identity_holds_on_every_pair():
    units = normalise_all(CATALOGUE)
    for first, u in units.items():
        for second, v in units.items():
            predicted = math.sqrt(max(0.0, 2 - 2 * cosine_similarity(u, v)))
            assert euclidean_distance(u, v) == pytest.approx(predicted, abs=1e-9), (
                first,
                second,
            )


@pytest.mark.parametrize("query_label", list(CATALOGUE))
def test_normalised_rankings_are_identical_under_both_measures(query_label):
    units = normalise_all(CATALOGUE)
    query = units[query_label]
    by_cosine = [label for label, _ in rank_by_cosine(query, units)]
    by_euclid = [label for label, _ in rank_by_euclidean(query, units)]
    assert by_cosine == by_euclid


def test_raw_rankings_can_disagree():
    raw = dict(CATALOGUE)
    raw["roast-chicken (2x)"] = LONG_ROAST_CHICKEN
    query = CATALOGUE["roast-chicken"]
    by_cosine = [label for label, _ in rank_by_cosine(query, raw)]
    by_euclid = [label for label, _ in rank_by_euclidean(query, raw)]
    assert by_cosine != by_euclid


def test_distance_on_the_sphere_falls_strictly_as_cosine_rises():
    previous = None
    for cos in (-1.0, -0.5, 0.0, 0.5, 0.9, 1.0):
        distance = math.sqrt(2 - 2 * cos)
        if previous is not None:
            assert distance < previous
        previous = distance


# -- The semantic search -----------------------------------------------------


def test_the_cooking_note_retrieves_roast_chicken():
    ranked = rank_by_cosine(QUERIES["roast it"], CATALOGUE)
    assert ranked[0][0] == "roast-chicken"
    assert ranked[0][1] == pytest.approx(0.993884, abs=1e-6)
    assert ranked[1][0] == "slow-cooker-stew"


def test_the_training_query_retrieves_race_day_nutrition_narrowly():
    ranked = rank_by_cosine(
        QUERIES["training for a race and what to eat"], CATALOGUE
    )
    assert ranked[0][0] == "race-day-nutrition"
    assert ranked[1][0] == "marathon-plan"
    # The margin is genuinely small, and the test says so rather than hiding it.
    assert 0.002 < ranked[0][1] - ranked[1][1] < 0.003


def test_raw_euclidean_gets_the_cooking_note_wrong():
    ranked = rank_by_euclidean(QUERIES["roast it"], CATALOGUE)
    assert ranked[0][0] == "slow-cooker-stew"
    assert ranked[0][0] != "roast-chicken"


def test_the_raw_dot_product_gets_the_training_query_wrong():
    query = QUERIES["training for a race and what to eat"]
    by_dot = sorted(CATALOGUE, key=lambda label: (-dot(query, CATALOGUE[label]), label))
    assert by_dot[0] == "marathon-plan"
    assert dot(query, CATALOGUE["marathon-plan"]) == 45.0
    assert dot(query, CATALOGUE["race-day-nutrition"]) == 38.0


@pytest.mark.parametrize("factor", [1, 3, 100, 1000])
def test_the_querys_own_length_changes_nothing(factor):
    base = QUERIES["roast it"]
    scaled = [factor * x for x in base]
    assert [label for label, _ in rank_by_cosine(scaled, CATALOGUE)] == [
        label for label, _ in rank_by_cosine(base, CATALOGUE)
    ]


def test_the_ranking_is_deterministic_under_ties():
    # Two articles score exactly 0 against the cooking note. The tie must break
    # the same way every run, or the test suite becomes flaky.
    ranked = rank_by_cosine(QUERIES["roast it"], CATALOGUE)
    tail = [label for label, score in ranked if abs(score) < TOL]
    assert tail == ["marathon-plan", "storm-bulletin"]


# -- The curse of dimensionality ---------------------------------------------


def exact_mean_abs_cos(dimension: int) -> float:
    return math.exp(
        math.lgamma(dimension / 2)
        - 0.5 * math.log(math.pi)
        - math.lgamma((dimension + 1) / 2)
    )


def test_the_exact_formula_reproduces_the_two_hand_checkable_cases():
    assert exact_mean_abs_cos(2) == pytest.approx(2 / math.pi, abs=1e-12)
    assert exact_mean_abs_cos(3) == pytest.approx(0.5, abs=1e-12)


@pytest.mark.parametrize("dimension", [2, 8, 128, 2048])
def test_measured_mean_absolute_cosine_matches_the_exact_formula(dimension):
    rng = np.random.default_rng(103)
    a = rng.standard_normal((2000, dimension))
    b = rng.standard_normal((2000, dimension))
    numerator = np.einsum("ij,ij->i", a, b)
    denominator = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
    measured = float(np.mean(np.abs(numerator / denominator)))
    expected = exact_mean_abs_cos(dimension)
    assert abs(measured - expected) / expected < SAMPLING_TOL


def test_mean_absolute_cosine_falls_as_dimension_grows():
    rng = np.random.default_rng(103)
    previous = None
    for dimension in (2, 8, 32, 128, 512, 2048):
        pairs = [
            (rng.standard_normal(dimension), rng.standard_normal(dimension))
            for _ in range(300)
        ]
        value = mean_absolute_cosine(pairs)
        if previous is not None:
            assert value < previous, dimension
        previous = value
    assert previous < 0.05


def test_the_measurement_is_reproducible_with_the_same_seed():
    def run():
        rng = np.random.default_rng(103)
        a = rng.standard_normal((500, 64))
        b = rng.standard_normal((500, 64))
        numerator = np.einsum("ij,ij->i", a, b)
        denominator = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
        return float(np.mean(np.abs(numerator / denominator)))

    assert run() == run()


def test_distances_concentrate_as_dimension_grows():
    rng = np.random.default_rng(104)
    ratios = []
    for dimension in (2, 8192):
        cloud = rng.standard_normal((500, dimension))
        query = rng.standard_normal(dimension)
        distances = np.linalg.norm(cloud - query, axis=1)
        ratios.append(float(distances.max() / distances.min()))
    assert ratios[0] > 5.0
    assert ratios[1] < 1.5
