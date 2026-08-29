"""Bowling scoring."""


class ScoringError(Exception):
    """A list of rolls that cannot be scored, because it breaks a rule of bowling."""


def score(rolls):
    """Total score for a completed ten-frame game, given every roll in order."""
    _check_pins(rolls)
    total = 0
    roll = 0
    bonus_rolls = 0
    for frame in range(1, 11):
        if roll >= len(rolls):
            raise ScoringError(f"a game has ten frames; the rolls stop before frame {frame}")
        if _is_strike(rolls, roll):
            if roll + 2 >= len(rolls):
                raise ScoringError(f"the strike in frame {frame} has no two bonus rolls after it")
            total += 10 + rolls[roll + 1] + rolls[roll + 2]
            bonus_rolls = 2
            roll += 1
        else:
            if roll + 1 >= len(rolls):
                raise ScoringError(f"frame {frame} has only one roll")
            pins = rolls[roll] + rolls[roll + 1]
            if pins > 10:
                raise ScoringError(f"a frame knocks down at most 10 pins, frame {frame} has {pins}")
            if pins == 10:
                if roll + 2 >= len(rolls):
                    raise ScoringError(f"the spare in frame {frame} has no bonus roll after it")
                total += 10 + rolls[roll + 2]
                bonus_rolls = 1
            else:
                total += pins
                bonus_rolls = 0
            roll += 2
    if roll + bonus_rolls != len(rolls):
        extra = len(rolls) - roll - bonus_rolls
        raise ScoringError(f"the game ends after frame ten, but {extra} extra roll(s) follow")
    return total


def _check_pins(rolls):
    for pins in rolls:
        if pins < 0 or pins > 10:
            raise ScoringError(f"a roll knocks down 0 to 10 pins, got {pins}")


def _is_strike(rolls, roll):
    return rolls[roll] == 10
