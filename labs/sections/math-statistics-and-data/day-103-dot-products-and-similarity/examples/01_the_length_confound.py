"""Section 1 — Euclidean distance answers the wrong question about text.

Day 99 measured how far apart two articles were with Euclidean distance, and
that worked well enough that it was easy to miss what it was actually
measuring. Here is the miss, in one number.

Take roast-chicken and write it again at twice the length. Same subject, same
emphasis, every count doubled. Euclidean distance says the doubled copy is
further from the original than an article about race-day nutrition is — which
is mostly about running.

Nothing is wrong with the arithmetic. The question was wrong. "How far apart
are these two points" is not the same question as "are these two articles
about the same thing", and for text they have different answers.

Run from the examples directory:

    python3 01_the_length_confound.py
"""

from __future__ import annotations

from catalogue import CATALOGUE, FEATURES, LONG_ROAST_CHICKEN
from similarity import cosine_similarity, euclidean_distance, l2_norm, normalise

TOL = 1e-12


def show_the_two_articles() -> None:
    short = CATALOGUE["roast-chicken"]
    print("The same article, written twice as long")
    print()
    header = f"  {'article':<26}" + "".join(f"{f:>10}" for f in FEATURES) + f"{'|v|':>10}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    print(f"  {'roast-chicken':<26}" + "".join(f"{n:>10}" for n in short)
          + f"{l2_norm(short):>10.4f}")
    print(f"  {'roast-chicken (2x length)':<26}"
          + "".join(f"{n:>10}" for n in LONG_ROAST_CHICKEN)
          + f"{l2_norm(LONG_ROAST_CHICKEN):>10.4f}")
    print()
    print("  Every count doubled. The writer said the same things, twice each.")
    print()


def show_the_failure() -> None:
    short = CATALOGUE["roast-chicken"]
    rival = CATALOGUE["race-day-nutrition"]

    d_long = euclidean_distance(short, LONG_ROAST_CHICKEN)
    d_rival = euclidean_distance(short, rival)

    print("Euclidean distance, worked out in full")
    print()
    diff_long = [a - b for a, b in zip(short, LONG_ROAST_CHICKEN)]
    print("  roast-chicken vs its own doubled copy")
    print(f"      {short} - {LONG_ROAST_CHICKEN} = {diff_long}")
    print(f"      squares: {' + '.join(str(d * d) for d in diff_long)}"
          f" = {sum(d * d for d in diff_long)}")
    print(f"      sqrt({sum(d * d for d in diff_long)}) = {d_long:.4f}")
    print()
    diff_rival = [a - b for a, b in zip(short, rival)]
    print("  roast-chicken vs race-day-nutrition")
    print(f"      {short} - {rival} = {diff_rival}")
    print(f"      squares: {' + '.join(str(d * d) for d in diff_rival)}"
          f" = {sum(d * d for d in diff_rival)}")
    print(f"      sqrt({sum(d * d for d in diff_rival)}) = {d_rival:.4f}")
    print()
    print("  So Euclidean distance says the doubled copy of roast-chicken")
    print(f"  ({d_long:.4f}) is FURTHER from roast-chicken than an article")
    print(f"  about race-day nutrition is ({d_rival:.4f}).")
    print()
    assert d_long > d_rival, "the confound should put the doubled copy further away"

    print("  There is a tidy reason the first number came out the way it did.")
    print("  Doubling a vector v gives 2v, and the difference is 2v - v = v, so")
    print("  the distance between an article and its doubled copy is exactly the")
    print(f"  article's own length: |v| = {l2_norm(short):.4f}. Longer articles are")
    print("  punished harder, which is the opposite of what a search should do.")
    print()


