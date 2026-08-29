"""Print every measured pair this lab asserts, as one table.

Run it with:

    .venv/bin/python examples/report_measurements.py

It imports nothing the tests do not import and computes nothing the
tests do not compute; it exists so you can read the numbers without
reading the assertions.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ml_lib as m  # noqa: E402
from sklearn.datasets import load_iris  # noqa: E402


def line(label: str, value) -> None:
    print(f"  {label:<46} {value}")


def main() -> None:
    print("Day 141 -- What the Number Is Not Telling You")
    print("Every value below is measured, not quoted.")
    print()

    print("1. Perfect accuracy, zero learning (labels are coin flips)")
    X_tr, y_tr = m.pure_noise_dataset(200, seed=141)
    X_te, y_te = m.pure_noise_dataset(1000, seed=242)
    hand = m.HandwrittenNearestNeighbour().fit(X_tr, y_tr)
    line("1-NN training accuracy (hand-written)", m.accuracy(y_tr, hand.predict(X_tr)))
    line("1-NN test accuracy (1000 unseen rows)", m.accuracy(y_te, hand.predict(X_te)))
    sk = m.one_nn().fit(X_tr, y_tr)
    line("1-NN training accuracy (scikit-learn)", m.accuracy(y_tr, sk.predict(X_tr)))
    line("1-NN test accuracy (scikit-learn)", m.accuracy(y_te, sk.predict(X_te)))
    X_iris, y_iris = load_iris(return_X_y=True)
    line("iris unique feature rows out of 150", len({tuple(r) for r in X_iris}))
    scrambled = np.random.default_rng(141).permutation(y_iris)
    hand_iris = m.HandwrittenNearestNeighbour().fit(X_iris, scrambled)
    line(
        "1-NN train accuracy, iris, scrambled labels",
        m.accuracy(scrambled, hand_iris.predict(X_iris)),
    )
    print()

    print("2. A rule beats a model")
    X_tr, y_tr = m.rule_dataset(300, seed=11)
    X_te, y_te = m.rule_dataset(2000, seed=12)
    line("three-line rule, test accuracy", m.accuracy(y_te, m.exact_rule(X_te)))
    for name, model in (
        ("depth-3 tree", m.shallow_tree(3)),
        ("depth-8 tree", m.shallow_tree(8)),
        ("full-depth tree", m.deep_tree()),
        ("15-NN", m.smooth_knn(15)),
    ):
        line(f"{name}, test accuracy", m.fit_score(model, X_tr, y_tr, X_te, y_te))
    print()

    print("3. The generalisation gap")
    perm = np.random.default_rng(141).permutation(len(y_iris))
    tr, te = perm[:100], perm[100:]
    tree = m.deep_tree().fit(X_iris[tr], y_iris[tr])
    a = m.accuracy(y_iris[tr], tree.predict(X_iris[tr]))
    b = m.accuracy(y_iris[te], tree.predict(X_iris[te]))
    line("iris full-depth tree, train accuracy", a)
    line("iris full-depth tree, test accuracy", b)
    line("iris gap", round(a - b, 4))
    X_tr, y_tr = m.noisy_rule_dataset(300, seed=21, noise_rate=0.2)
    X_te, y_te = m.noisy_rule_dataset(2000, seed=22, noise_rate=0.2)
    noisy = m.deep_tree().fit(X_tr, y_tr)
    c = m.accuracy(y_tr, noisy.predict(X_tr))
    d = m.accuracy(y_te, noisy.predict(X_te))
    line("noisy rule, train accuracy", c)
    line("noisy rule, test accuracy", d)
    line("noisy rule gap", round(c - d, 4))
    simple = m.linear_classifier().fit(X_tr, y_tr)
    line("same data, simple model, train accuracy", m.accuracy(y_tr, simple.predict(X_tr)))
    line("same data, simple model, test accuracy", m.accuracy(y_te, simple.predict(X_te)))
    print()

    print("4. Distribution shift (same rule, region translated by 3.0)")
    X_tr, y_tr = m.rule_dataset(400, seed=31)
    X_in, y_in = m.rule_dataset(2000, seed=32)
    X_sh, y_sh = m.rule_dataset(2000, seed=33, offset=3.0)
    tree = m.deep_tree().fit(X_tr, y_tr)
    line("in-distribution test accuracy", m.accuracy(y_in, tree.predict(X_in)))
    line("shifted test accuracy", m.accuracy(y_sh, tree.predict(X_sh)))
    line("the rule, on the shifted region", m.accuracy(y_sh, m.exact_rule(X_sh)))
    print()

    print("5. Interpolation versus extrapolation (y = x squared)")
    X_tr, y_tr = m.quadratic_curve(300, 0.0, 10.0, seed=41)
    X_in, y_in = m.quadratic_curve(200, 0.0, 10.0, seed=42)
    X_out, y_out = m.quadratic_curve(200, 10.0, 20.0, seed=43)
    knn = m.knn_regressor(5).fit(X_tr, y_tr)
    line("5-NN mean absolute error inside [0, 10]",
         round(m.mean_absolute_error(y_in, knn.predict(X_in)), 3))
    line("5-NN mean absolute error outside, [10, 20]",
         round(m.mean_absolute_error(y_out, knn.predict(X_out)), 3))
    line("5-NN largest prediction outside the range",
         round(float(np.max(knn.predict(X_out))), 3))
    line("largest target value ever seen in training",
         round(float(np.max(y_tr)), 3))
    lin = m.linear_regressor().fit(X_tr, y_tr)
    line("linear model, error inside the range",
         round(m.mean_absolute_error(y_in, lin.predict(X_in)), 3))
    line("linear model, error outside the range",
         round(m.mean_absolute_error(y_out, lin.predict(X_out)), 3))
    print()

    print("6. The baseline (90 percent class 0, features are pure noise)")
    X_tr, y_tr = m.imbalanced_noise_dataset(1000, seed=51)
    X_te, y_te = m.imbalanced_noise_dataset(1000, seed=52)
    line("majority-class baseline", m.fit_score(m.majority_baseline(), X_tr, y_tr, X_te, y_te))
    line("1-NN", m.fit_score(m.one_nn(), X_tr, y_tr, X_te, y_te))
    line("full-depth tree", m.fit_score(m.deep_tree(), X_tr, y_tr, X_te, y_te))
    line("iris majority-class baseline",
         m.fit_score(m.majority_baseline(), X_iris[tr], y_iris[tr], X_iris[te], y_iris[te]))
    line("iris 1-NN",
         m.fit_score(m.one_nn(), X_iris[tr], y_iris[tr], X_iris[te], y_iris[te]))
    print()

    print("7. The label-noise ceiling (exactly 25 percent of labels flipped)")
    X_tr, y_tr = m.noisy_rule_dataset(2000, seed=61, noise_rate=0.25)
    X_te, y_te = m.noisy_rule_dataset(4000, seed=62, noise_rate=0.25)
    line("the ceiling, 1 - noise_rate", 0.75)
    for name, model in (
        ("logistic regression", m.linear_classifier()),
        ("15-NN", m.smooth_knn(15)),
        ("depth-3 tree", m.shallow_tree(3)),
        ("full-depth tree", m.deep_tree()),
    ):
        line(f"{name}, test accuracy", m.fit_score(model, X_tr, y_tr, X_te, y_te))
    print()

    print("8. More data does not fix the wrong thing")
    X_te_c, y_te_c = m.checkerboard_dataset(4000, seed=71)
    small = m.fit_score(m.deep_tree(), *m.checkerboard_dataset(50, seed=120), X_te_c, y_te_c)
    large = m.fit_score(m.deep_tree(), *m.checkerboard_dataset(5000, seed=5070), X_te_c, y_te_c)
    line("variance-limited, n=50", small)
    line("variance-limited, n=5000", large)
    line("gain from 100x more data", round(large - small, 5))
    X_te_n, y_te_n = m.noisy_rule_dataset(4000, seed=81, noise_rate=0.30)
    few = m.fit_score(
        m.linear_classifier(), *m.noisy_rule_dataset(200, seed=280, noise_rate=0.30),
        X_te_n, y_te_n)
    many = m.fit_score(
        m.linear_classifier(), *m.noisy_rule_dataset(5000, seed=5080, noise_rate=0.30),
        X_te_n, y_te_n)
    line("noise-limited, n=200", few)
    line("noise-limited, n=5000", many)
    line("gain from 25x more data", round(many - few, 5))
    line("noise-limited ceiling", 0.7)
    print()

    print("9. should_use_ml, on six described problems")
    table = [
        ("VAT at a published rate", m.problem(True, True, True, True)),
        ("a rule exists, nothing else does", m.problem(True, False, False, False)),
        ("unlabelled support tickets", m.problem(False, False, True, True)),
        ("adaptive payment fraud", m.problem(False, True, False, True)),
        ("unsupervised dosing decision", m.problem(False, True, True, False)),
        ("handwritten postcodes", m.problem(False, True, True, True)),
    ]
    for label, case in table:
        line(label, m.should_use_ml(case))


if __name__ == "__main__":
    main()
