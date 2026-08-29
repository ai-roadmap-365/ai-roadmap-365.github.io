# Day 130 lab — the brief

Nine exercises, one per test function, in order. Work top to bottom in
`test_distributions.py`. Every sample comes from a fixture defined in
`conftest.py` (`bimodal_sample`, `skewed_sample`, `positive_sample`,
`quartile_pair`, `quartile_targets`, `ecdf_sample`, `overplot_cloud`,
`quadratic_data`, `discrete_sample`) — read `data.py` once to see exactly
what each one contains and how it was built before you start.

Check yourself at any point:

```bash
.venv/bin/pytest starter -v
```

On an untouched checkout that prints `9 skipped`. A **skip** means "not
attempted". Replace a `pytest.skip(...)` line with real assertions and
delete it — when every skip is gone and the suite is green, you are
finished:

```bash
.venv/bin/pytest starter -q
echo $?
```

Assert on computed numbers and artist state, not on what a plot *looks*
like — a histogram's bin counts, a KDE line's y-values, a five-number
summary, the pixel positions matplotlib actually painted. No image
comparison anywhere in this lab.

A helper, `count_local_maxima`, is already defined at the top of
`test_distributions.py` in `examples/` — write your own copy (or an
equivalent) in `starter/test_distributions.py` for exercises 1, 3 and 5;
it counts how many bars (or curve points) are strictly taller than their
neighbour(s), which is the working definition of "how many modes does
this picture show" used throughout this lab.

## The nine exercises

1. **Bin width changes the story.** `bimodal_sample` is 500 points from
   two overlapping normal clusters. Histogram it at 5 bins and at 100
   bins; count local maxima at each. Assert the two counts differ, that 5
   bins gives exactly one hump, and that 100 bins gives more than 10
   (noise, not structure). Then use `numpy.histogram_bin_edges(...,
   bins='fd')` and assert it recovers exactly two modes.

2. **The three rules disagree.** `skewed_sample` is a right-skewed,
   strictly positive draw. Get bin counts from `'sturges'`, `'scott'` and
   `'fd'` via `numpy.histogram_bin_edges` and assert all three differ.

3. **KDE bandwidth.** Draw `sns.kdeplot(bimodal_sample, bw_adjust=1.0)`
   and `bw_adjust=3.0`; read each line's `y` data off `ax.lines[0]` and
   count local maxima (interior points only — a KDE line has no "edge
   bin"). Assert the default finds 2 modes and the over-smoothed one
   finds 1.

4. **The KDE boundary problem.** `positive_sample` is strictly positive
   (an exponential). Draw its default KDE, confirm the `x` grid seaborn
   chose extends below zero, and integrate the curve's mass on that
   negative side with `numpy.trapezoid`. Assert it is a real, non-trivial
   fraction of the total area (more than 3%), and report the number.

5. **The boxplot's blind spot — the centrepiece.** `quartile_pair` gives
   you `(bimodal, unimodal)`; `quartile_targets` gives you the five
   numbers both were built to hit. Compute each sample's five-number
   summary with `numpy.percentile(x, [0, 25, 50, 75, 100])`. Assert both
   summaries land within 0.3 of the targets (and therefore of each
   other). Then histogram both at 15 bins and assert the bimodal sample
   shows 2 modes while the unimodal sample shows 1 — a picture a boxplot
   of either one could never show you.

6. **ECDF is parameter-free.** `ecdf_sample` has an odd length on
   purpose. Draw `sns.ecdfplot`, read `x, y = ax.lines[0].get_data()`,
   and assert every sorted observation appears in `x` (the ECDF is
   literally a step at each data point). Find where `y` first reaches
   0.5 with `numpy.searchsorted` and assert that `x` value equals
   `numpy.median(ecdf_sample)` to within `1e-9`.

7. **Overplotting.** `overplot_cloud` is 20,000 normal points. Render a
   *small* scatter (`figsize=(3, 3), dpi=72`) and, instead of reading
   pixels off the image, transform the data coordinates to pixel space
   with `ax.transData.transform(...)`, round to integers, and count
   distinct `(x, y)` pixel pairs with a `set`. Assert that count is under
   half the point count. Then draw a `hexbin` of the same data and assert
   its densest bin holds more than 20 points, reporting the max.

8. **Correlation without shape.** `quadratic_data` is `x` symmetric
   around 0 with `y = x**2 + noise`. Compute Pearson correlation with
   pandas' `.corr()` and assert it is near zero. `scipy` is not installed
   here, so pandas' built-in `method='spearman'` will raise
   `ModuleNotFoundError` — compute Spearman yourself as the Pearson
   correlation of `.rank()`-ed columns instead, and assert that is *also*
   near zero (a symmetric parabola has no monotonic component either).
   Fit a quadratic with `numpy.polyfit(x, y, 2)`, compute R² by hand, and
   assert it is above 0.95 — the fit sees what neither coefficient did.

9. **Jitter is distortion.** `discrete_sample` is integers 1 through 5.
   Add `numpy.random.default_rng(...).uniform(-w, w, n)` to build a
   jittered copy for some jitter width `w`. Assert every jittered point
   differs from its true value by at most `w`, and that
   `discrete_sample` itself is completely unchanged (jitter is applied
   to a copy, never in place).

The reference answer key lives in `examples/test_distributions.py` — read
it AFTER you have tried, never before.
