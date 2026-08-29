"""The nine-step pipeline for analyzing one A/B experiment end to end.

Work through `starter/00_brief.md` in order, filling in the functions below.
Check your progress with:

    .venv/bin/pytest starter -q

Unattempted work reports as skipped, never failed. Every function currently
raises NotImplementedError -- replace the body, not just the signature.
"""

from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path

REQUIRED_COLUMNS = ("user_id", "group", "segment", "converted", "latency_ms", "time_on_page_sec")
VALID_GROUPS = ("control", "treatment")


def load_experiment(path: str | Path) -> list[dict]:
    """Exercise 1. Read the CSV at `path` into a list of row dicts with
    `user_id` and `converted` as int, `latency_ms` and `time_on_page_sec` as
    float, and `group`/`segment` as the raw strings.

    Raise ValueError if a required column is missing, any cell is empty, or
    `group` is not "control" or "treatment". This function does NOT check
    whether the split is balanced -- that is exercise 2.
    """
    raise NotImplementedError


def srm_check(rows: list[dict], planned_split: float = 0.5, alpha: float = 0.001) -> dict:
    """Exercise 2. The sample-ratio mismatch check: a one-shot chi-squared
    goodness-of-fit test comparing the FINAL group counts against
    `planned_split`. With two categories, chi2 with 1 degree of freedom is
    the square of a standard normal, so its p-value has the closed form
    `math.erfc(math.sqrt(chi2 / 2))`.

    Return a dict with at least: n_control, n_treatment, n, planned_split,
    observed_split, chi2, p_value, alpha, passed (bool, True means the
    check PASSED -- the split looks like what was planned).
    """
    raise NotImplementedError


def group_summary(rows: list[dict], metric: str = "time_on_page_sec") -> dict:
    """Exercise 3. Per-group mean, median, sample standard deviation, min
    and max of `metric`. Return `{"control": {...}, "treatment": {...}}`.
    """
    raise NotImplementedError


def primary_test(rows: list[dict], metric: str = "converted", conf: float = 0.95) -> dict:
    """Exercise 4. A two-proportion z-test on `metric` (must be 0/1), plus a
    confidence interval on the difference (treatment minus control).

    Use the POOLED proportion for the z-statistic and its p-value, and the
    UNPOOLED proportions for the interval's standard error -- the
    conventional choice for each question. `math.erf` gives you the normal
    CDF; you will need its inverse for the interval's critical value (write
    a small bisection search, or reuse one you already wrote for Day 118).

    Return a dict with at least: p_control, p_treatment, diff, z, p_value,
    ci_low, ci_high, excludes_zero (bool).
    """
    raise NotImplementedError


def effect_size(primary_result: dict) -> dict:
    """Exercise 5. From a `primary_test` result, compute the absolute
    difference in percentage points AND the relative lift as a percentage
    of the control rate (None if the control rate is zero). Return both,
    plus the interval endpoints in percentage points.
    """
    raise NotImplementedError


def guardrail_check(
    rows: list[dict],
    metric: str = "latency_ms",
    tolerance: float = 5.0,
    lower_is_better: bool = True,
) -> dict:
    """Exercise 6. Compare the treatment and control means of a guardrail
    metric. For a lower-is-better metric, the guardrail FAILS if treatment's
    mean exceeds control's mean by more than `tolerance`.
    """
    raise NotImplementedError


def segment_analysis(rows: list[dict], metric: str = "converted") -> dict:
    """Exercise 7. Per-segment lift (reuse `primary_test` on each segment's
    rows), the pooled lift, and a `reversal_flagged` bool that is True only
    when EVERY segment's sign is the opposite of the pooled sign -- a
    Simpson's-paradox-shaped reversal. Report, never conclude, from a single
    segment.
    """
    raise NotImplementedError


def peek_path(rows: list[dict], metric: str = "converted", checkpoint_every: int = 500) -> list[dict]:
    """Exercise 8. Walk `rows` in file order, computing the primary p-value
    from everything seen so far every `checkpoint_every` rows. Return one
    dict per checkpoint with at least: n, diff_pp, p_value, significant.
    """
    raise NotImplementedError


def crossed_significance(path: list[dict], alpha: float = 0.05) -> bool:
    """Exercise 8. True if any checkpoint BEFORE THE LAST ONE has
    p_value < alpha."""
    raise NotImplementedError


def verdict(
    srm_result: dict,
    primary_result: dict,
    guardrail_result: dict,
    segment_result: dict,
    alpha: float = 0.05,
) -> dict:
    """Exercise 9. Combine every prior step into one verdict.

    If the SRM check failed, REFUSE to compute ship/inconclusive at all --
    return a dict with `verdict="do not trust this result"`, `refused=True`
    and a `reason`, and nothing that looks like a trustworthy effect
    estimate (no `estimate_pp` key).

    Otherwise: "ship" if the primary result is significant, its interval
    excludes zero, AND the guardrail passed; "do not trust this result" if
    significant but the guardrail failed; "inconclusive" otherwise.
    """
    raise NotImplementedError
