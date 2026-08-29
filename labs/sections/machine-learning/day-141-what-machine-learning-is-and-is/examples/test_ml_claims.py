"""Nine measured claims about what an accuracy number is not telling you.

Every assertion below is on a value or a shape that was measured on a
real run, never on a timing. Every dataset is seeded, so the numbers in
the comments are the numbers you will see.
"""

import numpy as np

import ml_lib as m

# --------------------------------------------------------------------------
# 1. Perfect accuracy, zero learning
# --------------------------------------------------------------------------


def test_01_one_nn_scores_a_perfect_1_000_having_learned_nothing():
    """Labels are coin flips. There is no function to approximate.

    Measured: training accuracy 1.000 for both the hand-written model and
    scikit-learn's; test accuracy 0.518 on 1000 unseen rows, which is
    chance.
    """
    X_train, y_train = m.pure_noise_dataset(200, seed=141)
    X_test, y_test = m.pure_noise_dataset(1000, seed=242)

    handwritten = m.HandwrittenNearestNeighbour().fit(X_train, y_train)
    train_acc = m.accuracy(y_train, handwritten.predict(X_train))
    test_acc = m.accuracy(y_test, handwritten.predict(X_test))

    assert train_acc == 1.0
    assert test_acc == 0.518
    assert abs(test_acc - 0.5) < 0.06  # chance, within sampling noise

    # scikit-learn's KNeighborsClassifier(n_neighbors=1) agrees exactly.
    library = m.one_nn().fit(X_train, y_train)
    assert m.accuracy(y_train, library.predict(X_train)) == 1.0
    assert m.accuracy(y_test, library.predict(X_test)) == test_acc


def test_01b_the_only_way_a_1_nn_misses_a_training_row_is_a_duplicate():
    """The "1.000 by construction" claim has exactly one exception.

    A training row is its own nearest neighbour at distance zero -- unless
    an identical feature row carries a different label, in which case the
    tie can be broken the wrong way. The iris dataset contains exactly one
    duplicated feature row (positions 101 and 142). Both carry class 2, so
    on the real labels 1-NN still scores 1.000; scramble the labels and the
    same pair drops it to 0.99. Measured, not assumed.
    """
    from sklearn.datasets import load_iris

    X, y = load_iris(return_X_y=True)
    unique_rows = {tuple(row) for row in X}
    assert X.shape == (150, 4)
    assert len(unique_rows) == 149  # one duplicated feature row

    on_real_labels = m.HandwrittenNearestNeighbour().fit(X, y)
    assert m.accuracy(y, on_real_labels.predict(X)) == 1.0

    scrambled = np.random.default_rng(141).permutation(y)
    on_scrambled = m.HandwrittenNearestNeighbour().fit(X, scrambled)
    assert m.accuracy(scrambled, on_scrambled.predict(X)) < 1.0


# --------------------------------------------------------------------------
# 2. A rule beats a model
# --------------------------------------------------------------------------


def test_02_a_three_line_rule_scores_1_000_and_every_model_scores_less():
    """`y = 1 if x1 > x0 else 0`. Three lines, exactly correct, forever.

    Measured on 2000 unseen rows: the rule 1.000; a depth-3 tree 0.8855;
    the best of four trained models (15-NN) 0.9675. None reaches the rule.
    """
    X_train, y_train = m.rule_dataset(300, seed=11)
    X_test, y_test = m.rule_dataset(2000, seed=12)

    rule_acc = m.accuracy(y_test, m.exact_rule(X_test))
    assert rule_acc == 1.0

    model_acc = m.fit_score(m.shallow_tree(3), X_train, y_train, X_test, y_test)
    assert model_acc == 0.8855
    assert model_acc < rule_acc

    scores = {
        "depth-3 tree": model_acc,
        "depth-8 tree": m.fit_score(m.shallow_tree(8), X_train, y_train, X_test, y_test),
        "full-depth tree": m.fit_score(m.deep_tree(), X_train, y_train, X_test, y_test),
        "15-NN": m.fit_score(m.smooth_knn(15), X_train, y_train, X_test, y_test),
    }
    assert max(scores.values()) == 0.9675
    assert all(score < rule_acc for score in scores.values())


# --------------------------------------------------------------------------
# 3. The generalisation gap
# --------------------------------------------------------------------------


