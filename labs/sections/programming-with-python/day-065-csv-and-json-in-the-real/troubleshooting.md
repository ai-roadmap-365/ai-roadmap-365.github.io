# Troubleshooting — Day 065 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old
version. Check with `python3 --version`.

## The starter raises `NotImplementedError`

Expected until you finish the five exercises. Each unfinished function
raises `NotImplementedError` on purpose so an empty function can never be
mistaken for a working one. Exercises 1–4 are in `starter/wrangle.py`;
exercise 5 is the state machine in `starter/csv_field_parser.py`.

## The first column is called `﻿order_id` and `row['order_id']` raises `KeyError`

You opened the file with `encoding='utf-8'` instead of
`encoding='utf-8-sig'`. The file begins with a byte-order mark — three
bytes, `EF BB BF` — that Excel and many Windows tools write at the start
of a UTF-8 export. Plain `utf-8` decodes those bytes into an invisible
character that becomes part of your first column name, so the name looks
right on screen and does not match anything in code. Prove it to yourself:

```bash
head -c 3 data/messy_orders.csv | xxd
python3 -c "print(repr(open('data/messy_orders.csv', encoding='utf-8').read(12)))"
python3 -c "print(repr(open('data/messy_orders.csv', encoding='utf-8-sig').read(12)))"
```

`utf-8-sig` strips the mark if it is present and is harmless if it is not,
which makes it the safe default for any file that may have come from a
spreadsheet.

## A blank line appears between every row of my output CSV

You opened the output file without `newline=''`. The `csv` writer emits
`\r\n` at the end of each record itself; if the text layer is *also*
translating `\n` into `\r\n` — which it does by default on Windows — you
get `\r\r\n` and a blank line between records. The fix is one keyword
argument, and it belongs on reading as well as writing:

```python
with open(path, "w", encoding="utf-8", newline="") as handle:
```

## A record containing a newline gets split into two rows

Same cause, other direction: you opened the input without `newline=''`.
The `csv` module has to see the raw characters so it can tell a newline
*inside* quotes (data) from a newline *between* records (a boundary). Let
the text layer chop the file into lines first and that distinction is gone
before `csv` ever sees it. Order 1002 in this lab exists to catch exactly
this bug.

## `TypeError: Object of type ... is not JSON serializable`

JSON has only six kinds of value — object, array, string, number, `true`
/ `false`, and `null` — so anything else must be converted first. The two
you will meet soonest are `datetime` objects and `set`s. Either convert
before dumping (`value.isoformat()`, `sorted(my_set)`) or pass a `default`
function that `json.dumps` calls for anything it does not recognise:

```python
json.dumps(record, default=str)
```

## `AttributeError: 'NoneType' object has no attribute 'strip'`

You hit the ragged row. Order 1005 has three fields where the header
promises five, so `DictReader` fills the two missing keys with `None`.
That is `DictReader` being honest, and Exercise 3 is where you decide
what a missing value means — here, the defaults from `config.json`. Check
`if value is None` before you call a string method on it.

## `json.decoder.JSONDecodeError: Expecting value: line 1 column 1`

Something that is not JSON reached `json.loads`. The usual causes: an
empty line in a JSON Lines file (skip blank lines — `read_jsonl` does), a
file written with `indent=` being read one line at a time (indented JSON
is *not* JSON Lines), or a trailing comma or comment left in a hand-edited
config file. JSON allows neither comments nor trailing commas, no matter
how reasonable they look.

## My from-scratch parser disagrees with the `csv` module

Read the disagreement rather than guessing — the comparison prints both
rows side by side. Three mistakes account for almost all of them:

- Treating a comma as a separator while in the `in-quoted` state. Inside
  quotes, a comma is data. So is a newline.
- Forgetting the `quote-in-quoted` state. A quote inside a quoted field is
  ambiguous until you see the *next* character: another quote means one
  literal quote, a comma or newline means the field ended.
- Never flushing the final field. If the text does not end with a newline,
  the last field is still sitting in your accumulator when the loop ends.

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly, as the README shows:
`bash tests/run_tests.sh`. You do not need to `chmod +x` anything.

## I want to start over

Delete the generated directory and restore the starter from git:

```bash
rm -rf out
git checkout -- starter/
```
