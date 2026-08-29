#!/usr/bin/env python3
"""wrangle.py — the finished data-wrangling pipeline (REFERENCE).

Reads a deliberately messy CSV (byte-order mark, embedded commas, a quoted
newline, doubled quotes, an empty field, a ragged row), proves that naive
splitting on commas mangles it, parses it properly with csv.DictReader,
cleans it against a JSON config, writes it back out as JSON, JSON Lines,
and a well-formed CSV, and then reloads each of those to prove the round
trip is lossless.

    python3 examples/wrangle.py

Everything it writes lands in out/ next to this lab; nothing else on your
machine is touched.
"""
import csv
import json
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent


# --- step 1: the naive parser, shown failing -------------------------------

def naive_split_rows(text, delimiter=","):
    """Split each line on the delimiter — the bug factory, kept for contrast."""
    return [line.split(delimiter) for line in text.splitlines()]


def naive_report(text, expected_columns):
    """Return a list of (line_number, field_count) for lines naive splitting breaks."""
    broken = []
    for number, row in enumerate(naive_split_rows(text), start=1):
        if len(row) != expected_columns:
            broken.append((number, len(row)))
    return broken


# --- step 2: parse properly ------------------------------------------------

def read_rows(csv_path, encoding, delimiter):
    """Read the CSV into a list of dicts using csv.DictReader.

    encoding='utf-8-sig' strips a leading byte-order mark if one is there.
    newline='' is required: the csv module does its own newline handling,
    and without it a quoted field containing a newline can be split in two.
    """
    with open(csv_path, "r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        return [dict(row) for row in reader]


# --- step 3: clean ---------------------------------------------------------

def clean_row(row, config):
    """Return one tidy record: no None values, stripped text, numbers as numbers."""
    cleaned = {}
    for column in config["columns"]:
        value = row.get(column)
        if value is None:
            value = config["defaults"].get(column, "")
        cleaned[column] = value.strip() if isinstance(value, str) else value
    for column in config["numeric_columns"]:
        cleaned[column] = float(cleaned[column])
    return cleaned


def clean_rows(rows, config):
    """Clean every row."""
    return [clean_row(row, config) for row in rows]


# --- step 4: write and read back -------------------------------------------

def write_json(records, path):
    """Write one JSON array. indent=2 for humans; ensure_ascii=False keeps text readable."""
    path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def read_json(path):
    """Read the JSON array back."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_jsonl(records, path):
    """Write JSON Lines: one compact JSON object per line, no outer array."""
    with open(path, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path):
    """Read JSON Lines back, one object per non-empty line."""
    records = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_csv(records, path, columns, delimiter):
    """Write a well-formed CSV with csv.DictWriter — it quotes whatever needs it."""
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(records)


def read_csv_typed(path, columns, delimiter, numeric_columns):
    """Read a clean CSV back, restoring the numeric columns (CSV has no types)."""
    with open(path, "r", encoding="utf-8", newline="") as handle:
        rows = [dict(row) for row in csv.DictReader(handle, delimiter=delimiter)]
    for row in rows:
        for column in numeric_columns:
            row[column] = float(row[column])
    return rows


# --- the pipeline ----------------------------------------------------------

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
