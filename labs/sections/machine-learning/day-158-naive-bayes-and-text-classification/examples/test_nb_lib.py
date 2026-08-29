"""
Tests for reference Naive Bayes implementation.
"""
import pytest
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
import nb_lib as nb


def test_tokenize_and_vocab():
    docs = ["Free cash prize now!", "Winner of cash prize", "Meeting at noon"]
    vocab = nb.build_vocabulary(docs)
    assert "cash" in vocab
    assert "prize" in vocab
    assert "meeting" in vocab

    bow = nb.text_to_bow(docs, vocab)
    assert bow.shape == (3, len(vocab))
    # Check 'cash' appears in first two docs
    cash_idx = vocab["cash"]
    assert bow[0, cash_idx] == 1.0
    assert bow[1, cash_idx] == 1.0
    assert bow[2, cash_idx] == 0.0


def test_scratch_nb_matches_scikit_learn():
    train_texts = [
        "win cash prize today claim now",
        "free lottery ticket winner cash",
        "quarterly financial report team meeting",
        "project review and schedule sync meeting tomorrow",
    ]
    y_train = np.array([1, 1, 0, 0]) # 1=spam, 0=ham

    vec = CountVectorizer()
    X_sk = vec.fit_transform(train_texts).toarray()
    
    # Scikit-learn MultinomialNB
    sk_nb = MultinomialNB(alpha=1.0)
    sk_nb.fit(X_sk, y_train)

    # Scratch MultinomialNB
    scratch_nb = nb.ScratchMultinomialNB(alpha=1.0)
    scratch_nb.fit(X_sk, y_train)

    # Verify log priors match
    np.testing.assert_allclose(scratch_nb.class_log_prior_, sk_nb.class_log_prior_, atol=1e-7)

    # Verify feature log probabilities match
    np.testing.assert_allclose(scratch_nb.feature_log_prob_, sk_nb.feature_log_prob_, atol=1e-7)

    # Verify predictions on test sample
    test_texts = ["claim free cash", "schedule project meeting"]
    X_test = vec.transform(test_texts).toarray()

    sk_preds = sk_nb.predict(X_test)
    scratch_preds = scratch_nb.predict(X_test)
    np.testing.assert_array_equal(scratch_preds, sk_preds)
