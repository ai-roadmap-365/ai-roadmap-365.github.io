# What is installed, why, and what it costs

Six packages, all free and open source, installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `matplotlib` | 3.11.1 | matplotlib licence (BSD-style, PSF-derived) | Every render in `render.py`, through the headless `Agg` backend; also the source of the `viridis` and `tab10` palettes exercise 5 measures. |
| `seaborn` | 0.13.2 | BSD 3-Clause | `color_palette("colorblind")` — the colourblind-safe pair exercise 4 measures. Nothing in this lab calls seaborn's plotting functions; it is used as a palette source, offline. |
| `pandas` | 3.0.5 | BSD 3-Clause | Not imported by this lab. It is pinned because seaborn declares it as a hard dependency, and leaving it unpinned would let the resolver pick a different version on a different day. |
| `numpy` | 2.5.2 | BSD 3-Clause | The point cloud in exercise 8, and every pixel count — the images are read as arrays. |
| `pillow` | 12.3.0 | MIT-CMU | Reads the rendered PNGs back off disk so their pixels can be counted. This is what makes "the chart uses more ink" a measurement. |
| `pytest` | 9.1.1 | MIT | The test harness every exercise is written against. |

`math`, `pathlib` and `tempfile` are Python standard library — no
install, no cost. `math` does the square-law arithmetic and the CIELAB
conversion; `tempfile` creates the directory every render is written
into, so nothing lands inside the lab.

Deliberately **not** installed, and described in the lesson from public
documentation only: Vega-Lite and plotly. No output attributed to either
is reproduced anywhere in this lab.

There is no paid tier of anything here, no account, no key and no signup,
personally or commercially.
