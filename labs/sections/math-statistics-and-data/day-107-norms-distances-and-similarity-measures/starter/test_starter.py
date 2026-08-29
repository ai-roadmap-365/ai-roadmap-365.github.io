"""Your running score. Run from the LAB DIRECTORY:

    .venv/bin/pytest starter -q

Anything you have not written yet is SKIPPED, not failed. A skip means "not
attempted"; a failure means "attempted and wrong", and the failure prints both
your answer and the real one.

Float comparisons use the tolerance TOL stated in measures.py, except the
predictions in answers.py, which use 1e-9 so you need not type more decimals
than the question asks for. Counts, names and rankings are compared exactly,
because they are exact.
"""

from __future__ import annotations

import itertools
import math

import numpy as np
import pytest

import answers
import catalogue
import measures

TOL = measures.TOL
PREDICTION_TOL = 1e-9

Q = catalogue.QUERY
ARTICLES = catalogue.ARTICLES


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


def close(a, b, tol=PREDICTION_TOL):
    """Elementwise closeness for numbers, vectors and matrices."""
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(close(x, y, tol) for x, y in zip(a, b))
    return abs(a - b) <= tol


def ranked(query, candidates, measure, higher_is_better=False):
    """`rank`, routed through `written` so an unwritten `rank` skips."""
    return written(measures.rank, query, candidates, measure, higher_is_better)


def top(query, candidates, measure, higher_is_better=False):
    return ranked(query, candidates, measure, higher_is_better)[0][0]


# -- 0. Always passes: the data is what the lab says it is --------------------


def test_0_00_the_catalogue_is_intact():
    """One test that passes before you write anything, so a green run means
    the suite itself is working rather than that nothing was collected."""
    assert catalogue.QUERY == (4, 3, 2, 1)
    assert catalogue.ARTICLES["Cartogram"] == tuple(3 * c for c in Q)
    assert len(catalogue.SENSOR_READINGS) == 8
    assert len(catalogue.BEARINGS) == 6
    assert len(catalogue.RECIPES["Sachertorte"]) == 11


# -- 1. The norms -------------------------------------------------------------


def test_1_01_l1_norm():
    assert written(measures.l1_norm, (3.0, -4.0, 12.0)) == 19.0
    assert written(measures.l1_norm, ()) == 0


def test_1_02_l2_norm():
    assert close(written(measures.l2_norm, (3.0, -4.0, 12.0)), 13.0, TOL)
    assert close(written(measures.l2_norm, (0.0, 0.0)), 0.0, TOL)


def test_1_03_linf_norm():
    assert written(measures.linf_norm, (3.0, -4.0, 12.0)) == 12.0
    assert written(measures.linf_norm, ()) == 0.0


def test_1_04_p_norm_reproduces_the_three_named_norms():
    v = (3.0, 4.0)
    assert close(written(measures.p_norm, v, 1), 7.0, TOL)
    assert close(written(measures.p_norm, v, 2), 5.0, TOL)
    assert close(written(measures.p_norm, v, math.inf), 4.0, TOL)


def test_1_05_p_norm_matches_numpy_for_fractional_p():
    v = (3.0, 4.0)
    for p in (1.5, 3, 8):
        mine = written(measures.p_norm, v, p)
        assert close(mine, float(np.linalg.norm(np.asarray(v), ord=p)), TOL)


def test_1_06_p_norm_refuses_p_below_one():
    try:
        measures.p_norm((3.0, 4.0), 0.5)
    except NotImplementedError as exc:
        pytest.skip(f"not written yet: {exc}")
    except ValueError:
        return
    pytest.fail("p_norm(v, 0.5) should raise ValueError: below p = 1 it is "
                "not a norm, because the triangle inequality fails")


def test_1_07_p_norm_is_non_increasing_in_p():
    v = (3.0, 4.0)
    values = [written(measures.p_norm, v, p) for p in (1, 1.5, 2, 3, 8, 64)]
    for earlier, later in zip(values, values[1:]):
        assert later <= earlier + TOL


# -- 2. The distances ---------------------------------------------------------


def test_2_01_l1_distance():
    assert close(written(measures.l1_distance, Q, ARTICLES["Aisle"]), 5.0, TOL)
    assert close(written(measures.l1_distance, Q, ARTICLES["Beacon"]), 6.0, TOL)


