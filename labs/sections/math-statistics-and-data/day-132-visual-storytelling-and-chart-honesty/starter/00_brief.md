# Charts That Cannot Lie To You — the nine exercises

Fourteen functions in `honesty.py`, grouped into nine exercises. Each one
raises `NotImplementedError` until you write it. Check yourself from
inside `starter/`:

```bash
../.venv/bin/pytest . -q
```

A fresh checkout reports **22 skipped**. Every function you finish turns
skips into passes.

Everything that *draws* is already written for you — `bar_pair`,
`line_pair`, `dual_axis_figure`, `bubble_pair`, `annotated_bar_chart`,
`bar3d_projected_areas`, `histogram_counts`, and the data generators.
What you write is the **measurement**: the part that turns "this chart is
misleading" from an opinion into a number.

One rule runs through all nine: **measure the chart, not the inputs.**
Every function that reports what a reader sees must read it back out of
matplotlib's own artists. If you can compute the answer without touching
the figure, you have measured the wrong thing.

## Exercise 1 — the lie factor

Write `lie_factor(shown_ratio, data_ratio)` and `drawn_bar_heights(ax)`.

The lie factor is the size of the effect shown in the graphic divided by
the size of the effect in the data. `drawn_bar_heights` is what makes it
honest: it reads each bar's real bounding box and converts it to
axes-fraction units, clipped to the visible plotting box, so a bar whose
top is cut off contributes only what the reader can see.

Two bars, values `100` and `102`. On a zero baseline the drawn ratio is
`1.02` and the lie factor is `1.0`. On `ylim=(99, 103)` the drawn ratio
is `3.0` — one bar three times the height of the other — and the lie
factor is `2.94`. Same two numbers. One line of code between them.

## Exercise 2 — truncation for bars versus lines

Write `drawn_change(ax)`.

A bar encodes value as length from the baseline, so cutting the axis
breaks the encoding. A line encodes *change* as vertical displacement,
and a labelled linear axis converts that displacement back to the true
change whatever the baseline is. Your function does exactly what a
careful reader does: measure the displacement as a fraction of the
plotting box, then multiply by the labelled axis range.

The test runs it on three different `ylim` values and expects `2.0` every
time. That invariance is the nuance made measurable — and it is why "the
axis must start at zero" is right for bars and wrong for lines.

## Exercise 3 — dual axes

Write `pearson(a, b)`, `tracking_gap(trace_a, trace_b)` and
`widened_limits(values, factor)`.

This is the day's centrepiece, and the result is not the one most people
expect. Independently scaling two y-axes **cannot** change the Pearson
correlation of the two drawn traces — scaling is affine, and correlation
is invariant under affine transforms. Your test proves it: the drawn
correlation matches the data correlation to within `1e-12`.

What the scaling *does* control is how close the two curves sit, which is
what readers actually respond to. `tracking_gap` measures that as a
root-mean-square vertical distance in axes fractions. Widen both axes 20
times and two uncorrelated series lie on top of each other — and so does
a pair with `r = 0.91`. Same picture, opposite data. **Overlap is
evidence of nothing.**

## Exercise 4 — the cherry-picked window

Write `trend_slope(y)`.

One series, three windows, three true sentences: falling at 0.73 a week,
growing at 0.70 a week, and essentially unchanged. The test asserts the
sign flips between the halves while the full series is flat.

## Exercise 5 — binning

Write `count_modes(counts)`.

Count the strictly-local maxima in a set of drawn bar heights — how a
reader counts humps. Then run it on the same 400 values binned two ways.
Sturges' rule draws one hump; the Freedman-Diaconis rule draws two. Both
rules are citable. Only one supports the sentence you wanted to write.

## Exercise 6 — radius versus area

Write `drawn_area_ratio(ax)`.

matplotlib's `scatter` takes `s` as marker area in **points squared**, so
the correct encoding is the one that looks like it is doing less. Encode
by radius instead and the drawn area ratio becomes the square of the data
ratio — `16` for a data ratio of `4` — which makes the lie factor equal
to the data ratio itself. Get that statement the right way round; the
sloppy version is easy to invert.

## Exercise 7 — 3D perspective

Write `_polygon_area(points)` (the shoelace formula).

Two 3D bars, heights 1 and 2, every corner pushed through the Axes' own
projection matrix. Flat bars give exactly `2.000`. Under perspective the
drawn ratio is `2.34` with the taller bar at the far depth and `4.20`
with it at the near depth. Where a bar *stands* changes how big it looks,
which breaks the one comparison the chart exists to support.

## Exercise 8 — ordering, annotation, emphasis

Write `comparisons_to_find_max(values)`, `axes_text(ax)` and
`relative_luminance(colour)`.

The legitimate craft, made measurable. Sorted bars put the answer at a
known end. An annotated chart carries its claim as text you can retrieve
from the Axes. And emphasis has to survive losing colour: the classic
red/green pair differs by only `0.0996` in luminance — the one channel
every reader has — while one dark bar against pale ones reaches `0.5505`.

## Exercise 9 — the caption contract

Write `review_chart(ax, caption)`.

Four checks, returning `(passed, failures)`:

1. the caption states a claim a reader could disagree with
2. the y axis is labelled
3. a non-zero baseline is named in the caption
4. the baseline is zero, **or** its absence is disclosed

It must **pass** the honest chart, **fail** the truncated one, **pass** a
line on a non-zero baseline whose caption says so, and **fail** a
perfectly accurate chart that carries no claim and no label.

That third case is the point of the whole day. The contract does not
forbid breaking a rule. It forbids breaking it in silence.

Check 1 is a keyword heuristic, and the docstring says so. It catches a
*missing* claim; it cannot judge a *wrong* one. No automated check can,
and a review tool that pretended otherwise would be its own kind of lie.
