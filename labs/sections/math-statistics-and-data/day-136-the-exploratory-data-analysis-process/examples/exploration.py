"""The exploration machinery for Day 136: the loop, the holdout, the
research log, triage, a stopping rule, and the handoff to Day 133.

The two-sample z-test is the same from-scratch construction Day 118 built
(`phi`, `p_from_z_two_sided`, `z_critical_two_sided`, `two_sample_z_test`),
reused here rather than re-derived, because everything in this lab is
about WHEN you are allowed to trust a p-value, not how one is computed.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# The z-test, from math.erf alone (Day 118)
# ---------------------------------------------------------------------------


def phi(z: float) -> float:
    """The standard normal CDF, built from the error function."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def p_from_z_two_sided(z: float) -> float:
    return 2.0 * (1.0 - phi(abs(z)))


def z_critical_two_sided(alpha: float) -> float:
    """The z whose two-sided tail probability is alpha, found by bisecting
    `phi` -- there is no closed form for its inverse."""
    lo, hi = 0.0, 10.0
    target = 1.0 - alpha / 2.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if phi(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def two_sample_z_test(a, b) -> tuple[float, float]:
    """Welch-style two-sample z-test: each sample keeps its own variance."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    mean_a, mean_b = a.mean(), b.mean()
    var_a, var_b = a.var(ddof=1), b.var(ddof=1)
    se = math.sqrt(var_a / len(a) + var_b / len(b))
    z = (mean_a - mean_b) / se
    return z, p_from_z_two_sided(z)


def cohens_d(a, b) -> float:
    """A standardized effect size: the mean difference in pooled standard
    deviations, so effect sizes are comparable across differently-scaled
    outcome columns."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    n_a, n_b = len(a), len(b)
    pooled_var = ((n_a - 1) * a.var(ddof=1) + (n_b - 1) * b.var(ddof=1)) / (n_a + n_b - 2)
    pooled_sd = math.sqrt(pooled_var)
    return (a.mean() - b.mean()) / pooled_sd


# ---------------------------------------------------------------------------
# Exercise 1 -- forking paths, measured
# ---------------------------------------------------------------------------


def simulate_forking_paths(rng: np.random.Generator, k: int, families: int,
                            n_per_group: int, alpha: float) -> dict[str, float]:
    """Run `families` independent replicates of "an analyst tries k
    completely unrelated comparisons on data with no real signal", and
    measure the fraction of replicates where at least one comparison comes
    back significant.

    Fully vectorised: draws real two-group samples (not bare z-statistics),
    for `families * k` independent comparisons at once, then reduces along
    the sample axis to get each comparison's z-statistic.
    """
    group_a = rng.standard_normal((families, k, n_per_group))
    group_b = rng.standard_normal((families, k, n_per_group))
    mean_a, mean_b = group_a.mean(axis=-1), group_b.mean(axis=-1)
    var_a, var_b = group_a.var(axis=-1, ddof=1), group_b.var(axis=-1, ddof=1)
    se = np.sqrt(var_a / n_per_group + var_b / n_per_group)
    z = (mean_a - mean_b) / se

    z_crit = z_critical_two_sided(alpha)
    significant = np.abs(z) > z_crit  # shape (families, k)
    at_least_one = significant.any(axis=1)  # shape (families,)

    simulated_rate = float(at_least_one.mean())
    exact_rate = 1.0 - (1.0 - alpha) ** k
    standard_error = math.sqrt(exact_rate * (1.0 - exact_rate) / families)
    return {
        "k": k,
        "families": families,
        "simulated_rate": simulated_rate,
        "exact_rate": exact_rate,
        "standard_error": standard_error,
        "deviation": abs(simulated_rate - exact_rate),
    }


# ---------------------------------------------------------------------------
# Exercise 2 -- a plausible story for noise
# ---------------------------------------------------------------------------


def scan_narrative_frame(df: pd.DataFrame, subset_cols: list[str],
                          outcome_cols: list[str]) -> list[dict[str, Any]]:
    """The forking-paths problem, made concrete: every combination of a
    grouping column and an outcome column is one candidate analysis, run
    with `pandas.DataFrame.groupby`. Two cut definitions per subset column
    (the raw boolean split, and its complement re-cut against the median
    of a second column) double the honest comparison count -- an analyst
    rarely stops at trying a column once."""
    results: list[dict[str, Any]] = []
    for subset_col in subset_cols:
        for outcome_col in outcome_cols:
            for cut_name, mask in (
                ("raw_split", df[subset_col]),
                ("narrower_cut", df[subset_col] & df["signed_up_this_quarter"]),
            ):
                grouped = df.assign(_mask=mask).groupby("_mask")[outcome_col]
                if grouped.ngroups != 2:
                    continue
                a = df.loc[mask, outcome_col].to_numpy()
                b = df.loc[~mask, outcome_col].to_numpy()
                if len(a) < 5 or len(b) < 5:
                    continue
                z, p = two_sample_z_test(a, b)
                d = cohens_d(a, b)
                results.append({
                    "subset": subset_col,
                    "outcome": outcome_col,
                    "cut": cut_name,
                    "z": z,
                    "p": p,
                    "effect_size": d,
                    "significant": p < 0.05,
                })
    return results


def best_significant_result(results: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The lowest p-value among the significant results -- the one an
    analyst who stopped at the first "hit" would write up."""
    hits = [r for r in results if r["significant"]]
    if not hits:
        return None
    return min(hits, key=lambda r: r["p"])


# ---------------------------------------------------------------------------
# Exercise 3 -- the holdout rescues you
# ---------------------------------------------------------------------------


def build_holdout_frame(rng: np.random.Generator, n_total: int, real_delta: float,
                         sigma: float, n_spurious: int) -> pd.DataFrame:
    """One dataset with exactly one real, planted effect (`real_metric`,
    which genuinely differs by group) and many spurious columns (no true
    difference in any of them)."""
    group = rng.integers(0, 2, n_total).astype(bool)  # True = treatment
    data = {"group": group}
    data["real_metric"] = np.where(
        group,
        rng.normal(real_delta, sigma, n_total),
        rng.normal(0.0, sigma, n_total),
    )
    for i in range(n_spurious):
        data[f"spurious_{i}"] = rng.normal(0.0, sigma, n_total)
    return pd.DataFrame(data)


def split_exploration_confirmation(df: pd.DataFrame, rng: np.random.Generator,
                                    frac: float = 0.5) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Hold out a confirmation set at the START, before any question has
    been asked of the data -- the practical device that separates
    exploration from confirmation."""
    shuffled = df.sample(frac=1.0, random_state=int(rng.integers(0, 2**31 - 1))).reset_index(drop=True)
    cut = int(len(shuffled) * frac)
    return shuffled.iloc[:cut].reset_index(drop=True), shuffled.iloc[cut:].reset_index(drop=True)


def test_column_by_group(df: pd.DataFrame, column: str) -> tuple[float, float]:
    a = df.loc[df["group"], column].to_numpy()
    b = df.loc[~df["group"], column].to_numpy()
    return two_sample_z_test(a, b)


def best_spurious_column(exploration_df: pd.DataFrame, spurious_cols: list[str]) -> tuple[str, float, float]:
    """The exploration-only scan: test every spurious column, report the
    one that happens to look best -- exactly what an analyst chasing a
    plausible story would report, before checking anything held out."""
    best_col, best_z, best_p = None, 0.0, 1.0
    for col in spurious_cols:
        z, p = test_column_by_group(exploration_df, col)
        if p < best_p:
            best_col, best_z, best_p = col, z, p
    return best_col, best_z, best_p


# ---------------------------------------------------------------------------
# Exercise 4 -- choices are comparisons
# ---------------------------------------------------------------------------


def build_choices_frame(rng: np.random.Generator, n_rows: int) -> pd.DataFrame:
    """No real signal: `metric` is independent of `days_since_signup` and of
    every threshold you might cut it at."""
    return pd.DataFrame({
        "days_since_signup": rng.integers(1, 400, n_rows),
        "sessions": rng.poisson(5, n_rows),
        "metric": rng.normal(0.0, 1.0, n_rows),
    })


def best_of_choice_grid(df: pd.DataFrame, subset_cutoffs: list[int],
                         outcome_definitions: list[str]) -> dict[str, Any]:
    """Vary a subset filter (recency cutoff) and an outcome definition, with
    NO explicit hypothesis test declared per variant -- just "which cut
    looks best" -- and return the best-looking result. `outcome_definitions`
    names of the form "metric" or "metric_x2" select or transform the
    outcome column actually compared."""
    best = None
    for cutoff in subset_cutoffs:
        recent = df[df["days_since_signup"] <= cutoff]
        rest = df[df["days_since_signup"] > cutoff]
        if len(recent) < 5 or len(rest) < 5:
            continue
        for definition in outcome_definitions:
            if definition == "metric":
                a, b = recent["metric"].to_numpy(), rest["metric"].to_numpy()
            elif definition == "metric_scaled":
                a, b = recent["metric"].to_numpy() * recent["sessions"].to_numpy(), \
                       rest["metric"].to_numpy() * rest["sessions"].to_numpy()
            else:
                raise ValueError(f"unknown outcome definition: {definition}")
            z, p = two_sample_z_test(a, b)
            candidate = {"cutoff": cutoff, "definition": definition, "z": z, "p": p}
            if best is None or p < best["p"]:
                best = candidate
    return best


def simulate_choice_grid_best_p_rate(rng: np.random.Generator, families: int,
                                      n_rows: int, subset_cutoffs: list[int],
                                      outcome_definitions: list[str], alpha: float) -> dict[str, float]:
    """Under a TRUE null (no real signal anywhere), how often does the
    single best-looking cell of the choice grid come back "significant" at
    alpha, versus how often ONE pre-declared comparison would? This is the
    forking-paths rate for choices nobody called a test."""
    n_variants = len(subset_cutoffs) * len(outcome_definitions)
    naive_hits = 0
    single_hits = 0
    for _ in range(families):
        df = build_choices_frame(rng, n_rows)
        best = best_of_choice_grid(df, subset_cutoffs, outcome_definitions)
        if best["p"] < alpha:
            naive_hits += 1
        # the "single pre-declared comparison" control: always the first cell
        recent = df[df["days_since_signup"] <= subset_cutoffs[0]]
        rest = df[df["days_since_signup"] > subset_cutoffs[0]]
        _, p_single = two_sample_z_test(recent["metric"].to_numpy(), rest["metric"].to_numpy())
        if p_single < alpha:
            single_hits += 1
    return {
        "n_variants": n_variants,
        "families": families,
        "naive_best_rate": naive_hits / families,
        "single_declared_rate": single_hits / families,
    }


# ---------------------------------------------------------------------------
# Exercise 5 -- Bonferroni, and its limit
# ---------------------------------------------------------------------------


def bonferroni_alpha(alpha: float, m: int) -> float:
    return alpha / m


def simulate_family_wise_rate(rng: np.random.Generator, k: int, families: int,
                               alpha: float) -> float:
    z_crit = z_critical_two_sided(alpha)
    zs = rng.standard_normal((families, k))
    return float((np.abs(zs) > z_crit).any(axis=1).mean())


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
    was found -- including the nothings. The log's own length IS the
    comparison count; nothing needs to be counted separately or trusted."""

    entries: list[LogEntry] = field(default_factory=list)

    def record(self, question: str, look: str, outcome: str | None,
               timestamp: str | None = None) -> LogEntry:
        entry = LogEntry(
            timestamp=timestamp or datetime.now(timezone.utc).isoformat(),
            question=question,
            look=look,
            outcome=outcome,
        )
        self.entries.append(entry)
        return entry

    @property
    def comparison_count(self) -> int:
        return len(self.entries)

    @property
    def null_count(self) -> int:
        return sum(1 for e in self.entries if e.outcome is None)

    def findings(self) -> list[LogEntry]:
        return [e for e in self.entries if e.outcome is not None]


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
    """Expected information times decision relevance, per hour of cost.
    A question that would teach you a great deal but changes no decision
    scores low on purpose (Day 119's framing: an answer that would not
    change what you do is not worth pursuing first); a cheap question with
    real decision weight outranks an expensive one with the same weight."""
    return (candidate.expected_information * candidate.decision_relevance) / candidate.cost_hours


def rank_candidates(candidates: list[Candidate]) -> list[Candidate]:
    return sorted(candidates, key=triage_score, reverse=True)


# ---------------------------------------------------------------------------
# Exercise 8 -- a stopping rule
# ---------------------------------------------------------------------------


def time_boxed_exploration(rng: np.random.Generator, budget_questions: int,
                            alpha: float) -> dict[str, Any]:
    """Ask exactly `budget_questions` questions of data with no real signal,
    then stop, REGARDLESS of whether anything looked significant along the
    way. Returns whether ANY of the budget's questions crossed alpha (which
    can still happen by chance) and how many were asked."""
    z_crit = z_critical_two_sided(alpha)
    zs = rng.standard_normal(budget_questions)
    return {
        "questions_asked": budget_questions,
        "any_significant": bool(np.any(np.abs(zs) > z_crit)),
    }


def stop_when_significant_rate(rng: np.random.Generator, families: int,
                                max_questions: int, alpha: float) -> float:
    """The failure mode: keep asking questions of data with NO real signal
    and stop the moment one looks significant. Measures the fraction of
    "exploration sessions" that end in a reported false positive -- which
    is far higher than alpha, because you gave chance many tries."""
    z_crit = z_critical_two_sided(alpha)
    hits = 0
    for _ in range(families):
        zs = rng.standard_normal(max_questions)
        if np.any(np.abs(zs) > z_crit):
            hits += 1
    return hits / families


def time_boxed_false_positive_rate(rng: np.random.Generator, families: int,
                                    budget_questions: int, alpha: float) -> float:
    """The honest counterpart: a fixed budget of questions is asked and the
    session reports "found something" only if the LAST question asked (the
    one pre-declared for reporting) is significant -- not whichever of the
    budget happened to look best. This is what a time-box protects, if the
    analyst does not also silently swap in `stop_when_significant_rate`'s
    behaviour once inside the budget."""
    z_crit = z_critical_two_sided(alpha)
    hits = 0
    for _ in range(families):
        zs = rng.standard_normal(budget_questions)
        if abs(zs[-1]) > z_crit:
            hits += 1
    return hits / families


# ---------------------------------------------------------------------------
# Exercise 9 -- the handoff to Day 133
# ---------------------------------------------------------------------------


REQUIRED_HANDOFF_FIELDS = ("finding", "confirmation_result", "comparison_count")


def build_handoff(finding: dict[str, Any], confirmation_result: dict[str, Any],
                   comparison_count: int) -> dict[str, Any]:
    """The object exploration hands to Day 133's report stage. Every field
    is required -- a report cannot be written from a finding alone, because
    the reader needs to know it survived confirmation and how many things
    were looked at along the way."""
    handoff = {
        "finding": finding,
        "confirmation_result": confirmation_result,
        "comparison_count": comparison_count,
    }
    validate_handoff(handoff)
    return handoff


def validate_handoff(handoff: dict[str, Any]) -> None:
    missing = [f for f in REQUIRED_HANDOFF_FIELDS if f not in handoff or handoff[f] is None]
    if missing:
        raise ValueError(f"handoff is missing required field(s): {', '.join(missing)}")
    if not isinstance(handoff["comparison_count"], int) or handoff["comparison_count"] < 1:
        raise ValueError("comparison_count must be a positive integer")


def write_report_stub(handoff: dict[str, Any]) -> str:
    """A minimal stand-in for Day 133's report generator: it REFUSES to run
    without a valid handoff, the same way Day 133's generator refuses a
    figure with no stated question."""
    validate_handoff(handoff)
    finding = handoff["finding"]
    conf = handoff["confirmation_result"]
    return (
        f"Finding: {finding.get('name', 'unnamed')} "
        f"(exploration p={finding.get('p', float('nan')):.4g}). "
        f"Confirmed on holdout: p={conf.get('p', float('nan')):.4g}. "
        f"Comparisons run before this finding was reported: {handoff['comparison_count']}."
    )