def test_2_02_l2_distance():
    assert close(written(measures.l2_distance, (0.0, 0.0), (6.0, 8.0)),
                 10.0, TOL)
    assert close(written(measures.l2_distance, Q, ARTICLES["Beacon"]),
                 math.sqrt(12.0), TOL)


def test_2_03_linf_distance():
    assert close(written(measures.linf_distance, (0.0, 0.0), (6.0, 8.0)),
                 8.0, TOL)
    assert close(written(measures.linf_distance, Q, ARTICLES["Aisle"]),
                 5.0, TOL)


def test_2_04_all_three_match_numpy_on_the_articles():
    for vec in ARTICLES.values():
        d = np.asarray(Q, dtype=float) - np.asarray(vec, dtype=float)
        assert close(written(measures.l1_distance, Q, vec),
                     float(np.linalg.norm(d, ord=1)), TOL)
        assert close(written(measures.l2_distance, Q, vec),
                     float(np.linalg.norm(d, ord=2)), TOL)
        assert close(written(measures.linf_distance, Q, vec),
                     float(np.linalg.norm(d, ord=np.inf)), TOL)


def test_2_05_comparing_different_lengths_raises():
    try:
        measures.l2_distance((1.0, 2.0, 3.0), (1.0, 2.0))
    except NotImplementedError as exc:
        pytest.skip(f"not written yet: {exc}")
    except measures.DimensionMismatch:
        return
    pytest.fail("comparing a length-3 vector with a length-2 vector must "
                "raise DimensionMismatch: use _paired rather than zip")


def test_2_06_the_ordering_linf_le_l2_le_l1_holds():
    for vec in ARTICLES.values():
        a = written(measures.linf_distance, Q, vec)
        b = written(measures.l2_distance, Q, vec)
        c = written(measures.l1_distance, Q, vec)
        assert a <= b + TOL <= c + 2 * TOL


# -- 3. Cosine ---------------------------------------------------------------


def test_3_01_cosine_of_a_scaled_copy_is_one():
    assert close(written(measures.cosine_similarity, Q, ARTICLES["Cartogram"]),
                 1.0, TOL)


def test_3_02_cosine_matches_numpy():
    for vec in ARTICLES.values():
        a = np.asarray(Q, dtype=float)
        b = np.asarray(vec, dtype=float)
        theirs = float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
        assert close(written(measures.cosine_similarity, Q, vec), theirs, TOL)


def test_3_03_cosine_of_orthogonal_vectors_is_zero():
    assert close(written(measures.cosine_similarity, (1.0, 0.0), (0.0, 1.0)),
                 0.0, TOL)


def test_3_04_cosine_refuses_the_zero_vector():
    try:
        measures.cosine_similarity((0.0, 0.0), (1.0, 1.0))
    except NotImplementedError as exc:
        pytest.skip(f"not written yet: {exc}")
    except ValueError:
        return
    pytest.fail("cosine_similarity must raise ValueError for a zero vector: "
                "it has no direction, and returning 0.0 hides the problem")


def test_3_05_cosine_distance_breaks_the_triangle_inequality():
    east, diagonal, north = (catalogue.EAST, catalogue.DIAGONAL,
                             catalogue.NORTH)
    detour = (written(measures.cosine_distance, east, diagonal)
              + written(measures.cosine_distance, diagonal, north))
    direct = written(measures.cosine_distance, east, north)
    assert detour < direct - TOL
    assert close(direct, 1.0, TOL)


# -- 4. Categorical and set data ---------------------------------------------


def test_4_01_hamming_on_the_parts_register():
    ref = catalogue.REFERENCE_RECORD
    got = {n: written(measures.hamming_distance, ref, r)
           for n, r in catalogue.CANDIDATE_RECORDS.items()}
    assert got == {"part-71": 1, "part-72": 3, "part-73": 6}


def test_4_02_hamming_returns_an_int_and_needs_no_arithmetic():
    value = written(measures.hamming_distance, ("red", "blue"),
                    ("green", "blue"))
    assert value == 1
    assert isinstance(value, int)


