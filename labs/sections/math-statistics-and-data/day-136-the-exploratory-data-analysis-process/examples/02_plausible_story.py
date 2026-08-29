"""Exercise 2 -- a plausible story for noise.

The "winning" comparison from exercise 1's forty-comparison scan is not
just statistically significant by the letter of the test -- it also LOOKS
like a real finding, in the specific sense that its effect size clears
the conventional boundary between a "medium" and a "large" effect (Cohen,
1988). That is exactly why forking paths are tempting rather than
obviously wrong: the noise did not produce a weak, forgettable blip. It
produced something a reasonable analyst would be excited to write up, and
could attach a plausible story to ("older customers use fewer sessions
because they are more habitual users") without anyone being able to tell,
from the number alone, that the story is fiction.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
import exploration as ex  # noqa: E402


def main() -> None:
    rng = np.random.default_rng(ds.NARRATIVE_SEED)
    df = ds.build_narrative_frame(rng)
    results = ex.scan_narrative_frame(df, ds.NARRATIVE_SUBSET_COLS, ds.NARRATIVE_OUTCOME_COLS)
    best = ex.best_significant_result(results)
    assert best is not None, "exercise 1's scan must produce at least one significant result"

    effect_size = abs(best["effect_size"])
    print(f"Winning comparison: {best['subset']} split, outcome = {best['outcome']} ({best['cut']})")
    print(f"  p-value:      {best['p']:.4f}")
    print(f"  effect size:  d = {effect_size:.3f}")
    print(f"  a plausible story: '{best['subset'].replace('_', ' ')} customers show a real difference")
    print(f"  in {best['outcome'].replace('_', ' ')}, and the effect is not small.'")

    assert effect_size >= ds.PUBLISHABLE_EFFECT_SIZE, (
        f"expected a 'publishable-looking' effect size >= {ds.PUBLISHABLE_EFFECT_SIZE}, got {effect_size:.3f}"
    )

    print(
        f"\nOK: d={effect_size:.3f} clears the conventional d=0.5 boundary "
        "between a medium and a large effect. The data underneath this "
        "number has NO true effect of any kind by construction -- every "
        "outcome column was drawn independently of every grouping column. "
        "A p-value and an effect size that both look real is what makes "
        "the garden of forking paths dangerous: the usual defence, 'but "
        "the effect is substantial, not just significant,' does not "
        "distinguish a real finding from a large false positive, because "
        "conditioning on 'passed the filter' inflates both the p-value's "
        "extremity and the effect size at the same time."
    )


if __name__ == "__main__":
    main()
