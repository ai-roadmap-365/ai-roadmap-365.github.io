"""Exercise 3 -- the holdout rescues you. The day's centrepiece.

One dataset is built with exactly one REAL, planted effect and thirty
SPURIOUS columns with no true effect at all. Before looking at anything,
the data is split in half: an exploration set and a confirmation set that
is not touched until a hypothesis has been chosen. Both the real effect
and the best-looking spurious column are tested on the exploration half;
then, and only then, both are tested again on the untouched confirmation
half.

The real effect survives. The spurious one, chosen for looking best among
thirty candidates on the exploration half, does not. This is the whole
day's practical device in one script.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
import exploration as ex  # noqa: E402


def main() -> None:
    rng = np.random.default_rng(ds.HOLDOUT_SEED)
    df = ex.build_holdout_frame(
        rng, ds.HOLDOUT_N_TOTAL, ds.REAL_EFFECT_DELTA, ds.REAL_EFFECT_SIGMA, ds.N_SPURIOUS_CANDIDATES
    )
    exploration_df, confirmation_df = ex.split_exploration_confirmation(df, rng)
    print(f"Split into {len(exploration_df)} exploration rows and {len(confirmation_df)} confirmation rows,")
    print("the confirmation half untouched until a hypothesis is chosen below.\n")

    # --- The real, planted effect ---
    z_real_exp, p_real_exp = ex.test_column_by_group(exploration_df, "real_metric")
    z_real_conf, p_real_conf = ex.test_column_by_group(confirmation_df, "real_metric")
    print("Real effect (real_metric, planted delta = "
          f"{ds.REAL_EFFECT_DELTA}):")
    print(f"  exploration:   z={z_real_exp:.3f}  p={p_real_exp:.3e}")
    print(f"  confirmation:  z={z_real_conf:.3f}  p={p_real_conf:.3e}")

    # --- The best-looking spurious column, chosen ONLY from exploration ---
    spurious_cols = [c for c in df.columns if c.startswith("spurious_")]
    best_col, z_spur_exp, p_spur_exp = ex.best_spurious_column(exploration_df, spurious_cols)
    z_spur_conf, p_spur_conf = ex.test_column_by_group(confirmation_df, best_col)
    print(f"\nBest-looking spurious column, chosen from {len(spurious_cols)} candidates on exploration only ({best_col}):")
    print(f"  exploration:   z={z_spur_exp:.3f}  p={p_spur_exp:.4f}")
    print(f"  confirmation:  z={z_spur_conf:.3f}  p={p_spur_conf:.4f}")

    assert p_real_exp < ds.ALPHA, f"real effect should be significant on exploration, got p={p_real_exp}"
    assert p_real_conf < ds.ALPHA, f"real effect should SURVIVE on confirmation, got p={p_real_conf}"
    assert p_spur_exp < ds.ALPHA, f"the chosen spurious column should look significant on exploration, got p={p_spur_exp}"
    assert p_spur_conf >= ds.ALPHA, f"the spurious column should NOT survive confirmation, got p={p_spur_conf}"

    print(
        "\nOK: the real effect is significant on both halves -- it was "
        "never sensitive to which half you looked at. The spurious column "
        "was chosen BECAUSE it looked best among thirty candidates on the "
        "exploration half, and that same selection is exactly why it fails "
        "on data it was never fitted to. A finding that survives an "
        "untouched confirmation set is worth reporting; one that does not "
        "was a shape in the noise."
    )


if __name__ == "__main__":
    main()
