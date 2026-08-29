"""The exercise suite. One test per exercise, plus a worked example.

Run it from the lab directory:

    .venv/bin/pytest starter -q

Before you start, one test passes and nine are skipped. As you finish each
exercise in `vectors.py`, delete the `@pytest.mark.skip(...)` line above its
test and run the suite again.

Every numeric assertion in this file goes through `math.isclose` or
`numpy.allclose` with the tolerance stated below. None of them uses `==`, and
exercise 8 is where you find out why: normalising a vector gives a magnitude
that is 1 to within floating-point error and is sometimes not exactly 1.0. A
test written with `==` would fail on correct code, which is worse than useless
because you would go looking for a bug that is not there.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

import vectors as mine

# The tolerance every assertion in this file uses, stated once so you can see
# exactly how much slack is being allowed. rel_tol handles large numbers,
# abs_tol handles values near zero where a relative tolerance is meaningless.
REL_TOL = 1e-9
ABS_TOL = 1e-12


def close(a, b) -> bool:
    return math.isclose(a, b, rel_tol=REL_TOL, abs_tol=ABS_TOL)


def allclose(a, b) -> bool:
    return bool(np.allclose(a, b, rtol=REL_TOL, atol=ABS_TOL))


CATALOGUE = {
    "roast-chicken":      [9, 0, 1, 0],
    "slow-cooker-stew":   [8, 0, 2, 0],
    "marathon-plan":      [0, 9, 1, 2],
    "race-day-nutrition": [4, 6, 3, 0],
    "household-budget":   [1, 0, 9, 0],
    "storm-bulletin":     [0, 1, 0, 9],
}


# ---------------------------------------------------------------------------
# Worked example — this one passes before you write anything. Read it first;
# it is the shape every test below follows.
# ---------------------------------------------------------------------------


def test_worked_example_the_guard_refuses_a_dimension_mismatch():
    """check_same_dimension is provided. This is what a finished test looks like."""
    mine.check_same_dimension([1, 2], [3, 4])  # same length: no complaint
    with pytest.raises(ValueError, match="dimension mismatch"):
        mine.check_same_dimension([1, 2], [3, 4, 5])


# ---------------------------------------------------------------------------
# Exercise 1 — add
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="exercise 1: implement add() in vectors.py, then delete this line")
def test_exercise_1_add():
    assert allclose(mine.add([1, 2, 3], [10, 20, 30]), [11, 22, 33])
    # Addition is commutative: the parallelogram has two equal sides.
    assert allclose(mine.add([3, -4], [1, 7]), mine.add([1, 7], [3, -4]))
    with pytest.raises(ValueError, match="dimension mismatch"):
        mine.add([1, 2], [1, 2, 3])


# ---------------------------------------------------------------------------
# Exercise 2 — subtract
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="exercise 2: implement subtract() in vectors.py, then delete this line")
def test_exercise_2_subtract():
    assert allclose(mine.subtract([4, 6], [1, 2]), [3, 4])
    # A vector minus itself is the zero vector.
    assert allclose(mine.subtract([7, -1, 4], [7, -1, 4]), [0, 0, 0])
    with pytest.raises(ValueError, match="dimension mismatch"):
        mine.subtract([1, 2], [1, 2, 3])


# ---------------------------------------------------------------------------
# Exercise 3 — scale
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="exercise 3: implement scale() in vectors.py, then delete this line")
def test_exercise_3_scale():
    assert allclose(mine.scale(3, [1, 2]), [3, 6])
    assert allclose(mine.scale(-1, [1, 2]), [-1, -2])
    assert allclose(mine.scale(0, [1, 2]), [0, 0])
    assert allclose(mine.scale(1, [4, -9]), [4, -9])


# ---------------------------------------------------------------------------
# Exercise 4 — dot
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="exercise 4: implement dot() in vectors.py, then delete this line")
def test_exercise_4_dot():
    # 1*4 + 2*5 + 3*6 = 4 + 10 + 18 = 32
    assert close(mine.dot([1, 2, 3], [4, 5, 6]), 32)
    # Perpendicular arrows have a dot product of zero.
    assert close(mine.dot([1, 0], [0, 1]), 0)
    assert close(mine.dot([3, 4], [-4, 3]), 0)
    # A number came back, not a list.
    assert not isinstance(mine.dot([1, 2], [3, 4]), list)
    # NumPy agrees on the same inputs.
    assert close(mine.dot([1, 2, 3], [4, 5, 6]), float(np.dot([1, 2, 3], [4, 5, 6])))


# ---------------------------------------------------------------------------
# Exercise 5 — l2_norm
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="exercise 5: implement l2_norm() in vectors.py, then delete this line")
def test_exercise_5_l2_norm():
    assert close(mine.l2_norm([3, 4]), 5)  # sqrt(9 + 16)
    assert close(mine.l2_norm([2, 3, 6]), 7)  # sqrt(4 + 9 + 36)
    assert close(mine.l2_norm([1, 2, 2]), 3)  # sqrt(1 + 4 + 4)
    assert close(mine.l2_norm([3, 4, 12]), 13)  # sqrt(9 + 16 + 144)
    assert close(mine.l2_norm([0, 0, 0]), 0)
    # Squaring removes the signs, so a reversed vector has the same magnitude.
    assert close(mine.l2_norm([-3, -4]), 5)
    # NumPy agrees.
    assert close(mine.l2_norm([3, 4, 12]), float(np.linalg.norm([3, 4, 12])))


# ---------------------------------------------------------------------------
# Exercise 6 — l1_norm
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="exercise 6: implement l1_norm() in vectors.py, then delete this line")
def test_exercise_6_l1_norm():
    assert close(mine.l1_norm([3, 4]), 7)
    assert close(mine.l1_norm([-3, 4]), 7)  # absolute values, so signs vanish
    assert close(mine.l1_norm([2, 2, 2]), 6)
    assert close(mine.l1_norm([4, 0, 0]), 4)
    assert close(mine.l1_norm([0, 0, 0]), 0)
    # The same vector, two different sizes. Neither is wrong.
    assert not close(mine.l1_norm([3, 4]), mine.l2_norm([3, 4]))
    assert close(mine.l1_norm([3, 4, 12]), float(np.linalg.norm([3, 4, 12], ord=1)))


# ---------------------------------------------------------------------------
# Exercise 7 — distance
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="exercise 7: implement distance() in vectors.py, then delete this line")
def test_exercise_7_distance():
    assert close(mine.distance([1, 2], [4, 6]), 5)
    assert close(mine.distance([0, 0, 0], [2, 3, 6]), 7)
    assert close(mine.distance([10, 10], [10, 10]), 0)
    # It is symmetric, because reversing the difference does not change its length.
    assert close(mine.distance([1, 2], [4, 6]), mine.distance([4, 6], [1, 2]))
    # And it really is the norm of the difference, by construction.
    assert close(
        mine.distance([9, 0, 1, 0], [1, 0, 9, 0]),
        mine.l2_norm(mine.subtract([9, 0, 1, 0], [1, 0, 9, 0])),
    )


# ---------------------------------------------------------------------------
# Exercise 8 — normalise, and the float trap
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="exercise 8: implement normalise() in vectors.py, then delete this line")
def test_exercise_8_normalise():
    assert allclose(mine.normalise([3, 4]), [0.6, 0.8])

    # Magnitude 1 for every one of these — to tolerance, never with ==.
    for v in ([3, 4], [1, 2, 2], [1, 1], [1, 1, 1], [0.1, 0.2, 0.3], [2, 3, 6]):
        assert close(mine.l2_norm(mine.normalise(v)), 1.0)

    # Direction survives: scaling the unit vector back up recovers the original.
    v = [3, 4]
    assert allclose(mine.scale(mine.l2_norm(v), mine.normalise(v)), v)

    # Magnitude does not survive, which is the whole point of normalising.
    assert not close(mine.l2_norm(mine.normalise(v)), mine.l2_norm(v))

    # The zero vector has no direction and cannot be normalised.
    with pytest.raises(ValueError, match="zero vector"):
        mine.normalise([0, 0, 0])


@pytest.mark.skip(reason="exercise 8: implement normalise() in vectors.py, then delete this line")
def test_exercise_8_why_you_must_not_use_equals_equals():
    """Proof, on this machine, that `== 1.0` is the wrong test.

    At least one of these six vectors normalises to a magnitude that is not
    exactly 1.0. Every one of them is 1.0 to tolerance. If you had written
    `assert mine.l2_norm(unit) == 1.0`, correct code would have failed.
    """
    cases = [[3, 4], [1, 2, 2], [1, 1], [1, 1, 1], [0.1, 0.2, 0.3], [2, 3, 6]]
    magnitudes = [mine.l2_norm(mine.normalise(v)) for v in cases]
    assert all(close(m, 1.0) for m in magnitudes)
    assert any(m != 1.0 for m in magnitudes)


# ---------------------------------------------------------------------------
# Exercise 9 — nearest, over the catalogue, under both norms
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="exercise 9: implement nearest() in vectors.py, then delete this line")
def test_exercise_9_nearest_neighbour_in_the_catalogue():
    winner, score = mine.nearest(
        CATALOGUE["roast-chicken"], CATALOGUE, exclude="roast-chicken"
    )
    assert winner == "slow-cooker-stew"
    # (9,0,1,0) - (8,0,2,0) = (1,0,-1,0); 1 + 1 = 2; sqrt(2)
    assert close(score, math.sqrt(2))

    expected = {
        "roast-chicken": "slow-cooker-stew",
        "slow-cooker-stew": "roast-chicken",
        "marathon-plan": "race-day-nutrition",
        "race-day-nutrition": "marathon-plan",
        "household-budget": "race-day-nutrition",
        "storm-bulletin": "marathon-plan",
    }
    for item, neighbour in expected.items():
        assert mine.nearest(CATALOGUE[item], CATALOGUE, exclude=item)[0] == neighbour

    # Without exclude, everything is its own nearest neighbour at distance 0.
    same, zero_score = mine.nearest(CATALOGUE["storm-bulletin"], CATALOGUE)
    assert same == "storm-bulletin"
    assert close(zero_score, 0)

    with pytest.raises(ValueError):
        mine.nearest([1, 2], {})


@pytest.mark.skip(reason="exercise 9: implement nearest() in vectors.py, then delete this line")
def test_exercise_9_l1_and_l2_choose_different_winners():
    """The two norms rank the same two candidates in opposite orders.

        spike  = (4, 0, 0):  L1 = 4,  L2 = 4
        spread = (2, 2, 2):  L1 = 6,  L2 = sqrt(12) = 3.4641...

    Squaring is what does it: one component of 4 contributes 16, while three
    components of 2 contribute 4 each.
    """
    query = [0, 0, 0]
    candidates = {"spike": [4, 0, 0], "spread": [2, 2, 2]}

    l2_winner, l2_score = mine.nearest(query, candidates, metric=mine.distance)
    l1_winner, l1_score = mine.nearest(query, candidates, metric=mine.l1_distance)

    assert l2_winner == "spread"
    assert close(l2_score, math.sqrt(12))
    assert l1_winner == "spike"
    assert close(l1_score, 4)
    assert l1_winner != l2_winner
