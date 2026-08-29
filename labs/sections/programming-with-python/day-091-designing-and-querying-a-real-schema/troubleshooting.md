# Troubleshooting — Day 091

Grouped by the message you actually see. If your problem is not here, run
`bash tests/run_tests.sh` first: it prints what it expected and what it got for
every value it compares, which usually names the problem for you.

## Setting up

**`sqlite3: command not found`**
Install it (`apt install sqlite3`, `brew install sqlite`, or use the copy
already at `/usr/bin/sqlite3` on macOS), or point the scripts at the one you
have: `SQLITE3=/path/to/sqlite3 bash tests/run_tests.sh`.

**`near "OVER": syntax error`**
Your `sqlite3` is older than 3.25.0 (2018) and has no window functions.
Questions 6, 7 and 8 cannot be written this way without them. Check with
`sqlite3 --version`. The test suite runs `SELECT row_number() OVER ()` as its
first check specifically so this fails with one clear line instead of a wall of
errors. Python's bundled SQLite is usually newer than the shell's — compare
them with `python3 -c "import sqlite3; print(sqlite3.sqlite_version)"`.

**`no such table: books` when you run the questions**
The schema has not been built into the database you are querying, or you built
it into a different file. SQLite silently *creates* an empty database from a
mistyped filename rather than complaining, which is the single most common
cause. Check with `sqlite3 library.db ".tables"` before assuming your schema
failed.

## Building the schema

**`Parse error: near ")": syntax error` in a `CREATE TABLE`**
Almost always a trailing comma after the last column or constraint. SQLite
points at the closing bracket, not at the comma.

**`Parse error: unrecognized token: "'"`**
An unclosed quote earlier in the file. Everything after it is being read as one
enormous string, so the error appears a long way from the cause.

**Your `CHECK` constraint is accepted but never fires**
Two likely causes. A column-level `CHECK` can only see its own column — a rule
comparing `due_at` with `borrowed_at` has to be a *table-level* constraint,
written after all the columns. And `CHECK (x <> 'bad')` is unknown, not false,
when `x` is NULL, so it lets the row through; write
`CHECK (x IS NULL OR x <> 'bad')` if that is not what you meant.

**`CHECK constraint failed` on a timestamp you think is fine**
The shape check is `LIKE '____-__-__T__:__:__Z'` — exactly four, two, two,
two, two, two characters with a literal `T` and a literal `Z`. `2026-8-16` has
one digit where two are required. `2026-08-16 09:00:00` uses a space instead of
a `T`. Both are refused, on purpose: the format is the reason string comparison
is chronological comparison, and one row in a different shape breaks every
range query silently.

**`FOREIGN KEY constraint failed` while seeding**
Rows are being inserted before their parents. The seed file inserts categories,
then authors, then books, then credits, then members, then loans, then
reservations, in that order, for exactly this reason. Inside a transaction you
can also defer the check, but ordering the inserts is simpler.

**No error at all when you insert an obviously broken row**
`PRAGMA foreign_keys` is off. It is off by default on every new connection, it
is not stored in the database file, and it is a documented no-op inside an open
transaction (Day 87). Issue it as the first statement after connecting.
`PRAGMA foreign_key_check` will list orphan rows that are already there.

## The queries

**Question 1 reports 8 books instead of 7**
The soft-delete filter is missing: `WHERE withdrawn_at IS NULL`, or use the
`current_collection` view. This is the running cost of soft delete, and it does
not raise an error — it just quietly reports a number that is wrong.

**Question 6 is missing the member who has borrowed nothing**
An `INNER JOIN` where a `LEFT JOIN` was needed. She has no loan rows, so an
inner join has nothing to give her. Day 87, arriving with a bill.

**Question 6 reports 1 loan for that member instead of 0**
`count(*)` counts rows, and the outer join manufactured one NULL-filled row for
her. `count(l.loan_id)` counts non-NULL values of that column, and aggregate
functions skip NULLs, so it correctly reports 0.

**`misuse of window function ROW_NUMBER()`**
A window function cannot appear in a `WHERE` clause or inside an aggregate. It
is computed after `WHERE` and after `GROUP BY`, so to filter on its result you
have to compute it in a subquery or CTE and filter in the query outside. That is
why questions 6 and 8 are both written as two steps.

**`SUM ... OVER` gives the same number on every row**
The `ORDER BY` inside the `OVER (...)` is missing. Without it there is no
ordering to accumulate along, so every row gets the total of the whole
partition. With it, the default frame is everything up to and including the
current row — a running total.

**Your recursive CTE returns only one row**
The recursive part is not finding children. Check the direction of the join: it
should be `categories c JOIN subtree s ON c.parent_id = s.category_id`, reading
"c is a child of something already found". Reversing it walks upwards to the
root instead, which is a perfectly good query for a different question.

**Your recursive CTE never finishes**
There is a cycle in the data, or the recursive part has no condition that
eventually stops matching. The schema's
`CHECK (parent_id IS NULL OR parent_id <> category_id)` blocks the
one-row cycle, but not a longer one. Carrying a `depth` column and adding
`WHERE s.depth < 10` to the recursive part is the cheap, honest guard.

**Question 5's total is 7.099999999999999**
Money left integer arithmetic somewhere. Sum `fine_pence` as integers and divide
by 100 exactly once, at the point of display. Day 70's floating-point lesson is
the reason.

**Question 4 says a loan is 0 days overdue when it is clearly late**
`CAST(... AS INTEGER)` truncates towards zero, so anything under 24 hours late
is 0 whole days. That is what "whole days" means. If you want it to round up,
use `CAST(... AS INTEGER) + 1` only when the fractional part is non-zero, and be
explicit about which one the library's fine policy actually uses — this is the
kind of question worth asking before writing the query rather than after.

## The report script

**`no such database: library.db`**
Build it first: `sqlite3 library.db < examples/01_schema.sql` then
`sqlite3 library.db < examples/02_seed.sql`. The script refuses to run against
a missing file rather than creating an empty one, which is the opposite of what
the `sqlite3` shell does and is deliberate.

**`sqlite3.OperationalError: no such column: full_name`**
The report reads rows by name through `sqlite3.Row`, so the column names in the
`SELECT` and the names in the formatting code have to agree. If you renamed a
column in your schema, rename it in the repository method's `AS` clause too.

**The overdue answers change every time you run it**
Something is reading a clock. Nothing here should: the instant is a parameter
with a default of `2026-08-16T09:00:00Z`. The test suite checks that the script
never imports `datetime` at all.

## The checkers

**`0 of 16 exercises complete.` with a wall of parse errors**
That is the correct starting state. The seed cannot load into a schema whose
tables do not exist yet, so the ten question checks cannot run. Work down
`starter/01_schema.sql` and they will start reporting.

**The checker says your answer does not match, but it looks right**
The comparison is exact, including column order and row order. Re-read the
`Columns:` and `Order:` lines in the comment above the exercise. Extra columns
count as a mismatch even when the rows are correct.

**`03_check.sh` reports the schema as done but the questions all fail**
Your column names differ from the ones the shared seed inserts into, so the
seed loaded into a table shaped differently from what the queries expect. The
column names are fixed for exactly this reason; the design decisions around them
are yours.

## Windows

`tests/run_tests.sh` and `starter/03_check.sh` are bash scripts and use
`mktemp -d`, so run them under WSL and follow the Linux instructions. Neither
was run on native Windows when the expected output was captured, and none is
claimed for it.