def show_the_fix() -> None:
    short = CATALOGUE["roast-chicken"]
    rival = CATALOGUE["race-day-nutrition"]

    cos_long = cosine_similarity(short, LONG_ROAST_CHICKEN)
    cos_rival = cosine_similarity(short, rival)

    print("Cosine similarity, on exactly the same numbers")
    print()
    print(f"  cos(roast-chicken, its doubled copy)   = {cos_long:.10f}")
    print(f"  cos(roast-chicken, race-day-nutrition) = {cos_rival:.10f}")
    print()
    print("  1.0 means the angle between them is zero: the two vectors point")
    print("  in exactly the same direction. They are the same article, and the")
    print("  measure says so.")
    print()
    assert abs(cos_long - 1.0) < TOL, "a scaled copy must have cosine similarity 1"
    assert cos_rival < cos_long

    print("  Why it is exactly 1 rather than nearly 1: cosine similarity")
    print("  divides by both lengths, so scaling either vector by a positive")
    print("  number multiplies the top and the bottom by the same factor and")
    print("  cancels. Here is that cancellation with the real numbers:")
    print()
    dot_long = sum(a * b for a, b in zip(short, LONG_ROAST_CHICKEN))
    print(f"      dot = 9*18 + 0*0 + 1*2 + 0*0 = {dot_long}")
    print(f"      |v|  = {l2_norm(short):.6f}")
    print(f"      |2v| = {l2_norm(LONG_ROAST_CHICKEN):.6f}"
          f"  (exactly twice {l2_norm(short):.6f})")
    print(f"      {dot_long} / ({l2_norm(short):.6f} * "
          f"{l2_norm(LONG_ROAST_CHICKEN):.6f}) = {cos_long:.10f}")
    print()

    unit_short = normalise(short)
    unit_long = normalise(LONG_ROAST_CHICKEN)
    print("  The same thing said with unit vectors. Normalise both — divide each")
    print("  by its own length — and they land on the identical point:")
    print()
    print(f"      unit(roast-chicken)   = [{', '.join(f'{x:.6f}' for x in unit_short)}]")
    print(f"      unit(doubled copy)    = [{', '.join(f'{x:.6f}' for x in unit_long)}]")
    print(f"      distance between them = "
          f"{euclidean_distance(unit_short, unit_long):.10f}")
    print()
    assert euclidean_distance(unit_short, unit_long) < TOL


def show_the_whole_catalogue() -> None:
    short = CATALOGUE["roast-chicken"]
    print("Both measures against roast-chicken, whole catalogue, doubled copy included")
    print()
    rows = dict(CATALOGUE)
    rows["roast-chicken (2x)"] = LONG_ROAST_CHICKEN
    header = f"  {'article':<24}{'Euclidean':>12}{'cosine':>12}{'agrees?':>10}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    by_euclid = sorted(rows, key=lambda k: euclidean_distance(short, rows[k]))
    by_cosine = sorted(rows, key=lambda k: -cosine_similarity(short, rows[k]))
    for label, vector in rows.items():
        agrees = by_euclid.index(label) == by_cosine.index(label)
        print(f"  {label:<24}{euclidean_distance(short, vector):>12.4f}"
              f"{cosine_similarity(short, vector):>12.4f}{str(agrees):>10}")
    print()
    print(f"  ranked by Euclidean : {', '.join(by_euclid)}")
    print(f"  ranked by cosine    : {', '.join(by_cosine)}")
    print()
    print("  The two rankings disagree on RAW counts, and they disagree in the")
    print("  place that matters: cosine puts the doubled copy joint first,")
    print("  Euclidean puts it fourth. Section 4 shows that once every vector is")
    print("  normalised the two measures agree completely — the disagreement is")
    print("  entirely about magnitude.")
    print()
    assert by_euclid != by_cosine, "the whole point is that raw rankings differ"
    assert by_cosine[0] in ("roast-chicken", "roast-chicken (2x)")


def main() -> int:
    show_the_two_articles()
    show_the_failure()
    show_the_fix()
    show_the_whole_catalogue()
    print("01_the_length_confound.py: every assertion held.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
