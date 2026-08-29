# Security notes — Day 090

This lab is mostly a security lab wearing a data-access hat. Read this page
before you run anything, because one of the scripts destroys a table on
purpose.

## The one thing to know before you run it

`examples/injection_demo.py` performs a real SQL injection attack and really
drops a table. It is safe, and here is precisely why:

- It calls `tempfile.mkdtemp()` and builds **its own** database inside that
  fresh directory. It never opens a file you created, never takes a path
  from the command line, and never touches the lab's own data.
- The directory is removed in a `finally:` block, so it goes away even if a
  check inside the script fails.
- The last line it prints is `sandbox removed. Nothing outside it was ever
  opened.`, and `tests/run_tests.sh` asserts that line is there.

Every other script does the same thing. There is no database file anywhere
in this lab directory at rest, and a harness check fails if a run leaves one.

## SQL injection, demonstrated rather than described

The dangerous line and the safe line look almost identical, which is exactly
why this is worth seeing rather than being told:

```python
# WRONG — the value is inside the statement before the parser sees it.
connection.execute("SELECT * FROM members WHERE name = '" + name + "'")

# RIGHT — the statement is compiled first; the value is bound afterwards.
connection.execute("SELECT * FROM members WHERE name = ?", (name,))
```

With `name = "Ada' OR '1'='1"`, the first form returns every member in the
table, addresses and PINs included. The second returns nothing, because no
member is called that.

Four precisions, because half-understood advice is what gets people hurt.

- **Escaping is not the fix.** Writing your own quote-doubling means being
  right about every encoding and dialect quirk, forever, in code that gets
  copied. Binding moves the problem to the engine, where it belongs.
- **`execute` refusing two statements is not a defence.** It is a limit of
  Python's `sqlite3` module, and the lab shows the same string succeeding
  through `executescript`. More importantly, act 1 of the demonstration
  leaks every row without needing a second statement at all. Reading a
  table you should not see is usually worth more to an attacker than
  destroying it.
- **Parameters are for values, not identifiers.** `ORDER BY ?` binds a
  value, so every row sorts by the same constant — a test in
  `examples/test_repository.py` proves it. When a column name must vary,
  select from an allow-list you wrote. `db.py` keeps whole statements in
  `SORTED_QUERIES` so that nothing is assembled even there.
- **`LIKE` patterns still need care.** Binding a value into a `LIKE`
  comparison is safe from injection, but `%` and `_` inside that value are
  still wildcards. Use an `ESCAPE` clause when the user's text should be
  matched literally.

## The mechanical guard

`examples/no_sql_strings.py` parses every Python file with `ast` and fails
if a statement reaching `execute`, `executemany` or `executescript` was
built by an f-string, `+`, `%` or `.format`. It runs inside the test suite.

Two properties make it worth having rather than performative: it does not
flag adjacent string literals, which are the correct way to wrap a long
statement across lines, and the test suite feeds it a deliberately unsafe
file to prove it still catches one. A guard nobody has watched fail is a
guard you are guessing about.

## What a SQLite file is, from a program's point of view

- **No users, no roles, no passwords.** Filesystem permissions are the
  entire access control. `chmod 600` a database holding anything private.
- **Not encrypted.** `strings library.db` reads your data. Encrypted builds
  exist as separate products; the standard library does not encrypt.
- **A deleted row is not scrubbed.** The space is marked free and reused.
  `VACUUM` rebuilds the file; `PRAGMA secure_delete = ON` overwrites.
  Neither is on by default.
- **Your program's privileges are the database's privileges.** There is no
  boundary between them, which is why the injection above is not just a
  data-leak risk: `PRAGMA` statements and, in some builds, extension loading
  are reachable from SQL text.
- **Never open a database file you were sent.** The format is complex and a
  deliberately corrupted file is an attack surface. Nothing in this lab
  opens a file it did not create.

## Errors are a security surface too

`db.py` catches `sqlite3.IntegrityError` at the repository boundary and
raises `DuplicateTitle`. That is a design decision with a security edge: raw
database errors leak schema details — table names, column names, constraint
names — and an error message is the cheapest reconnaissance an attacker
gets. Translate at the boundary; log the original, show the translation.

## Foreign keys are a security control

`PRAGMA foreign_keys` is OFF by default in SQLite, **per connection**. Off,
every `REFERENCES` clause in your schema enforces nothing. `connect()` turns
it on the moment the connection is opened, and a test asserts that a plain
`sqlite3.connect` to the same file has it off — because the setting belongs
to the connection, not the file.

There is a second trap, and it is silent: setting the pragma **inside a
transaction is a no-op**. No error, no warning, and the value simply does
not change. `transactions_demo.py` prints `0` and then `1` to show it.

## What this lab does not do

- No server, no listening socket, no port.
- No credential of any kind, so nothing to leak.
- No network — asserted mechanically by the harness.
- No third-party package, so no supply chain beyond Python itself.
- No `sudo`, and nothing written outside this directory or a temporary one.
