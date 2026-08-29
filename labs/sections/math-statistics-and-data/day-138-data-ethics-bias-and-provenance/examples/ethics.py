"""Bias you can measure — the measurement and documentation functions.

Every function here is deterministic. The ones that draw data take an
explicit seed and use ``numpy.random.default_rng``, so the same seed gives
the same numbers on every machine and every run. Nothing in this module
reads a real dataset about real people: every table is constructed here,
in code, with properties chosen so that the thing being demonstrated is a
fact about the construction rather than a claim about anyone.

The module has four groups of functions:

* measurement of bias  -- ``biased_frame_experiment``, ``coverage_report``,
  ``proxy_gap_experiment``, ``aggregation_bias_experiment``
* fairness accounting  -- ``fairness_population``, ``evaluate_policy``,
  ``calibration_by_score_bin``, ``fairness_incompatibility``
* disclosure risk      -- ``unique_row_count``, ``generalise_quasi_ids``,
  ``k_anonymity_level``, ``suppress_small_classes``, ``homogeneous_classes``
* documentation        -- ``check_datasheet``, ``diff_versions``
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 1. More data does not fix a biased frame
# ---------------------------------------------------------------------------

#: The world the sample is drawn from. Group "B" is one tenth of the
#: population and its outcome sits INTERCEPT_GAP units above group "A" at
#: every value of x. The slope is identical for both groups, so the only
#: thing a pooled straight-line fit can get wrong about group B is the
#: intercept -- which makes the bias analytically predictable and therefore
#: checkable rather than merely plausible.
POPULATION_SHARE_B = 0.10
FRAME_SHARE_B = 0.01
INTERCEPT_A = 2.0
INTERCEPT_B = 8.0
INTERCEPT_GAP = INTERCEPT_B - INTERCEPT_A
TRUE_SLOPE = 1.0
NOISE_SD = 1.0


def draw_from_frame(n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Draw ``n`` rows the way the biased sampling frame draws them.

    The frame reaches group B with probability ``FRAME_SHARE_B`` rather than
    its true population share ``POPULATION_SHARE_B``. Everything else about
    the two groups is identical: same x distribution, same slope, same noise.
    """
    group = np.where(rng.random(n) < FRAME_SHARE_B, "B", "A")
    x = rng.uniform(0.0, 10.0, size=n)
    intercept = np.where(group == "B", INTERCEPT_B, INTERCEPT_A)
    y = intercept + TRUE_SLOPE * x + rng.normal(0.0, NOISE_SD, size=n)
    return pd.DataFrame({"group": group, "x": x, "y": y})


def fit_pooled_line(frame: pd.DataFrame) -> tuple[float, float]:
    """Ordinary least squares of y on x, ignoring the group column entirely.

    Returns ``(slope, intercept)``. This is the model almost everyone fits
    first: one line for everybody.
    """
    slope, intercept = np.polyfit(frame["x"].to_numpy(), frame["y"].to_numpy(), 1)
    return float(slope), float(intercept)


def signed_group_error(slope: float, intercept: float, group: str) -> float:
    """Signed prediction error of a pooled line for one group's true line.

    Because both groups share ``TRUE_SLOPE``, the error is the same at every
    x, so a single number describes it exactly: predicted intercept minus
    true intercept, plus the slope error times a representative x. Evaluated
    at x = 5, the midpoint of the x range.
    """
    true_intercept = INTERCEPT_B if group == "B" else INTERCEPT_A
    x_mid = 5.0
    predicted = intercept + slope * x_mid
    truth = true_intercept + TRUE_SLOPE * x_mid
    return float(predicted - truth)


