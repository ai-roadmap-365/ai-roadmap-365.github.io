"""Supplementary -- JSON, SQL (sqlite3) and the stdlib csv module.

Run: python3 10_other_formats.py

Not one of the nine graded exercises -- this script exists to back the
lesson's Tools section with real, captured output for the formats it
covers beyond CSV and Parquet. openpyxl (Excel) is deliberately NOT run
here because it is not installed in this environment; the lesson describes
it from documentation only and says so plainly.
"""

import csv
import io
import json
import sqlite3
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


tmpdir = Path(tempfile.mkdtemp(prefix="d121-ex10-"))
try:
    # --- JSON ---------------------------------------------------------
    records = [
        {"id": 1, "name": "Alice", "active": True},
        {"id": 2, "name": "Bob", "active": False},
    ]
    json_path = tmpdir / "users.json"
    json_path.write_text(json.dumps(records))
    df_json = pd.read_json(json_path)
    print("read_json() on a list of records:")
    print(df_json)
    print(df_json.dtypes)
    check("read_json() recovers all 2 records", len(df_json) == 2)
    check("read_json() infers 'active' as a real boolean column", df_json["active"].dtype == "bool")

    # --- sqlite3 --------------------------------------------------------
    db_path = tmpdir / "orders.db"
    conn = sqlite3.connect(db_path)
    orders = pd.DataFrame({"order_id": [1, 2, 3], "amount": [19.99, 44.50, 7.25]})
    orders.to_sql("orders", conn, index=False, if_exists="replace")
    from_sql = pd.read_sql("SELECT * FROM orders WHERE amount > 10", conn)
    print("\nread_sql() against a real sqlite3 connection:")
    print(from_sql)
    check("read_sql()'s WHERE filter runs inside the database, not in pandas", len(from_sql) == 2)
    check("read_sql() returns the correct rows", set(from_sql["order_id"]) == {1, 2})
    conn.close()

    # --- stdlib csv module ------------------------------------------------
    # Where the stdlib module beats pandas: streaming one row at a time with
    # NO type inference at all -- every field arrives as exactly the string
    # that was in the file, which is sometimes exactly what you want.
    csv_path = tmpdir / "raw.csv"
    csv_path.write_text("id,code\n001,00A\n002,00B\n")
    rows = []
    with open(csv_path, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows.append(row)
    print("\nstdlib csv.DictReader (no type inference at all):")
    print(rows)
    check("csv.DictReader keeps every field as a plain str, leading zeros included", rows[0]["id"] == "001")
    check(
        "read_csv(), by contrast, would infer 'id' as an integer and drop those zeros",
        int(pd.read_csv(csv_path)["id"].iloc[0]) == 1,
    )
finally:
    for f in tmpdir.iterdir():
        f.unlink()
    tmpdir.rmdir()

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("10_other_formats.py: every assertion held.")
