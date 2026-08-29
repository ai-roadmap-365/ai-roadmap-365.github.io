#!/usr/bin/env python3
"""Day 046 lab starter — Precision and Money Math.

Complete the five numbered exercises below. Each one names the exact tool to
use. Run the file after each change to see your progress:

    python3 starter/precision_demo.py

The finished reference version lives in examples/precision_demo.py — try each
exercise yourself first, then compare. Record your answers in
starter/numbers-worksheet.md.
"""

from decimal import Decimal
import math


def main():
    # ------------------------------------------------------------------
    # Exercise 1: show the float error.
    # Add 0.1 and 0.2 with the + operator, store it in `total`, and print it.
    # Then print whether `total` is exactly equal to 0.3 using ==.
    # Replace the two placeholder lines below.
    total = 0.0  # <-- Exercise 1: change 0.0 to 0.1 + 0.2
    print(f"0.1 + 0.2 = {total}")
    print(f"Equals 0.3 exactly? {total == 0.3}")

    # ------------------------------------------------------------------
    # Exercise 2: compare floats safely.
    # Set `close` to the result of math.isclose(total, 0.3).
    # It should be True even though the == check above is False.
    close = None  # <-- Exercise 2: change None to math.isclose(total, 0.3)
    print(f"math.isclose(total, 0.3) = {close}")

    # ------------------------------------------------------------------
    # Exercise 3: compute an exact total with Decimal.
    # Build Decimals from the STRING form of each price (Decimal("19.99")),
    # never from the float, then sum them. The exact answer is 28.78.
    prices = ["19.99", "5.99", "2.50", "0.10", "0.20"]
    decimal_total = Decimal("0")  # <-- Exercise 3: sum Decimal(p) for p in prices
    print(f"Decimal cart total = {decimal_total}")
    print(f"Exactly 28.78? {decimal_total == Decimal('28.78')}")

    # ------------------------------------------------------------------
    # Exercise 4: use // (floor division).
    # A customer is owed 725 cents in change. How many whole dollars (100c)
    # is that? Use // to get the integer count.
    change_cents = 725
    dollars = 0  # <-- Exercise 4: change 0 to change_cents // 100
    print(f"{dollars} whole dollars in {change_cents} cents")

    # ------------------------------------------------------------------
    # Exercise 5: use % (modulo).
    # After handing out the whole dollars, how many cents are left over?
    # Use % to get the remainder.
    leftover_cents = 0  # <-- Exercise 5: change 0 to change_cents % 100
    print(f"{leftover_cents} cents left over after the dollars")


if __name__ == "__main__":
    main()
