"""The machine learning workflow as runnable stages, with contracts.

The workflow in the textbook is a row of boxes with arrows. This module is
the same workflow with the arrows made load-bearing: every stage declares
what it requires and what it produces, the runner refuses to run a stage
whose inputs are absent, and every run leaves a step log and a manifest of
content hashes behind it.

That is not ceremony. The point of this lab is that **the same three
stages in a different order produce a different number**, and that the
wrong order is silent. A stage contract is what turns a silent
twenty-three point lie into a loud error naming the stage that broke.
"""

from __future__ import annotations

import hashlib
import inspect
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier


class StageContractError(RuntimeError):
    """Raised when a stage is asked to run without the inputs it declared."""


# --------------------------------------------------------------------------
# The runner
# --------------------------------------------------------------------------


@dataclass
class Artifact:
    """Everything the pipeline knows so far, plus how it came to know it."""

    data: dict = field(default_factory=dict)
    log: list = field(default_factory=list)

    def with_(self, **produced) -> "Artifact":
        """Return a new artifact carrying the additional keys.

        Deliberately not in-place. A stage that mutates its input makes the
        step log a work of fiction, because the log then describes states
        that no longer exist.
        """
        merged = dict(self.data)
        merged.update(produced)
        return Artifact(data=merged, log=list(self.log))


@dataclass
class Stage:
    """One step of the workflow, with its input and output contract."""

    name: str
    run: Callable[[Artifact], dict]
    requires: tuple = ()
    produces: tuple = ()


def run_pipeline(stages, artifact: Artifact, enforce_contracts: bool = True) -> Artifact:
    """Run every stage in order, recording what each one did.

    With ``enforce_contracts=False`` the runner behaves like most real
    pipelines: it runs whatever it is given, in whatever order, and reports
    a number. Exercise 3 measures what that costs.
    """
    for stage in stages:
        if enforce_contracts:
            missing = [k for k in stage.requires if k not in artifact.data]
            if missing:
                raise StageContractError(
                    f"stage {stage.name!r} requires {missing} which no earlier stage produced"
                )
        produced = stage.run(artifact)
        if enforce_contracts:
            unexpected = sorted(set(produced) - set(stage.produces))
            absent = sorted(set(stage.produces) - set(produced))
            if absent or unexpected:
                raise StageContractError(
                    f"stage {stage.name!r} declared {list(stage.produces)} "
                    f"but produced {sorted(produced)}"
                )
        artifact = artifact.with_(**produced)
        artifact.log.append((stage.name, tuple(sorted(produced))))
    return artifact


def step_log(artifact: Artifact):
    """The ordered record of which stage produced which keys."""
    return list(artifact.log)


def fingerprint(value) -> str:
    """A stable content hash for an array, a number or a string."""
    if isinstance(value, np.ndarray):
        payload = np.ascontiguousarray(value).tobytes() + str(value.dtype).encode()
    else:
        payload = repr(value).encode()
    return hashlib.sha256(payload).hexdigest()[:16]


def manifest(artifact: Artifact, keys) -> dict:
    """Content hashes for the named keys, so two runs can be compared.

    A pipeline that cannot prove it produced the same thing twice cannot be
    debugged, because you can never tell a fix from a coincidence.
    """
    return {k: fingerprint(artifact.data[k]) for k in sorted(keys)}


def stage_source_lines(stages) -> dict:
    """How many lines of code each stage's function actually is.

    Self-referential on purpose: exercise 7 uses this to measure the shape
    of this very pipeline, rather than repeating the folklore figure about
    how much of the work is not modelling.
    """
    out = {}
    for stage in stages:
        source = inspect.getsource(stage.run)
        lines = [ln for ln in source.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        out[stage.name] = len(lines)
    return out


# --------------------------------------------------------------------------
# Datasets
# --------------------------------------------------------------------------


def noise_dataset(n_samples: int = 100, n_features: int = 5000, seed: int = 143):
    """Labels are coin flips. No feature carries any information whatsoever.

    Any workflow that reports better than chance on this data has a bug,
    and the bug is what exercise 3 is about.
    """
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n_samples, n_features))
    y = rng.integers(0, 2, size=n_samples)
    return X, y


