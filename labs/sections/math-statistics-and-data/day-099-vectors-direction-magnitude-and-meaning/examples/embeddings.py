"""A tiny embedding, hand-made, so that "similar" becomes a number.

Six short articles. Four features, counted by hand: how many times the article
talks about cooking, about running, about money, and about weather. That is it.
Each article is now a list of four numbers — a vector — and the sentence
"these two articles are similar" has become "these two vectors are close",
which is a claim you can check with arithmetic.

Real embeddings are produced by a trained model and have hundreds or thousands
of components whose meanings nobody assigned by hand. Everything else is the
same: a row of numbers per item, and nearness measured with a norm.

Run from the examples directory:

    python3 embeddings.py
"""

from __future__ import annotations

from vectors import distance, l2_norm, normalise, nearest, subtract

FEATURES = ("cooking", "running", "money", "weather")

CATALOGUE = {
    "roast-chicken":      [9, 0, 1, 0],
    "slow-cooker-stew":   [8, 0, 2, 0],
    "marathon-plan":      [0, 9, 1, 2],
    "race-day-nutrition": [4, 6, 3, 0],
    "household-budget":   [1, 0, 9, 0],
    "storm-bulletin":     [0, 1, 0, 9],
}


def print_catalogue() -> None:
    print("The catalogue: one row of four numbers per article")
    print()
    header = f"{'article':<20}" + "".join(f"{f:>10}" for f in FEATURES) + f"{'|v|':>10}"
    print(header)
    print("-" * len(header))
    for label, vec in CATALOGUE.items():
        row = "".join(f"{n:>10}" for n in vec)
        print(f"{label:<20}{row}{l2_norm(vec):>10.4f}")
    print()


def print_matrix() -> None:
    labels = list(CATALOGUE)
    print("Pairwise Euclidean distance (the magnitude of the difference)")
    print()
    print(f"{'':<20}" + "".join(f"{lab[:9]:>11}" for lab in labels))
    for a in labels:
        cells = "".join(f"{distance(CATALOGUE[a], CATALOGUE[b]):>11.4f}" for b in labels)
        print(f"{a:<20}{cells}")
    print()


def print_working(a: str, b: str) -> None:
    """Show one distance in full, the way you would do it on paper."""
    u, v = CATALOGUE[a], CATALOGUE[b]
    diff = [int(x) for x in subtract(u, v)]
    squares = [d * d for d in diff]
    print(f"  {a} vs {b}")
    print(f"      {u} - {v} = {diff}")
    print(f"      squares: {' + '.join(str(s) for s in squares)} = {sum(squares)}")
    print(f"      sqrt({sum(squares)}) = {distance(u, v):.4f}")


def print_nearest() -> None:
    print("Nearest neighbour of each article, itself excluded")
    print()
    for label in CATALOGUE:
        winner, score = nearest(
            CATALOGUE[label], CATALOGUE, exclude=label
        )
        print(f"  {label:<20} -> {winner:<20} at {score:.4f}")
    print()


def print_length_effect() -> None:
    """Why normalising is so common: length is not topic."""
    print("Part 1 — the same article, three times as long")
    print()
    short = CATALOGUE["roast-chicken"]
    long_version = [3 * n for n in short]
    print(f"  short = {str(short):<16} |v| = {l2_norm(short):.4f}")
    print(f"  long  = {str(long_version):<16} |v| = {l2_norm(long_version):.4f}")
    print(f"  raw distance between them       = {distance(short, long_version):.4f}")
    print(
        "  distance after normalising both = "
        f"{distance(normalise(short), normalise(long_version)):.4f}"
    )
    print()
    print("  Raw counts put these two far apart. They are not about different")
    print("  things — one is simply longer. Normalising throws the length away")
    print("  and keeps only the direction, which is the part that carries the")
    print("  topic. The long version is the short version scaled by 3, so after")
    print("  normalising they are the same vector and the distance is 0.")
    print()

    print("Part 2 — a short note, where raw counts pick the wrong article")
    print()
    query = [1, 0, 0, 0]
    print(f"  query = {query}  (a one-line cooking note: 'roast it')")
    print()
    unit_catalogue = {label: normalise(v) for label, v in CATALOGUE.items()}
    unit_query = normalise(query)
    header = f"  {'article':<20}{'raw distance':>16}{'normalised distance':>22}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for label, vec in CATALOGUE.items():
        print(
            f"  {label:<20}{distance(query, vec):>16.4f}"
            f"{distance(unit_query, unit_catalogue[label]):>22.4f}"
        )
    raw_winner, raw_score = nearest(query, CATALOGUE)
    unit_winner, unit_score = nearest(unit_query, unit_catalogue)

    raw_order = sorted(CATALOGUE, key=lambda k: distance(query, CATALOGUE[k]))
    unit_order = sorted(
        CATALOGUE, key=lambda k: distance(unit_query, unit_catalogue[k])
    )
    print()
    print(f"  nearest on raw counts : {raw_winner} at {raw_score:.4f}")
    print(f"  nearest normalised    : {unit_winner} at {unit_score:.4f}")
    print(f"  they disagree         : {raw_winner != unit_winner}")
    print(f"  raw rank of roast-chicken        : {raw_order.index('roast-chicken') + 1}")
    print(
        f"  normalised rank of roast-chicken : "
        f"{unit_order.index('roast-chicken') + 1}"
    )
    print()
    print("  The note is purely about cooking, so roast-chicken — the article")
    print("  most purely about cooking — should win. On raw counts it comes")
    print("  third, behind slow-cooker-stew and behind race-day-nutrition,")
    print("  which is mostly about running. Nothing is wrong with the")
    print("  arithmetic. The query vector is short, so it sits near the origin,")
    print("  and raw distance from a point near the origin is dominated by how")
    print("  long each article is rather than by what it is about. Normalising")
    print("  puts every vector on the unit sphere, which deletes length from")
    print("  the comparison and leaves only direction — and direction is the")
    print("  part that carries the topic. Normalised, roast-chicken wins.")
    print()


def main() -> int:
    print_catalogue()
    print_matrix()
    print("Two of those distances, worked out in full")
    print()
    print_working("roast-chicken", "slow-cooker-stew")
    print()
    print_working("roast-chicken", "household-budget")
    print()
    print_nearest()
    print_length_effect()

    closest_pair = min(
        (
            (distance(CATALOGUE[a], CATALOGUE[b]), a, b)
            for i, a in enumerate(CATALOGUE)
            for b in list(CATALOGUE)[i + 1 :]
        )
    )
    score, a, b = closest_pair
    print(f"Closest pair in the whole catalogue: {a} and {b} at {score:.4f}")
    print()
    print("That is the entire idea behind semantic search. Turn each item into")
    print("a vector, turn the query into a vector the same way, and return the")
    print("items whose vectors are nearest. Everything after this is about")
    print("getting better vectors and searching them faster.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
