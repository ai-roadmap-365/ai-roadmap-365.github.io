"""Exercise 8 — the legitimate craft, made measurable.

Storytelling is not the opposite of honesty. An unordered, unlabelled,
uncommented chart is not neutral; it is unhelpful, and it quietly hands
the reader's conclusion over to whatever the default sort order happened
to be. This exercise measures three pieces of real craft: ordering,
annotation, and emphasis that survives a greyscale printer.
"""

import matplotlib.pyplot as plt
import seaborn as sns

import honesty as H

LABELS = ["north", "south", "east", "west", "central"]
VALUES = [41.0, 88.0, 37.0, 52.0, 63.0]
CLAIM = "south is 39% higher than the next region"


def main():
    print("Part 1 -- ordering. A five-bar chart, answering 'which is biggest?'")
    print()
    unsorted_cost = H.comparisons_to_find_max(VALUES)
    ordered = sorted(VALUES, reverse=True)
    sorted_cost = H.comparisons_to_find_max(ordered)
    print(f"  alphabetical order {VALUES}  -> {unsorted_cost} comparisons")
    print(f"  sorted descending  {ordered}  -> {sorted_cost} comparisons")
    print()
    assert unsorted_cost == len(VALUES) - 1, unsorted_cost
    assert sorted_cost == 0, sorted_cost
    assert sorted_cost < unsorted_cost
    print("  This is an idealised model of reading effort, not a measurement")
    print("  of human readers: sorted bars put the answer at a known end, so")
    print("  position encodes rank and no comparison is needed. Its claim is")
    print("  the ordering of the two numbers, not their exact size.")
    print()

    print("Part 2 -- annotation. The chart states its claim as retrievable text.")
    print()
    fig, ax = H.annotated_bar_chart(LABELS, VALUES, CLAIM)
    try:
        fig.canvas.draw()
        text = H.axes_text(ax)
        bar_order = [t.get_text() for t in ax.get_xticklabels()]
    finally:
        plt.close(fig)
    print(f"  bars, left to right : {bar_order}")
    for item in text:
        print(f"  text on the Axes    : {item!r}")
    print()
    assert CLAIM in text, text
    assert text.count(CLAIM) >= 2, "the claim should be both the title and an annotation"
    assert bar_order[0] == "south", bar_order
    assert "value" in text, text
    print("  A caption that states a claim is what lets a reader disagree with")
    print("  the chart. A chart with no claim cannot be argued with, which")
    print("  reads as neutrality and is really just an unfinished argument.")
    print()

    print("Part 3 -- emphasis that survives losing colour.")
    print()
    pairs = {
        "highlight vs muted (this chart)": (H.HIGHLIGHT, H.MUTED),
        "seaborn 'colorblind' first two": tuple(sns.color_palette("colorblind").as_hex()[:2]),
        "classic red vs classic green": (H.CLASSIC_RED, H.CLASSIC_GREEN),
    }
    print("  pair                              colours              luminance gap")
    gaps = {}
    for name, (first, second) in pairs.items():
        gap = H.luminance_separation(first, second)
        gaps[name] = gap
        print(f"  {name:<32}  {first} / {second}   {gap:.4f}")
    print()
    red_green = gaps["classic red vs classic green"]
    emphasis = gaps["highlight vs muted (this chart)"]
    palette = gaps["seaborn 'colorblind' first two"]
    assert emphasis > 0.5, emphasis
    assert palette > red_green, (palette, red_green)
    assert emphasis > palette > red_green

    print(f"  The classic red/green pair differs by {red_green:.4f} in luminance --")
    print("  the one channel every reader has. Told apart by hue alone, it is")
    print("  the pair that vanishes for a red-green colour-deficient reader,")
    print("  on a greyscale printer, and on a washed-out projector.")
    print(f"  Seaborn's 'colorblind' palette opens at {palette:.4f}, and deliberate")
    print(f"  emphasis -- one dark bar against pale ones -- reaches {emphasis:.4f}.")
    print()
    print("  Luminance is ONE component of whether two colours can be told")
    print("  apart, not the whole of it; a full colour-deficiency simulation")
    print("  needs a colour-appearance model this lab does not implement.")
    print("  The narrow claim it does support: two colours with nearly equal")
    print("  luminance are separable by hue alone, and hue alone is exactly")
    print("  what some of your readers do not have.")
    print()
    print("08_ordering_and_annotation.py: every assertion held.")


if __name__ == "__main__":
    main()
