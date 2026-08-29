"""Exercise 7 -- segments, carefully.

Segments generate hypotheses, they do not confirm them -- testing every
segment at the full alpha is Day 118's multiple-comparisons problem wearing
a friendly face. But segments are also where Simpson's paradox hides: an
effect can point one way in EVERY segment and the opposite way overall. This
step reports each segment plainly, and explicitly flags a reversal instead
of silently reporting the pooled number as if the segments agreed with it.
"""

from pathlib import Path

from experiment import load_experiment, segment_analysis

DATA_DIR = Path(__file__).parent.parent / "data"

rows_a = load_experiment(DATA_DIR / "exp_a.csv")
rows_b = load_experiment(DATA_DIR / "exp_b.csv")

seg_a = segment_analysis(rows_a)
seg_b = segment_analysis(rows_b)

print("dataset A:")
print(f"  pooled diff = {seg_a['pooled_diff_pp']:+.3f} pp")
for segment, info in seg_a["segments"].items():
    print(f"    {segment:<8} n_c={info['n_control']:>5} n_t={info['n_treatment']:>5} diff={info['diff_pp']:+.3f} pp")
print(f"  reversal_flagged = {seg_a['reversal_flagged']}")

print("dataset B:")
print(f"  pooled diff = {seg_b['pooled_diff_pp']:+.3f} pp")
for segment, info in seg_b["segments"].items():
    print(f"    {segment:<8} n_c={info['n_control']:>5} n_t={info['n_treatment']:>5} diff={info['diff_pp']:+.3f} pp")
print(f"  reversal_flagged = {seg_b['reversal_flagged']}")

# Dataset A: no reversal. The one segment that dips slightly negative
# (tablet, close to zero) does not make every segment disagree with the
# pooled sign, so the flag must stay off.
assert not seg_a["reversal_flagged"], "dataset A should not trip the Simpson's-paradox flag"

# Dataset B: genuine Simpson's paradox. Every segment's sign is the OPPOSITE
# of the pooled sign, and the analysis must say so rather than silently
# reporting the pooled +lift as if it were good news.
assert seg_b["pooled_diff_pp"] > 0, "dataset B's pooled number should look positive"
for segment, info in seg_b["segments"].items():
    assert info["diff_pp"] < 0, (
        f"dataset B segment '{segment}' should show a NEGATIVE effect "
        f"(the true effect everywhere in B is negative), got {info['diff_pp']:+.3f} pp"
    )
assert seg_b["reversal_flagged"], (
    "dataset B's pooled-positive-but-every-segment-negative pattern must be flagged, not silently reported"
)
assert set(seg_b["reversed_segments"]) == set(seg_b["segments"]), (
    "every segment in B is expected to be listed as reversed"
)

print("07_segment_analysis.py: every assertion held.")
