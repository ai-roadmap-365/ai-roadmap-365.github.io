"""The reference solutions: what the workflow is, and what its order costs.

Every number here was captured from a real run of this file on the
authoring machine. If a number changes, the claim in the lesson is wrong
and one of the two must be fixed.
"""

import numpy as np
import pytest

import workflow_lib as w


@pytest.fixture(scope="module")
def noise():
    return w.noise_dataset()


@pytest.fixture(scope="module")
def imbalanced():
    return w.imbalanced_dataset(1000, 11), w.imbalanced_dataset(2000, 12)


# --- 1. The workflow is stages with contracts, not boxes with arrows ------


def test_01_the_honest_pipeline_runs_in_the_declared_order():
    result = w.run_pipeline(w.honest_stages(), w.starting_artifact())
    assert [name for name, _keys in result.log] == [
        "load",
        "split",
        "select",
        "fit_and_score",
        "baseline",
    ]
    # Each stage recorded exactly the keys it declared it would produce.
    produced = dict(result.log)
    assert produced["load"] == ("X", "y")
    assert produced["split"] == ("folds",)
    assert produced["select"] == ("selected",)
    assert produced["fit_and_score"] == ("fold_scores", "score")
    assert produced["baseline"] == ("baseline",)


def test_01b_a_stage_never_mutates_the_artifact_it_was_given():
    start = w.starting_artifact()
    before = set(start.data)
    w.run_pipeline(w.honest_stages(), start)
    # The starting artifact is untouched: every stage returned a new one.
    assert set(start.data) == before
    assert start.log == []


# --- 2. The honest pipeline reports chance on data that is chance --------


def test_02_the_honest_pipeline_reports_chance_on_pure_noise():
    result = w.run_pipeline(w.honest_stages(), w.starting_artifact())
    assert result.data["score"] == 0.5
    assert result.data["baseline"] == 0.54
    assert result.data["fold_scores"].shape == (5,)
    # Labels are coin flips, so chance is the only honest answer.
    assert abs(result.data["score"] - 0.5) < 0.01


# --- 3. The same stages in the wrong order, and what a contract is for ---


def test_03_reordering_two_stages_invents_twenty_three_accuracy_points():
    honest = w.run_pipeline(w.honest_stages(), w.starting_artifact())
    leaky = w.run_pipeline(w.leaky_stages(), w.starting_artifact(), enforce_contracts=False)
    assert honest.data["score"] == 0.5
    assert leaky.data["score"] == 0.73
    assert round(leaky.data["score"] - honest.data["score"], 4) == 0.23
    # The step logs differ by one transposition and nothing else.
    assert [n for n, _ in honest.log] == ["load", "split", "select", "fit_and_score", "baseline"]
    assert [n for n, _ in leaky.log] == ["load", "select", "split", "fit_and_score", "baseline"]


def test_03b_the_contract_turns_a_silent_lie_into_a_named_failure():
    with pytest.raises(w.StageContractError) as excinfo:
        w.run_pipeline(w.leaky_stages(), w.starting_artifact(), enforce_contracts=True)
    message = str(excinfo.value)
    assert "'select'" in message
    assert "folds" in message
    # The honest pipeline passes the same contracts without complaint.
    ok = w.run_pipeline(w.honest_stages(), w.starting_artifact(), enforce_contracts=True)
    assert ok.data["score"] == 0.5


def test_03c_the_inflation_grows_with_the_number_of_features_chosen(noise):
    X, y = noise
    rows = w.inflation_by_k(X, y, [5, 10, 20, 50])
    assert rows == [
        (5, 0.65, 0.39, 0.26),
        (10, 0.72, 0.5, 0.22),
        (20, 0.73, 0.5, 0.23),
        (50, 0.85, 0.38, 0.47),
    ]
    # Every wrong-order score beats its honest counterpart, at every k.
    assert all(wrong > right for _k, wrong, right, _gap in rows)
    # And the honest scores stay at or below chance, as they must.
    assert all(right <= 0.5 for _k, _wrong, right, _gap in rows)


# --- 4. The metric is chosen before the model, and it decides ------------


def test_04_the_metric_you_choose_decides_which_model_you_ship(imbalanced):
    (X_train, y_train), (X_test, y_test) = imbalanced
    scores = w.score_all(w.candidate_models(), X_train, y_train, X_test, y_test)
    assert scores["majority baseline"] == {
        "accuracy": 0.92,
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
    }
    assert scores["logistic (default threshold)"]["accuracy"] == 0.9435
    assert scores["logistic (default threshold)"]["recall"] == 0.4813
    assert scores["logistic (balanced)"]["accuracy"] == 0.8685
    assert scores["logistic (balanced)"]["recall"] == 0.8438
    # The decision inverts on the metric, with nothing else changing.
    assert w.winner(scores, "accuracy") == "logistic (default threshold)"
    assert w.winner(scores, "recall") == "logistic (balanced)"
    assert w.winner(scores, "accuracy") != w.winner(scores, "recall")