def biased_frame_experiment(
    n: int, replicates: int = 40, seed: int = 138
) -> dict[str, float]:
    """Fit the pooled line ``replicates`` times at sample size ``n``.

    Returns the mean signed error for each group across replicates (the
    BIAS -- what more data cannot fix) and the standard deviation of that
    error across replicates (the VARIANCE -- what more data does fix), plus
    the in-sample RMSE, which is the number that makes the model look fine.
    """
    root = np.random.default_rng(seed)
    seeds = root.integers(0, 2**32 - 1, size=replicates)

    errors_a: list[float] = []
    errors_b: list[float] = []
    rmses: list[float] = []
    b_shares: list[float] = []

    for s in seeds:
        rng = np.random.default_rng(int(s))
        sample = draw_from_frame(n, rng)
        slope, intercept = fit_pooled_line(sample)
        errors_a.append(signed_group_error(slope, intercept, "A"))
        errors_b.append(signed_group_error(slope, intercept, "B"))
        predicted = intercept + slope * sample["x"].to_numpy()
        residual = sample["y"].to_numpy() - predicted
        rmses.append(float(np.sqrt(np.mean(residual**2))))
        b_shares.append(float((sample["group"] == "B").mean()))

    return {
        "n": float(n),
        "replicates": float(replicates),
        "bias_a": float(np.mean(errors_a)),
        "bias_b": float(np.mean(errors_b)),
        "sd_b": float(np.std(errors_b, ddof=1)),
        "sd_a": float(np.std(errors_a, ddof=1)),
        "in_sample_rmse": float(np.mean(rmses)),
        "sample_share_b": float(np.mean(b_shares)),
    }


def bias_variance_ladder(
    sizes: Sequence[int] = (500, 5_000, 50_000),
    replicates: int = 40,
    seed: int = 138,
) -> pd.DataFrame:
    """Run ``biased_frame_experiment`` at each sample size and tabulate it."""
    rows = [biased_frame_experiment(n, replicates=replicates, seed=seed) for n in sizes]
    table = pd.DataFrame(rows)
    table["n"] = table["n"].astype("int64")
    return table


# ---------------------------------------------------------------------------
# 2. Coverage mismatch, computed
# ---------------------------------------------------------------------------


def coverage_report(
    sample_counts: Mapping[str, int],
    reference_shares: Mapping[str, float],
    flag_below: float = 0.5,
    flag_above: float = 2.0,
) -> dict[str, Any]:
    """Compare a sample's group composition against a reference population.

    ``total_variation_distance`` is one half the sum of absolute differences
    between the two share vectors: 0.0 when the sample mirrors the reference,
    1.0 when they share no mass at all. It is a single summary, so it is
    reported alongside the thing that actually names the problem: a
    per-group ``representation_ratio`` of sample share divided by reference
    share. A ratio of 0.1 means the group appears at one tenth of the rate
    the reference population says it should.

    A group is flagged when its ratio falls outside
    ``[flag_below, flag_above]``.
    """
    groups = sorted(set(sample_counts) | set(reference_shares))
    total = sum(sample_counts.values())
    if total <= 0:
        raise ValueError("sample_counts must contain at least one row")

    sample_shares = {g: sample_counts.get(g, 0) / total for g in groups}
    ratios: dict[str, float] = {}
    flagged: list[str] = []
    for g in groups:
        reference = reference_shares.get(g, 0.0)
        if reference <= 0.0:
            ratios[g] = float("inf") if sample_shares[g] > 0 else 1.0
        else:
            ratios[g] = sample_shares[g] / reference
        if ratios[g] < flag_below or ratios[g] > flag_above:
            flagged.append(g)

    tvd = 0.5 * sum(
        abs(sample_shares[g] - reference_shares.get(g, 0.0)) for g in groups
    )

    return {
        "groups": groups,
        "sample_shares": sample_shares,
        "reference_shares": dict(reference_shares),
        "representation_ratio": ratios,
        "total_variation_distance": float(tvd),
        "flagged": flagged,
        "worst_group": min(ratios, key=lambda g: ratios[g]),
    }


# ---------------------------------------------------------------------------
# 3. The proxy gap
# ---------------------------------------------------------------------------

#: Group B's need is recorded at ACCESS_FACTOR_B of its true level, because
#: the proxy measures a recorded interaction rather than the need itself and
#: group B interacts with the recording system less often. Group A's need is
#: recorded faithfully.
ACCESS_FACTOR_A = 1.0
ACCESS_FACTOR_B = 0.85


