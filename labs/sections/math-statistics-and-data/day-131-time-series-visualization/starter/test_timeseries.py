"""Your exercises for Day 131 -- "Time Told Honestly".

Nine exercises, seventeen tests. Every test below currently calls
`pytest.skip(...)` -- replace the skip with real assertions and delete
the skip line. Read `00_brief.md` for the exercise-by-exercise
explanation, and `data.py` for what each builder function actually
returns.

Check yourself at any point:

    pytest starter -v

The reference answer key lives in `examples/test_timeseries.py` -- read
it AFTER you have tried, never before.
"""

import matplotlib
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import pytest

from data import ALIASING_SAMPLE_INTERVAL_DAYS, ALIASING_TRUE_PERIOD_DAYS, MISSING_DAY_POSITION

# --------------------------------------------------------------------------
# Exercise 1 -- index versus datetime axis.
# --------------------------------------------------------------------------


def test_1_index_axis_x_positions_are_perfectly_uniform(gapped_series):
    pytest.skip("Plot ax.plot(range(len(gapped_series)), ...); assert every x-step in get_xdata() is 1.0")


def test_1_datetime_axis_x_positions_reveal_the_gap(gapped_series):
    pytest.skip(
        "Plot ax.plot(gapped_series['date'], ...); convert get_xdata() with mdates.date2num; "
        "assert one step is 15.0 and the rest are 1.0"
    )


# --------------------------------------------------------------------------
# Exercise 2 -- resample aggregation changes the answer.
# --------------------------------------------------------------------------


def test_2_monthly_mean_sum_and_last_are_three_different_answers(daily_1to90):
    pytest.skip(
        "Resample daily_1to90 to 'MS' with .mean(), .sum() and .last(); assert January's three "
        "values are 16.0, 496.0 and 31.0, and that all three are distinct"
    )


# --------------------------------------------------------------------------
# Exercise 3 -- aliasing.
# --------------------------------------------------------------------------


def test_3_downsampling_below_the_true_frequency_manufactures_a_false_period(aliasing_signal):
    pytest.skip(
        "Downsample aliasing_signal[::ALIASING_SAMPLE_INTERVAL_DAYS]; find the smallest k>0 where "
        "the sampled sequence repeats; assert the spurious period (k * sample interval) is 20 days, "
        "not the true 4-day period"
    )


# --------------------------------------------------------------------------
# Exercise 4 -- trailing lag.
# --------------------------------------------------------------------------


def test_4_trailing_rolling_mean_peak_lags_the_true_peak(single_peak_series):
    pytest.skip(
        "Compute single_peak_series.rolling(30).mean(); compare its .idxmax() to "
        "single_peak_series.idxmax(); assert the trailing peak is 10-20 days LATE"
    )


def test_4_centred_rolling_mean_peak_does_not_lag(single_peak_series):
    pytest.skip(
        "Compute single_peak_series.rolling(30, center=True).mean(); assert its .idxmax() equals "
        "the true peak exactly (0-day offset)"
    )


# --------------------------------------------------------------------------
# Exercise 5 -- missing row versus NaN.
# --------------------------------------------------------------------------


def test_5_matplotlib_connects_across_a_missing_row_with_no_nan_present(series_with_a_missing_row, full_series):
    pytest.skip(
        "Plot series_with_a_missing_row; read get_ydata(); assert its length is one less than "
        "full_series and it contains no NaN anywhere"
    )


def test_5_matplotlib_breaks_the_line_at_an_explicit_nan(series_with_an_explicit_nan, full_series):
    pytest.skip(
        "Plot series_with_an_explicit_nan; assert get_ydata() has the same length as full_series "
        "and a real NaN at position MISSING_DAY_POSITION"
    )


def test_5_reindexing_the_missing_row_series_produces_the_explicit_nan_series(
    series_with_a_missing_row, series_with_an_explicit_nan, full_series
):
    pytest.skip(
        "Reindex series_with_a_missing_row to full_series.index; assert the result equals "
        "series_with_an_explicit_nan with pandas.testing.assert_series_equal"
    )


# --------------------------------------------------------------------------
# Exercise 6 -- log straightness.
# --------------------------------------------------------------------------


def test_6_constant_percentage_growth_is_collinear_in_log_space(pct_growth_series):
    pytest.skip(
        "Take np.log(pct_growth_series.values), then np.diff of that; assert the standard "
        "deviation of the differences is under 1e-9"
    )


def test_6_constant_linear_growth_is_not_collinear_in_log_space(linear_growth_series):
    pytest.skip(
        "Same as above but on linear_growth_series; assert the standard deviation of the "
        "log-differences is measurably larger (over 1e-3)"
    )


# --------------------------------------------------------------------------
# Exercise 7 -- year-over-year alignment.
# --------------------------------------------------------------------------


def test_7_month_day_alignment_keeps_dec_31_lined_up_across_a_leap_year(two_year_daily):
    pytest.skip(
        "Build a (month, day) key for both years' indexes, merge on it, and assert Dec 31 merges "
        "to one row with both years present, while Feb 29 merges to one row with only 2024 present"
    )


def test_7_raw_ordinal_day_of_year_misaligns_after_the_leap_day(two_year_daily):
    pytest.skip(
        "Read .dayofyear for Dec 31 in each year's index; assert 2024's is 366, 2025's is 365, "
        "and the two differ despite being the same calendar date"
    )


# --------------------------------------------------------------------------
# Exercise 8 -- small multiples.
# --------------------------------------------------------------------------


def test_8_faceting_produces_one_axes_per_series_with_exactly_one_line_each(many_series):
    pytest.skip(
        "Create one subplot per column of many_series, plot each column into its own Axes, and "
        "assert len(fig.axes) equals the column count with exactly one line in each Axes"
    )


# --------------------------------------------------------------------------
# Exercise 9 -- DST honesty.
# --------------------------------------------------------------------------


def test_9_spring_forward_day_has_23_hours(hourly_utc):
    pytest.skip(
        "Build an hourly series across 2024-03-06 to 2024-03-14 with the hourly_utc fixture, "
        "resample('D').size(), and assert 2024-03-10 has 23 rows"
    )


def test_9_fall_back_day_has_25_hours(hourly_utc):
    pytest.skip(
        "Same idea across 2024-10-30 to 2024-11-06; assert 2024-11-03 has 25 rows"
    )


def test_9_an_ordinary_day_outside_the_dst_boundary_has_24_hours(hourly_utc):
    pytest.skip("Using the same spring-forward range, assert an ordinary day (2024-03-08) has 24 rows")
