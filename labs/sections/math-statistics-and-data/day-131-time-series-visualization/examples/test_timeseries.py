"""The worked reference suite for Day 131 -- "Time Told Honestly".

Nine exercises, each proving one real pandas 3.0.5 / matplotlib 3.11.1
behaviour by building a real series, plotting or resampling it, and
reading real x-positions, artist state, or computed values -- never by
reading source. Run it:

    pytest examples

Every table and signal these tests use comes from `data.py`, imported
through the fixtures in `conftest.py`. Read `starter/00_brief.md` for the
exercise-by-exercise explanation; this file is the answer key.
"""

import matplotlib
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import pytest

from data import ALIASING_SAMPLE_INTERVAL_DAYS, ALIASING_TRUE_PERIOD_DAYS, MISSING_DAY_POSITION

# --------------------------------------------------------------------------
# Exercise 1 -- index versus datetime axis. Same data, same code except
# for the x argument. Against the RangeIndex the fourteen-day gap is
# invisible; against the parsed datetime it is a real, measurable jump.
# --------------------------------------------------------------------------


def test_1_index_axis_x_positions_are_perfectly_uniform(gapped_series):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot(range(len(gapped_series)), gapped_series["value"])
    xdata = np.asarray(ax.lines[0].get_xdata(), dtype=float)
    diffs = np.diff(xdata)
    # Every step is exactly 1 -- the outage is completely erased.
    assert set(np.unique(diffs)) == {1.0}


def test_1_datetime_axis_x_positions_reveal_the_gap(gapped_series):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot(gapped_series["date"], gapped_series["value"])
    xdata = mdates.date2num(ax.lines[0].get_xdata())
    diffs = np.diff(xdata)

    normal_steps = diffs[diffs < 5]
    gap_steps = diffs[diffs >= 5]
    assert set(np.round(normal_steps, 6)) == {1.0}  # every ordinary day is one apart
    assert len(gap_steps) == 1  # exactly one wide step
    assert gap_steps[0] == 15.0  # 14 missing days plus the 1-day step either side of them


# --------------------------------------------------------------------------
# Exercise 2 -- resampling is a claim. Ninety days of value = day number;
# January's mean, sum and last are three different, all-true numbers.
# --------------------------------------------------------------------------


def test_2_monthly_mean_sum_and_last_are_three_different_answers(daily_1to90):
    monthly_mean = daily_1to90.resample("MS").mean()
    monthly_sum = daily_1to90.resample("MS").sum()
    monthly_last = daily_1to90.resample("MS").last()

    january_mean = float(monthly_mean.iloc[0])
    january_sum = float(monthly_sum.iloc[0])
    january_last = float(monthly_last.iloc[0])

    assert (january_mean, january_sum, january_last) == (16.0, 496.0, 31.0)
    assert len({january_mean, january_sum, january_last}) == 3  # all distinct

    # Each is arithmetic anyone can re-check against January's 31 raw values (1..31).
    january_raw = daily_1to90.loc["2024-01"]
    assert january_raw.mean() == january_mean
    assert january_raw.sum() == january_sum
    assert january_raw.iloc[-1] == january_last


# --------------------------------------------------------------------------
# Exercise 3 -- aliasing. True period 4 days, sampled every 5th day.
# The sampled sequence repeats every 4 SAMPLES -- a spurious period of
# 20 real days, five times the true period, manufactured entirely by the
# sampling interval.
# --------------------------------------------------------------------------


