#!/usr/bin/env python3
"""csv_field_parser.py — YOUR working file: a CSV parser from scratch.

You have used the csv module. Now build the part of it that matters, so
that quoting stops being magic. All of RFC 4180's quoting rules fit in one
state machine that walks the text one character at a time.

The four states
---------------
  field-start      between fields; the next character decides everything
  in-field         inside an UNQUOTED field; a comma or newline ends it
  in-quoted        inside a QUOTED field; commas and newlines are DATA
  quote-in-quoted  saw a quote while quoted; the next character says whether
                   that quote was an escaped quote ("") or the closing quote

Finish Exercise 5, then run this file. It parses the lab's messy CSV twice
— once with your parser, once with the standard library — and prints
whether they agree on every row.

    python3 starter/csv_field_parser.py
"""
import csv
import io
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent


def parse_csv(text, delimiter=",", quotechar='"'):
    """Parse CSV text into a list of rows, each row a list of field strings."""
    rows = []      # finished rows
    row = []       # fields of the row being built
    field = []     # characters of the field being built
    state = "field-start"

    for char in text:
        # Exercise 5: THE QUOTING STATE MACHINE.
        #
        # Handle each state in turn. The rules, in full:
        #
        # state == "field-start"
        #   char is the quote character -> state becomes "in-quoted"
        #   char is the delimiter       -> the field was empty: row.append("")
        #   char is "\n"                -> empty last field, end the row:
        #                                  row.append(""), rows.append(row), row = []
        #   char is "\r"                -> ignore it (so CRLF and LF agree)
        #   anything else               -> field.append(char); state = "in-field"
        #
        # state == "in-field"
        #   char is the delimiter -> finish the field:
        #        row.append("".join(field)); field = []; state = "field-start"
        #   char is "\n"          -> finish the field AND the row, then
        #        rows.append(row); row = []; state = "field-start"
        #   char is "\r"          -> ignore it
        #   anything else         -> field.append(char)
        #
        # state == "in-quoted"      <-- the state that makes CSV work
        #   char is the quote character -> state = "quote-in-quoted"
        #   anything else               -> field.append(char)
        #        Yes, ANYTHING: commas and newlines are ordinary data in here.
        #        That single line is why hand-splitting on commas is a bug.
        #
        # state == "quote-in-quoted"
        #   char is the quote character -> "" means one literal quote:
        #        field.append(quotechar); state = "in-quoted"
        #   char is the delimiter -> the quoted field ended; finish the field
        #        and go back to "field-start"
        #   char is "\n"          -> the quoted field and the row both ended
        #   char is "\r"          -> ignore it
        #   anything else         -> stray text after a closing quote; the
        #        forgiving choice is field.append(char); state = "in-field"
        raise NotImplementedError("Exercise 5: implement the state machine")

    # Flush the final field/row when the text does not end with a newline.
    if field or row or state != "field-start":
        row.append("".join(field))
        rows.append(row)
    return rows


def parse_with_stdlib(text, delimiter=","):
    """Parse the same text with the standard library, for comparison (provided)."""
    return [list(row) for row in csv.reader(io.StringIO(text, newline=""), delimiter=delimiter)]


def compare(text, delimiter=","):
    """Return (mine, theirs, agree) for one blob of CSV text (provided)."""
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
