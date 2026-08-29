"""Tests over the reference implementation. Run from the LAB DIRECTORY:

    .venv/bin/pytest examples -q

Every float comparison states a tolerance. `measures.TOL` is 1e-12 and is used
unless a test says otherwise and says why. Integer results -- Hamming counts,
rankings, set sizes -- are compared exactly, because they are exact.

NumPy appears here as the independent answer, never as the implementation:
`measures.py` computes with `abs`, `**`, `sum` and `math.sqrt` only.
"""

from __future__ import annotations

import itertools
import math

import numpy as np
import pytest

import catalogue
import measures
from measures import TOL

Q = catalogue.QUERY
ARTICLES = catalogue.ARTICLES


# -- 1. Norms -----------------------------------------------------------------


def test_1_01_l1_norm_is_the_sum_of_absolute_values():
    assert measures.l1_norm((3.0, -4.0, 12.0)) == 19.0


def test_1_02_l2_norm_of_3_4_12_is_exactly_13():
    # 9 + 16 + 144 = 169, a perfect square, so this is exact and `==` is safe.
    assert measures.l2_norm((3.0, -4.0, 12.0)) == 13.0


def test_1_03_linf_norm_is_the_largest_absolute_component():
    assert measures.linf_norm((3.0, -4.0, 12.0)) == 12.0


def test_1_04_p_norm_reproduces_l1_l2_and_linf():
    v = (3.0, 4.0)
    assert measures.p_norm(v, 1) == measures.l1_norm(v) == 7.0
    assert measures.p_norm(v, 2) == measures.l2_norm(v) == 5.0
    assert measures.p_norm(v, math.inf) == measures.linf_norm(v) == 4.0


def test_1_05_p_norm_is_non_increasing_in_p():
    v = (3.0, 4.0)
    values = [measures.p_norm(v, p) for p in (1, 1.5, 2, 3, 4, 8, 16, 64)]
    for earlier, later in zip(values, values[1:]):
        assert later <= earlier + TOL


def test_1_06_p_norm_never_falls_below_the_largest_component():
    v = (3.0, 4.0)
    floor = measures.linf_norm(v)
    for p in (1, 1.5, 2, 3, 10, 100, math.inf):
        assert measures.p_norm(v, p) >= floor - TOL


def test_1_07_p_norm_refuses_p_below_one_because_it_is_not_a_norm():
    with pytest.raises(ValueError):
        measures.p_norm((3.0, 4.0), 0.5)


def test_1_08_every_norm_of_the_zero_vector_is_zero():
    zero = (0.0, 0.0, 0.0)
    assert measures.l1_norm(zero) == 0.0
    assert measures.l2_norm(zero) == 0.0
    assert measures.linf_norm(zero) == 0.0
    assert measures.p_norm(zero, 3) == 0.0


@pytest.mark.parametrize("norm", [measures.l1_norm, measures.l2_norm,
                                  measures.linf_norm])
def test_1_09_absolute_homogeneity(norm):
    v = catalogue.AXIOM_VECTOR
    k = catalogue.AXIOM_SCALAR
    assert abs(norm([k * x for x in v]) - abs(k) * norm(v)) <= TOL


@pytest.mark.parametrize("norm", [measures.l1_norm, measures.l2_norm,
                                  measures.linf_norm])
def test_1_10_triangle_inequality_for_norms(norm):
    v = catalogue.AXIOM_VECTOR
    w = catalogue.TRIANGLE_TRIPLE[1]
    assert norm([a + b for a, b in zip(v, w)]) <= norm(v) + norm(w) + TOL


def test_1_11_squared_euclidean_fails_absolute_homogeneity():
    """The reason 'squared distance' is not a distance, measured."""
    v = catalogue.AXIOM_VECTOR
    squared = sum(x * x for x in v)
    doubled = sum((2 * x) ** 2 for x in v)
    assert abs(doubled - 4 * squared) <= TOL
    assert abs(doubled - 2 * squared) > 1.0


