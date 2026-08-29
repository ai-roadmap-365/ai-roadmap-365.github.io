"""Thirteen exercises in what the machine learning workflow actually is.

Read `00_brief.md` first. Each function below is a `pytest.skip` naming
exactly what to build and what to assert; replace the skip with real code.
`workflow_lib.py` is complete -- it is the machinery, not the exercise.

Run this suite on its own:

    .venv/bin/pytest starter -q

Never run `pytest starter examples` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import numpy as np  # noqa: F401  (you will need it)
import pytest

import workflow_lib as w  # noqa: F401  (you will need it)


@pytest.fixture(scope="module")
def noise():
    return w.noise_dataset()


@pytest.fixture(scope="module")
def imbalanced():
    return w.imbalanced_dataset(1000, 11), w.imbalanced_dataset(2000, 12)


def test_01_the_honest_pipeline_runs_in_the_declared_order():
    pytest.skip(
        "Run w.run_pipeline(w.honest_stages(), w.starting_artifact()). Assert "
        "the stage names in result.log are load, split, select, fit_and_score, "
        "baseline in that order, and that each stage recorded exactly the keys "
        "it declared: load -> ('X', 'y'), split -> ('folds',), select -> "
        "('selected',), fit_and_score -> ('fold_scores', 'score'), baseline -> "
        "('baseline',)."
    )


def test_01b_a_stage_never_mutates_the_artifact_it_was_given():
    pytest.skip(
        "Capture set(start.data) before running the pipeline, run it, and "
        "assert the starting artifact's keys and empty log are unchanged. A "
        "stage that mutates its input makes the step log a work of fiction, "
        "because the log then describes states that no longer exist."
    )


def test_02_the_honest_pipeline_reports_chance_on_pure_noise():
    pytest.skip(
        "Assert the honest pipeline's score is exactly 0.5, its baseline is "
        "0.54, and fold_scores has shape (5,). The labels in noise_dataset "
        "are coin flips, so chance is the only honest answer -- and note the "
        "baseline of 0.54 is above 0.5 because 100 coin flips do not land "
        "exactly fifty-fifty."
    )


def test_03_reordering_two_stages_invents_twenty_three_accuracy_points():
    pytest.skip(
        "Run the honest pipeline, then run w.leaky_stages() with "
        "enforce_contracts=False. Assert the scores are 0.5 and 0.73 and that "
        "the difference is 0.23. Then assert the two step logs differ by "
        "exactly one transposition: select and split have swapped places and "
        "nothing else changed. Same data, same model, same folds."
    )


def test_03b_the_contract_turns_a_silent_lie_into_a_named_failure():
    pytest.skip(
        "Run w.leaky_stages() with enforce_contracts=True inside "
        "pytest.raises(w.StageContractError). Assert the message names the "
        "stage 'select' and the missing key 'folds'. Then assert the honest "
        "pipeline passes the very same contracts and still scores 0.5."
    )


def test_03c_the_inflation_grows_with_the_number_of_features_chosen(noise):
    pytest.skip(
        "Assert w.inflation_by_k(X, y, [5, 10, 20, 50]) equals [(5, 0.65, "
        "0.39, 0.26), (10, 0.72, 0.5, 0.22), (20, 0.73, 0.5, 0.23), (50, "
        "0.85, 0.38, 0.47)]. Then assert the structural facts that hold "
        "regardless of the numbers: every wrong-order score beats its honest "
        "counterpart, and every honest score is at or below chance."
    )


def test_04_the_metric_you_choose_decides_which_model_you_ship(imbalanced):
    pytest.skip(
        "Score w.candidate_models() with w.score_all. Assert the majority "
        "baseline is accuracy 0.92 with recall 0.0, that logistic at the "
        "default threshold is 0.9435 accuracy and 0.4813 recall, and that "
        "logistic balanced is 0.8685 accuracy and 0.8438 recall. Then assert "
        "w.winner picks 'logistic (default threshold)' on accuracy and "
        "'logistic (balanced)' on recall -- the decision inverts, with "
        "nothing changing but the metric."
    )


def test_04b_a_model_that_never_predicts_the_positive_class_scores_ninety_two(imbalanced):
    pytest.skip(
        "Assert the majority baseline scores 0.92 accuracy and 0.0 recall. "
        "Collect the models that beat 0.92 accuracy and assert the set is "
        "exactly logistic (default threshold), 5-NN and depth-3 tree, and "
        "that the best of them beats the constant by only 0.0235. Then "
        "assert the one model that actually finds positives -- logistic "
        "balanced, recall 0.8438 -- scores WORSE than the constant. Assert "
        "the test set carries 160 positives in 2000 rows."
    )


def test_05_the_confusion_matrix_says_what_the_accuracy_hides(imbalanced):
    pytest.skip(
        "Fit logistic at the default threshold and assert w.error_table is "
        "[[1810, 30], [83, 77]]. Assert the four cells sum to 2000, that the "
        "false negatives (83) exceed the true positives (77), and that the "
        "accuracy recomputed from the table is 0.9435. A model can be 94 "
        "percent accurate and miss more of the thing you care about than it "
        "finds."
    )


def test_06_two_runs_of_the_pipeline_are_byte_identical():
    pytest.skip(
        "Build w.manifest over ('X', 'y', 'fold_scores', 'score') for two "
        "separate runs at seed 143 and assert they are equal. Assert the "
        "manifest is {'X': '51b0a421bd652dd2', 'fold_scores': "
        "'8f0ac332958b9bc4', 'score': 'd2cbad71ff333de6', 'y': "
        "'9984503b5352c5a1'}. A pipeline that cannot prove it produced the "
        "same thing twice cannot be debugged."
    )


def test_06b_a_different_seed_produces_a_different_manifest():
    pytest.skip(
        "Compare the seed 143 manifest against a seed 144 one and assert "
        "they differ, including on the 'X' key specifically. This is the "
        "control: a manifest that never changes is not evidence of "
        "determinism, it is evidence that you are hashing a constant."
    )


def test_07_the_modelling_stage_is_the_smallest_part_of_the_pipeline():
    pytest.skip(
        "Assert w.stage_source_lines(w.honest_stages()) is {'load': 5, "
        "'split': 2, 'select': 10, 'fit_and_score': 9, 'baseline': 4}, "
        "totalling 30, and that fit_and_score is 30 percent of it. Then "
        "assert what is NOT in that dict: no cleaning stage, no monitoring "
        "stage, no deployment stage. That is why 30 percent is an upper "
        "bound and not an estimate."
    )


def test_08_a_stage_cannot_run_without_the_inputs_it_declared():
    pytest.skip(
        "Run the honest pipeline against an empty w.Artifact(data={}) inside "
        "pytest.raises(w.StageContractError) and assert the message names "
        "'load'. Then run the same thing with enforce_contracts=False and "
        "assert it raises KeyError instead. Both fail; only one tells you "
        "which stage broke."
    )
