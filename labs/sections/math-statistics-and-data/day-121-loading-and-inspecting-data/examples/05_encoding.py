"""Exercise 5 -- encoding: pandas assumes UTF-8, and a mismatch fails loudly.

Run: python3 05_encoding.py

read_csv()'s `encoding` parameter defaults to UTF-8. A file actually
written in a different encoding -- latin-1 (ISO-8859-1) is common in older
exports from Windows and legacy databases -- either raises a
UnicodeDecodeError on the first byte sequence it cannot interpret as valid
UTF-8, or, when the byte sequence HAPPENS to also be valid (but different)
UTF-8, decodes into visibly wrong characters ("mojibake") with no error at
all. Only naming the correct encoding round-trips the text exactly.
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


ORIGINAL_NAME = "José"  # "José"
ORIGINAL_CITY = "São Paulo"  # "São Paulo"

tmpdir = Path(tempfile.mkdtemp(prefix="d121-ex05-"))
try:
    csv_path = tmpdir / "customers_latin1.csv"
    # Written deliberately in latin-1, the encoding this file actually is.
    csv_path.write_text(f"name,city\n{ORIGINAL_NAME},{ORIGINAL_CITY}\n", encoding="latin-1")

    error_class = None
    error_message = ""
    try:
        pd.read_csv(csv_path, encoding="utf-8")
    except UnicodeDecodeError as exc:
        error_class = type(exc).__name__
        error_message = str(exc)
    print(f"reading with encoding='utf-8' (WRONG for this file): {error_class}: {error_message}")

    check(
        "reading a latin-1 file as UTF-8 raises UnicodeDecodeError -- it does not silently succeed",
        error_class == "UnicodeDecodeError",
    )

    correct = pd.read_csv(csv_path, encoding="latin-1")
    print("\nreading with encoding='latin-1' (correct for this file):")
    print(correct)

    check(
        "reading with the correct encoding recovers the accented name exactly",
        correct.loc[0, "name"] == ORIGINAL_NAME,
    )
    check(
        "reading with the correct encoding recovers the accented city exactly",
        correct.loc[0, "city"] == ORIGINAL_CITY,
    )

    # pandas' default (no encoding= given) is UTF-8, and fails the same way
    # on this file -- confirming the parameter's documented default rather
    # than merely asserting it.
    default_error_class = None
    try:
        pd.read_csv(csv_path)
    except UnicodeDecodeError as exc:
        default_error_class = type(exc).__name__
    check(
        "the undecorated default (no encoding= argument) behaves identically to encoding='utf-8'",
        default_error_class == "UnicodeDecodeError",
    )
finally:
    for f in tmpdir.iterdir():
        f.unlink()
    tmpdir.rmdir()

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("05_encoding.py: every assertion held.")
