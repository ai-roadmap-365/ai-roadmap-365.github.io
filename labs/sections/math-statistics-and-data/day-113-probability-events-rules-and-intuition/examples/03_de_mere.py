"""Exercise 3 -- the Chevalier de Méré's two bets, exact and simulated.

In the 1650s de Méré believed these two bets were equally good:

  bet 1: at least one 6 in 4 rolls of one die
  bet 2: at least one double-six in 24 rolls of two dice

The reasoning was seductive: a double six is 1/6 as likely as a six, so
rolling 6x as many times should even things out. It does not. This script
derives both exactly with the complement rule, then confirms both by
simulation -- the exact arithmetic and the measurement have to agree, or one
of them is wrong.
"""

from fractions import Fraction

import numpy as np

import dataset as D
import probability as P
import simulate as S

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


print("Bet 1: at least one 6 in 4 rolls of one die")
print("-" * 60)

# The complement rule collapses "at least one" to one line: 1 minus the
# probability that every single roll fails.
p_no_six_one_roll = P.complement(Fraction(1, 6))
p_no_six_all_four = p_no_six_one_roll**D.DE_MERE_SINGLE_ROLLS
p_bet_one = P.complement(p_no_six_all_four)
print(f"  P(no 6 in one roll)       = {p_no_six_one_roll}")
print(f"  P(no 6 in all 4 rolls)    = {p_no_six_one_roll}^4 = {p_no_six_all_four}")
print(f"  P(at least one 6)         = 1 - {p_no_six_all_four} = {p_bet_one}")
print(f"                            = {float(p_bet_one):.10f}  ~ {round(float(p_bet_one), 4)}")

via_at_least_one = P.at_least_one(Fraction(1, 6), D.DE_MERE_SINGLE_ROLLS)
check("at_least_one() agrees with the step-by-step derivation", via_at_least_one == p_bet_one)
check("bet 1 rounds to 0.5177", round(float(p_bet_one), 4) == 0.5177)
check("bet 1 matches dataset.py's exact value", p_bet_one == D.DE_MERE_SINGLE_EXACT)

print()
print("Bet 2: at least one double-six in 24 rolls of two dice")
print("-" * 60)

p_no_double_one_roll = P.complement(Fraction(1, 36))
p_no_double_all_24 = p_no_double_one_roll**D.DE_MERE_DOUBLE_ROLLS
p_bet_two = P.complement(p_no_double_all_24)
print(f"  P(no double-six in one roll)     = {p_no_double_one_roll}")
print(f"  P(no double-six in all 24 rolls) = {p_no_double_one_roll}^24")
print(f"  P(at least one double-six)       = {float(p_bet_two):.10f}  ~ {round(float(p_bet_two), 4)}")

via_at_least_one_2 = P.at_least_one(Fraction(1, 36), D.DE_MERE_DOUBLE_ROLLS)
check("at_least_one() agrees with the step-by-step derivation", via_at_least_one_2 == p_bet_two)
check("bet 2 rounds to 0.4914", round(float(p_bet_two), 4) == 0.4914)
check("bet 2 matches dataset.py's exact value", p_bet_two == D.DE_MERE_DOUBLE_EXACT)

print()
print("The two bets are NOT equally good")
print("-" * 60)
print(f"  bet 1 (one die,  4 rolls):  {float(p_bet_one):.6f}  -- above 0.5, favours the player")
print(f"  bet 2 (two dice, 24 rolls): {float(p_bet_two):.6f}  -- below 0.5, favours the house")
check("bet 1 is favourable to the player", p_bet_one > Fraction(1, 2))
check("bet 2 is NOT favourable to the player", p_bet_two < Fraction(1, 2))
check("the two bets differ, contrary to the naive '6x the rolls' reasoning", p_bet_one != p_bet_two)

print()
print(f"Simulated at n = {D.DE_MERE_SIM_TRIALS:,} trials per bet, seed 42")
print("-" * 60)

rng = np.random.default_rng(D.REPRODUCIBILITY_SEED_A)
sim_one = S.simulate_at_least_one_six(rng, D.DE_MERE_SIM_TRIALS)
sim_two = S.simulate_at_least_one_double_six(rng, D.DE_MERE_SIM_TRIALS)

print(f"  bet 1: simulated {sim_one:.6f}  vs exact {float(p_bet_one):.6f}"
      f"  (gap {abs(sim_one - float(p_bet_one)):.6f}, tolerance {D.DE_MERE_SINGLE_TOL:.6f})")
print(f"  bet 2: simulated {sim_two:.6f}  vs exact {float(p_bet_two):.6f}"
      f"  (gap {abs(sim_two - float(p_bet_two)):.6f}, tolerance {D.DE_MERE_DOUBLE_TOL:.6f})")

check(
    "bet 1's simulation lands within 3 standard errors of the exact value",
    abs(sim_one - float(p_bet_one)) < D.DE_MERE_SINGLE_TOL,
)
check(
    "bet 2's simulation lands within 3 standard errors of the exact value",
    abs(sim_two - float(p_bet_two)) < D.DE_MERE_DOUBLE_TOL,
)

print()
if all(ok for _, ok in checks_held):
    print(f"03_de_mere.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
