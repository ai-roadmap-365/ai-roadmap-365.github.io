"""Day 092 starter — build the document store yourself.

    python3 starter/01_exercises.py

This file RUNS as it stands. It builds a store, loads the four books, and
checks itself. Every one of the five exercises below is already written in a
way that executes without error and is **wrong in one specific, named way** —
so you always have a working program in front of you, and the checker at the
bottom tells you exactly which piece is still wrong.

Before you begin:  0 of 5 exercises complete.  (exit code 1)
When you finish:   5 of 5 exercises complete.  (exit code 0)

Each exercise is a single line marked with a trailing `# exercise-N` comment.
Replace that one line. Nothing else in the file needs to change.

The worked answers are in `examples/04_docstore.py`. Try each exercise before
you look; the point of the day is the trade-off, and you feel the trade-off by
implementing the thing that gives it up.
"""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path

BOOKS = [
    {"book_id": 101, "title": "The C Programming Language",
     "published_year": 1978, "shelf": "A3"},
    {"book_id": 102, "title": "The Mythical Man-Month",
     "published_year": 1975, "shelf": "B1"},
    {"book_id": 103, "title": "Artificial Intelligence: A Modern Approach",
     "published_year": 1995, "shelf": "C2"},
    {"book_id": 104, "title": "The Practice of Programming",
     "published_year": 1999, "shelf": "A3"},
]

# The document with one character wrong. Exercises 4 and 5 are about catching it.
MISSPELLED = {"book_id": 105, "titel": "Compilers: Principles, Techniques, and Tools",
              "published_year": 1986, "shelf": "C1"}

REQUIRED_FIELDS = ("book_id", "title", "published_year", "shelf")