def proxy_gap_experiment(
    n_a: int = 3_000, n_b: int = 1_000, budget: int = 500, seed: int = 138
) -> dict[str, Any]:
    """Rank by a proxy, then check what that costs against the real target.

    Both groups are drawn from the SAME true-need distribution, so a fair
    procedure would select them in proportion to their size. The proxy
    understates group B's need systematically. Selecting the top ``budget``
    rows by proxy is compared against selecting the top ``budget`` by true
    need, and both the composition and the total true need served are
    reported for each.
    """
    rng = np.random.default_rng(seed)
    n = n_a + n_b
    group = np.array(["A"] * n_a + ["B"] * n_b)
    true_need = rng.normal(50.0, 10.0, size=n)
    access = np.where(group == "B", ACCESS_FACTOR_B, ACCESS_FACTOR_A)
    proxy = true_need * access + rng.normal(0.0, 2.0, size=n)

    frame = pd.DataFrame({"group": group, "true_need": true_need, "proxy": proxy})

    by_proxy = frame.nlargest(budget, "proxy")
    by_target = frame.nlargest(budget, "true_need")

    population_share_b = n_b / n
    return {
        "budget": budget,
        "population_share_b": float(population_share_b),
        "proxy_correlation": float(frame["proxy"].corr(frame["true_need"])),
        "selected_share_b_by_proxy": float((by_proxy["group"] == "B").mean()),
        "selected_share_b_by_target": float((by_target["group"] == "B").mean()),
        "need_served_by_proxy": float(by_proxy["true_need"].sum()),
        "need_served_by_target": float(by_target["true_need"].sum()),
        "b_need_served_by_proxy": float(
            by_proxy.loc[by_proxy["group"] == "B", "true_need"].sum()
        ),
        "b_need_served_by_target": float(
            by_target.loc[by_target["group"] == "B", "true_need"].sum()
        ),
    }


# ---------------------------------------------------------------------------
# 4. Aggregation bias
# ---------------------------------------------------------------------------


def aggregation_bias_experiment(
    n_per_group: int = 2_000, seed: int = 138
) -> dict[str, Any]:
    """One pooled line against two per-group lines on the same rows.

    Group A lives at low x with a high intercept; group B lives at high x
    with a much higher intercept. Both groups have a NEGATIVE true slope.
    Pooled, the group offset dominates and the fitted slope comes out
    positive: a single model that is wrong in direction for every subgroup
    in the data, while looking like a confident fit overall.
    """
    rng = np.random.default_rng(seed)
    x_a = rng.uniform(0.0, 5.0, size=n_per_group)
    y_a = 10.0 - 1.0 * x_a + rng.normal(0.0, 1.0, size=n_per_group)
    x_b = rng.uniform(5.0, 10.0, size=n_per_group)
    y_b = 30.0 - 1.0 * x_b + rng.normal(0.0, 1.0, size=n_per_group)

    frame = pd.DataFrame(
        {
            "group": np.array(["A"] * n_per_group + ["B"] * n_per_group),
            "x": np.concatenate([x_a, x_b]),
            "y": np.concatenate([y_a, y_b]),
        }
    )

    pooled_slope, pooled_intercept = fit_pooled_line(frame)

    per_group: dict[str, dict[str, float]] = {}
    pooled_rmse: dict[str, float] = {}
    grouped_rmse: dict[str, float] = {}
    for name, part in frame.groupby("group", observed=True):
        slope, intercept = np.polyfit(part["x"].to_numpy(), part["y"].to_numpy(), 1)
        per_group[str(name)] = {"slope": float(slope), "intercept": float(intercept)}
        own = intercept + slope * part["x"].to_numpy()
        pool = pooled_intercept + pooled_slope * part["x"].to_numpy()
        grouped_rmse[str(name)] = float(
            np.sqrt(np.mean((part["y"].to_numpy() - own) ** 2))
        )
        pooled_rmse[str(name)] = float(
            np.sqrt(np.mean((part["y"].to_numpy() - pool) ** 2))
        )

    return {
        "pooled_slope": pooled_slope,
        "pooled_intercept": pooled_intercept,
        "per_group_fit": per_group,
        "pooled_rmse_by_group": pooled_rmse,
        "per_group_rmse_by_group": grouped_rmse,
        "pooled_worse_for_every_group": all(
            pooled_rmse[g] > grouped_rmse[g] for g in pooled_rmse
        ),
        "sign_flip": pooled_slope > 0
        and all(fit["slope"] < 0 for fit in per_group.values()),
    }


