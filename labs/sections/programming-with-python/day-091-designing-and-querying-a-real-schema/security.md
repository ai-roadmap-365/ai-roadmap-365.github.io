# Security notes — Day 091

## What this lab does to your machine

Almost nothing, and that is checked rather than promised.

- **No network.** Nothing here opens a socket. The test suite asserts that no
  file in `examples/` or `starter/` imports `socket`, `urllib`, `http` or
  `requests`, and that **no URL appears anywhere** in the lab's `.sql`, `.py`
  or `.sh` files at all.
- **No privilege.** Nothing runs `sudo`. The suite greps for a line that would
  actually invoke it, as opposed to a comment saying it does not.
- **No credentials.** There is no account, no key, no token, and no service to
  log in to. SQLite is a file.
- **No installation.** `requirements.txt` lists no packages. Nothing is added
  to your Python environment, your `PATH`, or any scheduler.
- **No mess.** Both `tests/run_tests.sh` and `starter/03_check.sh` build every
  database inside `mktemp -d` and remove it in a `trap`, and the suite asserts
  afterwards that no database was created in the lab directory or in
  `starter/`.

## The data in this lab

The books are real published works and the authors are their real authors, used
as catalogue entries. **Everything else is invented for this lab**: the library,
the six members, their email addresses, the fourteen loans, the fines and the
reservations. No real person's borrowing history appears anywhere, and none
should.

Every invented email address is on the `.invalid` top-level domain, which is
reserved by RFC 2606 precisely so that it can never resolve or be delivered to.
The test suite checks that: it extracts every address from the seed file and
fails if any of them ends in anything else. That check exists because seed data
has a way of escaping into screenshots, bug reports and public repositories, and
an address that looks plausible eventually receives mail.

The reason to be careful is the same one Day 87 raised, and this day sharpens
it. A library loan record ties a named individual to what they read and when.
Each table here is fairly harmless alone — `books` is a catalogue, `members` is
a mailing list, `loans` is integers and dates. It is the **join** that produces
the sensitive record, and today's schema makes several of those joins one line
long.

## Schema design is a privacy decision, made early and hard to undo

This is the day's own security point, and it is a design point rather than a
coding one.

**What you choose to store is the ceiling on what can ever leak.** The brief
does not ask for a member's date of birth, home address, or reading interests,
so the schema does not have columns for them. A column that does not exist
cannot be joined, exported, indexed by mistake, or subpoenaed.

**Soft delete keeps data you have been asked to remove.** `members.left_at`
means a member who has left is still a row, with their name and email address,
indefinitely. The brief has a good reason — an outstanding fine survives the
membership — but "we keep it because deleting is inconvenient" is not that
reason. If you build this for real, decide in advance what a departed member's
row is allowed to retain and how long for, and write the deletion job at the
same time as the soft-delete column. The cost of not doing so is that the row
is still there in five years, in every backup, and nobody remembers why.

**The queries are the disclosure boundary, not the tables.** Question 4 in this
lab produces "this named person has this named book and is ten days late". That
is a perfectly ordinary operational report and it is also, in one row, a reading
record. When you decide who may run which report, reason about the query.

## Constraints are integrity, not access control

Every `CHECK`, `UNIQUE`, `NOT NULL` and `REFERENCES` in this schema stops bad
*data*. None of them stops a bad *reader*. Anyone who can read the database file
can read every row in it, because a SQLite database is an ordinary file with
ordinary filesystem permissions and no encryption.

And, from Day 87 and still true here: **foreign-key enforcement is off unless
you turn it on, per connection, every time.** `examples/01_schema.sql`,
`examples/02_seed.sql` and `LibraryRepository.__init__` in
`examples/05_report.py` each issue `PRAGMA foreign_keys = ON` as their first
statement. If you write your own connection code, do the same, first, before
anything opens a transaction.

## SQL injection, and the one thing a placeholder cannot do

The report script takes two values from the command line: a database path and a
report instant. The instant goes into the SQL, and it goes in as a bound
parameter:

```python
# never
self.connection.execute(f"... WHERE l.due_at < '{now}'")

# always — and this is what 05_report.py does
self.connection.execute("... WHERE l.due_at < ?", (now,))
```

The placeholder form sends the value to SQLite separately from the statement,
so it can never be parsed as SQL no matter what it contains. That is not a
clever escaping trick; the value never reaches the parser.

The limit worth knowing: **table and column names cannot be parameterised.**
`SELECT * FROM ?` is not valid SQL. Nothing in this lab interpolates one, and
if you ever need to, check the name against a hard-coded allow-list rather than
against a pattern.

Note also what `LibraryRepository` buys here beyond tidiness. Every statement
in the lab lives inside that one class, so the formatting code physically
cannot build a query out of string concatenation — there is no connection object
in scope for it to do so with. That is a security property of the structure,
not of anybody's discipline.

## Cleanup

```bash
rm -f library.db
find . -type d -name __pycache__ -prune -exec rm -rf -- {} +
```

Nothing else was created, nothing was installed, and nothing outside this
directory was touched. If you never ran the optional walkthrough commands by
hand, there is nothing to remove at all — both scripts clean up after
themselves.