def test_1_12_squared_euclidean_still_ranks_identically_to_l2():
    by_l2 = measures.rank(Q, ARTICLES, measures.l2_distance)
    by_sq = measures.rank(
        Q, ARTICLES, lambda a, b: sum((x - y) ** 2 for x, y in zip(a, b)))
    assert [n for n, _ in by_l2] == [n for n, _ in by_sq]


# -- 2. Agreement with NumPy --------------------------------------------------


@pytest.mark.parametrize("p", [1, 1.5, 2, 3, 8, math.inf])
def test_2_01_p_norm_matches_numpy_linalg_norm_ord(p):
    for v in ((3.0, 4.0), catalogue.AXIOM_VECTOR, (0.5, -0.25, 7.0, -3.5)):
        mine = measures.p_norm(v, p)
        theirs = float(np.linalg.norm(np.asarray(v), ord=p))
        assert abs(mine - theirs) <= TOL


@pytest.mark.parametrize("p, ord_", [(1, 1), (2, 2), (math.inf, np.inf)])
def test_2_02_distances_match_numpy_on_the_articles(p, ord_):
    for vec in ARTICLES.values():
        mine = measures.minkowski_distance(Q, vec, p)
        d = np.asarray(Q, dtype=float) - np.asarray(vec, dtype=float)
        assert abs(mine - float(np.linalg.norm(d, ord=ord_))) <= TOL


def test_2_03_l2_distance_matches_math_dist():
    for vec in ARTICLES.values():
        assert abs(measures.l2_distance(Q, vec)
                   - math.dist(Q, vec)) <= TOL


def test_2_04_cosine_similarity_matches_a_numpy_computation():
    for vec in ARTICLES.values():
        a = np.asarray(Q, dtype=float)
        b = np.asarray(vec, dtype=float)
        theirs = float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
        assert abs(measures.cosine_similarity(Q, vec) - theirs) <= TOL


# -- 3. The opening disagreement ----------------------------------------------


def test_3_01_cartogram_is_exactly_three_times_the_query():
    assert ARTICLES["Cartogram"] == tuple(3 * c for c in Q)


def test_3_02_l1_picks_aisle():
    assert measures.winner(Q, ARTICLES, measures.l1_distance) == "Aisle"


def test_3_03_l2_picks_beacon():
    assert measures.winner(Q, ARTICLES, measures.l2_distance) == "Beacon"


def test_3_04_linf_also_picks_beacon_for_a_different_reason():
    assert measures.winner(Q, ARTICLES, measures.linf_distance) == "Beacon"
    assert measures.linf_distance(Q, ARTICLES["Aisle"]) == 5.0
    assert measures.linf_distance(Q, ARTICLES["Beacon"]) == 2.0


def test_3_05_cosine_picks_cartogram():
    assert measures.winner(Q, ARTICLES, measures.cosine_similarity,
                           higher_is_better=True) == "Cartogram"


def test_3_06_three_measures_name_three_different_winners():
    picks = {
        measures.winner(Q, ARTICLES, measures.l1_distance),
        measures.winner(Q, ARTICLES, measures.l2_distance),
        measures.winner(Q, ARTICLES, measures.cosine_similarity,
                        higher_is_better=True),
    }
    assert len(picks) == 3


def test_3_07_the_exact_distances():
    assert measures.l1_distance(Q, ARTICLES["Aisle"]) == 5.0
    assert measures.l1_distance(Q, ARTICLES["Beacon"]) == 6.0
    assert measures.l1_distance(Q, ARTICLES["Cartogram"]) == 20.0
    assert measures.l2_distance(Q, ARTICLES["Aisle"]) == 5.0
    assert abs(measures.l2_distance(Q, ARTICLES["Beacon"])
               - math.sqrt(12.0)) <= TOL


def test_3_08_cosine_of_cartogram_is_exactly_one_to_tolerance():
    assert abs(measures.cosine_similarity(Q, ARTICLES["Cartogram"])
               - 1.0) <= TOL


