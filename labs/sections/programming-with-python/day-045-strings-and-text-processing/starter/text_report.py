#!/usr/bin/env python3
"""Build a Text Report -- Day 045 lab STARTER.

Complete the five numbered exercises below, then run your program:

    python3 starter/text_report.py

Check your work with:

    bash tests/run_tests.sh

The finished reference lives in examples/text_report.py -- read it only after
you have tried each exercise yourself. Edit ONLY the lines the exercises point
to; leave the rest of the scaffolding in place.
"""

from pathlib import Path

# Characters we peel off the edges of a word before counting it.
PUNCTUATION = ".,;:!?\"'()[]-"

REPORT_WIDTH = 44
LABEL_WIDTH = 20
VALUE_WIDTH = 10


def normalize(token):
    """Lower-case a token and strip surrounding punctuation: 'River,' -> 'river'."""
    return token.strip(PUNCTUATION).lower()


def main():
    sample_path = Path(__file__).resolve().parent.parent / "examples" / "sample.txt"

    # Exercise 1: read the whole file into `text` as one UTF-8 string.
    #   Replace None with:  sample_path.read_text(encoding="utf-8")
    text = None
    if text is None:
        print("Exercise 1 not done yet: read the sample file into `text`.")
        return

    lines = text.splitlines()
    words = text.split()

    # Exercise 2: build a title-cased heading from the first line.
    #   Use lines[0].strip().title()   (str methods, chained left to right)
    heading = "HEADING GOES HERE"

    # Exercise 3: count words into a dict using split + normalize.
    #   For each token in `words`: word = normalize(token); if word is not empty,
    #   add 1 to counts[word] (start each new word at 0 with counts.get).
    counts = {}
    # ... write the counting loop here ...

    # Exercise 4: find the most common word and how many times it appears.
    #   Loop over counts.items() and keep the (word, n) with the largest n.
    common_word, common_n = "", 0
    # ... write the loop here ...

    n_lines = len(lines)
    n_words = len(words)
    n_chars = len(text)
    n_unique = len(counts)

    bar = "=" * REPORT_WIDTH
    print(bar)
    print(f"{heading:^{REPORT_WIDTH}}")
    print(bar)
    print()

    # Exercise 5: print the four statistic rows using f-string format specs so
    #   the label is left-aligned in LABEL_WIDTH and the number right-aligned in
    #   VALUE_WIDTH. The 'Lines' row is done for you; add 'Words', 'Characters',
    #   and 'Unique words' the same way.
    print(f"{'Statistic':<{LABEL_WIDTH}}{'Value':>{VALUE_WIDTH}}")
    print("-" * (LABEL_WIDTH + VALUE_WIDTH))
    print(f"{'Lines':<{LABEL_WIDTH}}{n_lines:>{VALUE_WIDTH}}")
    # ... add the Words, Characters, and Unique words rows here ...

    print()
    if n_words:
        pct = common_n / n_words * 100
        print(f'Most common word:  "{common_word}" ({common_n} times, {pct:.1f}% of words)')


if __name__ == "__main__":
    main()
