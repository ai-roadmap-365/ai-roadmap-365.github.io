# Expected output — required fields on every platform

The reference program `examples/precision_demo.py` is deterministic: it does
pure arithmetic on fixed numbers, so **its output is identical on macOS,
Linux, and Windows** for any standard CPython build. The full captured run is
in [`sample-run.txt`](sample-run.txt). These specific lines must appear:

| Section | Line that must appear | Why it is fixed |
| --- | --- | --- |
| 1. Float trap | `0.1 + 0.2 = 0.30000000000000004` | IEEE 754 double arithmetic is specified bit-for-bit |
| 1. Float trap | `Is it exactly 0.3? False` | The stored sum is slightly above 0.3 |
| 1. Float trap | `0.1 stored as = 0.1000000000000000055511151231257827021181583404541015625` | The exact value of the nearest double to 0.1 |
| 2. isclose | `math.isclose(total, 0.3) -> True` | The two values are within the default tolerance |
| 3. Money | `float sum = 28.779999999999998` | Float rounding error accumulates across the cart |
| 3. Money | `Decimal sum = 28.78` | Decimal is exact for base-10 fractions |
| 3. Money | `Charge the customer: $28.78` | Quantized to the nearest cent |
| 4. Change | `Change owed: 725 cents ($7.25)` | Integer arithmetic, no rounding |
| 4. Change | `7 x dollar (100c)` | `725 // 100 == 7` |
| 5. math | `math.sqrt(2) = 1.4142135623730951` | The nearest double to the square root of 2 |

## What may legitimately differ

Nothing in this program depends on the machine, the clock, or the network, so
there are **no platform-specific values** to account for. If any line above
differs on your machine, you are almost certainly on a very unusual Python
build; note it and move on. (Contrast this with the Day 001 lab, whose output
is entirely machine-specific.)