def test_4_03_hamming_on_the_bit_flags():
    assert written(measures.hamming_distance, catalogue.FLAGS_A,
                   catalogue.FLAGS_B) == 2


def test_4_04_jaccard_basic_cases():
    assert close(written(measures.jaccard_similarity, {1, 2, 3, 4},
                         {1, 2, 3, 4, 5}), 0.8, TOL)
    assert close(written(measures.jaccard_similarity, {1, 2}, {3, 4}),
                 0.0, TOL)
    assert close(written(measures.jaccard_similarity, set(), set()), 1.0, TOL)


def test_4_05_jaccard_on_the_recipes():
    q = catalogue.RECIPE_QUERY
    assert close(written(measures.jaccard_similarity, q,
                         catalogue.RECIPES["Sachertorte"]), 4 / 11, TOL)
    assert close(written(measures.jaccard_similarity, q,
                         catalogue.RECIPES["Shortbread"]), 2 / 5, TOL)


def test_4_06_to_binary_vector():
    assert written(measures.to_binary_vector, {"a", "c"},
                   ["a", "b", "c"]) == [1.0, 0.0, 1.0]


def test_4_07_jaccard_and_cosine_disagree_on_the_recipes():
    q = catalogue.RECIPE_QUERY
    axes = measures.vocabulary(q, *catalogue.RECIPES.values())
    qv = written(measures.to_binary_vector, q, axes)
    jac = {n: written(measures.jaccard_similarity, q, s)
           for n, s in catalogue.RECIPES.items()}
    cos = {n: written(measures.cosine_similarity, qv,
                      written(measures.to_binary_vector, s, axes))
           for n, s in catalogue.RECIPES.items()}
    assert max(jac, key=jac.get) == "Shortbread"
    assert max(cos, key=cos.get) == "Sachertorte"


def test_4_08_jaccard_distance_satisfies_the_triangle_inequality():
    universe = ("a", "b", "c")
    subsets = [frozenset(c) for r in range(len(universe) + 1)
               for c in itertools.combinations(universe, r)]
    for a, b, c in itertools.product(subsets, repeat=3):
        assert (written(measures.jaccard_distance, a, b)
                + written(measures.jaccard_distance, b, c)
                >= written(measures.jaccard_distance, a, c) - TOL)


# -- 5. Statistics and scaling -----------------------------------------------


def test_5_01_column_means():
    assert close(written(measures.column_means,
                         [(1.0, 10.0), (3.0, 20.0)]), [2.0, 15.0], TOL)


def test_5_02_column_stds_use_the_population_divisor():
    rows = list(catalogue.BEARINGS.values())
    mine = written(measures.column_stds, rows)
    theirs = np.asarray(rows, dtype=float).std(axis=0)
    assert close(list(mine), list(theirs), TOL)


def test_5_03_column_stds_are_not_the_sample_divisor():
    rows = list(catalogue.BEARINGS.values())
    mine = written(measures.column_stds, rows)
    sample = np.asarray(rows, dtype=float).std(axis=0, ddof=1)
    assert not close(list(mine), list(sample), 1e-6)


def test_5_04_standardise_gives_mean_zero_and_sd_one():
    rows = list(catalogue.BEARINGS.values())
    z = written(measures.standardise, rows)
    assert close(written(measures.column_means, z), [0.0, 0.0], 1e-12)
    assert close(written(measures.column_stds, z), [1.0, 1.0], 1e-12)


def test_5_05_standardise_uses_supplied_means_and_stds():
    rows = [(1.0,), (3.0,)]
    z = written(measures.standardise, rows, [0.0], [1.0])
    assert close(z, [[1.0], [3.0]], TOL)


def test_5_06_standardise_leaves_a_constant_column_at_zero():
    z = written(measures.standardise, [(1.0, 5.0), (2.0, 5.0), (3.0, 5.0)])
    assert [row[1] for row in z] == [0.0, 0.0, 0.0]


