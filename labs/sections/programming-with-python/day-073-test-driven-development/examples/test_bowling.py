"""The bowling scorer, one failing test at a time."""

import pytest

import bowling


def test_a_gutter_game_scores_zero():
    assert bowling.score([0] * 20) == 0


def test_a_game_of_all_ones_scores_twenty():
    assert bowling.score([1] * 20) == 20


def test_a_strike_adds_the_next_two_rolls():
    assert bowling.score([10, 3, 4] + [0] * 16) == 24


def test_a_spare_adds_the_next_roll():
    assert bowling.score([5, 5, 3] + [0] * 17) == 16


def test_a_roll_outside_zero_to_ten_is_refused():
    with pytest.raises(bowling.ScoringError):
        bowling.score([11] + [0] * 19)
    with pytest.raises(bowling.ScoringError):
        bowling.score([-1] + [0] * 19)


def test_a_frame_of_more_than_ten_pins_is_refused():
    with pytest.raises(bowling.ScoringError):
        bowling.score([7, 5] + [0] * 18)


def test_a_game_with_the_wrong_number_of_rolls_is_refused():
    with pytest.raises(bowling.ScoringError):
        bowling.score([0] * 19)
    with pytest.raises(bowling.ScoringError):
        bowling.score([0] * 21)


def test_a_perfect_game_scores_three_hundred():
    assert bowling.score([10] * 12) == 300


def test_a_real_game_scores_133():
    rolls = [1, 4, 4, 5, 6, 4, 5, 5, 10, 0, 1, 7, 3, 6, 4, 10, 2, 8, 6]
    assert bowling.score(rolls) == 133
