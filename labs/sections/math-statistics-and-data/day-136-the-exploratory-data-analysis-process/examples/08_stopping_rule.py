"""Exercise 8 -- a stopping rule.

Two ways to decide when exploration ends, tested against data with NO
real signal so the true false-positive rate is knowable: a time-boxed
rule that asks a fixed budget of questions and stops regardless of
whether anything looked interesting along the way, versus the failure
mode named directly in the brief -- "we stopped when we found
something" -- which keeps asking until the first p < 0.05 turns up.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402

import dataset as ds  # noqa: E402
import exploration as ex  # noqa: E402


def main() -> None:
    rng = np.random.default_rng(ds.STOPPING_SEED)
    budget = ds.STOPPING_BUDGET_QUESTIONS

    print(f"Budget: {budget} questions. Data has NO real signal, so the honest false-positive")
    print(f"rate at alpha={ds.ALPHA} should sit near {ds.ALPHA} for any rule that does not")
    print("selectively report based on what it saw along the way.\n")

    tb_rate = ex.time_boxed_false_positive_rate(rng, ds.STOPPING_FAMILIES, budget, ds.ALPHA)
    print(f"Time-boxed rule (ask {budget}, report the pre-declared last one, stop regardless):")
    print(f"  measured false-positive rate: {tb_rate:.4f}")

    sw_rate = ex.stop_when_significant_rate(rng, ds.STOPPING_FAMILIES, budget, ds.ALPHA)
    print(f"\n'Stop when significant' rule (ask up to {budget}, stop and report at the first p<{ds.ALPHA}):")
    print(f"  measured false-positive rate: {sw_rate:.4f}")

    assert abs(tb_rate - ds.ALPHA) < 0.015, f"time-boxed rate should sit near alpha={ds.ALPHA}, got {tb_rate:.4f}"
    assert sw_rate > 3 * ds.ALPHA, f"stop-when-significant rate should be far above alpha={ds.ALPHA}, got {sw_rate:.4f}"
    assert sw_rate > tb_rate, "stopping when significant must inflate the false-positive rate above the time-boxed rule"

    print(
        f"\nOK: the time-boxed rule lands at {tb_rate:.4f}, close to the "
        f"nominal alpha={ds.ALPHA}, because it reports a decision made "
        f"before any data was seen. 'Stop when significant' lands at "
        f"{sw_rate:.4f} -- roughly {sw_rate / ds.ALPHA:.1f} times higher -- "
        "using the exact same budget of looks, because the stopping "
        "decision itself was made using the data. Time-boxing (or a "
        "fixed count of questions) is not a bureaucratic nicety; it is "
        "the difference between these two numbers."
    )


if __name__ == "__main__":
    main()
