"""
Tests for starter Naive Bayes implementation.
"""
import pytest
import numpy as np
import nb_lib as nb


def test_tokenize_stub():
    with pytest.raises(NotImplementedError):
        nb.tokenize("Hello world")


def test_nb_stub():
    clf = nb.ScratchMultinomialNB()
    with pytest.raises(NotImplementedError):
        clf.fit(np.zeros((2, 2)), np.array([0, 1]))
