"""The exploration machinery for Day 136 -- YOUR skeleton.

Read `00_brief.md` first, then fill these in one at a time. Check yourself
as you go:

    .venv/bin/pytest starter -q

Unattempted functions raise `NotImplementedError`, which the test suite
reports as SKIPPED, not failed. A skip means "not attempted yet"; a
failure means "attempted and wrong", and shows your answer next to the
correct one.

The two-sample z-test (`phi`, `p_from_z_two_sided`, `z_critical_two_sided`,
`two_sample_z_test`) is the same from-scratch construction Day 118 built.
If you kept your Day 118 solution, your versions will work here unchanged.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# The z-test, from math.erf alone (Day 118) -- carry your solution forward,
# or rebuild it here.
# ---------------------------------------------------------------------------


def phi(z: float) -> float:
    """The standard normal CDF, built from the error function."""
    raise NotImplementedError


def p_from_z_two_sided(z: float) -> float:
    raise NotImplementedError


def z_critical_two_sided(alpha: float) -> float:
    """The z whose two-sided tail probability is alpha, found by bisecting
    `phi` -- there is no closed form for its inverse."""
    raise NotImplementedError


def two_sample_z_test(a, b) -> tuple[float, float]:
    """Welch-style two-sample z-test: each sample keeps its own variance."""
    raise NotImplementedError


def cohens_d(a, b) -> float:
    """A standardized effect size: the mean difference in pooled standard
    deviations, so effect sizes are comparable across differently-scaled
    outcome columns."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 1 -- forking paths, measured
# ---------------------------------------------------------------------------


def simulate_forking_paths(rng: np.random.Generator, k: int, families: int,
                            n_per_group: int, alpha: float) -> dict[str, float]:
    """Run `families` independent replicates of "an analyst tries k
    completely unrelated comparisons on data with no real signal", and
    measure the fraction of replicates where at least one comparison comes
    back significant. Return a dict with keys "k", "families",
    "simulated_rate", "exact_rate", "standard_error", "deviation".

    Vectorize it: draw two arrays of shape (families, k, n_per_group) with
    `rng.standard_normal`, reduce along the last axis to get each
    comparison's mean and variance, then its z-statistic.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 2 -- a plausible story for noise
# ---------------------------------------------------------------------------


def scan_narrative_frame(df: pd.DataFrame, subset_cols: list[str],
                          outcome_cols: list[str]) -> list[dict[str, Any]]:
    """Every combination of a grouping column and an outcome column is one
    candidate analysis. For each subset column, run it twice: once as the
    raw boolean split, and once narrowed by `& df["signed_up_this_quarter"]`
    (call the second cut "narrower_cut"). Return one dict per comparison
    with keys "subset", "outcome", "cut", "z", "p", "effect_size",
    "significant" (p < 0.05). Skip any split where either side has fewer
    than 5 rows.
    """
    raise NotImplementedError


def best_significant_result(results: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The lowest p-value among the significant results, or None if none
    of them were significant."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 3 -- the holdout rescues you (the day's centrepiece)
# ---------------------------------------------------------------------------


def build_holdout_frame(rng: np.random.Generator, n_total: int, real_delta: float,
                         sigma: float, n_spurious: int) -> pd.DataFrame:
    """One dataset with exactly one real, planted effect (`real_metric`,
    genuinely `real_delta` higher when `group` is True) and `n_spurious`
    spurious columns named `spurious_0` .. `spurious_{n_spurious-1}` with
    no true difference in any of them."""
    raise NotImplementedError


def split_exploration_confirmation(df: pd.DataFrame, rng: np.random.Generator,
                                    frac: float = 0.5) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Shuffle the frame (use `df.sample(frac=1.0, random_state=...)` seeded
    from `rng`) and split it into an exploration half and a confirmation
    half at `frac`."""
    raise NotImplementedError


def test_column_by_group(df: pd.DataFrame, column: str) -> tuple[float, float]:
    """Two-sample z-test of `column`, split by the boolean `group` column."""
    raise NotImplementedError


