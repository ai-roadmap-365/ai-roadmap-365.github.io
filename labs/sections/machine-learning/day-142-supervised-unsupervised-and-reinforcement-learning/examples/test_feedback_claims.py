"""The reference solutions: ten claims about the three kinds of feedback.

Every number here was captured from a real run of this file on the
authoring machine. If a number changes, the claim in the lesson is wrong
and one of the two must be fixed.
"""

import numpy as np
import pytest

import feedback_lib as f


@pytest.fixture(scope="module")
def iris():
    return f.iris_features_and_labels()


# --- 1. Supervised: the answer key is in the data -------------------------


def test_01_supervised_learning_has_a_per_example_answer(iris):
    X, y = iris
    train, test = f.split_indices(len(y), 100, seed=142)
    score = f.supervised_score(X, y, train, test, n_neighbors=5)
    assert score == 0.92
    # The defining property: every training row carries its own answer.
    assert len(y[train]) == 100
    assert set(np.unique(y[train]).tolist()) == {0, 1, 2}


# --- 2. Unsupervised: cluster numbers mean nothing -------------------------


def test_02_cluster_ids_are_arbitrary_and_raw_accuracy_is_meaningless(iris):
    X, y = iris
    assignment = f.cluster(X, 3, seed=0).labels_
    raw = f.raw_cluster_accuracy(y, assignment)
    best, mapping = f.best_permutation_accuracy(y, assignment)
    assert raw == 0.24
    assert best == pytest.approx(0.8933333333333333)
    assert mapping == (1, 0, 2)
    # Sixty-five accuracy points separate the same clustering from itself.
    assert round(best - raw, 4) == 0.6533


# --- 3. What k-means actually found on iris -------------------------------


def test_03_kmeans_isolates_one_species_and_blends_two(iris):
    X, y = iris
    assignment = f.cluster(X, 3, seed=0).labels_
    table = f.cluster_confusion(y, assignment, 3, 3)
    # Setosa lands entirely in one cluster; the other two species do not.
    assert table[0].tolist() == [0, 50, 0]
    assert table[1].tolist() == [48, 0, 2]
    assert table[2].tolist() == [14, 0, 36]
    assert int(table[0].max()) == 50
    assert int(table[1].max()) == 48 and int(table[2].max()) == 36


# --- 4. Structure is not unique -------------------------------------------


def test_04_standardising_changes_the_clustering_and_here_makes_it_worse(iris):
    X, y = iris
    raw_assignment = f.cluster(X, 3, seed=0).labels_
    scaled_assignment = f.cluster(f.standardise(X), 3, seed=0).labels_
    assert f.agreement(raw_assignment, scaled_assignment) == pytest.approx(0.8036117420390129)
    raw_vs_truth = f.agreement(y, raw_assignment)
    scaled_vs_truth = f.agreement(y, scaled_assignment)
    assert raw_vs_truth == pytest.approx(0.7302382722834697)
    assert scaled_vs_truth == pytest.approx(0.6201351808870379)
    # The folklore says always standardise. On this dataset it loses ground.
    assert scaled_vs_truth < raw_vs_truth


# --- 5. k is a choice, not a discovery ------------------------------------


def test_05_inertia_cannot_choose_k_and_silhouette_chooses_the_wrong_one(iris):
    X, _y = iris
    ks = [2, 3, 4, 5, 6]
    inertia = f.inertia_curve(X, ks)
    # Inertia falls monotonically, so "minimise inertia" always answers k = n.
    assert all(a > b for a, b in zip(inertia, inertia[1:]))
    assert [round(v, 3) for v in inertia] == [152.348, 78.851, 57.228, 46.446, 39.04]
    silhouette = f.silhouette_curve(X, ks)
    assert [round(v, 4) for v in silhouette] == [0.681, 0.5528, 0.4981, 0.4887, 0.3648]
    # The best silhouette is at k = 2. Iris has three species.
    assert ks[int(np.argmax(silhouette))] == 2


# --- 6. Reinforcement: evaluative feedback and the cost of not exploring ---