def _first_repeat_period(sequence: np.ndarray, atol: float = 1e-9) -> int:
    for k in range(1, len(sequence) // 2):
        if np.allclose(sequence[:-k], sequence[k:], atol=atol):
            return k
    raise AssertionError("no repeating period found")


def test_3_downsampling_below_the_true_frequency_manufactures_a_false_period(aliasing_signal):
    sampled = aliasing_signal[:: ALIASING_SAMPLE_INTERVAL_DAYS]

    observed_period_in_samples = _first_repeat_period(sampled)
    observed_period_days = observed_period_in_samples * ALIASING_SAMPLE_INTERVAL_DAYS

    assert ALIASING_TRUE_PERIOD_DAYS == 4
    assert observed_period_days == 20  # the spurious period this sampling interval manufactures
    assert observed_period_days != ALIASING_TRUE_PERIOD_DAYS
    assert observed_period_days == 5 * ALIASING_TRUE_PERIOD_DAYS  # five times longer than the real cycle

    # The full-resolution signal itself genuinely repeats every 4 days --
    # the alias is entirely a product of the sampling interval, not the signal.
    full_res_period = _first_repeat_period(aliasing_signal)
    assert full_res_period == ALIASING_TRUE_PERIOD_DAYS


# --------------------------------------------------------------------------
# Exercise 4 -- trailing lag. A trailing rolling mean's own peak sits
# roughly half the window AFTER the true peak; a centred window's peak
# does not move at all.
# --------------------------------------------------------------------------


def test_4_trailing_rolling_mean_peak_lags_the_true_peak(single_peak_series):
    window = 30
    trailing = single_peak_series.rolling(window).mean()

    true_peak_date = single_peak_series.idxmax()
    trailing_peak_date = trailing.idxmax()
    offset_days = (trailing_peak_date - true_peak_date).days

    assert offset_days > 0  # the trailing peak is measurably LATE
    assert 10 <= offset_days <= 20  # roughly half the 30-day window (14, measured here)


def test_4_centred_rolling_mean_peak_does_not_lag(single_peak_series):
    window = 30
    centred = single_peak_series.rolling(window, center=True).mean()

    true_peak_date = single_peak_series.idxmax()
    centred_peak_date = centred.idxmax()
    offset_days = (centred_peak_date - true_peak_date).days

    assert offset_days == 0  # no lag at all -- unlike the trailing version above


# --------------------------------------------------------------------------
# Exercise 5 -- missing row versus NaN. matplotlib connects straight
# across an absent row (no NaN anywhere in the drawn data); it genuinely
# breaks at an explicit NaN. Reindexing converts the first case into the
# second.
# --------------------------------------------------------------------------


def test_5_matplotlib_connects_across_a_missing_row_with_no_nan_present(series_with_a_missing_row, full_series):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot(series_with_a_missing_row.index, series_with_a_missing_row.values)
    ydata = np.asarray(ax.lines[0].get_ydata(), dtype=float)

    assert len(ydata) == len(full_series) - 1  # the absent row is simply not there
    assert not np.isnan(ydata).any()  # nothing marks where the gap was


def test_5_matplotlib_breaks_the_line_at_an_explicit_nan(series_with_an_explicit_nan, full_series):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot(series_with_an_explicit_nan.index, series_with_an_explicit_nan.values)
    ydata = np.asarray(ax.lines[0].get_ydata(), dtype=float)

    assert len(ydata) == len(full_series)  # all twenty rows are still present
    assert np.isnan(ydata[MISSING_DAY_POSITION])  # the gap is visible AS a gap


def test_5_reindexing_the_missing_row_series_produces_the_explicit_nan_series(
    series_with_a_missing_row, series_with_an_explicit_nan, full_series
):
    reindexed = series_with_a_missing_row.reindex(full_series.index)
    pd.testing.assert_series_equal(reindexed, series_with_an_explicit_nan)
    assert pd.isna(reindexed.iloc[MISSING_DAY_POSITION])


# --------------------------------------------------------------------------
# Exercise 6 -- log straightness. Constant percentage growth is collinear
# in log space (its log-differences are constant); constant linear growth
# is not.
# --------------------------------------------------------------------------


def test_6_constant_percentage_growth_is_collinear_in_log_space(pct_growth_series):
    log_values = np.log(pct_growth_series.values)
    log_diffs = np.diff(log_values)
    assert log_diffs.std() < 1e-9  # essentially perfectly constant -- a straight line


def test_6_constant_linear_growth_is_not_collinear_in_log_space(linear_growth_series):
    log_values = np.log(linear_growth_series.values)
    log_diffs = np.diff(log_values)
    assert log_diffs.std() > 1e-3  # measurably curved, not a straight line


# --------------------------------------------------------------------------
# Exercise 7 -- year-over-year alignment. Aligning by calendar (month, day)
# keeps Dec 31 lined up with Dec 31 in both a leap and a non-leap year;
# aligning by raw ordinal day-of-year does not, because 2024 has 366 days
# and 2025 has 365.
# --------------------------------------------------------------------------


def test_7_month_day_alignment_keeps_dec_31_lined_up_across_a_leap_year(two_year_daily):
    s2024, s2025 = two_year_daily
    df2024 = s2024.to_frame("value")
    df2024["month_day"] = list(zip(df2024.index.month, df2024.index.day))
    df2025 = s2025.to_frame("value")
    df2025["month_day"] = list(zip(df2025.index.month, df2025.index.day))

    merged = pd.merge(df2024, df2025, on="month_day", suffixes=("_2024", "_2025"), how="outer")
    dec_31_row = merged.loc[merged["month_day"] == (12, 31)]

    assert len(dec_31_row) == 1  # Dec 31 exists in both years and merges to exactly one row
    assert not dec_31_row[["value_2024", "value_2025"]].isna().any().any()  # both sides present

    feb_29_row = merged.loc[merged["month_day"] == (2, 29)]
    assert len(feb_29_row) == 1
    assert not pd.isna(feb_29_row["value_2024"].iloc[0])  # 2024 has a Feb 29
    assert pd.isna(feb_29_row["value_2025"].iloc[0])  # 2025 does not


def test_7_raw_ordinal_day_of_year_misaligns_after_the_leap_day(two_year_daily):
    s2024, s2025 = two_year_daily
    dec_31_2024_ordinal = s2024.index[-1].dayofyear
    dec_31_2025_ordinal = s2025.index[-1].dayofyear

    assert dec_31_2024_ordinal == 366  # 2024 is a leap year
    assert dec_31_2025_ordinal == 365  # 2025 is not
    assert dec_31_2024_ordinal != dec_31_2025_ordinal  # same calendar date, different ordinal number


# --------------------------------------------------------------------------
# Exercise 8 -- small multiples. Faceting a many-series frame produces one
# Axes per series, each carrying exactly one line.
# --------------------------------------------------------------------------


def test_8_faceting_produces_one_axes_per_series_with_exactly_one_line_each(many_series):
    import matplotlib.pyplot as plt

    n_series = many_series.shape[1]
    fig, axes = plt.subplots(n_series, 1, sharex=True, figsize=(6, 2 * n_series))

    for ax, column in zip(axes, many_series.columns):
        ax.plot(many_series.index, many_series[column])

    assert len(fig.axes) == n_series
    for ax in fig.axes:
        assert len(ax.lines) == 1


# --------------------------------------------------------------------------
# Exercise 9 -- DST honesty. Hourly data resampled to daily calendar days
# across a US Eastern DST boundary produces one 23-hour day (spring
# forward) and one 25-hour day (fall back).
# --------------------------------------------------------------------------


def test_9_spring_forward_day_has_23_hours(hourly_utc):
    s = hourly_utc("2024-03-06", "2024-03-14")
    daily_counts = s.resample("D").size()
    assert int(daily_counts.loc["2024-03-10"]) == 23


def test_9_fall_back_day_has_25_hours(hourly_utc):
    s = hourly_utc("2024-10-30", "2024-11-06")
    daily_counts = s.resample("D").size()
    assert int(daily_counts.loc["2024-11-03"]) == 25


def test_9_an_ordinary_day_outside_the_dst_boundary_has_24_hours(hourly_utc):
    s = hourly_utc("2024-03-06", "2024-03-14")
    daily_counts = s.resample("D").size()
    assert int(daily_counts.loc["2024-03-08"]) == 24
