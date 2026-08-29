"""Section 6 — a semantic search, complete, in about fifteen lines.

Everything in this file that does actual work is imported from
`similarity.py`, and the search itself is four lines:

    def search(query, catalogue, k=3):
        scored = [(label, cosine_similarity(query, v)) for label, v in catalogue.items()]
        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        return scored[:k]

That is the retrieval step of a document-answering system. Everything a real
one adds is about getting better vectors — a trained model instead of hand
counts — and about searching millions of them quickly instead of six of them
exhaustively. The comparison at the centre does not change.

Run from the examples directory:

    python3 06_semantic_search.py
"""

from __future__ import annotations

from catalogue import CATALOGUE, FEATURES, QUERIES
from similarity import (
    angle_degrees,
    cosine_similarity,
    dot,
    euclidean_distance,
    l2_norm,
    normalise_all,
    rank_by_cosine,
    rank_by_euclidean,
)

TOL = 1e-12


def search(query, catalogue, k=3):
    """The whole retrieval step. Score everything, sort, take the top k."""
    scored = [
        (label, cosine_similarity(query, vector)) for label, vector in catalogue.items()
    ]
    scored.sort(key=lambda pair: (-pair[1], pair[0]))
    return scored[:k]


def show_the_index() -> None:
    print("The index: six articles, four features, and their unit vectors")
    print()
    units = normalise_all(CATALOGUE)
    header = (f"  {'article':<20}" + "".join(f"{f:>9}" for f in FEATURES)
              + f"{'|v|':>9}   unit vector")
    print(header)
    print("  " + "-" * (len(header) - 2))
    for label, vector in CATALOGUE.items():
        unit = "[" + ", ".join(f"{x:.3f}" for x in units[label]) + "]"
        print(f"  {label:<20}" + "".join(f"{n:>9}" for n in vector)
              + f"{l2_norm(vector):>9.4f}   {unit}")
    print()
    print("  Normalising once, on the way in, is what a vector store does. After")
    print("  this every query is a dot product and there is not a square root")
    print("  left in the hot path.")
    print()
    for label, unit in units.items():
        assert abs(l2_norm(unit) - 1.0) < 1e-12, label


def run_one_query(text: str, query, expected_top: str) -> None:
    print(f"Query: \"{text}\"  ->  {query}")
    print()
    header = (f"  {'rank':<6}{'article':<22}{'a.b':>7}{'cosine':>10}"
              f"{'angle':>9}{'euclid (raw)':>15}")
    print(header)
    print("  " + "-" * (len(header) - 2))
    ranked = rank_by_cosine(query, CATALOGUE)
    for position, (label, score) in enumerate(ranked, start=1):
        vector = CATALOGUE[label]
        print(f"  {position:<6}{label:<22}{dot(query, vector):>7.0f}{score:>10.6f}"
              f"{angle_degrees(query, vector):>9.2f}"
              f"{euclidean_distance(query, vector):>15.4f}")
    print()
    top, top_score = ranked[0]
    runner, runner_score = ranked[1]
    print(f"  top result : {top} at {top_score:.6f}")
    print(f"  runner-up  : {runner} at {runner_score:.6f}")
    print(f"  margin     : {top_score - runner_score:.6f}")
    print()
    assert top == expected_top, (text, top, expected_top)

    raw_euclid = rank_by_euclidean(query, CATALOGUE)
    print("  For contrast, the same query ranked by RAW Euclidean distance:")
    print(f"    {', '.join(label for label, _ in raw_euclid)}")
    print(f"    nearest by distance: {raw_euclid[0][0]} at {raw_euclid[0][1]:.4f}")
    if raw_euclid[0][0] != top:
        print("    which is NOT the cosine winner. Raw distance is still being")
        print("    dominated by how long each article is.")
    else:
        print("    which agrees with cosine here — agreement is possible, it is")
        print("    just not guaranteed while the vectors have different lengths.")
    print()

    by_dot = sorted(
        CATALOGUE, key=lambda label: (-dot(query, CATALOGUE[label]), label)
    )
    print("  And by the RAW dot product, with no division at all:")
    print(f"    {', '.join(by_dot)}")
    print(f"    highest dot product: {by_dot[0]} at {dot(query, CATALOGUE[by_dot[0]]):.0f}")
    if by_dot[0] != top:
        print("    also NOT the cosine winner. The dot product rewards long")
        print("    articles, because a longer vector has more of everything to")
        print("    multiply. Dot product and cosine are the same ranking only")
        print("    after the vectors are normalised.")
    else:
        print("    which agrees with cosine here, but only by luck of these")
        print("    particular lengths.")
    print()


def show_top_three() -> None:
    print("The four-line search, used the way it would be used")
    print()
    for text, query in QUERIES.items():
        hits = search(query, CATALOGUE, k=3)
        print(f"  \"{text}\"")
        for position, (label, score) in enumerate(hits, start=1):
            print(f"      {position}. {label:<22}{score:.4f}")
        print()


def show_magnitude_does_not_matter() -> None:
    print("The query's own length is irrelevant, which is worth proving")
    print()
    base = QUERIES["roast it"]
    header = f"  {'query':<22}{'roast-chicken':>16}{'slow-cooker-stew':>20}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    first = None
    for factor in (1, 3, 100):
        scaled = [factor * x for x in base]
        chicken = cosine_similarity(scaled, CATALOGUE["roast-chicken"])
        stew = cosine_similarity(scaled, CATALOGUE["slow-cooker-stew"])
        print(f"  {str(scaled):<22}{chicken:>16.10f}{stew:>20.10f}")
        if first is None:
            first = (chicken, stew)
        else:
            assert abs(chicken - first[0]) < TOL
            assert abs(stew - first[1]) < TOL
    print()
    print("  Identical to ten decimal places. A one-word query and the same")
    print("  word repeated a hundred times rank the catalogue exactly the same,")
    print("  because the only thing cosine reads is the direction. Under raw")
    print("  Euclidean distance those three queries give three different")
    print("  answers, and Day 99 showed the shortest of them picking the wrong")
    print("  article.")
    print()


def main() -> int:
    show_the_index()
    run_one_query("roast it", QUERIES["roast it"], "roast-chicken")
    run_one_query(
        "training for a race and what to eat",
        QUERIES["training for a race and what to eat"],
        "race-day-nutrition",
    )
    show_top_three()
    show_magnitude_does_not_matter()
    print("06_semantic_search.py: every assertion held.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
