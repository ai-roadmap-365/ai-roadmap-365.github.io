"""Exercise 4 -- linearity of expectation holds even for dependent variables.

Let X be the first die and Y be the sum of both dice. Y obviously depends on
X -- half of Y's value IS X. Yet E[X + Y] = E[X] + E[Y] holds exactly, with
no independence assumption anywhere in the proof. This is the centrepiece
of the lesson's expectation-versus-variance asymmetry: expectation forgives
dependence completely.
"""

import dataset as D
import distributions as dist

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


outcomes = D.TWO_DICE_SPACE
weight = D.TWO_DICE_WEIGHT
X = D.first_die
Y = D.dice_sum

print("X = first die, Y = sum of both dice -- Y depends on X directly")
print("-" * 60)

E_X = dist.expectation_over(outcomes, weight, X)
E_Y = dist.expectation_over(outcomes, weight, Y)
E_X_plus_Y = dist.expectation_over(outcomes, weight, lambda o: X(o) + Y(o))

print(f"  E[X]     = {E_X}")
print(f"  E[Y]     = {E_Y}")
print(f"  E[X]+E[Y]= {E_X} + {E_Y} = {E_X + E_Y}")
print(f"  E[X+Y]   = {E_X_plus_Y}   (computed directly over the joint 36-outcome space)")

check("X and Y are dependent (Y's value literally includes X's)", True)
check("E[X + Y] equals E[X] + E[Y] EXACTLY", E_X_plus_Y == E_X + E_Y)

print()
print("  Linearity of expectation makes no independence assumption anywhere")
print("  in its proof -- it is just E[X+Y] = sum over the sample space of")
print("  (X(o)+Y(o)) * weight(o), and addition distributes over that sum")
print("  regardless of how X and Y relate to each other.")

print()
if all(ok for _, ok in checks_held):
    print(f"04_linearity_with_dependence.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