def test_03_train_accuracy_exceeds_test_accuracy_and_the_gap_is_the_story():
    """Two gaps, both measured: a small honest one and a large one.

    iris, full-depth tree: train 1.000, test 0.960, gap 0.040.
    Noisy constructed data, same model: train 1.000, test 0.6535,
    gap 0.3465. Identical training score, wildly different models.
    """
    from sklearn.datasets import load_iris

    X, y = load_iris(return_X_y=True)
    perm = np.random.default_rng(141).permutation(len(y))
    train_idx, test_idx = perm[:100], perm[100:]

    tree = m.deep_tree().fit(X[train_idx], y[train_idx])
    iris_train = m.accuracy(y[train_idx], tree.predict(X[train_idx]))
    iris_test = m.accuracy(y[test_idx], tree.predict(X[test_idx]))
    assert iris_train == 1.0
    assert iris_test == 0.96
    assert iris_train > iris_test
    assert round(iris_train - iris_test, 4) == 0.04

    X_train, y_train = m.noisy_rule_dataset(300, seed=21, noise_rate=0.2)
    X_test, y_test = m.noisy_rule_dataset(2000, seed=22, noise_rate=0.2)
    noisy = m.deep_tree().fit(X_train, y_train)
    noisy_train = m.accuracy(y_train, noisy.predict(X_train))
    noisy_test = m.accuracy(y_test, noisy.predict(X_test))
    assert noisy_train == 1.0
    assert noisy_test == 0.6535
    assert round(noisy_train - noisy_test, 4) == 0.3465

    # Same perfect training score, gap eight times larger.
    assert noisy_train == iris_train
    assert (noisy_train - noisy_test) > 8 * (iris_train - iris_test)

    # And the sentence the whole day turns on: on this same data a much
    # simpler model scores WORSE in training (0.780 against 1.000) and
    # BETTER on unseen data (0.7655 against 0.6535). The better training
    # score belongs to the worse model.
    simple = m.linear_classifier().fit(X_train, y_train)
    simple_train = m.accuracy(y_train, simple.predict(X_train))
    simple_test = m.accuracy(y_test, simple.predict(X_test))
    assert simple_train == 0.78
    assert simple_test == 0.7655
    assert simple_train < noisy_train
    assert simple_test > noisy_test


# --------------------------------------------------------------------------
# 4. Distribution shift
# --------------------------------------------------------------------------


def test_04_accuracy_collapses_when_the_input_region_moves():
    """Same labelling rule, different region of feature space.

    Trained on the unit square, the tree scores 0.948 on unseen points
    from the unit square and 0.4895 -- below chance -- on the identical
    problem translated by 3.0. The rule scores 1.000 on both.
    """
    X_train, y_train = m.rule_dataset(400, seed=31)
    X_in, y_in = m.rule_dataset(2000, seed=32)
    X_shifted, y_shifted = m.rule_dataset(2000, seed=33, offset=3.0)

    tree = m.deep_tree().fit(X_train, y_train)
    in_dist = m.accuracy(y_in, tree.predict(X_in))
    shifted = m.accuracy(y_shifted, tree.predict(X_shifted))

    assert in_dist == 0.948
    assert shifted == 0.4895
    assert shifted < 0.55  # at or below chance
    assert in_dist - shifted > 0.4

    # The model was never told the region had moved, and could not have
    # been: nothing in the training data describes where it ends.
    assert m.accuracy(y_shifted, m.exact_rule(X_shifted)) == 1.0


# --------------------------------------------------------------------------
# 5. Interpolation versus extrapolation
# --------------------------------------------------------------------------


