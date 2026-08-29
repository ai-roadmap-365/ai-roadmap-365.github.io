"""The transaction model, demonstrated on the interpreter you are running.

This is the part of `sqlite3` that has changed most across Python versions,
so nothing here is asserted from memory: every line prints what THIS
interpreter actually does, and the test suite checks the behaviour rather
than the version number.

Run it:  python3 transactions_demo.py
"""

from __future__ import annotations

import shutil
import sqlite3
import sys
import tempfile
from contextlib import closing
from pathlib import Path

from db import BookRepository, LoanRepository, apply_schema, connect, transaction
from domain import Book, Member


def rule(text: str) -> None:
    print()
    print(text)
    print("-" * len(text))


def main() -> int:
    sandbox = Path(tempfile.mkdtemp(prefix="day090-transactions-"))
    try:
        return run(sandbox)
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def run(sandbox: Path) -> int:
    print(f"python {sys.version.split()[0]}   sqlite3.sqlite_version {sqlite3.sqlite_version}")

    rule("1. the module's implicit transaction handling, watched")
    path = sandbox / "implicit.db"
    with closing(sqlite3.connect(path)) as connection:
        print(f"    default isolation_level: {connection.isolation_level!r}"
              "   (empty string = the module manages transactions for you)")
        print(f"    connection.autocommit:   {connection.autocommit}"
              f"   (== sqlite3.LEGACY_TRANSACTION_CONTROL, which is"
              f" {sqlite3.LEGACY_TRANSACTION_CONTROL})")
        print(f"    in_transaction on a fresh connection: {connection.in_transaction}")

        connection.execute("CREATE TABLE t (n INTEGER) STRICT")
        print(f"    after CREATE TABLE (DDL):             {connection.in_transaction}"
              "   — no transaction was opened")
        connection.execute("INSERT INTO t (n) VALUES (1)")
        print(f"    after INSERT (DML):                   {connection.in_transaction}"
              "   — the module opened one for you")
        connection.rollback()
        remaining = connection.execute("SELECT count(*) AS n FROM t").fetchone()[0]
        print(f"    after rollback(), rows in t:          {remaining}")
        print("    That INSERT was never committed. A program that forgets to")
        print("    commit and then exits loses the write, and nothing warns it.")

    rule("2. what `with connection:` does — and the two things it does not")
    path = sandbox / "withblock.db"
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE t (n INTEGER) STRICT")
    with connection:
        connection.execute("INSERT INTO t (n) VALUES (1)")
    print(f"    after a successful with-block, in_transaction: {connection.in_transaction}"
          "   (committed)")

    try:
        with connection:
            connection.execute("INSERT INTO t (n) VALUES (2)")
            raise ValueError("something went wrong halfway through")
    except ValueError as error:
        print(f"    the block raised: {error}")
    kept = [row[0] for row in connection.execute("SELECT n FROM t ORDER BY n")]
    print(f"    rows in t now: {kept}   — the second insert was rolled back")

    still_open = True
    try:
        connection.execute("SELECT 1").fetchone()
    except sqlite3.ProgrammingError:
        still_open = False
    print(f"    is the connection still usable after the with-block? {still_open}")
    print("    THIS IS THE MISREADING WORTH KILLING: `with connection:` commits or")
    print("    rolls back a TRANSACTION. It does not close the connection. For")
    print("    closing, use contextlib.closing(sqlite3.connect(...)) — or both,")
    print("    nested, which is the honest full form.")
    connection.close()

    rule("3. explicit control: isolation_level=None and a context manager you wrote")
    path = sandbox / "explicit.db"
    with closing(connect(path)) as connection:
        apply_schema(connection)
        print(f"    connect() sets isolation_level = {connection.isolation_level!r}"
              "   — nothing implicit remains")
        books = BookRepository(connection)
        loans = LoanRepository(connection)

        with transaction(connection):
            books.add_many(
                [
                    Book(title="The Mythical Man-Month", author="Fred Brooks", year=1975, copies=1),
                    Book(title="Programming Pearls", author="Jon Bentley", year=1986, copies=2),
                ]
            )
            loans.add_member(Member(name="Ada Lovelace", email="ada@example.invalid"))
        print(f"    seeded inside one transaction: {books.count()} books")

        rule("4. all-or-nothing across two writes, proved by breaking the second")
        before_copies = books.get(1).copies
        before_loans = loans.open_count()
        print(f"    before: book 1 has {before_copies} copy/copies, {before_loans} open loan(s)")
        try:
            with transaction(connection):
                loans.borrow(1, 1, "2026-08-01", "2026-08-15")
                # Member 999 does not exist. PRAGMA foreign_keys is ON, so
                # this write is refused — after the loan row and the
                # decremented copy count are already in the transaction.
                loans.borrow(2, 999, "2026-08-01", "2026-08-15")
        except sqlite3.IntegrityError as error:
            print(f"    the transaction raised: {type(error).__name__}: {error}")
        after_copies = books.get(1).copies
        after_loans = loans.open_count()
        print(f"    after:  book 1 has {after_copies} copy/copies, {after_loans} open loan(s)")
        print("    Both halves of the FIRST borrow were undone as well. That is")
        print("    atomicity: the group either lands or it does not.")

        rule("5. the pragma trap: PRAGMA foreign_keys is a no-op inside a transaction")
        connection.execute("PRAGMA foreign_keys = OFF")
        print(f"    outside a transaction, set OFF -> "
              f"{connection.execute('PRAGMA foreign_keys').fetchone()[0]}")
        connection.execute("BEGIN")
        connection.execute("PRAGMA foreign_keys = ON")
        inside = connection.execute("PRAGMA foreign_keys").fetchone()[0]
        print(f"    inside a transaction, set ON   -> {inside}"
              "   (silently ignored — no error, no warning)")
        connection.commit()
        connection.execute("PRAGMA foreign_keys = ON")
        outside = connection.execute("PRAGMA foreign_keys").fetchone()[0]
        print(f"    outside again, set ON          -> {outside}")
        print("    This is why connect() runs the pragma the moment the")
        print("    connection is opened, before anything can begin a transaction.")

    rule("6. connection.autocommit — the newer, explicit control")
    path = sandbox / "autocommit.db"
    with closing(sqlite3.connect(path)) as writer, closing(sqlite3.connect(path)) as reader:
        writer.execute("CREATE TABLE t (n INTEGER) STRICT")
        writer.commit()

        writer.autocommit = True
        writer.execute("INSERT INTO t (n) VALUES (1)")
        seen = reader.execute("SELECT count(*) AS n FROM t").fetchone()[0]
        print(f"    autocommit = True:  in_transaction {writer.in_transaction},"
              f" another connection already sees {seen} row(s) — committed immediately")

        writer.autocommit = False
        writer.execute("INSERT INTO t (n) VALUES (2)")
        seen = reader.execute("SELECT count(*) AS n FROM t").fetchone()[0]
        print(f"    autocommit = False: in_transaction {writer.in_transaction},"
              f" the other connection still sees {seen} row(s) — uncommitted")
        writer.rollback()
        seen = reader.execute("SELECT count(*) AS n FROM t").fetchone()[0]
        print(f"    after rollback():   the other connection sees {seen} row(s)")
        print("    autocommit=False opens a transaction and keeps one open, so a")
        print("    long-lived connection holds a read lock until you commit.")
        writer.autocommit = sqlite3.LEGACY_TRANSACTION_CONTROL
        print(f"    set back to LEGACY_TRANSACTION_CONTROL"
              f" ({sqlite3.LEGACY_TRANSACTION_CONTROL}): isolation_level is honoured again")

    print()
    print("sandbox removed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
