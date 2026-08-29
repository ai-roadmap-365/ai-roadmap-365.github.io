# Troubleshooting — Day 092

Every symptom below was produced on the authoring machine while building this
lab, except where it says otherwise. Find your error message; the fix is under
it.

## Setting up

**`sqlite3: command not found`**

The shell is not installed or not on your `PATH`. macOS ships it at
`/usr/bin/sqlite3`. On Debian or Ubuntu, `sudo apt install sqlite3` — that is
the one `sudo` in this lab's world, and it is in this document rather than in
any script. If it lives somewhere unusual, tell the suite where:

```bash
SQLITE3=/opt/local/bin/sqlite3 bash tests/run_tests.sh
```

**`Error: no such function: json_extract`**

Your `sqlite3` predates 3.38.0 (2022), when the JSON functions became part of
the default build. Half this lab needs them. Check and upgrade:

```bash
sqlite3 --version
```

**`Error: near "->>": syntax error`**

The same cause, one release more precisely: `->` and `->>` also arrived in
3.38.0. Everything they do can be written with `json_extract`, so if you cannot
upgrade, section 2 of `examples/03_json_in_sqlite.sql` is the only part you
lose.

**The shell has the JSON functions but Python does not, or the reverse**

They are two different copies of SQLite. Print both:

```bash
sqlite3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

On the authoring machine they were 3.51.0 and 3.53.3. If Python's copy is the
old one, a Python installed from python.org or from your package manager will
usually be newer than a very old system Python.

## The relational baseline

**`examples/01_relational.sql` ends with `Parse error near line 116: table
books has no column named titel`, and the script exits 1**

That is correct, and it is the whole reason the file exists. The last statement
misspells a column on purpose so you watch the relational engine refuse the
write at the moment of the mistake, naming the field. Every other shape in this
lab accepts the same mistake in silence.

If that line ever *stops* appearing, something has gone wrong — the comparison
has lost its control case. The test suite asserts the refusal happens, asserts
the script exits non-zero, and asserts the table still holds exactly 4 books.

**`Error: FOREIGN KEY constraint failed` when you experiment**

Foreign keys are off by default in SQLite and `01_relational.sql` turns them on
with `PRAGMA foreign_keys = ON`. That pragma is **per connection**, so a new
`sqlite3` session starts with them off again. Re-issue it every time, which is
also the answer to "why did my delete succeed in the shell and fail in the
script".

## The key-value store

**`dbm.error: db type could not be determined`**

You pointed `dbm.open(..., "r")` at a path that is not a `dbm` file, or at one
written by a backend this Python cannot read. Delete the store and let the
script recreate it. Note the file may not be the name you expect — see below.

**The store file is not where you expected**

Different `dbm` backends create different files for the same name. `dbm.sqlite3`
creates one file, `library_kv`. `dbm.ndbm` creates `library_kv.db`. `dbm.gnu`
creates `library_kv`. This is why the scripts always pass a directory and build
the path themselves rather than globbing. Ask Python which backend you have:

```bash
python3 -c "import dbm, sys; print(dbm.whichdb(sys.argv[1]))" /path/to/library_kv
```

**`dbm.whichdb` reports something other than `dbm.sqlite3`**

Expected, and harmless. `dbm.sqlite3` became Python's default in 3.13; older
Pythons and most Linux boxes report `dbm.gnu` or `dbm.ndbm`. The value size in
bytes printed by `02_key_value_dbm.py` may differ with the backend. Nothing
else in the lab changes, and the tests match on the `dbm.` prefix rather than
the exact backend.

**`TypeError: keys must be bytes or strings`**

`dbm` stores bytes, not objects. That is the point being made: the store never
looks inside the value. Encode on the way in and decode on the way out —
`json.dumps(book).encode("utf-8")` and `json.loads(raw)`.

## JSON inside SQLite

**`CHECK constraint failed: json_valid(body)`**

You inserted text that is not JSON. Note what this constraint does and does not
do: it checks the blob *parses*, and nothing at all about which fields it has.
That is the entire remaining schema, and section 8 of the script demonstrates
it by inserting the misspelled document successfully.

**Your query returns zero rows and you are sure the document is there**

It probably is there. Check for the field rather than for the value:

```sql
SELECT doc_id FROM documents WHERE json_extract(body, '$.title') IS NULL;
```

`json_extract` returns SQL `NULL` for a field that does not exist, and `NULL =
'anything'` is never true, so a misspelled field name produces silence rather
than an error. This is the single most common way to lose time in a document
store, and it is today's lesson rather than a bug.

**Watch the quoting of `$.` in the shell**

In bash, `$.` inside double quotes is fine but `$.a` inside a double-quoted
string next to other expansions can surprise you. Prefer single quotes for the
JSON path, and escape the dollar when the whole statement is double-quoted:

```bash
sqlite3 :memory: "SELECT json_extract('{\"a\":1}', '\$.a');"
```

**The plan still says `SCAN` after you created the index**

Two causes, both instructive.

1. **The expressions do not match.** An index on
   `json_extract(body, '$.shelf')` does nothing for a query written
   `body ->> '$.shelf'`, even though the two ask the same question. Section 7
   of `examples/03_json_in_sqlite.sql` demonstrates exactly this. Index the
   expression the query actually uses.
2. **The table is tiny.** With four rows a scan is cheaper than an index lookup
   and the planner is right to say so. `examples/04_docstore.py` loads 20,000
   filler documents before it times anything, for this reason.

**`EXPLAIN QUERY PLAN` prints a `QUERY PLAN` header line**

It does in the shell. When you are matching output, take the last line. The
test suite does exactly that.

## The from-scratch document store

**`ValueError: not a safe field name`**

The allow-list did its job. Field names are interpolated into SQL text, so they
must be plain identifiers. If you hit this with a legitimate field name
containing a dot or a space, you have found the real limitation of this
seventy-line store, and the honest fix is a nested-path implementation that
still validates every segment — not a wider regular expression.

**`sqlite3.OperationalError: database is locked`**

Two connections are writing at once, or a previous run left a connection open.
Close the store (`store.close()`), or point the script at a fresh directory.

**The timings are nothing like the captured ones**

Expected. The capture reads `without index: 5.779 ms`, `with index: 0.066 ms`,
`ratio: 88x`; a repeat run on the same machine gave 95x. Disk, CPU and load all
move it. The suite asserts a floor of 5x and asserts the plan changes from
`SCAN` to `SEARCH`, because those are the facts, and the millisecond figure is
one machine on one day.

If your ratio is close to 1x, the index is not being used — go back to the
`SCAN` entry above.

## The starter

**It prints five `not yet` lines and exits 1 before you have touched it**

Correct. Every exercise ships as a working line that is wrong in one named way,
so the file always runs and always tells you which piece is still wrong. You are
looking for `5 of 5 exercises complete.` and exit 0.

**Exercise 3 stays `not yet` even though an index was created**

You created an index on the wrong expression. `CREATE INDEX ... ON documents
(key)` succeeds — `key` is a real column — and does nothing for a query
filtering on `json_extract(body, '$.shelf')`. Index the same expression the
query uses.

**Exercise 5 returns an empty list and you are sure the document is missing a
title**

`WHERE json_extract(body, '$.title') = NULL` is never true. Use `IS NULL`.

## Windows

Use WSL and follow the Linux instructions. `tests/run_tests.sh` is a bash
script and depends on `mktemp -d`. It was not run on native Windows here, so
this lab claims nothing about that path rather than guessing.
