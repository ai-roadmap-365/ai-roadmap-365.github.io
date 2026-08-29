"""Twelve exercises in the three kinds of feedback a learner can be given.

Read `00_brief.md` first. Each function below is a `pytest.skip` naming
exactly what to build and what to assert; replace the skip with real code.
`feedback_lib.py` is complete -- it is the machinery, not the exercise.

Run this suite on its own:

    .venv/bin/pytest starter -q

Never run `pytest starter examples` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import numpy as np  # noqa: F401  (you will need it)
import pytest

import feedback_lib as f  # noqa: F401  (you will need it)


@pytest.fixture(scope="module")
def iris():
    return f.iris_features_and_labels()


def test_01_supervised_learning_has_a_per_example_answer(iris):
    pytest.skip(
        "Split iris with f.split_indices(150, 100, seed=142). Score a "
        "5-NN with f.supervised_score and assert it is exactly 0.92. Then "
        "assert the training half really carries 100 answers and that all "
        "three species appear in it. The point is not the score: it is "
        "that an answer exists for every single training row."
    )


def test_02_cluster_ids_are_arbitrary_and_raw_accuracy_is_meaningless(iris):
    pytest.skip(
        "Cluster iris with f.cluster(X, 3, seed=0). Compare the cluster "
        "ids to the species with f.raw_cluster_accuracy -- assert 0.24. "
        "Then use f.best_permutation_accuracy and assert 0.8933333333333333 "
        "with mapping (1, 0, 2). Assert the gap is 0.6533. Both numbers "
        "describe the identical partition; only the numbering differs."
    )


def test_03_kmeans_isolates_one_species_and_blends_two(iris):
    pytest.skip(
        "Build f.cluster_confusion(y, assignment, 3, 3) for the same "
        "clustering. Assert the three rows are [0, 50, 0], [48, 0, 2] and "
        "[14, 0, 36]. Say in a comment which species k-means separated "
        "perfectly and which two it could not tell apart -- and note that "
        "you needed the labels to find that out."
    )


def test_04_standardising_changes_the_clustering_and_here_makes_it_worse(iris):
    pytest.skip(
        "Cluster raw iris and f.standardise(X) at k=3, seed=0. Assert "
        "f.agreement between the two clusterings is 0.8036117420390129. "
        "Assert agreement with the true species is 0.7302382722834697 raw "
        "and 0.6201351808870379 scaled, then assert scaled < raw. The "
        "textbook advice loses on this dataset; report what you measured."
    )


def test_05_inertia_cannot_choose_k_and_silhouette_chooses_the_wrong_one(iris):
    pytest.skip(
        "For ks = [2, 3, 4, 5, 6] assert f.inertia_curve rounds to "
        "[152.348, 78.851, 57.228, 46.446, 39.04] and is strictly "
        "decreasing -- so minimising it always answers k = n. Assert "
        "f.silhouette_curve rounds to [0.681, 0.5528, 0.4981, 0.4887, "
        "0.3648] and that its argmax is k=2, not the 3 species iris has."
    )


def test_06_greedy_locks_on_and_epsilon_greedy_does_not():
    pytest.skip(
        "Run f.average_bandit(runs=200, k=10, steps=1000, epsilon=e) for "
        "e in (0.0, 0.01, 0.1). Assert mean rewards 0.9838, 1.1314, 1.28 "
        "and optimal-action rates 0.313, 0.4336, 0.708. Assert the gap "
        "between epsilon=0.1 and greedy is 0.3949, and that reward rises "
        "with epsilon across all three."
    )


def test_06b_a_bandit_only_ever_reveals_the_arm_you_pulled():
    pytest.skip(
        "Create f.GaussianBandit(k=10, seed=3). Call pull(0) and assert "
        "you got back one float. Then call full_feedback() and assert it "
        "has shape (10,). Write a comment naming what full_feedback() "
        "represents and why no real agent is ever handed it."
    )


def test_07_argmax_tie_breaking_decides_whether_the_agent_learns_at_all():
    pytest.skip(
        "On f.GridWorld(5) (shortest path 8), run f.q_learning for 300 "
        "episodes at seed 0 twice: break_ties_randomly=False and True. "
        "Assert the first reaches the goal in 0 of 300 episodes and the "
        "second in 300 of 300. For the second assert mean episode length "
        "46.8 over the first ten and 10.4 over the last ten, and that "
        "f.greedy_path_length is exactly 8."
    )


def test_07b_the_reward_travels_backwards_one_state_per_episode():
    pytest.skip(
        "Call f.value_spread_by_episode(world, [1, 2, 3, 5, 10, 25, 50, "
        "100, 300]). Assert the valued-state counts for the first five "
        "entries are [1, 2, 3, 5, 10] -- exactly one new state per "
        "episode. Assert 18, 20, 21 and 22 for 25, 50, 100 and 300. "
        "Assert the greedy path is still unreachable at 10 episodes and "
        "is 8 steps at 25."
    )


def test_08_a_log_records_only_what_the_logging_policy_chose():
    pytest.skip(
        "Call f.logged_policy_dataset(k=10, steps=2000, epsilon=0.1, "
        "seed=0). Assert the best arm is 6 and that it was pulled 1813 of "
        "2000 times, that the other nine arms share 187 pulls, and that "
        "the busiest of those nine has only 30. That imbalance is not a "
        "flaw in the log; it is what a good policy produces."
    )


def test_08b_a_greedy_log_confirms_whatever_it_locked_onto():
    pytest.skip(
        "Call f.log_verdicts(range(8), epsilon=0.0). Assert 5 of the 8 "
        "logs name the wrong arm and 4 contain exactly one arm (seeds 1, "
        "2, 3 and 6, all arm 0). Then call it with epsilon=0.1: assert "
        "all 8 logs contain all 10 arms, that 7 of 8 are now correct, and "
        "that the one failure is (1, 10, 1, 4, False)."
    )


def test_08c_the_winners_curse_is_why_the_explored_log_still_gets_one_wrong():
    pytest.skip(
        "For seed 1 at epsilon=0.1: assert the true best arm is 4 with "
        "true mean 0.9054 and 1524 pulls, and that arm 1 has true mean "
        "0.8216 and 274 pulls. Assert the logged means are 0.8634 and "
        "0.9262. Assert arm 4 is under-estimated and arm 1 over-estimated, "
        "and that f.logged_best_arm therefore returns 1. An argmax over "
        "noisy estimates favours the most inflated one. Remember this."
    )


def test_09_three_chosen_labels_are_worth_about_nine_random_ones(iris):
    pytest.skip(
        "Assert f.average_label_budget_curve(X, y, [3, 5, 10, 20, 50], "
        "repeats=40) rounds to [0.6455, 0.778, 0.896, 0.924, 0.947] and "
        "is strictly increasing, while the single-seed 142 curve is [0.64, "
        "0.92, 0.92, 0.86, 0.96] and is NOT. Assert "
        "f.average_cluster_then_label(X, y, 3, repeats=40) is 0.876, that "
        "it beats three random labels by 0.2305, that it sits between the "
        "5- and 10-label figures, and that it stays under the 0.9535 "
        "ceiling from f.average_full_supervision."
    )


def test_10_the_deciding_question_is_whether_your_actions_change_the_data():
    pytest.skip(
        "Run f.classify_problem on all four combinations built by "
        "f.problem: (labels, inert, immediate), (no labels, inert, "
        "immediate), (labels, actions change data, immediate) and "
        "(labels, actions change data, delayed). Assert the four verdicts "
        "are 'supervised learning', 'unsupervised learning', "
        "'reinforcement learning: contextual bandit' and 'reinforcement "
        "learning: sequential, with delayed credit', and that all four "
        "are distinct. Having labels did not make the third one supervised."
    )


def test_10b_an_incomplete_problem_description_is_refused():
    pytest.skip(
        "Assert f.classify_problem({'has_labels': True}) raises KeyError. "
        "A function that guesses at a missing field is worse than one "
        "that refuses, because the guess is invisible in the output."
    )
