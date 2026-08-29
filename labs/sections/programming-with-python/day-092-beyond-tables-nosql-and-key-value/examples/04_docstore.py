"""Day 092 · Step 4 — a document store, built from first principles.

    python3 examples/04_docstore.py <directory>

Roughly seventy lines of Python over `sqlite3` give you the four operations a
document database advertises: put, get, delete, and find-by-field. Building it
is the fastest way to stop treating "NoSQL" as a category of magic. A document
store is a key-value store that agrees to look inside the value.

The second half of the file is the more valuable half: it shows, by running
them, the four things this store does NOT give you that yesterday's relational
schema did.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from library_data import BOOKS, MISSPELLED_BOOK  # noqa: E402

# A field name must be a plain identifier. This check is not decoration: the
# field is interpolated into the SQL text below, because a JSON path cannot be
# passed as a bound parameter if you also want an index on it to be usable.
# Anything interpolated into SQL must come from an allow-list, never from input.
SAFE_FIELD = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class DocumentStore:
    """A minimal document store: JSON documents in one table, keyed by string."""

    def __init__(self, path: str) -> None:
        self.connection = sqlite3.connect(path)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
              key  TEXT PRIMARY KEY,
              body TEXT NOT NULL CHECK (json_valid(body))
            )
            """
        )
        self.connection.commit()

    # --- the key-value half -------------------------------------------------

    def put(self, key: str, document: dict) -> None:
        """Store a document. Replaces whatever was there. No shape is checked."""
        self.connection.execute(
            "INSERT INTO documents (key, body) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET body = excluded.body",
            (key, json.dumps(document)),
        )
        self.connection.commit()

    def get(self, key: str) -> dict | None:
        row = self.connection.execute(
            "SELECT body FROM documents WHERE key = ?", (key,)
        ).fetchone()
        return None if row is None else json.loads(row[0])

    def delete(self, key: str) -> bool:
        cursor = self.connection.execute("DELETE FROM documents WHERE key = ?", (key,))
        self.connection.commit()
        return cursor.rowcount > 0

    # --- the half that makes it a DOCUMENT store ----------------------------

    def _path(self, field: str) -> str:
        if not SAFE_FIELD.match(field):
            raise ValueError(f"not a safe field name: {field!r}")
        return f"json_extract(body, '$.{field}')"

    def find(self, field: str, value: object) -> list[dict]:
        """Every document whose FIELD equals VALUE. This is the whole query language."""
        sql = f"SELECT body FROM documents WHERE {self._path(field)} = ? ORDER BY key"
        return [json.loads(row[0]) for row in self.connection.execute(sql, (value,))]

    def create_index(self, field: str) -> None:
        """Index the extracted field, so find() stops scanning every document."""
        expression = self._path(field)
        self.connection.execute(
            f"CREATE INDEX IF NOT EXISTS idx_docs_{field} ON documents ({expression})"
        )
        self.connection.commit()

    def plan_for_find(self, field: str) -> str:
        sql = f"SELECT body FROM documents WHERE {self._path(field)} = ?"
        rows = self.connection.execute(f"EXPLAIN QUERY PLAN {sql}", ("x",)).fetchall()
        return " / ".join(row[3] for row in rows)

    def count(self) -> int:
        return self.connection.execute("SELECT count(*) FROM documents").fetchone()[0]

    def close(self) -> None:
        self.connection.close()


def timed(callable_, repeats: int) -> tuple[float, object]:
    start = time.perf_counter()
    for _ in range(repeats):
        result = callable_()
    return (time.perf_counter() - start) / repeats * 1000, result


