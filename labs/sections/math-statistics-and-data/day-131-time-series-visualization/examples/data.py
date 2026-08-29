"""The tables and signals every exercise in this lab is built from.

Nothing here is randomised or loaded from a file -- every table is a small,
deterministic construction so a reader can check every asserted number by
eye against the source. This lab's through-line is that time has structure
a plain axis throws away, so most of these builders return a real
`DatetimeIndex`, not a `RangeIndex` -- and where an exercise needs to
compare "index axis" against "datetime axis" behaviour, it builds both on
purpose.

`build_gapped_series()` -- exercise 1. Two contiguous stretches of daily
observations with a real fourteen-day gap between them (a sensor that was
offline), the exact shape a naive plot silently erases.

`build_daily_1to90()` -- exercise 2 and part of exercise 5. Ninety days of
`value = day number` (1..90), so every resample aggregate is hand-checkable
arithmetic: January's mean is 16.0, its sum is 496.0, its last value is
31.0.

`build_aliasing_signal()` -- exercise 3. A daily cosine with a *true*
period of 4 days, long enough (400 days) to sample repeatedly at any
interval.

`build_single_peak_series()` -- exercise 4. A 200-day triangular bump
centred exactly on day 100, base width 120 days, used to measure how far a
rolling mean's own peak drifts from the true one.

`build_series_with_a_missing_day()` -- exercise 5. Twenty daily values
with the day-10 row physically absent from the DataFrame (not present at
all, as opposed to present-with-NaN).

`build_pct_growth_series()` / `build_linear_growth_series()` -- exercise
6. Sixty periods of constant 5%-per-period compounding growth versus
sixty periods of constant 5-units-per-period linear growth.

`build_two_year_daily()` -- exercise 7. Full calendar years 2024 (a leap
year, 366 days) and 2025 (365 days), value = day-of-year-in-that-year, so
Feb 29's own row is trivially identifiable.

`build_many_series(n)` -- exercise 8. `n` short random-walk-free series
sharing one date range, each with a distinct deterministic offset, for
faceting into small multiples.

`build_hourly_utc(start, end)` -- exercise 9. Hourly, UTC-anchored
timestamps across a US Eastern DST boundary, built in UTC first and
converted afterward so no ambiguous or nonexistent local time is ever
constructed directly.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Exercise 1 -- the opening failure. Two runs of daily dates with a real
# fourteen-day gap between them: Jan 1 - Jan 31 (31 days), then a break,
# then Feb 15 - Feb 28 (14 days). 45 rows total. Plotted against a plain
# RangeIndex the gap is invisible; plotted against the parsed datetime it
# is a visible jump.
# --------------------------------------------------------------------------


def build_gapped_series() -> pd.DataFrame:
    first_run = pd.date_range("2024-01-01", periods=31, freq="D")
    second_run = pd.date_range("2024-02-15", periods=14, freq="D")
    dates = first_run.append(second_run)
    values = np.arange(len(dates), dtype=float)
    return pd.DataFrame({"date": dates, "value": values})


# --------------------------------------------------------------------------
# Exercise 2 -- resample aggregation changes the answer. Ninety days
# (Jan 1 - Mar 30, 2024), value equal to the day number (1..90), so every
# monthly aggregate is arithmetic anyone can re-check: January's 31 values
# are 1..31, mean 16.0, sum 496.0, last 31.0 -- three different, all true,
# numbers from the same 31 rows.
# --------------------------------------------------------------------------


def build_daily_1to90() -> pd.Series:
    dates = pd.date_range("2024-01-01", periods=90, freq="D")
    values = np.arange(1, len(dates) + 1, dtype=float)
    return pd.Series(values, index=dates, name="value")


# --------------------------------------------------------------------------
# Exercise 3 -- aliasing. A daily cosine with a TRUE period of 4 days,
# sampled every 5th day. 5 and 4 share no common factor smaller than
# themselves in a way that keeps the alias clean: the sampled sequence
# repeats every 4 SAMPLES (20 real days), a spurious period 5x longer than
# the signal that actually produced it, and nowhere close to either input
# number.
# --------------------------------------------------------------------------

ALIASING_TRUE_PERIOD_DAYS = 4
ALIASING_SAMPLE_INTERVAL_DAYS = 5


def build_aliasing_signal(n_days: int = 400) -> np.ndarray:
    t = np.arange(n_days, dtype=float)
    return np.cos(2 * np.pi * t / ALIASING_TRUE_PERIOD_DAYS)


# --------------------------------------------------------------------------
# Exercise 4 -- trailing lag. A single triangular bump over 200 days,
# peaking exactly at day-position 100 (base half-width 60 days either
# side), so a rolling window's own peak position can be measured against a
# known, exact answer.
# --------------------------------------------------------------------------

PEAK_POSITION_DAYS = 100
PEAK_HALF_WIDTH_DAYS = 60


def build_single_peak_series() -> pd.Series:
    idx = pd.date_range("2024-01-01", periods=200, freq="D")
    t = np.arange(len(idx))
    values = np.maximum(0, PEAK_HALF_WIDTH_DAYS - np.abs(t - PEAK_POSITION_DAYS)) / PEAK_HALF_WIDTH_DAYS
    return pd.Series(values, index=idx, name="value")


# --------------------------------------------------------------------------
# Exercise 5 -- missing row versus NaN. Twenty daily values, value = day
# position (0..19). `full` carries all twenty rows. `missing_row` is the
# same series with the day-10 row DROPPED entirely -- nineteen rows, no
# NaN anywhere -- as opposed to a series that keeps all twenty rows but
# sets day 10's value to NaN explicitly.
# --------------------------------------------------------------------------

MISSING_DAY_POSITION = 10


def build_full_series() -> pd.Series:
    idx = pd.date_range("2024-01-01", periods=20, freq="D")
    values = np.arange(len(idx), dtype=float)
    return pd.Series(values, index=idx, name="value")


def build_series_with_a_missing_row() -> pd.Series:
    full = build_full_series()
    return full.drop(full.index[MISSING_DAY_POSITION])


def build_series_with_an_explicit_nan() -> pd.Series:
    full = build_full_series().copy()
    full.iloc[MISSING_DAY_POSITION] = np.nan
    return full


# --------------------------------------------------------------------------
# Exercise 6 -- log straightness. Sixty periods of 5%-per-period
# compounding growth versus sixty periods of a fixed 5-units-per-period
# linear increase, both starting at 100.
# --------------------------------------------------------------------------


def build_pct_growth_series(periods: int = 60, rate: float = 0.05) -> pd.Series:
    idx = pd.date_range("2024-01-01", periods=periods, freq="D")
    t = np.arange(periods, dtype=float)
    values = 100.0 * (1.0 + rate) ** t
    return pd.Series(values, index=idx, name="value")


def build_linear_growth_series(periods: int = 60, step: float = 5.0) -> pd.Series:
    idx = pd.date_range("2024-01-01", periods=periods, freq="D")
    t = np.arange(periods, dtype=float)
    values = 100.0 + step * t
    return pd.Series(values, index=idx, name="value")


# --------------------------------------------------------------------------
# Exercise 7 -- year-over-year alignment. Full calendar years 2024 (a leap
# year -- 366 days, including Feb 29) and 2025 (365 days). Value equals
# the position within that year (0-based), so every value is trivially
# checkable, and the leap day's own row is easy to isolate.
# --------------------------------------------------------------------------


def build_two_year_daily() -> tuple[pd.Series, pd.Series]:
    dates_2024 = pd.date_range("2024-01-01", "2024-12-31", freq="D")
    dates_2025 = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    s2024 = pd.Series(np.arange(len(dates_2024), dtype=float), index=dates_2024, name="value")
    s2025 = pd.Series(np.arange(len(dates_2025), dtype=float), index=dates_2025, name="value")
    return s2024, s2025


# --------------------------------------------------------------------------
# Exercise 8 -- small multiples. `n` series over the same 60-day range,
# each a distinct deterministic sine with its own offset, so they are
# visibly different but reproducible.
# --------------------------------------------------------------------------


def build_many_series(n: int = 6, periods: int = 60) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=periods, freq="D")
    t = np.arange(periods, dtype=float)
    data = {f"series_{i}": 10 * (i + 1) + 3 * np.sin(2 * np.pi * t / (10 + i)) for i in range(n)}
    return pd.DataFrame(data, index=idx)


# --------------------------------------------------------------------------
# Exercise 9 -- DST honesty. Hourly timestamps built in UTC first (never
# constructing a local wall-clock time directly, so no nonexistent or
# ambiguous local hour is ever asked for), then converted to US/Eastern,
# which observes DST. Spring-forward (2024-03-10) loses an hour; fall-back
# (2024-11-03) repeats one.
# --------------------------------------------------------------------------


def build_hourly_utc(start: str, end: str) -> pd.Series:
    rng_utc = pd.date_range(start, end, freq="h", tz="UTC", inclusive="left")
    local = rng_utc.tz_convert("America/New_York")
    return pd.Series(1, index=local, name="reading")
