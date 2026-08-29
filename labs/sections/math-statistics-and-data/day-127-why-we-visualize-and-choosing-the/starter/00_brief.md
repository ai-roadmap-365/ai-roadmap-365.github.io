# Day 127 lab — the brief

Nine exercises, in order. Work top to bottom in `test_charts.py`. The
instruments live in four modules you read but do **not** edit:

- `encoding.py` — the square law (`encoded_area_ratio`), sRGB → CIELAB
  (`delta_e_cie76`), the deuteranopia transform
  (`simulate_deuteranopia`, `deuteranopia_collapse`), WCAG luminance, and
  Spearman's rho written out by hand because scipy is not installed here.
- `charts.py` — `ENCODING_RANKING` and `encoding_rank`, the two decision
  functions `best_encoding` and `choose_chart`, the three thresholds
  (`TABLE_MAX_VALUES`, `OVERPLOT_POINT_LIMIT`, `SMALL_MULTIPLE_LIMIT`),
  and `comparisons_to_find_max`.
- `palettes.py` — the swatches, taken from matplotlib's and seaborn's own
  defaults rather than hand-picked to prove a point.
- `render.py` — everything that draws (`render_circle`,
  `render_region_bar_chart`, `render_scatter`, `render_hexbin`) and
  everything that measures a drawing (`count_non_background_pixels`,
  `count_pixels_of_color`, `data_ink_ratio`,
  `count_distinct_luminance_levels`).

Read all four once before you start. Two fixtures come from
`conftest.py`: `points` (the seeded 10,000-point cloud) and `png_dir` (a
temporary directory outside the lab — every render goes there, and
nowhere else).

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