def test_06_greedy_locks_on_and_epsilon_greedy_does_not():
    greedy_reward, greedy_optimal = f.average_bandit(runs=200, k=10, steps=1000, epsilon=0.0)
    small_reward, small_optimal = f.average_bandit(runs=200, k=10, steps=1000, epsilon=0.01)
    explore_reward, explore_optimal = f.average_bandit(runs=200, k=10, steps=1000, epsilon=0.1)
    assert round(greedy_reward, 4) == 0.9838
    assert round(greedy_optimal, 4) == 0.313
    assert round(small_reward, 4) == 1.1314
    assert round(small_optimal, 4) == 0.4336
    assert round(explore_reward, 4) == 1.28
    assert round(explore_optimal, 4) == 0.708
    # Never exploring costs 39.49 points of optimal-action rate.
    assert round(explore_optimal - greedy_optimal, 4) == 0.3949
    assert explore_reward > small_reward > greedy_reward


def test_06b_a_bandit_only_ever_reveals_the_arm_you_pulled():
    bandit = f.GaussianBandit(k=10, seed=3)
    reward = bandit.pull(0)
    assert isinstance(reward, float)
    # There is no method that returns the reward you would have got from
    # another arm on that same pull -- except the one this lab added
    # purely so the missing information can be named.
    full = bandit.full_feedback()
    assert full.shape == (10,)


# --- 7. Delayed feedback, credit assignment, and one silent bug -----------


def test_07_argmax_tie_breaking_decides_whether_the_agent_learns_at_all():
    world = f.GridWorld(5)
    assert world.shortest_path_length() == 8

    _q_bad, lengths_bad, reached_bad = f.q_learning(
        world, episodes=300, seed=0, break_ties_randomly=False
    )
    assert reached_bad == 0
    assert lengths_bad[0] == 200 and lengths_bad[-1] == 200

    q_good, lengths_good, reached_good = f.q_learning(
        world, episodes=300, seed=0, break_ties_randomly=True
    )
    assert reached_good == 300
    assert round(float(np.mean(lengths_good[:10])), 1) == 46.8
    assert round(float(np.mean(lengths_good[-10:])), 1) == 10.4
    # With no exploration at all, the learned policy walks the shortest path.
    assert f.greedy_path_length(world, q_good) == 8


def test_07b_the_reward_travels_backwards_one_state_per_episode():
    world = f.GridWorld(5)
    rows = f.value_spread_by_episode(world, [1, 2, 3, 5, 10, 25, 50, 100, 300], seed=0)
    reached = {n: states for n, states, _path in rows}
    assert [reached[n] for n in (1, 2, 3, 5, 10)] == [1, 2, 3, 5, 10]
    assert reached[25] == 18 and reached[50] == 20
    assert reached[100] == 21 and reached[300] == 22
    paths = {n: path for n, _states, path in rows}
    # Before episode 25 the greedy policy cannot reach the goal at all.
    assert paths[10] == 200 and paths[25] == 8


# --- 8. Logged bandit data is not a supervised dataset --------------------


def test_08_a_log_records_only_what_the_logging_policy_chose():
    arms, _rewards, best, counts = f.logged_policy_dataset(
        k=10, steps=2000, epsilon=0.1, seed=0
    )
    pulls = f.arm_pull_counts(counts)
    assert best == 6
    assert pulls[6] == 1813
    assert sum(pulls.values()) == 2000
    # Nine arms share 187 pulls between them; none has enough data to judge.
    assert sum(v for a, v in pulls.items() if a != 6) == 187
    assert max(v for a, v in pulls.items() if a != 6) == 30
    assert len(arms) == 2000


def test_08b_a_greedy_log_confirms_whatever_it_locked_onto():
    verdicts = f.log_verdicts(range(8), epsilon=0.0)
    correct = [row for row in verdicts if row[4]]
    wrong = [row for row in verdicts if not row[4]]
    assert len(verdicts) == 8
    assert len(wrong) == 5 and len(correct) == 3
    # Four of the eight logs contain exactly one arm: the log cannot even
    # represent the question a supervised model would be asked.
    single_arm = [row for row in verdicts if row[1] == 1]
    assert len(single_arm) == 4
    assert all(row[2] == 0 for row in single_arm)
    assert [row[0] for row in single_arm] == [1, 2, 3, 6]

    explored = f.log_verdicts(range(8), epsilon=0.1)
    assert all(row[1] == 10 for row in explored)
    # Exploring more than doubles the hit rate -- and still gets one wrong.
    assert sum(1 for row in explored if row[4]) == 7
    assert [row for row in explored if not row[4]] == [(1, 10, 1, 4, False)]


