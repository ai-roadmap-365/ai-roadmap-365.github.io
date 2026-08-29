#!/usr/bin/env python3
"""csv_field_parser.py — a CSV parser built from scratch (REFERENCE).

This is the whole of RFC 4180 quoting in about fifty lines: a state
machine that walks the text one character at a time and decides, for each
character, whether it is data, a field boundary, a record boundary, or a
quote that changes the rules.

The four states
---------------
  field-start      between fields; the next character decides everything
  in-field         inside an UNQUOTED field; a comma or newline ends it
  in-quoted        inside a QUOTED field; commas and newlines are DATA
  quote-in-quoted  saw a quote while quoted; the next character says whether
                   that quote was an escaped quote ("") or the closing quote

Run this file directly to prove the parser agrees with the standard
library on the lab's deliberately messy file:

    python3 examples/csv_field_parser.py
"""
import csv
import io
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent


def parse_csv(text, delimiter=",", quotechar='"'):
    """Parse CSV text into a list of rows, each row a list of field strings.

    Implements RFC 4180 quoting: a field may be wrapped in quotes, in which
    case it may contain the delimiter, newlines, and doubled quotes ("")
    that stand for one literal quote. Carriage returns outside a quoted
    field are ignored so that CRLF and LF files parse the same way.
    """
    rows = []
    row = []
    field = []
    state = "field-start"

    for char in text:
        if state == "field-start":
            if char == quotechar:
                state = "in-quoted"
            elif char == delimiter:
                row.append("")
            elif char == "\n":
                row.append("")
                rows.append(row)
                row = []
            elif char != "\r":
                field.append(char)
                state = "in-field"

        elif state == "in-field":
            if char == delimiter:
                row.append("".join(field))
                field = []
                state = "field-start"
            elif char == "\n":
                row.append("".join(field))
                field = []
                rows.append(row)
                row = []
                state = "field-start"
            elif char != "\r":
                field.append(char)

        elif state == "in-quoted":
            if char == quotechar:
                state = "quote-in-quoted"
            else:
                field.append(char)  # commas and newlines are plain data here

        elif state == "quote-in-quoted":
            if char == quotechar:
                field.append(quotechar)  # "" means one literal quote
                state = "in-quoted"
            elif char == delimiter:
                row.append("".join(field))
                field = []
                state = "field-start"
            elif char == "\n":
                row.append("".join(field))
                field = []
                rows.append(row)
                row = []
                state = "field-start"
            elif char != "\r":
                field.append(char)
                state = "in-field"

    if field or row or state != "field-start":
        row.append("".join(field))
        rows.append(row)
    return rows


def parse_with_stdlib(text, delimiter=","):
    """Parse the same text with the standard library, for comparison."""
    return [list(row) for row in csv.reader(io.StringIO(text, newline=""), delimiter=delimiter)]


def compare(text, delimiter=","):
    """Return (mine, theirs, agree) for one blob of CSV text."""
    mine = parse_csv(text, delimiter=delimiter)
    theirs = parse_with_stdlib(text, delimiter=delimiter)
    return mine, theirs, mine == theirs


def main():
    text = (LAB_DIR / "data" / "messy_orders.csv").read_text(encoding="utf-8-sig")
    mine, theirs, agree = compare(text)
    print(f"rows parsed by the from-scratch parser: {len(mine)}")
    print(f"rows parsed by the csv module:          {len(theirs)}")
    for index, (a, b) in enumerate(zip(mine, theirs)):
        mark = "same" if a == b else "DIFFERENT"
        print(f"  row {index}: {mark}  {a}")
    print(f"agree on every row: {agree}")
    return 0 if agree else 1


if __name__ == "__main__":
    raise SystemExit(main())
