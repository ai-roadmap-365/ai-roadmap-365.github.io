"""Exercise 4 -- dates: what parse_dates changes, and why a string date lies.

Run: python3 04_dates.py

Without parse_dates, a date column is just text -- the pandas-3.0 str
dtype, sorted the way any string sorts: character by character. That looks
fine as long as every date is written in the same fixed-width format. The
moment one row is written without a leading zero, the string sort silently
puts it in the wrong place, and nothing about the column's dtype warns you
this could happen.
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


tmpdir = Path(tempfile.mkdtemp(prefix="d121-ex04-"))
try:
    csv_path = tmpdir / "events.csv"
    csv_path.write_text("event,date\nfirst,2024-01-05\nsecond,2024-01-20\nthird,2024-1-9\n")

    unparsed = pd.read_csv(csv_path)
    print("without parse_dates:")
    print(unparsed)
    print(unparsed.dtypes)

    parsed = pd.read_csv(csv_path, parse_dates=["date"])
    print("\nwith parse_dates=['date']:")
    print(parsed)
    print(parsed.dtypes)

    check("without parse_dates the column is the str dtype", str(unparsed["date"].dtype) == "str")
    check(
        "with parse_dates the column becomes a real datetime64 dtype",
        str(parsed["date"].dtype).startswith("datetime64"),
    )

    string_sorted = unparsed.sort_values("date")["event"].tolist()
    parsed_sorted = parsed.sort_values("date")["event"].tolist()
    print("\nstring-sorted event order:  ", string_sorted)
    print("parsed-datetime event order:", parsed_sorted)

    # "third" is 2024-01-09 -- chronologically between "first" (Jan 5) and
    # "second" (Jan 20). Written without a leading zero as "2024-1-9", it
    # sorts as a STRING after "2024-01-20", because the character '1' (from
    # "2024-1-9") is greater than '0' (from "2024-01-...") at that position.
    check(
        "the true chronological order is first, third, second",
        parsed_sorted == ["first", "third", "second"],
    )
    check(
        "the raw string sort gets this WRONG -- it puts 'third' last",
        string_sorted == ["first", "second", "third"],
    )
    check(
        "the two sort orders genuinely disagree, proving the string sort is unsafe",
        string_sorted != parsed_sorted,
    )
finally:
    for f in tmpdir.iterdir():
        f.unlink()
    tmpdir.rmdir()

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("04_dates.py: every assertion held.")
