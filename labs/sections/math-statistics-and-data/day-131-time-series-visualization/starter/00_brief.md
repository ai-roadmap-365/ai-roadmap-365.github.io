# Day 131 lab — the brief

Nine exercises, seventeen tests, in order. Work top to bottom in
`test_timeseries.py`. Every table or signal comes from a fixture defined
in `conftest.py`, itself built from `data.py` — read `data.py` once to
see exactly what each fixture contains before you start.

Check yourself at any point:

```bash
.venv/bin/pytest starter -v
```

On an untouched checkout that prints `17 skipped`. A **skip** means "not
attempted". Replace a `pytest.skip(...)` line with real assertions and
delete it — when every skip is gone and the suite is green, you are
finished:

```bash
.venv/bin/pytest starter -q
echo $?
```

Assert on x-positions, computed values and artist state, not on what a
plot *looks* like. Every fact this lab cares about — whether an axis is
evenly spaced, which number a resample produced, how far a rolling
window's peak drifted, whether a line contains a `NaN` — is readable
straight off the objects pandas and matplotlib hand back, with no image
comparison anywhere.

---

## Exercise 1 — index versus datetime axis (`gapped_series`)

`gapped_series` has two runs of daily dates with a real fourteen-day gap
between them (a sensor offline for two weeks). Plot `ax.plot(range(len(gapped_series)),
gapped_series["value"])` and read `ax.lines[0].get_xdata()` — every step
between consecutive x-values must be exactly `1.0`; the fourteen-day
outage is completely invisible on a plain row index. Then plot
`ax.plot(gapped_series["date"], gapped_series["value"])` instead, convert
the returned x-data with `matplotlib.dates.date2num`, and assert that
every step is `1.0` **except one**, which is `15.0` (fourteen missing
days plus the one-day step on either side of them) — the same data, the
same code except for one axis, and only the second one tells the truth
about when the gap happened.

## Exercise 2 — resampling is a claim (`daily_1to90`)

`daily_1to90` is ninety days (Jan 1 – Mar 30, 2024) with `value` equal to
the day number, so January's 31 raw values are `1, 2, ..., 31`. Resample
to `"MS"` with `.mean()`, `.sum()` and `.last()` and read January's value
from each — they must be `16.0`, `496.0` and `31.0` respectively, three
different, all-true numbers computed from the exact same 31 rows. Assert
all three are distinct, and cross-check each against
`daily_1to90.loc["2024-01"]` directly.

## Exercise 3 — aliasing (`aliasing_signal`)

`aliasing_signal` is a daily cosine with a genuine period of
`ALIASING_TRUE_PERIOD_DAYS` (4) days. Downsample it by taking every
`ALIASING_SAMPLE_INTERVAL_DAYS`-th (5th) value:
`aliasing_signal[::ALIASING_SAMPLE_INTERVAL_DAYS]`. Find the smallest
`k > 0` for which the sampled sequence repeats itself (shifting by `k`
and comparing with `numpy.allclose`) — that `k`, multiplied by the
5-day sampling interval, is the **spurious** period the downsampling
manufactured. Assert it comes out to 20 days: five times longer than the
true 4-day cycle, and present only because of how the signal was
sampled, not because of anything in the signal itself.

## Exercise 4 — trailing lag (`single_peak_series`)

`single_peak_series` is a single triangular bump peaking at a known,
exact day. Compute `single_peak_series.rolling(30).mean()` (the default,
**trailing** window) and compare its `.idxmax()` to the true peak's
`.idxmax()` — assert the trailing peak lands 10 to 20 days *after* the
real one (roughly half the 30-day window). Then compute
`single_peak_series.rolling(30, center=True).mean()` and assert **its**
peak lands exactly on the true one, offset zero.

## Exercise 5 — missing row versus NaN (`series_with_a_missing_row`,
`series_with_an_explicit_nan`, `full_series`)

`series_with_a_missing_row` has the day-10 row dropped entirely (19
rows, no `NaN` anywhere). Plot it and read `ax.lines[0].get_ydata()`:
assert its length is one less than `full_series` and it contains no
`NaN` — matplotlib drew a straight, uninterrupted line across the gap.
`series_with_an_explicit_nan` keeps all twenty rows but sets day 10's
value to `NaN`; plot it and assert the returned y-data has the *full*
twenty-row length with a real `NaN` at `MISSING_DAY_POSITION` — the same
missing observation, but now visible as a break. Finally, reindex
`series_with_a_missing_row` to `full_series.index` and assert the result
equals `series_with_an_explicit_nan` exactly
(`pandas.testing.assert_series_equal`) — reindexing is what converts an
invisible gap into an honest one.

## Exercise 6 — log straightness (`pct_growth_series`,
`linear_growth_series`)

`pct_growth_series` grows by a fixed 5% every period (true compounding);
`linear_growth_series` grows by a fixed 5 units every period. Take
`numpy.log` of each series' values, then `numpy.diff` of the logged
values. Assert the percentage-growth series' log-differences have a
standard deviation under `1e-9` (essentially a perfectly straight line
in log space) and the linear-growth series' log-differences have a
standard deviation over `1e-3` (measurably curved).

## Exercise 7 — year-over-year alignment (`two_year_daily`)

`two_year_daily` returns `(series_2024, series_2025)` — 2024 is a leap
year (366 days, including Feb 29), 2025 is not (365). Build a `(month,
day)` key from each index (ignoring the year) and merge the two on that
key. Assert Dec 31 merges to exactly one row with both years' values
present, and Feb 29 merges to exactly one row with **only** 2024's value
present (2025's side is `NaN`). Separately, read `.dayofyear` for Dec 31
in each year's own index directly and assert 2024's is `366` while
2025's is `365` — the same calendar date, two different ordinal numbers,
which is exactly why aligning by raw day-of-year (instead of by
calendar month/day) would silently misalign every date after Feb 29.

## Exercise 8 — small multiples (`many_series`)

`many_series` is a DataFrame with several distinct columns sharing one
date range. Create one subplot per column
(`plt.subplots(n_series, 1, ...)`), plot each column into its own `Axes`,
and assert `len(fig.axes)` equals the number of columns, with exactly
one `Line2D` in every one of those `Axes`.

## Exercise 9 — DST honesty (`hourly_utc`)

`hourly_utc(start, end)` builds hourly timestamps in UTC first, then
converts them to `"America/New_York"`, which observes Daylight Saving
Time — so no nonexistent or ambiguous local hour is ever constructed
directly. Build a range spanning 2024-03-10 (spring forward) and
resample to daily counts with `.resample("D").size()`: assert that day
has `23` hourly readings. Build a second range spanning 2024-11-03 (fall
back) and assert that day has `25`. For contrast, assert an ordinary day
inside the spring-forward range (2024-03-08) has the expected `24`.