One rule about tolerances. Pure arithmetic (`encoded_area_ratio`, a rank
correlation, a comparison count) is exact — assert it exactly. Anything
measured off a rendered image is a rasteriser's opinion about where a
circle's edge falls, so give it a tolerance: `pytest.approx(4.0,
rel=0.02)` is honest, and an exact equality that happens to pass is luck
you should not depend on.

Nothing in this lab depends on timing. Never assert a duration.

---

## Exercise 1 — the square law, measured

Two values, 50 and 100. The second is exactly twice the first.

**1a, the arithmetic.** Call `encoding.encoded_area_ratio(VALUES,
mode="radius")` and again with `mode="area"`. The radius encoding gives a
circle twice as wide, which is a circle **four** times as large: assert
`4.0`, and assert it equals the data ratio *squared*. The area encoding
gives `2.0`. Assert the two encodings differ by a factor of exactly 2 —
that factor is the exaggeration a radius-scaled bubble chart applies to
every comparison in it, without misstating a single number.

**1b, the same claim off real pixels.** Render three circles into
`png_dir` with `render.render_circle`: radius 40, radius 80, and radius
`40 * sqrt(2)`. Measure each with `render.measure_circle_area_px`, which
counts painted pixels. Assert the 80-pixel circle covers about four times
the pixels of the 40-pixel one and the `40*sqrt(2)` one about twice, both
with `rel=0.02`. Report both counts in the test's own comments — the
measured numbers on the authoring machine are 5,156 and 20,368 pixels
against an ideal `pi*r^2` of 5,026.5 and 20,106.2, a couple of percent
out because a circle's edge does not land on pixel boundaries. The ratio
survives that intact, which is why the ratio is what the exercise asserts.

## Exercise 2 — the perceptual ranking as a decision function

Cleveland and McGill (1984) ran experiments asking people to judge
magnitudes from each visual channel and ranked the channels by measured
accuracy. `charts.ENCODING_RANKING` is that ranking.

**2a.** Use `charts.encoding_rank` to assert the ordering: position on a
common scale, then position on non-aligned scales, then length, then
angle and slope, then area, then volume, then colour saturation. Then
assert `encoding_rank("hue")` raises `ValueError`. Hue is not a bad
magnitude channel — it is not a magnitude channel at all, and the error
says so.

**2b.** Build a list of `((data_type, task), expected_channel)` cases and
assert `charts.best_encoding` returns each. Cover at least
`quantitative`/`compare`, `quantitative`/`compare_across_panels`,
`quantitative`/`magnitude_on_map`, `ordinal`/`encode_in_color`,
`nominal`/`identify_group` and `nominal`/`compare`. **Justify each
expected answer in a comment** — the justification is the exercise, not
the assertion. Finish with the load-bearing negative: assert
`best_encoding("ordinal", "encode_in_color")` is *not* `"hue"`, which
exercise 5 then measures the reason for.

**2c.** Assert `best_encoding` raises `ValueError` matching
`"unknown data type"` and `"unknown task"` respectively.

## Exercise 3 — from the question to the chart

`choose_chart(question_kind, n_categories, data_types)` takes the reader's
question and names an instrument.

**3a.** Build a case table covering all five question kinds, with at
least one case on each side of `TABLE_MAX_VALUES`,
`OVERPLOT_POINT_LIMIT` and `SMALL_MULTIPLE_LIMIT`, and assert every one.

**3b.** Collect the function's answers over every question kind and a
spread of sizes into a set, and assert that neither `"pie"` nor
`"donut"` is in it — anywhere, for anything. Then assert that for a
ranking question the answer is always `"sorted_horizontal_bar"`.

**3c.** Assert it raises for an unknown question kind, an unknown data
type, `n_categories=0`, and `change_over_time` with no temporal variable
in `data_types`. That last one matters: a function that guesses at a time
axis it was not given is worse than one that refuses.

## Exercise 4 — colour deficiency, simulated and measured

`encoding.simulate_deuteranopia` applies the Machado, Oliveira and
Fernandes (2009) severity-1.0 matrix in linear RGB.
`encoding.deuteranopia_collapse` returns the CIE76 distance before, the
distance after, and the fraction retained.

**4a.** Run it on `PAL.PASS_FAIL_RED` and `PAL.PASS_FAIL_GREEN` —
matplotlib's own `tab10` red and green, the two colours a pass/fail chart
gets by default. Assert the normal-vision distance is above 100, the
simulated distance is below `COLLAPSE_THRESHOLD` (10.0), and the retained
fraction is below 0.10. Report all three.

**4b.** Run it on `PAL.SAFE_BLUE` and `PAL.SAFE_ORANGE`, the first two
entries of seaborn's `colorblind` palette. Assert the simulated distance
stays above `SURVIVAL_THRESHOLD` and the retained fraction above 0.90,
and that the safe pair ends more than ten times further apart than the
red/green pair.

Write into your comments what this does and does not license. A
simulation approximates a deficiency; it does not reproduce anyone's
experience, it assumes one severity, and it cannot represent anomalous
trichromacy at all. A small simulated distance is strong evidence a
palette is risky. A large one is weak evidence it is fine.

## Exercise 5 — an ordered variable on a categorical palette

**5a.** Take `PAL.viridis_steps(5)`, compute
`encoding.relative_luminance` of each swatch, and assert the list comes
out already sorted. Then assert
`encoding.luminance_order_correlation(palette)` is approximately `1.0`.

**5b.** Do the same with `PAL.tab10_steps(5)`. Assert the luminance list
is *not* sorted and the rank correlation is far smaller in absolute
value. Report the number you measure. `tab10` is not defective — it is
doing exactly its job, which is to make neighbouring swatches look as
different as possible, and "different" has no direction. Putting an
ordered variable on it destroys order the data actually had.

## Exercise 6 — sorting is an encoding decision

Build a list of 20 unsorted values.
`charts.comparisons_to_find_max(values, presented_sorted=False)` models a
reader holding a running best and checking every remaining bar: 19
comparisons. With `presented_sorted=True` it is 1 — read the top row,
glance at the second to confirm the chart really is sorted, stop.

Assert both, and then assert the *answer* is identical either way:
`sorted(values, reverse=True)[0] == values[charts.index_of_max(values)]`.
Sorting moved nothing but the reader's effort, which is why skipping it
is expensive and doing it is free.

## Exercise 7 — the data-ink ratio

Render `render.render_region_bar_chart` into `png_dir` twice, once with
`decorated=True` and once with `decorated=False`. Same eight numbers,
same bars, same labels; the decorated version adds a tinted panel,
gridlines on both axes and a heavy box.

Count total ink with `render.count_non_background_pixels` and the data
fraction with `render.data_ink_ratio(path, render.BAR_RGB)` — the bars
are drawn in one flat colour nothing else uses, so that isolates the data
ink exactly. Assert the plain chart's ratio is higher and the gap is more
than 0.5. **Report both counts and both ratios.**

The point is not that gridlines are banned. It is that every mark claims
some of the reader's attention, and the ones that are not data should
have to justify themselves.

## Exercise 8 — overplotting

**8a.** Confirm with `render.points_inside_axes` that none of the 10,000
points is clipped — otherwise a low pixel count could just mean points
fell off the edge. Render with `alpha=1.0` and count painted pixels.
Assert the count is below 75% of `N_POINTS`: every missing pixel is a
point that landed where another point already was and changed nothing.

Then the sharper measurement: assert
`render.count_distinct_luminance_levels` of that image is exactly **2**.
Paper and ink. Whether a pixel carries one point or forty it is the same
black, so the density is not dimmed — it is absent.

**8b.** Render the same cloud three ways: `alpha=1.0`, `alpha=0.05`, and
`render.render_hexbin`. Count distinct luminance levels in each. Assert
the alpha version has more than the opaque one, and the hexbin more than
50. Finish by asserting
`charts.choose_chart("relationship", N_POINTS, ["quantitative"])` is
`"hexbin"` — the recommendation and the measurement are the same fact
seen twice.

## Exercise 9 — when a table beats a chart

Assert `choose_chart("comparison", 3, ...)` is `"table"` and
`choose_chart("comparison", 30, ...)` is `"sorted_horizontal_bar"`.
Assert the boundary sits exactly at `charts.TABLE_MAX_VALUES` by testing
that value and that value plus one.

Then write the comment that is the actual exercise: **why** the boundary
is where it is. A chart's advantage is that it converts comparison from
arithmetic into a perceptual judgement. With three numbers there was no
arithmetic to convert — the reader can simply read them, exactly, which a
bar length never lets them do. Past five values the set stops fitting in
the reader's head at once and the perceptual judgement starts to pay for
the precision it costs. Five is where this course draws the line; the
number is a judgement, and the point is that it is written down where you
can argue with it.
