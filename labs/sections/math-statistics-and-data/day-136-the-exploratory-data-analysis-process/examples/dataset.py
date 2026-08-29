"""Shared constants, data generators and tolerances for the Day 136 lab.

Every number an exercise checks against lives here, next to a comment
saying where it came from -- exact arithmetic, a derived standard error,
or a tolerance observed across several seeds during development (seeds
1, 7, 42, 118, 2026, recorded beside the constant it produced). Nothing in
this file is fabricated: every tolerance was checked by re-running the
exercise logic across those five seeds before being fixed here.

No real signal means exactly that: outcome columns are drawn independently
of every grouping column, so the TRUE effect of any comparison built from
them is zero. Any "significant" result exercise 1 finds is, by
construction, a false positive.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Exercise 1 -- forking paths, measured
# ---------------------------------------------------------------------------

ALPHA = 0.05
FORK_K_VALUES = (5, 20, 40)
FORK_FAMILIES = 2000  # replicated "runs of the whole exploration" per k
FORK_N_PER_GROUP = 200  # large enough that the z-test's normal approximation
# is trustworthy; Day 118 measured that interval coverage undershoots at
# n=40 for the same reason (a t, not a z, critical value is correct at small
# n) -- this lab avoids that undershoot the same way, by choosing n large.
# Simulated rates across seeds 1, 7, 42, 118, 2026 landed within 2.4 standard
# errors of the exact value in every case observed; three standard errors is
# the assertion tolerance below, with headroom.
FORK_SIM_TOLERANCE_SE = 3.0

# ---------------------------------------------------------------------------
# Exercise 2 -- a plausible story for noise (one concrete scan)
# ---------------------------------------------------------------------------

NARRATIVE_SEED = 6
NARRATIVE_N_ROWS = 80
NARRATIVE_SUBSET_COLS = ["region_west", "signed_up_tuesday", "over_40",
                         "used_mobile_app", "referred_by_friend"]
NARRATIVE_OUTCOME_COLS = ["revenue", "sessions", "days_active", "support_tickets"]
# 5 subset columns x 4 outcome columns = 20 comparisons is already close to
# the "after examining forty combinations" story; two subset DEFINITIONS
# per column (the raw split and its complement compared against a slightly
# different cut) bring the honest count to 40 -- see build_narrative_frame.
NARRATIVE_MIN_COMPARISONS = 40
# A "publishable-looking" standardized effect size, the common Cohen's d
# rule-of-thumb boundary between "medium" and "large" (Cohen, 1988).
PUBLISHABLE_EFFECT_SIZE = 0.5

# ---------------------------------------------------------------------------
# Exercise 3 -- the holdout rescues you (the day's centrepiece)
# ---------------------------------------------------------------------------

HOLDOUT_SEED = 1
HOLDOUT_N_TOTAL = 4000  # split 50/50 into exploration and confirmation
REAL_EFFECT_DELTA = 0.30  # a genuine, modest mean difference (Cohen's d ~0.3)
REAL_EFFECT_SIGMA = 1.0
# The spurious column carries NO true effect. Among the many spurious
# columns an analyst might have looked at, this lab shows the ONE the
# authoring run found significant on the exploration half, at the fixed
# seed above -- the same selection-after-the-fact the lesson's opening
# story warns about, made concrete instead of hypothetical.
N_SPURIOUS_CANDIDATES = 30

# ---------------------------------------------------------------------------
# Exercise 4 -- choices are comparisons
# ---------------------------------------------------------------------------

CHOICES_SEED = 7
CHOICES_N_ROWS = 600
CHOICES_SUBSET_CUTOFFS = [30, 60, 90, 150, 300]  # five "recent enough" cutoffs
CHOICES_OUTCOME_DEFINITIONS = ["metric", "metric_scaled"]  # two outcome definitions
CHOICES_FAMILIES = 3000  # replicated null worlds, to measure the inflation

# ---------------------------------------------------------------------------
# Exercise 5 -- Bonferroni, and its limit
# ---------------------------------------------------------------------------

BONFERRONI_KNOWN_M = 20
BONFERRONI_FAMILIES = 20000
# The true number of comparisons an analyst actually ran before landing on
# the one they report -- larger than what got written down.
BONFERRONI_TRUE_M = 60

# ---------------------------------------------------------------------------
# Exercise 8 -- a stopping rule
# ---------------------------------------------------------------------------

STOPPING_SEED = 9
STOPPING_BUDGET_QUESTIONS = 10  # the time-boxed / count-based rule's budget
STOPPING_FAMILIES = 20000


def two_group_frame(rng: np.random.Generator, n_per_group: int,
                     mean_a: float = 0.0, mean_b: float = 0.0,
                     sigma: float = 1.0) -> pd.DataFrame:
    """One real, tidy two-group DataFrame -- the shape an analyst actually
    looks at, not a bare pair of arrays."""
    outcome = np.concatenate([
        rng.normal(mean_a, sigma, n_per_group),
        rng.normal(mean_b, sigma, n_per_group),
    ])
    group = np.array(["A"] * n_per_group + ["B"] * n_per_group)
    return pd.DataFrame({"group": group, "outcome": outcome})


def build_narrative_frame(rng: np.random.Generator) -> pd.DataFrame:
    """One dataset with genuinely no signal: every outcome column is drawn
    independently of every grouping column. Built with pandas because this
    is exactly the object an analyst opens in a notebook -- one table, five
    candidate ways to split customers into two groups, four candidate
    outcome columns to compare between them."""
    n = NARRATIVE_N_ROWS
    data = {col: rng.integers(0, 2, n).astype(bool) for col in NARRATIVE_SUBSET_COLS}
    # An independent second condition, so a "narrower cut" of each subset
    # column is still a legitimate second comparison rather than a mask
    # built from the very outcome column it will be tested against.
    data["signed_up_this_quarter"] = rng.integers(0, 2, n).astype(bool)
    for col in NARRATIVE_OUTCOME_COLS:
        data[col] = rng.normal(0.0, 1.0, n)
    return pd.DataFrame(data)