def test_3_09_cartogram_is_the_worst_answer_under_both_l1_and_l2():
    for measure in (measures.l1_distance, measures.l2_distance):
        order = measures.rank(Q, ARTICLES, measure)
        assert order[-1][0] == "Cartogram"


def test_3_10_higher_is_better_actually_reverses_the_order():
    ascending = measures.rank(Q, ARTICLES, measures.cosine_similarity)
    descending = measures.rank(Q, ARTICLES, measures.cosine_similarity,
                               higher_is_better=True)
    assert [n for n, _ in ascending] == [n for n, _ in descending][::-1]


# -- 4. Metrics and non-metrics -----------------------------------------------


@pytest.mark.parametrize("d", [measures.l1_distance, measures.l2_distance,
                               measures.linf_distance])
def test_4_01_symmetry(d):
    x, y, _ = catalogue.TRIANGLE_TRIPLE
    assert abs(d(x, y) - d(y, x)) <= TOL


@pytest.mark.parametrize("d", [measures.l1_distance, measures.l2_distance,
                               measures.linf_distance])
def test_4_02_zero_only_when_identical(d):
    x, y, _ = catalogue.TRIANGLE_TRIPLE
    assert d(x, x) == 0.0
    assert d(x, y) > 0.0


@pytest.mark.parametrize("d", [measures.l1_distance, measures.l2_distance,
                               measures.linf_distance])
def test_4_03_triangle_inequality_in_all_six_orderings(d):
    for a, b, c in itertools.permutations(catalogue.TRIANGLE_TRIPLE):
        assert d(a, b) + d(b, c) >= d(a, c) - TOL


def test_4_04_cosine_distance_violates_the_triangle_inequality():
    east, diagonal, north = (catalogue.EAST, catalogue.DIAGONAL,
                             catalogue.NORTH)
    detour = (measures.cosine_distance(east, diagonal)
              + measures.cosine_distance(diagonal, north))
    direct = measures.cosine_distance(east, north)
    assert detour < direct - TOL
    assert abs(direct - 1.0) <= TOL
    assert abs(detour - (2.0 - math.sqrt(2.0))) <= TOL


def test_4_05_cosine_distance_is_zero_between_different_vectors():
    assert abs(measures.cosine_distance((1.0, 0.0), (2.0, 0.0))) <= TOL


def test_4_06_angular_distance_repairs_the_triangle_inequality():
    def angular(u, v):
        c = max(-1.0, min(1.0, measures.cosine_similarity(u, v)))
        return math.acos(c) / math.pi

    east, diagonal, north = (catalogue.EAST, catalogue.DIAGONAL,
                             catalogue.NORTH)
    assert (angular(east, diagonal) + angular(diagonal, north)
            >= angular(east, north) - TOL)


def test_4_07_jaccard_distance_is_a_metric_on_every_triple():
    universe = ("a", "b", "c", "d")
    subsets = [frozenset(c) for r in range(len(universe) + 1)
               for c in itertools.combinations(universe, r)]
    assert len(subsets) == 16
    for a, b, c in itertools.product(subsets, repeat=3):
        assert (measures.jaccard_distance(a, b)
                + measures.jaccard_distance(b, c)
                >= measures.jaccard_distance(a, c) - TOL)


def test_4_08_hamming_distance_is_a_metric_on_every_triple():
    strings = list(itertools.product((0, 1), repeat=4))
    for a, b, c in itertools.product(strings, repeat=3):
        assert (measures.hamming_distance(a, b)
                + measures.hamming_distance(b, c)
                >= measures.hamming_distance(a, c))


def test_4_09_cosine_distance_fails_on_many_binary_triples():
    vectors = [v for v in itertools.product((0, 1), repeat=4) if any(v)]
    violations = sum(
        1 for a, b, c in itertools.product(vectors, repeat=3)
        if (measures.cosine_distance(a, b) + measures.cosine_distance(b, c)
            < measures.cosine_distance(a, c) - TOL))
    assert violations > 0
    assert violations == 326  # measured, and asserted so a change is noticed


