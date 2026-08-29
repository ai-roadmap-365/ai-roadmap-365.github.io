"""The nine-step pipeline for analyzing one A/B experiment end to end.

Every function here does exactly one step from the lesson, in the same
order: load and validate, check the randomization (sample-ratio mismatch),
describe the groups honestly, test the primary metric with a confidence
interval, express the effect size in real units, check the guardrail,
report segments without concluding from them, watch what peeking would have
done, and finally combine everything into one verdict. Nothing here imports
scipy or statsmodels -- the normal CDF needed for a p-value comes from
`math.erf`, exactly as Day 118 built it.
"""

from __future__ import annotations

import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

REQUIRED_COLUMNS = ("user_id", "group", "segment", "converted", "latency_ms", "time_on_page_sec")
VALID_GROUPS = ("control", "treatment")


# ---------------------------------------------------------------------------
# Exercise 1 -- load and validate
# ---------------------------------------------------------------------------


def load_experiment(path: str | Path) -> list[dict]:
    """Read the experiment CSV into a list of row dicts with the right
    types, and refuse to hand back data that cannot be trusted structurally.

    Raises ValueError if a required column is missing, any cell is empty, or
    a `group` value is anything other than "control"/"treatment". Does NOT
    check the balance of the split -- that is exercise 2's job, on purpose,
    because "the columns are well-formed" and "the randomization worked" are
    two different questions with two different failure modes.
    """
    path = Path(path)
    rows: list[dict] = []
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or set(REQUIRED_COLUMNS) - set(reader.fieldnames):
            missing = set(REQUIRED_COLUMNS) - set(reader.fieldnames or [])
            raise ValueError(f"missing required column(s): {sorted(missing)}")
        for i, raw in enumerate(reader, start=2):  # row 1 is the header
            for col in REQUIRED_COLUMNS:
                if raw.get(col, "") == "":
                    raise ValueError(f"missing value in column '{col}' at line {i}")
            if raw["group"] not in VALID_GROUPS:
                raise ValueError(f"unexpected group '{raw['group']}' at line {i}")
            rows.append(
                {
                    "user_id": int(raw["user_id"]),
                    "group": raw["group"],
                    "segment": raw["segment"],
                    "converted": int(raw["converted"]),
                    "latency_ms": float(raw["latency_ms"]),
                    "time_on_page_sec": float(raw["time_on_page_sec"]),
                }
            )
    if not rows:
        raise ValueError(f"{path} contains no data rows")
    return rows


# ---------------------------------------------------------------------------
# Exercise 2 -- the sample-ratio mismatch check
# ---------------------------------------------------------------------------


def srm_check(rows: list[dict], planned_split: float = 0.5, alpha: float = 0.001) -> dict:
    """A one-shot chi-squared goodness-of-fit test comparing the FINAL group
    counts against the planned split. With exactly two categories, chi2 with
    1 degree of freedom is the square of a standard normal, so its p-value
    has the closed form `erfc(sqrt(chi2 / 2))` -- no lookup table, no scipy.
    """
    n_control = sum(1 for r in rows if r["group"] == "control")
    n_treatment = sum(1 for r in rows if r["group"] == "treatment")
    n = n_control + n_treatment
    expected_control = n * planned_split
    expected_treatment = n * (1.0 - planned_split)
    chi2 = (n_control - expected_control) ** 2 / expected_control + (
        n_treatment - expected_treatment
    ) ** 2 / expected_treatment
    p_value = math.erfc(math.sqrt(chi2 / 2.0))
    observed_split = n_control / n
    return {
        "n_control": n_control,
        "n_treatment": n_treatment,
        "n": n,
        "planned_split": planned_split,
        "observed_split": observed_split,
        "chi2": chi2,
        "p_value": p_value,
        "alpha": alpha,
        "passed": p_value >= alpha,
    }


# ---------------------------------------------------------------------------
# Exercise 3 -- per-group descriptive summary
# ---------------------------------------------------------------------------


def group_summary(rows: list[dict], metric: str = "time_on_page_sec") -> dict:
    """Mean, median, sample standard deviation, min and max of `metric`,
    computed separately for each group. Day 116's lesson in one function:
    report both the mean and the median, because a handful of extreme
    sessions can drag the mean away from where "most users" actually sit."""
    out: dict = {}
    for group in VALID_GROUPS:
        values = [r[metric] for r in rows if r["group"] == group]
        out[group] = {
            "n": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
            "min": min(values),
            "max": max(values),
        }
    return out


# ---------------------------------------------------------------------------
# Exercise 4 -- the primary-metric test, with a confidence interval
# ---------------------------------------------------------------------------


