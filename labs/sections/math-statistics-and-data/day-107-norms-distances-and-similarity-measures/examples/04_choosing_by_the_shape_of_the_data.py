"""Four kinds of data, four right answers. Choose by the shape, not by habit.

Run from the `examples/` directory:

    ../.venv/bin/python3 04_choosing_by_the_shape_of_the_data.py

Grid movement, tolerance checking, categorical fields and sets. Each section
shows a case where the popular default -- Euclidean, or cosine -- is not merely
suboptimal but answers a question nobody asked.
"""

from __future__ import annotations

import catalogue
import measures
from measures import TOL

print("=" * 74)
print("1. Manhattan, Euclidean and Chebyshev on ONE displacement")
print("=" * 74)
print()

a, b = catalogue.FLOOR_FROM, catalogue.FLOOR_TO
dx, dy = b[0] - a[0], b[1] - a[1]
print(f"  A warehouse floor. Go from {a} to {b}, in metres.")
print(f"  The displacement is {dx} across and {dy} along. One pair of points.")
print()
l1 = measures.l1_distance(a, b)
l2 = measures.l2_distance(a, b)
linf = measures.linf_distance(a, b)
print(f"    L1  (Manhattan) = {l1:5.1f}   a picker walking the aisles, one axis")
print("                              at a time. There is no diagonal to walk.")
print(f"    L2  (Euclidean) = {l2:5.1f}   a drone flying it straight. This is the")
print("                              only one that is a physical length here.")
print(f"    Linf (Chebyshev)= {linf:5.1f}   a two-axis gantry whose motors run at")
print("                              the same speed AT THE SAME TIME, so the")
print("                              slower axis alone sets the finishing time.")
print()
assert (l1, l2, linf) == (14.0, 10.0, 8.0)
print("  14, 10 and 8. None is a rounding of another and none is wrong. Each")
print("  is the real cost for a different machine, and if you pick the wrong")
print("  one your route planner optimises a journey nobody takes.")
print()
print(f"  The ordering L-inf <= L2 <= L1 is guaranteed, not a coincidence:")
print("  it is the falling p-column from script 02, applied to a difference.")
assert linf <= l2 <= l1
print()

print("=" * 74)
print("2. Chebyshev, where a single worst component decides alone")
print("=" * 74)
print()
print("  A machined part with four dimensions, in millimetres. It is rejected")
print(f"  if ANY dimension is out by more than {catalogue.PART_TOLERANCE_MM} mm.")
print("  That acceptance rule is an L-infinity ball and cannot be written as")
print("  anything else.")
print()
print(f"    nominal   {catalogue.NOMINAL_PART}")
print()
header = f"    {'batch':<10}{'deviations':<32}{'L1':>8}{'L2':>8}{'L-inf':>8}  verdict"
print(header)
print("    " + "-" * (len(header) - 4))
verdicts = {}
for name, part in catalogue.MEASURED_PARTS.items():
    dev = [round(p - n, 6) for p, n in zip(part, catalogue.NOMINAL_PART)]
    d1 = measures.l1_distance(part, catalogue.NOMINAL_PART)
    d2 = measures.l2_distance(part, catalogue.NOMINAL_PART)
    di = measures.linf_distance(part, catalogue.NOMINAL_PART)
    ok = di <= catalogue.PART_TOLERANCE_MM + TOL
    verdicts[name] = ok
    shown = "[" + ", ".join(f"{v:+.2f}" for v in dev) + "]"
    print(f"    {name:<10}{shown:<32}{d1:>8.2f}{d2:>8.4f}{di:>8.2f}"
          f"  {'ACCEPT' if ok else 'REJECT'}")
print()
assert verdicts == {"batch-A": True, "batch-B": False}
print("  Read that twice. batch-A is out on all four dimensions and its total")
print("  error is nearly double batch-B's -- and batch-A is the one that")
print("  passes. Both L1 and L2 rank batch-B as the better part. Both are")
print("  answering a question the inspection department did not ask.")
print()
print("  Whenever the rule is 'no single feature may be worse than X',")
print("  the measure is Chebyshev. Averaging is not a safe default there;")
print("  it is a way of hiding one bad value behind three good ones.")
print()

print("=" * 74)
print("3. Hamming, for data with no arithmetic in it")
print("=" * 74)
print()
print("  Six categorical fields from a parts register. There is no sense in")
print("  which brass is nearer to steel than nylon is, and any measure that")
print("  subtracts one from the other has invented information.")
print()
print((f"    {'field':<10}"
       + "".join(f"{f:<12}" for f in catalogue.FIELDS)).rstrip())
print((f"    {'reference':<10}"
       + "".join(f"{v:<12}" for v in catalogue.REFERENCE_RECORD)).rstrip())
print()
for name, record in catalogue.CANDIDATE_RECORDS.items():
    marks = "".join(
        f"{(v + ' *') if v != r else v:<12}"
        for v, r in zip(record, catalogue.REFERENCE_RECORD))
    print(f"    {name:<10}{marks}".rstrip())
print()
print("    (* marks a field that differs)")
print()
print(f"    {'record':<10}{'Hamming':>10}{'normalised':>14}")
print("    " + "-" * 30)
hammings = {}
for name, record in catalogue.CANDIDATE_RECORDS.items():
    h = measures.hamming_distance(catalogue.REFERENCE_RECORD, record)
    hammings[name] = h
    print(f"    {name:<10}{h:>10}"
          f"{measures.normalised_hamming(catalogue.REFERENCE_RECORD, record):>14.4f}")
