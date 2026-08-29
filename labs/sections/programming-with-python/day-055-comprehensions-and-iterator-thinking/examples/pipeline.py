#!/usr/bin/env python3
"""Comprehensions and a lazy generator pipeline.

A complete, small, real program that demonstrates both halves of Day 55:

  1. Comprehensions (list, dict, set) — the everyday transforms that map and
     filter a collection in one readable line.
  2. A lazy generator pipeline — reading, filtering, and aggregating a stream
     of records one at a time, holding only a single record in memory, and
     proving it returns the same answer as a plain eager loop.

Run it:
    python3 examples/pipeline.py

It reads no files and takes no arguments: the "stream" is a small in-memory
list of rows standing in for a data source far too large to hold at once.
"""
import itertools
import sys

# A tiny in-memory "stream". In real life these rows would arrive from a huge
# file or a network socket, one at a time, far too large to hold in memory.
RECORDS = [
    "alice,34,engineering,88",
    "bob,29,design,72",
    "carol,41,engineering,95",
    "dave,38,design,60",
    "erin,25,engineering,79",
    "frank,52,marketing,84",
]


def parse(row):
    """Turn a raw 'name,age,team,score' row into a typed dict."""
    name, age, team, score = row.split(",")
    return {"name": name, "age": int(age), "team": team, "score": int(score)}


# --- Comprehensions: the everyday transforms -------------------------------

def high_scorer_names(records):
    """List comprehension: names of records scoring >= 80, upper-cased."""
    return [r["name"].upper() for r in records if r["score"] >= 80]


def name_to_score(records):
    """Dict comprehension: map each name to its score."""
    return {r["name"]: r["score"] for r in records}


def distinct_teams(records):
    """Set comprehension: the distinct teams present (order not kept)."""
    return {r["team"] for r in records}


# --- Lazy generator pipeline -----------------------------------------------

def read_records(rows):
    """Generator: yield one parsed record at a time (O(1) memory)."""
    for row in rows:
        yield parse(row)


def only_team(records, team):
    """Generator: keep only records for one team, lazily."""
    for r in records:
        if r["team"] == team:
            yield r


def scores(records):
    """Generator: yield just the score of each record."""
    for r in records:
        yield r["score"]


def average_score_lazy(rows, team):
    """Average score for a team via a lazy generator pipeline.

    Each record is read, filtered, and consumed one at a time — the program
    never holds more than a single record, however long `rows` is.
    """
    pipeline = scores(only_team(read_records(rows), team))
    total = 0
    count = 0
    for score in pipeline:
        total += score
        count += 1
    return total / count if count else 0.0


def average_score_loop(rows, team):
    """The same answer computed eagerly with a plain loop (the baseline)."""
    matching = []
    for row in rows:
        record = parse(row)
        if record["team"] == team:
            matching.append(record["score"])
    return sum(matching) / len(matching) if matching else 0.0


def first_ids(n):
    """itertools.count + islice: the first n ids from an endless counter."""
    return list(itertools.islice(itertools.count(1000), n))


def main(argv):
    """Print every result and assert the lazy pipeline matches the loop."""
    team = "engineering"

    print("high scorers (list):  ", high_scorer_names([parse(r) for r in RECORDS]))
    print("name -> score (dict): ", name_to_score([parse(r) for r in RECORDS]))
    print("distinct teams (set): ", sorted(distinct_teams([parse(r) for r in RECORDS])))
    print("first 3 ids (itertools):", first_ids(3))

    lazy = average_score_lazy(RECORDS, team)
    loop = average_score_loop(RECORDS, team)
    print(f"{team} average (lazy pipeline): {lazy:.1f}")
    print(f"{team} average (loop baseline): {loop:.1f}")

    assert lazy == loop, "lazy pipeline must match the loop baseline"
    print("match: lazy pipeline == loop baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
