# Security notes — Day 085

This lab starts no server, opens no port, needs no credential, and never
reaches the network. What it does do is teach you to put data in a file that
other programs will read, so the security content here is real rather than
ceremonial.

## What this lab does to your machine

- Creates ordinary files (`library.db`, `typing.db`, `starter.db`) in
  directories you name. Nothing else.
- Runs `python3` and `sqlite3`, both already installed.
- Needs no `sudo`, no privileged port, no system configuration, no service.
- `tests/run_tests.sh` builds every database inside a `mktemp -d` directory and
  removes it in a `trap`, so a completed run leaves nothing behind. One of its
  checks asserts exactly that.

## SQL injection, and the one habit that ends it

The single most consequential security lesson of the whole week is one
character of extra typing.

**Never build a SQL statement by putting a value into a string.** Pass the
value as a parameter and let the driver keep it a value:

```python
# WRONG. The value can become part of the statement.
connection.execute(f"SELECT * FROM members WHERE name = '{name}'")

# RIGHT. The value is compared, never parsed.
connection.execute("SELECT * FROM members WHERE name = ?", (name,))
```

`examples/library_py.py` demonstrates this with a hostile value —
`Ada'; DROP TABLE loans; --` — passed as a parameter. It returns zero rows,
the `loans` table is untouched, and the point is made without ever running the
dangerous version.

Two things worth being precise about, because half-understood advice is what
gets people hurt:

- **Escaping is not the fix.** Writing your own quote-doubling function means
  being right about every encoding, every dialect quirk and every edge case,
  forever. Parameters move the problem to the engine, which is where it
  belongs.
- **Parameters are for values, not for identifiers.** You cannot write
  `ORDER BY ?` and pass a column name. If a table or column name genuinely has
  to be chosen at runtime, validate it against an allow-list you wrote — never
  interpolate whatever arrived.

Python's `sqlite3` module also gives you `executemany` for a batch and
`execute` with named parameters (`:name`) when positional `?` gets hard to
read. Both keep the same guarantee.

## Constraints are a security control, not just a tidiness one

Most "data corruption" is not an attack; it is a write nobody checked. The
schema in `examples/schema.sql` refuses seven kinds of bad write, and
`tests/run_tests.sh` proves each refusal. `NOT NULL`, `UNIQUE`, `CHECK` and
`REFERENCES` are the cheapest validation you will ever deploy, because they
apply to *every* writer — including the script somebody writes next year that
never heard of your validation code.

**Turn foreign keys on.** SQLite defaults `PRAGMA foreign_keys` to OFF for
backward compatibility, per connection. Off, a `REFERENCES` clause enforces
nothing. The lab's suite demonstrates this directly: the same write that is
refused with the pragma on is accepted with it off.

## The database file is data, with everything that implies

- **There is no access control inside the file.** SQLite has no users, no roles
  and no passwords. Anybody who can read the file can read all of it, and
  anybody who can write it can change all of it. Permissions on the file *are*
  the security model — `chmod 600` it if it holds anything private.
- **It is not encrypted.** A SQLite database is plainly readable with `strings`
  or a hex editor. Encrypted variants exist as separate products; the ordinary
  library does not encrypt. If the data must be encrypted at rest, encrypt the
  filesystem or use a build that offers it, and do not assume otherwise.
- **Deleting a row does not scrub the bytes.** The space is marked free and
  reused later. `VACUUM` rebuilds the file, and `PRAGMA secure_delete = ON`
  overwrites deleted content. Neither is on by default.
- **Backups are file copies, and timing matters.** Copying the file while a
  write is in progress can capture a torn state. Use the shell's `.backup`
  command or the module's `Connection.backup()`, both of which take a
  consistent snapshot of a live database.
- **A journal or WAL file beside it is part of the database.** Copying
  `library.db` and leaving `library.db-wal` behind can lose recent commits.
  Move them together.

## Untrusted database files

Opening a SQLite file is not as innocent as opening a text file. The file
format is complex, and a deliberately corrupted database can trigger bugs in
the engine. SQLite's own documentation treats "opening a database from an
untrusted source" as a security-relevant act and offers defences for it.
Nothing in this lab opens a file you did not create, and that is the habit to
carry: treat a database file you were sent the way you would treat any other
executable-adjacent input.

## Privacy: a database accumulates, which is the point and the risk

Day 84 made this argument about a state file and it applies with more force
here, because a database makes accumulation easy and querying cheap. A schema
is a written-down decision about what you keep; write it deliberately. Store
the fields you need rather than the fields you were given, decide how long
rows live before you write the first one, and remember that a `members` table
with names and addresses carries the same obligations as any other record
about a person — including the obligation to be able to delete it.

## What this lab deliberately does not do

- No server, so no listening socket and no authentication to get wrong.
- No credential of any kind, so nothing to leak.
- No network, asserted mechanically: the suite fails if any executable lab file
  contains a URL.
- No third-party package, asserted the same way — so no supply chain beyond
  Python itself.
- No `sudo`, and nothing written outside the lab directory or a temporary one.
