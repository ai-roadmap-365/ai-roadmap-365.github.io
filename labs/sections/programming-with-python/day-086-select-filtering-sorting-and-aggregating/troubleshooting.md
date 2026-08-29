# Troubleshooting

Almost every problem in this lab is the same problem wearing a different hat:
the query ran, it printed something, and the something was wrong. SQL will not
warn you. These are the shapes that mistake takes.

## `sqlite3: command not found`

The shell is not installed. On macOS it ships with the system; on Debian and
Ubuntu the shell is a separate package from the library, so `import sqlite3`
can work in Python while the command does not exist:

```bash
sudo apt install sqlite3      # Debian, Ubuntu
sudo dnf install sqlite       # Fedora
```

`tests/run_tests.sh` checks for it first and stops with that instruction rather
than failing halfway through.

## `Error: unable to open database file`

You are not in the lab directory, or the database has not been built. Both are
fixed the same way:

```bash
cd labs/sections/programming-with-python/day-086-select-filtering-sorting-and-aggregating
bash examples/build_db.sh
```

Every command in this lab's README is written to be run from the lab directory,
and every path in it is relative to that directory.

## `Error: no such table: books`

You opened a database that exists but is empty. That happens when you type a
database name SQLite has never seen: `sqlite3 libary.db` (note the typo) does
not fail — it cheerfully creates a brand-new empty file with that name. Delete
the stray file and rebuild:

```bash
ls *.db examples/*.db
rm -f examples/library.db
bash examples/build_db.sh
```

## A query returns 0 rows and you are sure it should not

Nine times out of ten in this lab, a NULL is involved. Work through these in
order:

1. Are you comparing to NULL with `=` or `<>`? Both are UNKNOWN for every row,
   and `WHERE` keeps only rows where the predicate is TRUE. Use `IS NULL` or
   `IS NOT NULL`.
2. Is the column you filtered on nullable, and did you write a negative filter?
   `WHERE city <> 'Pune'` silently drops every member whose city is NULL. Write
   `WHERE city IS NULL OR city <> 'Pune'` when you mean to keep them.
3. Are you using `NOT IN` on a nullable column? Same trap, same fix.
4. Did you use `GLOB` when you meant `LIKE`? `GLOB` is case-sensitive and uses
   `*` and `?`; `LIKE` folds case for ASCII letters and uses `%` and `_`.

To see it rather than reason about it:

```bash
sqlite3 -header -column examples/library.db < examples/queries/03-null-traps.sql
```

## `Error: in prepare, misuse of aggregate: COUNT()`

You put an aggregate in `WHERE`. `WHERE` runs before the rows are grouped, so at
that moment there is no group for `COUNT(*)` to count. The clause that filters
groups is `HAVING`:

```sql
-- rejected
SELECT author, COUNT(*) FROM books WHERE COUNT(*) > 3 GROUP BY author;
-- correct
SELECT author, COUNT(*) FROM books GROUP BY author HAVING COUNT(*) > 3;
```

## A `SELECT` alias used in `WHERE` works here and breaks somewhere else

This is the trap in reverse, and it is worth reading carefully because it is the
one that costs you a day rather than a minute.

`WHERE` is evaluated before `SELECT`, so by the rules of standard SQL an alias
invented in the `SELECT` list does not exist yet and a query using it in `WHERE`
must be rejected. PostgreSQL rejects it. SQLite **accepts** it, as a documented
extension. Verified on the authoring machine with sqlite3 3.51.0:

```console
$ sqlite3 examples/library.db 'SELECT title, pages*2 AS reading_minutes FROM books WHERE reading_minutes > 800;'
Grammar of Machines|960
Salt and Longitude|1056
The Lost Cartographers|1224
Continental Drift Blues|842
Coasts of Elsewhere|910
The Long Instrument|1024
```

So the query you wrote today runs perfectly, and the same file moved to
PostgreSQL next year does not. If you want the query to be portable, repeat the
expression or wrap it — both are accepted everywhere:

```sql
-- portable, repeating the expression
SELECT title, pages*2 AS reading_minutes FROM books WHERE pages*2 > 800;
-- portable, computing it in an inner query first
SELECT * FROM (SELECT title, pages*2 AS reading_minutes FROM books)
WHERE reading_minutes > 800;
```

`ORDER BY` is the opposite case: using an alias there is standard SQL and works
on every engine, precisely because `ORDER BY` runs after `SELECT`.

## `ORDER BY ... NULLS LAST` is rejected

Your SQLite predates 3.30 (2019). Use the portable form, which works on every
version and on other engines too:

```sql
ORDER BY rating IS NULL, rating ASC
```

`rating IS NULL` evaluates to 0 for the rows that have a value and 1 for the
rows that do not, so sorting on it ascending puts the real values first.

## An average looks too low

You almost certainly wrapped the column in `COALESCE(col, 0)`. That does not
"handle" the missing ratings; it invents four books rated zero and mixes them
into the arithmetic. In this database it moves the average from **4.16** to
**3.47**, and nothing anywhere says so.

`AVG` already ignores NULLs. If you want to know how much data the average is
actually based on, ask for it:

```sql
SELECT COUNT(*) AS rows, COUNT(rating) AS rated, AVG(rating) FROM books;
```

## `bash starter/check.sh` says a numeric answer is wrong but the number looks right

Compare the text, not the value. `28` and `28.0` are different strings, and
`check.sh` compares strings because that is what the shell has. Exercise 11
requires `28.0`, which is what `JULIANDAY(...) - JULIANDAY(...)` returns — a
real number of days. If yours prints `28`, you have probably rounded or cast it.

## `bash tests/run_tests.sh` fails on a check you did not touch

The harness builds its own throwaway database under `mktemp -d` and never reads
`examples/library.db`, so it cannot be affected by anything you did to your copy.
A failure there means `examples/seed.sql`, an example query, or the answer key
has genuinely changed. Read the failing line: it prints the expected value and
the actual one side by side.

## Everything works but the lab directory has a `library.db` in it

An older command built it in the wrong place. The database belongs under
`examples/`, it is git-ignored there, and `tests/run_tests.sh` has a check that
fails if one appears in the lab root:

```bash
rm -f library.db
bash examples/build_db.sh
```

## Windows

Use WSL and follow the Linux instructions. The three shell scripts here are bash
scripts, and `mktemp -d` and `trap` behave as they do on Linux inside WSL. On
native Windows you can still run every `.sql` file by hand through the Windows
build of the `sqlite3` shell — the SQL is identical — but `tests/run_tests.sh`,
`examples/build_db.sh` and `starter/check.sh` will not run. That path has not
been executed on the authoring machine, so it is described rather than promised.