def main(directory: str) -> int:
    store = DocumentStore(str(Path(directory) / "docstore.db"))

    print("--- 1. put, get, delete: the key-value contract ---")
    for book in BOOKS:
        store.put(f"book:{book['book_id']}", book)
    fetched = store.get("book:103")
    print(f"documents stored: {store.count()}")
    print(f"get('book:103') -> {fetched['title']}")
    print(f"  its authors field is a real list: {fetched['authors']}")
    print(f"get('book:999') -> {store.get('book:999')}")
    print(f"delete('book:104') -> {store.delete('book:104')}")
    print(f"delete('book:104') again -> {store.delete('book:104')}")
    store.put("book:104", BOOKS[3])

    print()
    print("--- 2. find by a field inside the document ---")
    for book in store.find("shelf", "A3"):
        print(f"    shelf A3: {book['book_id']}  {book['title']}")
    for book in store.find("published_year", 1975):
        print(f"    published 1975: {book['book_id']}  {book['title']}")
    print(f"find('shelf', 'Z9') -> {store.find('shelf', 'Z9')}")

    print()
    print("--- 3. make find() fast: an index on an extracted field ---")
    # Load enough documents that a scan is measurably worse than a lookup.
    bulk = 20_000
    rows = []
    for number in range(bulk):
        rows.append(
            (
                f"filler:{number}",
                json.dumps(
                    {
                        "book_id": 200_000 + number,
                        "title": f"Filler Volume {number}",
                        "published_year": 2000 + number % 25,
                        "shelf": f"F{number % 400}",
                        "authors": ["Anon"],
                    }
                ),
            )
        )
    store.connection.executemany(
        "INSERT INTO documents (key, body) VALUES (?, ?)", rows
    )
    store.connection.commit()
    print(f"documents now in the store: {store.count()}")

    before_plan = store.plan_for_find("shelf")
    before_ms, before_rows = timed(lambda: store.find("shelf", "F137"), 20)
    store.create_index("shelf")
    after_plan = store.plan_for_find("shelf")
    after_ms, after_rows = timed(lambda: store.find("shelf", "F137"), 20)

    print(f"plan without the index: {before_plan}")
    print(f"plan with the index:    {after_plan}")
    print(f"find('shelf', 'F137') returned {len(before_rows)} documents both times: "
          f"{len(before_rows) == len(after_rows)}")
    print(f"without index: {before_ms:8.3f} ms per call")
    print(f"with index:    {after_ms:8.3f} ms per call")
    print(f"ratio: {before_ms / after_ms:.0f}x  (timings vary by machine and by run;")
    print("       the plan changing from SCAN to SEARCH does not)")

    print()
    print("--- 4. now the bill. Four things this store does not do. ---")

    print("(a) no schema enforcement: the misspelled document is accepted")
    store.put("book:105", MISSPELLED_BOOK)
    print(f"    put('book:105', ...) raised nothing; stored keys now: {store.count()}")
    print(f"    get('book:105') -> {sorted(store.get('book:105').keys())}")
    hits = store.find("shelf", "C1")
    print(f"    find('shelf', 'C1') finds it: {len(hits)} document")
    print("    find('title', 'Compilers: Principles, Techniques, and Tools') "
          f"-> {store.find('title', 'Compilers: Principles, Techniques, and Tools')}")
    print("    the book is in the store and the title query cannot see it")

    print()
    print("(b) no referential integrity: a loan may point at a book that is gone")
    store.put("loan:1", {"loan_id": 1, "book_id": 999, "member_id": 1})
    print("    put a loan for book_id 999, which does not exist -> accepted")
    print(f"    get('book:999') -> {store.get('book:999')}")
    print("    nothing in the store will ever tell you about that dangling id")

    print()
    print("(c) no join: relating two documents is a second round trip in Python")
    loan = store.get("loan:1")
    joined = store.get(f"book:{loan['book_id']}")
    print(f"    loan -> book lookup returned {joined}, so the application must")
    print("    decide what a missing parent means. That decision used to be the")
    print("    database's job, and it used to be one word: REFERENCES.")

    print()
    print("(d) no cross-document transaction unless you write one")
    print("    put() commits per document, so two related writes are two")
    print("    transactions and a crash between them leaves the store half-updated.")
    try:
        with store.connection:  # sqlite3's own transaction context manager
            store.connection.execute(
                "INSERT INTO documents (key, body) VALUES (?, ?)",
                ("book:106", json.dumps({"book_id": 106, "title": "Committed"})),
            )
            raise RuntimeError("something failed after the first write")
    except RuntimeError as error:
        print(f"    raised: {error}")
    print(f"    get('book:106') after the rollback -> {store.get('book:106')}")
    print("    that atomicity is available — but only because this document store")
    print("    is built on a relational engine that already had it.")

    store.close()
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python3 examples/04_docstore.py <directory>")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
