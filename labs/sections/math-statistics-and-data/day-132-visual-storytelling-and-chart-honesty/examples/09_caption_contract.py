"""Exercise 9 — a review contract you can run on your own charts.

Everything before this was diagnosis. This is the tool. Four checks, run
against a chart's own Axes and its caption, that catch the distortions
this lab measured -- and that pass a chart which breaks a rule and says
so, because breaking a rule deliberately and disclosing it is
professional work, and breaking it silently is not.
"""

import matplotlib.pyplot as plt

import honesty as H

VALUES = (100.0, 102.0)


def report(name, ax, caption):
    passed, failures = H.review_chart(ax, caption)
    print(f"  {name}")
    print(f"    caption : {caption!r}")
    print(f"    ylim    : {ax.get_ylim()}")
    print(f"    ylabel  : {ax.get_ylabel()!r}")
    print(f"    verdict : {'PASS' if passed else 'FAIL'}")
    for failure in failures:
        print(f"      - {failure}")
    print()
    return passed, failures


def main():
    print("Four checks. A chart passes only if all four hold.")
    print("  1. the caption states a claim a reader could disagree with")
    print("  2. the y axis is labelled")
    print("  3. a non-zero baseline is named in the caption")
    print("  4. the baseline is zero, or its absence is disclosed")
    print()

    fig, ax = H.bar_pair(VALUES)
    try:
        fig.canvas.draw()
        honest_pass, honest_failures = report(
            "HONEST -- zero baseline",
            ax,
            "Group B is 2% higher than group A.",
        )
    finally:
        plt.close(fig)

    fig, ax = H.bar_pair(VALUES, ylim=(99, 103))
    try:
        fig.canvas.draw()
        lying_pass, lying_failures = report(
            "TRUNCATED -- baseline moved, nothing said",
            ax,
            "Group B is 2% higher than group A.",
        )
    finally:
        plt.close(fig)

    fig, ax = H.line_pair(VALUES, ylim=(99, 103))
    ax.set_ylabel("value")
    try:
        fig.canvas.draw()
        disclosed_pass, disclosed_failures = report(
            "DISCLOSED -- a line on a non-zero baseline, declared",
            ax,
            "Group B is 2% higher than group A. Note: the y axis starts at "
            "99, not zero, so the change is legible; the baseline is "
            "labelled on the axis.",
        )
    finally:
        plt.close(fig)

    fig, ax = H.bar_pair(VALUES)
    ax.set_ylabel("")
    try:
        fig.canvas.draw()
        bare_pass, bare_failures = report(
            "BARE -- zero baseline, but no label and no claim",
            ax,
            "Results.",
        )
    finally:
        plt.close(fig)

    assert honest_pass, honest_failures
    assert not lying_pass, "the truncated chart must fail the contract"
    assert any("does not say so" in f for f in lying_failures), lying_failures
    assert any("without disclosure" in f for f in lying_failures), lying_failures
    assert disclosed_pass, disclosed_failures
    assert not bare_pass, "an unlabelled, claimless chart must fail"
    assert len(bare_failures) == 2, bare_failures

    print("  The interesting row is the third one. It uses a non-zero")
    print("  baseline, which is the exact thing the second row failed for,")
    print("  and it passes -- because it is a line rather than a bar, and")
    print("  because the caption says what it did. The contract does not")
    print("  forbid breaking the rule. It forbids breaking it in silence.")
    print()
    print("  The fourth row is the other half of the lesson: a chart can be")
    print("  perfectly accurate and still fail, because a chart with no")
    print("  claim and no label has not communicated anything.")
    print()
    print("  Check 1 is a keyword heuristic. It catches a MISSING claim; it")
    print("  cannot judge a WRONG one. No automated check can, and a review")
    print("  tool that pretended otherwise would be its own kind of lie.")
    print()
    print("09_caption_contract.py: every assertion held.")


if __name__ == "__main__":
    main()
