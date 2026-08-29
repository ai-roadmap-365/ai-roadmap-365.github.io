"""Section 7 — as the dimension grows, random vectors become nearly orthogonal.

Real embeddings do not have four components. They have hundreds or thousands.
Something happens in that space which has no analogue in two or three
dimensions, and which is worth measuring rather than being told:

  * two random directions become almost perpendicular, so almost every pair of
    unrelated things scores near 0;
  * the distances between random points bunch up, so the nearest and the
    furthest point in a random cloud stop being very different.

Both are measured here with a seeded generator, so the numbers below are
reproducible: numpy.random.default_rng(103) on numpy 2.5.2. Re-run it and you
get the same values. Change the seed and the numbers move a little; the shape
of the result does not.

The vectors are drawn from a standard normal distribution, which is the usual
choice because it gives a direction that is uniform over the sphere. Drawing
each component uniformly from a box would bias the directions towards the
corners.

Run from the examples directory:

    python3 07_curse_of_dimensionality.py
"""

from __future__ import annotations

import math

import numpy as np

SEED = 103
PAIRS = 2000
DIMENSIONS = (2, 3, 8, 32, 128, 512, 2048, 8192)


def exact_mean_abs_cos(dimension: int) -> float:
    """The exact mean of |cos| for two independent random directions in d dims.

        E|cos| = gamma(d/2) / (sqrt(pi) * gamma((d+1)/2))

    Two values are checkable by hand and both come out of this expression:
    in 2 dimensions the angle is uniform over the circle so the answer is
    2/pi = 0.63662, and in 3 dimensions the cosine itself is uniform over
    -1 to 1 so the answer is exactly 0.5.
    """
    return math.exp(
        math.lgamma(dimension / 2)
        - 0.5 * math.log(math.pi)
        - math.lgamma((dimension + 1) / 2)
    )