def test_05_a_model_interpolates_beautifully_and_extrapolates_not_at_all():
    """y = x squared, learned on [0, 10], asked about [10, 20].

    Measured mean absolute error: 0.180 inside the training range,
    139.704 outside it -- 774 times worse. This is not a bug in the
    model. A nearest-neighbour regressor has nothing outside its range
    but the edge of what it saw.
    """
    X_train, y_train = m.quadratic_curve(300, 0.0, 10.0, seed=41)
    X_in, y_in = m.quadratic_curve(200, 0.0, 10.0, seed=42)
    X_out, y_out = m.quadratic_curve(200, 10.0, 20.0, seed=43)

    model = m.knn_regressor(5).fit(X_train, y_train)
    mae_in = m.mean_absolute_error(y_in, model.predict(X_in))
    mae_out = m.mean_absolute_error(y_out, model.predict(X_out))

    assert round(mae_in, 3) == 0.180
    assert round(mae_out, 3) == 139.704
    assert mae_out > 700 * mae_in

    # Its predictions outside the range are bounded by what it has seen.
    assert float(np.max(model.predict(X_out))) <= float(np.max(y_train))

    # A linear model extrapolates differently -- and still badly, because
    # the truth is a parabola: 6.007 inside, 101.643 outside.
    linear = m.linear_regressor().fit(X_train, y_train)
    assert round(m.mean_absolute_error(y_in, linear.predict(X_in)), 3) == 6.007
    assert round(m.mean_absolute_error(y_out, linear.predict(X_out)), 3) == 101.643


# --------------------------------------------------------------------------
# 6. The baseline
# --------------------------------------------------------------------------


def test_06_a_good_looking_accuracy_that_loses_to_predicting_the_majority():
    """90 percent of rows are class 0 and the features are pure noise.

    The majority-class baseline scores exactly 0.900. A 1-NN scores
    0.821 and a full-depth tree 0.817. Both would be reported as "82
    percent accurate" and both are worse than a constant.
    """
    X_train, y_train = m.imbalanced_noise_dataset(1000, seed=51)
    X_test, y_test = m.imbalanced_noise_dataset(1000, seed=52)

    baseline = m.fit_score(m.majority_baseline(), X_train, y_train, X_test, y_test)
    assert baseline == 0.9
    assert float(np.mean(y_test == 0)) == 0.9  # exact by construction

    one_nn = m.fit_score(m.one_nn(), X_train, y_train, X_test, y_test)
    tree = m.fit_score(m.deep_tree(), X_train, y_train, X_test, y_test)
    assert one_nn == 0.821
    assert tree == 0.817
    assert one_nn < baseline and tree < baseline

    # On a problem where the features do carry signal, the same comparison
    # is the one that shows it: iris baseline 0.260, 1-NN 0.980.
    from sklearn.datasets import load_iris

    X, y = load_iris(return_X_y=True)
    perm = np.random.default_rng(141).permutation(len(y))
    tr, te = perm[:100], perm[100:]
    iris_baseline = m.fit_score(m.majority_baseline(), X[tr], y[tr], X[te], y[te])
    iris_model = m.fit_score(m.one_nn(), X[tr], y[tr], X[te], y[te])
    assert iris_baseline == 0.26
    assert iris_model == 0.98
    assert iris_model > iris_baseline


# --------------------------------------------------------------------------
# 7. The irreducible error ceiling
# --------------------------------------------------------------------------


def test_07_no_model_beats_the_label_noise_ceiling():
    """Exactly 25 percent of labels are flipped, in training and in test.

    A perfect model of the underlying rule would score 0.750 on this test
    set, because a quarter of its correct answers are marked wrong. That
    is the ceiling. Measured: logistic regression 0.73725, 15-NN 0.72675,
    depth-3 tree 0.68825, full-depth tree 0.60875. None exceeds 0.750.
    """
    noise_rate = 0.25
    ceiling = 1.0 - noise_rate
    X_train, y_train = m.noisy_rule_dataset(2000, seed=61, noise_rate=noise_rate)
    X_test, y_test = m.noisy_rule_dataset(4000, seed=62, noise_rate=noise_rate)

    scores = {
        "logistic regression": m.fit_score(
            m.linear_classifier(), X_train, y_train, X_test, y_test
        ),
        "15-NN": m.fit_score(m.smooth_knn(15), X_train, y_train, X_test, y_test),
        "depth-3 tree": m.fit_score(m.shallow_tree(3), X_train, y_train, X_test, y_test),
        "full-depth tree": m.fit_score(m.deep_tree(), X_train, y_train, X_test, y_test),
    }
    assert scores["logistic regression"] == 0.73725
    assert scores["15-NN"] == 0.72675
    assert scores["depth-3 tree"] == 0.68825
    assert scores["full-depth tree"] == 0.60875
    for name, score in scores.items():
        assert score <= ceiling, f"{name} scored {score}, above the ceiling {ceiling}"

    # The best model is within 1.3 points of the ceiling. The remaining
    # 26.3 points are not available to any model, however large.
    assert ceiling - max(scores.values()) < 0.02

    # The exact flip count is what makes the ceiling exact rather than
    # estimated: 1000 of 4000 test labels.
    _, y_clean = m.rule_dataset(4000, seed=62)
    assert int(np.sum(y_clean != y_test)) == 1000


