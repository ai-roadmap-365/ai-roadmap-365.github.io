#!/usr/bin/env python3
"""Word Frequency & Records — dictionaries in depth.

A complete, small program that shows the core dictionary idioms:

  * counting word frequencies with the d.get(key, 0) + 1 pattern
  * finding the most common word (ties broken by first appearance)
  * storing small records as a list of dictionaries
  * grouping records with setdefault
  * building a filtered view with a dict comprehension

It reads input from the command line (never input()), validates it, prints
clear output, and fails gracefully with a non-zero exit code on bad input.

Usage:
    python3 wordstats.py "some words to count"
    python3 wordstats.py --records

Examples:
    python3 wordstats.py "a a b"   ->  a: 2 / b: 1 / most common: a (2)
    python3 wordstats.py --records ->  grouped and filtered records
"""
import sys

# A tiny table of records, modelled as a list of dictionaries. Each record is
# a dict with named fields — exactly the shape of a JSON payload or a config.
PEOPLE = [
    {"name": "Ada", "role": "engineer"},
    {"name": "Grace", "role": "admiral"},
    {"name": "Alan", "role": "engineer"},
]


def count_words(text):
    """Return a dict mapping each word in text to how many times it appears.

    Uses the get()-with-default idiom so a first-seen word starts at 0 and no
    KeyError is ever raised. Insertion order (Python 3.7+) means the returned
    dict lists words in the order they first appeared.
    """
    counts = {}
    for word in text.split():
        counts[word] = counts.get(word, 0) + 1
    return counts


def most_common(counts):
    """Return (word, count) for the highest count; ties go to the first seen.

    Raises ValueError if counts is empty, so callers get a clear message
    rather than a confusing result.
    """
    if not counts:
        raise ValueError("no words to rank")
    best_word = None
    best_count = -1
    for word, n in counts.items():
        if n > best_count:  # strictly greater, so the earliest word wins ties
            best_word, best_count = word, n
    return best_word, best_count


def group_by_role(people):
    """Group record names by their role using setdefault.

    Returns a dict mapping each role to the list of names with that role, with
    roles in the order they were first encountered.
    """
    groups = {}
    for person in people:
        groups.setdefault(person["role"], []).append(person["name"])
    return groups


def names_up_to_m(people):
    """Return the sorted names whose first letter is A-M, via a dict comprehension.

    Builds a {name: role} mapping with a comprehension, then filters and sorts
    the names — showing a dict comprehension feeding a downstream query.
    """
    by_name = {person["name"]: person["role"] for person in people}
    return sorted(name for name in by_name if name[0].upper() <= "M")


def report_counts(text):
    """Print the word counts and the most common word for text."""
    counts = count_words(text)
    if not counts:
        raise ValueError("no words found in the input text")
    for word, n in counts.items():
        print(f"{word}: {n}")
    word, n = most_common(counts)
    print(f"most common: {word} ({n})")


def report_records():
    """Print the grouped and filtered records."""
    groups = group_by_role(PEOPLE)
    for role, names in groups.items():
        print(f"{role}s: {names}")
    print(f"names A-M: {names_up_to_m(PEOPLE)}")


def main(argv):
    """Entry point. Returns an exit code: 0 on success, 1 on bad input."""
    args = argv[1:]
    if not args:
        print("error: expected text to count, or --records", file=sys.stderr)
        print('usage: python3 wordstats.py "some words"   |   --records',
              file=sys.stderr)
        return 1
    try:
        if args[0] == "--records":
            report_records()
        else:
            report_counts(args[0])
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