def _normal_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def primary_test(rows: list[dict], metric: str = "converted", conf: float = 0.95) -> dict:
    """A two-proportion z-test on `metric` (must be 0/1), plus a Wald
    confidence interval on the difference (treatment minus control). The
    z-statistic and its two-sided p-value use the POOLED proportion, which
    is standard for the hypothesis test; the confidence interval uses the
    UNPOOLED standard error, which is standard for interval estimation --
    the two are different questions and conventionally use different
    variance estimates.
    """
    control = [r[metric] for r in rows if r["group"] == "control"]
    treatment = [r[metric] for r in rows if r["group"] == "treatment"]
    n_c, n_t = len(control), len(treatment)
    p_c, p_t = sum(control) / n_c, sum(treatment) / n_t
    diff = p_t - p_c

    pooled = (sum(control) + sum(treatment)) / (n_c + n_t)
    se_pooled = math.sqrt(pooled * (1.0 - pooled) * (1.0 / n_c + 1.0 / n_t))
    z = diff / se_pooled if se_pooled > 0 else 0.0
    p_value = 2.0 * (1.0 - _normal_cdf(abs(z)))

    se_unpooled = math.sqrt(p_c * (1.0 - p_c) / n_c + p_t * (1.0 - p_t) / n_t)
    # two-sided critical value for `conf`, via the inverse of the normal CDF
    # approximated by binary search -- avoids needing scipy.stats.norm.ppf.
    z_crit = _inverse_normal_cdf(0.5 + conf / 2.0)
    ci_low = diff - z_crit * se_unpooled
    ci_high = diff + z_crit * se_unpooled

    return {
        "metric": metric,
        "n_control": n_c,
        "n_treatment": n_t,
        "p_control": p_c,
        "p_treatment": p_t,
        "diff": diff,
        "z": z,
        "p_value": p_value,
        "conf": conf,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "excludes_zero": ci_low > 0.0 or ci_high < 0.0,
    }


