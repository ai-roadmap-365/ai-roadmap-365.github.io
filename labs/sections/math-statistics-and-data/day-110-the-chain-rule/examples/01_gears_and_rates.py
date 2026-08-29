"""Rates multiply. That is the chain rule, before any calculus is involved.

Run from inside `examples/`:

    ../.venv/bin/python3 01_gears_and_rates.py
"""

import dataset as D
from chainrule import gear_ratio, product

print("=" * 74)
print("1. Two gears")
print("=" * 74)
print()
print("  Gear A turns 2 times for every 1 turn of gear B.")
print("  Gear B turns 3 times for every 1 turn of gear C.")
print()
print("  So how many times does A turn for one turn of C?")
print()
print("  Turn C once      -> B turns 3 times")
print("  B turns 3 times  -> A turns 3 x 2 = 6 times")
print()
print(f"  overall ratio = 2 x 3 = {gear_ratio(D.GEAR_RATIOS)}")
print()
print("  You did not need calculus for that, and you did not need to be")
print("  told a rule. You multiplied, because 'per' stacks by multiplying.")

assert gear_ratio(D.GEAR_RATIOS) == D.GEAR_RATIO_PRODUCT

print()
print("=" * 74)
print("2. A longer gear train")
print("=" * 74)
print()
print("  Add two more stages and nothing about the reasoning changes.")
print()
print("     stage      ratio     running product")
running = 1.0
for i, ratio in enumerate(D.GEAR_TRAIN, start=1):
    running *= ratio
    print(f"     {i}          {ratio:<9.2f} {running:.2f}")
print()
print(f"  overall ratio = {gear_ratio(D.GEAR_TRAIN)}")
print()
print("  Four stages, four numbers, one product. The chain rule for a")
print("  composition of four functions has exactly this shape, and the only")
print("  thing calculus adds is that the ratios are allowed to depend on")
print("  where you are -- a gear ratio is fixed, a derivative is not.")

assert gear_ratio(D.GEAR_TRAIN) == D.GEAR_TRAIN_PRODUCT

print()
print("=" * 74)
print("3. The same arithmetic with money")
print("=" * 74)
print()
print("  These three rates are invented for the arithmetic. They are not")
print("  quoted from any market and no real currency is named.")
print()
print("     1 unit of the first  buys 1.25 of the second")
print("     1 unit of the second buys 0.80 of the third")
print("     1 unit of the third  buys  150 of the fourth")
print()
print(f"     1.25 x 0.80 x 150 = {product(D.CURRENCY_RATES)}")
print()
print("  Notice the middle rate is BELOW one, and it drags the product down")
print("  relative to what the other two would have given alone. Hold on to")
print("  that: fifty factors slightly below one is how a gradient vanishes,")
print("  and script 07 measures it.")

assert product(D.CURRENCY_RATES) == D.CURRENCY_PRODUCT

print()
print("=" * 74)
print("4. What the notation is for")
print("=" * 74)
print()
print("  Write the gear answer the way calculus writes it:")
print()
print("      dA     dA     dB")
print("      --  =  --  x  --")
print("      dC     dB     dC")
print()
print("      6   =   2  x   3")
print()
print("  The 'dB' looks like it cancels, top and bottom. That reading is a")
print("  useful mnemonic and it is NOT a proof: dA and dB are not numbers")
print("  and there is no division happening. The reason the rule is true is")
print("  the gear reasoning above -- rates per something stack by")
print("  multiplying -- not the accident that the symbols line up.")
print()
print("  The mnemonic also stops working the moment a variable reaches the")
print("  output by more than one route. Script 04 is that case, and there")
print("  the contributions are ADDED. Nothing cancels.")

print()
print("01_gears_and_rates.py: every assertion held.")
