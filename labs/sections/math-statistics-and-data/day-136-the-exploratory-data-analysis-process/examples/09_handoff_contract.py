"""Exercise 9 -- the handoff to Day 133.

Exploration ends by choosing which few findings deserve a document. This
script builds the object exploration hands to the report stage -- the
finding, its result on the untouched confirmation set (exercise 3), and
the comparison count the research log kept (exercise 6) -- and proves the
report stage REFUSES to run without all three, the same way Day 133's
report generator refuses a figure with no stated question.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
import exploration as ex  # noqa: E402


def main() -> None:
    # Re-derive exercise 3's real finding so this script is self-contained.
    rng = np.random.default_rng(ds.HOLDOUT_SEED)
    df = ex.build_holdout_frame(
        rng, ds.HOLDOUT_N_TOTAL, ds.REAL_EFFECT_DELTA, ds.REAL_EFFECT_SIGMA, ds.N_SPURIOUS_CANDIDATES
    )
    exploration_df, confirmation_df = ex.split_exploration_confirmation(df, rng)
    z_exp, p_exp = ex.test_column_by_group(exploration_df, "real_metric")
    z_conf, p_conf = ex.test_column_by_group(confirmation_df, "real_metric")

    finding = {"name": "real_metric by group", "p": p_exp, "z": z_exp}
    confirmation_result = {"p": p_conf, "z": z_conf, "survived": p_conf < ds.ALPHA}
    comparison_count = ds.N_SPURIOUS_CANDIDATES + 1  # every spurious column tried, plus the real one

    handoff = ex.build_handoff(finding, confirmation_result, comparison_count)
    report_line = ex.write_report_stub(handoff)
    print("A valid handoff builds and the report stage accepts it:")
    print(f"  {report_line}")

    assert handoff["finding"] == finding
    assert handoff["confirmation_result"] == confirmation_result
    assert handoff["comparison_count"] == comparison_count

    print("\nNow proving the report stage refuses an incomplete handoff:")
    for missing_field in ex.REQUIRED_HANDOFF_FIELDS:
        kwargs = {
            "finding": finding,
            "confirmation_result": confirmation_result,
            "comparison_count": comparison_count,
        }
        kwargs[missing_field] = None
        try:
            ex.build_handoff(**kwargs)
        except ValueError as exc:
            print(f"  missing '{missing_field}': refused -- {exc}")
        else:
            raise AssertionError(f"expected build_handoff to refuse a handoff missing '{missing_field}'")

    try:
        ex.write_report_stub({"finding": finding})  # missing the other two fields entirely
    except ValueError as exc:
        print(f"  a bare finding with nothing else: refused -- {exc}")
    else:
        raise AssertionError("expected write_report_stub to refuse a finding with no confirmation result or count")

    print(
        "\nOK: the report stage cannot be handed a finding alone. It needs "
        "to know the finding survived an untouched confirmation set "
        "(exercise 3) and how many comparisons were run before it was "
        "chosen (exercise 6's research log) -- which is exactly what makes "
        "the choice of what to write up, at the end of exploration, "
        "defensible rather than asserted."
    )


if __name__ == "__main__":
    main()
