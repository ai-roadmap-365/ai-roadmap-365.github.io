#!/usr/bin/env python3
"""Build a Text Report -- Day 045 lab (completed reference implementation).

Reads examples/sample.txt and prints a clean, aligned report built entirely
from string methods and f-strings:

  * a title-cased heading taken from the first line,
  * line, word, character, and unique-word counts,
  * the most common word (found with split + a plain dict),
  * a formatted statistics table using f-string format specs,
  * small demonstrations of slicing and strip/split/join.

It reads only the local sample file next to this script. No network, no
arguments, no writing outside standard output.
"""

from pathlib import Path

# Characters we peel off the edges of a word before counting it. Using
# str.strip keeps this beginner-friendly; a complex pattern would call for
# the regular-expression tools introduced on Day 38.
PUNCTUATION = ".,;:!?\"'()[]-"

REPORT_WIDTH = 44
LABEL_WIDTH = 20
VALUE_WIDTH = 10


def load_text(path):
    """Return the full contents of a UTF-8 text file as one str."""
    return Path(path).read_text(encoding="utf-8")


def normalize(token):
    """Lower-case a token and strip surrounding punctuation.

    "River," -> "river"; "words." -> "words"; "too:" -> "too".
    """
    return token.strip(PUNCTUATION).lower()


def count_words(text):
    """Return a dict mapping each normalized word to how often it appears."""
    counts = {}
    for token in text.split():
        word = normalize(token)
        if word:  # skip tokens that were pure punctuation
            counts[word] = counts.get(word, 0) + 1
    return counts


def most_common(counts):
    """Return (word, n) for the most frequent word; ties break on first seen."""
    best_word = ""
    best_n = 0
    for word, n in counts.items():
        if n > best_n:
            best_word, best_n = word, n
    return best_word, best_n


def main():
    sample_path = Path(__file__).resolve().parent / "sample.txt"
    text = load_text(sample_path)

    lines = text.splitlines()
    heading = lines[0].strip().title()

    words = text.split()
    counts = count_words(text)
    common_word, common_n = most_common(counts)

    n_lines = len(lines)
    n_words = len(words)
    n_chars = len(text)
    n_unique = len(counts)

    bar = "=" * REPORT_WIDTH
    print(bar)
    print(f"{heading:^{REPORT_WIDTH}}")
    print(bar)
    print()

    # Slicing + strip/split/join in one line: collapse all whitespace, then
    # take the first 40 characters as a preview.
    preview = " ".join(text.split())[:40]
    print(f"Preview:  {preview}...")
    print(f"Heading reversed:  {heading[::-1]}")
    print(f"First / last body word:  {words[1]!r} / {words[-1].strip(PUNCTUATION)!r}")
    print()

    print(f"{'Statistic':<{LABEL_WIDTH}}{'Value':>{VALUE_WIDTH}}")
    print("-" * (LABEL_WIDTH + VALUE_WIDTH))
    print(f"{'Lines':<{LABEL_WIDTH}}{n_lines:>{VALUE_WIDTH}}")
    print(f"{'Words':<{LABEL_WIDTH}}{n_words:>{VALUE_WIDTH}}")
    print(f"{'Characters':<{LABEL_WIDTH}}{n_chars:>{VALUE_WIDTH}}")
    print(f"{'Unique words':<{LABEL_WIDTH}}{n_unique:>{VALUE_WIDTH}}")
    print()

    pct = common_n / n_words * 100
    print(f'Most common word:  "{common_word}" ({common_n} times, {pct:.1f}% of words)')


if __name__ == "__main__":
    main()