# ---------------------------------------------------------------------------
# 5. The fairness tension
# ---------------------------------------------------------------------------

#: A fully specified, integer-exact population. Each entry is
#: (group, score, count). Within every (group, score) cell exactly
#: ``score`` of the rows are positive, so the score is PERFECTLY calibrated
#: for both groups by construction -- no fitting, no randomness, no
#: approximation. The two groups differ only in where their mass sits, which
#: gives them different base rates: that difference is the whole engine of
#: the incompatibility.
FAIRNESS_CELLS: tuple[tuple[str, float, int], ...] = (
    ("A", 0.1, 50),
    ("A", 0.3, 100),
    ("A", 0.5, 200),
    ("A", 0.7, 300),
    ("A", 0.9, 350),
    ("B", 0.1, 350),
    ("B", 0.3, 300),
    ("B", 0.5, 200),
    ("B", 0.7, 100),
    ("B", 0.9, 50),
)


def fairness_population() -> pd.DataFrame:
    """The constructed population as a tidy frame of score cells.

    Columns: group, score, count, positives. ``positives`` is exactly
    ``score * count`` and every one of those products is a whole number, so
    nothing here is rounded.
    """
    rows = []
    for group, score, count in FAIRNESS_CELLS:
        positives = score * count
        assert abs(positives - round(positives)) < 1e-9, "cell must be integer-exact"
        rows.append(
            {
                "group": group,
                "score": score,
                "count": count,
                "positives": int(round(positives)),
            }
        )
    return pd.DataFrame(rows)


def base_rates(population: pd.DataFrame | None = None) -> dict[str, float]:
    """Fraction of each group that is actually positive."""
    pop = fairness_population() if population is None else population
    grouped = pop.groupby("group", observed=True)[["count", "positives"]].sum()
    return {
        str(g): float(row["positives"] / row["count"])
        for g, row in grouped.iterrows()
    }


def calibration_by_score_bin(population: pd.DataFrame | None = None) -> pd.DataFrame:
    """Observed positive rate in every (group, score) cell.

    Calibration means the score can be read as a probability: among rows
    scored 0.7, seven in ten really are positive, in EVERY group. This
    returns the observed rate so the claim can be checked rather than
    asserted.
    """
    pop = fairness_population() if population is None else population
    out = pop.copy()
    out["observed_rate"] = out["positives"] / out["count"]
    out["deviation"] = (out["observed_rate"] - out["score"]).abs()
    return out[["group", "score", "count", "observed_rate", "deviation"]]


def _select_from_top(part: pd.DataFrame, target: float, key: str) -> float:
    """Select ``target`` units of ``key`` from the highest scores downward.

    Returns the number of ROWS selected. When the target lands inside a score
    band, that band is taken proportionally -- the standard way to hit an
    exact rate when a whole band would overshoot. Returns a float because a
    proportional slice of a band generally is not a whole number of rows.
    """
    ordered = part.sort_values("score", ascending=False)
    remaining = target
    rows_selected = 0.0
    for _, band in ordered.iterrows():
        available = float(band[key])
        if available <= 0:
            continue
        if remaining >= available - 1e-9:
            rows_selected += float(band["count"])
            remaining -= available
        else:
            fraction = remaining / available
            rows_selected += fraction * float(band["count"])
            remaining = 0.0
        if remaining <= 1e-9:
            break
    return rows_selected


