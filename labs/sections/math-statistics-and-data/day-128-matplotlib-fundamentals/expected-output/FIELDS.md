# What may legitimately differ on your machine

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-20: Python 3.14.0, matplotlib 3.11.1, numpy 2.5.2,
pytest 9.1.1, macOS 26.5.2 (Apple Silicon, arm64), through a lab-local
`.venv` created by the documented setup commands.

## Exact and identical everywhere

- **Pixel dimensions** (`03-pixel-arithmetic.txt`): `(600, 400)` at
  `figsize=(6, 4)`, `dpi=100`; `(1200, 800)` at `dpi=200`; `(300, 200)` at
  `dpi=50`. This is exact integer arithmetic — `figsize[i] * dpi`, rounded
  by matplotlib's own rasteriser the same way on every platform — not a
  measurement with any sampling noise in it.
- **The data round-trip** (`02-data-round-trip.txt`): the stored x and y
  arrays are byte-for-byte the input arrays. No floating-point
  recomputation happens between `ax.plot()` and `get_xydata()`.
- **Figure counts** (`01-the-two-apis.txt`, `08-figure-leak.txt`):
  `plt.get_fignums()` lengths (1, 2, 5, 22, 0) are exact integers, not
  measurements.
- **Legend text and order** (`07-legends.txt`): `['measured', 'predicted']`
  is a direct readback of what was passed as `label=`, not a computed
  value.
- **Subplot grid shape** (`05-subplots.txt`): `(2, 3)` and the per-cell
  label/title dictionaries are exact structural facts about what
  `plt.subplots(2, 3)` returns.
- **SVG-contains-text / PNG-does-not** (`09-vector-versus-raster.txt`):
  the boolean outcomes (`True` / `False`) are guaranteed by the file
  formats themselves — SVG is XML markup, PNG is a raster format with no
  text layer — on any correctly functioning matplotlib install.

## Version-specific — will differ across matplotlib versions

- **The exact log-scale y-limits** in `06-log-scale-drops-nonpositive.txt`
  (`(0.8706, 18.3792)`) come from matplotlib's internal margin-and-locator
  logic for log axes, which has changed between major versions in the
  past. The property that matters — the lower limit is strictly greater
  than zero, so the zero-valued point falls outside the rendered range —
  is what the lab's tests assert, not the specific numbers.
- **The exact byte sizes** in `09-vector-versus-raster.txt` (SVG character
  count, PNG byte count) depend on matplotlib's SVG/PNG serialisation,
  which has changed across versions (metadata blocks, compression
  settings). The lab's tests assert presence/absence of the label text,
  never a specific file size.
- **The "More than 20 figures" warning text** in `08-figure-leak.txt` is
  matplotlib's own message string, sourced from `matplotlib.pyplot`'s
  `_pylab_helpers` module; the *threshold* (20) and the *fact that it
  fires* are what the lab's test checks (`pytest.warns(..., match="More
  than 20 figures")`), which is stable across the 3.x series but is not a
  documented public contract.

## Machine-dependent

- **`platform`** in `test-run.txt` section 1 (`macOS-26.5.2-arm64-...`)
  reflects the authoring machine's OS and architecture. Linux and Windows
  report differently; nothing in the lab depends on the exact string.
- Nothing in this lab is randomly sampled — no `numpy.random` calls appear
  anywhere in `examples/` or `starter/` — so there is no seed-dependent
  output to track, unlike several earlier days in this section.
