"""Exercise 7: Simpson's paradox. Treatment A beats treatment B in EVERY
subgroup, and treatment B beats treatment A overall -- from the same
table, both directions verified by direct arithmetic."""

import dataset as D
import descriptive as F


def main() -> None:
    a_easy_rate = F.success_rate(*D.TREATMENT_A_EASY)
    a_hard_rate = F.success_rate(*D.TREATMENT_A_HARD)
    b_easy_rate = F.success_rate(*D.TREATMENT_B_EASY)
    b_hard_rate = F.success_rate(*D.TREATMENT_B_HARD)

    print("                 easy subgroup      hard subgroup")
    print(
        f"treatment A   {D.TREATMENT_A_EASY[0]}/{D.TREATMENT_A_EASY[1]} = {a_easy_rate:.1%}"
        f"         {D.TREATMENT_A_HARD[0]}/{D.TREATMENT_A_HARD[1]} = {a_hard_rate:.1%}"
    )
    print(
        f"treatment B   {D.TREATMENT_B_EASY[0]}/{D.TREATMENT_B_EASY[1]} = {b_easy_rate:.1%}"
        f"        {D.TREATMENT_B_HARD[0]}/{D.TREATMENT_B_HARD[1]} = {b_hard_rate:.1%}"
    )

    # Direction one: A wins BOTH subgroups.
    assert a_easy_rate > b_easy_rate
    assert a_hard_rate > b_hard_rate
    print()
    print(f"A beats B in the easy subgroup:  {a_easy_rate:.1%} > {b_easy_rate:.1%}")
    print(f"A beats B in the hard subgroup:  {a_hard_rate:.1%} > {b_hard_rate:.1%}")

    a_total = F.combined_rate(D.TREATMENT_A_EASY, D.TREATMENT_A_HARD)
    b_total = F.combined_rate(D.TREATMENT_B_EASY, D.TREATMENT_B_HARD)
    a_n = D.TREATMENT_A_EASY[1] + D.TREATMENT_A_HARD[1]
    b_n = D.TREATMENT_B_EASY[1] + D.TREATMENT_B_HARD[1]
    print()
    print(f"treatment A overall: {a_total:.1%}  (out of {a_n} trials)")
    print(f"treatment B overall: {b_total:.1%}  (out of {b_n} trials)")

    # Direction two: B wins OVERALL. Both directions, same table.
    assert b_total > a_total

    print()
    print(
        "A won every subgroup and lost overall. The mechanism: A took "
        f"{D.TREATMENT_A_HARD[1]} of its {a_n} trials in the hard subgroup "
        f"(where success is rare for everyone), while B took only "
        f"{D.TREATMENT_B_HARD[1]} of its {b_n} trials there. The overall "
        "rate is a WEIGHTED average, and the weights -- not the treatment "
        "-- are what flipped the ranking."
    )
    print("07_simpsons_paradox.py: every assertion held.")


if __name__ == "__main__":
    main()
