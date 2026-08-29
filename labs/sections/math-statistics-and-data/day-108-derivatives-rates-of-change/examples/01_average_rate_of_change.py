"""A rate is a difference divided by the interval it happened over.

Run from inside `examples/`:

    ../.venv/bin/python3 01_average_rate_of_change.py

Nothing in this script is calculus yet. It is a stopwatch and a tape measure.
"""

from __future__ import annotations

import dataset as D
from derivatives import average_rate

print("Day 108 / 01 — average rate of change")
print()

# --------------------------------------------------------------------------
print("1. A car, timed once a second")
# --------------------------------------------------------------------------
print()
print("   The distances are invented. They are 4 * t**2 metres, so the car is")
print("   speeding up steadily and every number below can be checked by hand.")
print()
print("     t (s)   distance (m)")
for t, d in zip(D.CAR_TIMES_S, D.CAR_DISTANCE_M):
    print(f"     {t:5.1f}   {d:12.1f}")
print()

# --------------------------------------------------------------------------
print("2. Rise over run, over the whole trip")
# --------------------------------------------------------------------------
print()


def distance(t: float) -> float:
    """Distance in metres at time t seconds. 4 * t**2, matching the table."""
    return 4.0 * t * t


whole = average_rate(distance, 0.0, 6.0)
print("     rise = 144.0 - 0.0 =", D.CAR_DISTANCE_M[-1] - D.CAR_DISTANCE_M[0], "metres")
print("     run  =   6.0 - 0.0 =", D.CAR_TIMES_S[-1] - D.CAR_TIMES_S[0], "seconds")
print(f"     average speed = rise / run = {whole} m/s")
assert whole == D.CAR_AVERAGE_SPEED_WHOLE_TRIP
print()
print("   24 metres per second, averaged over six seconds. Note what that")
print("   number does NOT say: the car was never travelling at 24 m/s for the")
print("   whole trip. It started at rest and finished much faster.")
print()

# --------------------------------------------------------------------------
print("3. The same question, asked of one second at a time")
# --------------------------------------------------------------------------
print()
print("     interval      rise (m)   run (s)   average speed (m/s)")
per_second = []
for i in range(len(D.CAR_TIMES_S) - 1):
    a, b = D.CAR_TIMES_S[i], D.CAR_TIMES_S[i + 1]
    rise = D.CAR_DISTANCE_M[i + 1] - D.CAR_DISTANCE_M[i]
    speed = average_rate(distance, a, b)
    per_second.append(speed)
    print(f"     [{a:.0f}, {b:.0f}]        {rise:8.1f}   {b - a:7.1f}   {speed:19.1f}")
print()
assert per_second == [4.0, 12.0, 20.0, 28.0, 36.0, 44.0]
assert per_second[3] == D.CAR_AVERAGE_SPEED_SECOND_FOUR
print("   Six different answers to 'how fast was the car'. All six are correct.")
print("   They are answers to six different questions.")
print()

# --------------------------------------------------------------------------
print("4. The question a speedometer answers")
# --------------------------------------------------------------------------
print()
print("   A speedometer does not show an average over an interval. It shows a")
print("   number at an INSTANT. Ask for the average speed over an interval of")
print("   no width at all and the arithmetic refuses:")
print()
try:
    average_rate(distance, 3.0, 3.0)
except ZeroDivisionError as exc:
    print("     ZeroDivisionError:", str(exc).split(";")[0])
else:  # pragma: no cover - the call above always raises
    raise AssertionError("average_rate over a zero-width interval must refuse")
print()
print("   Rise zero, run zero, and 0/0 is not a number. That refusal is the")
print("   whole problem, and the derivative is the machine that gets round it:")
print("   instead of asking for the rate over no interval, ask for the rate")
print("   over intervals that get smaller and smaller, and see whether the")
print("   answers settle on something. Script 02 does exactly that.")
print()
print("   For this car the settled answer at t = 3 is", D.CAR_INSTANT_SPEED_AT_3, "m/s,")
print("   which sits between the 20 m/s averaged over second three and the")
print("   28 m/s averaged over second four -- as it must.")
assert per_second[2] < D.CAR_INSTANT_SPEED_AT_3 < per_second[3]
print()

print("01_average_rate_of_change.py: every assertion held.")
