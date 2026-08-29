#!/usr/bin/env python3
"""Day 046 lab — Precision and Money Math (completed reference).

Runs five short demonstrations of how Python handles numbers and where
floating-point precision bites:

  1. The classic float trap: 0.1 + 0.2 is not exactly 0.3.
  2. Comparing floats safely with math.isclose.
  3. A shopping-cart total in float (wrong) vs Decimal (exact).
  4. Making change with floor division (//) and modulo (%).
  5. A few essentials from the math module (sqrt, floor, ceil).

Everything here uses only the Python standard library — no installs, no
network, no API keys. Run it with:

    python3 examples/precision_demo.py
"""

from decimal import Decimal, ROUND_HALF_UP
import math


def section(title):
    """Print a labelled section header so the output reads clearly."""
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def demo_float_trap():
    section("1. The float trap: 0.1 + 0.2 != 0.3")
    total = 0.1 + 0.2
    print(f"0.1 + 0.2        = {total}")
    print(f"Is it exactly 0.3? {total == 0.3}")
    # A float prints its shortest round-tripping form, which hides the error.
    # Decimal(float) shows the exact value actually stored in the 64 bits.
    print(f"0.1 stored as    = {Decimal(0.1)}")
    print(f"0.1 + 0.2 stored = {Decimal(total)}")


def demo_isclose():
    section("2. Comparing floats safely with math.isclose")
    total = 0.1 + 0.2
    print(f"total == 0.3               -> {total == 0.3}")
    print(f"math.isclose(total, 0.3)   -> {math.isclose(total, 0.3)}")
    print(f"round(total, 2) == 0.3     -> {round(total, 2) == 0.3}")


def demo_money():
    section("3. Shopping cart: float (wrong) vs Decimal (exact)")
    prices_float = [19.99, 5.99, 2.50, 0.10, 0.20]
    prices_decimal = [Decimal(str(p)) for p in prices_float]

    float_total = sum(prices_float)
    decimal_total = sum(prices_decimal)

    print(f"Items: {prices_float}")
    print(f"float sum   = {float_total!r}")
    print(f"Decimal sum = {decimal_total}")
    print(f"float == 28.78?   {float_total == 28.78}")
    print(f"Decimal == 28.78? {decimal_total == Decimal('28.78')}")

    # Money is rounded to the nearest cent, half rounding up, the way a till does.
    rounded = decimal_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    print(f"Charge the customer: ${rounded}")


def demo_change():
    section("4. Making change with // and %")
    # Work in whole cents (integers) so there is no float error at all.
    price_cents = 1275   # $12.75
    paid_cents = 2000    # $20.00
    change = paid_cents - price_cents
    print(f"Price ${price_cents / 100:.2f}, paid ${paid_cents / 100:.2f}")
    print(f"Change owed: {change} cents (${change / 100:.2f})")

    coins = [("dollar", 100), ("quarter", 25), ("dime", 10),
             ("nickel", 5), ("penny", 1)]
    remaining = change
    for name, value in coins:
        count = remaining // value   # how many whole coins of this size fit
        remaining = remaining % value  # what is left over after handing them out
        print(f"  {count} x {name} ({value}c)")
    print(f"Remaining after change: {remaining} cents")


def demo_math_module():
    section("5. The math module: sqrt, floor, ceil")
    print(f"math.sqrt(2)   = {math.sqrt(2)}")
    print(f"math.floor(3.7) = {math.floor(3.7)}")
    print(f"math.ceil(3.2)  = {math.ceil(3.2)}")
    print(f"math.pi        = {math.pi}")


def main():
    demo_float_trap()
    demo_isclose()
    demo_money()
    demo_change()
    demo_math_module()
    print()
    print("Done. See numbers-worksheet.md to record what you observed.")


if __name__ == "__main__":
    main()
