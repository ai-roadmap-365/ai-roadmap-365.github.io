"""The nine experiments, each one a function that returns numbers.

The tests assert on what these return, and `tests/run_tests.sh` prints
them. Keeping the experiments here rather than inside the tests means the
same code produces the numbers in the lesson, the numbers in
`expected-output/` and the numbers the assertions check, so the three
cannot drift apart.

Every function is deterministic. Where an experiment averages over many
random splits it says so in its name and its docstring, and the seeds are
generated from a fixed base seed.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import data
import features as F
import models as M

HONEST_COLUMNS = ["visits", "minutes_on_site", "discount_pct"]
LEAKY_COLUMNS = HONEST_COLUMNS + ["days_to_first_invoice"]


def _fit_score(X_train, y_train, X_test, y_test, model=None) -> float:
    model = model or M.LogisticRegression()
    model.fit(X_train, y_train)
    return model.score(X_test, y_test)


# --- 1. target leakage -----------------------------------------------------


def target_leakage(test_size: int = 100, seed: int = 137) -> dict[str, float]:
    """Score the same task twice: with the planted leak and without it.

    Both runs use the same split, the same model and the same number of
    gradient steps. The only difference is one column.
    """
    frame = data.signups()
    y = frame["converted"].to_numpy()
    train_idx, test_idx = M.random_split(len(frame), test_size, seed)
    out: dict[str, float] = {}
    for name, columns in (("with_leak", LEAKY_COLUMNS), ("without_leak", HONEST_COLUMNS)):
        X = frame[columns].to_numpy(dtype=float)
        scaler = F.Standardiser().fit(X[train_idx])
        out[name] = _fit_score(
            scaler.transform(X[train_idx]),
            y[train_idx],
            scaler.transform(X[test_idx]),
            y[test_idx],
        )
    out["gap_points"] = 100.0 * (out["with_leak"] - out["without_leak"])
    return out


# --- 2. train/test contamination through a scaler --------------------------


def scaling_contamination(
    trials: int = 200, train_size: int = 60, test_size: int = 25, seed: int = 137
) -> dict[str, float]:
    """Fit the scaler on everything, or on the training rows only.

    Averaged over `trials` random splits, because with a 25-row test set
    one row is four accuracy points and a single split says nothing. The
    model is the nearest-centroid classifier, which is distance-based and
    therefore cares about scale; a logistic regression run to convergence
    is very nearly invariant to an affine change of features and shows
    almost nothing here.

    The mechanism is worth stating plainly: the contaminated scaler is a
    BETTER estimate of the population mean and spread than a scaler
    fitted on 60 rows. It got that way by reading rows it was not allowed
    to read, and the score it produces is therefore not a score you will
    ever see in production.
    """
    frame = data.pricing()
    X_all = frame[["order_value", "tenure_days"]].to_numpy(dtype=float)
    y_all = frame["renewed"].to_numpy()
    contaminated_scores: list[float] = []
    correct_scores: list[float] = []
    for trial in range(trials):
        rng = np.random.default_rng(seed + trial)
        order = rng.permutation(len(frame))
        train_idx = order[:train_size]
        test_idx = order[train_size : train_size + test_size]

        wrong = F.Standardiser().fit(X_all)  # every row, including the test rows
        right = F.Standardiser().fit(X_all[train_idx])  # training rows only

        contaminated_scores.append(
            _fit_score(
                wrong.transform(X_all[train_idx]),
                y_all[train_idx],
                wrong.transform(X_all[test_idx]),
                y_all[test_idx],
                M.NearestCentroid(),
            )
        )
        correct_scores.append(
            _fit_score(
                right.transform(X_all[train_idx]),
                y_all[train_idx],
                right.transform(X_all[test_idx]),
                y_all[test_idx],
                M.NearestCentroid(),
            )
        )
    contaminated = float(np.mean(contaminated_scores))
    correct = float(np.mean(correct_scores))
    return {
        "contaminated": contaminated,
        "correct": correct,
        "optimism_points": 100.0 * (contaminated - correct),
        "trials": float(trials),
        "train_size": float(train_size),
        "test_size": float(test_size),
        "contaminated_mean_order_value": float(F.Standardiser().fit(X_all).mean_[0]),
    }


def imputer_contamination(
    trials: int = 150, train_size: int = 120, test_size: int = 200, seed: int = 137
) -> dict[str, float]:
    """The same question asked of an imputer instead of a scaler.

    A group-mean imputer is not an affine map. Each missing value is
    filled with a number computed from the rows that happen to be
    observed in its own group -- so if the fit sees the test rows, a
    test row's gap is filled using the readings of its own panel that
    live in the test set. That is information the deployed system will
    not have, and here it is worth several accuracy points rather than
    the fraction of a point the scaler was worth.
    """
    frame = data.panel_readings()
    panel = frame["panel"].to_numpy()
    reading = frame["reading"].to_numpy(dtype=float)
    y = frame["fault"].to_numpy()
    n = len(frame)
    missing = np.isnan(reading)

    everything = F.GroupMeanImputer().fit(panel, reading)

    def build(rows, imputer) -> np.ndarray:
        filled = imputer.transform(panel[rows], reading[rows])
        return np.column_stack([filled, missing[rows].astype(float)])

    contaminated_scores: list[float] = []
    correct_scores: list[float] = []
    for trial in range(trials):
        rng = np.random.default_rng(seed + trial)
        order = rng.permutation(n)
        train_idx = order[:train_size]
        test_idx = order[train_size : train_size + test_size]
        train_only = F.GroupMeanImputer().fit(panel[train_idx], reading[train_idx])
        for imputer, bucket in ((everything, contaminated_scores), (train_only, correct_scores)):
            X_train = build(train_idx, imputer)
            X_test = build(test_idx, imputer)
            scaler = F.Standardiser().fit(X_train)
            bucket.append(
                _fit_score(
                    scaler.transform(X_train), y[train_idx], scaler.transform(X_test), y[test_idx]
                )
            )
    contaminated = float(np.mean(contaminated_scores))
    correct = float(np.mean(correct_scores))
    return {
        "contaminated": contaminated,
        "correct": correct,
        "optimism_points": 100.0 * (contaminated - correct),
        "trials": float(trials),
        "train_size": float(train_size),
        "test_size": float(test_size),
        "missing_fraction": float(missing.mean()),
        "groups_known_to_all_data_fit": float(len(everything.means_)),
    }


# --- 3. target encoding ----------------------------------------------------


def target_encoding(
    test_size: int = 150, seed: int = 137, n_folds: int = 5, trials: int = 40
) -> dict[str, float]:
    """Three ways to encode a city, scored on the same held-out rows.

    * `naive_all_data` computes the per-city mean of the target over the
      whole table, then splits. Every test row's feature was computed
      partly from its own answer.
    * `naive_train_only` computes it on the training rows only, which
      removes the test rows' contribution but still lets each training
      row see its own target.
    * `out_of_fold` encodes each training row from the folds that do not
      contain it.
    """
    frame = data.city_signups()
    y = frame["converted"].to_numpy()
    visits = frame["visits"].to_numpy(dtype=float)
    city = frame["city"].to_numpy()

    all_scores: list[float] = []
    train_scores: list[float] = []
    oof_scores: list[float] = []
    for trial in range(trials):
        train_idx, test_idx = M.random_split(len(frame), test_size, seed + trial)

        def score(train_codes, test_codes) -> float:
            X_train = np.column_stack([visits[train_idx], train_codes])
            X_test = np.column_stack([visits[test_idx], test_codes])
            scaler = F.Standardiser().fit(X_train)
            return _fit_score(
                scaler.transform(X_train), y[train_idx], scaler.transform(X_test), y[test_idx]
            )

        all_map, all_default = F.target_encode_fit(city, y)
        all_scores.append(
            score(
                F.target_encode_transform(city[train_idx], all_map, all_default),
                F.target_encode_transform(city[test_idx], all_map, all_default),
            )
        )

        train_map, train_default = F.target_encode_fit(city[train_idx], y[train_idx])
        train_scores.append(
            score(
                F.target_encode_transform(city[train_idx], train_map, train_default),
                F.target_encode_transform(city[test_idx], train_map, train_default),
            )
        )

        oof = F.target_encode_out_of_fold(
            city[train_idx], y[train_idx], n_folds=n_folds, seed=seed + trial
        )
        oof_scores.append(
            score(oof, F.target_encode_transform(city[test_idx], train_map, train_default))
        )

    naive_all = float(np.mean(all_scores))
    naive_train = float(np.mean(train_scores))
    out_of_fold = float(np.mean(oof_scores))
    return {
        "naive_all_data": naive_all,
        "naive_train_only": naive_train,
        "out_of_fold": out_of_fold,
        "gap_all_vs_oof_points": 100.0 * (naive_all - out_of_fold),
        "gap_train_vs_oof_points": 100.0 * (naive_train - out_of_fold),
        "n_folds": float(n_folds),
        "trials": float(trials),
    }


# --- 4. temporal leakage ---------------------------------------------------


def temporal_leakage(test_size: int = 60, seed: int = 137) -> dict[str, float]:
    """The same table, split two ways: at random, and by time.

    The rows are already in time order. The random split lets rows from
    the last regime into training, so the model is scored on a rule it
    has already seen. The time-ordered split holds the last regime out
    entirely, which is the only one of the two that answers the question
    anybody actually asked.
    """
    frame = data.sensor_log()
    y = frame["alarm"].to_numpy()
    reading = frame["reading"].to_numpy(dtype=float)
    batch = frame["batch"].to_numpy()

    def score(train_idx, test_idx) -> float:
        # The batch encoding is fitted on the training rows only, which is
        # the correct thing to do and is exactly what exposes the problem:
        # a batch the training rows never contained becomes an all-zero
        # block, and the model has nothing to say about it.
        seen = sorted(set(batch[train_idx].tolist()))
        train_block, _ = F.one_hot(batch[train_idx], seen)
        test_block, _ = F.one_hot(batch[test_idx], seen)
        X_train = np.column_stack([reading[train_idx], train_block])
        X_test = np.column_stack([reading[test_idx], test_block])
        scaler = F.Standardiser().fit(X_train)
        return _fit_score(
            scaler.transform(X_train), y[train_idx], scaler.transform(X_test), y[test_idx]
        )

    random_train, random_test = M.random_split(len(frame), test_size, seed)
    ordered_train, ordered_test = M.time_ordered_split(len(frame), test_size)
    random_score = score(random_train, random_test)
    ordered_score = score(ordered_train, ordered_test)
    return {
        "random_split": random_score,
        "time_ordered_split": ordered_score,
        "gap_points": 100.0 * (random_score - ordered_score),
        "batches_seen_by_random_train": float(len(set(batch[random_train].tolist()))),
        "batches_seen_by_ordered_train": float(len(set(batch[ordered_train].tolist()))),
        "test_batches_unseen_by_ordered_train": float(
            len(set(batch[ordered_test].tolist()) - set(batch[ordered_train].tolist()))
        ),
        "majority_rate_in_ordered_test": float(max(y[ordered_test].mean(), 1 - y[ordered_test].mean())),
    }


# --- 5. cyclical encoding --------------------------------------------------


def cyclical_distances(period: int = 24) -> dict[str, float]:
    """Distances between hours, raw and on the circle.

    Raw integer hours: 23 and 0 sit 23 units apart while 3 and 4 sit 1
    apart. Sine-cosine: every adjacent pair, wrap included, sits exactly
    2*sin(pi/24) apart.
    """
    hours = np.arange(period)
    raw = hours.reshape(-1, 1).astype(float)
    circle = F.cyclical_encode(hours, period)

    def distance(matrix, a: int, b: int) -> float:
        return float(np.linalg.norm(matrix[a] - matrix[b]))

    adjacent_raw = [distance(raw, h, (h + 1) % period) for h in range(period)]
    adjacent_circle = [distance(circle, h, (h + 1) % period) for h in range(period)]
    return {
        "raw_23_to_0": distance(raw, 23, 0),
        "raw_3_to_4": distance(raw, 3, 4),
        "cyclical_23_to_0": distance(circle, 23, 0),
        "cyclical_3_to_4": distance(circle, 3, 4),
        "cyclical_0_to_12": distance(circle, 0, 12),
        "cyclical_adjacent_spread": float(max(adjacent_circle) - min(adjacent_circle)),
        "raw_adjacent_spread": float(max(adjacent_raw) - min(adjacent_raw)),
        "expected_adjacent": float(2.0 * np.sin(np.pi / period)),
    }


# --- 6. ordinal versus one-hot --------------------------------------------


def ordinal_versus_one_hot(seed: int = 137) -> dict[str, object]:
    """Fit the same model on an ordinal code and on a one-hot block.

    The colours have no order, and their return rates are deliberately
    not monotone in the alphabetical code. A model reading the code as a
    number can only produce predictions that rise or fall with it; the
    one-hot model is free to give each colour its own answer.
    """
    frame = data.paint_orders()
    y = frame["returned"].to_numpy()
    colours = frame["colour"].to_numpy()
    order = list(data.PAINT_COLOURS)

    codes = F.ordinal_encode(colours, order).reshape(-1, 1)
    ordinal_model = M.LogisticRegression(learning_rate=0.3, steps=4000).fit(codes, y)
    ordinal_rates = ordinal_model.predict_proba(
        np.arange(len(order), dtype=float).reshape(-1, 1)
    )

    block, categories = F.one_hot(colours, order)
    one_hot_model = M.LogisticRegression(learning_rate=0.3, steps=4000).fit(block, y)
    one_hot_rates = one_hot_model.predict_proba(np.eye(len(order)))

    observed = np.array(
        [float(y[colours == name].mean()) for name in order], dtype=float
    )

    def is_monotone(values: np.ndarray) -> bool:
        diffs = np.diff(values)
        return bool(np.all(diffs >= -1e-12) or np.all(diffs <= 1e-12))

    return {
        "categories": categories,
        "observed_rates": observed.tolist(),
        "ordinal_predictions": ordinal_rates.tolist(),
        "one_hot_predictions": one_hot_rates.tolist(),
        "ordinal_is_monotone": is_monotone(ordinal_rates),
        "one_hot_is_monotone": is_monotone(one_hot_rates),
        "ordinal_max_error": float(np.max(np.abs(ordinal_rates - observed))),
        "one_hot_max_error": float(np.max(np.abs(one_hot_rates - observed))),
        "ordinal_accuracy": float(ordinal_model.score(codes, y)),
        "one_hot_accuracy": float(one_hot_model.score(block, y)),
    }


# --- 7. an interaction -----------------------------------------------------


def interaction(test_size: int = 150, seed: int = 137) -> dict[str, float]:
    """Score income alone, spend alone, and the ratio of the two."""
    frame = data.credit_lines()
    y = frame["stressed"].to_numpy()
    train_idx, test_idx = M.random_split(len(frame), test_size, seed)
    income = frame["income"].to_numpy(dtype=float)
    spend = frame["spend"].to_numpy(dtype=float)
    ratio = F.ratio_feature(spend, income)

    def score(column: np.ndarray) -> float:
        X = column.reshape(-1, 1)
        scaler = F.Standardiser().fit(X[train_idx])
        return _fit_score(
            scaler.transform(X[train_idx]), y[train_idx], scaler.transform(X[test_idx]), y[test_idx]
        )

    both = np.column_stack([income, spend])
    scaler = F.Standardiser().fit(both[train_idx])
    both_score = _fit_score(
        scaler.transform(both[train_idx]),
        y[train_idx],
        scaler.transform(both[test_idx]),
        y[test_idx],
    )
    return {
        "income_only": score(income),
        "spend_only": score(spend),
        "ratio_only": score(ratio),
        "income_and_spend": both_score,
    }


# --- 8. vocabulary fitted on the wrong rows --------------------------------


def vocabulary_contamination(
    top_k: int = 30, test_size: int = 100, seed: int = 137, min_docs: int = 2, trials: int = 40
) -> dict[str, float]:
    """Choose the words on everything, or on the training documents only.

    The vocabulary is selected by association with the label, so choosing
    it on all the documents means the test labels helped decide which
    features exist. That is feature selection fitted before the split --
    the second kind of leakage, wearing a text-shaped costume.
    """
    frame = data.tickets()
    documents = frame["text"].tolist()
    y = frame["urgent"].to_numpy()
    all_data_vocab = F.Vocabulary(top_k=top_k, min_docs=min_docs).fit(documents, y)

    all_scores: list[float] = []
    train_scores: list[float] = []
    shared: list[int] = []
    for trial in range(trials):
        train_idx, test_idx = M.random_split(len(frame), test_size, seed + trial)
        train_docs = [documents[i] for i in train_idx]
        test_docs = [documents[i] for i in test_idx]
        train_only_vocab = F.Vocabulary(top_k=top_k, min_docs=min_docs).fit(
            train_docs, y[train_idx]
        )
        shared.append(len(set(all_data_vocab.words) & set(train_only_vocab.words)))
        for vocabulary, bucket in ((all_data_vocab, all_scores), (train_only_vocab, train_scores)):
            bucket.append(
                _fit_score(
                    vocabulary.transform(train_docs),
                    y[train_idx],
                    vocabulary.transform(test_docs),
                    y[test_idx],
                )
            )

    # One split, examined in detail, for the unseen-word behaviour.
    train_idx, test_idx = M.random_split(len(frame), test_size, seed)
    train_docs = [documents[i] for i in train_idx]
    test_docs = [documents[i] for i in test_idx]
    train_only_vocab = F.Vocabulary(top_k=top_k, min_docs=min_docs).fit(train_docs, y[train_idx])
    unseen = train_only_vocab.unseen_words(test_docs)
    test_matrix = train_only_vocab.transform(test_docs)

    fitted_all = float(np.mean(all_scores))
    fitted_train = float(np.mean(train_scores))
    return {
        "fitted_on_all_data": fitted_all,
        "fitted_on_train_only": fitted_train,
        "gap_points": 100.0 * (fitted_all - fitted_train),
        "unseen_test_words": float(len(unseen)),
        "test_matrix_columns": float(test_matrix.shape[1]),
        "test_matrix_rows": float(test_matrix.shape[0]),
        "shared_words": float(np.mean(shared)),
        "top_k": float(top_k),
        "trials": float(trials),
    }


# --- extra: a bin boundary is a decision (Day 130's bin width again) -------


def binning_decision(bins: int = 3) -> dict[str, object]:
    """Bin the same column two ways and read two different stories off it.

    Equal-width edges come from NumPy's own edge calculator. Equal-count
    edges come from the quantiles of the same column. Neither is wrong.
    They put wildly different numbers of rows in the top bin, and the
    renewal rate you would quote for "high value orders" depends entirely
    on which one you picked.
    """
    frame = data.pricing()
    values = frame["order_value"].to_numpy(dtype=float)
    y = frame["renewed"].to_numpy()

    width_edges = F.equal_width_bins(values, bins)
    count_edges = np.quantile(values, np.linspace(0.0, 1.0, bins + 1))
    width_index = F.bin_index(values, width_edges)
    count_index = F.bin_index(values, count_edges)

    def top_bin(index: np.ndarray) -> tuple[int, float]:
        top = index == index.max()
        return int(top.sum()), float(y[top].mean())

    width_rows, width_rate = top_bin(width_index)
    count_rows, count_rate = top_bin(count_index)
    return {
        "bins": bins,
        "equal_width_edges": [round(float(e), 2) for e in width_edges],
        "equal_count_edges": [round(float(e), 2) for e in count_edges],
        "equal_width_top_bin_rows": width_rows,
        "equal_count_top_bin_rows": count_rows,
        "equal_width_top_bin_rate": width_rate,
        "equal_count_top_bin_rate": count_rate,
        "rows": int(len(values)),
    }


# --- 9. the audit ----------------------------------------------------------


def audit_table() -> pd.DataFrame:
    """The signups table plus one categorical leak and one honest column."""
    frame = data.signups().copy()
    rng = np.random.default_rng(data.SEED + 9)
    converted = frame["converted"].to_numpy()
    frame["email_template"] = pd.Series(
        np.where(converted == 1, "welcome_pack", "abandoned_cart"), dtype="str"
    )
    frame["channel"] = pd.Series(
        rng.choice(["search", "social", "direct"], len(frame)), dtype="str"
    )
    return frame


def audit_result(corr_threshold: float = 0.90) -> dict[str, object]:
    frame = audit_table()
    flags = F.leakage_audit(frame, "converted", corr_threshold=corr_threshold)
    return {
        "flagged": [f.column for f in flags],
        "rules": {f.column: f.rule for f in flags},
        "details": {f.column: f.detail for f in flags},
        "columns_checked": [c for c in frame.columns if c != "converted"],
    }
