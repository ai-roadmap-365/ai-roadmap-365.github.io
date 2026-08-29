# Day 092 lab — One Domain, Four Shapes

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Beyond Tables: NoSQL and Key-Value Stores
- **Day number:** 92 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-092-beyond-tables-nosql-and-key-value
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-092-beyond-tables-nosql-and-key-value` when the site is running.
<!-- generated-links:end -->

## Purpose

Take the library from Week 13 — the same four books, the same authors — and
store it four different ways. Then measure what each shape costs you.

That is the whole lab, and it is deliberately narrow. "NoSQL" is a word that
covers four unrelated families of database, and reading about them produces a
comfortable feeling of understanding that evaporates the moment you have to
choose one. So instead of reading, you run the same domain through every shape
you can actually execute on this machine and watch the differences appear as
numbers:

- **Relational** (Week 13's shape, as the control) — a column is a contract,
  checked at write time, and a query may filter on anything.
- **Key-value** (`dbm`, which ships with Python) — one key, one opaque blob.
  Getting by the key examines **1** key. Getting by anything else examines
  **every** key, in a loop you write yourself.
- **Documents inside the relational engine** (SQLite's JSON functions) — the
  pragmatic middle path most teams should try before adopting a second
  database.
- **A document store you build** — seventy lines over `sqlite3` giving you
  `put`, `get`, `delete`, `find` by field, and an index on an extracted field
  that turns a `SCAN` into a `SEARCH`.

Then the punchline. One book is catalogued with its title field spelled
`titel` — one character wrong. You watch **three of the four shapes accept it
without a murmur**, and you watch the catalogue query return nothing at all in
every one of them. Not an error. Not an empty database. A report that is
quietly one book short.

That silence is the lesson of the day, and it is asserted in the test suite
from both directions: the document **is** in the store, and the query **cannot
see it**. Either half alone proves nothing — a store that rejected the write
would also return zero rows.

## Learning objectives

By the end of this lab you can:

1. Model one domain in four storage shapes and state, for each, exactly which
   guarantee you gave up and what you got for it.
2. Measure the cost of a key-value store's central trade: count the keys
   examined for a lookup by key against a lookup by any other field.
3. Build a secondary index by hand over a key-value store, and demonstrate it
   going stale with no error raised — the key-value version of an orphan row.
4. Query inside a JSON document from SQL using `json_extract`, `->`, `->>` and
   `json_each`, and say what `->` and `->>` return differently.
5. Create an index on an extracted field, read `EXPLAIN QUERY PLAN` to confirm
   `SCAN` became `SEARCH`, and explain why the same index does nothing for the
   same question spelled a different way.
6. Implement a document store from first principles — `put`, `get`, `delete`,
   `find` — and name the four things it does not give you that a relational
   schema did.
7. Demonstrate schema-on-read: write a malformed document, prove it was stored,
   prove the query cannot see it, and write the audit query that finds it.
8. Interpolate a field name into SQL safely, using an allow-list, and explain
   why the value is a bound parameter and the field name cannot be.

## Prerequisites

- **Week 13** (Days 85-91). This lab assumes you can read a `CREATE TABLE`, a
  `JOIN`, and an `EXPLAIN QUERY PLAN` without being reminded what they are.
  Day 89's index material is the one that carries the most weight today.
- **Day 90** — using SQLite from Python, including bound parameters.
- **Days 43-60** — Python: dictionaries, functions, classes, and `json`.
- Comfort with a terminal, and about 30 minutes.

Nothing else. In particular, no database server, no container, no account.

## Supported operating systems

- **macOS** — captured here on macOS 26.5.2 (Apple Silicon, arm64).
- **Linux** — the same commands, unchanged. The one visible difference is which
  `dbm` backend Python picks; see `expected-output/FIELDS.md`.
- **Windows** — use WSL and follow the Linux path. `tests/run_tests.sh` is a
  bash script and uses `mktemp -d`. It was not run on native Windows here, so
  this lab claims nothing about that path rather than guessing.

## Hardware requirements

Any machine that runs Python. `examples/04_docstore.py` loads 20,000 filler
documents so that the index comparison has something to measure; that database
is a few megabytes and the script finishes in seconds. Nothing here needs a
GPU, and nothing here needs more than a few hundred megabytes of disk.

## Required software

| Tool | Version used here | Why |
| --- | --- | --- |
| `python3` | 3.14.0 | Standard library only: `sqlite3`, `dbm`, `json`, `re`, `sys`, `time`, `tempfile`, `pathlib` |
| `sqlite3` (the shell) | 3.51.0 | Runs the two `.sql` examples |

**One version floor:** SQLite **3.38.0** (2022) or newer, in both your shell and
your Python. That release made the JSON functions part of the default build and
added `->` and `->>`. Confirm all of it at once:

```bash
sqlite3 :memory: "SELECT sqlite_version(), json_extract('{\"a\":1}','\$.a'), '{\"a\":2}' ->> '\$.a', (SELECT count(*) FROM json_each('[1,2,3]'));"
```

You should see your version followed by `1|2|3`. The test suite runs the same
three probes first, so an old build fails with one clear line.

## Free and open-source options

Everything in this lab is free and open source, and that is not a compromise:

- **SQLite** is in the public domain, and its JSON support is the same feature
  PostgreSQL charges nothing for either. The middle path this lab recommends
  costs nothing to try.
- **`dbm`** is part of Python's standard library. It is a real key-value store,
  not a stand-in — bytes in, bytes out, addressed by one key — and the
  trade-off it forces on you is exactly Redis's.
- **PostgreSQL** has richer JSON support than SQLite, including a binary
  `jsonb` type. Everything you learn here transfers to it.
- **Redis**, **MongoDB**, **Cassandra** and **Neo4j** all publish free editions
  you can download and run locally. Their licences have changed more than once
  in the last few years and differ between the server, the drivers and the
  managed offerings, so check the current terms on each project's own site
  before you build on one — this lab will not quote you a licence it did not
  read today.

**None of those four servers is installed on the authoring machine, and none
was run.** The lesson describes them from their published documentation and
shows the commands you would type. This lab reproduces **no output** from any
of them, because inventing a `redis-cli` transcript would have been easy and
would have taught you a fiction. Everything captured in `expected-output/` came
from a real run of the code in this directory.

## Installation

None. There is nothing to install.

```bash
cd labs/sections/programming-with-python/day-092-beyond-tables-nosql-and-key-value
python3 --version
sqlite3 --version
```

See `requirements/README.md` for the full versions table, the reasoning behind
the version floor, and a longer account of why no client libraries appear here.

## File structure

```
day-092-beyond-tables-nosql-and-key-value/
├── README.md                  this file
├── metadata.yml               how the lab is run, and what it was run on
├── requirements/
│   ├── README.md              versions, the SQLite floor, what is deliberately absent
│   └── requirements.txt       empty of packages, on purpose
├── examples/
│   ├── library_data.py        the one domain: four books, in one place
│   ├── 01_relational.sql      shape one — the control. Exits 1 on purpose
│   ├── 02_key_value_dbm.py    shape two — a real key-value store, and its bill
│   ├── 03_json_in_sqlite.sql  shape three — documents inside the relational engine
│   ├── 04_docstore.py         shape four — the document store, built from scratch
│   └── 05_schema_on_read.py   the punchline: one misspelled book, four shapes
├── starter/
│   └── 01_exercises.py        five exercises; runs from the start, checks itself
├── tests/
│   └── run_tests.sh           67 checks; exits 0 on success, non-zero on any failure
├── expected-output/
│   ├── FIELDS.md              what must match, what may differ, and why
│   ├── relational.txt         captured
│   ├── key-value.txt          captured
│   ├── json-in-sqlite.txt     captured
│   ├── docstore.txt           captured
│   ├── schema-on-read.txt     captured
│   ├── starter-progress.txt   captured, before and after
│   └── test-run.txt           captured
├── troubleshooting.md         every error message this lab can produce
└── security.md                what it does to your machine, and the field-name allow-list
```

Every example imports its data from `examples/library_data.py`. That is what
makes the comparison honest: when two shapes disagree about what a query
returns, the difference is the shape, not the data.

## How to run

Give the examples a scratch directory rather than letting them write here:

```bash
cd labs/sections/programming-with-python/day-092-beyond-tables-nosql-and-key-value
work=$(mktemp -d)
```

Then, in this order — each step sets up the next:

```bash
# Shape one: the relational control. This exits 1 on purpose. Read why.
sqlite3 "$work/library.db" < examples/01_relational.sql