def cosine_rows(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cosine similarity of matching rows of two arrays, vectorised."""
    numerator = np.einsum("ij,ij->i", a, b)
    denominator = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
    return np.clip(numerator / denominator, -1.0, 1.0)


def measure() -> list[dict[str, float]]:
    rng = np.random.default_rng(SEED)
    rows = []
    for dimension in DIMENSIONS:
        a = rng.standard_normal((PAIRS, dimension))
        b = rng.standard_normal((PAIRS, dimension))
        cosines = cosine_rows(a, b)
        angles = np.degrees(np.arccos(cosines))
        rows.append(
            {
                "dimension": dimension,
                "mean_abs_cos": float(np.mean(np.abs(cosines))),
                "max_abs_cos": float(np.max(np.abs(cosines))),
                "mean_angle": float(np.mean(angles)),
                "std_angle": float(np.std(angles)),
                "exact": exact_mean_abs_cos(dimension),
                "asymptotic": math.sqrt(2.0 / (math.pi * dimension)),
                "frac_within_10_deg": float(np.mean(np.abs(angles - 90.0) < 10.0)),
            }
        )
    return rows


def show_orthogonality(rows) -> None:
    print(f"Mean |cosine| between {PAIRS} random vector pairs, by dimension")
    print(f"(numpy.random.default_rng({SEED}), standard normal components)")
    print()
    header = (f"  {'dimension':>10}{'mean |cos|':>13}{'exact':>10}"
              f"{'sqrt(2/(pi d))':>16}{'max |cos|':>12}{'mean angle':>13}"
              f"{'sd of angle':>13}{'within 10 deg':>15}")
    print(header)
    print("  " + "-" * (len(header) - 2))
    for row in rows:
        print(f"  {row['dimension']:>10}{row['mean_abs_cos']:>13.4f}"
              f"{row['exact']:>10.4f}{row['asymptotic']:>16.4f}"
              f"{row['max_abs_cos']:>12.4f}"
              f"{row['mean_angle']:>13.2f}{row['std_angle']:>13.2f}"
              f"{row['frac_within_10_deg'] * 100:>14.1f}%")
    print()

    first, last = rows[0], rows[-1]
    print(f"  From dimension {first['dimension']} to dimension {last['dimension']},"
          f" the mean absolute cosine")
    print(f"  fell from {first['mean_abs_cos']:.4f} to {last['mean_abs_cos']:.4f}"
          f" — a factor of {first['mean_abs_cos'] / last['mean_abs_cos']:.0f}.")
    print(f"  The fraction of pairs within 10 degrees of a right angle rose from")
    print(f"  {first['frac_within_10_deg'] * 100:.1f}% to"
          f" {last['frac_within_10_deg'] * 100:.1f}%.")
    print()

    for earlier, later in zip(rows, rows[1:]):
        assert later["mean_abs_cos"] < earlier["mean_abs_cos"], (earlier, later)
    assert rows[-1]["mean_abs_cos"] < 0.02

    worst_exact = max(
        abs(row["mean_abs_cos"] - row["exact"]) / row["exact"] for row in rows
    )
    worst_asymptotic = max(
        abs(row["exact"] - row["asymptotic"]) / row["exact"] for row in rows
    )
    print("  Two predictions sit beside the measurement, and the difference")
    print("  between them is worth a paragraph. The 'exact' column is")
    print("  gamma(d/2) / (sqrt(pi) gamma((d+1)/2)), the true mean of |cos| for")
    print("  two independent random directions. The last column is the")
    print("  approximation sqrt(2 / (pi d)), which is the one usually quoted.")
    print()
    print(f"  The measurement matches the exact value to within"
          f" {worst_exact * 100:.1f}% at every")
    print(f"  dimension, on {PAIRS} pairs. The approximation is off by up to"
          f" {worst_asymptotic * 100:.0f}%")
    print("  at the small dimensions — it is a large-d limit, and at d = 2 and")
    print("  d = 3 it simply is not the right number. Two hand-checkable cases")
    print("  settle which column to trust: in 2 dimensions the angle is uniform")
    print("  around the circle so the mean of |cos| is 2/pi = 0.63662, and in 3")
    print("  dimensions the cosine itself is uniform from -1 to 1 so the mean is")
    print("  exactly 0.5. The exact column gives both; the approximation gives")
    print("  neither; the measurement agrees with the exact column. This is a")
    print("  small thing, and it is the habit that matters: when a run and a")
    print("  quoted formula disagree, find out which one is answering your")
    print("  question before assuming the run is wrong.")
    print()
    for row in rows:
        assert abs(row["mean_abs_cos"] - row["exact"]) / row["exact"] < 0.05
    assert abs(exact_mean_abs_cos(2) - 2 / math.pi) < 1e-12
    assert abs(exact_mean_abs_cos(3) - 0.5) < 1e-12
    print("  None of that changes the headline, which is the first column")
    print("  falling towards zero as the dimension grows.")
    print()


def show_distance_concentration() -> None:
    print("The second half of the curse: distances bunch up")
    print()
    rng = np.random.default_rng(SEED + 1)
    points = 500
    header = (f"  {'dimension':>10}{'nearest':>12}{'furthest':>12}"
              f"{'ratio':>10}{'spread / mean':>16}")
    print(header)
    print("  " + "-" * (len(header) - 2))
    ratios = []
    for dimension in DIMENSIONS:
        cloud = rng.standard_normal((points, dimension))
        query = rng.standard_normal(dimension)
        distances = np.linalg.norm(cloud - query, axis=1)
        nearest = float(distances.min())
        furthest = float(distances.max())
        ratio = furthest / nearest
        spread = float(distances.std() / distances.mean())
        ratios.append(ratio)
        print(f"  {dimension:>10}{nearest:>12.4f}{furthest:>12.4f}"
              f"{ratio:>10.4f}{spread:>16.4f}")
    print()
    print(f"  In {DIMENSIONS[0]} dimensions the furthest of {points} random points")
    print(f"  is {ratios[0]:.1f} times as far as the nearest. In"
          f" {DIMENSIONS[-1]} dimensions it is {ratios[-1]:.2f} times as far.")
    print("  'Nearest neighbour' still has an answer, but the answer stops being")
    print("  meaningfully nearer than everything else, and small errors in the")
    print("  vectors start deciding the winner.")
    print()
    assert ratios[-1] < ratios[0]
    assert ratios[-1] < 1.5


def show_what_it_means() -> None:
    print("What this changes about reading a similarity score")
    print()
    print("  A cosine similarity of 0.3 is a strong signal in 1000 dimensions")
    print("  and unremarkable in 2, because in 1000 dimensions two unrelated")
    print("  things score near 0 and almost nothing lands at 0.3 by accident.")
    print("  The table above is the calibration: in this run at dimension 512")
    print("  the mean |cos| between unrelated pairs was already under 0.04.")
    print()
    print("  Three practical consequences, in order of how often they bite:")
    print()
    print("  1. Never read a raw similarity score without knowing the")
    print("     dimension. 'Above 0.8 means relevant' is a claim about one")
    print("     model in one space, not a general fact.")
    print("  2. Calibrate against your own data. Score a few hundred pairs you")
    print("     know are unrelated, look at the distribution, and set the")
    print("     threshold from that rather than from a number in a blog post.")
    print("  3. Expect exact nearest-neighbour search to stop paying for")
    print("     itself as the dimension grows. When the nearest point is barely")
    print("     nearer than the tenth nearest, an approximate index that is")
    print("     usually right is a good trade — which is what real vector")
    print("     databases do, and why they are called approximate.")
    print()


def main() -> int:
    rows = measure()
    show_orthogonality(rows)
    show_distance_concentration()
    show_what_it_means()
    print("07_curse_of_dimensionality.py: every assertion held.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
