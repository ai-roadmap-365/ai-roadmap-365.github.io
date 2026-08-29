"""The twelve candidate figures, and the five that survive the filter.

This module is the *content* of the Day 133 report; `report.py` is the
machinery. Reading them together is the point of the day: exploration
produced twelve candidate figures, seven of them answer no stated
question, and `report.survivors` throws those seven out before they can
reach the reader. Their `dropped_because` lines survive, though, in the
report's "what we looked at and found nothing in" section -- because a
null result you keep to yourself is a null result the next person has to
rediscover.

Every number in every caption is computed from the frame that is passed
in. Nothing is a typed literal. Change the input and the sentences change
with it, which is what exercises 3 and 6 check.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.axes import Axes

from data import ANOMALY_MONTH, ANOMALY_REGION, PRICING_CHANGE_MONTH, REGIONS, source_description
from report import (
    SAFE_PALETTE,
    Candidate,
    Estimate,
    Finding,
    Report,
    bootstrap_interval,
    discarded,
    survivors,
)

#: The two six-month windows either side of the pricing change.
BEFORE_WINDOW = (7, 12)
AFTER_WINDOW = (13, 18)


def _direct(frame: pd.DataFrame) -> pd.DataFrame:
    """Direct-channel rows only -- the subset with no missing revenue."""
    return frame[frame["channel"] == "direct"]


def _window_mean(frame: pd.DataFrame, region: str, window: tuple[int, int]) -> float:
    rows = _direct(frame)
    low, high = window
    selected = rows[(rows["region"] == region) & rows["month"].between(low, high)]
    return float(selected["revenue"].mean())


def _window_values(frame: pd.DataFrame, region: str, window: tuple[int, int]) -> np.ndarray:
    rows = _direct(frame)
    low, high = window
    selected = rows[(rows["region"] == region) & rows["month"].between(low, high)]
    return selected["revenue"].to_numpy(dtype=float)


def _ratio_interval(
    before: np.ndarray, after: np.ndarray, *, resamples: int = 2000, seed: int = 133
) -> tuple[float, float]:
    """Percentile bootstrap for a percentage change between two small windows.

    Six observations on each side is not much, and the interval this returns
    is correspondingly wide. That width is information, not an embarrassment:
    it is the report telling the reader how hard the number should be leaned on.
    """
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(resamples):
        b = rng.choice(before, size=before.size, replace=True).mean()
        a = rng.choice(after, size=after.size, replace=True).mean()
        draws.append(100.0 * (a / b - 1.0))
    values = np.asarray(draws)
    return float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))


# ---------------------------------------------------------------------------
# Figure 1 -- data quality
# ---------------------------------------------------------------------------


def draw_missing_by_column(ax: Axes, frame: pd.DataFrame) -> None:
    counts = frame.isna().sum()
    ax.bar(list(counts.index), list(counts.to_numpy()), color=SAFE_PALETTE[0])
    ax.set_xlabel("column")
    ax.set_ylabel("rows with no value")
    ax.set_title("Missing values by column")


def analyse_missing(frame: pd.DataFrame) -> Finding:
    missing = frame["revenue"].isna()
    n_missing = int(missing.sum())
    pct = 100.0 * n_missing / len(frame)
    partner_share = 100.0 * float((frame.loc[missing, "channel"] == "partner").mean())
    indicator = missing.to_numpy(dtype=float)
    low, high = bootstrap_interval(indicator, statistic=lambda a: 100.0 * a.mean())
    return Finding(
        caption=(
            f"{n_missing} of {len(frame)} rows ({pct:.1f}%) have no revenue, and "
            f"{partner_share:.0f}% of those gaps are partner rows -- the missingness "
            "is a channel problem, not random loss"
        ),
        prose=(
            "Every other column is complete. Because the gaps sit entirely in one "
            "channel, any figure that pools the two channels and drops missing rows "
            "silently under-counts partner activity, so the rest of this report uses "
            "direct-channel rows wherever a level is being compared."
        ),
        estimate=Estimate(
            label="share of rows with missing revenue",
            value=pct,
            unit="%",
            low=low,
            high=high,
        ),
    )


# ---------------------------------------------------------------------------
# Figure 2 -- univariate
# ---------------------------------------------------------------------------


def draw_channel_populations(ax: Axes, frame: pd.DataFrame) -> None:
    direct = frame.loc[frame["channel"] == "direct", "revenue"].dropna()
    partner = frame.loc[frame["channel"] == "partner", "revenue"].dropna()
    bins = np.histogram_bin_edges(frame["revenue"].dropna(), bins="fd")
    ax.hist(direct, bins=bins, color=SAFE_PALETTE[0], alpha=0.75, label="direct")
    ax.hist(partner, bins=bins, color=SAFE_PALETTE[1], alpha=0.75, label="partner")
    ax.set_xlabel("monthly revenue for one region and channel")
    ax.set_ylabel("number of region-months")
    ax.set_title("Revenue is a mixture of two channels")
    ax.legend()


def analyse_populations(frame: pd.DataFrame) -> Finding:
    direct = frame.loc[frame["channel"] == "direct", "revenue"].dropna().to_numpy(float)
    partner = frame.loc[frame["channel"] == "partner", "revenue"].dropna().to_numpy(float)
    ratio = 100.0 * float(np.median(partner)) / float(np.median(direct))
    low, high = bootstrap_interval(partner, statistic=np.median)
    return Finding(
        caption=(
            f"Revenue is two populations rather than one: the median partner "
            f"region-month is {ratio:.0f}% of the median direct region-month, so any "
            "average taken across both channels describes a mixture nobody sells into"
        ),
        prose=(
            "The two histograms barely overlap. A single mean over this column would "
            "land in the empty gap between them and describe no real region-month at "
            "all -- Day 116's warning about a summary that discards the thing you "
            "needed, met again in a column you would have been tempted to average."
        ),
        estimate=Estimate(
            label="median partner region-month revenue",
            value=float(np.median(partner)),
            unit=" USD",
            low=low,
            high=high,
            decimals=0,
        ),
    )


# ---------------------------------------------------------------------------
# Figure 3 -- relationship
# ---------------------------------------------------------------------------


def draw_orders_vs_revenue(ax: Axes, frame: pd.DataFrame) -> None:
    rows = frame.dropna(subset=["revenue"])
    x = rows["orders"].to_numpy(dtype=float)
    y = rows["revenue"].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    grid = np.linspace(x.min(), x.max(), 50)
    ax.scatter(x, y, s=12, color=SAFE_PALETTE[0], label="region-month")
    ax.plot(grid, slope * grid + intercept, color=SAFE_PALETTE[3], label="least-squares fit")
    ax.set_xlabel("orders in the month")
    ax.set_ylabel("revenue in the month (USD)")
    ax.set_title("Orders and revenue")
    ax.legend()


def analyse_relationship(frame: pd.DataFrame) -> Finding:
    rows = frame.dropna(subset=["revenue"])
    x = rows["orders"].to_numpy(dtype=float)
    y = rows["revenue"].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    predicted = slope * x + intercept
    r_squared = 1.0 - float(np.sum((y - predicted) ** 2) / np.sum((y - y.mean()) ** 2))
    per_order = y / x
    low, high = bootstrap_interval(per_order)
    return Finding(
        caption=(
            f"Revenue rises about {slope:.0f} USD per additional order and the "
            f"straight-line fit accounts for {100.0 * r_squared:.1f}% of the variation, "
            "so a region-month that missed its revenue missed its order count"
        ),
        prose=(
            "There is no second cluster off the line and no curvature worth naming. "
            "That is a boring finding, and it is in the report precisely because it "
            "closes a question the reader would otherwise have to ask: revenue here "
            "is not being moved by price. The fitted slope "
            f"({slope:.0f} USD) sits a little below the mean revenue per order "
            f"({per_order.mean():.0f} USD) because the fit carries a non-zero "
            f"intercept of {intercept:,.0f} USD; the two numbers answer slightly "
            "different questions and the report says which is which rather than "
            "quoting whichever is larger."
        ),
        estimate=Estimate(
            label="mean revenue per order",
            value=float(per_order.mean()),
            unit=" USD",
            low=low,
            high=high,
        ),
    )


# ---------------------------------------------------------------------------
# Figure 4 -- segments
# ---------------------------------------------------------------------------


def draw_region_trend(ax: Axes, frame: pd.DataFrame) -> None:
    rows = _direct(frame)
    for index, region in enumerate(REGIONS):
        series = rows[rows["region"] == region].sort_values("month")
        ax.plot(
            series["month"].to_numpy(),
            series["revenue"].to_numpy(),
            color=SAFE_PALETTE[index],
            label=region,
        )
    ax.axvline(
        PRICING_CHANGE_MONTH - 0.5,
        color=SAFE_PALETTE[7],
        linestyle="--",
        label=f"pricing change (month {PRICING_CHANGE_MONTH})",
    )
    ax.set_xlabel("month")
    ax.set_ylabel("direct-channel revenue (USD)")
    ax.set_title("Direct revenue by region")
    ax.legend(fontsize=7, ncols=2)


def analyse_segments(frame: pd.DataFrame) -> Finding:
    changes: dict[str, float] = {}
    for region in REGIONS:
        before = _window_mean(frame, region, BEFORE_WINDOW)
        after = _window_mean(frame, region, AFTER_WINDOW)
        changes[region] = 100.0 * (after / before - 1.0)

    west = changes["West"]
    grew = [region for region, change in changes.items() if change > 0]
    low, high = _ratio_interval(
        _window_values(frame, "West", BEFORE_WINDOW),
        _window_values(frame, "West", AFTER_WINDOW),
    )

    # The East's after-window contains the single month-18 spike. Recompute it
    # without that one observation, because quoting the inflated figure without
    # saying so would be exactly the failure Day 132 named.
    clean_after = _direct(frame)
    clean_after = clean_after[
        (clean_after["region"] == ANOMALY_REGION)
        & clean_after["month"].between(*AFTER_WINDOW)
        & (clean_after["month"] != ANOMALY_MONTH)
    ]
    east_without_anomaly = 100.0 * (
        float(clean_after["revenue"].mean()) / _window_mean(frame, ANOMALY_REGION, BEFORE_WINDOW)
        - 1.0
    )
    direction = "fell" if west < 0 else "rose"
    return Finding(
        caption=(
            f"{len(grew)} regions grew across the pricing change while the West "
            f"{direction} {abs(west):.1f}%, and the break lands in month "
            f"{PRICING_CHANGE_MONTH} in that region only"
        ),
        prose=(
            "Comparing the six months before month "
            f"{PRICING_CHANGE_MONTH} with the six months after, the four regions move "
            + ", ".join(f"{region} {change:+.1f}%" for region, change in changes.items())
            + ". The West is the only one that changes direction, and it changes it at "
            "the month the price moved. This is an association in observational data, "
            "not a controlled comparison: nothing here rules out a third cause that "
            f"happened to the West in the same month. {ANOMALY_REGION}'s "
            f"{changes[ANOMALY_REGION]:+.1f}% is not what it looks like either: drop the "
            f"single month-{ANOMALY_MONTH} observation and it falls to "
            f"{east_without_anomaly:+.1f}%, which is why Figure 5 exists."
        ),
        estimate=Estimate(
            label="West change across the pricing change (six months either side)",
            value=west,
            unit="%",
            low=low,
            high=high,
        ),
    )


# ---------------------------------------------------------------------------
# Figure 5 -- anomaly
# ---------------------------------------------------------------------------


def draw_east_anomaly(ax: Axes, frame: pd.DataFrame) -> None:
    rows = _direct(frame)
    series = rows[rows["region"] == ANOMALY_REGION].sort_values("month")
    months = series["month"].to_numpy()
    colours = [
        SAFE_PALETTE[3] if month == ANOMALY_MONTH else SAFE_PALETTE[0] for month in months
    ]
    ax.bar(months, series["revenue"].to_numpy(), color=colours)
    ax.set_xlabel("month")
    ax.set_ylabel("direct-channel revenue (USD)")
    ax.set_title(f"{ANOMALY_REGION}: one month is not like the others")


def analyse_anomaly(frame: pd.DataFrame) -> Finding:
    rows = _direct(frame)
    series = rows[rows["region"] == ANOMALY_REGION]
    spike = float(series.loc[series["month"] == ANOMALY_MONTH, "revenue"].iloc[0])
    others = series.loc[series["month"] != ANOMALY_MONTH, "revenue"].to_numpy(float)
    multiple = spike / float(np.median(others))
    neighbours = series[series["month"].isin([ANOMALY_MONTH - 1, ANOMALY_MONTH + 1])]
    neighbour_multiple = float(neighbours["revenue"].mean()) / float(np.median(others))
    return Finding(
        caption=(
            f"{ANOMALY_REGION} month {ANOMALY_MONTH} is {multiple:.1f} times the "
            f"region's median month while the months either side sit at "
            f"{neighbour_multiple:.2f} times it, so this is one observation and not a "
            "level change"
        ),
        prose=(
            "The distinction matters for what you do next. A level change is a fact "
            "about the business and belongs in the forecast; a single spike is a fact "
            "about one month and belongs with whoever can explain it. Until someone "
            "does, the honest move is to report both the figure including it and the "
            "figure excluding it, and to say which one the decision was made on."
        ),
        estimate=Estimate(
            label=f"{ANOMALY_REGION} month {ANOMALY_MONTH} as a multiple of the region median",
            value=multiple,
            unit="x",
            no_interval_note=(
                "a single observation has no sampling interval; one point is one point"
            ),
        ),
    )


# ---------------------------------------------------------------------------
# The twelve candidates
# ---------------------------------------------------------------------------


def candidate_figures() -> list[Candidate]:
    """Everything exploration produced, in the order it was produced.

    Five carry a question. Seven do not, and `report.survivors` drops them.
    """
    return [
        Candidate(
            slug="missing-revenue",
            question="Which rows have no revenue, and is the missingness concentrated anywhere?",
            draw=draw_missing_by_column,
            analyse=analyse_missing,
        ),
        Candidate(
            slug="cumulative-revenue",
            dropped_because=(
                "A cumulative revenue curve was drawn and discarded: a cumulative "
                "series rises whatever the underlying months do, so it answered no "
                "question the monthly series had not already answered"
            ),
        ),
        Candidate(
            slug="channel-populations",
            question="Is monthly revenue one population, or several stacked on top of each other?",
            draw=draw_channel_populations,
            analyse=analyse_populations,
        ),
        Candidate(
            slug="orders-histogram",
            dropped_because=(
                "The order-count distribution was checked for a second population; it "
                "shows the same channel split the revenue column already shows, so it "
                "adds no evidence of its own"
            ),
        ),
        Candidate(
            slug="orders-vs-revenue",
            question="How tightly do orders and revenue move together, and what is one extra order worth?",
            draw=draw_orders_vs_revenue,
            analyse=analyse_relationship,
        ),
        Candidate(
            slug="region-channel-interaction",
            dropped_because=(
                "Region-by-channel interaction was checked; the partner channel runs "
                "at the same share of direct in all four regions, so there is no "
                "interaction to report"
            ),
        ),
        Candidate(
            slug="region-trend",
            question="Did any region's trajectory change at the month-13 pricing change?",
            draw=draw_region_trend,
            analyse=analyse_segments,
        ),
        Candidate(
            slug="revenue-per-order-by-region",
            dropped_because=(
                "Revenue per order was compared across the four regions; they are "
                "indistinguishable on this measure, which is worth one line here so "
                "the next reader does not spend an afternoon on it"
            ),
        ),
        Candidate(
            slug="east-anomaly",
            question="Is the East's month-18 jump a level change or a single outlier?",
            draw=draw_east_anomaly,
            analyse=analyse_anomaly,
        ),
        Candidate(
            slug="calendar-seasonality",
            dropped_because=(
                "Calendar seasonality was checked by lining the two years up month "
                "against month; nothing stood out above the month-to-month noise"
            ),
        ),
        Candidate(
            slug="missing-by-month",
            dropped_because=(
                "The missing revenue rows were checked for a time pattern as well as "
                "a channel pattern; they are scattered across the two years rather "
                "than clustered in any single month"
            ),
        ),
        Candidate(
            slug="revenue-heatmap",
            dropped_because=(
                "A region-by-month heatmap was drawn and discarded: it held the same "
                "information as the trend lines while making the month-13 break "
                "harder to see, which is the wrong trade for a report"
            ),
        ),
    ]


def build_report(frame: pd.DataFrame) -> Report:
    """Run the whole pipeline: candidates, filter, panels, ready to render."""
    candidates = candidate_figures()
    report = Report(
        title="Where did the West's revenue go?",
        question=(
            "Four regions sell through two channels. Did any region's revenue "
            "trajectory change around the month-13 pricing change, and is the change "
            "big enough and clean enough to act on?"
        ),
        decision=(
            "Whether to roll the month-13 pricing change back in the West before it "
            "is extended to the other three regions."
        ),
        provenance=source_description(),
        caveats=[
            "This is observational data, not an experiment. The month-13 break is an "
            "association in time; it is not proof that the pricing change caused it.",
            "The regional comparison uses six months either side of the change. Six "
            "observations per side is a small window, and the interval on that number "
            "is correspondingly wide -- read the interval, not the point estimate.",
            "Level comparisons use direct-channel rows only, because the partner "
            "channel is the one with missing revenue. Partner totals in this report "
            "are therefore lower bounds.",
            "Every figure here uses a colourblind-safe palette and labelled axes, and "
            "no axis in this report is truncated below zero.",
        ],
        null_results=[candidate.dropped_because for candidate in discarded(candidates)],
    )
    for candidate in survivors(candidates):
        report.add_panel(candidate, frame)
    return report


# ---------------------------------------------------------------------------
# Two deliberately broken specimens, used by the exercises
# ---------------------------------------------------------------------------


def draw_inaccessible(ax: Axes, frame: pd.DataFrame) -> None:
    """A chart that breaks the accessibility contract in three ways at once.

    Red against green is the classic pair that vanishes for the commonest
    form of colour vision deficiency, and neither axis is labelled. Exercise 9
    asserts that the build check catches all of it.
    """
    rows = _direct(frame)
    for region, colour in zip(REGIONS[:2], ("red", "green")):
        series = rows[rows["region"] == region].sort_values("month")
        ax.plot(series["month"].to_numpy(), series["revenue"].to_numpy(), color=colour)


def bare_point_estimate_candidate() -> Candidate:
    """A candidate whose finding reports a number with no uncertainty at all."""

    def analyse(frame: pd.DataFrame) -> Finding:
        total = float(frame["revenue"].sum())
        return Finding(
            caption=f"Total recorded revenue across the two years is {total:,.0f} USD",
            prose="A number with nothing attached to say how firm it is.",
            estimate=Estimate(label="total recorded revenue", value=total, unit=" USD", decimals=0),
        )

    return Candidate(
        slug="bare-total",
        question="What is the total recorded revenue?",
        draw=draw_missing_by_column,
        analyse=analyse,
    )
