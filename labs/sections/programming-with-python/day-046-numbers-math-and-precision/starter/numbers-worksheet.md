# Numbers worksheet — Day 046

Fill this in as you complete the exercises in `precision_demo.py`. Everything
you need appears in the program's own output; copy the real values you see.

## 1. The float trap

Run `python3 examples/precision_demo.py` (or your completed starter) and record:

- `0.1 + 0.2` prints as: `________________________________`
- Is it exactly equal to `0.3`? (`True` / `False`): `______`
- The exact value of `0.1` actually stored in the 64 bits (the long
  `Decimal(0.1)` line): `________________________________________________`

One sentence, in your own words, on *why* `0.1` cannot be stored exactly:

```
______________________________________________________________________
```

## 2. Comparing floats safely

- `total == 0.3` gives: `______`
- `math.isclose(total, 0.3)` gives: `______`

Which of these should you use when comparing two computed floats, and why?

```
______________________________________________________________________
```

## 3. The exact Decimal total

For the cart `[19.99, 5.99, 2.50, 0.10, 0.20]`:

- `float` sum prints as: `________________________________`
- `Decimal` sum prints as: `______`
- The amount the customer is charged: `$______`

Why did you build the Decimals from **strings** (`Decimal("19.99")`) rather
than from floats (`Decimal(19.99)`)?

```
______________________________________________________________________
```

## 4. Floor division vs true division

For a change amount of `725` cents:

- `725 / 100` (true division, `/`) gives: `______`
- `725 // 100` (floor division, `//`) gives: `______`
- `725 % 100` (modulo, `%`) gives: `______`

One sentence on when you would reach for `//` and `%` instead of `/`:

```
______________________________________________________________________
```