# Shape two: a real key-value store, and the cost of asking it anything
# except "give me this key".
python3 examples/02_key_value_dbm.py "$work"

# Shape three: JSON documents inside SQLite — the pragmatic middle path.
sqlite3 "$work/docs.db" < examples/03_json_in_sqlite.sql

# Shape four: the document store, from first principles, with timings.
python3 examples/04_docstore.py "$work"

# The punchline: one misspelled book, run through all four shapes.
python3 examples/05_schema_on_read.py "$work"

# Now do it yourself.
python3 starter/01_exercises.py

# And check everything.
bash tests/run_tests.sh

rm -rf "$work"
```

The test suite needs no scratch directory of its own — it makes one with
`mktemp -d` and removes it in a `trap`.

## What the commands do

**`sqlite3 "$work/library.db" < examples/01_relational.sql`** builds Week 13's
schema in miniature — five tables, a junction table for the many-to-many, three
indexes — seeds it, then asks it four questions. The fourth is the one that
matters: it inserts a book whose title column is spelled `titel`, the database
refuses it by name, and **the script exits 1**. That refusal is the control
case for the whole lab. Keep the message in mind: `table books has no column
named titel`.

**`python3 examples/02_key_value_dbm.py "$work"`** stores the same four books in
a `dbm` store, one key each, and prints the count of keys examined for three
different questions: 1 for a get by key, 4 of 4 for a filter on
`published_year`, 3 with a hand-built secondary index. Then it deletes a book,
leaves the index alone, and shows the index still pointing at a key that no
longer exists — with no error raised anywhere.

**`sqlite3 "$work/docs.db" < examples/03_json_in_sqlite.sql`** puts each whole
book in one JSON column and shows the relational engine querying inside it:
`json_extract`, the `->` and `->>` operators and how their return types differ,
`json_each` unrolling the authors array that needed a junction table an hour
ago, and then `EXPLAIN QUERY PLAN` three times — without an index (`SCAN`), with
an index on the extracted field (`SEARCH`), and for the same question spelled
with `->>` (`SCAN` again, because an expression index matches the expression and
not the intent).

**`python3 examples/04_docstore.py "$work"`** builds the store: `put`, `get`,
`delete`, `find` by field, `create_index`. It loads 20,000 filler documents,
times `find` before and after the index, and prints both plans. Then the second
half — the more valuable half — runs the four things this store does **not**
give you: no schema enforcement, no referential integrity, no join, and no
cross-document transaction unless you write one.

**`python3 examples/05_schema_on_read.py "$work"`** runs the misspelled book
through all four shapes and prints one summary table. Three columns matter: was
the write accepted, how many books are now stored, and can a query for the
title find it.

**`python3 starter/01_exercises.py`** is your turn. Five exercises, each one
line, each shipped as a **working line that is wrong in one named way** — so
the file always runs and always tells you which piece is still wrong. `0 of 5`
and exit 1 before you start; `5 of 5` and exit 0 when you are done.

**`bash tests/run_tests.sh`** runs 67 checks over all of the above.

## Expected output

Complete captures of every command are in `expected-output/`, taken from a real
run on 2026-08-16. The three moments worth reading before you run anything:

**The control case refusing the write** (`expected-output/relational.txt`):

```
--- 4. schema-on-write: a misspelled column is refused, now, loudly ---
Parse error near line 116: table books has no column named titel
```

**The key-value store's central trade** (`expected-output/key-value.txt`):

```
--- 2. get by key: one lookup, no scan ---
book:101 -> The C Programming Language (1978), shelf A3
keys examined: 1