def test_4_10_normalised_vectors_make_cosine_and_l2_agree():
    for u, v in itertools.combinations(
            (catalogue.EAST, catalogue.DIAGONAL, catalogue.NORTH), 2):
        un = [c / measures.l2_norm(u) for c in u]
        vn = [c / measures.l2_norm(v) for c in v]
        lhs = measures.l2_distance(un, vn) ** 2
        rhs = 2.0 - 2.0 * measures.cosine_similarity(un, vn)
        assert abs(lhs - rhs) <= 1e-9


def test_4_11_cosine_similarity_refuses_the_zero_vector():
    with pytest.raises(ValueError):
        measures.cosine_similarity((0.0, 0.0), (1.0, 1.0))


# -- 5. Manhattan, Chebyshev and the shape of the question --------------------


def test_5_01_the_warehouse_displacement_gives_14_10_and_8():
    a, b = catalogue.FLOOR_FROM, catalogue.FLOOR_TO
    assert measures.l1_distance(a, b) == 14.0
    assert measures.l2_distance(a, b) == 10.0
    assert measures.linf_distance(a, b) == 8.0


def test_5_02_linf_never_exceeds_l2_never_exceeds_l1():
    rng = np.random.default_rng(107)
    for _ in range(500):
        u = rng.normal(size=5)
        v = rng.normal(size=5)
        assert (measures.linf_distance(u, v)
                <= measures.l2_distance(u, v) + TOL
                <= measures.l1_distance(u, v) + 2 * TOL)


def test_5_03_chebyshev_accepts_the_part_l1_and_l2_would_reject():
    nominal = catalogue.NOMINAL_PART
    tol_mm = catalogue.PART_TOLERANCE_MM
    a = catalogue.MEASURED_PARTS["batch-A"]
    b = catalogue.MEASURED_PARTS["batch-B"]
    assert measures.linf_distance(a, nominal) <= tol_mm + TOL
    assert measures.linf_distance(b, nominal) > tol_mm
    # ... while both L1 and L2 rank batch-B as the better part.
    assert measures.l1_distance(b, nominal) < measures.l1_distance(a, nominal)
    assert measures.l2_distance(b, nominal) > measures.l2_distance(a, nominal)


def test_5_04_l1_and_l2_disagree_about_the_two_batches():
    """The pair that shows L1 and L2 are genuinely different questions."""
    nominal = catalogue.NOMINAL_PART
    a = catalogue.MEASURED_PARTS["batch-A"]
    b = catalogue.MEASURED_PARTS["batch-B"]
    assert measures.l1_distance(a, nominal) > measures.l1_distance(b, nominal)
    assert measures.l2_distance(a, nominal) < measures.l2_distance(b, nominal)


# -- 6. Categorical and set data ----------------------------------------------


def test_6_01_hamming_counts_the_fields_that_differ():
    ref = catalogue.REFERENCE_RECORD
    got = {n: measures.hamming_distance(ref, r)
           for n, r in catalogue.CANDIDATE_RECORDS.items()}
    assert got == {"part-71": 1, "part-72": 3, "part-73": 6}


def test_6_02_normalised_hamming_is_a_fraction_of_the_fields():
    ref = catalogue.REFERENCE_RECORD
    assert measures.normalised_hamming(
        ref, catalogue.CANDIDATE_RECORDS["part-73"]) == 1.0
    assert abs(measures.normalised_hamming(
        ref, catalogue.CANDIDATE_RECORDS["part-71"]) - 1 / 6) <= TOL


def test_6_03_hamming_needs_no_arithmetic_on_the_values():
    assert measures.hamming_distance(("red", "blue"), ("green", "blue")) == 1
    assert measures.hamming_distance((None, 3, "x"), (None, 4, "x")) == 1


def test_6_04_hamming_refuses_different_lengths():
    with pytest.raises(measures.DimensionMismatch):
        measures.hamming_distance((1, 2, 3), (1, 2))


