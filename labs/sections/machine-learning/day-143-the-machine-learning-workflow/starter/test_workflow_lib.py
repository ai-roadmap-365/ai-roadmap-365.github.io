"""Machinery checks: the runner itself behaves, before any claim is made.

These four tests are solved in both `starter/` and `examples/`. They exist
so that a broken runner reports itself as a broken runner rather than as a
surprising scientific result.
"""

import numpy as np
import pytest

import workflow_lib as w


def test_the_artifact_is_immutable_and_carries_its_history():
    start = w.Artifact(data={"a": 1})
    nxt = start.with_(b=2)
    assert start.data == {"a": 1}
    assert nxt.data == {"a": 1, "b": 2}
    assert nxt is not start
    # Overwriting a key is allowed; silently mutating the original is not.
    third = nxt.with_(a=99)
    assert third.data["a"] == 99 and nxt.data["a"] == 1


def test_the_fingerprint_is_stable_content_addressing():
    a = np.arange(10)
    b = np.arange(10)
    assert w.fingerprint(a) == w.fingerprint(b)
    assert w.fingerprint(a) != w.fingerprint(np.arange(11))
    # dtype is part of the identity: the same values in a different type
    # are a different artifact, and treating them as equal hides real bugs.
    assert w.fingerprint(np.arange(10)) != w.fingerprint(np.arange(10, dtype=float))
    assert len(w.fingerprint(a)) == 16


def test_the_contract_checks_both_directions():
    called = []

    def under_producing(_artifact):
        called.append("under")
        return {}

    stages = [w.Stage("under", under_producing, requires=(), produces=("x",))]
    with pytest.raises(w.StageContractError) as excinfo:
        w.run_pipeline(stages, w.Artifact(data={}))
    assert "'under'" in str(excinfo.value)
    assert called == ["under"]

    def over_producing(_artifact):
        return {"x": 1, "surprise": 2}

    stages = [w.Stage("over", over_producing, requires=(), produces=("x",))]
    with pytest.raises(w.StageContractError):
        w.run_pipeline(stages, w.Artifact(data={}))


def test_the_folds_are_stratified_and_cover_every_row_exactly_once():
    X, y = w.imbalanced_dataset(500, seed=3)
    splits = w.folds(X, y, n_splits=5, seed=143)
    assert len(splits) == 5
    seen = np.concatenate([test for _train, test in splits])
    assert sorted(seen.tolist()) == list(range(500))
    # Stratified: every fold carries roughly the population positive rate.
    rate = float(y.mean())
    for _train, test in splits:
        assert abs(float(y[test].mean()) - rate) < 0.02
