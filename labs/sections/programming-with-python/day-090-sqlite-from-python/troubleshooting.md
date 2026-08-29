# Troubleshooting — Day 090

Every entry says what you will see, what is actually happening, and what to
do about it.

## `sqlite3.ProgrammingError: Incorrect number of bindings supplied. The current statement uses 1, and there are 5 supplied.`

You forgot the comma:

```python
connection.execute("SELECT * FROM books WHERE title = ?", (title))   # WRONG
connection.execute("SELECT * FROM books WHERE title = ?", (title,))  # right
```

`(title)` is just `title` in brackets. If `title` is a five-character
string, the module sees a five-item sequence and reports exactly that. A
list works too and is harder to get wrong: `[title]`.

## `sqlite3.ProgrammingError: Binding 1 (':title') is a named parameter, but you supplied a sequence which requires nameless (qmark) placeholders.`

You mixed the two styles. Named placeholders take a mapping:

```python
connection.execute("SELECT * FROM books WHERE title = :title", {"title": title})
```

Qmark placeholders take a sequence. Pick one per statement.

## `sqlite3.ProgrammingError: You can only execute one statement at a time.`

`execute` runs exactly one statement. For a multi-statement script, use
`executescript` — and understand what you are agreeing to: it takes **no
parameters at all**, and it issues an implicit `COMMIT` before it runs, so
it can never be nested inside a transaction.

If this error appeared because a *value* contained a semicolon, stop and
read `security.md`. You are building SQL out of a string.

## The same value returns rows when concatenated and none when bound

That is the lab working. See `examples/injection_demo.py`, act 1 and act 4.

## `sqlite3.IntegrityError: FOREIGN KEY constraint failed`

The write named a row that does not exist. Check the id.

The opposite is more interesting: if a write you *expected* to be refused is
**accepted**, `PRAGMA foreign_keys` is off on that connection. It is OFF by
default, it is per connection, and it is not remembered in the file. Use
`db.connect()` rather than `sqlite3.connect()` and it is handled.

## `PRAGMA foreign_keys = ON` runs without error and changes nothing

You are inside a transaction. The pragma is a **silent no-op** there: no
error, no warning, no change. Run it immediately after connecting, which is
what `db.connect()` does, before anything can open a transaction.

```python
connection.execute("PRAGMA foreign_keys = ON")
print(connection.execute("PRAGMA foreign_keys").fetchone()[0])   # 1, or 0 if it was ignored
```

## `sqlite3.IntegrityError: cannot store TEXT value in INTEGER column books.year`

A `STRICT` table refusing the wrong type — which is what you asked it to do.
Convert the value before binding, or declare the column `ANY` if it
genuinely holds mixed types. Note the exception class: a type violation in a
STRICT table is an `IntegrityError`, not a `DataError`.

## `sqlite3.ProgrammingError: Cannot operate on a closed database.`

You used the connection after `close()`. The usual cause is this misreading:

```python
with sqlite3.connect(path) as connection:   # does NOT close on exit
    ...
connection.execute("SELECT 1")              # so this actually works
```

`with connection:` manages a **transaction**, not the connection's lifetime.
For closing, use `contextlib.closing`:

```python
from contextlib import closing
with closing(db.connect(path)) as connection:
    with db.transaction(connection):
        ...
```

## My writes vanished when the program exited

Nothing committed them. In the module's default mode a transaction opens
before the first `INSERT`, `UPDATE` or `DELETE` and stays open until you
commit. Exit without committing and the work is rolled back, silently.

Either use `db.transaction()` — which commits at the end of the block — or
`with connection:`, or set `connection.autocommit = True` and accept that
every statement then stands alone.

## `sqlite3.OperationalError: database is locked`

Another connection holds the write lock. Usually it is a connection your own
program forgot to close, or a `db.connect()` left open in an interactive
session. `connect()` sets a five-second busy timeout, so this means the lock
was held for longer than that.

SQLite allows many readers and **one writer at a time**. Keep write
transactions short: do the computation first, then open the transaction.

## `sqlite3.OperationalError: no such table: books`

You connected to the wrong file. `sqlite3.connect("library.db")` is a
relative path, and if the file does not exist SQLite creates a new empty one
rather than complaining — so this error usually means "you just made an
empty database next door".

```python
print(Path("library.db").resolve(), Path("library.db").stat().st_size)
```

## `DeprecationWarning: The default date adapter is deprecated as of Python 3.12`

You passed a `datetime.date` or `datetime.datetime` straight to a
placeholder. The default adapters are deprecated and will be removed. Store
dates as ISO-8601 text, which is what this lab does throughout:

```python
connection.execute("INSERT INTO loans (due_on) VALUES (?)", (due.isoformat(),))
```

Or register your own adapter and converter, explicitly, so the conversion is
code you own rather than a default that is going away.

## `smoke.py` prints "0 of 9 exercises finished"

That is the starter telling you where to begin. Open `starter/db.py`, find
`EXERCISE 1`, write it, and run `smoke.py` again. It exits non-zero until
all nine are done, on purpose.

## `smoke.py` says "stream_all calls fetchall; iterate the cursor instead"

Exercise 7 asks for a generator. Replace `return [row_to_book(r) for r in
cursor.fetchall()]` with a loop that yields:

```python
for row in cursor:
    yield row_to_book(row)
```

The check parses your code with `ast`, so a mention of `fetchall` in a
comment does not count — only a call.

## `bulk_insert.py` takes a long time

The first of its three methods commits once per row, and on a filesystem
that really flushes, each commit is an `fsync`. Twenty thousand rows that
way took about thirteen seconds on the authoring machine. That slowness is
the finding, not a fault. Pass a smaller number if you are impatient:
`python3 bulk_insert.py 2000`.

## `bulk_insert.py` shows almost no difference between the three methods

Your filesystem is not really flushing to disk — normal in some containers
and virtual machines. The ordering still holds; the demonstration is just
less dramatic. `expected-output/FIELDS.md` says so explicitly.

## `tests/run_tests.sh` fails one check

Read the `FAIL:` line — each one names a property, not a file. Then run the
matching script from `examples/` by hand to see the whole output. The
harness copies everything into a temporary directory, so a failure never
leaves your own work in a strange state.

If it is the last check — a sandbox left in the temporary directory — a
script crashed before its `finally:` ran. Remove the leftovers with
`find "${TMPDIR:-/tmp}" -maxdepth 1 -name 'day090-*'` and delete what it
lists.

## `bash: tests/run_tests.sh: No such file or directory`

Run it from the lab directory, not from `tests/`:

```bash
cd labs/sections/programming-with-python/day-090-sqlite-from-python
bash tests/run_tests.sh
```

## Something left a `.db` file behind

Delete it. A SQLite database is one ordinary file with no service and no
registry entry. If you see `-journal` or `-wal` beside it, those belong to
the same database; remove them together, and only when no process has it
open.
