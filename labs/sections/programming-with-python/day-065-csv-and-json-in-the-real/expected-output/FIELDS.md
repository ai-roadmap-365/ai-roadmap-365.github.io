# Expected output — Day 065 lab

These are real captured runs from the authoring machine (macOS 26.5.1,
Apple Silicon, Python 3.14.0, bash 3.2, 2026-07-19). Every step is
deterministic: the same input file produces the same records, the same
byte counts, and the same exit codes on any platform Python 3 runs on.

## Files

- `sample-run.txt` — the reference pipeline driven end to end
  (`python3 examples/wrangle.py`), the from-scratch parser compared
  against the standard library (`python3 examples/csv_field_parser.py`),
  the first three bytes of the input file shown as hex so the byte-order
  mark is visible, and the two generated files printed.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the
  starter still unfinished (26 checks, 0 failures, exit 0). Absolute paths
  are shown as `<repo>`; on your machine they are your real path.

## What the input file contains

`data/messy_orders.csv` is 288 bytes and holds **6 records spread over 7
physical lines** — the mismatch is the whole point.

| Trap | Where | What a correct parser must do |
| --- | --- | --- |
| Byte-order mark (`EF BB BF`) | first three bytes | strip it, so the first column is named `order_id`, not `﻿or der_id` |
| Comma inside a quoted field | order 1001, `"widget, large"` | keep it as one field |
| Newline inside a quoted field | order 1002, notes | keep both lines in one field; the record spans two physical lines |
| Doubled quotes | order 1003, `"Alan ""Turing"" Jr."` | collapse `""` to one `"` |
| Empty field | order 1004, notes | produce `''`, not `None` |
| Ragged row (3 fields, not 5) | order 1005 | produce `None` for the two missing keys |

## Required behaviour on every platform

| Call | Result |
| --- | --- |
| `naive_report(text, 5)` | `[(2, 6), (4, 2), (7, 3)]` |
| `naive_split_rows(text)[4][1]` | `'"Alan ""Turing"" Jr."'` — right field count, wrong data |
| `read_rows(path, 'utf-8-sig', ',')` | 5 dicts; `list(rows[0])[0] == 'order_id'` |
| `rows[0]['items']` | `'widget, large'` |
| `rows[1]['notes']` | `'Leave at door.\nRing the bell twice.'` |
| `rows[2]['customer']` | `'Alan "Turing" Jr.'` |
| `rows[4]['notes']`, `rows[4]['total']` | `None`, `None` |
| `clean_rows(rows, config)[4]` | `notes == ''`, `total == 0.0` (a float) |
| `clean_rows(rows, config)[0]['total']` | `49.5` (a float, not the string `'49.50'`) |
| `read_json(write_json(records))` | equal to `records` |
| `read_jsonl(write_jsonl(records))` | equal to `records`, and the file has exactly 5 lines |
| `read_csv_typed(write_csv(records))` | equal to `records` |
| `parse_csv(text)` (from scratch) | equal to `csv.reader` output on all 6 rows |
| `parse_csv('a,"say ""hi""",d\n')` | `[['a', 'say "hi"', 'd']]` |
| `parse_csv('a,b\r\nc,d\r\n')` | `[['a', 'b'], ['c', 'd']]` |

## Generated files

Running `python3 examples/wrangle.py` creates `out/` with three files:

| File | Size | Shape |
| --- | --- | --- |
| `orders.json` | 703 bytes | one indented JSON array of 5 objects |
| `orders.jsonl` | 565 bytes | 5 lines, one compact JSON object each |
| `orders-clean.csv` | 289 bytes | header plus 5 records over 6 physical lines, re-quoted by `DictWriter` |

The JSON Lines file is smaller than the JSON array here purely because it
carries no indentation; the important difference is that it can be read
one line at a time.

## Platform notes

- The only visible difference between platforms is the shell prompt (`$`)
  shown before each command; the program's own output is identical.
- The `xxd` command used to show the byte-order mark is present on macOS
  and most Linux distributions. If yours lacks it, use
  `od -An -tx1 -N3 data/messy_orders.csv`, which prints `ef bb bf`.
- `orders-clean.csv` is written with `newline=''`, so it uses `\r\n`
  record terminators on every platform (that is what RFC 4180 asks for and
  what the `csv` module writes by default). Its byte count is therefore
  the same everywhere. Counting its bytes is instructive: the file holds
  **6 CRLF pairs and exactly one lone LF** — the six record terminators,
  plus the newline that lives *inside* order 1002's quoted notes field and
  was carried through untouched.
- Floating-point values round-trip exactly here because every total in the
  file is representable in binary (`49.5`, `12.0`, `240.0`, `3.25`,
  `0.0`). That is deliberate — a value like `0.1` would still round-trip
  through JSON, but printing it can surprise you.