--- 3. the same question as SQL's WHERE published_year < 1990 ---
    there is no WHERE. You write the loop.
    101  The C Programming Language
    102  The Mythical Man-Month
keys examined: 4 of 4 (every key in the store)
```

**The punchline** (`expected-output/schema-on-read.txt`):

```
store                             the write   stored  query finds it
--------------------------------  ----------  ------  --------------
relational (books table)          REFUSED     4       no
key-value (dbm)                   ACCEPTED    5       no
JSON documents in SQLite          ACCEPTED    5       no
the from-scratch document store   ACCEPTED    5       no
```

Read that last column twice. In three of the four stores the book is present
and the catalogue query cannot see it.

The timings in `expected-output/docstore.txt` — `without index: 5.779 ms`,
`with index: 0.066 ms`, `ratio: 88x` — **will differ on your machine**, and a
repeat run on the same machine gave 95x. What will not differ is the plan
changing from `SCAN documents` to `SEARCH documents USING INDEX
idx_docs_shelf`. `expected-output/FIELDS.md` lists exactly which values must
match and which are allowed to move.

## Validation steps

Work through these in order; each one is a claim you can check yourself.

1. **The control refuses the write.** Run `01_relational.sql` and confirm the
   error names `titel`, and that `SELECT count(*) FROM books` is still 4.
2. **The key-value trade is real.** In `key-value.txt`, confirm `keys examined:
   1` for the get and `keys examined: 4 of 4` for the filter. Add a fifth book
   to `library_data.py` and confirm the second number becomes 5 while the first
   stays 1.
3. **A hand-built index goes stale silently.** Confirm the last section reports
   `ids in that index with no book left in the store: [102]` and
   `no error was raised at any point`.
4. **`->` and `->>` differ.** In `json-in-sqlite.txt` section 2, confirm
   `arrow_type` is `text` and `arrow2_type` is `integer`.
5. **The index changes the plan.** Confirm `SCAN documents` in section 5 and
   `SEARCH documents USING COVERING INDEX idx_documents_shelf` in section 6.
6. **And matches the expression, not the intent.** Confirm section 7 says
   `SCAN documents` for the `->>` spelling of the same filter.
7. **The store is fast for the right reason.** In `docstore.txt`, confirm the
   plan changed *and* that `find` returned 50 documents both times. An index
   changes speed, never results.
8. **The malformed document is stored.** Confirm
   `get('book:105') -> ['authors', 'book_id', 'published_year', 'shelf',
   'titel']`.
9. **And invisible.** Confirm the title query for it returns `[]`, and that
   `find('shelf', 'C1')` still finds it — the document is there, it is the
   *title* that is unreachable.
10. **The audit finds it.** Solve exercise 5 and confirm
    `keys_without_a_title()` returns `['book:105']`. That query is the whole of
    what you have instead of a schema.

## Tests

```bash
bash tests/run_tests.sh
echo "exit=$?"
```

Expect:

```
67 checks, 0 failure(s).
exit=0
```

The suite checks real values, not file existence. It runs every example, reads
answers back out of the databases rather than out of the transcripts, and
asserts them. Section 5 asserts the punchline from both directions — the
document is stored **and** the query returns zero rows — because either half
alone would also be true of a store that had rejected the write.

Two properties worth knowing about:

- **It proves it can fail.** Section 6 solves the starter, confirms `5 of 5`,
  then deliberately leaves one exercise unsolved and asserts the checker
  reports `4 of 5`. A checker that cannot fail proves nothing.
- **It asserts shapes, not milliseconds.** The index comparison asserts a floor
  of 5x and asserts the plan changed from `SCAN` to `SEARCH`. A test that
  asserted "0.066 ms" would be flaky on your machine and would be asserting the
  wrong thing anyway.

If a check fails, the harness prints what it expected and what it got. Find the
message in `troubleshooting.md`.

## Cleanup

```bash
rm -rf "$work"
find . -type d -name "__pycache__" -prune -exec rm -rf -- {} +
```

`tests/run_tests.sh` needs no cleanup — it builds everything under `mktemp -d`,
removes it in a `trap`, and its final section asserts that no `.db` file and no
`__pycache__` were left in this directory.

To reset your exercise work:

```bash
git checkout -- starter/
```

## Troubleshooting

`troubleshooting.md` covers every error this lab can produce, grouped by where
you hit it: setting up, the relational baseline, the key-value store, JSON in
SQLite, the from-scratch store, and the starter. The four you are most likely
to meet:

- **`no such function: json_extract`** — your SQLite predates 3.38.0.
- **`examples/01_relational.sql` exits 1** — correct, and the point of the file.
- **Your query returns zero rows and the document is definitely there** — check
  for the *field* with `IS NULL`, not for the value. `json_extract` returns
  `NULL` for a field that does not exist, and `NULL = 'anything'` is never
  true. This is today's lesson wearing the costume of a bug.
- **The plan still says `SCAN` after you created the index** — either the
  indexed expression is not the queried expression, or the table is too small
  for an index to be worth using.

## Security notes

Full detail in `security.md`. The three that matter today:

- **The field name is interpolated into SQL**, because a JSON path passed as a
  bound parameter defeats the expression index this lab is about. It is
  therefore checked against an allow-list of plain identifiers first, and the
  test suite calls `find("shelf'); DROP TABLE documents; --", "A3")` and asserts
  a `ValueError`. Values are bound parameters, always.
- **The document model moves your sensitive fields.** `members.email` as a
  column is a place you can grant, revoke, encrypt or drop. The same address
  inside a JSON blob is not: there is no column-level privilege to apply, no
  list of fields to audit, and a new field can appear without anyone noticing.
- **`dbm` never looks inside a value**, so never store a pickle you did not
  create. This lab uses `json` throughout for that reason.

Nothing here opens a socket, invokes `sudo`, or installs anything, and the test
suite asserts all three.

## Extension exercises

1. **Add a second index and watch it not help.** Index
   `json_extract(body, '$.published_year')` in the from-scratch store, then run
   `find("published_year", 1978)` and confirm `SEARCH`. Now query with a range
   (`>= 1990`) instead of equality and read the plan again.
2. **Make the stale index impossible.** Rewrite
   `02_key_value_dbm.py`'s delete so that removing a book also repairs the
   decade index. Then ask the harder question: what happens if the process dies
   between the two writes? Write down what a key-value store gives you to
   prevent that, and what it does not.
3. **Write the validator the document store lacks.** Extend `put()` so it
   raises on a document missing any of `REQUIRED_FIELDS`. Note carefully what
   you have just done: you reinvented schema-on-write, in application code,
   enforced by one function that everybody must remember to call.
4. **Then find the documents already stored before you added it.** The audit
   query from exercise 5, generalised to every required field. This is the real
   cost of schema-on-read, and it arrives months after the decision.
5. **Denormalize the loans.** Store each loan as a document with the book's
   title copied into it, so a loan report needs no join. Then change one book's
   title and count how many documents you must now update, and what happens if
   you miss one.
6. **If you have Docker**, run `docker run --rm -p 6379:6379 redis` and repeat
   `02_key_value_dbm.py`'s three questions with `redis-cli`: `SET`, `GET`, and
   then a filter on `published_year`. The third one is the interesting one —
   `KEYS *` followed by a loop, which is the same scan, and which Redis's own
   documentation warns against in production for exactly that reason. Nothing
   in this lab requires it, and no output from it is reproduced here.
7. **Draw your own system.** Pick a feature you have built or used, and decide
   which of the four shapes each part of its data wants. Most real systems use
   more than one, and the interesting work is the boundary between them.

## Navigation

- **Previous day:** Day 91 — Designing and Querying a Real Schema
  (`labs/sections/programming-with-python/day-091-designing-and-querying-a-real-schema/`).
- **Next day:** Day 93 — ORMs and SQLAlchemy
  (`labs/sections/programming-with-python/day-093-orms-and-sqlalchemy/`).
- **Week 14** — Data Formats and Pipelines
  (`labs/sections/programming-with-python/`), which begins here and ends in a
  pipeline that ingests, validates, stores and reports.