def imbalanced_dataset(n: int, seed: int, rate: float = 0.08):
    """A rare positive class whose features overlap the negatives.

    Eight percent positive, shifted by 1.1 standard deviations. Separable
    enough to be worth modelling, overlapping enough that the metric you
    choose decides which model wins.
    """
    rng = np.random.default_rng(seed)
    n_pos = int(round(n * rate))
    y = np.zeros(n, dtype=int)
    y[:n_pos] = 1
    X = rng.normal(size=(n, 4))
    X[y == 1] += 1.1
    order = rng.permutation(n)
    return X[order], y[order]


# --------------------------------------------------------------------------
# The individual steps, usable on their own
# --------------------------------------------------------------------------


def correlation_ranking(X, y):
    """Absolute correlation between each column and the label."""
    y = np.asarray(y, dtype=float)
    out = np.empty(X.shape[1])
    for j in range(X.shape[1]):
        out[j] = abs(float(np.corrcoef(X[:, j], y)[0, 1]))
    return out


def top_k_features(X, y, k: int):
    """The k columns most correlated with the label, as indices."""
    return np.argsort(correlation_ranking(X, y))[-k:]


def folds(X, y, n_splits: int = 5, seed: int = 143):
    """Deterministic stratified folds, so both orderings see the same splits."""
    return list(StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed).split(X, y))


def select_then_split_score(X, y, k: int = 20, n_splits: int = 5, seed: int = 143) -> float:
    """The WRONG order: choose features using every row, then cross-validate.

    Every fold's test rows helped choose the features, so the features were
    fitted to the answers. Nothing raises. A number comes out.
    """
    chosen = top_k_features(X, y, k)
    scores = []
    for train, test in folds(X, y, n_splits, seed):
        model = KNeighborsClassifier(1).fit(X[train][:, chosen], y[train])
        scores.append(float(np.mean(model.predict(X[test][:, chosen]) == y[test])))
    return float(np.mean(scores))


def split_then_select_score(X, y, k: int = 20, n_splits: int = 5, seed: int = 143) -> float:
    """The RIGHT order: split first, then choose features inside each fold."""
    scores = []
    for train, test in folds(X, y, n_splits, seed):
        chosen = top_k_features(X[train], y[train], k)
        model = KNeighborsClassifier(1).fit(X[train][:, chosen], y[train])
        scores.append(float(np.mean(model.predict(X[test][:, chosen]) == y[test])))
    return float(np.mean(scores))


def inflation_by_k(X, y, ks, n_splits: int = 5, seed: int = 143):
    """How much the wrong order inflates the score, at each feature count."""
    rows = []
    for k in ks:
        wrong = select_then_split_score(X, y, k, n_splits, seed)
        right = split_then_select_score(X, y, k, n_splits, seed)
        rows.append((k, round(wrong, 4), round(right, 4), round(wrong - right, 4)))
    return rows


# --------------------------------------------------------------------------
# Metrics, baselines and error analysis
# --------------------------------------------------------------------------


def candidate_models() -> dict:
    """The five candidates exercise 4 compares. Settings are fixed."""
    return {
        "majority baseline": DummyClassifier(strategy="most_frequent"),
        "logistic (default threshold)": LogisticRegression(max_iter=1000),
        "logistic (balanced)": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "5-NN": KNeighborsClassifier(5),
        "depth-3 tree": DecisionTreeClassifier(max_depth=3, random_state=0),
    }


def score_all(models: dict, X_train, y_train, X_test, y_test) -> dict:
    """Accuracy, precision, recall and F1 for every candidate."""
    out = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        out[name] = {
            "accuracy": round(float(accuracy_score(y_test, pred)), 4),
            "precision": round(float(precision_score(y_test, pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, pred, zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, pred, zero_division=0)), 4),
        }
    return out


def winner(scores: dict, metric: str) -> str:
    """Which candidate a given metric would have you ship."""
    return max(scores, key=lambda name: scores[name][metric])


def error_table(model, X_test, y_test):
    """The confusion matrix, as plain integers -- rows true, columns predicted."""
    return confusion_matrix(y_test, model.predict(X_test)).tolist()