def _metrics_for_selection(part: pd.DataFrame, rows_selected: float) -> dict[str, float]:
    """Selection rate, true-positive rate and precision for one group.

    ``rows_selected`` is a count of rows taken from the top score band
    downward; the positives inside that selection are accumulated band by
    band, taking a proportional slice of whichever band the cut falls in.
    """
    ordered = part.sort_values("score", ascending=False)
    remaining = rows_selected
    positives_selected = 0.0
    for _, band in ordered.iterrows():
        count = float(band["count"])
        if remaining >= count - 1e-9:
            positives_selected += float(band["positives"])
            remaining -= count
        else:
            fraction = remaining / count if count else 0.0
            positives_selected += fraction * float(band["positives"])
            remaining = 0.0
        if remaining <= 1e-9:
            break

    total = float(part["count"].sum())
    total_positives = float(part["positives"].sum())
    return {
        "selection_rate": rows_selected / total,
        "true_positive_rate": positives_selected / total_positives,
        "precision": positives_selected / rows_selected if rows_selected else 0.0,
        "rows_selected": rows_selected,
        "positives_selected": positives_selected,
    }


def evaluate_policy(
    policy: str, population: pd.DataFrame | None = None
) -> dict[str, Any]:
    """Score one decision policy on all three fairness criteria at once.

    Policies:

    * ``"single_threshold"`` -- one cut at score >= 0.5 for everybody. This
      is the policy that leaves the calibrated score untouched.
    * ``"demographic_parity"`` -- give both groups the same selection rate,
      set to the rate the single threshold produces overall.
    * ``"equal_opportunity"`` -- give both groups the same true-positive
      rate, set to the rate that policy targets.

    Reported gaps are absolute differences between the two groups:
    ``parity_gap`` (selection rate), ``equal_opportunity_gap`` (true-positive
    rate) and ``precision_gap`` (precision among the selected, the
    calibration-of-the-decision criterion). None of the three is privileged
    here; all three are printed so the trade can be seen rather than
    argued about.
    """
    pop = fairness_population() if population is None else population
    groups = sorted(pop["group"].unique())
    parts = {g: pop[pop["group"] == g] for g in groups}

    if policy == "single_threshold":
        rows = {
            g: float(parts[g].loc[parts[g]["score"] >= 0.5, "count"].sum())
            for g in groups
        }
    elif policy == "demographic_parity":
        selected_at_threshold = sum(
            float(parts[g].loc[parts[g]["score"] >= 0.5, "count"].sum())
            for g in groups
        )
        total = float(pop["count"].sum())
        rate = selected_at_threshold / total
        rows = {g: rate * float(parts[g]["count"].sum()) for g in groups}
    elif policy == "equal_opportunity":
        target_tpr = 0.80
        rows = {
            g: _select_from_top(
                parts[g], target_tpr * float(parts[g]["positives"].sum()), "positives"
            )
            for g in groups
        }
    else:  # pragma: no cover - guarded by the caller
        raise ValueError(f"unknown policy: {policy!r}")

    per_group = {g: _metrics_for_selection(parts[g], rows[g]) for g in groups}
    a, b = groups[0], groups[1]
    return {
        "policy": policy,
        "per_group": per_group,
        "parity_gap": abs(
            per_group[a]["selection_rate"] - per_group[b]["selection_rate"]
        ),
        "equal_opportunity_gap": abs(
            per_group[a]["true_positive_rate"] - per_group[b]["true_positive_rate"]
        ),
        "precision_gap": abs(per_group[a]["precision"] - per_group[b]["precision"]),
    }


FAIRNESS_POLICIES = ("single_threshold", "demographic_parity", "equal_opportunity")


def fairness_incompatibility(tolerance: float = 1e-9) -> dict[str, Any]:
    """Evaluate every policy and report which criteria each one satisfies.

    Returns the three policies' gap triples plus ``any_policy_satisfies_all``,
    which is the claim this exercise exists to test. It is False here, and
    that is a consequence of the two groups having different base rates --
    not of the policies being badly chosen.
    """
    results = {p: evaluate_policy(p) for p in FAIRNESS_POLICIES}
    satisfied = {
        p: {
            "demographic_parity": r["parity_gap"] <= tolerance,
            "equal_opportunity": r["equal_opportunity_gap"] <= tolerance,
            "equal_precision": r["precision_gap"] <= tolerance,
        }
        for p, r in results.items()
    }
    return {
        "results": results,
        "satisfied": satisfied,
        "base_rates": base_rates(),
        "any_policy_satisfies_all": any(
            all(flags.values()) for flags in satisfied.values()
        ),
    }


