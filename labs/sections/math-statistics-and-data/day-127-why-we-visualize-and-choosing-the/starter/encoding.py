"""The measurable half of visual encoding: geometry and colour arithmetic.

Nothing in this module renders anything. Everything here is a pure
function over numbers, which is exactly why it can be asserted on. The
rendering lives in `render.py`.

Two ideas carry the whole file.

1. **Area is quadratic in radius.** If you draw a value as a circle's
   RADIUS, doubling the value quadruples the ink. The reader judges the
   ink, so every ratio in the chart comes out squared. `area_for_radius`
   and the two `radii_*` functions make that concrete enough to assert on.

2. **A colour pair that is far apart for you may be on top of each other
   for a reader with a colour vision deficiency.** `simulate_deuteranopia`
   applies a published transformation matrix; `delta_e_cie76` measures how
   far apart two colours are afterwards. Neither function has an opinion --
   they return numbers, and the tests read them.

Colour maths conventions used throughout:

* An sRGB colour is a 3-tuple of floats in [0, 1] -- the same convention
  matplotlib and seaborn hand you.
* "Linear RGB" is sRGB with its transfer function undone. The colour
  vision deficiency matrix is defined on LINEAR RGB, not on the gamma
  encoded values, so `simulate_deuteranopia` linearises first and
  re-encodes afterwards. Skipping that step is the single most common
  error in hand-rolled deficiency simulators and it visibly changes the
  answer.
* CIELAB is computed against the D65 white point, matching sRGB's own
  reference white.
"""

from __future__ import annotations

import math

# --------------------------------------------------------------------------
# 1. Size encoding -- the square law
# --------------------------------------------------------------------------


def area_for_radius(radius: float) -> float:
    """Area of a circle of this radius. The whole square law in one line."""
    if radius < 0:
        raise ValueError(f"radius must be non-negative, got {radius}")
    return math.pi * radius * radius


def radii_scaled_by_radius(values: list[float], unit_radius: float = 1.0) -> list[float]:
    """Encode each value as a circle whose RADIUS is proportional to it.

    This is what you get from the obvious, wrong implementation --
    `plt.scatter(x, y, s=value)` reads `s` as an area, but a hand-written
    `Circle(xy, radius=value)` or a d3 `.attr("r", value)` does exactly
    this. A value twice as large is drawn with twice the radius and
    therefore FOUR times the area.
    """
    return [unit_radius * float(v) for v in values]


def radii_scaled_by_area(values: list[float], unit_radius: float = 1.0) -> list[float]:
    """Encode each value as a circle whose AREA is proportional to it.

    Take the square root and the distortion disappears: a value twice as
    large is drawn with twice the ink, so the ratio the reader perceives
    is the ratio in the data.
    """
    out = []
    for v in values:
        v = float(v)
        if v < 0:
            raise ValueError(f"cannot encode a negative value as an area: {v}")
        out.append(unit_radius * math.sqrt(v))
    return out


def encoded_area_ratio(values: list[float], mode: str) -> float:
    """Ratio of drawn AREA between the last and first value, under `mode`.

    `mode` is "radius" (the distorting encoding) or "area" (the honest
    one). Returns a plain float so a test can compare it against the
    ratio in the data itself.
    """
    if mode == "radius":
        radii = radii_scaled_by_radius(values)
    elif mode == "area":
        radii = radii_scaled_by_area(values)
    else:
        raise ValueError(f"mode must be 'radius' or 'area', got {mode!r}")
    first, last = area_for_radius(radii[0]), area_for_radius(radii[-1])
    if first == 0:
        raise ValueError("the first value encodes to zero area; ratio is undefined")
    return last / first


# --------------------------------------------------------------------------
# 2. Colour spaces
# --------------------------------------------------------------------------


def _srgb_to_linear_channel(c: float) -> float:
    """Undo sRGB's transfer function for one channel in [0, 1]."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb_channel(c: float) -> float:
    """Re-apply sRGB's transfer function for one channel, then clamp."""
    c = max(0.0, min(1.0, c))
    v = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return max(0.0, min(1.0, v))