def test_04b_a_model_that_never_predicts_the_positive_class_scores_ninety_two(
    imbalanced,
):
    (X_train, y_train), (X_test, y_test) = imbalanced
    scores = w.score_all(w.candidate_models(), X_train, y_train, X_test, y_test)
    baseline = scores["majority baseline"]
    assert baseline["accuracy"] == 0.92 and baseline["recall"] == 0.0
    beats = {
        name: s["accuracy"]
        for name, s in scores.items()
        if s["accuracy"] > baseline["accuracy"]
    }
    # Three of the four real models beat a constant -- by at most 2.35 points.
    assert set(beats) == {"logistic (default threshold)", "5-NN", "depth-3 tree"}
    assert round(max(beats.values()) - baseline["accuracy"], 4) == 0.0235
    # And the one that actually finds positives is the one that loses here.
    assert scores["logistic (balanced)"]["accuracy"] < baseline["accuracy"]
    assert scores["logistic (balanced)"]["recall"] == 0.8438
    assert int(y_test.sum()) == 160 and len(y_test) == 2000


# --- 5. Error analysis is a stage, not an afterthought ------------------


def test_05_the_confusion_matrix_says_what_the_accuracy_hides(imbalanced):
    (X_train, y_train), (X_test, y_test) = imbalanced
    model = w.candidate_models()["logistic (default threshold)"]
    model.fit(X_train, y_train)
    table = w.error_table(model, X_test, y_test)
    assert table == [[1810, 30], [83, 77]]
    true_negative, false_positive = table[0]
    false_negative, true_positive = table[1]
    assert true_negative + false_positive + false_negative + true_positive == 2000
    # 94.35% accurate, and it misses more positives than it catches.
    assert false_negative > true_positive
    assert round((true_negative + true_positive) / 2000, 4) == 0.9435


# --- 6. Reproducibility: the same inputs must give the same artifact ----


def test_06_two_runs_of_the_pipeline_are_byte_identical():
    keys = ("X", "y", "fold_scores", "score")
    first = w.manifest(w.run_pipeline(w.honest_stages(), w.starting_artifact()), keys)
    second = w.manifest(w.run_pipeline(w.honest_stages(), w.starting_artifact()), keys)
    assert first == second
    assert first == {
        "X": "51b0a421bd652dd2",
        "fold_scores": "8f0ac332958b9bc4",
        "score": "d2cbad71ff333de6",
        "y": "9984503b5352c5a1",
    }


def test_06b_a_different_seed_produces_a_different_manifest():
    keys = ("X", "y", "fold_scores", "score")
    first = w.manifest(w.run_pipeline(w.honest_stages(), w.starting_artifact()), keys)
    other = w.manifest(
        w.run_pipeline(w.honest_stages(), w.starting_artifact(seed=144)), keys
    )
    assert first != other
    # A manifest that never changes is not evidence of determinism.
    assert first["X"] != other["X"]


# --- 7. The modelling stage is the small one ---------------------------


def test_07_the_modelling_stage_is_the_smallest_part_of_the_pipeline():
    lines = w.stage_source_lines(w.honest_stages())
    assert lines == {"load": 5, "split": 2, "select": 10, "fit_and_score": 9, "baseline": 4}
    total = sum(lines.values())
    assert total == 30
    assert round(lines["fit_and_score"] / total, 4) == 0.3
    # And this pipeline has no cleaning, no monitoring and no deployment
    # stage at all -- so 30% is an upper bound, not an estimate.
    assert set(lines) == {"load", "split", "select", "fit_and_score", "baseline"}
    assert "clean" not in lines and "monitor" not in lines and "deploy" not in lines


# --- 8. A missing input is caught before it becomes a wrong number ------


def test_08_a_stage_cannot_run_without_the_inputs_it_declared():
    stages = w.honest_stages()
    empty = w.Artifact(data={})
    with pytest.raises(w.StageContractError) as excinfo:
        w.run_pipeline(stages, empty)
    assert "'load'" in str(excinfo.value)
    # With contracts off it fails too -- but as a KeyError deep inside the
    # stage, naming a dictionary key rather than the stage that broke.
    with pytest.raises(KeyError):
        w.run_pipeline(stages, empty, enforce_contracts=False)
