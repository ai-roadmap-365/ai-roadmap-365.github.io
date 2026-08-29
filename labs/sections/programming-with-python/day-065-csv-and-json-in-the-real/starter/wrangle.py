#!/usr/bin/env python3
"""wrangle.py — YOUR working file: the data-wrangling pipeline.

The messy file waits for you at data/messy_orders.csv. It contains, on
purpose, every violation you will meet in the wild:

  * a byte-order mark (three invisible bytes) before the header
  * a comma inside a quoted field          ("widget, large")
  * a newline inside a quoted field        (order 1002's notes)
  * doubled quotes standing for one quote  (Alan ""Turing"" Jr.)
  * an empty field                         (order 1004 has no notes)
  * a ragged row with only three fields    (order 1005)

Your job is to load it correctly, clean it, and round-trip it to JSON and
JSON Lines without losing a byte. The pipeline in main() is written for
you; the four numbered exercises below are the pieces it calls.

Everything you write lands in out/ next to this lab. Nothing else on your
machine is touched.

Finish the exercises, then run:
    python3 starter/wrangle.py
    bash tests/run_tests.sh
"""
import csv
import json
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent


# --- step 1: the naive parser, shown failing -------------------------------

def naive_split_rows(text, delimiter=","):
    """Split each line on the delimiter — the bug factory, provided complete."""
    return [line.split(delimiter) for line in text.splitlines()]


def naive_report(text, expected_columns):
    """Return a list of (line_number, field_count) for lines naive splitting breaks.

    Line numbers start at 1, counting physical lines of the file.
    """
    # Exercise 1: PROVE THE BUG.
    # 1. Start with an empty list called broken.
    # 2. Loop over naive_split_rows(text) with enumerate(..., start=1) so you
    #    get (number, row) pairs.
    # 3. If len(row) != expected_columns, append the tuple (number, len(row)).
    # 4. Return broken.
    # When you run it you will find three bad lines — and, more unsettling,
    # that one badly parsed line has the RIGHT field count and the WRONG data.
    raise NotImplementedError("Exercise 1: implement naive_report")


# --- step 2: parse properly ------------------------------------------------

def read_rows(csv_path, encoding, delimiter):
    """Read the CSV into a list of plain dicts using csv.DictReader."""
    # Exercise 2: PARSE PROPERLY.
    # 1. open(csv_path, "r", encoding=encoding, newline="") — both keyword
    #    arguments matter. encoding is "utf-8-sig" here, which strips the
    #    byte-order mark; newline="" hands newline handling to the csv module
    #    so a quoted newline does not split a row in two.
    # 2. Build reader = csv.DictReader(handle, delimiter=delimiter).
    # 3. Return [dict(row) for row in reader]  (dict() gives you a plain dict).
    # The ragged row will come back with None for its missing values — that is
    # DictReader telling you the truth, and Exercise 3 decides what to do.
    raise NotImplementedError("Exercise 2: implement read_rows")


# --- step 3: clean ---------------------------------------------------------

def clean_row(row, config):
    """Return one tidy record: no None values, stripped text, numbers as numbers."""
    # Exercise 3: CLEAN.
    # 1. Make an empty dict called cleaned.
    # 2. For each column in config["columns"]:
    #      value = row.get(column)
    #      if value is None: use config["defaults"].get(column, "") instead
    #      store value.strip() when it is a string, otherwise value as-is
    #        (hint: isinstance(value, str))
    # 3. For each column in config["numeric_columns"], replace the stored
    #    string with float(...) of it. CSV has no types; you add them here.
    # 4. Return cleaned.
    raise NotImplementedError("Exercise 3: implement clean_row")


def clean_rows(rows, config):
    """Clean every row (provided complete)."""
    return [clean_row(row, config) for row in rows]


# --- step 4: write and read back -------------------------------------------

