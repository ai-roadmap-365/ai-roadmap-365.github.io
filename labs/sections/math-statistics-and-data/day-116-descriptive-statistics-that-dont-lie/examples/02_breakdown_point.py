"""Exercise 2: the breakdown point. Corrupt exactly one salary out of nine
and watch what happens to the mean versus the median."""

import dataset as D
import descriptive as F


def main() -> None:
    print(f"salaries           : {D.SALARY_LIST}")
    print(f"corrupted value    : {D.CORRUPTED_SALARY:,}")

    mean_before, mean_after = F.breakdown_point_mean(D.SALARY_LIST, D.CORRUPTED_SALARY)
    print(f"mean before        = {mean_before:,.2f}")
    print(f"mean after         = {mean_after:,.2f}")
    mean_shift = mean_after - mean_before
    print(f"mean moved by      = {mean_shift:,.2f}")
    assert mean_shift > D.BREAKDOWN_MEAN_SHIFT_FLOOR

    median_before, median_after = F.breakdown_point_median(D.SALARY_LIST, D.CORRUPTED_SALARY)
    print(f"median before      = {median_before:,.2f}")
    print(f"median after       = {median_after:,.2f}")
    median_shift = median_after - median_before
    print(f"median moved by    = {median_shift:,.2f}")
    # Exact equality is the right assertion: one corrupted value out of nine
    # cannot move the median AT ALL, because the median only cares about the
    # RANK of the middle value, and the corrupted value (however extreme)
    # is still the single largest value, occupying the same rank position
    # (9th of 9) whether it is $60,000 or $10,000,000.
    assert median_shift == 0.0

    print(
        "One value out of nine dragged the mean by "
        f"${mean_shift:,.0f} and the median by exactly $0."
    )
    print("02_breakdown_point.py: every assertion held.")


if __name__ == "__main__":
    main()