# --------------------------------------------------------------------------
# The stages themselves
# --------------------------------------------------------------------------


def _stage_load(artifact: Artifact) -> dict:
    X, y = noise_dataset(
        artifact.data["n_samples"], artifact.data["n_features"], artifact.data["seed"]
    )
    return {"X": X, "y": y}


def _stage_split(artifact: Artifact) -> dict:
    return {"folds": folds(artifact.data["X"], artifact.data["y"], seed=artifact.data["seed"])}


def _stage_select(artifact: Artifact) -> dict:
    """Choose features. Requires `folds`, so it cannot run before the split."""
    per_fold = []
    for train, _test in artifact.data["folds"]:
        per_fold.append(
            top_k_features(
                artifact.data["X"][train], artifact.data["y"][train], artifact.data["k"]
            )
        )
    return {"selected": per_fold}


def _stage_leaky_select(artifact: Artifact) -> dict:
    """Choose features from every row at once, then reuse them in every fold.

    This is what a leaky pipeline actually does. It is not a strawman: the
    global selection is computed once, which is cheaper, and then handed to
    every fold as though it had been computed there.
    """
    chosen = top_k_features(artifact.data["X"], artifact.data["y"], artifact.data["k"])
    n_folds = len(artifact.data.get("folds", [])) or artifact.data["n_splits"]
    return {"selected": [chosen for _ in range(n_folds)]}


def _stage_fit_and_score(artifact: Artifact) -> dict:
    scores = []
    for (train, test), chosen in zip(artifact.data["folds"], artifact.data["selected"]):
        model = KNeighborsClassifier(1).fit(
            artifact.data["X"][train][:, chosen], artifact.data["y"][train]
        )
        pred = model.predict(artifact.data["X"][test][:, chosen])
        scores.append(float(np.mean(pred == artifact.data["y"][test])))
    return {"fold_scores": np.array(scores), "score": float(np.mean(scores))}


def _stage_baseline(artifact: Artifact) -> dict:
    y = artifact.data["y"]
    counts = np.bincount(y)
    return {"baseline": float(counts.max() / len(y))}


def honest_stages():
    """Load, split, select inside the split, fit, baseline. In that order."""
    return [
        Stage("load", _stage_load, requires=("n_samples", "n_features", "seed"), produces=("X", "y")),
        Stage("split", _stage_split, requires=("X", "y", "seed"), produces=("folds",)),
        Stage("select", _stage_select, requires=("X", "y", "folds", "k"), produces=("selected",)),
        Stage(
            "fit_and_score",
            _stage_fit_and_score,
            requires=("X", "y", "folds", "selected"),
            produces=("fold_scores", "score"),
        ),
        Stage("baseline", _stage_baseline, requires=("y",), produces=("baseline",)),
    ]


def leaky_stages():
    """The same five stages, with selection moved in front of the split.

    Note the `select` stage still declares `folds` among its requirements,
    because that requirement is *true*: choosing features is a per-fold
    operation. Declaring it honestly is the entire mechanism by which the
    runner can notice the ordering is wrong. A team that writes
    `requires=("X", "y")` here has not been caught out by a subtle bug --
    they have written down a claim that is false.
    """
    return [
        Stage("load", _stage_load, requires=("n_samples", "n_features", "seed"), produces=("X", "y")),
        Stage(
            "select",
            _stage_leaky_select,
            requires=("X", "y", "folds", "k"),
            produces=("selected",),
        ),
        Stage("split", _stage_split, requires=("X", "y", "seed"), produces=("folds",)),
        Stage(
            "fit_and_score",
            _stage_fit_and_score,
            requires=("X", "y", "folds", "selected"),
            produces=("fold_scores", "score"),
        ),
        Stage("baseline", _stage_baseline, requires=("y",), produces=("baseline",)),
    ]


def starting_artifact(
    n_samples: int = 100,
    n_features: int = 5000,
    k: int = 20,
    seed: int = 143,
    n_splits: int = 5,
):
    """The inputs the pipeline is given before any stage has run."""
    return Artifact(
        data={
            "n_samples": n_samples,
            "n_features": n_features,
            "k": k,
            "seed": seed,
            "n_splits": n_splits,
        }
    )