def test_6_05_on_bits_hamming_equals_l1_and_squared_l2():
    a, b = catalogue.FLAGS_A, catalogue.FLAGS_B
    h = measures.hamming_distance(a, b)
    assert h == 2
    assert abs(measures.l1_distance(a, b) - h) <= TOL
    assert abs(measures.l2_distance(a, b) ** 2 - h) <= 1e-9


def test_6_06_jaccard_and_cosine_rank_the_recipes_differently():
    q = catalogue.RECIPE_QUERY
    axes = measures.vocabulary(q, *catalogue.RECIPES.values())
    qv = measures.to_binary_vector(q, axes)
    jac = {n: measures.jaccard_similarity(q, s)
           for n, s in catalogue.RECIPES.items()}
    cos = {n: measures.cosine_similarity(qv, measures.to_binary_vector(s, axes))
           for n, s in catalogue.RECIPES.items()}
    assert max(jac, key=jac.get) == "Shortbread"
    assert max(cos, key=cos.get) == "Sachertorte"


def test_6_07_the_exact_jaccard_and_cosine_values():
    q = catalogue.RECIPE_QUERY
    axes = measures.vocabulary(q, *catalogue.RECIPES.values())
    qv = measures.to_binary_vector(q, axes)
    sach = catalogue.RECIPES["Sachertorte"]
    short = catalogue.RECIPES["Shortbread"]
    assert abs(measures.jaccard_similarity(q, sach) - 4 / 11) <= TOL
    assert abs(measures.jaccard_similarity(q, short) - 2 / 5) <= TOL
    assert abs(measures.cosine_similarity(
        qv, measures.to_binary_vector(sach, axes)) - 4 / math.sqrt(44)) <= TOL
    assert abs(measures.cosine_similarity(
        qv, measures.to_binary_vector(short, axes)) - 2 / math.sqrt(12)) <= TOL


def test_6_08_cosine_on_binary_data_is_never_below_jaccard():
    universe = tuple("abcdef")
    subsets = [frozenset(c) for r in range(1, len(universe) + 1)
               for c in itertools.combinations(universe, r)]
    axes = list(universe)
    for a, b in itertools.combinations(subsets, 2):
        jac = measures.jaccard_similarity(a, b)
        cos = measures.cosine_similarity(measures.to_binary_vector(a, axes),
                                         measures.to_binary_vector(b, axes))
        assert cos >= jac - TOL


def test_6_09_jaccard_of_two_empty_sets_is_the_documented_convention():
    assert measures.jaccard_similarity(set(), set()) == 1.0
    assert measures.jaccard_distance(set(), set()) == 0.0


def test_6_10_jaccard_of_disjoint_sets_is_zero():
    assert measures.jaccard_similarity({1, 2}, {3, 4}) == 0.0


def test_6_11_vocabulary_is_sorted_so_the_axes_are_stable():
    axes = measures.vocabulary({"pear", "apple"}, {"fig"})
    assert axes == ["apple", "fig", "pear"]


def test_6_12_to_binary_vector_marks_exactly_the_members():
    axes = ["a", "b", "c"]
    assert measures.to_binary_vector({"a", "c"}, axes) == [1.0, 0.0, 1.0]


# -- 7. Matrices, covariance and Mahalanobis ---------------------------------


def test_7_01_covariance_of_the_readings_is_exactly_7_5_and_7():
    assert measures.covariance_matrix(catalogue.SENSOR_READINGS) == [
        [7.5, 7.0], [7.0, 7.5]]


def test_7_02_covariance_matches_numpy_with_bias_true():
    mine = np.asarray(measures.covariance_matrix(catalogue.SENSOR_READINGS))
    theirs = np.cov(np.asarray(catalogue.SENSOR_READINGS, dtype=float),
                    rowvar=False, bias=True)
    assert np.allclose(mine, theirs, atol=TOL)


