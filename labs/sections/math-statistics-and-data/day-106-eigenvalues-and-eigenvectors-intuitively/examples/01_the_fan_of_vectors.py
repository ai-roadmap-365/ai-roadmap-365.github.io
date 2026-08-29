"""Exercise 1 — most vectors get knocked off their line. A few do not.

Run from inside examples/:

    ../.venv/bin/python3 01_the_fan_of_vectors.py

No symbols, no equation, no theory. Take twenty-four directions spread evenly
around the circle, apply the matrix to each one, and measure how far each
output has swung away from its input. Then look at the column of numbers and
notice that two of them are zero.
"""

from __future__ import annotations

import numpy as np

from dataset import A, A_EIGEN_ANGLES_DEG
from eigen import deviation_degrees, direction_degrees, eigen_lines_by_sweep, sweep_deviations

SCRIPT = "01_the_fan_of_vectors.py"


def main() -> None:
    print(f"{SCRIPT}")
    print("=" * 72)
    print()
    print("The matrix, which is just a transformation that moves the grid:")
    print()
    print("    A = [[4, 1],")
    print("         [2, 3]]")
    print()

    # ---------------------------------------------------------------- 1
    print("1. Twenty-four directions, one every 15 degrees, each one a unit vector.")
    print("   For each: where it points, where its output points, and how far")
    print("   apart those two directions are.")
    print()
    print("   in (deg)   out (deg)   swung by (deg)   length in -> out")
    print("   " + "-" * 60)

    zero_deviation = []
    for angle in range(0, 360, 15):
        radians = np.radians(angle)
        v = np.array([np.cos(radians), np.sin(radians)])
        out = A @ v
        swing = deviation_degrees(v, out)
        length = float(np.linalg.norm(out))
        marker = "   <-- kept its direction" if swing < 1e-9 else ""
        print(
            f"   {angle:6d}     {direction_degrees(out):7.3f}     {swing:9.4f}"
            f"        1.000 -> {length:5.3f}{marker}"
        )
        if swing < 1e-9:
            zero_deviation.append(angle)

    print()
    print(f"   Directions that came back on their own line: {zero_deviation}")
    print("   45 and 225 are the same line, pointing opposite ways along it.")
    print("   So out of twenty-four directions, ONE line survived.")
    print()
    assert zero_deviation == [45, 225], zero_deviation

    # ---------------------------------------------------------------- 2
    print("2. But look again at the column. It dips towards zero twice, not once.")
    print("   Around 45 degrees it reaches zero exactly. Around 120 degrees it")
    print("   gets down to 5.36 and climbs again — so the true minimum is")
    print("   somewhere between the sample points, and the coarse fan stepped")
    print("   right over it.")
    print()
    print("   Sweeping every thousandth of a degree from 0 to 180 instead:")
    print()

    found = eigen_lines_by_sweep(A)
    for angle in found["lines"]:
        deviation = sweep_deviations(A, [angle])[0][0]
        print(f"     a surviving line near {angle:11.6f} degrees  (deviation {deviation:.3e})")
    print()
    print(f"   Directions swept: 180,000. Directions that kept their line to")
    print(f"   within a hundredth of a degree: {found['fraction'] * 180000:.0f}, in {len(found['lines'])} separate bands.")
    print()
    print("   Two lines, not one. Only 180 degrees was swept because a line and")
    print("   its reverse are the same line, so the other half is a repeat.")
    print()
    assert found["verdict"] == "some"
    assert len(found["lines"]) == 2, found
    assert np.allclose(found["lines"], [45.0, 116.565], atol=1e-2), found

    # ---------------------------------------------------------------- 3
    print("3. Those two lines have names you can write down exactly.")
    print()
    for angle in A_EIGEN_ANGLES_DEG:
        radians = np.radians(angle)
        v = np.array([np.cos(radians), np.sin(radians)])
        out = A @ v
        stretch = float(np.linalg.norm(out)) / float(np.linalg.norm(v))
        print(f"     direction {angle:18.14f} degrees")
        print(f"       in  = [{v[0]: .6f}, {v[1]: .6f}]")
        print(f"       out = [{out[0]: .6f}, {out[1]: .6f}]")
        print(f"       swung by {deviation_degrees(v, out):.3e} degrees, stretched by {stretch:.6f}")
        print()
        assert deviation_degrees(v, out) < 1e-9

    print("   45 degrees is the direction of (1, 1). The output is 5 times longer.")
    print("   116.565... degrees is the direction of (1, -2). The output is 2 times longer.")
    print()
    print("   Check both on paper, with no decimals at all:")
    print()
    for vector in ((1.0, 1.0), (1.0, -2.0)):
        v = np.array(vector)
        out = A @ v
        factor = out[0] / v[0]
        print(f"     A @ ({v[0]:.0f}, {v[1]:.0f}) = ({out[0]:.0f}, {out[1]:.0f}) = {factor:.0f} * ({v[0]:.0f}, {v[1]:.0f})")
        assert np.allclose(out, factor * v)
    print()
    print("   That is the entire definition, arrived at by measurement:")
    print("   a vector that the matrix only STRETCHES is an eigenvector, and")
    print("   the stretch factor is its eigenvalue.")
    print()

    # ---------------------------------------------------------------- 4
    print("4. Why the zero vector is excluded, even though it fits the equation.")
    print()
    zero = np.array([0.0, 0.0])
    print(f"     A @ (0, 0) = ({(A @ zero)[0]:.0f}, {(A @ zero)[1]:.0f})")
    print("     and that equals lambda * (0, 0) for lambda = 5, for lambda = 2,")
    print("     for lambda = 1000, and for every other number there is.")
    print("     It satisfies the equation for EVERY value, so it distinguishes")
    print("     nothing, which is another way of saying it tells you nothing.")
    print("     It also has no direction to keep. So it is ruled out by")
    print("     definition, and that exclusion is doing real work rather than")
    print("     being bookkeeping.")
    print()
    assert np.allclose(A @ zero, 0.0)
    for lam in (5.0, 2.0, 1000.0, -3.5):
        assert np.allclose(A @ zero, lam * zero)

    print(f"{SCRIPT}: every assertion held.")


if __name__ == "__main__":
    main()