# ---------------------------------------------------------------------------
# 6-7. Disclosure risk: uniqueness, generalisation, k-anonymity and its limit
# ---------------------------------------------------------------------------

QUASI_IDS = ("birth_year", "postcode", "sex")
GENERALISED_QUASI_IDS = ("birth_decade", "postcode", "sex")


def synthetic_register(n: int = 5_000, seed: int = 138) -> pd.DataFrame:
    """A synthetic register: no real person is represented here.

    Three quasi-identifiers -- birth year, postcode, sex -- plus one
    sensitive attribute, ``diagnosis``. Nothing in this table was collected;
    every value is drawn from a seeded generator, which is the point: the
    uniqueness counts below are properties of the shape of the table, not
    facts about anybody.
    """
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "birth_year": rng.integers(1940, 2006, size=n),
            "postcode": rng.integers(1000, 1060, size=n).astype(str),
            "sex": rng.choice(["F", "M"], size=n),
            "diagnosis": rng.choice(
                ["none", "asthma", "diabetes", "hypertension"],
                size=n,
                p=[0.55, 0.15, 0.15, 0.15],
            ),
        }
    )


def unique_row_count(frame: pd.DataFrame, quasi_ids: Iterable[str]) -> int:
    """Rows that are the ONLY row with their combination of quasi-identifiers.

    A unique row can be singled out by anyone who knows those few fields
    about a person, whether or not the table carries a name.
    """
    keys = list(quasi_ids)
    sizes = frame.groupby(keys, observed=True)[keys[0]].transform("size")
    return int((sizes == 1).sum())


