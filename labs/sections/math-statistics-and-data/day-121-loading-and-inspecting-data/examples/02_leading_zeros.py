"""Exercise 2 -- leading zeros: an identifier column silently becomes a number.

Run: python3 02_leading_zeros.py

An identifier column like "00123" LOOKS like text -- it has meaningful
leading zeros, the way a ZIP code, an account number or a barcode does. By
default read_csv() infers it as int64, because every character in it is a
digit, and the leading zeros are simply gone: "00123" becomes 123. Nothing
raises. The join against another system that still has "00123" fails
silently, one row at a time, with no exception naming which row.
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


tmpdir = Path(tempfile.mkdtemp(prefix="d121-ex02-"))
try:
    csv_path = tmpdir / "customers.csv"
    csv_path.write_text("id,name\n00123,Alice\n00456,Bob\n00789,Carla\n")

    default = pd.read_csv(csv_path)
    print("default read:")
    print(default)
    print(default.dtypes)

    typed = pd.read_csv(csv_path, dtype={"id": "str"})
    print("\ndtype={'id': 'str'}:")
    print(typed)
    print(typed.dtypes)

    check("the default read infers id as int64", default["id"].dtype == "int64")
    check(
        "the default read silently drops the leading zeros: '00123' becomes 123",
        int(default.loc[0, "id"]) == 123,
    )
    check("dtype={'id': 'str'} keeps id as the str dtype", str(typed["id"].dtype) == "str")
    check(
        "dtype={'id': 'str'} preserves the leading zeros exactly",
        typed.loc[0, "id"] == "00123",
    )
    check(
        "the two reads disagree on the very same cell",
        str(default.loc[0, "id"]) != typed.loc[0, "id"],
    )
finally:
    for f in tmpdir.iterdir():
        f.unlink()
    tmpdir.rmdir()

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("02_leading_zeros.py: every assertion held.")
