"""Exercise 1 -- the Namibia trap: read_csv() as an inference engine.

Run: python3 01_the_namibia_trap.py

pandas' default na_values list includes the literal string "NA". A country
code column containing "NA" for Namibia is read, by default, as a MISSING
value -- not an error, not a warning, just a quiet substitution. The country
does not disappear loudly; every downstream count of "missing" data is now
wrong in a way no test catches unless you already knew to look for it.
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


tmpdir = Path(tempfile.mkdtemp(prefix="d121-ex01-"))
try:
    csv_path = tmpdir / "country_codes.csv"
    csv_path.write_text("code,country\nNA,Namibia\nUS,United States\nFR,France\n")

    default = pd.read_csv(csv_path)
    print("default read:")
    print(default)

    kept = pd.read_csv(csv_path, keep_default_na=False)
    print("\nkeep_default_na=False:")
    print(kept)

    check(
        "the default read turns Namibia's 'NA' into a real missing value",
        pd.isna(default.loc[0, "code"]),
    )
    check(
        "the default read leaves the OTHER two codes untouched",
        default.loc[1, "code"] == "US" and default.loc[2, "code"] == "FR",
    )
    check(
        "keep_default_na=False keeps 'NA' as the literal string",
        kept.loc[0, "code"] == "NA" and isinstance(kept.loc[0, "code"], str),
    )
    check(
        "keep_default_na=False does not turn anything else into a string it wasn't",
        kept.loc[1, "code"] == "US" and kept.loc[2, "code"] == "FR",
    )
    # The row count is identical either way -- the row never disappeared,
    # only the value inside one cell of it silently changed meaning.
    check("both reads keep all three rows", len(default) == 3 and len(kept) == 3)
finally:
    for f in tmpdir.iterdir():
        f.unlink()
    tmpdir.rmdir()

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("01_the_namibia_trap.py: every assertion held.")
