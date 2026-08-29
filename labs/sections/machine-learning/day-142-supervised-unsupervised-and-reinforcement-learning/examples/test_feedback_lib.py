"""Machinery checks: the library itself behaves, before any claim is made.

These three tests are solved in both `starter/` and `examples/`. They are
here so that a broken helper reports itself as a broken helper rather than
as a surprising scientific result.
"""

import numpy as np
import pytest

import feedback_lib as f


def test_the_bandit_is_deterministic_given_a_seed():
    a = f.GaussianBandit(k=10, seed=5)
    b = f.GaussianBandit(k=10, seed=5)
    assert np.array_equal(a.means, b.means)
    assert a.best_arm == b.best_arm == int(np.argmax(a.means))
    # Different seeds give different problems, or the averaging is a lie.
    c = f.GaussianBandit(k=10, seed=6)
    assert not np.array_equal(a.means, c.means)


def test_the_gridworld_walls_block_movement_and_the_goal_ends_the_episode():
    world = f.GridWorld(4)
    # Moving up from the top-left corner leaves you where you are.
    assert world.step((0, 0), 0) == ((0, 0), 0.0, False)
    assert world.step((0, 0), 2) == ((0, 0), 0.0, False)
    # Moving into the goal pays 1.0 and terminates.
    nxt, reward, done = world.step((3, 2), 3)
    assert nxt == (3, 3) and reward == 1.0 and done is True
    # Every other transition pays nothing at all.
    assert world.step((1, 1), 1) == ((2, 1), 0.0, False)
    assert world.n_states() == 16
    assert world.shortest_path_length() == 6


def test_argmax_random_tiebreak_actually_spreads_over_ties():
    rng = np.random.default_rng(0)
    picks = {f.argmax_random_tiebreak(np.zeros(4), rng) for _ in range(200)}
    assert picks == {0, 1, 2, 3}
    # With a clear winner it is still an argmax.
    assert f.argmax_random_tiebreak(np.array([0.0, 9.0, 1.0, 2.0]), rng) == 1
    # np.argmax, by contrast, never leaves index 0 on an all-zero row.
    assert int(np.argmax(np.zeros(4))) == 0


def test_best_permutation_accuracy_is_never_worse_than_the_raw_number():
    y = np.array([0, 0, 1, 1, 2, 2])
    ids = np.array([2, 2, 0, 0, 1, 1])
    raw = f.raw_cluster_accuracy(y, ids)
    best, mapping = f.best_permutation_accuracy(y, ids)
    assert raw == 0.0
    assert best == 1.0
    # mapping[i] is the true label that cluster i turned out to hold.
    assert mapping == (1, 2, 0)
    with pytest.raises(AssertionError):
        assert best < raw
