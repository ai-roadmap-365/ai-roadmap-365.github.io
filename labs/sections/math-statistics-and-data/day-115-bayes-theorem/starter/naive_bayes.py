"""Exercises 8 and 9: Naive Bayes from scratch, and why it must be built in
log space.

"Naive" names one specific, false assumption: that every word in a document
is conditionally independent of every other word, given the document's
class. Fill in the bodies marked `# YOUR CODE HERE`.
"""

import math
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction


def tokenize(text: str) -> list[str]:
    """The whole tokenizer this lab needs: lowercase, split on whitespace."""
    return text.lower().split()


@dataclass(frozen=True)
class NaiveBayesModel:
    """Word counts, vocabulary and class priors, trained from labelled
    documents. Everything downstream -- smoothed or not, log space or not --
    is computed from these four fields alone.
    """

    classes: tuple[str, ...]
    vocabulary: frozenset[str]
    word_counts: dict[str, Counter]
    total_words: dict[str, int]
    doc_counts: dict[str, int]

    @property
    def total_docs(self) -> int:
        return sum(self.doc_counts.values())


def train(docs_by_class: dict[str, tuple[str, ...]]) -> NaiveBayesModel:
    """Count every word in every class's training documents.

    For each class: tokenize every document, accumulate word counts in a
    `Counter`, track the running total word count, and grow the shared
    vocabulary set with every token seen (in ANY class).
    """
    # YOUR CODE HERE
    raise NotImplementedError


def class_prior(model: NaiveBayesModel, cls: str) -> Fraction:
    """P(class) = documents in that class / total training documents."""
    # YOUR CODE HERE
    raise NotImplementedError


def word_probability(model: NaiveBayesModel, word: str, cls: str, alpha: int) -> Fraction:
    """P(word | class), with Laplace (add-alpha) smoothing.

    (count(word, class) + alpha) / (total_words[class] + alpha * |vocabulary|)

    alpha = 0 reproduces the unsmoothed textbook version: a word with zero
    occurrences in a class gets probability exactly 0.
    """
    # YOUR CODE HERE
    raise NotImplementedError


def document_score(model: NaiveBayesModel, tokens: list[str], cls: str, alpha: int) -> Fraction:
    """The (unnormalised) joint probability P(class) x product of
    P(word | class) over every word in the document, computed as an exact
    Fraction by literal multiplication. Skip any token that never appeared
    in ANY training class (out-of-vocabulary).
    """
    # YOUR CODE HERE
    raise NotImplementedError


def classify(model: NaiveBayesModel, text: str, alpha: int) -> tuple[str, dict[str, Fraction]]:
    """Predict the class with the highest unnormalised joint probability.
    Returns the winning class and every class's raw score.
    """
    # YOUR CODE HERE
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 9: log space, and why a product of many small floats is not
# optional to avoid
# ---------------------------------------------------------------------------


def multiply_probabilities(factors: list[float]) -> float:
    """The naive way: multiply plain Python floats together, one at a time."""
    # YOUR CODE HERE
    raise NotImplementedError


def sum_of_logs(factors: list[float]) -> float:
    """The fix: work in log space. Use `math.fsum` over `math.log(factor)`
    for each factor, rather than a running `+=` sum.
    """
    # YOUR CODE HERE
    raise NotImplementedError


def document_log_score(model: NaiveBayesModel, tokens: list[str], cls: str, alpha: int) -> float:
    """The log-space equivalent of document_score: sum of logs instead of
    a product of probabilities.
    """
    # YOUR CODE HERE
    raise NotImplementedError


def classify_log_space(model: NaiveBayesModel, text: str, alpha: int) -> tuple[str, dict[str, float]]:
    """The same classification decision as classify(), but computed in log
    space.
    """
    # YOUR CODE HERE
    raise NotImplementedError
