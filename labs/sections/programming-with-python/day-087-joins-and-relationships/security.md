# Security notes — Day 087

## What this lab does to your machine

Almost nothing, and that is checked rather than promised.

- **No network.** Nothing here opens a socket. The test suite asserts that no
  file in `examples/` or `starter/` imports `socket`, `urllib`, `http` or
  `requests`, and that the only URL anywhere in the lab's scripts is the SQLite
  documentation page cited in a comment.
- **No privilege.** Nothing runs `sudo`. The suite greps for a line that would
  actually invoke it, as opposed to a comment saying it does not.
- **No credentials.** There is no account, no key, no token, and no service to
  log in to. SQLite is a file.
- **No installation.** `requirements.txt` lists no packages. Nothing is added to
  your Python environment, your `PATH`, or any scheduler.
- **No mess.** The harness builds every database inside `mktemp -d` and removes
  it in a `trap`, then asserts that no database was created in the lab
  directory. Your own `starter/library.db` is the only file you create, and
  Cleanup removes it.

## The data in this lab

The books and authors are real, published works and their real authors, used as
catalogue entries. **The five members and six loans are invented for this lab.**
No real person's borrowing history appears anywhere, and none should: a library
loan record is one of the more sensitive things a small institution holds. It
ties a named individual to what they read and when.

That is worth a moment, because it is the security lesson hiding inside a
lesson about joins. Each of the five tables on its own is fairly harmless.
`books` is a catalogue. `members` is a mailing list. `loans` is a table of
integers and dates. **The join is what makes it sensitive** — one query across
three tables produces "this named person read this named book on this date",
which is exactly the record that reading-privacy law in several countries
exists to protect.

The general form: *a join can create a disclosure that none of its inputs
contains.* When you are reasoning about who may see what, the unit to reason
about is the query, not the table.

## Foreign keys are an integrity control, not a security control

Enabling `PRAGMA foreign_keys = ON` stops a loan pointing at a member who does
not exist. It stops nothing else. It is not an access control, it does not
authenticate anybody, and it does not protect the file — anyone who can read
`library.db` can read every row in it, because a SQLite database is an ordinary
file with ordinary filesystem permissions and no encryption.

If a database on disk holds anything you would not hand to whoever gets the
laptop, the protection is filesystem permissions, full-disk encryption, or not
storing it — not a constraint inside the schema.

Worth stating plainly because the default surprises people: **enforcement is
off unless you turn it on, per connection, every time.** A schema full of
`REFERENCES` clauses on a system where nobody ever issued the pragma has been
accumulating orphan rows silently, possibly for years. `PRAGMA
foreign_key_check` will tell you; it is a good thing to run against any
inherited SQLite database before you trust its relationships.

## SQL injection, and why you do not see it here

Every query in this lab is a literal string written by you, with no user input
anywhere, so there is nothing to inject into. The moment a value comes from
outside — a form, a filename, an API parameter — that stops being true.

The rule, in Python:

```python
# never
connection.execute(f"SELECT * FROM members WHERE name = '{name}'")

# always
connection.execute("SELECT * FROM members WHERE name = ?", (name,))
```

The placeholder form sends the value to SQLite *separately* from the statement,
so it can never be parsed as SQL no matter what it contains. This is not a
string-escaping technique that a clever input might defeat; the value never
passes through the parser at all.

One thing the placeholder cannot do: **table and column names are not
parameterisable.** `SELECT * FROM ?` is not valid. `examples/06_join_from_scratch.py`
does interpolate a table name into a query — `f"SELECT * FROM {table}"` — and it
is safe there only because the caller passes a constant from that same file. If
a table name ever comes from outside your program, check it against a hard-coded
allow-list of names you accept, and reject anything else.

## Cartesian products as a denial of service

A missing join condition is a correctness bug at this scale and a resource
problem at any real one. Two tables of ten thousand rows joined with no
condition is a hundred million rows, and the database will honestly try to
produce them. On a shared server that is an outage, caused by a query that
looked fine in review.

Two habits that cost nothing: run `EXPLAIN QUERY PLAN` before running anything
unfamiliar against a large table (`examples/09_query_plans.sql` shows what a
cartesian product looks like — two bare `SCAN`s), and put a `LIMIT` on
exploratory queries until you trust them.

## Cleanup

```bash
rm -f starter/library.db library.db
```

Nothing else was created, nothing was installed, and nothing outside this
directory was touched.
