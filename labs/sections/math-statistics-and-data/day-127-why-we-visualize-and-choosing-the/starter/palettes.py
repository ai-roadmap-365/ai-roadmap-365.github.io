"""The palettes this lab measures, taken from the libraries themselves.

Nothing here is a hand-picked colour chosen to make a point. Every swatch
is what matplotlib or seaborn hands you by default, which is what makes
the measurements in `test_charts.py` about real tools rather than about a
straw man.

* `PASS_FAIL_RED` and `PASS_FAIL_GREEN` are `tab10`'s red and green --
  matplotlib's default cycle, positions 3 and 2. The reflex "red means
  failed, green means passed" chart is drawn in exactly these two colours
  by anyone who does not stop to think about it.
* `SAFE_BLUE` and `SAFE_ORANGE` are the first two entries of seaborn's
  `colorblind` palette, which is that library's own answer to the same
  problem.
* `viridis_steps` samples matplotlib's default SEQUENTIAL colormap, which
  is built to increase monotonically in luminance.
* `tab10_steps` samples its default CATEGORICAL palette, which is built so
  neighbouring swatches look as different as possible -- and therefore
  carries no luminance order at all.

Both `viridis` and `tab10` ship inside matplotlib. Nothing here touches
the network.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

Color = tuple[float, float, float]


def _rgb(c) -> Color:
    return (float(c[0]), float(c[1]), float(c[2]))


# matplotlib's default categorical cycle, positions 3 (red) and 2 (green).
PASS_FAIL_RED: Color = _rgb(plt.get_cmap("tab10")(3))
PASS_FAIL_GREEN: Color = _rgb(plt.get_cmap("tab10")(2))

# seaborn's own colourblind-safe categorical palette, first two entries.
_CB = sns.color_palette("colorblind")
SAFE_BLUE: Color = _rgb(_CB[0])
SAFE_ORANGE: Color = _rgb(_CB[1])


def viridis_steps(n: int = 5) -> list[Color]:
    """`n` evenly spaced samples of matplotlib's sequential default."""
    cmap = plt.get_cmap("viridis")
    return [_rgb(cmap(i / (n - 1))) for i in range(n)]


def tab10_steps(n: int = 5) -> list[Color]:
    """The first `n` entries of matplotlib's categorical default."""
    cmap = plt.get_cmap("tab10")
    return [_rgb(cmap(i)) for i in range(n)]


# An ordered variable with five levels. Its ORDER is the whole point: a
# palette that does not preserve it has destroyed information the data
# had, which is a different and worse failure than merely looking bad.
SATISFACTION_LEVELS: tuple[str, ...] = (
    "very dissatisfied",
    "dissatisfied",
    "neutral",
    "satisfied",
    "very satisfied",
)