def test_5_07_standardising_changes_the_bearing_winner():
    rows = list(catalogue.BEARINGS.values())
    means = written(measures.column_means, rows)
    stds = written(measures.column_stds, rows)
    raw = top(catalogue.BEARING_QUERY, catalogue.BEARINGS,
              measures.l2_distance)
    q = written(measures.standardise, [catalogue.BEARING_QUERY],
                means, stds)[0]
    scaled = {n: written(measures.standardise, [v], means, stds)[0]
              for n, v in catalogue.BEARINGS.items()}
    assert raw == "R"
    assert top(q, scaled, measures.l2_distance) == "P"


# -- 6. Covariance and Mahalanobis -------------------------------------------


def test_6_01_covariance_of_the_sensor_readings():
    cov = written(measures.covariance_matrix, catalogue.SENSOR_READINGS)
    assert close(cov, [[7.5, 7.0], [7.0, 7.5]], TOL)


def test_6_02_covariance_matches_numpy_with_bias_true():
    mine = written(measures.covariance_matrix, catalogue.SENSOR_READINGS)
    theirs = np.cov(np.asarray(catalogue.SENSOR_READINGS, dtype=float),
                    rowvar=False, bias=True)
    assert close(mine, theirs.tolist(), TOL)


def test_6_03_mahalanobis_with_the_identity_is_euclidean():
    identity = [[1.0, 0.0], [0.0, 1.0]]
    for probe in ((3.0, 3.0), (3.0, -3.0), (-2.5, 4.75)):
        assert close(
            written(measures.mahalanobis_distance, probe, (0.0, 0.0),
                    identity),
            written(measures.l2_distance, probe, (0.0, 0.0)), TOL)


def test_6_04_mahalanobis_separates_the_two_probes():
    mean = written(measures.column_means, catalogue.SENSOR_READINGS)
    cov = written(measures.covariance_matrix, catalogue.SENSOR_READINGS)
    inv = measures.inverse(cov)
    along = written(measures.mahalanobis_distance, catalogue.PROBE_ALONG,
                    mean, inv)
    across = written(measures.mahalanobis_distance, catalogue.PROBE_ACROSS,
                     mean, inv)
    assert close(across, 6.0, TOL)
    assert close(along, math.sqrt(9.0 / 7.25), TOL)


def test_6_05_euclidean_cannot_separate_them():
    mean = written(measures.column_means, catalogue.SENSOR_READINGS)
    assert close(written(measures.l2_distance, catalogue.PROBE_ALONG, mean),
                 written(measures.l2_distance, catalogue.PROBE_ACROSS, mean),
                 TOL)


def test_6_06_mahalanobis_clamps_a_tiny_negative_rather_than_raising():
    inv = measures.inverse(written(measures.covariance_matrix,
                                   catalogue.SENSOR_READINGS))
    assert close(written(measures.mahalanobis_distance, (1.0, 1.0),
                         (1.0, 1.0), inv), 0.0, TOL)


# -- 7. The ranking function -------------------------------------------------


def test_7_01_rank_returns_name_score_pairs_for_every_candidate():
    order = ranked(Q, ARTICLES, measures.l1_distance)
    assert sorted(n for n, _ in order) == sorted(ARTICLES)
    assert all(isinstance(score, float) for _, score in order)


def test_7_02_rank_ascends_for_a_distance():
    scores = [s for _, s in ranked(Q, ARTICLES, measures.l2_distance)]
    assert scores == sorted(scores)


def test_7_03_rank_descends_for_a_similarity():
    scores = [s for _, s in ranked(Q, ARTICLES, measures.cosine_similarity,
                                   higher_is_better=True)]
    assert scores == sorted(scores, reverse=True)


def test_7_04_ties_break_by_name():
    candidates = {"zulu": (1.0, 1.0), "alpha": (1.0, 1.0), "mike": (1.0, 1.0)}
    order = [n for n, _ in ranked((0.0, 0.0), candidates,
                                  measures.l2_distance)]
    assert order == ["alpha", "mike", "zulu"]


def test_7_05_three_measures_name_three_different_winners():
    picks = {
        "l1": top(Q, ARTICLES, measures.l1_distance),
        "l2": top(Q, ARTICLES, measures.l2_distance),
        "cos": top(Q, ARTICLES, measures.cosine_similarity, True),
    }
    assert picks == {"l1": "Aisle", "l2": "Beacon", "cos": "Cartogram"}