def test_7_03_inverse_matches_numpy_linalg_inv():
    for m in ([[7.5, 7.0], [7.0, 7.5]],
              [[2.0, 0.0, 1.0], [1.0, 3.0, 2.0], [1.0, 0.0, 4.0]],
              [[1.0, 0.0], [0.0, 1.0]]):
        mine = np.asarray(measures.inverse(m))
        assert np.allclose(mine, np.linalg.inv(np.asarray(m)), atol=1e-10)


def test_7_04_inverse_times_original_is_the_identity():
    m = [[7.5, 7.0], [7.0, 7.5]]
    product = measures.matmul(m, measures.inverse(m))
    for i, row in enumerate(product):
        for j, value in enumerate(row):
            assert abs(value - (1.0 if i == j else 0.0)) <= TOL


def test_7_05_a_singular_matrix_refuses_to_invert():
    with pytest.raises(ValueError):
        measures.inverse([[1.0, 2.0], [2.0, 4.0]])


def test_7_06_the_two_probes_are_the_same_euclidean_distance_from_the_mean():
    mean = measures.column_means(catalogue.SENSOR_READINGS)
    a = measures.l2_distance(catalogue.PROBE_ALONG, mean)
    b = measures.l2_distance(catalogue.PROBE_ACROSS, mean)
    assert abs(a - b) <= TOL
    assert abs(a - math.sqrt(18.0)) <= TOL


def test_7_07_mahalanobis_tells_them_apart():
    mean = measures.column_means(catalogue.SENSOR_READINGS)
    inv = measures.inverse(measures.covariance_matrix(
        catalogue.SENSOR_READINGS))
    along = measures.mahalanobis_distance(catalogue.PROBE_ALONG, mean, inv)
    across = measures.mahalanobis_distance(catalogue.PROBE_ACROSS, mean, inv)
    assert abs(across - 6.0) <= TOL
    assert abs(along - math.sqrt(9.0 / 7.25)) <= TOL
    assert across / along > 5.0


def test_7_08_the_same_two_probes_through_numpy_agree_within_tolerance():
    """Two correct inverses disagree in the last bit. The tolerance earns
    its keep here: `== 6.0` passes for one route and fails for the other."""
    data = np.asarray(catalogue.SENSOR_READINGS, dtype=float)
    inv_np = np.linalg.inv(np.cov(data, rowvar=False, bias=True))
    z = np.asarray(catalogue.PROBE_ACROSS)
    theirs = float(math.sqrt(z @ inv_np @ z))
    mine = measures.mahalanobis_distance(
        catalogue.PROBE_ACROSS,
        measures.column_means(catalogue.SENSOR_READINGS),
        measures.inverse(measures.covariance_matrix(
            catalogue.SENSOR_READINGS)))
    assert abs(mine - theirs) <= TOL
    assert abs(theirs - 6.0) <= TOL


def test_7_09_mahalanobis_with_the_identity_is_euclidean():
    identity = [[1.0, 0.0], [0.0, 1.0]]
    for probe in ((3.0, 3.0), (3.0, -3.0), (-2.5, 4.75), (0.0, 0.0)):
        assert abs(measures.mahalanobis_distance(probe, (0.0, 0.0), identity)
                   - measures.l2_distance(probe, (0.0, 0.0))) <= TOL


def test_7_10_mahalanobis_agrees_with_the_eigen_decomposition():
    """Day 106's eigenvectors are the axes Mahalanobis measures along."""
    cov = measures.covariance_matrix(catalogue.SENSOR_READINGS)
    values, vectors = np.linalg.eigh(np.asarray(cov))
    inv = measures.inverse(cov)
    for probe in (catalogue.PROBE_ALONG, catalogue.PROBE_ACROSS,
                  (1.0, -4.0), (2.5, 0.25)):
        z = np.asarray(probe)
        by_hand = math.sqrt(sum(
            float(z @ vector) ** 2 / value
            for value, vector in zip(values, vectors.T)))
        assert abs(by_hand - measures.mahalanobis_distance(
            probe, (0.0, 0.0), inv)) <= 1e-9