def write_json(records, path):
    """Write one JSON array (provided complete)."""
    path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def read_json(path):
    """Read the JSON array back (provided complete)."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_jsonl(records, path):
    """Write JSON Lines: one compact JSON object per line, no outer array."""
    # Exercise 4a: WRITE JSON LINES.
    # 1. open(path, "w", encoding="utf-8") in a with-block.
    # 2. For each record, write json.dumps(record, ensure_ascii=False) then "\n".
    #    Do NOT pass indent — a JSON Lines record must be exactly one line.
    raise NotImplementedError("Exercise 4a: implement write_jsonl")


def read_jsonl(path):
    """Read JSON Lines back, one object per non-empty line."""
    # Exercise 4b: READ JSON LINES.
    # 1. Start with an empty list called records.
    # 2. open(path, "r", encoding="utf-8") and loop over the file line by line.
    # 3. Strip each line; skip it if it is empty; otherwise append
    #    json.loads(line) to records.
    # 4. Return records.
    raise NotImplementedError("Exercise 4b: implement read_jsonl")


def write_csv(records, path, columns, delimiter):
    """Write a well-formed CSV with csv.DictWriter (provided complete)."""
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(records)


def read_csv_typed(path, columns, delimiter, numeric_columns):
    """Read a clean CSV back, restoring the numeric columns (provided complete)."""
    with open(path, "r", encoding="utf-8", newline="") as handle:
        rows = [dict(row) for row in csv.DictReader(handle, delimiter=delimiter)]
    for row in rows:
        for column in numeric_columns:
            row[column] = float(row[column])
    return rows


# --- the pipeline (provided complete) --------------------------------------

def main():
    config = json.loads((LAB_DIR / "data" / "config.json").read_text(encoding="utf-8"))
    csv_path = LAB_DIR / config["input_csv"]
    raw_text = csv_path.read_text(encoding=config["encoding"])
    delimiter = config["delimiter"]
    columns = config["columns"]

    print("=== 1. naive line.split(',') ===")
    broken = naive_report(raw_text, len(columns))
    print(f"lines whose field count is not {len(columns)}: {len(broken)}")
    for number, count in broken:
        print(f"  line {number}: {count} fields")
    naive = naive_split_rows(raw_text)
    print(f"naive row for order 1001: {naive[1]}")
    print(f"naive row for order 1003: {naive[4]}")
    print("(order 1003 has 5 fields, so the count check passes — and the data is still wrong)")

    print()
    print("=== 2. csv.DictReader ===")
    rows = read_rows(csv_path, config["encoding"], delimiter)
    print(f"records parsed: {len(rows)}")
    print(f"first key is 'order_id' (byte-order mark stripped): {list(rows[0])[0] == 'order_id'}")
    print(f"order 1002 notes: {rows[1]['notes']!r}")
    print(f"order 1003 customer: {rows[2]['customer']!r}")
    print(f"order 1005 (ragged) total: {rows[4]['total']!r}")

    print()
    print("=== 3. clean ===")
    records = clean_rows(rows, config)
    for record in records:
        print(f"  {record['order_id']} {record['customer']:<18} {record['total']:>7.2f}")

    print()
    print("=== 4. write and round-trip ===")
    out_dir = LAB_DIR / config["output_dir"]
    out_dir.mkdir(exist_ok=True)
    json_path = out_dir / config["output_json"]
    jsonl_path = out_dir / config["output_jsonl"]
    clean_csv_path = out_dir / config["output_csv"]

    write_json(records, json_path)
    write_jsonl(records, jsonl_path)
    write_csv(records, clean_csv_path, columns, delimiter)

    from_json = read_json(json_path)
    from_jsonl = read_jsonl(jsonl_path)
    from_csv = read_csv_typed(clean_csv_path, columns, delimiter, config["numeric_columns"])

    assert from_json == records, "JSON round trip lost or changed data"
    assert from_jsonl == records, "JSON Lines round trip lost or changed data"
    assert from_csv == records, "CSV round trip lost or changed data"

    print(f"wrote {json_path.name}  ({json_path.stat().st_size} bytes)")
    print(f"wrote {jsonl_path.name} ({jsonl_path.stat().st_size} bytes, {len(records)} lines)")
    print(f"wrote {clean_csv_path.name} ({clean_csv_path.stat().st_size} bytes)")
    print("round trip lossless: JSON yes, JSONL yes, CSV yes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
