# Troubleshooting — Day 087

## `sqlite3: command not found`

macOS ships it at `/usr/bin/sqlite3`. On Debian or Ubuntu, `sudo apt install
sqlite3` installs the shell (the *library* is already there — the package you
want is the command-line one). On Fedora, `sudo dnf install sqlite`.

You can also do the whole lab through Python without the shell at all:

```bash
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

The test harness needs the shell, but takes an override if yours lives
somewhere unusual: `SQLITE3=/opt/local/bin/sqlite3 bash tests/run_tests.sh`.

## `no such table: authors`

You are pointing `sqlite3` at a database that has not been built, or at a
database that does not exist — which SQLite quietly *creates*, empty, rather
than complaining. That is the single most common source of this message: a
typo in the filename gives you a brand-new, blank database instead of an error.

Rebuild:

```bash
bash starter/01_build.sh
sqlite3 starter/library.db ".tables"
```

You should see all five table names. If `.tables` prints nothing, you are
looking at an empty file you just created by accident.

## My `FOREIGN KEY constraint failed` never happens

This is the lesson, arriving as a bug report. Foreign-key enforcement is **off
by default on every new SQLite connection**, so a `REFERENCES` clause you never
switched on is documentation, not a constraint.

```sql
PRAGMA foreign_keys;        -- prints 0 on a fresh connection
PRAGMA foreign_keys = ON;   -- and it only lasts for THIS connection
```

Three things make this bite:

1. **It is per connection.** Every new `sqlite3` invocation, every new
   `sqlite3.connect()`, starts fresh with it off. Setting it in one shell
   session does nothing for the next.
2. **It is not stored in the file.** There is no way to mark a database as
   "always enforce". The application has to say so every time it connects.
3. **It is a no-op inside an open transaction.** See the next entry.

## I set the pragma in Python and it still reads back as 0

Real behaviour, reproducible with `examples/07_foreign_keys_python.py`:

```text
connection.in_transaction: True
pragma set, but it reads back as: 0
after commit(), setting it again reads back as: 1
```

SQLite documents `PRAGMA foreign_keys` as a no-op inside a transaction, and
Python's `sqlite3` module opens transactions for you around `INSERT`, `UPDATE`
and `DELETE`. So a pragma issued after your first write is silently ignored —
no exception, no warning, just no effect.

The fix is a habit, not a workaround: **issue it as the first statement after
connecting**, before anything else touches the database.

```python
connection = sqlite3.connect("library.db")
connection.execute("PRAGMA foreign_keys = ON")   # first, always
```

## My join returns far more rows than either table has

You have written a cartesian product. Either a join condition is missing
entirely, or one of them is wrong so nothing matches the way you meant.

Count first, then look:

```sql
SELECT count(*) FROM books;                    -- 4
SELECT count(*) FROM authors;                  -- 7
SELECT count(*) FROM books CROSS JOIN authors; -- 28
```

The rule of thumb: joining N tables needs at least N−1 join conditions. Three
tables with only one `ON` clause will multiply. `examples/09_query_plans.sql`
shows what this looks like to the planner — two bare `SCAN` lines with nothing
tying them together.

## My join returns rows I did not expect to see twice

Look for a many-to-many in the path. `examples/05_joins.sql` §10 joins loans to
books to `book_authors` to authors, and Chandra Iyer appears **twice** — because
the book she has out has two authors. Three outstanding loans become four rows.

That is not a bug, and `SELECT DISTINCT` is usually the wrong fix because it
hides the question rather than answering it. Decide what one row is supposed to
mean. If it means "one loan", do not join to authors at all, or aggregate them
with `group_concat`.

## My LEFT JOIN behaves like an INNER JOIN

Almost always a predicate on the right-hand table that has migrated into the
`WHERE` clause. Once the outer join has filled the right-hand columns with
NULLs, nearly every `WHERE` test on those columns is false, and the unmatched
rows you went to the trouble of keeping get thrown away again.

```sql
-- keeps all 5 members
... LEFT JOIN loans l ON l.member_id = m.member_id AND l.returned_on IS NULL

-- keeps 4, and they are the wrong 4
... LEFT JOIN loans l ON l.member_id = m.member_id WHERE l.returned_on IS NULL
```

Run both against the seeded data (`joins.txt` §8 and §8b). The `WHERE` version
drops Dana Whitfield, who has returned everything, **and keeps Eli Nakamura**,
who has never borrowed anything — because her NULL-extended row does satisfy
`returned_on IS NULL`. Wrong in both directions at once.

The exception that is not an exception: `WHERE right_table.key IS NULL` is
deliberate. That is the anti-join idiom, and it works precisely *because* it
collapses the outer join down to the unmatched rows.

## My counts are all 1 instead of 0

`count(*)` after a `LEFT JOIN` counts rows, and the NULL-extended row for an
unmatched group is still a row. Count a column from the **right-hand** table
instead — `count(l.loan_id)` — because aggregate functions skip NULLs.

```sql
count(*)            -- Eli Nakamura: 1   wrong
count(l.loan_id)    -- Eli Nakamura: 0   right
```

## My self-join loses rows

Same cause as the LEFT JOIN entry, one level subtler. `members` joined to
itself on `referred_by` with an inner join drops everybody who was referred by
nobody — here that is Ada Okafor and Eli Nakamura, so five members become
three. Use `LEFT JOIN` unless you specifically want only the referred ones.

## `Error: near "AS": syntax error` on my self-join

Both sides of a self-join need distinct aliases, and every column reference
needs to say which alias it means:

```sql
FROM members AS m LEFT JOIN members AS r ON r.member_id = m.referred_by
```

Without the aliases SQLite cannot tell `member_id` from `member_id`.

## `database is locked`

Another process has a write transaction open — most often a `sqlite3` shell you
left sitting at its prompt in another terminal, or an editor with a database
viewer attached. Close it. Nothing in this lab writes concurrently, so if you
see this, something outside the lab is holding the file.

## The test harness fails on one section only

Read the two lines it prints under the failure: `expected:` and `actual:`. Every
value check names the query it disagrees about. The usual cause is an edited
`examples/03_seed.sql` — the checks assert exact names and counts against the
shipped data, so changing the seed changes the answers. Restore it with
`git checkout -- examples/03_seed.sql`.

## The harness passes but my own queries disagree with it

The harness builds its database in a temporary directory and removes it
afterwards. Your `starter/library.db` is a separate file, and if you ran the
anomaly script or the foreign-key script against it, it may no longer hold the
seeded data. Rebuild with `bash starter/01_build.sh`.

## Nothing works and I want to start over

```bash
rm -f starter/library.db library.db
bash starter/01_build.sh
git checkout -- starter/
```

The last line discards your exercise answers, so do it only when you mean it.