def _inverse_normal_cdf(target: float, lo: float = -10.0, hi: float = 10.0) -> float:
    """Bisection search for the z such that Phi(z) == target. 60 iterations
    on a range of 20 gets well past double precision; this is not meant to be
    fast, only exact enough and dependency-free."""
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if _normal_cdf(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


# ---------------------------------------------------------------------------
# Exercise 5 -- effect size, in the metric's own units
# ---------------------------------------------------------------------------


def effect_size(primary_result: dict) -> dict:
    """The absolute difference in percentage points, AND the relative lift
    -- never report a p-value alone. Relative lift is undefined if the
    control rate is zero; that is reported explicitly rather than silently
    divided."""
    diff_pp = primary_result["diff"] * 100.0
    p_c = primary_result["p_control"]
    relative_lift_pct = (primary_result["diff"] / p_c * 100.0) if p_c > 0 else None
    return {
        "abs_diff_pp": diff_pp,
        "relative_lift_pct": relative_lift_pct,
        "ci_low_pp": primary_result["ci_low"] * 100.0,
        "ci_high_pp": primary_result["ci_high"] * 100.0,
    }


# ---------------------------------------------------------------------------
# Exercise 6 -- the guardrail
# ---------------------------------------------------------------------------


def guardrail_check(
    rows: list[dict],
    metric: str = "latency_ms",
    tolerance: float = 5.0,
    lower_is_better: bool = True,
) -> dict:
    """A guardrail metric must not worsen by more than `tolerance` in its own
    units. For a lower-is-better metric like latency, "worse" means
    treatment's mean exceeds control's mean by more than `tolerance`."""
    control = [r[metric] for r in rows if r["group"] == "control"]
    treatment = [r[metric] for r in rows if r["group"] == "treatment"]
    mean_c = statistics.mean(control)
    mean_t = statistics.mean(treatment)
    diff = mean_t - mean_c
    worsened = diff if lower_is_better else -diff
    return {
        "metric": metric,
        "control_mean": mean_c,
        "treatment_mean": mean_t,
        "diff": diff,
        "tolerance": tolerance,
        "passed": worsened <= tolerance,
    }


# ---------------------------------------------------------------------------
# Exercise 7 -- segment analysis, reported not concluded
# ---------------------------------------------------------------------------


def segment_analysis(rows: list[dict], metric: str = "converted") -> dict:
    """Per-segment lift, alongside the pooled lift, with an explicit flag
    when a segment's sign disagrees with the pooled sign -- a Simpson's-
    paradox-shaped reversal. This function never recommends a decision from
    a segment; it only reports and flags."""
    by_segment: dict[str, dict] = {}
    segments = sorted({r["segment"] for r in rows})
    for segment in segments:
        seg_rows = [r for r in rows if r["segment"] == segment]
        result = primary_test(seg_rows, metric=metric)
        by_segment[segment] = {
            "n_control": result["n_control"],
            "n_treatment": result["n_treatment"],
            "diff_pp": result["diff"] * 100.0,
        }

    pooled = primary_test(rows, metric=metric)
    pooled_diff_pp = pooled["diff"] * 100.0
    pooled_sign = _sign(pooled_diff_pp)

    reversed_segments = [
        segment
        for segment, info in by_segment.items()
        if info["diff_pp"] != 0 and _sign(info["diff_pp"]) != pooled_sign and pooled_sign != 0
    ]
    all_segments_reversed = len(reversed_segments) == len(segments) and len(segments) > 0

    return {
        "segments": by_segment,
        "pooled_diff_pp": pooled_diff_pp,
        "reversed_segments": reversed_segments,
        "reversal_flagged": all_segments_reversed,
    }


def _sign(x: float) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


# ---------------------------------------------------------------------------
# Exercise 8 -- peeking on real data
# ---------------------------------------------------------------------------


def peek_path(rows: list[dict], metric: str = "converted", checkpoint_every: int = 500) -> list[dict]:
    """Walk `rows` in the order they appear in the file (the simulated
    arrival order) and compute the primary-metric p-value at every
    `checkpoint_every` rows using only the data seen so far. Returns one
    entry per checkpoint. Nothing here decides to stop early -- that
    decision, and its cost, is exercise 9 and the lesson's point."""
    path: list[dict] = []
    seen: list[dict] = []
    for i, row in enumerate(rows, start=1):
        seen.append(row)
        if i % checkpoint_every == 0:
            n_c = sum(1 for r in seen if r["group"] == "control")
            n_t = sum(1 for r in seen if r["group"] == "treatment")
            if n_c == 0 or n_t == 0:
                continue
            result = primary_test(seen, metric=metric)
            path.append(
                {
                    "n": i,
                    "diff_pp": result["diff"] * 100.0,
                    "p_value": result["p_value"],
                    "significant": result["p_value"] < 0.05,
                }
            )
    return path


def crossed_significance(path: list[dict], alpha: float = 0.05) -> bool:
    """True if the running p-value dropped below `alpha` at any checkpoint
    before the last one -- the moment a peeker watching live would have been
    tempted to stop."""
    return any(point["p_value"] < alpha for point in path[:-1])


# ---------------------------------------------------------------------------
# Exercise 9 -- the verdict
# ---------------------------------------------------------------------------


def verdict(
    srm_result: dict,
    primary_result: dict,
    guardrail_result: dict,
    segment_result: dict,
    alpha: float = 0.05,
) -> dict:
    """Combine every prior step into one plain-language verdict.

    If the sample-ratio mismatch check failed, this function REFUSES to
    compute ship/inconclusive from the primary result at all -- randomization
    that did not work makes the treatment and control groups no longer
    comparable, so no downstream number can be trusted, however clean it
    looks. That refusal is itself the verdict.
    """
    if not srm_result["passed"]:
        return {
            "verdict": "do not trust this result",
            "refused": True,
            "reason": (
                "sample-ratio mismatch check failed "
                f"(observed split {srm_result['observed_split']:.3f}, "
                f"planned {srm_result['planned_split']:.3f}, "
                f"p={srm_result['p_value']:.2e} < alpha={srm_result['alpha']}); "
                "randomization cannot be trusted, so no effect estimate downstream can be trusted either"
            ),
        }

    significant = primary_result["p_value"] < alpha and primary_result["excludes_zero"]
    guardrail_ok = guardrail_result["passed"]

    if significant and guardrail_ok:
        outcome = "ship"
    elif significant and not guardrail_ok:
        outcome = "do not trust this result"
    else:
        outcome = "inconclusive"

    note = ""
    if segment_result["reversal_flagged"]:
        note = (
            " Every segment shows the OPPOSITE sign from the pooled result "
            "-- this is exploratory and must be investigated before shipping, "
            "regardless of what the pooled number says."
        )

    return {
        "verdict": outcome,
        "refused": False,
        "estimate_pp": primary_result["diff"] * 100.0,
        "ci_pp": (primary_result["ci_low"] * 100.0, primary_result["ci_high"] * 100.0),
        "would_flip_if_ci_included_zero": not primary_result["excludes_zero"],
        "guardrail_ok": guardrail_ok,
        "note": note,
    }