def generalise_quasi_ids(frame: pd.DataFrame) -> pd.DataFrame:
    """Replace exact birth year with the decade it falls in.

    One field, coarsened one step. Nothing else changes -- so any drop in
    uniqueness is attributable to this single edit.
    """
    out = frame.copy()
    out["birth_decade"] = (out["birth_year"] // 10 * 10).astype("int64")
    return out


def k_anonymity_level(frame: pd.DataFrame, quasi_ids: Iterable[str]) -> int:
    """The size of the smallest equivalence class.

    A table is k-anonymous when every combination of quasi-identifiers that
    appears at all appears at least k times, so this minimum IS the k the
    table achieves.
    """
    keys = list(quasi_ids)
    return int(frame.groupby(keys, observed=True)[keys[0]].size().min())


def suppress_small_classes(
    frame: pd.DataFrame, quasi_ids: Iterable[str], k: int
) -> tuple[pd.DataFrame, int]:
    """Drop every row whose equivalence class is smaller than ``k``.

    Returns the surviving frame and the number of rows suppressed. This is
    what k-anonymity costs: it is bought with rows, and the rows it costs
    are exactly the unusual ones -- which is worth saying out loud, because
    the people in rare categories are frequently the people an analysis was
    supposed to be about.
    """
    keys = list(quasi_ids)
    sizes = frame.groupby(keys, observed=True)[keys[0]].transform("size")
    kept = frame[sizes >= k]
    return kept.reset_index(drop=True), int(len(frame) - len(kept))


#: A small, hand-built table where k-anonymity holds and still discloses.
#: Every equivalence class has four rows, so the table is 4-anonymous. The
#: class (1970, "1001", "F") has four rows that all carry the same
#: diagnosis, so knowing only that someone is a 1970s-born woman in postcode
#: 1001 and appears in this table reveals her diagnosis exactly. No
#: re-identification was needed; the anonymity held and the secret still
#: came out.
HOMOGENEOUS_TABLE_ROWS: tuple[dict[str, Any], ...] = tuple(
    [
        {"birth_decade": 1970, "postcode": "1001", "sex": "F", "diagnosis": "diabetes"}
    ]
    * 4
    + [
        {"birth_decade": 1970, "postcode": "1001", "sex": "M", "diagnosis": "none"},
        {"birth_decade": 1970, "postcode": "1001", "sex": "M", "diagnosis": "asthma"},
        {"birth_decade": 1970, "postcode": "1001", "sex": "M", "diagnosis": "none"},
        {
            "birth_decade": 1970,
            "postcode": "1001",
            "sex": "M",
            "diagnosis": "hypertension",
        },
        {"birth_decade": 1980, "postcode": "1002", "sex": "F", "diagnosis": "none"},
        {"birth_decade": 1980, "postcode": "1002", "sex": "F", "diagnosis": "asthma"},
        {"birth_decade": 1980, "postcode": "1002", "sex": "F", "diagnosis": "none"},
        {"birth_decade": 1980, "postcode": "1002", "sex": "F", "diagnosis": "diabetes"},
    ]
)


def homogeneous_table() -> pd.DataFrame:
    """The 4-anonymous table that still leaks, as a frame."""
    return pd.DataFrame(list(HOMOGENEOUS_TABLE_ROWS))


def homogeneous_classes(
    frame: pd.DataFrame, quasi_ids: Iterable[str], sensitive: str, k: int
) -> list[dict[str, Any]]:
    """Equivalence classes of size >= k whose sensitive values are all identical.

    These are the classes where k-anonymity is satisfied and the sensitive
    attribute is disclosed anyway. In the l-diversity vocabulary these are
    the classes with l = 1.
    """
    keys = list(quasi_ids)
    leaks: list[dict[str, Any]] = []
    for key, part in frame.groupby(keys, observed=True):
        values = set(part[sensitive])
        if len(part) >= k and len(values) == 1:
            leaks.append(
                {
                    "class": tuple(key) if isinstance(key, tuple) else (key,),
                    "size": int(len(part)),
                    "distinct_sensitive_values": len(values),
                    "disclosed_value": next(iter(values)),
                }
            )
    return sorted(leaks, key=lambda item: str(item["class"]))


# ---------------------------------------------------------------------------
# 8. A datasheet contract
# ---------------------------------------------------------------------------

#: The provenance fields a dataset must carry before anything is built on
#: it. Each one answers a question that cannot be recovered from the data
#: once it is lost: who made these decisions, when, for what, and about whom.
DATASHEET_REQUIRED_FIELDS: tuple[str, ...] = (
    "collector",
    "collection_period",
    "purpose",
    "population_definition",
    "sampling_frame",
    "inclusion_criteria",
    "exclusion_criteria",
    "known_gaps",
    "licence",
    "version",
    "changelog",
)


def check_datasheet(
    record: Mapping[str, Any], required: Sequence[str] = DATASHEET_REQUIRED_FIELDS
) -> dict[str, Any]:
    """Check a dataset's documentation against the required provenance fields.

    A field counts as missing when it is absent, ``None``, or an empty
    string or collection -- an empty ``known_gaps`` list is a real answer
    only if it is deliberate, so this contract requires it to be written
    down rather than left off. Returns the missing fields BY NAME, because
    "documentation incomplete" is not actionable and
    "no exclusion_criteria recorded" is.
    """
    missing = []
    for name in required:
        if name not in record:
            missing.append(name)
            continue
        value = record[name]
        if value is None:
            missing.append(name)
        elif isinstance(value, str) and not value.strip():
            missing.append(name)
        elif isinstance(value, (list, tuple, dict, set)) and len(value) == 0:
            missing.append(name)
    return {
        "complete": not missing,
        "missing": missing,
        "checked": list(required),
    }


# ---------------------------------------------------------------------------
# 9. Version drift
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DatasetVersion:
    """One released version of a dataset: the rows plus the datasheet."""

    version: str
    frame: pd.DataFrame
    datasheet: dict[str, Any] = field(default_factory=dict)


def build_versions(n: int = 2_000, seed: int = 138) -> tuple[DatasetVersion, DatasetVersion]:
    """Two releases of the same dataset, differing only in who is in it.

    The measured column is byte-for-byte identical between the two versions.
    What changed is the sampling frame: version 2 cut group B's quota from
    half the sample to a quarter. Because both groups' values are drawn from
    the same distribution, every summary statistic of ``value`` -- count,
    mean, standard deviation, quartiles, extremes -- is EXACTLY unchanged. A
    reader comparing ``describe()`` output between the two releases sees
    nothing at all.
    """
    rng = np.random.default_rng(seed)
    value = rng.normal(50.0, 10.0, size=n)

    labels_v1 = np.where(np.arange(n) % 2 == 0, "A", "B")
    labels_v2 = np.where(np.arange(n) % 4 == 3, "B", "A")

    common = {
        "collector": "Course fixture generator (synthetic)",
        "collection_period": "2026-01-01/2026-06-30",
        "purpose": "Teaching example for measuring composition drift",
        "population_definition": "Synthetic adults in groups A and B",
        "inclusion_criteria": ["synthetic record generated by this module"],
        "exclusion_criteria": ["none"],
        "licence": "CC0-1.0",
        "known_gaps": ["contains no real people by design"],
    }

    v1 = DatasetVersion(
        version="1.0.0",
        frame=pd.DataFrame({"group": labels_v1, "value": value}),
        datasheet={
            **common,
            "sampling_frame": "equal quota: 50% group A, 50% group B",
            "version": "1.0.0",
            "changelog": ["1.0.0 initial release"],
        },
    )
    v2 = DatasetVersion(
        version="2.0.0",
        frame=pd.DataFrame({"group": labels_v2, "value": value}),
        datasheet={
            **common,
            "sampling_frame": "revised quota: 75% group A, 25% group B",
            "version": "2.0.0",
            "changelog": [
                "1.0.0 initial release",
                "2.0.0 sampling frame re-scoped: group B quota reduced from 50% to 25%",
            ],
        },
    )
    return v1, v2


def summary_stats(frame: pd.DataFrame, column: str = "value") -> dict[str, float]:
    """The summary a reader would actually look at when comparing releases."""
    series = frame[column]
    return {
        "count": float(series.count()),
        "mean": float(series.mean()),
        "std": float(series.std()),
        "min": float(series.min()),
        "median": float(series.median()),
        "max": float(series.max()),
    }


def diff_versions(
    old: DatasetVersion,
    new: DatasetVersion,
    group_column: str = "group",
    value_column: str = "value",
    shift_threshold: float = 0.05,
) -> dict[str, Any]:
    """Compare two releases on summary statistics AND on composition.

    ``summary_identical`` is True when every summary statistic matches to
    within floating-point tolerance -- the case where a release-note-free
    upgrade looks like no change at all. ``composition_shift`` is the largest
    absolute change in any group's share. ``changelog_explains`` reports
    whether the new version's changelog gained an entry the old one did not
    have, which is the only part of this comparison that says WHY.
    """
    old_stats = summary_stats(old.frame, value_column)
    new_stats = summary_stats(new.frame, value_column)
    summary_identical = all(
        abs(old_stats[k] - new_stats[k]) < 1e-9 for k in old_stats
    )

    old_shares = old.frame[group_column].value_counts(normalize=True).to_dict()
    new_shares = new.frame[group_column].value_counts(normalize=True).to_dict()
    groups = sorted(set(old_shares) | set(new_shares))
    shifts = {
        g: float(new_shares.get(g, 0.0) - old_shares.get(g, 0.0)) for g in groups
    }
    composition_shift = max(abs(v) for v in shifts.values()) if shifts else 0.0

    old_log = list(old.datasheet.get("changelog", []))
    new_log = list(new.datasheet.get("changelog", []))
    new_entries = [entry for entry in new_log if entry not in old_log]

    return {
        "old_version": old.version,
        "new_version": new.version,
        "summary_old": old_stats,
        "summary_new": new_stats,
        "summary_identical": summary_identical,
        "group_shares_old": {g: float(old_shares.get(g, 0.0)) for g in groups},
        "group_shares_new": {g: float(new_shares.get(g, 0.0)) for g in groups},
        "group_share_shift": shifts,
        "composition_shift": float(composition_shift),
        "material_shift": composition_shift >= shift_threshold,
        "summary_hides_the_change": summary_identical
        and composition_shift >= shift_threshold,
        "changelog_new_entries": new_entries,
        "changelog_explains": bool(new_entries),
        "frame_changed": old.datasheet.get("sampling_frame")
        != new.datasheet.get("sampling_frame"),
    }
