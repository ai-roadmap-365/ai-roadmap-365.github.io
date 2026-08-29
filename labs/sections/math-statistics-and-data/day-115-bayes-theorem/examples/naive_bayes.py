"""Exercises 8 and 9: Naive Bayes from scratch, and why it must be built in
log space.

"Naive" names one specific, false assumption: that every word in a document
is conditionally independent of every other word, given the document's
class. That assumption is false -- word choice is not independent of
context -- and the classifier is useful anyway, because getting the RELATIVE
ranking of P(spam | words) versus P(ham | words) right does not require the
individual word-independence assumption to be true, only for its errors to
not systematically favour the wrong class.
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
    """Count every word in every class's training documents."""
    word_counts: dict[str, Counter] = {}
    total_words: dict[str, int] = {}
    doc_counts: dict[str, int] = {}
    vocabulary: set[str] = set()

    for cls, docs in docs_by_class.items():
        counts: Counter = Counter()
        for doc in docs:
            tokens = tokenize(doc)
            counts.update(tokens)
            vocabulary.update(tokens)
        word_counts[cls] = counts
        total_words[cls] = sum(counts.values())
        doc_counts[cls] = len(docs)

    return NaiveBayesModel(
        classes=tuple(docs_by_class.keys()),
        vocabulary=frozenset(vocabulary),
        word_counts=word_counts,
        total_words=total_words,
        doc_counts=doc_counts,
    )


def class_prior(model: NaiveBayesModel, cls: str) -> Fraction:
    """P(class) = documents in that class / total training documents."""
    return Fraction(model.doc_counts[cls], model.total_docs)


def word_probability(model: NaiveBayesModel, word: str, cls: str, alpha: int) -> Fraction:
    """P(word | class), with Laplace (add-alpha) smoothing.

    alpha = 0 reproduces the unsmoothed textbook version: a word with zero
    occurrences in a class gets probability exactly 0. alpha = 1 (the
    default this lab uses when smoothing) redistributes a small amount of
    probability mass to every word in the vocabulary, including ones never
    seen in this class, so no single word can zero out the whole document.
    """
    count = model.word_counts[cls][word]
    vocab_size = len(model.vocabulary)
    numerator = count + alpha
    denominator = model.total_words[cls] + alpha * vocab_size
    return Fraction(numerator, denominator)


def document_score(model: NaiveBayesModel, tokens: list[str], cls: str, alpha: int) -> Fraction:
    """The (unnormalised) joint probability P(class) x product of
    P(word | class) over every word in the document, computed as an exact
    Fraction by literal multiplication -- never divided by P(words) to
    normalise, because argmax over classes does not need the shared
    denominator. Out-of-vocabulary words (never seen in ANY training class)
    are skipped rather than scored, exactly as most real implementations
    handle them.
    """
    score = class_prior(model, cls)
    for word in tokens:
        if word not in model.vocabulary:
            continue
        score *= word_probability(model, word, cls, alpha)
    return score


def classify(model: NaiveBayesModel, text: str, alpha: int) -> tuple[str, dict[str, Fraction]]:
    """Predict the class with the highest unnormalised joint probability,
    computed exactly with Fraction. Returns the winning class and every
    class's raw score, so a caller can see exactly how close -- or how
    lopsided -- the decision was.
    """
    tokens = tokenize(text)
    scores = {cls: document_score(model, tokens, cls, alpha) for cls in model.classes}
    winner = max(scores, key=lambda cls: scores[cls])
    return winner, scores


# ---------------------------------------------------------------------------
# Exercise 9: log space, and why a product of many small floats is not
# optional to avoid
# ---------------------------------------------------------------------------


def multiply_probabilities(factors: list[float]) -> float:
    """The naive way: multiply plain Python floats together, one at a time.

    A document with several hundred words, each contributing a per-word
    probability on the order of a few percent, produces exactly this
    computation -- and float64 cannot represent the result once it falls
    below about 5e-324: it silently becomes 0.0, and every class's score
    ties at zero.
    """
    product = 1.0
    for factor in factors:
        product *= factor
    return product


def sum_of_logs(factors: list[float]) -> float:
    """The fix: work in log space. A product of small numbers becomes a
    sum of (large, negative, and very much NOT tiny) numbers, and float64
    represents sums like this one without any trouble at all.
    """
    return math.fsum(math.log(factor) for factor in factors)


def document_log_score(model: NaiveBayesModel, tokens: list[str], cls: str, alpha: int) -> float:
    """The log-space equivalent of document_score: sum of logs instead of
    a product of probabilities. This is what a real implementation uses --
    document_score above exists in this lab to make the underflow failure
    visible, not because it is the version you should ship.
    """
    log_score = math.log(float(class_prior(model, cls)))
    for word in tokens:
        if word not in model.vocabulary:
            continue
        log_score += math.log(float(word_probability(model, word, cls, alpha)))
    return log_score


def classify_log_space(model: NaiveBayesModel, text: str, alpha: int) -> tuple[str, dict[str, float]]:
    """The same classification decision as classify(), but computed in log
    space -- the version that does not silently break on a longer document
    or a larger vocabulary.
    """
    tokens = tokenize(text)
    scores = {cls: document_log_score(model, tokens, cls, alpha) for cls in model.classes}
    winner = max(scores, key=lambda cls: scores[cls])
    return winner, scores
