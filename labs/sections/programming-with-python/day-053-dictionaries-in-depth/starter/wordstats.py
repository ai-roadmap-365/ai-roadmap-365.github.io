#!/usr/bin/env python3
"""Word Frequency & Records — YOUR working file.

Build this program one exercise at a time. Each numbered exercise below names
exactly what to write. The finished reference is in examples/wordstats.py —
try each exercise yourself before peeking.

When all exercises are done, this file should behave just like the reference:

    python3 starter/wordstats.py "a a b"   ->  a: 2 / b: 1 / most common: a (2)
    python3 starter/wordstats.py --records ->  grouped and filtered records

Then run:  bash tests/run_tests.sh
"""
import sys

PEOPLE = [
    {"name": "Ada", "role": "engineer"},
    {"name": "Grace", "role": "admiral"},
    {"name": "Alan", "role": "engineer"},
]


def count_words(text):
    """Return a dict mapping each word in text to how many times it appears."""
    # Exercise 1: COUNT WITH .get().
    # Split text into words, then for each word do:
    #     counts[word] = counts.get(word, 0) + 1
    # so a first-seen word starts at 0 (no KeyError). Return the counts dict.
    # Verify by hand: count_words("a b a") must be {"a": 2, "b": 1}.
    raise NotImplementedError("Exercise 1: implement count_words with .get()")


def most_common(counts):
    """Return (word, count) for the highest count; ties go to the first seen."""
    # Exercise 2: FIND THE TOP WORD.
    # If counts is empty, raise ValueError("no words to rank").
    # Otherwise walk counts.items() and keep the word with the largest count.
    # Use a STRICTLY-greater test (n > best_count) so the EARLIEST word wins
    # on ties. Return (best_word, best_count).
    raise NotImplementedError("Exercise 2: implement most_common")


def group_by_role(people):
    """Group record names by their role using setdefault."""
    # Exercise 3: GROUP WITH setdefault.
    # For each person dict, append person["name"] to the list stored under
    # person["role"], creating that list once with:
    #     groups.setdefault(person["role"], []).append(person["name"])
    # Return the groups dict.
    raise NotImplementedError("Exercise 3: implement group_by_role with setdefault")


def names_up_to_m(people):
    """Return the sorted names whose first letter is A-M, via a dict comprehension."""
    # Exercise 4: DICT COMPREHENSION.
    # Build a {name: role} mapping with a dict comprehension over people, then
    # return the sorted names whose first letter (name[0].upper()) is <= "M".
    raise NotImplementedError("Exercise 4: implement names_up_to_m with a dict comprehension")


def report_counts(text):
    """Print the word counts and the most common word for text. (Provided.)"""
    counts = count_words(text)
    if not counts:
        raise ValueError("no words found in the input text")
    for word, n in counts.items():
        print(f"{word}: {n}")
    word, n = most_common(counts)
    print(f"most common: {word} ({n})")


def report_records():
    """Print the grouped and filtered records. (Provided.)"""
    groups = group_by_role(PEOPLE)
    for role, names in groups.items():
        print(f"{role}s: {names}")
    print(f"names A-M: {names_up_to_m(PEOPLE)}")


def main(argv):
    """Entry point. Returns an exit code: 0 on success, 1 on bad input. (Provided.)"""
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