# --------------------------------------------------------------------------
# 8. More data does not fix the wrong thing
# --------------------------------------------------------------------------


def test_08_more_data_fixes_variance_and_does_nothing_for_label_noise():
    """Two problems, one hundredfold and one twenty-fivefold increase.

    Variance-limited (a clean 4x4 checkerboard boundary, full-depth
    tree): 0.5995 at n=50, 0.99725 at n=5000 -- a gain of 39.8 points.
    Noise-limited (a linearly separable rule with 30 percent of labels
    flipped, logistic regression): 0.6655 at n=200, 0.68675 at n=5000 --
    a gain of 2.1 points against a ceiling of 0.700, which it was already
    within 3.5 points of at n=200.
    """
    X_test_c, y_test_c = m.checkerboard_dataset(4000, seed=71)
    small = m.fit_score(
        m.deep_tree(), *m.checkerboard_dataset(50, seed=120), X_test_c, y_test_c
    )
    large = m.fit_score(
        m.deep_tree(), *m.checkerboard_dataset(5000, seed=5070), X_test_c, y_test_c
    )
    assert small == 0.5995
    assert large == 0.99725
    assert large - small > 0.30

    noise_rate = 0.30
    X_test_n, y_test_n = m.noisy_rule_dataset(4000, seed=81, noise_rate=noise_rate)
    few = m.fit_score(
        m.linear_classifier(),
        *m.noisy_rule_dataset(200, seed=280, noise_rate=noise_rate),
        X_test_n,
        y_test_n,
    )
    many = m.fit_score(
        m.linear_classifier(),
        *m.noisy_rule_dataset(5000, seed=5080, noise_rate=noise_rate),
        X_test_n,
        y_test_n,
    )
    assert few == 0.6655
    assert many == 0.68675
    assert many - few < 0.05

    # The honest statement: the noise-limited model does improve, by 2.1
    # points, because n=200 is a small sample. What it cannot do is cross
    # its ceiling, and it starts 3.5 points below it.
    ceiling = 1.0 - noise_rate
    assert many < ceiling
    assert ceiling - few < 0.05
    assert (large - small) > 15 * (many - few)


# --------------------------------------------------------------------------
# 9. The decision function
# --------------------------------------------------------------------------


def test_09_should_use_ml_gives_the_verdict_the_case_deserves():
    """A table of cases, each justified in a comment.

    The order of the questions is the point: the cheapest disqualifier is
    asked first.
    """
    cases = [
        # Value-added tax on a known rate table. The rule is law, written
        # down, and a model that approximates it is a compliance defect.
        (m.problem(True, True, True, True), "write the rule"),
        # A rule exists but nothing else does. Still write the rule: the
        # rule is exactly correct without any of the rest.
        (m.problem(True, False, False, False), "write the rule"),
        # Sentiment of free-text support tickets, none of them labelled.
        # No labels, no supervised learning. Get labels first.
        (m.problem(False, False, True, True), "get labels first"),
        # Fraud patterns in a payment network where adversaries adapt
        # weekly. Labels exist, but yesterday's distribution is gone.
        (m.problem(False, True, False, True), "not yet: the distribution moves"),
        # An automated dosing decision with no human in the loop, where a
        # single wrong answer is not recoverable.
        (m.problem(False, True, True, False), "no: errors are not tolerable"),
        # Handwritten postcode recognition: no rule anyone can write,
        # millions of labelled examples, a stable distribution, and a
        # wrong read costs one redirected letter.
        (m.problem(False, True, True, True), "yes"),
    ]
    for case, expected in cases:
        assert m.should_use_ml(case) == expected, case

    # A missing question is an error, not a default. You do not get to
    # skip one of the four.
    try:
        m.should_use_ml({"exact_rule_exists": False})
    except KeyError as error:
        assert "labels_available" in str(error)
    else:
        raise AssertionError("should_use_ml accepted an incomplete problem")
