# Day 128 lab brief — "Plots You Can Assert On"

Nine exercises. Write each function in `plotting.py`, then check yourself:

```bash
cd starter   # if you are not already there
../.venv/bin/pytest . -q
```

An unattempted function's test **skips** — that means "not written yet,"
not "wrong." A wrong answer **fails**, and prints both the value your code
produced and the value the test expected.

Everything in this lab runs headless (`matplotlib.use("Agg")`, already
done at the top of `plotting.py` — never add `plt.show()`) and writes
files only to a temporary directory that the tests clean up after
themselves. You do not need network access, `sudo`, or any file outside
this lab.

## The nine exercises

1. **The two APIs.** Write `draw_line_pyplot_style` using only `plt.*`
   calls, and `draw_line_object_style` using `fig, ax = plt.subplots()`
   then `ax.*` calls. Call each twice with different data and compare
   `plt.get_fignums()`: the pyplot version should put both lines on ONE
   figure; the object version should produce TWO figures, one line each.
2. **Data round-trip.** `make_line_axes(x, y)` should plot exactly what it
   is given — `ax.lines[0].get_xydata()` should equal the input arrays,
   not an approximation of them.
3. **Pixel arithmetic.** `png_dimensions(path)` reads a PNG's width and
   height from its file header — no imaging library needed, just 24 bytes
   and two big-endian integers. `save_at_size_and_dpi(fig, path, dpi)`
   saves without a tight bounding box, so `figsize * dpi` predicts the
   saved pixel dimensions exactly.
4. **Labels and limits.** `configure_axes(ax, xlabel, title, ylim=None)`
   sets a label and a title, and — when given — an explicit `ylim` that
   overrides whatever autoscaling would otherwise have chosen.
5. **Subplots.** `make_grid(nrows, ncols)` returns the Figure and the
   array of Axes from `plt.subplots(nrows, ncols)`, untouched. Each Axes
   in that array is independent: a label set on one must not appear on
   any other.
6. **Log scale and non-positive data.** `plot_with_log_yscale(x, y)`
   switches the y-axis to `'log'` and forces a draw. Data containing zero
   does not raise an error — it silently narrows the rendered range. Find
   out, by inspecting `ax.get_ylim()`, whether the zero point ends up
   inside or outside the visible range.
7. **Legends.** `plot_two_series_with_legend` plots two labelled series
   and calls `ax.legend()` once. The legend's text should match the two
   labels, in the order they were plotted.
8. **Figure lifecycle.** `open_figures_without_closing(n)` opens `n`
   figures and returns them without calling `plt.close()` on any of
   them — the leak is the point of this exercise, not a bug to fix here.
9. **Vector versus raster.** `save_png_and_svg(fig, png_path, svg_path)`
   saves the same figure as both formats. An SVG is markup — its axis
   label appears as searchable text in the file. A PNG is pixels — the
   same label does not appear as bytes anywhere in the file.

Read the docstring on each function in `plotting.py` before writing it —
it states the exact API calls and, where it matters, the exact strings
the tests check for.