class MiniDocStore:
    def __init__(self, path: str) -> None:
        self.connection = sqlite3.connect(path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS documents ("
            "  key TEXT PRIMARY KEY,"
            "  body TEXT NOT NULL CHECK (json_valid(body)))"
        )
        self.connection.commit()

    def put(self, key: str, document: dict) -> None:
        """Given to you, and complete. Note what it does NOT check."""
        self.connection.execute(
            "INSERT INTO documents (key, body) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET body = excluded.body",
            (key, json.dumps(document)),
        )
        self.connection.commit()

    # --- EXERCISE 1 --------------------------------------------------------
    # Return the document stored under `key`, decoded from JSON, or None when
    # there is no such key. The query is written for you; `row` is either None
    # or a one-element tuple holding the JSON text.
    #
    # As shipped this always returns None, so every get() looks like a miss.
    def get(self, key: str) -> dict | None:
        row = self.connection.execute(
            "SELECT body FROM documents WHERE key = ?", (key,)
        ).fetchone()
        return None  # exercise-1

    # --- EXERCISE 2 --------------------------------------------------------
    # Return every document whose `field` equals `value`, ordered by key.
    # Reach inside the stored JSON with SQLite's json_extract():
    #
    #     json_extract(body, '$.shelf') = ?
    #
    # `field` is interpolated into the SQL text rather than bound as a
    # parameter — a JSON path cannot be a bound parameter if you also want an
    # index on it to be usable — which is exactly why validate_field() below
    # exists and is called first. Never interpolate anything you have not
    # checked against an allow-list.
    #
    # As shipped the predicate is `0 = ?`, which is false for every document,
    # so find() always returns an empty list.
    def find(self, field: str, value: object) -> list[dict]:
        validate_field(field)
        sql = "SELECT body FROM documents WHERE 0 = ? ORDER BY key"  # exercise-2
        return [json.loads(row[0]) for row in self.connection.execute(sql, (value,))]

    # --- EXERCISE 3 --------------------------------------------------------
    # Create an index that makes find() on this field a SEARCH instead of a
    # SCAN. The index must be on the *same expression* the query uses — an
    # index on json_extract(body, '$.shelf') does nothing for a query written
    # with ->> and nothing at all for a query on a different field.
    #
    # As shipped this indexes the `key` column, which is already the primary
    # key, so the plan for find() stays SCAN.
    def create_index(self, field: str) -> None:
        validate_field(field)
        expression = "key"  # exercise-3
        self.connection.execute(
            f"CREATE INDEX IF NOT EXISTS idx_docs_{field} ON documents ({expression})"
        )
        self.connection.commit()

    # --- EXERCISE 5 --------------------------------------------------------
    # Nothing stops a document being stored without a title, so somebody has to
    # go looking. Return the keys of every document that has no `title` field,
    # sorted. json_extract() returns SQL NULL for a field that is not there, so
    # `WHERE json_extract(body, '$.title') IS NULL` is the audit.
    #
    # As shipped it returns an empty list, which is the comfortable answer and
    # the wrong one.
    def keys_without_a_title(self) -> list[str]:
        return []  # exercise-5

    # --- given to you ------------------------------------------------------

    def plan_for_find(self, field: str) -> str:
        validate_field(field)
        sql = (f"SELECT body FROM documents "
               f"WHERE json_extract(body, '$.{field}') = ?")
        rows = self.connection.execute(f"EXPLAIN QUERY PLAN {sql}", ("x",)).fetchall()
        return " / ".join(row[3] for row in rows)

    def close(self) -> None:
        self.connection.close()


def validate_field(field: str) -> None:
    """Refuse anything that is not a plain identifier, before it reaches SQL."""
    if not field.replace("_", "").isalnum() or field[:1].isdigit():
        raise ValueError(f"not a safe field name: {field!r}")


# --- EXERCISE 4 ------------------------------------------------------------
# Return the REQUIRED_FIELDS that `document` does not have, in the order they
# appear in REQUIRED_FIELDS. This is the schema check the document store does
# not perform for you — the one that would have caught `titel` at write time.
#
# As shipped it reports nothing missing, ever, which is precisely the failure
# mode of a schema-on-read system with no validation layer.
def missing_fields(document: dict) -> list[str]:
    return []  # exercise-4


def check(number: int, label: str, passed: bool, detail: str) -> bool:
    print(f"  exercise {number}: {'ok      ' if passed else 'not yet '} {label}")
    if not passed:
        print(f"      {detail}")
    return passed


def main() -> int:
    with tempfile.TemporaryDirectory() as work:
        store = MiniDocStore(str(Path(work) / "starter.db"))
        for book in BOOKS:
            store.put(f"book:{book['book_id']}", book)
        store.put("book:105", MISSPELLED)

        results = []

        fetched = store.get("book:102")
        results.append(check(
            1, "get() returns the stored document",
            isinstance(fetched, dict) and fetched.get("title") == "The Mythical Man-Month",
            f"get('book:102') returned {fetched!r}; it should be the decoded document",
        ))

        shelf_a3 = store.find("shelf", "A3")
        results.append(check(
            2, "find() filters on a field inside the document",
            [b.get("book_id") for b in shelf_a3] == [101, 104],
            f"find('shelf', 'A3') returned {len(shelf_a3)} documents; expected 101 and 104",
        ))

        store.create_index("shelf")
        plan = store.plan_for_find("shelf")
        results.append(check(
            3, "create_index() turns the SCAN into a SEARCH",
            "SEARCH" in plan,
            f"the plan for find('shelf', ...) is still: {plan}",
        ))

        good = missing_fields(BOOKS[0])
        bad = missing_fields(MISSPELLED)
        results.append(check(
            4, "missing_fields() catches the misspelled document",
            good == [] and bad == ["title"],
            f"missing_fields(a good book) = {good!r}, "
            f"missing_fields(the misspelled one) = {bad!r}; expected [] and ['title']",
        ))

        orphans = store.keys_without_a_title()
        results.append(check(
            5, "keys_without_a_title() audits what nothing enforces",
            orphans == ["book:105"],
            f"returned {orphans!r}; expected ['book:105']",
        ))

        store.close()

    done = sum(results)
    print()
    print(f"{done} of {len(results)} exercises complete.")
    return 0 if done == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
