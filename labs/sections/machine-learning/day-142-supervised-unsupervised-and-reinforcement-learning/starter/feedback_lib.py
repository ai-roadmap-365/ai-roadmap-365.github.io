"""Three kinds of feedback, built from scratch and measured.

The taxonomy in this lesson is not a taxonomy of algorithms. It is a
taxonomy of the *feedback signal* a learner is given:

* supervised   -- instructive feedback: for every input you are told the
                  correct output, so the error is defined per example;
* unsupervised -- no feedback at all: there is no correct output, only
                  structure, and structure is not unique;
* reinforcement -- evaluative and delayed feedback: you are told how good
                  the action you took was, never what the best action
                  would have been, and often only much later.

Everything here is deterministic given a seed. The bandit and the
gridworld are written from first principles in NumPy so that the shape of
each feedback signal is visible in the code rather than hidden inside a
library.
"""

from __future__ import annotations

import numpy as np
from itertools import permutations

from sklearn.cluster import KMeans
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

# --------------------------------------------------------------------------
# Shared helpers
# --------------------------------------------------------------------------


def iris_features_and_labels():
    """The iris measurements and the species column, as plain arrays."""
    return load_iris(return_X_y=True)


def accuracy(y_true, y_pred) -> float:
    """Fraction of positions where two label arrays agree."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float(np.mean(y_true == y_pred))


def standardise(X):
    """Centre each column at zero and scale it to unit variance."""
    return StandardScaler().fit_transform(X)


# --------------------------------------------------------------------------
# 1. Supervised: instructive feedback
# --------------------------------------------------------------------------


def supervised_score(X, y, train_idx, test_idx, n_neighbors: int = 5) -> float:
    """Fit a k-NN on the training rows and score it on the held-out rows.

    This is the whole shape of supervised learning: every training row
    carries its own answer, so the learner can measure and reduce a
    per-example error.
    """
    model = KNeighborsClassifier(n_neighbors=n_neighbors)
    model.fit(X[train_idx], y[train_idx])
    return accuracy(y[test_idx], model.predict(X[test_idx]))


def split_indices(n: int, n_train: int, seed: int):
    """A deterministic random split of range(n) into train and test halves."""
    order = np.random.default_rng(seed).permutation(n)
    return order[:n_train], order[n_train:]


# --------------------------------------------------------------------------
# 2-5. Unsupervised: no feedback at all
# --------------------------------------------------------------------------


def cluster(X, k: int, seed: int = 0):
    """k-means with a fixed seed and a fixed number of restarts."""
    return KMeans(n_clusters=k, n_init=10, random_state=seed).fit(X)


def raw_cluster_accuracy(y_true, cluster_ids) -> float:
    """Compare cluster ids to true labels as if the ids meant something.

    They do not. k-means numbers its clusters by where its own centroids
    happened to land, so this figure is an artefact of the numbering.
    """
    return accuracy(y_true, cluster_ids)


def best_permutation_accuracy(y_true, cluster_ids):
    """The honest version: try every relabelling and keep the best.

    Returns ``(accuracy, mapping)`` where ``mapping[i]`` is the true label
    assigned to cluster ``i``. This is the number people *mean* when they
    say a clustering "recovered the classes", and computing it requires
    the labels -- which unsupervised learning, by definition, does not
    have.
    """
    y_true = np.asarray(y_true)
    cluster_ids = np.asarray(cluster_ids)
    labels = sorted(set(int(v) for v in y_true))
    ids = sorted(set(int(v) for v in cluster_ids))
    best = (-1.0, None)
    for perm in permutations(labels, len(ids)):
        mapped = np.empty_like(cluster_ids)
        for cid, lab in zip(ids, perm):
            mapped[cluster_ids == cid] = lab
        score = accuracy(y_true, mapped)
        if score > best[0]:
            best = (score, tuple(perm))
    return best


def cluster_confusion(y_true, cluster_ids, n_labels: int, n_clusters: int):
    """Rows are true classes, columns are cluster ids; entries are counts."""
    y_true = np.asarray(y_true)
    cluster_ids = np.asarray(cluster_ids)
    table = np.zeros((n_labels, n_clusters), dtype=int)
    for t, c in zip(y_true, cluster_ids):
        table[int(t), int(c)] += 1
    return table


def inertia_curve(X, ks, seed: int = 0):
    """Within-cluster sum of squares for each k in ``ks``."""
    return [float(cluster(X, k, seed=seed).inertia_) for k in ks]


def silhouette_curve(X, ks, seed: int = 0):
    """Mean silhouette score for each k in ``ks`` (k >= 2 only)."""
    out = []
    for k in ks:
        assignment = cluster(X, k, seed=seed).labels_
        out.append(float(silhouette_score(X, assignment)))
    return out


def agreement(labels_a, labels_b) -> float:
    """Adjusted Rand index: agreement between two partitions, ignoring names."""
    return float(adjusted_rand_score(labels_a, labels_b))


# --------------------------------------------------------------------------
# 6. Reinforcement: evaluative feedback, on a bandit built from scratch
# --------------------------------------------------------------------------


class GaussianBandit:
    """A k-armed bandit. Pulling arm i returns N(mean_i, 1).

    The defining property is what you are *not* told: pulling arm i tells
    you the reward for arm i on this pull and nothing whatever about the
    other k-1 arms. That is evaluative feedback. A supervised learner in
    the same position would have been handed the whole reward vector.
    """

    def __init__(self, k: int = 10, seed: int = 0):
        self.k = k
        self.rng = np.random.default_rng(seed)
        self.means = self.rng.normal(0.0, 1.0, size=k)
        self.best_arm = int(np.argmax(self.means))

    def pull(self, arm: int) -> float:
        """Return the reward for one pull of ``arm`` -- and only that arm."""
        return float(self.rng.normal(self.means[arm], 1.0))

    def full_feedback(self) -> np.ndarray:
        """The reward vector a supervised learner would have been given.

        No reinforcement-learning agent ever sees this. It exists here only
        so the lab can measure what the missing information is worth.
        """
        return self.rng.normal(self.means, 1.0)


def run_bandit(k: int = 10, steps: int = 1000, epsilon: float = 0.1, seed: int = 0):
    """Epsilon-greedy action-value learning, written out in full.

    ``epsilon=0.0`` is the pure greedy agent. Returns a dict with the
    reward at each step and whether the optimal arm was chosen at each
    step.
    """
    bandit = GaussianBandit(k=k, seed=seed)
    chooser = np.random.default_rng(seed + 10_000)
    estimates = np.zeros(k)
    counts = np.zeros(k, dtype=int)
    rewards = np.zeros(steps)
    optimal = np.zeros(steps, dtype=bool)

    for t in range(steps):
        if chooser.random() < epsilon:
            arm = int(chooser.integers(k))
        else:
            arm = int(np.argmax(estimates))
        reward = bandit.pull(arm)
        counts[arm] += 1
        # incremental mean: estimate += (reward - estimate) / count
        estimates[arm] += (reward - estimates[arm]) / counts[arm]
        rewards[t] = reward
        optimal[t] = arm == bandit.best_arm

    return {
        "rewards": rewards,
        "optimal": optimal,
        "estimates": estimates,
        "counts": counts,
        "true_means": bandit.means,
        "best_arm": bandit.best_arm,
    }


def average_bandit(runs: int = 200, **kwargs):
    """Average ``run_bandit`` over independent problems, as the field does.

    A single bandit run is almost pure noise; the published comparison
    between greedy and epsilon-greedy is an average over many problems.
    Returns ``(mean_reward, fraction_optimal)`` over the whole horizon.
    """
    reward_total = 0.0
    optimal_total = 0.0
    for r in range(runs):
        out = run_bandit(seed=r, **kwargs)
        reward_total += float(np.mean(out["rewards"]))
        optimal_total += float(np.mean(out["optimal"]))
    return reward_total / runs, optimal_total / runs


# --------------------------------------------------------------------------
# 7. Delayed feedback and credit assignment: a gridworld, from scratch
# --------------------------------------------------------------------------


class GridWorld:
    """A ``size`` x ``size`` grid. Reward +1 at the goal, 0 everywhere else.

    The agent starts top-left, the goal is bottom-right, and every step
    costs nothing. So the feedback for the very first move arrives only
    after the goal is reached -- which is the credit-assignment problem in
    its smallest honest form.
    """

    ACTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))  # up, down, left, right

    def __init__(self, size: int = 5):
        self.size = size
        self.start = (0, 0)
        self.goal = (size - 1, size - 1)

    def n_states(self) -> int:
        return self.size * self.size

    def state_index(self, pos) -> int:
        return pos[0] * self.size + pos[1]

    def step(self, pos, action: int):
        """Return ``(next_pos, reward, done)``. Walls block movement."""
        dr, dc = self.ACTIONS[action]
        r = min(max(pos[0] + dr, 0), self.size - 1)
        c = min(max(pos[1] + dc, 0), self.size - 1)
        nxt = (r, c)
        if nxt == self.goal:
            return nxt, 1.0, True
        return nxt, 0.0, False

    def shortest_path_length(self) -> int:
        """The optimal number of steps from start to goal on an open grid."""
        return (self.size - 1) * 2


def argmax_random_tiebreak(values, rng) -> int:
    """Return an index of the maximum, choosing uniformly among ties.

    ``np.argmax`` returns the *lowest* index that attains the maximum. On a
    Q-table that starts at all zeros every row is one big tie, so the greedy
    branch of an epsilon-greedy agent degenerates into a constant action.
    This lab measures what that costs; see exercise 7.
    """
    values = np.asarray(values)
    best = np.flatnonzero(values == values.max())
    return int(best[rng.integers(len(best))])


def q_learning(
    world: GridWorld,
    episodes: int = 300,
    alpha: float = 0.5,
    gamma: float = 0.95,
    epsilon: float = 0.2,
    max_steps: int = 200,
    seed: int = 0,
    break_ties_randomly: bool = True,
):
    """Tabular Q-learning, written out so the bootstrap is visible.

    The update ``Q[s,a] += alpha * (r + gamma * max_a' Q[s',a'] - Q[s,a])``
    is how a reward that only ever appears at the goal travels backwards to
    the first move. Nobody ever tells the agent which action was correct; it
    infers it from its own later estimates.

    Set ``break_ties_randomly=False`` to get the ``np.argmax`` behaviour that
    exercise 7 measures as a failure.
    """
    rng = np.random.default_rng(seed)
    n_actions = len(world.ACTIONS)
    Q = np.zeros((world.n_states(), n_actions))
    lengths = []
    reached = 0

    for _ in range(episodes):
        pos = world.start
        done = False
        for step in range(max_steps):
            s = world.state_index(pos)
            if rng.random() < epsilon:
                a = int(rng.integers(n_actions))
            elif break_ties_randomly:
                a = argmax_random_tiebreak(Q[s], rng)
            else:
                a = int(np.argmax(Q[s]))
            nxt, reward, done = world.step(pos, a)
            s_next = world.state_index(nxt)
            target = reward + (0.0 if done else gamma * float(np.max(Q[s_next])))
            Q[s, a] += alpha * (target - Q[s, a])
            pos = nxt
            if done:
                break
        reached += int(done)
        lengths.append(step + 1)

    return Q, lengths, reached


def greedy_path_length(world: GridWorld, Q, max_steps: int = 200) -> int:
    """Follow the learned policy with no exploration and count the steps.

    Returns ``max_steps`` if the policy never reaches the goal, which is the
    honest answer for a Q-table the reward never reached.
    """
    pos = world.start
    for step in range(max_steps):
        a = int(np.argmax(Q[world.state_index(pos)]))
        pos, _reward, done = world.step(pos, a)
        if done:
            return step + 1
    return max_steps


def states_with_nonzero_value(Q) -> int:
    """How many grid squares the reward signal has actually reached."""
    return int(np.sum(np.max(Q, axis=1) > 0.0))


# --------------------------------------------------------------------------
# 8. Why logged bandit data is not a supervised dataset
# --------------------------------------------------------------------------


def logged_policy_dataset(k: int = 10, steps: int = 2000, epsilon: float = 0.1, seed: int = 0):
    """Turn a bandit run into the (arm, reward) table a log would contain."""
    out = run_bandit(k=k, steps=steps, epsilon=epsilon, seed=seed)
    arms = []
    rewards = []
    bandit = GaussianBandit(k=k, seed=seed)
    chooser = np.random.default_rng(seed + 10_000)
    estimates = np.zeros(k)
    counts = np.zeros(k, dtype=int)
    for _ in range(steps):
        if chooser.random() < epsilon:
            arm = int(chooser.integers(k))
        else:
            arm = int(np.argmax(estimates))
        reward = bandit.pull(arm)
        counts[arm] += 1
        estimates[arm] += (reward - estimates[arm]) / counts[arm]
        arms.append(arm)
        rewards.append(reward)
    return np.array(arms), np.array(rewards), out["best_arm"], counts


def arm_pull_counts(counts) -> dict:
    """Pulls per arm, as a plain dict, for reporting."""
    return {i: int(c) for i, c in enumerate(counts)}


# --------------------------------------------------------------------------
# 9. Labels are the expensive part: semi-supervised in its simplest form
# --------------------------------------------------------------------------


def label_budget_curve(X, y, budgets, seed: int = 0, n_neighbors: int = 1):
    """Accuracy as a function of how many labelled rows you can afford.

    Rows are chosen uniformly at random, which is what you get when nobody
    thinks about *which* rows to label.
    """
    train_idx, test_idx = split_indices(len(y), 100, seed=seed)
    rng = np.random.default_rng(seed + 7)
    scores = []
    for b in budgets:
        chosen = rng.permutation(train_idx)[:b]
        model = KNeighborsClassifier(n_neighbors=min(n_neighbors, b))
        model.fit(X[chosen], y[chosen])
        scores.append(accuracy(y[test_idx], model.predict(X[test_idx])))
    return scores


def cluster_then_label(X, y, k: int, seed: int = 0):
    """Spend the label budget on one representative row per cluster.

    Cluster the *unlabelled* data, label the row closest to each centroid,
    and propagate that label to the whole cluster. This is unsupervised
    learning being used to make supervised learning cheaper, which is the
    honest reason the two categories sit in one lesson.
    """
    train_idx, test_idx = split_indices(len(y), 100, seed=seed)
    km = cluster(X[train_idx], k, seed=seed)
    representatives = []
    for c in range(k):
        members = np.where(km.labels_ == c)[0]
        d = np.linalg.norm(X[train_idx][members] - km.cluster_centers_[c], axis=1)
        representatives.append(int(members[int(np.argmin(d))]))
    rep_labels = y[train_idx][representatives]
    propagated = rep_labels[km.labels_]
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(X[train_idx], propagated)
    return accuracy(y[test_idx], model.predict(X[test_idx])), len(representatives)


def full_supervision_score(X, y, seed: int = 0) -> float:
    """The ceiling: every training row labelled."""
    train_idx, test_idx = split_indices(len(y), 100, seed=seed)
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(X[train_idx], y[train_idx])
    return accuracy(y[test_idx], model.predict(X[test_idx]))


# --------------------------------------------------------------------------
# 10. The decision function: which kind of problem is this?
# --------------------------------------------------------------------------


def problem(*, has_labels: bool, actions_change_the_data: bool, feedback_is_immediate: bool):
    """Build the three-answer description a problem must supply."""
    return {
        "has_labels": has_labels,
        "actions_change_the_data": actions_change_the_data,
        "feedback_is_immediate": feedback_is_immediate,
    }


def classify_problem(spec: dict) -> str:
    """Name the learning setting a problem actually belongs to.

    Order matters. The question that decides the most is whether your
    actions change what data you see next -- because that single property
    is what makes a problem reinforcement learning no matter how many
    labels you have.
    """
    for key in ("has_labels", "actions_change_the_data", "feedback_is_immediate"):
        if key not in spec:
            raise KeyError(f"problem description is missing {key!r}")
    if spec["actions_change_the_data"]:
        if spec["feedback_is_immediate"]:
            return "reinforcement learning: contextual bandit"
        return "reinforcement learning: sequential, with delayed credit"
    if spec["has_labels"]:
        return "supervised learning"
    return "unsupervised learning"


# --------------------------------------------------------------------------
# Reporting helpers used by both the tests and report_measurements.py
# --------------------------------------------------------------------------


def logged_arm_means(arms, rewards) -> dict:
    """Mean logged reward per arm -- the only thing a log can tell you."""
    arms = np.asarray(arms)
    rewards = np.asarray(rewards)
    return {int(a): float(np.mean(rewards[arms == a])) for a in sorted(set(arms.tolist()))}


def logged_best_arm(arms, rewards) -> int:
    """The arm a supervised model trained on the log would choose."""
    means = logged_arm_means(arms, rewards)
    return max(means, key=means.get)


def log_verdicts(seeds, epsilon: float, k: int = 10, steps: int = 2000):
    """For each seed, whether the log's favourite arm is the truly best arm.

    Returns a list of ``(seed, distinct_arms, logged_pick, true_best, correct)``.
    """
    rows = []
    for seed in seeds:
        arms, rewards, true_best, _counts = logged_policy_dataset(
            k=k, steps=steps, epsilon=epsilon, seed=seed
        )
        pick = logged_best_arm(arms, rewards)
        rows.append(
            (seed, len(set(arms.tolist())), pick, int(true_best), bool(pick == int(true_best)))
        )
    return rows


def average_label_budget_curve(X, y, budgets, repeats: int = 40, base_seed: int = 142):
    """``label_budget_curve`` averaged over independent splits and draws.

    A single split of 150 rows is far too noisy to read a trend from -- one
    run of this curve is not even monotone. Averaging is not decoration; it
    is the difference between a measurement and an anecdote.
    """
    total = np.zeros(len(budgets))
    for s in range(repeats):
        total += np.array(label_budget_curve(X, y, budgets, seed=base_seed + s))
    return [float(v) for v in total / repeats]


def average_cluster_then_label(X, y, k: int, repeats: int = 40, base_seed: int = 142) -> float:
    """``cluster_then_label`` averaged over the same splits, for comparison."""
    scores = [cluster_then_label(X, y, k, seed=base_seed + s)[0] for s in range(repeats)]
    return float(np.mean(scores))


def average_full_supervision(X, y, repeats: int = 40, base_seed: int = 142) -> float:
    """The every-row-labelled ceiling, averaged over the same splits."""
    scores = [full_supervision_score(X, y, seed=base_seed + s) for s in range(repeats)]
    return float(np.mean(scores))


def value_spread_by_episode(world, episode_counts, seed: int = 0):
    """How many states the reward has reached after each episode count.

    This is credit assignment made countable: with a reward only at the
    goal, the first episode leaves exactly one state with a non-zero value,
    the second leaves two, and so on.
    """
    rows = []
    for n in episode_counts:
        Q, _lengths, _reached = q_learning(world, episodes=n, seed=seed)
        rows.append((n, states_with_nonzero_value(Q), greedy_path_length(world, Q)))
    return rows
