"""Day 092 · Step 2 — the same library as a key-value store.

`dbm` is a real key-value store, it ships with Python, and it is the only one of
today's four shapes that needs nothing installed. Redis and Memcached are the
famous names; `dbm` has the same contract in miniature: bytes in, bytes out,
addressed by one key.

    python3 examples/02_key_value_dbm.py <directory>

What this file is for is not "look, a dictionary on disk". It is to make the
cost of the trade measurable. Fetching by key is one lookup. Fetching by
anything else is a scan of every key in the store, and you write that scan
yourself, in your own process, decoding every value on the way past.

Then it shows the standard fix — a secondary index you maintain by hand — and
the bill that comes with it.
"""

from __future__ import annotations

import dbm
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from library_data import BOOKS, key_for  # noqa: E402


def main(directory: str) -> int:
    store_path = Path(directory) / "library_kv"

    # --- 1. write the four books, one key each -----------------------------
    with dbm.open(str(store_path), "c") as store:
        for book in BOOKS:
            # The value is opaque to the store. JSON is our choice, not its
            # requirement; it would take a pickle, a protobuf or a JPEG just as
            # happily, because it never looks inside.
            store[key_for(book["book_id"])] = json.dumps(book).encode("utf-8")

    print("--- 1. what the store actually holds ---")
    with dbm.open(str(store_path), "r") as store:
        keys = sorted(k.decode("utf-8") for k in store.keys())
        print(f"backend chosen by Python: {dbm.whichdb(str(store_path))}")
        print(f"keys: {keys}")
        print(f"the value under book:102 is {len(store[b'book:102'])} bytes of opaque blob")

    # --- 2. the operation it is built for ----------------------------------
    print()
    print("--- 2. get by key: one lookup, no scan ---")
    with dbm.open(str(store_path), "r") as store:
        raw = store[key_for(101).encode("utf-8")]
    book = json.loads(raw)
    print(f"book:101 -> {book['title']} ({book['published_year']}), shelf {book['shelf']}")
    print("keys examined: 1")

    # --- 3. the operation it is NOT built for ------------------------------
    print()
    print("--- 3. the same question as SQL's WHERE published_year < 1990 ---")
    print("    there is no WHERE. You write the loop.")
    examined = 0
    matches = []
    with dbm.open(str(store_path), "r") as store:
        for key in store.keys():
            examined += 1
            candidate = json.loads(store[key])
            if candidate["published_year"] < 1990:
                matches.append(candidate)
    for candidate in sorted(matches, key=lambda b: b["book_id"]):
        print(f"    {candidate['book_id']}  {candidate['title']}")
    print(f"keys examined: {examined} of {examined} (every key in the store)")
    print("json.loads calls: %d (every value decoded, matching or not)" % examined)

    # --- 4. the fix, and its price -----------------------------------------
    print()
    print("--- 4. the usual fix: a secondary index you maintain yourself ---")
    with dbm.open(str(store_path), "w") as store:
        by_decade: dict[str, list[int]] = {}
        for book in BOOKS:
            decade = f"{book['published_year'] // 10 * 10}s"
            by_decade.setdefault(decade, []).append(book["book_id"])
        for decade, ids in by_decade.items():
            store[f"index:decade:{decade}"] = json.dumps(sorted(ids)).encode("utf-8")

    with dbm.open(str(store_path), "r") as store:
        ids_1970s = json.loads(store[b"index:decade:1970s"])
        looked_up = [json.loads(store[key_for(i).encode("utf-8")]) for i in ids_1970s]
    print(f"index:decade:1970s -> {ids_1970s}")
    for candidate in looked_up:
        print(f"    {candidate['book_id']}  {candidate['title']}")
    print(f"keys examined: {1 + len(ids_1970s)} (one index key, then one key per hit)")

    print()
    print("    That index is now YOUR problem. Nothing in the store knows it")
    print("    exists. Every write to a book must also rewrite the index entry,")
    print("    in the right order, and there is no transaction spanning both.")
    print("    Delete a book without touching the index and the index points at")
    print("    a key that is gone — the key-value store's version of an orphan.")

    # --- 5. prove that claim rather than asserting it ----------------------
    print()
    print("--- 5. delete a book and forget the index ---")
    with dbm.open(str(store_path), "w") as store:
        del store[key_for(102).encode("utf-8")]
    with dbm.open(str(store_path), "r") as store:
        listed = json.loads(store[b"index:decade:1970s"])
        dangling = [i for i in listed if key_for(i).encode("utf-8") not in store]
    print(f"index:decade:1970s still lists {listed}")
    print(f"ids in that index with no book left in the store: {dangling}")
    print("no error was raised at any point")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python3 examples/02_key_value_dbm.py <directory>")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