def srgb_to_linear(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(_srgb_to_linear_channel(float(c)) for c in rgb)  # type: ignore[return-value]


def linear_to_srgb(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(_linear_to_srgb_channel(float(c)) for c in rgb)  # type: ignore[return-value]


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    """WCAG relative luminance: the perceived lightness of a colour.

    This is the quantity a greyscale photocopy of your chart keeps and
    everything else throws away. A palette that carries order in hue but
    not in luminance is a palette whose order vanishes in print.
    """
    r, g, b = srgb_to_linear(rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


# D65 white point in XYZ, scaled so Y = 1. sRGB's own reference white.
_D65 = (0.95047, 1.00000, 1.08883)


def srgb_to_xyz(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    r, g, b = srgb_to_linear(rgb)
    x = 0.4124564 * r + 0.3575761 * g + 0.1804375 * b
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = 0.0193339 * r + 0.1191920 * g + 0.9503041 * b
    return (x, y, z)


def _lab_f(t: float) -> float:
    delta = 6 / 29
    return t ** (1 / 3) if t > delta**3 else t / (3 * delta**2) + 4 / 29


def srgb_to_lab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert sRGB to CIELAB (L*, a*, b*) against D65.

    CIELAB exists because RGB distance is a poor model of perceived
    difference: two RGB triples the same Euclidean distance apart can look
    obviously different or nearly identical. CIELAB was built so that
    Euclidean distance is at least roughly proportional to perceived
    difference, which is what makes `delta_e_cie76` meaningful at all.
    """
    x, y, z = srgb_to_xyz(rgb)
    fx, fy, fz = _lab_f(x / _D65[0]), _lab_f(y / _D65[1]), _lab_f(z / _D65[2])
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def delta_e_cie76(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    """CIE76 colour difference: Euclidean distance in CIELAB.

    The 1976 formula is the simplest of the family and is used here
    deliberately: it is short enough to read, has no tuning constants to
    get wrong, and the tests only ever ask whether a distance is large or
    small, never for a precise perceptual match. Rough guide, from the
    literature: about 2.3 is the "just noticeable difference" for adjacent
    patches; a difference in the low single digits is two colours a reader
    will struggle to tell apart at all in a legend.
    """
    la, aa, ba = srgb_to_lab(a)
    lb, ab, bb = srgb_to_lab(b)
    return math.sqrt((la - lb) ** 2 + (aa - ab) ** 2 + (ba - bb) ** 2)


# --------------------------------------------------------------------------
# 3. Colour vision deficiency simulation
# --------------------------------------------------------------------------

# Machado, Oliveira and Fernandes (2009), "A Physiologically-based Model
# for Simulation of Color Vision Deficiency", IEEE Transactions on
# Visualization and Computer Graphics 15(6):1291-1298. This is the
# deuteranomaly matrix at severity 1.0 -- that is, deuteranopia, the
# complete absence of a working M cone. The nine coefficients were read
# from the authors' published matrix table, not reconstructed from memory.
#
# The matrix operates on LINEAR RGB. `simulate_deuteranopia` linearises
# before multiplying and re-encodes afterwards.
DEUTERANOPIA_MATRIX_MACHADO_2009 = (
    (0.367322, 0.860646, -0.227968),
    (0.280085, 0.672501, 0.047413),
    (-0.011820, 0.042940, 0.968881),
)


def simulate_deuteranopia(
    rgb: tuple[float, float, float],
    matrix: tuple[tuple[float, float, float], ...] = DEUTERANOPIA_MATRIX_MACHADO_2009,
) -> tuple[float, float, float]:
    """Return an sRGB approximation of how `rgb` appears to a deuteranope.

    A very important limit, stated here rather than buried: this
    APPROXIMATES a deficiency, it does not reproduce an experience. The
    model is a linear transform fitted to a physiological model of cone
    response; it says nothing about how a particular person has learned to
    compensate over a lifetime, it assumes a single severity, and it
    cannot represent the many varieties of anomalous trichromacy at all.
    Treat a small simulated distance as strong evidence that a palette is
    risky, and a large one as weak evidence that it is fine. The reliable
    move is still to carry the distinction in a second channel -- shape,
    position, direct labelling -- so colour is never load-bearing alone.
    """
    r, g, b = srgb_to_linear(rgb)
    out = tuple(m[0] * r + m[1] * g + m[2] * b for m in matrix)
    return linear_to_srgb(out)  # type: ignore[arg-type]


def deuteranopia_collapse(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> dict[str, float]:
    """Measure how much of a pair's separation survives deuteranopia.

    Returns the normal-vision distance, the simulated distance, and the
    fraction retained. A pair whose separation nearly vanishes is a pair
    that must not be the only thing distinguishing two series.
    """
    normal = delta_e_cie76(a, b)
    simulated = delta_e_cie76(simulate_deuteranopia(a), simulate_deuteranopia(b))
    return {
        "normal_delta_e": normal,
        "simulated_delta_e": simulated,
        "retained_fraction": simulated / normal if normal else 0.0,
    }


# --------------------------------------------------------------------------
# 4. Rank correlation, without scipy
# --------------------------------------------------------------------------


def _ranks(values: list[float]) -> list[float]:
    """Ranks, averaging ties -- the standard midrank treatment."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        midrank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = midrank
        i = j + 1
    return ranks


def spearman_rho(xs: list[float], ys: list[float]) -> float:
    """Spearman's rank correlation, computed from Pearson on the ranks.

    scipy is not installed in this environment, so this is the honest
    twenty-line version rather than a call to `scipy.stats.spearmanr`.
    Written this way it also handles ties correctly, which the shortcut
    "1 - 6*sum(d^2)/(n^3-n)" formula quietly does not.
    """
    if len(xs) != len(ys):
        raise ValueError("spearman_rho needs two sequences of the same length")
    if len(xs) < 2:
        raise ValueError("spearman_rho needs at least two observations")
    rx, ry = _ranks(list(xs)), _ranks(list(ys))
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    if dx == 0 or dy == 0:
        raise ValueError("a sequence with no variation has no rank correlation")
    return num / (dx * dy)


def luminance_order_correlation(palette: list[tuple[float, float, float]]) -> float:
    """Rank correlation between a palette's position and its luminance.

    A SEQUENTIAL palette is built so that step 1 is darker than step 2 is
    darker than step 3; its correlation is +/-1 exactly. A CATEGORICAL
    palette is built so that neighbouring swatches are as DIFFERENT as
    possible, which says nothing at all about their lightness order --
    so mapping an ordered variable onto one destroys the order.
    """
    positions = [float(i) for i in range(len(palette))]
    luminances = [relative_luminance(c) for c in palette]
    return spearman_rho(positions, luminances)
