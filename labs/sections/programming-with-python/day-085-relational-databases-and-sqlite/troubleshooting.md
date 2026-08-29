# Troubleshooting — Day 085

Most first-day database problems are one of five things. Each entry below says
what you will see, what is actually happening, and what to do.

## `sqlite3: command not found`

The shell is not installed or not on your `PATH`. macOS ships it. On Debian or
Ubuntu, `sudo apt install sqlite3`; on Fedora, `sudo dnf install sqlite`. On
Windows, use WSL and follow the Linux path.

You still have the engine either way: `python3 -c "import sqlite3"` works
without the shell, because the Python module carries its own copy of the
library. Only the dot-command walkthrough needs the shell.

## `sqlite3 --version` and Python disagree

They are allowed to. On the authoring machine the shell reports 3.51.0 and
Python reports 3.53.3. The two are separate programs that each link their own
copy of SQLite; both read and write the same file format, and neither is
wrong. This is a fact worth knowing rather than a fault to fix — see
`requirements/README.md`.

The version that matters is the one belonging to whichever program you are
running. If a feature works in one and not the other, check that program's
number, not the machine's.

## `Runtime error: FOREIGN KEY constraint failed`

This is the lab working. It means you tried to write a loan naming a member or
a book that does not exist, and the database refused. Look at the id you used.

The opposite problem is more interesting: if the *same* bad write is
**accepted**, your connection has foreign keys switched off. SQLite defaults
`PRAGMA foreign_keys` to OFF for backward compatibility, and it is a
**per-connection** setting — not a property of the file, and not remembered
between sessions. Turn it on at the top of every script and every connection:

```sql
PRAGMA foreign_keys = ON;
```

```python
connection.execute("PRAGMA foreign_keys = ON")
```

A `REFERENCES` clause with foreign keys off is a comment.

## `Runtime error: UNIQUE constraint failed: books.book_id`

You applied `seed.sql` twice. The primary key rejects the second copy, which is
exactly its job. Start clean:

```bash
rm -f library.db
sqlite3 library.db < schema.sql
sqlite3 library.db < seed.sql
```

Note what did **not** happen: the second run did not half-load. `seed.sql`
wraps its inserts in `BEGIN; ... COMMIT;`, so the whole batch either lands or
none of it does.

## `Error: table books already exists`

You applied `schema.sql` to a database that already has it. Same fix: delete
the file and start again. `CREATE TABLE IF NOT EXISTS` would silence the error,
and you should resist it here — the message is telling you the truth about the
state of the file.

## `Usage: .headers on|off` or `extra argument: "draw"`

You put a `-- comment` on the same line as a dot-command. A dot-command takes
the whole line, so the comment is read as an argument. Dot-commands are not
SQL: no semicolon, no trailing comments. Put the comment on its own line.

## A query returns fewer rows than you expect, and nothing is wrong

Check the storage classes:

```sql
SELECT year, typeof(year) FROM books;
```

If a row shows `text` in a column declared `INTEGER`, that value was written as
text and SQLite kept it that way. In SQLite's sort order every integer comes
before every text value, so `WHERE year < 2000` will never match it — silently.
This is type affinity, it is documented, and `STRICT` tables are the fix. See
`examples/typing_demo.sql`, which demonstrates the whole thing in twenty lines.

## `cannot store TEXT value in INTEGER column`

A `STRICT` table refusing a value, which is what you asked it to do. Either fix
the value or, if the column genuinely holds mixed types, declare it `ANY`.

`STRICT` needs SQLite 3.37.0 or newer. If the shell rejects the keyword
outright, check `sqlite3 --version`.

## `database is locked`

Another connection holds a write transaction on the file. Usually it is an
interactive `sqlite3` session you left open at the `sqlite>` prompt with an
uncommitted `BEGIN`. Type `COMMIT;` or `ROLLBACK;` there, or `.quit`.

This is the honest limit of SQLite's concurrency model: many readers at once,
one writer at a time. `PRAGMA journal_mode = WAL` lets readers carry on while
one writer works, which helps a great deal and does not change the one-writer
rule.

## `no such column: Ada`

You wrote `WHERE name = "Ada"`. In SQL, double quotes mean an *identifier* — a
column or table name — and single quotes mean a *string*. SQLite tries the
identifier first and only falls back to treating it as a string, which is why
the mistake sometimes works and sometimes produces this. Use single quotes for
text, always.

Better still, from Python, do not quote anything: pass the value as a
parameter and let the driver deal with it.

## `sqlite3.OperationalError: no such table: books`

You connected to the wrong file. `sqlite3.connect("library.db")` uses a
*relative* path, so it depends on your working directory — and if the file does
not exist, SQLite creates a new empty one rather than complaining. That is why
this error usually means "you just created an empty database next door".

```bash
ls -l library.db          # is it where you think, and is it 0 bytes?
sqlite3 library.db ".tables"
```

## The starter's `table_scan.py` prints "not finished yet"

That is the starter telling you which exercise is next. Implement the function
it names and run it again. It exits non-zero until all three are written, on
purpose: an unfinished lab should not be able to look finished.

## `tests/run_tests.sh` fails on one check

Read the `FAIL:` line — each one names the property, not the file. Then run the
matching example by hand from `examples/` to see the full output. The harness
copies everything into a temporary directory, so a failure never leaves your
own `library.db` in a strange state.

## Something left a `library.db` where you did not want one

Delete it. A SQLite database is one ordinary file with no registry entry, no
service and no configuration anywhere else — `rm library.db` removes it
completely. If you see `library.db-journal` or `library.db-wal` alongside it,
those belong to the same database; remove them together, and only when no
process has the database open.
