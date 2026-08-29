"""Exercise 5 — two textbook bin rules, two opposite conclusions.

Day 130 established that bin width is a choice. This is what the choice
costs. The sample really is drawn from two components. Sturges' rule
draws one hump; the Freedman-Diaconis rule draws two. Neither rule is
wrong, and neither chart is a lie -- but only one of them supports the
sentence the author wants to write.
"""

import numpy as np

import honesty as H


def main():
    sample = H.bimodal_sample()
    print(f"A sample of {len(sample)} values, drawn from TWO normal components")
    print("centred at -0.85 and +0.85 with standard deviation 0.95. There are,")
    print("by construction, two modes in the process that generated it.")
    print()

    results = {}
    print("  rule                bins   width   humps drawn   counts")
    for rule in ("sturges", "fd"):
        edges = np.histogram_bin_edges(sample, bins=rule)
        counts = H.histogram_counts(sample, bins=rule)
        modes = H.count_modes(counts)
        results[rule] = (len(counts), float(edges[1] - edges[0]), modes)
        shown = " ".join(f"{int(c):>3d}" for c in counts)
        print(f"  {rule:<18}  {len(counts):>3d}   {edges[1] - edges[0]:.3f}       {modes}        {shown}")
    print()

    sturges_bins, sturges_width, sturges_modes = results["sturges"]
    fd_bins, fd_width, fd_modes = results["fd"]

    assert sturges_modes == 1, sturges_modes
    assert fd_modes == 2, fd_modes
    assert sturges_modes != fd_modes

    print("  Two statements, each supported by a chart drawn from the same")
    print("  400 numbers with a rule you could cite in a methods section:")
    print(f"    Sturges ({sturges_bins} bins, width {sturges_width:.3f}):")
    print("      'the distribution is unimodal, centred near zero'")
    print(f"    Freedman-Diaconis ({fd_bins} bins, width {fd_width:.3f}):")
    print("      'the distribution is bimodal, with two distinct groups'")
    print()
    print(f"  The two rules differ by {fd_bins - sturges_bins} bins. That is the whole distance")
    print("  between the two conclusions, and it is the fragility -- not")
    print("  either chart -- that the reader needs told.")
    print()
    print("  The defence: when a conclusion depends on the bin width, say so,")
    print("  and show the raw values as a rug or a strip plot underneath, so")
    print("  the reader can see what the bins are hiding.")
    print()
    print("05_binning_changes_the_conclusion.py: every assertion held.")


if __name__ == "__main__":
    main()