def test_08c_the_winners_curse_is_why_the_explored_log_still_gets_one_wrong():
    """Seed 1 loses to an arm with a twentieth of the data, on purpose.

    The logging policy pulled the genuinely best arm 1524 times and a
    slightly worse arm 274 times. More data made the good arm's estimate
    *more accurate* -- and so it came in slightly under its true mean,
    while the thinly-sampled arm came in over. Taking an argmax over noisy
    estimates systematically favours whichever estimate is most inflated.
    Day 144 measures this same effect as model-selection bias.
    """
    arms, rewards, best, counts = f.logged_policy_dataset(
        k=10, steps=2000, epsilon=0.1, seed=1
    )
    bandit = f.GaussianBandit(k=10, seed=1)
    means = f.logged_arm_means(arms, rewards)
    assert best == 4
    assert int(counts[4]) == 1524 and int(counts[1]) == 274
    assert round(float(bandit.means[4]), 4) == 0.9054
    assert round(float(bandit.means[1]), 4) == 0.8216
    assert round(means[4], 4) == 0.8634
    assert round(means[1], 4) == 0.9262
    # The better arm is under-estimated; the worse arm is over-estimated.
    assert means[4] < float(bandit.means[4])
    assert means[1] > float(bandit.means[1])
    assert f.logged_best_arm(arms, rewards) == 1


# --- 9. Unsupervised learning buying supervised learning cheaper ----------


def test_09_three_chosen_labels_are_worth_about_nine_random_ones(iris):
    X, y = iris
    budgets = [3, 5, 10, 20, 50]
    curve = f.average_label_budget_curve(X, y, budgets, repeats=40)
    assert [round(v, 4) for v in curve] == [0.6455, 0.778, 0.896, 0.924, 0.947]
    # Averaging is not decoration: a single split is not even monotone.
    single = f.label_budget_curve(X, y, budgets, seed=142)
    assert single == [0.64, 0.92, 0.92, 0.86, 0.96]
    assert not all(a <= b for a, b in zip(single, single[1:]))
    assert all(a < b for a, b in zip(curve, curve[1:]))

    chosen = f.average_cluster_then_label(X, y, 3, repeats=40)
    assert round(chosen, 4) == 0.876
    # Same budget of three labels, 23 accuracy points better.
    assert round(chosen - curve[0], 4) == 0.2305
    # And it lands between five and ten randomly chosen labels.
    assert curve[1] < chosen < curve[2]
    ceiling = f.average_full_supervision(X, y, repeats=40)
    assert round(ceiling, 4) == 0.9535
    assert chosen < ceiling


# --- 10. Naming the setting before choosing the algorithm -----------------


def test_10_the_deciding_question_is_whether_your_actions_change_the_data():
    supervised = f.classify_problem(
        f.problem(has_labels=True, actions_change_the_data=False, feedback_is_immediate=True)
    )
    unsupervised = f.classify_problem(
        f.problem(has_labels=False, actions_change_the_data=False, feedback_is_immediate=True)
    )
    bandit = f.classify_problem(
        f.problem(has_labels=True, actions_change_the_data=True, feedback_is_immediate=True)
    )
    sequential = f.classify_problem(
        f.problem(has_labels=True, actions_change_the_data=True, feedback_is_immediate=False)
    )
    assert supervised == "supervised learning"
    assert unsupervised == "unsupervised learning"
    assert bandit == "reinforcement learning: contextual bandit"
    assert sequential == "reinforcement learning: sequential, with delayed credit"
    # Having labels does not make a problem supervised.
    assert bandit != supervised
    assert len({supervised, unsupervised, bandit, sequential}) == 4


def test_10b_an_incomplete_problem_description_is_refused():
    with pytest.raises(KeyError):
        f.classify_problem({"has_labels": True})