def test_7_11_the_eigenvalues_are_half_and_fourteen_and_a_half():
    values = sorted(np.linalg.eigvalsh(
        np.asarray(measures.covariance_matrix(catalogue.SENSOR_READINGS))))
    assert abs(values[0] - 0.5) <= 1e-12
    assert abs(values[1] - 14.5) <= 1e-12


def test_7_12_mahalanobis_is_symmetric():
    inv = measures.inverse(measures.covariance_matrix(
        catalogue.SENSOR_READINGS))
    a, b = catalogue.PROBE_ALONG, catalogue.PROBE_ACROSS
    assert abs(measures.mahalanobis_distance(a, b, inv)
               - measures.mahalanobis_distance(b, a, inv)) <= TOL


# -- 8. Standardising ---------------------------------------------------------


def test_8_01_standardised_columns_have_mean_zero_and_sd_one():
    rows = list(catalogue.BEARINGS.values())
    z = measures.standardise(rows)
    for mean in measures.column_means(z):
        assert abs(mean) <= 1e-12
    for sd in measures.column_stds(z):
        assert abs(sd - 1.0) <= 1e-12


def test_8_02_column_stds_use_the_population_divisor_n():
    rows = list(catalogue.BEARINGS.values())
    mine = measures.column_stds(rows)
    theirs = np.asarray(rows, dtype=float).std(axis=0)
    assert np.allclose(np.asarray(mine), theirs, atol=TOL)
    # ... and NOT the n-1 divisor, which is a visibly different number.
    sample = np.asarray(rows, dtype=float).std(axis=0, ddof=1)
    assert not np.allclose(np.asarray(mine), sample, atol=1e-6)


def test_8_03_raw_euclidean_picks_the_unusable_bearing():
    assert measures.winner(catalogue.BEARING_QUERY, catalogue.BEARINGS,
                           measures.l2_distance) == "R"


def test_8_04_standardising_changes_the_winner():
    rows = list(catalogue.BEARINGS.values())
    means = measures.column_means(rows)
    stds = measures.column_stds(rows)
    q = measures.standardise([catalogue.BEARING_QUERY], means, stds)[0]
    scaled = {n: measures.standardise([v], means, stds)[0]
              for n, v in catalogue.BEARINGS.items()}
    assert measures.winner(q, scaled, measures.l2_distance) == "P"


def test_8_05_the_bore_column_contributes_almost_nothing_before_scaling():
    q = catalogue.BEARING_QUERY
    for row in catalogue.BEARINGS.values():
        bore = (q[0] - row[0]) ** 2
        mass = (q[1] - row[1]) ** 2
        if bore + mass > 0:
            assert bore / (bore + mass) < 1e-4


def test_8_06_a_unit_change_alone_flips_the_ranking():
    q, cands = catalogue.BEARING_QUERY, catalogue.BEARINGS
    metres = measures.winner(q, cands, measures.l2_distance)
    micro_q = (q[0] * 1e6, q[1])
    micro = {n: (v[0] * 1e6, v[1]) for n, v in cands.items()}
    assert metres == "R"
    assert measures.winner(micro_q, micro, measures.l2_distance) == "P"


def test_8_07_standardise_leaves_a_constant_column_at_zero():
    rows = [(1.0, 5.0), (2.0, 5.0), (3.0, 5.0)]
    z = measures.standardise(rows)
    assert [row[1] for row in z] == [0.0, 0.0, 0.0]


def test_8_08_standardising_a_query_against_itself_would_give_zeros():
    """The mistake the API's `means`/`stds` arguments exist to prevent."""
    alone = measures.standardise([catalogue.BEARING_QUERY])[0]
    assert alone == [0.0, 0.0]


def test_8_09_cosine_is_not_invariant_to_a_column_unit_change():
    q, cands = catalogue.BEARING_QUERY, catalogue.BEARINGS
    a = measures.rank(q, cands, measures.cosine_similarity,
                      higher_is_better=True)
    micro_q = (q[0] * 1e6, q[1])
    micro = {n: (v[0] * 1e6, v[1]) for n, v in cands.items()}
    b = measures.rank(micro_q, micro, measures.cosine_similarity,
                      higher_is_better=True)
    assert [n for n, _ in a] != [n for n, _ in b]


