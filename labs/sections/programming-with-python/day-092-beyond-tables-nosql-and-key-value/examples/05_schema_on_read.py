"""Day 092 · Step 5 — one misspelled document, four stores.

    python3 examples/05_schema_on_read.py <directory>

This is the punchline of the lab, and it is worth running twice.

A cataloguer types `titel` instead of `title`. One character. The question this
file answers by experiment is: which of the four shapes tells you, and when?

    schema-on-write   the store refuses the write, now, at the point of the
                      mistake, with a message naming the field
    schema-on-read    the store accepts the write, and the mistake surfaces
                      later — as a query that silently returns nothing, in a
                      report nobody thought to check

Nobody abolished the schema. The document stores moved it into your application
code, where it is written down in no single place and enforced by nobody.
"""

from __future__ import annotations

import dbm
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from library_data import BOOKS, MISSPELLED_BOOK, key_for  # noqa: E402
from importlib import import_module  # noqa: E402

DocumentStore = import_module("04_docstore").DocumentStore

WANTED = "Compilers: Principles, Techniques, and Tools"


def relational(directory: Path) -> tuple[str, str, int, int]:
    connection = sqlite3.connect(str(directory / "relational.db"))
    connection.execute(
        "CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, "
        "published_year INTEGER NOT NULL, shelf TEXT NOT NULL)"
    )
    for book in BOOKS:
        connection.execute(
            "INSERT INTO books VALUES (?, ?, ?, ?)",
            (book["book_id"], book["title"], book["published_year"], book["shelf"]),
        )
    connection.commit()
    try:
        connection.execute(
            "INSERT INTO books (book_id, titel, published_year, shelf) VALUES (?, ?, ?, ?)",
            (105, WANTED, 1986, "C1"),
        )
        outcome, detail = "ACCEPTED", "(no error)"
    except sqlite3.OperationalError as error:
        outcome, detail = "REFUSED", f"{type(error).__name__}: {error}"
    found = connection.execute(
        "SELECT count(*) FROM books WHERE title = ?", (WANTED,)
    ).fetchone()[0]
    total = connection.execute("SELECT count(*) FROM books").fetchone()[0]
    connection.close()
    return outcome, detail, found, total


def key_value(directory: Path) -> tuple[str, str, int, int]:
    path = directory / "kv_store"
    with dbm.open(str(path), "c") as store:
        for book in BOOKS:
            store[key_for(book["book_id"])] = json.dumps(book).encode("utf-8")
        store[key_for(105)] = json.dumps(MISSPELLED_BOOK).encode("utf-8")
        outcome, detail = "ACCEPTED", "(no error — the value is opaque bytes)"
        found = sum(
            1
            for key in store.keys()
            if json.loads(store[key]).get("title") == WANTED
        )
        total = len(store.keys())
    return outcome, detail, found, total


def json_in_sqlite(directory: Path) -> tuple[str, str, int, int]:
    connection = sqlite3.connect(str(directory / "json.db"))
    connection.execute(
        "CREATE TABLE documents (doc_id INTEGER PRIMARY KEY, "
        "body TEXT NOT NULL CHECK (json_valid(body)))"
    )
    for book in BOOKS:
        connection.execute(
            "INSERT INTO documents VALUES (?, ?)", (book["book_id"], json.dumps(book))
        )
    connection.commit()
    try:
        connection.execute(
            "INSERT INTO documents VALUES (?, ?)", (105, json.dumps(MISSPELLED_BOOK))
        )
        connection.commit()
        outcome, detail = "ACCEPTED", "(no error — json_valid() only checks it parses)"
    except sqlite3.IntegrityError as error:
        outcome, detail = "REFUSED", f"{type(error).__name__}: {error}"
    found = connection.execute(
        "SELECT count(*) FROM documents WHERE json_extract(body, '$.title') = ?",
        (WANTED,),
    ).fetchone()[0]
    total = connection.execute("SELECT count(*) FROM documents").fetchone()[0]
    connection.close()
    return outcome, detail, found, total


def document_store(directory: Path) -> tuple[str, str, int, int]:
    store = DocumentStore(str(directory / "docstore05.db"))
    for book in BOOKS:
        store.put(key_for(book["book_id"]), book)
    store.put(key_for(105), MISSPELLED_BOOK)
    outcome, detail = "ACCEPTED", "(no error — put() checks nothing about shape)"
    found = len(store.find("title", WANTED))
    total = store.count()
    store.close()
    return outcome, detail, found, total


def main(directory: str) -> int:
    work = Path(directory)
    shapes = [
        ("relational (books table)", relational),
        ("key-value (dbm)", key_value),
        ("JSON documents in SQLite", json_in_sqlite),
        ("the from-scratch document store", document_store),
    ]

    print("--- writing a book whose title field is spelled 'titel' ---")
    print()
    results = []
    for label, run in shapes:
        outcome, detail, found, total = run(work)
        results.append((label, outcome, found, total))
        print(f"{label}")
        print(f"    the write: {outcome}  {detail}")
        print(f"    books now in this store: {total}")
        print(f"    query WHERE title = '{WANTED}'  ->  {found} row(s)")
        print()

    print("--- summary ---")
    print(f"{'store':32}  {'the write':10}  {'stored':6}  {'query finds it'}")
    print(f"{'-' * 32}  {'-' * 10}  {'-' * 6}  {'-' * 14}")
    for label, outcome, found, total in results:
        print(f"{label:32}  {outcome:10}  {total:<6}  {'yes' if found else 'no'}")

    print()
    print("The relational store is the only one that said anything at all, and it")
    print("said it at the moment of the mistake, naming the field. The other three")
    print("stored the book happily. In every one of them the book is present and")
    print("the catalogue query cannot see it: not an error, not an empty database,")
    print("but a report that is quietly one book short.")
    print()
    print("This is what schema-on-read means in practice. The schema did not go")
    print("away — the check moved from the database to whatever validation your")
    print("application performs, and if your application performs none, then")
    print("nothing anywhere checks it.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python3 examples/05_schema_on_read.py <directory>")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