def best_spurious_column(exploration_df: pd.DataFrame, spurious_cols: list[str]) -> tuple[str, float, float]:
    """Test every spurious column against `group` on `exploration_df` only,
    and return (column_name, z, p) for whichever one has the smallest p."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 4 -- choices are comparisons
# ---------------------------------------------------------------------------


def build_choices_frame(rng: np.random.Generator, n_rows: int) -> pd.DataFrame:
    """Columns "days_since_signup" (integers 1-399), "sessions" (Poisson,
    mean 5) and "metric" (standard normal, independent of everything)."""
    raise NotImplementedError


def best_of_choice_grid(df: pd.DataFrame, subset_cutoffs: list[int],
                         outcome_definitions: list[str]) -> dict[str, Any]:
    """For every (cutoff, outcome definition) pair -- "metric" as-is, or
    "metric_scaled" (metric * sessions) -- split on
    `days_since_signup <= cutoff` and run a two-sample z-test. Return the
    single dict with keys "cutoff", "definition", "z", "p" that has the
    smallest p across the whole grid. Skip any split with fewer than 5 rows
    on either side."""
    raise NotImplementedError


def simulate_choice_grid_best_p_rate(rng: np.random.Generator, families: int,
                                      n_rows: int, subset_cutoffs: list[int],
                                      outcome_definitions: list[str], alpha: float) -> dict[str, float]:
    """Across `families` freshly generated no-signal datasets, measure how
    often `best_of_choice_grid`'s winner is significant at `alpha`
    ("naive_best_rate"), versus how often ONE pre-declared comparison
    (cutoff=subset_cutoffs[0], definition="metric") is significant
    ("single_declared_rate"). Return a dict with keys "n_variants",
    "families", "naive_best_rate", "single_declared_rate"."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 5 -- Bonferroni, and its limit
# ---------------------------------------------------------------------------


def bonferroni_alpha(alpha: float, m: int) -> float:
    raise NotImplementedError


def simulate_family_wise_rate(rng: np.random.Generator, k: int, families: int,
                               alpha: float) -> float:
    """Draw `families` families of `k` independent standard-normal
    z-statistics and return the fraction of families with at least one
    exceeding the two-sided critical value for `alpha`."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 6 -- the research log as a data structure
# ---------------------------------------------------------------------------


@dataclass
class LogEntry:
    timestamp: str
    question: str
    look: str
    outcome: str | None  # None is a valid, recorded outcome: "nothing found"


@dataclass
class ResearchLog:
    """A dated record of every question asked, what was looked at, and what
    was found -- including the nothings."""

    entries: list[LogEntry] = field(default_factory=list)

    def record(self, question: str, look: str, outcome: str | None,
               timestamp: str | None = None) -> LogEntry:
        """Append a LogEntry (timestamp defaults to now, in UTC ISO format
        if none is given) and return it."""
        raise NotImplementedError

    @property
    def comparison_count(self) -> int:
        raise NotImplementedError

    @property
    def null_count(self) -> int:
        """How many entries have outcome is None."""
        raise NotImplementedError

    def findings(self) -> list[LogEntry]:
        """Every entry whose outcome is NOT None."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 7 -- triage
# ---------------------------------------------------------------------------


@dataclass
class Candidate:
    name: str
    expected_information: float  # 0-1: how much this could change our belief
    cost_hours: float  # analyst-hours to answer
    decision_relevance: float  # 0-1: how much the answer could change a decision


def triage_score(candidate: Candidate) -> float:
    """expected_information * decision_relevance, divided by cost_hours."""
    raise NotImplementedError


def rank_candidates(candidates: list[Candidate]) -> list[Candidate]:
    """Candidates sorted by `triage_score`, highest first."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 8 -- a stopping rule
# ---------------------------------------------------------------------------


def time_boxed_false_positive_rate(rng: np.random.Generator, families: int,
                                    budget_questions: int, alpha: float) -> float:
    """Across `families` sessions, each draws `budget_questions` standard-
    normal z-statistics (no real signal). A session counts as a reported
    false positive only if its LAST question (index -1, the one
    pre-declared for reporting) exceeds the two-sided critical value.
    Return the fraction of sessions that report one."""
    raise NotImplementedError


def stop_when_significant_rate(rng: np.random.Generator, families: int,
                                max_questions: int, alpha: float) -> float:
    """Across `families` sessions, each draws up to `max_questions`
    standard-normal z-statistics (no real signal). A session counts as a
    reported false positive if ANY of its questions exceeds the two-sided
    critical value. Return the fraction of sessions that report one."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 9 -- the handoff to Day 133
# ---------------------------------------------------------------------------


REQUIRED_HANDOFF_FIELDS = ("finding", "confirmation_result", "comparison_count")


def build_handoff(finding: dict[str, Any], confirmation_result: dict[str, Any],
                   comparison_count: int) -> dict[str, Any]:
    """Assemble a dict with keys "finding", "confirmation_result",
    "comparison_count", call `validate_handoff` on it, and return it."""
    raise NotImplementedError


def validate_handoff(handoff: dict[str, Any]) -> None:
    """Raise ValueError naming every missing or None required field. Also
    raise ValueError if comparison_count is not a positive integer."""
    raise NotImplementedError


def write_report_stub(handoff: dict[str, Any]) -> str:
    """Call `validate_handoff` first (so this refuses an incomplete
    handoff), then return a one-line summary string naming the finding,
    its exploration and confirmation p-values, and the comparison count."""
    raise NotImplementedError