def test_8_10_cosine_is_invariant_to_scaling_a_whole_vector():
    q, cands = catalogue.BEARING_QUERY, catalogue.BEARINGS
    a = measures.rank(q, cands, measures.cosine_similarity,
                      higher_is_better=True)
    doubled = {n: tuple(7.5 * c for c in v) for n, v in cands.items()}
    b = measures.rank(q, doubled, measures.cosine_similarity,
                      higher_is_better=True)
    assert [n for n, _ in a] == [n for n, _ in b]
    for (_, x), (_, y) in zip(a, b):
        assert abs(x - y) <= TOL


# -- 9. The ranking function and the guard rails ------------------------------


def test_9_01_rank_returns_every_candidate_once():
    order = measures.rank(Q, ARTICLES, measures.l1_distance)
    assert sorted(n for n, _ in order) == sorted(ARTICLES)


def test_9_02_rank_is_sorted_ascending_for_a_distance():
    scores = [s for _, s in measures.rank(Q, ARTICLES, measures.l2_distance)]
    assert scores == sorted(scores)


def test_9_03_rank_is_sorted_descending_for_a_similarity():
    scores = [s for _, s in measures.rank(Q, ARTICLES,
                                          measures.cosine_similarity,
                                          higher_is_better=True)]
    assert scores == sorted(scores, reverse=True)


def test_9_04_ties_break_by_name_so_the_output_is_deterministic():
    candidates = {"zulu": (1.0, 1.0), "alpha": (1.0, 1.0),
                  "mike": (1.0, 1.0)}
    order = [n for n, _ in measures.rank((0.0, 0.0), candidates,
                                         measures.l2_distance)]
    assert order == ["alpha", "mike", "zulu"]


def test_9_05_swapping_the_measure_is_one_argument():
    """The claim the lab is built on, stated as a test."""
    picks = {name: measures.winner(Q, ARTICLES, measure, higher)
             for name, (measure, higher) in {
                 "l1": (measures.l1_distance, False),
                 "l2": (measures.l2_distance, False),
                 "cos": (measures.cosine_similarity, True),
             }.items()}
    assert picks == {"l1": "Aisle", "l2": "Beacon", "cos": "Cartogram"}


@pytest.mark.parametrize("fn", [measures.l1_distance, measures.l2_distance,
                                measures.linf_distance, measures.dot])
def test_9_06_comparing_different_lengths_raises(fn):
    with pytest.raises(measures.DimensionMismatch):
        fn((1.0, 2.0, 3.0), (1.0, 2.0))


def test_9_07_dimension_mismatch_is_catchable_as_a_value_error():
    with pytest.raises(ValueError):
        measures.l2_distance((1.0,), (1.0, 2.0))


def test_9_08_mat_vec_and_matmul_agree_with_numpy():
    m = [[2.0, -1.0, 0.5], [0.0, 3.0, 1.0]]
    v = [1.0, 2.0, -4.0]
    assert np.allclose(np.asarray(measures.mat_vec(m, v)),
                       np.asarray(m) @ np.asarray(v), atol=TOL)
    n = [[1.0, 0.0], [2.0, -1.0], [0.5, 4.0]]
    assert np.allclose(np.asarray(measures.matmul(m, n)),
                       np.asarray(m) @ np.asarray(n), atol=TOL)


def test_9_09_transpose_swaps_rows_and_columns():
    assert measures.transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5],
                                                          [3, 6]]


def test_9_10_mahalanobis_refuses_a_matrix_that_is_not_a_covariance_inverse():
    bad = [[-1.0, 0.0], [0.0, -1.0]]
    with pytest.raises(ValueError):
        measures.mahalanobis_distance((1.0, 1.0), (0.0, 0.0), bad)
