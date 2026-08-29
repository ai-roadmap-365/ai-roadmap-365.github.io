"""Chart choice as a function you can call, argue with, and test.

"Which chart should I use?" is normally answered by taste, which is why it
is normally answered badly. Two published results turn most of it into
arithmetic:

* Cleveland and McGill (1984) ranked visual channels by how accurately
  people read magnitudes off them. That ranking is `ENCODING_RANKING`.
* A variable's TYPE decides which channels can carry it honestly at all.
  A nominal variable on a length channel invents an order that is not in
  the data; an ordinal variable on a categorical hue palette destroys the
  order that is.

`best_encoding` combines the two: given a data type and the reader's task,
return the most accurately-judged channel that is still honest. Then
`choose_chart` answers the question one level up -- given the QUESTION,
how many values, and what types they are, name the chart.

These functions are opinionated on purpose. They are not the last word on
visualisation; they are a written-down default you can disagree with
explicitly, which is strictly better than an unwritten one you cannot.
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# The Cleveland-McGill ordering
# --------------------------------------------------------------------------

# Ordered most accurately judged first. From Cleveland and McGill (1984),
# "Graphical Perception: Theory, Experimentation, and Application to the
# Development of Graphical Methods", Journal of the American Statistical
# Association 79(387):531-554. Their elementary perceptual tasks, with the
# names shortened for use as identifiers.
ENCODING_RANKING: tuple[str, ...] = (
    "position_common_scale",  # 1. dots or bar ends on one shared axis
    "position_nonaligned_scales",  # 2. the same, but across separate panels
    "length",  # 3. bar lengths not sharing a baseline
    "angle_slope",  # 4. pie slices, and line steepness
    "area",  # 5. bubble size, treemap tiles
    "volume",  # 6. 3-D bars, spheres
    "color_saturation",  # 7. heatmap intensity, density shading
)

# Channels that carry identity but NOT magnitude. Cleveland and McGill did
# not rank these, because there is no magnitude to read off them: hue is
# how you say "these two lines are different series", never "this one is
# 1.8 times that one".
IDENTITY_CHANNELS: tuple[str, ...] = ("hue", "shape")

# Sequential lightness -- a colormap like viridis, ordered by luminance.
# It carries ORDER faithfully and magnitude only roughly, which places it
# with saturation at the bottom of the accuracy ordering but well above
# categorical hue for anything ordered.
ORDERED_COLOR_CHANNEL = "luminance_sequential"

DATA_TYPES: frozenset[str] = frozenset({"nominal", "ordinal", "quantitative", "temporal"})


def encoding_rank(channel: str) -> int:
    """Position of `channel` in the Cleveland-McGill ordering, 0 = best."""
    try:
        return ENCODING_RANKING.index(channel)
    except ValueError:
        raise ValueError(
            f"{channel!r} is not a ranked magnitude channel; "
            f"ranked channels are {ENCODING_RANKING}"
        ) from None


# `best_encoding`'s task vocabulary. Each task says what the reader is
# trying to DO, because the same variable in the same chart deserves a
# different channel depending on the question being asked of it.
TASKS: frozenset[str] = frozenset(
    {
        "compare",  # read two magnitudes and say which is bigger, by how much
        "compare_across_panels",  # the same, but the values sit in separate small multiples
        "identify_group",  # tell which series a mark belongs to
        "encode_in_color",  # the two spatial axes are taken; colour is all that is left
        "magnitude_on_map",  # position is spent on geography, so magnitude needs another channel
        "trend",  # read direction and rate of change over an ordered axis
    }
)


def best_encoding(data_type: str, task: str) -> str:
    """Most accurately-judged channel that can honestly carry `data_type`.

    The rule in one sentence: take the highest-ranked channel from
    Cleveland and McGill that (a) the task has not already spent on
    something else, and (b) does not claim more structure than the data
    type has.
    """
    if data_type not in DATA_TYPES:
        raise ValueError(f"unknown data type {data_type!r}; expected one of {sorted(DATA_TYPES)}")
    if task not in TASKS:
        raise ValueError(f"unknown task {task!r}; expected one of {sorted(TASKS)}")

    if task == "identify_group":
        # Identity, not magnitude. A nominal variable has no order to
        # preserve and no size to read, so hue is exactly right -- and
        # putting it on a magnitude channel would invent an order.
        return "hue"

    if task == "encode_in_color":
        # Both spatial axes are already spent. Colour is the only channel
        # left, and the data type decides WHICH colour channel.
        if data_type == "nominal":
            return "hue"
        if data_type in ("ordinal", "temporal"):
            # Order must survive. Categorical hue would destroy it; a
            # luminance-ordered ramp preserves it.
            return ORDERED_COLOR_CHANNEL
        return "color_saturation"  # quantitative: magnitude, read roughly

    if task == "magnitude_on_map":
        # Position is spent on latitude and longitude. Of what remains,
        # area is the highest-ranked channel that survives being placed at
        # an arbitrary map location -- length would need a shared baseline
        # the map cannot provide.
        return "area"

    if task == "compare_across_panels":
        # Small multiples: each panel has its own axis, so this is
        # Cleveland and McGill's second task by construction.
        return "position_nonaligned_scales"

    if task == "trend":
        # Direction over an ordered axis. Slope is the thing being read,
        # but it is read off points placed on one common scale, and the
        # accuracy of the reading is the accuracy of those positions.
        return "position_common_scale"

    # task == "compare": one shared axis, the best channel there is. This
    # holds for every data type, including nominal -- a bar chart of
    # nominal categories puts the CATEGORY on the categorical axis and the
    # QUANTITY on the common scale, which invents no order at all.
    return "position_common_scale"


# --------------------------------------------------------------------------
# From the question to the chart
# --------------------------------------------------------------------------

QUESTION_KINDS: frozenset[str] = frozenset(
    {
        "comparison",  # which of these is biggest? by how much?
        "distribution",  # what shape is this variable? where is the mass?
        "relationship",  # does x move with y?
        "composition",  # what are the parts of this whole?
        "change_over_time",  # what happened, and in which direction?
    }
)

# Below this many values, a table is the better instrument. The number is
# a judgement, not a measurement, and the reasoning is written out in
# `choose_chart`'s docstring so you can move it deliberately.
TABLE_MAX_VALUES = 5

# Above this many points, individual marks stop being individually
# readable and the chart is showing density whether you meant it to or
# not. Better to say so and draw density directly.
OVERPLOT_POINT_LIMIT = 2000

# Above this many series, one panel becomes a tangle. Split it.
SMALL_MULTIPLE_LIMIT = 8


def choose_chart(question_kind: str, n_categories: int, data_types: list[str]) -> str:
    """Recommend a chart -- or a table -- for a question.

    `n_categories` is the number of values the reader must take in: bars in
    a bar chart, points in a scatter, lines in a line chart.

    Two recommendations in here are the point of the whole function.

    **It recommends a table below `TABLE_MAX_VALUES` values.** Three
    numbers do not need an axis, a legend and a title in order to be
    compared; they need to be readable. A chart's advantage is that it
    turns comparison into a perceptual judgement instead of an arithmetic
    one, and with three numbers there was never any arithmetic to save.
    The threshold is a judgement call, and 5 is where the trade tips in
    this course's experience -- put it somewhere else if your readers
    differ, but put it somewhere on purpose.

    **It never recommends a pie chart, for anything.** Reading a pie means
    judging angle and area, ranked fourth and fifth by Cleveland and
    McGill, when the identical data on a sorted bar chart would be
    position on a common scale, ranked first. The one case usually offered
    in a pie's defence -- two or three parts of a whole -- falls below
    `TABLE_MAX_VALUES` and gets a table, which answers the question
    exactly rather than approximately.
    """
    if question_kind not in QUESTION_KINDS:
        raise ValueError(
            f"unknown question kind {question_kind!r}; expected one of {sorted(QUESTION_KINDS)}"
        )
    if n_categories < 1:
        raise ValueError(f"n_categories must be at least 1, got {n_categories}")
    unknown = set(data_types) - DATA_TYPES
    if unknown:
        raise ValueError(f"unknown data types {sorted(unknown)}; expected from {sorted(DATA_TYPES)}")

    if question_kind == "change_over_time":
        # A time axis is not optional here: "over time" with no temporal
        # variable is a question about something else.
        if "temporal" not in data_types:
            raise ValueError(
                "change_over_time needs a temporal variable in data_types; "
                f"got {sorted(data_types)}"
            )
        return "small_multiples_line" if n_categories > SMALL_MULTIPLE_LIMIT else "line"

    if question_kind == "relationship":
        if "quantitative" not in data_types:
            raise ValueError(
                "relationship needs at least one quantitative variable; " f"got {sorted(data_types)}"
            )
        # Past the overplot limit the marks are stacked on each other and
        # the reader is looking at ink density, not at points.
        return "hexbin" if n_categories > OVERPLOT_POINT_LIMIT else "scatter"

    if question_kind == "distribution":
        if "quantitative" not in data_types:
            raise ValueError(
                "distribution needs a quantitative variable; " f"got {sorted(data_types)}"
            )
        if n_categories <= 1:
            return "histogram"
        if n_categories <= SMALL_MULTIPLE_LIMIT:
            return "small_multiples_histogram"
        return "boxplot_by_category"

    # comparison and composition share the table rule.
    if n_categories <= TABLE_MAX_VALUES:
        return "table"

    if question_kind == "composition":
        return "stacked_bar"

    return "sorted_horizontal_bar"


# --------------------------------------------------------------------------
# Sorting, measured as reader effort
# --------------------------------------------------------------------------


def comparisons_to_find_max(values: list[float], presented_sorted: bool) -> int:
    """How many comparisons a reader makes to find the largest value.

    This simulates a reader, not a computer. Two behaviours, both real:

    * **Source order.** The reader has no idea where the biggest bar is,
      so they hold a running best and check every remaining bar against
      it: `n - 1` comparisons for `n` bars.
    * **Sorted, descending.** The reader looks at the top row. They still
      make ONE comparison -- top row against the next one -- to confirm
      the chart really is sorted and the leader really is ahead. After
      that they stop, because sorting is a promise about everything below.

    The answer is identical either way. The effort is not, and sorting is
    the cheapest thing you will ever do to a chart.
    """
    n = len(values)
    if n < 2:
        raise ValueError("finding a maximum needs at least two values")
    return 1 if presented_sorted else n - 1


def index_of_max(values: list[float]) -> int:
    """Index of the largest value, for confirming sorting changes only effort."""
    return max(range(len(values)), key=lambda i: values[i])
