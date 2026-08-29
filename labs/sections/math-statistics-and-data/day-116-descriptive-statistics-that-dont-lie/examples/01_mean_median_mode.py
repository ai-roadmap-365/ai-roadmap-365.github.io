"""Exercise 1: mean, median and mode, from scratch, checked against the
`statistics` module on the same inputs."""

import statistics as st

import dataset as D
import descriptive as F


def main() -> None:
    m = F.mean(D.ODD_LIST)
    ref_mean = st.fmean(D.ODD_LIST)
    print(f"odd list         : {D.ODD_LIST}")
    print(f"  mean (ours)     = {m}")
    print(f"  mean (stdlib)   = {ref_mean}")
    assert m == ref_mean

    med = F.median(D.ODD_LIST)
    ref_med = st.median(D.ODD_LIST)
    print(f"  median (ours)   = {med}")
    print(f"  median (stdlib) = {ref_med}")
    assert med == ref_med

    mo = F.modes(D.ODD_LIST)
    print(f"  modes           = {mo}")
    assert mo == [7]

    print(f"even list         : {D.EVEN_LIST}")
    med_even = F.median(D.EVEN_LIST)
    ref_med_even = st.median(D.EVEN_LIST)
    print(f"  median (ours)   = {med_even}")
    print(f"  median (stdlib) = {ref_med_even}")
    assert med_even == ref_med_even == 6.0  # average of 4.0 and 8.0

    print(f"multimodal list   : {D.MULTIMODAL_LIST}")
    mo_multi = F.modes(D.MULTIMODAL_LIST)
    ref_multi = sorted(st.multimode(D.MULTIMODAL_LIST))
    print(f"  modes (ours)    = {mo_multi}")
    print(f"  modes (stdlib)  = {ref_multi}")
    assert mo_multi == ref_multi == [3, 8]
    # statistics.mode() (singular) does NOT raise on ties -- it silently
    # returns whichever tied value it saw first, which is exactly the
    # "average income" trap in miniature: a single-number summary hiding
    # that there were two equally valid answers.
    single = st.mode(D.MULTIMODAL_LIST)
    print(f"  statistics.mode() picks just one: {single} (silently drops {mo_multi[1] if single == mo_multi[0] else mo_multi[0]})")
    assert single in mo_multi

    print("01_mean_median_mode.py: every assertion held.")


if __name__ == "__main__":
    main()
