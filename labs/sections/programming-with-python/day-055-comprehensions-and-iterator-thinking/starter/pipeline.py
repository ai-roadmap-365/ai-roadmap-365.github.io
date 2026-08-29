#!/usr/bin/env python3
"""Comprehensions and a lazy generator pipeline — YOUR working file.

Complete the five numbered exercises below. Each names exactly what to write.
The finished reference is in examples/pipeline.py — try each exercise
yourself before peeking.

When all five are done, this file prints the same output as the reference:

    python3 starter/pipeline.py

Then run:  bash tests/run_tests.sh
"""
import itertools
import sys

RECORDS = [
    "alice,34,engineering,88",
    "bob,29,design,72",
    "carol,41,engineering,95",
    "dave,38,design,60",
    "erin,25,engineering,79",
    "frank,52,marketing,84",
]


def parse(row):
    """Turn a raw 'name,age,team,score' row into a typed dict. (Provided.)"""
    name, age, team, score = row.split(",")
    return {"name": name, "age": int(age), "team": team, "score": int(score)}


# --- Comprehensions ---------------------------------------------------------

def high_scorer_names(records):
    """List comprehension: names of records scoring >= 80, upper-cased."""
    # Exercise 1: LIST COMPREHENSION.
    # Return a list of r["name"].upper() for each record r whose
    # r["score"] is >= 80. One line: [ ... for r in records if ... ].
    # Expected on the sample data: ['ALICE', 'CAROL', 'FRANK'].
    raise NotImplementedError("Exercise 1: implement high_scorer_names")


def name_to_score(records):
    """Dict comprehension: map each name to its score."""
    # Exercise 2: DICT COMPREHENSION.
    # Return {r["name"]: r["score"] for r in records}. The key is the name,
    # the value is the score.
    raise NotImplementedError("Exercise 2: implement name_to_score")


def distinct_teams(records):
    """Set comprehension: the distinct teams present."""
    # Exercise 3: SET COMPREHENSION.
    # Return a set of each r["team"]. Duplicates collapse automatically.
    raise NotImplementedError("Exercise 3: implement distinct_teams")


# --- Lazy generator pipeline ------------------------------------------------

def read_records(rows):
    """Generator: yield one parsed record at a time (O(1) memory). (Provided.)"""
    for row in rows:
        yield parse(row)


def only_team(records, team):
    """Generator: keep only records for one team, lazily."""
    # Exercise 4: GENERATOR FUNCTION.
    # Loop over records; for each r whose r["team"] == team, `yield r`.
    # Use yield (not return, not append) so this stays lazy.
    raise NotImplementedError("Exercise 4: implement only_team")


def scores(records):
    """Generator: yield just the score of each record. (Provided.)"""
    for r in records:
        yield r["score"]


def average_score_lazy(rows, team):
    """Average score for a team via a lazy generator pipeline."""
    # Exercise 5: ASSEMBLE THE PIPELINE.
    # Build:  pipeline = scores(only_team(read_records(rows), team))
    # Then loop over the pipeline, summing the scores and counting them,
    # and return total / count (or 0.0 if count is 0). Each record is
    # touched exactly once, one at a time.
    raise NotImplementedError("Exercise 5: implement average_score_lazy")


def average_score_loop(rows, team):
    """The same answer computed eagerly with a plain loop. (Provided baseline.)"""
    matching = []
    for row in rows:
        record = parse(row)
        if record["team"] == team:
            matching.append(record["score"])
    return sum(matching) / len(matching) if matching else 0.0


def first_ids(n):
    """itertools.count + islice: the first n ids from an endless counter. (Provided.)"""
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
