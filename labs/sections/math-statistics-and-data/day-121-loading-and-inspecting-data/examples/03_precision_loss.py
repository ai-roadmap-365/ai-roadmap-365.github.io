"""Exercise 3 -- precision: an ID above 2**53 cannot survive a trip through float64.

Run: python3 03_precision_loss.py

read_csv() infers a purely-numeric column as int64, which represents every
integer in this example exactly. The corruption happens one step LATER, the
moment anything casts that column to float64 -- a join, an arithmetic
operation, a naive "convert everything numeric to float" cleanup step.
float64 has a 53-bit mantissa: it can represent every integer up to 2**53
exactly, and past that boundary it silently rounds to the nearest value it
CAN represent, with no error and no warning.
"""

import tempfile
from pathlib import Path

import pandas as pd

checks = 0
failures = 0


def check(label, condition):
    global checks, failures
    checks += 1
    if condition:
        print(f"  ok: {label}")
    else:
        print(f"  FAIL: {label}")
        failures += 1


BIG_ID = 2**53 + 1  # 9007199254740993 -- one past the exact-integer boundary
print(f"2**53 + 1 = {BIG_ID}")

tmpdir = Path(tempfile.mkdtemp(prefix="d121-ex03-"))
try:
    csv_path = tmpdir / "orders.csv"
    csv_path.write_text(f"order_id\n{BIG_ID}\n")

    df = pd.read_csv(csv_path)
    print("\nread_csv() infers:")
    print(df.dtypes)
    read_value = int(df.loc[0, "order_id"])
    print("value as read:", read_value)

    check("read_csv() infers the column as int64", df["order_id"].dtype == "int64")
    check("int64 preserves the ID exactly, digit for digit", read_value == BIG_ID)

    promoted = df.astype({"order_id": "float64"})
    promoted_value = int(promoted.loc[0, "order_id"])
    print("\nafter .astype('float64'):")
    print(promoted.dtypes)
    print("value after float64 round-trip:", promoted_value)
    print(f"exact:    {BIG_ID}")
    print(f"corrupted:{promoted_value}")

    check(
        "the float64 round-trip silently changes the value",
        promoted_value != BIG_ID,
    )
    check(
        "the corrupted value is exactly one less than the true ID -- the last digit collapsed",
        BIG_ID - promoted_value == 1,
    )
    # Show the exact differing digits, not just "it's wrong".
    exact_str = str(BIG_ID)
    corrupt_str = str(promoted_value)
    check(
        "both numbers have the same number of digits (16)",
        len(exact_str) == len(corrupt_str) == 16,
    )
    first_diff = next(i for i, (a, b) in enumerate(zip(exact_str, corrupt_str)) if a != b)
    print(f"\nfirst differing digit is at position {first_diff}: "
          f"'{exact_str[first_diff]}' (exact) vs '{corrupt_str[first_diff]}' (corrupted)")
    check(
        "the two numbers agree on every digit except the very last one",
        exact_str[:-1] == corrupt_str[:-1] and exact_str[-1] != corrupt_str[-1],
    )
finally:
    for f in tmpdir.iterdir():
        f.unlink()
    tmpdir.rmdir()

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("03_precision_loss.py: every assertion held.")