print()
assert hammings == {"part-71": 1, "part-72": 3, "part-73": 6}
print("  part-71 differs only in colour: order it. part-73 shares nothing")
print("  with the reference at all, and the number 6 says exactly that.")
print()
print("  On bits, which is where Hamming defined it in 1950 for error-")
print("  detecting codes, the same count is the number of bit flips between")
print("  two words:")
print()
print(f"    A = {''.join(str(b) for b in catalogue.FLAGS_A)}")
print(f"    B = {''.join(str(b) for b in catalogue.FLAGS_B)}")
diff_marks = "".join(
    "^" if x != y else " "
    for x, y in zip(catalogue.FLAGS_A, catalogue.FLAGS_B))
print(f"        {diff_marks}".rstrip())
flag_h = measures.hamming_distance(catalogue.FLAGS_A, catalogue.FLAGS_B)
print(f"    Hamming distance = {flag_h}")
assert flag_h == 2
print()
print("  And on bits only, Hamming coincides exactly with squared Euclidean")
print("  and with L1, because every difference is 0 or 1 and 1 squared is 1:")
print()
l1_flags = measures.l1_distance(catalogue.FLAGS_A, catalogue.FLAGS_B)
sq_flags = measures.l2_distance(catalogue.FLAGS_A, catalogue.FLAGS_B) ** 2
print(f"    L1 = {l1_flags:.1f}   squared L2 = {sq_flags:.1f}   Hamming = {flag_h}")
assert abs(l1_flags - flag_h) <= TOL and abs(sq_flags - flag_h) <= 1e-9
print()
print("  That coincidence is worth knowing and worth distrusting. It holds")
print("  for BINARY features and collapses the moment a categorical field is")
print("  encoded as 0, 1, 2 -- because then 'nylon' minus 'steel' becomes 2")
print("  and 'brass' minus 'steel' becomes 1, and you have quietly asserted")
print("  that brass is twice as similar to steel as nylon is.")
print()
mislabelled = {"steel": 0, "brass": 1, "nylon": 2}
ref_code = mislabelled[catalogue.REFERENCE_RECORD[0]]
for name in ("part-72", "part-73"):
    code = mislabelled[catalogue.CANDIDATE_RECORDS[name][0]]
    print(f"    integer-encoded material distance, reference to {name}: "
          f"{abs(code - ref_code)}")
print("    ... which is a claim about metallurgy that nobody made.")
print()

print("=" * 74)
print("4. Jaccard against cosine on the same set data")
print("=" * 74)
print()
print("  This is the one most people get wrong, because cosine is the habit.")
print()
q = catalogue.RECIPE_QUERY
print(f"  You want a recipe using: {sorted(q)}")
print()
axes = measures.vocabulary(q, *catalogue.RECIPES.values())
qv = measures.to_binary_vector(q, axes)
print(f"    {'recipe':<14}{'size':>6}{'shared':>8}{'union':>7}"
      f"{'Jaccard':>10}{'cosine':>10}")
print("    " + "-" * 55)
jac, cos = {}, {}
for name, items in catalogue.RECIPES.items():
    jac[name] = measures.jaccard_similarity(q, items)
    cos[name] = measures.cosine_similarity(
        qv, measures.to_binary_vector(items, axes))
    print(f"    {name:<14}{len(items):>6}{len(q & items):>8}"
          f"{len(q | items):>7}{jac[name]:>10.4f}{cos[name]:>10.4f}")
print()

jac_winner = max(jac, key=jac.get)
cos_winner = max(cos, key=cos.get)
print(f"    Jaccard picks {jac_winner}")
print(f"    cosine  picks {cos_winner}")
assert jac_winner == "Shortbread"
assert cos_winner == "Sachertorte"
assert jac_winner != cos_winner
print()
print("  Same two sets. Same query. Opposite answers, and both defensible.")
print()
print("    cosine  = shared / sqrt(|query| * |recipe|)"
      f"  = 4 / sqrt(4*11) = {cos['Sachertorte']:.4f}")
print("    Jaccard = shared / |union|"
      f"                   = 4 / 11        = {jac['Sachertorte']:.4f}")
print()
print("  Sachertorte contains every ingredient you named. Cosine rewards that")
print("  and charges only a square root for the seven extras. Jaccard puts")
print("  the extras in the denominator at full price, so an eleven-ingredient")
print("  cake is not a close match to a four-ingredient request even when it")
print("  is a superset of it.")
print()
print("  Which is right depends on the question:")
print("    'has it got what I asked for?'      -> cosine")
print("    'is it about the same size job?'    -> Jaccard")
print()
print("  For duplicate detection, overlapping tag sets, shingled documents and")
print("  anything where a long item must not out-rank a focused one, Jaccard")
print("  is the safer default -- and unlike cosine distance, 1 - Jaccard is a")
print("  genuine metric, which script 03 checked on all 4096 triples.")
print()
print("  One more asymmetry worth seeing. Cosine on binary data cannot fall")
print("  below Jaccard, ever, because sqrt(|a| * |b|) <= |a union b|:")
print()
pairs_checked = 0
for name, items in catalogue.RECIPES.items():
    assert cos[name] >= jac[name] - TOL
    pairs_checked += 1
    print(f"    {name:<14} cosine {cos[name]:.4f}  >=  Jaccard {jac[name]:.4f}")
assert pairs_checked == 2
print()
print("  So cosine is systematically the more generous of the two on sets.")
print("  If your relevance scores look suspiciously high, that is a candidate")
print("  explanation before you go looking for a bug.")
print()

print("04_choosing_by_the_shape_of_the_data.py: every assertion held.")
