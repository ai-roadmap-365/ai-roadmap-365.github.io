"""
Naive Bayes reference library.
"""
import numpy as np
import re


def tokenize(text: str) -> list[str]:
    """
    Tokenize raw text into lowercase alphanumeric words: [a-z0-9_]+
    """
    return re.findall(r"\b\w+\b", text.lower())


def build_vocabulary(corpus: list[str]) -> dict[str, int]:
    """
    Build word-to-index mapping sorted alphabetically from a list of documents.
    """
    vocab = set()
    for doc in corpus:
        tokens = tokenize(doc)
        vocab.update(tokens)
    sorted_words = sorted(list(vocab))
    return {w: i for i, w in enumerate(sorted_words)}


def text_to_bow(corpus: list[str], vocab: dict[str, int]) -> np.ndarray:
    """
    Convert text corpus into a Bag-of-Words count matrix (N, V).
    """
    matrix = np.zeros((len(corpus), len(vocab)), dtype=float)
    for doc_idx, doc in enumerate(corpus):
        tokens = tokenize(doc)
        for token in tokens:
            if token in vocab:
                matrix[doc_idx, vocab[token]] += 1.0
    return matrix


class ScratchMultinomialNB:
    """
    Multinomial Naive Bayes with Laplace smoothing:
    theta_{c, j} = (N_{c, j} + alpha) / (N_c + alpha * V)
    log P(y=c | x) = log P(y=c) + sum_j x_j * log theta_{c, j}
    """
    def __init__(self, alpha: float = 1.0):
        self.alpha = float(alpha)
        self.class_log_prior_ = None
        self.feature_log_prob_ = None
        self.classes_ = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        self.classes_ = np.unique(y)
        num_classes = len(self.classes_)
        num_features = X.shape[1]
        
        self.class_log_prior_ = np.zeros(num_classes)
        self.feature_log_prob_ = np.zeros((num_classes, num_features))
        
        total_samples = len(y)
        
        for c_idx, c in enumerate(self.classes_):
            X_c = X[y == c]
            # Prior: P(y=c) = N_c / N
            self.class_log_prior_[c_idx] = np.log(len(X_c) / total_samples)
            
            # Word counts for class c
            word_counts_c = np.sum(X_c, axis=0) # (V,)
            total_words_c = np.sum(word_counts_c)
            
            # Laplace smoothed conditional probability:
            # theta_{c, j} = (count_{c, j} + alpha) / (total_words_c + alpha * V)
            smoothed_prob = (word_counts_c + self.alpha) / (total_words_c + self.alpha * num_features)
            self.feature_log_prob_[c_idx] = np.log(smoothed_prob)
            
        return self

    def predict_log_proba(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        # joint_log_prob = log_prior + X @ log_prob.T  ==> (N, K)
        return self.class_log_prior_ + np.dot(X, self.feature_log_prob_.T)

    def predict(self, X: np.ndarray) -> np.ndarray:
        log_probs = self.predict_log_proba(X)
        best_indices = np.argmax(log_probs, axis=1)
        return self.classes_[best_indices]