def test_7_06_the_warehouse_displacement():
    a, b = catalogue.FLOOR_FROM, catalogue.FLOOR_TO
    assert close(written(measures.l1_distance, a, b), 14.0, TOL)
    assert close(written(measures.l2_distance, a, b), 10.0, TOL)
    assert close(written(measures.linf_distance, a, b), 8.0, TOL)


def test_7_07_chebyshev_accepts_the_part_the_others_would_reject():
    nominal = catalogue.NOMINAL_PART
    limit = catalogue.PART_TOLERANCE_MM
    a = catalogue.MEASURED_PARTS["batch-A"]
    b = catalogue.MEASURED_PARTS["batch-B"]
    assert written(measures.linf_distance, a, nominal) <= limit + TOL
    assert written(measures.linf_distance, b, nominal) > limit
    assert (written(measures.l1_distance, b, nominal)
            < written(measures.l1_distance, a, nominal))


# -- 8. Your predictions ------------------------------------------------------


def test_8_01_l1_query_to_aisle():
    assert close(predicted("L1_QUERY_TO_AISLE"), 5.0)


def test_8_02_l1_query_to_beacon():
    assert close(predicted("L1_QUERY_TO_BEACON"), 6.0)


def test_8_03_l2_query_to_aisle():
    assert close(predicted("L2_QUERY_TO_AISLE"), 5.0)


def test_8_04_linf_query_to_beacon():
    assert close(predicted("LINF_QUERY_TO_BEACON"), 2.0)


def test_8_05_cosine_query_to_cartogram():
    assert close(predicted("COSINE_QUERY_TO_CARTOGRAM"), 1.0, 5e-5)


def test_8_06_l1_winner():
    assert predicted("L1_WINNER") == "Aisle"


def test_8_07_l2_winner():
    assert predicted("L2_WINNER") == "Beacon"


def test_8_08_cosine_winner():
    assert predicted("COSINE_WINNER") == "Cartogram"


def test_8_09_p_norm_at_1():
    assert close(predicted("P_NORM_3_4_AT_1"), 7.0)


def test_8_10_p_norm_at_2():
    assert close(predicted("P_NORM_3_4_AT_2"), 5.0)


def test_8_11_p_norm_at_infinity():
    assert close(predicted("P_NORM_3_4_AT_INF"), 4.0)


def test_8_12_p_norm_falls_as_p_rises():
    assert predicted("P_NORM_AS_P_RISES") == "fall"


def test_8_13_squared_euclidean_breaks_absolute_homogeneity():
    assert predicted("AXIOM_SQUARED_EUCLIDEAN_BREAKS") == "absolute homogeneity"


def test_8_14_cosine_distance_east_north():
    assert close(predicted("COSINE_DISTANCE_EAST_NORTH"), 1.0)


def test_8_15_cosine_triangle_does_not_hold():
    assert predicted("COSINE_TRIANGLE_HOLDS") is False


def test_8_16_jaccard_distance_is_a_metric():
    assert predicted("JACCARD_DISTANCE_IS_A_METRIC") is True


def test_8_17_hamming_reference_to_part_73():
    assert close(predicted("HAMMING_REFERENCE_TO_PART_73"), 6)


def test_8_18_hamming_flags():
    assert close(predicted("HAMMING_FLAGS"), 2)


def test_8_19_jaccard_recipe_winner():
    assert predicted("JACCARD_RECIPE_WINNER") == "Shortbread"


def test_8_20_cosine_recipe_winner():
    assert predicted("COSINE_RECIPE_WINNER") == "Sachertorte"


def test_8_21_covariance_of_readings():
    assert close(predicted("COVARIANCE_OF_READINGS"),
                 [[7.5, 7.0], [7.0, 7.5]])


def test_8_22_probes_are_equidistant_under_euclidean():
    assert predicted("PROBES_EQUIDISTANT_UNDER_EUCLIDEAN") is True


def test_8_23_mahalanobis_to_probe_across():
    assert close(predicted("MAHALANOBIS_TO_PROBE_ACROSS"), 6.0)


def test_8_24_raw_bearing_winner():
    assert predicted("RAW_BEARING_WINNER") == "R"


def test_8_25_standardised_bearing_winner():
    assert predicted("STANDARDISED_BEARING_WINNER") == "P"
