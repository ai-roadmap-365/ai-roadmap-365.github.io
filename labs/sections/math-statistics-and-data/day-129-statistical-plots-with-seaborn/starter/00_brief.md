# Day 129 lab — the brief

Nine exercises, sixteen tests, in order. Work top to bottom in
`test_seaborn.py`. Every table comes from a fixture defined in
`conftest.py` (`team_scores`, `wide_revenue`, `long_revenue`) — read
`data.py` once to see exactly what each one contains before you start.

Check yourself at any point:

```bash
.venv/bin/pytest starter -v
```

On an untouched checkout that prints `16 skipped`. A **skip** means "not
attempted". Replace a `pytest.skip(...)` line with real assertions and
delete it — when every skip is gone and the suite is green, you are
finished:

```bash
.venv/bin/pytest starter -q
echo $?
```

Assert on returned objects and artist state, not on what a plot *looks*
like. seaborn draws with matplotlib underneath, so every fact this lab
cares about — a return type, a bar's height, an error bar's extent, how
many `Axes` a facet grid produced, which `rcParams` changed — is readable
straight off the objects seaborn hands back, with no image comparison
anywhere.

---

## Exercise 1 — return types (`team_scores`)

`sns.scatterplot(data=..., x=..., y=..., ax=ax)` draws into the `Axes`
you hand it and returns that same `Axes` — assert `result is ax`.
`sns.relplot(data=..., x=..., y=...)`, called with **no** `ax=`, creates
its own `Figure` and returns a `seaborn.axisgrid.FacetGrid` wrapping it.
Assert the return type of each, and that the `FacetGrid`'s `.figure` is a
real `matplotlib.figure.Figure` that its own `.ax` belongs to.

## Exercise 2 — the barplot trap (`team_scores`)

Draw `sns.barplot(data=team_scores, x="team", y="score", ax=ax)`. Read
each bar's height from `ax.patches` (`bar.get_height()`) and compare it
to `team_scores.groupby("team")["score"].mean()` — they must match
exactly. Then, for each team, assert that team's bar height is **not**
one of that team's own four raw scores. Separately: team A's mean is
*higher* than team B's, even though three of team B's four raw scores
beat every one of team A's — compute that comparison directly from the
raw values, not from the bar heights. Finally, draw
`sns.stripplot(data=team_scores, x="team", y="score", ax=ax)` and read
every point back out of `ax.collections[i].get_offsets()`; assert the
full set of y-values recovered equals the full set of raw scores — the
strip chart hides nothing the bar chart hid.

## Exercise 3 — bootstrap randomness (`team_scores`)

`sns.barplot`'s default error bar is a **bootstrapped** 95% confidence
interval — a random resampling procedure. Draw the same barplot **six**
times with no `seed=` argument, read each run's line extents from
`ax.lines`, and assert that not all six runs are identical (collect them
into a set and assert its length is more than 1). Six draws, not two —
with only four observations per group, a bootstrap resamples from a
small, discrete space, and any single pair of runs can coincidentally
land on the same extent by chance; six independent draws makes the claim
itself reliable to test. Then draw it twice more with the *same*
explicit `seed=` value both times and assert those two extents match
exactly. This is the day's sharpest measured fact: the same call, the
same data, different pictures — unless you pin the seed.

## Exercise 4 — `errorbar=` options (`team_scores`)

Compare `errorbar='sd'` (one standard deviation, a closed-form
statistic) against `errorbar=('ci', 95)` (a bootstrapped interval) on the
same data, same seed. Assert their extents differ. Then draw `'sd'` with
two *different* seed values and assert the extents are identical either
way — `'sd'` does not resample, so a seed cannot change it.

## Exercise 5 — long versus wide (`wide_revenue`, `long_revenue`)

`wide_revenue` has one row per region and a `q1`..`q4` column each.
Asking `sns.lineplot` for `x="quarter", y="revenue", hue="region"` on
that frame must raise `ValueError` — those column names do not exist in
wide form. Melt `wide_revenue` yourself with the Day 124 call
(`id_vars="region", var_name="quarter", value_name="revenue"`), compare
your result to the `long_revenue` fixture with
`pandas.testing.assert_frame_equal`, then draw the same `lineplot` call
against the long form and confirm it succeeds, with one legend entry per
region (`ax.get_legend_handles_labels()`).

## Exercise 6 — faceting (`long_revenue`)

Call `sns.catplot(data=long_revenue, x="quarter", y="revenue",
col="region", kind="bar")`. Assert the number of `Axes` in the returned
`FacetGrid` (`grid.axes.flat`) equals `long_revenue["region"].nunique()`.
Repeat with `col_wrap=3` and assert the *Axes count is unchanged* but the
grid's `(_nrow, _ncol)` shape is now `(2, 3)` instead of `(1, 5)`.

## Exercise 7 — the escape hatch (`team_scores`)

Draw a boxplot into an `ax` you own. Assert `ax.get_ylabel()` is
seaborn's own default (the column name, `"score"`). Then call
`ax.set_ylabel(...)` and `ax.set_ylim(...)` — the Day 128 object API,
used *after* seaborn has already drawn — and assert both stick.

## Exercise 8 — theme side effects

Capture `matplotlib.rcParams[key]` for a handful of keys (`axes.facecolor`,
`axes.grid`, `axes.edgecolor`, `grid.color`, `axes.axisbelow`,
`xtick.bottom`, `ytick.left`) before calling `sns.set_theme()`. Assert
every one of those keys changed. Then restore them with
`matplotlib.rcParams.update(before)` and assert the restored dictionary
equals the captured one exactly — proof that the side effect is real and
reversible.

## Exercise 9 — overlay (`team_scores`)

Draw a boxplot into an `ax`, then a stripplot into the *same* `ax`.
Assert `len(ax.patches) == 4` (the four boxes) both before and after the
stripplot call, and `len(ax.collections)` goes from `0` to `4` (one point
collection per team) once the stripplot is added. Sum every collection's
point count and assert it equals `len(team_scores)` — all sixteen raw
points are visible, on top of the aggregated boxes.
