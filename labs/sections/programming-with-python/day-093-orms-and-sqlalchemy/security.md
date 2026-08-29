# Security notes — Day 093

## What this lab does to your machine

Very little, and all of it inside its own directory.

- Creates `.venv/` in the lab directory when you install, and nothing outside
  it. Delete it at any time with `rm -rf .venv`.
- Builds every database **in memory** (`sqlite://`) except two demos that need
  a real file so a genuinely separate connection can be asked what it can see.
  Those use `tempfile.mkdtemp()`, and both delete the directory on the way
  out — `demo_unit_of_work.py` prints `temporary database removed: True` as
  its last line so the claim is checkable rather than asserted.
- Writes no configuration, touches no file in your home directory, and needs
  no `sudo`. Section 9 of `tests/run_tests.sh` scans every `.py`, `.sh` and
  `.ini` file in the lab and fails if any line would invoke `sudo`.
- Sets `PYTHONDONTWRITEBYTECODE=1` and asserts at the end of the run that no
  `__pycache__` and no `.db` file was left behind.

## Network

Installing the two pinned packages needs the network, once. **Nothing else in
this lab does.**

That is not a promise made in prose. `starter/conftest.py` replaces
`socket.socket.connect` and `socket.create_connection` with a function that
raises `NetworkAccessAttempted`, and section 9 of the harness trips that guard
deliberately to prove it is armed rather than decorative. The same section
asserts that no URL appears anywhere in the lab's scripts and that nothing
imports `urllib`, `http` or `requests`.

## SQL injection, and what an ORM does and does not do for you

This is the security point that actually matters today, and it is easy to get
half right.

**What the ORM does for you.** Everything you express through `select()`,
`insert()`, `update()`, `where()` and `values()` is compiled into a statement
with **bound parameters**. Look at any captured line in `expected-output/` and
you will see it:

```
SELECT books.title, books.author FROM books WHERE books.copies >= ? ORDER BY books.title
```

The `?` is the whole story. The value never becomes part of the statement
text; it is handed to the driver separately, so there is no string for an
attacker's quote character to break out of. Day 90 made you do this by hand
with `sqlite3` placeholders. The ORM does it by construction, and you have to
work to defeat it.

**What the ORM does not do for you.** Three specific gaps:

1. **Raw SQL is still raw SQL.** `session.execute(text("SELECT ... WHERE name = '" + name + "'"))` is exactly as injectable as it looks. `text()` supports bound parameters — `text("... WHERE name = :name")` with `{"name": name}` — and you should use them every time.
2. **Identifiers are not parameters.** A table name, a column name or a sort direction cannot be bound; parameters bind values only. If a user chooses which column to sort by, validate that choice against a fixed allow-list of column objects you control. Never interpolate a user-supplied string into an `order_by`.
3. **`filter_by(**request.args)` is a hole of a different shape.** It is not injection — it is mass assignment. If a client can name any column, a client can filter on, or with `values()` write to, a column you never meant to expose.

**Authorization is not a query concern at all.** A perfectly parameterised
`select(Loan)` returns every loan in the table. The ORM has no opinion about
who is allowed to see them. Constraints stop bad *data*; they do nothing about
a bad *reader*. That was true of the schema on Day 91 and it is true of the
object model today.

## Two ORM-specific hazards worth naming

**The N+1 problem is a denial-of-service vector, not only a performance bug.**
An endpoint that lazily loads a relationship per result issues one query per
row. Let a client control the page size and they control how many queries your
database runs. The fix is the same fix as the performance fix — load eagerly,
and count the statements in a test so a regression is caught before it ships.

**`echo=True` prints your data to the log.** It is the best learning tool in
the library and it is a disclosure risk in production: the parameter values it
prints are the values, including whatever personal data is in them. Use it
freely while learning, and never leave it on in a deployed service. The same
caution applies to `logging.getLogger("sqlalchemy.engine").setLevel(INFO)`.
The `QueryCounter` in `examples/counting.py` deliberately records only
statement text and how many parameter sets there were — **never the parameter
values** — which is the shape you want if you ever ship query counting as
telemetry.

## Data in this lab

Every member name and email address in `examples/library.py` is invented for
this exercise. Every address uses the `library.test` domain: `.test` is
reserved by the IETF as a name that can never resolve, so none of them can
reach a real mailbox even by accident. The test suite checks that no address
in the seed uses any other domain.

The books and their authors are real published works, cited as titles only.
The loans, dates, borrowing records and membership details are fictional, and
no real borrowing record was used anywhere in this lab. If you replace the
seed, keep the replacement equally and obviously fictional.

## Secrets

There are none, and there is nowhere to put one. The database URL is
`sqlite://` or a path in a temporary directory. No API key, no token, no
password, no account. Nothing in this lab should ever be given a credential —
if you find yourself wanting to add a real database URL to try the demos
against PostgreSQL, put it in an environment variable and keep it out of the
files, the same rule as every other day.
