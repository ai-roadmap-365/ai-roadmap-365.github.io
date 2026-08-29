"""Exercise 4 — apply the matrix over and over and watch a direction win.

Run from inside examples/:

    ../.venv/bin/python3 04_power_method.py

Multiply a random vector by A. Then multiply the answer by A. Then again.
Nothing here is clever, and after twenty-five rounds you have found the
dominant eigenvector to ten decimal places.

That algorithm has a name — the power method — and it is not a toy. It is
where PageRank came from, it is what an implicitly restarted Arnoldi
iteration is a sophisticated version of, and it is how you find the leading
eigenvector of a matrix far too large to factorise, because it never needs the
matrix itself, only the ability to multiply by it.
"""

from __future__ import annotations

import numpy as np

from dataset import (
    A,
    A_EIGEN_ANGLES_DEG,
    A_EIGENVALUES,
    A_EIGENVECTORS,
    SYMMETRIC,
    power_method_start,
)
from eigen import abs_cosine, direction_degrees, power_method, rayleigh_quotient

SCRIPT = "04_power_method.py"

TOL = 1e-9


def main() -> None:
    print(f"{SCRIPT}")
    print("=" * 72)
    print()

    start = power_method_start()
    dominant = np.array(A_EIGENVECTORS[0])

    # ---------------------------------------------------------------- 1
    print("1. Why repeated multiplication should work at all.")
    print()
    print("   Write the starting vector as a mixture of the two eigenvectors:")
    print()
    basis = np.column_stack([np.array(A_EIGENVECTORS[0]), np.array(A_EIGENVECTORS[1])])
    weights = np.linalg.solve(basis, start)
    print(f"       v0 = [{start[0]: .6f}, {start[1]: .6f}]")
    print(f"          = {weights[0]: .6f} * (1, 1)  +  {weights[1]: .6f} * (1, -2)")
    reconstructed = weights[0] * basis[:, 0] + weights[1] * basis[:, 1]
    print(f"       check: that mixture is [{reconstructed[0]: .6f}, {reconstructed[1]: .6f}]")
    print()
    assert np.allclose(reconstructed, start, atol=1e-12)

    print("   Now apply A. It does not mix the ingredients: it multiplies each")
    print("   one by its own eigenvalue, because that is what an eigenvector IS.")
    print()
    print("       A^k v0 = c1 * 5^k * (1, 1)  +  c2 * 2^k * (1, -2)")
    print()
    print("   So the (1, 1) ingredient grows by 5 each round and the (1, -2)")
    print("   ingredient grows by 2. After k rounds the second is smaller than")
    print("   the first by a factor of (2/5)^k, which goes to nothing:")
    print()
    for k in (1, 5, 10, 20, 25):
        print(f"       k = {k:2d}:  (2/5)^k = {(0.4 ** k):.3e}")
    print()
    print("   Nothing needed to be eliminated. The dominant direction simply")
    print("   outgrew the other one, and that is the whole idea.")
    print()

    # ---------------------------------------------------------------- 2
    print("2. Watch it happen, one iteration at a time.")
    print()
    print("   The starting vector is drawn from a seeded random generator, on")
    print("   purpose: the claim is that ALMOST ANY start converges, so a start")
    print("   chosen to work would prove nothing.")
    print()
    print(f"       v0 = [{start[0]: .6f}, {start[1]: .6f}], pointing at {direction_degrees(start):.6f} degrees")
    print(f"       target: the eigen-line at {direction_degrees(dominant):.6f} degrees, eigenvalue {A_EIGENVALUES[0]:.0f}")
    print()
    print("    k    direction (deg)   Rayleigh quotient   off target (deg)")
    print("   " + "-" * 62)
    v = start.copy()
    for k in range(0, 13):
        quotient = rayleigh_quotient(A, v)
        off = float(np.degrees(np.arccos(min(1.0, abs_cosine(v, dominant)))))
        print(f"   {k:2d}     {direction_degrees(v):11.6f}      {quotient:12.8f}      {off:10.6f}")
        w = A @ v
        v = w / np.linalg.norm(w)
    print()
    print("   The direction crawls in from 20 degrees and settles on 45, and the")
    print("   Rayleigh quotient — (v . A v) / (v . v), the best single number to")
    print("   call the eigenvalue for a given v — settles on 5 alongside it.")
    print()
    print("   The textbook claim about the Rayleigh quotient is that its error is")
    print("   the SQUARE of the vector's, so it converges twice as fast. Measure")
    print("   it rather than repeat it, because on this matrix it is not true.")
    print()
    print("      k   angle error (rad)   quotient error   ratio to angle   to angle^2")
    print("   " + "-" * 72)
    v = start.copy()
    for k in range(1, 9):
        w = A @ v
        v = w / np.linalg.norm(w)
        angle = float(np.arccos(min(1.0, abs_cosine(v, dominant))))
        error = abs(rayleigh_quotient(A, v) - 5.0)
        print(f"   {k:3d}      {angle:.6e}     {error:.6e}     {error / angle:10.6f}   {error / angle**2:10.2f}")
    print()
    print(f"   The ratio to the ANGLE settles on 1.0. The ratio to the angle")
    print(f"   SQUARED runs away. On A the Rayleigh quotient converges linearly,")
    print(f"   at exactly the same rate as the vector, and buys nothing.")
    print()
    print("   Now the same measurement on the symmetric matrix [[2, 1], [1, 2]],")
    print("   whose dominant eigenvalue is 3:")
    print()
    print("      k   angle error (rad)   quotient error   ratio to angle   to angle^2")
    print("   " + "-" * 72)
    v = start.copy()
    symmetric_target = np.array([1.0, 1.0])
    for k in range(1, 9):
        w = SYMMETRIC @ v
        v = w / np.linalg.norm(w)
        angle = float(np.arccos(min(1.0, abs_cosine(v, symmetric_target))))
        error = abs(rayleigh_quotient(SYMMETRIC, v) - 3.0)
        print(f"   {k:3d}      {angle:.6e}     {error:.6e}     {error / angle:10.6f}   {error / angle**2:10.4f}")
    print()
    print("   There the ratio to the angle squared locks onto 2.0000 and stays,")
    print("   which is textbook quadratic convergence.")
    print()
    print("   So the textbook claim is right, and it has a condition attached")
    print("   that is easy to drop: the quadratic result needs the eigenvectors")
    print("   to be at right angles, which SYMMETRY guarantees and A does not")
    print("   have. A is not symmetric — 1 in one corner and 2 in the other —")
    print("   so its eigen-lines at 45 and 116.6 degrees meet at 71.6 degrees,")
    print("   not 90, and the speed-up does not apply.")
    print()
    angle_between = A_EIGEN_ANGLES_DEG[1] - A_EIGEN_ANGLES_DEG[0]
    print(f"       angle between A's two eigen-lines: {angle_between:.4f} degrees")
    print(f"       angle between the symmetric matrix's:  90.0000 degrees")
    print()
    assert abs(angle_between - 71.565051) < 1e-4

    # ---------------------------------------------------------------- 3
    print("3. Run it to convergence and report the count.")
    print()
    result = power_method(A, start, tol=1e-10)
    print(f"       tolerance          1e-10 on the distance between successive unit vectors")
    print(f"       iterations         {result['iterations']}")
    print(f"       converged          {result['converged']}")
    print(f"       final change       {result['change']:.6e}")
    print(f"       vector             [{result['vector'][0]: .12f}, {result['vector'][1]: .12f}]")
    print(f"       direction          {direction_degrees(result['vector']):.12f} degrees")
    print(f"       eigenvalue         {result['eigenvalue']:.12f}")
    print(f"       abs_cosine with (1, 1)  {abs_cosine(result['vector'], dominant):.15f}")
    print()
    assert result["converged"]
    assert result["iterations"] == 25
    assert abs_cosine(result["vector"], dominant) > 1.0 - 1e-12
    assert abs(result["eigenvalue"] - 5.0) < 1e-9

    # ---------------------------------------------------------------- 4
    print("4. The convergence RATE is the eigenvalue ratio, and you can measure it.")
    print()
    print("   Theory says the error should shrink by |lambda2 / lambda1| = 2/5 =")
    print("   0.4 each round. Divide each step's change by the previous one:")
    print()
    print("      k    change        ratio to previous")
    print("   " + "-" * 44)
    history = result["history"]
    for index in range(4, 14):
        ratio = history[index] / history[index - 1]
        print(f"     {index + 1:3d}   {history[index]:.6e}     {ratio:.6f}")
    print()
    final_ratio = history[13] / history[12]
    print(f"   Measured ratio at step 14: {final_ratio:.6f}. Predicted: {2 / 5:.6f}.")
    print("   The algorithm is telling you the SECOND eigenvalue through the")
    print("   speed at which it finds the first one.")
    print()
    assert abs(final_ratio - 0.4) < 1e-3

    print("   That also tells you when the power method is a bad idea. If the")
    print("   two largest eigenvalues are close, the ratio is near 1 and")
    print("   convergence is glacial. Here is the same code on a matrix whose")
    print("   eigenvalues are 5 and 4.9:")
    print()
    slow = np.array([[5.0, 0.0], [0.0, 4.9]])
    slow_result = power_method(slow, np.array([0.6, 0.8]), tol=1e-10)
    print(f"       eigenvalue ratio 4.9 / 5 = {4.9 / 5:.4f}")
    print(f"       iterations to the same 1e-10 tolerance: {slow_result['iterations']}")
    print(f"       compared with {result['iterations']} for the ratio 0.4 matrix")
    print()
    assert slow_result["iterations"] > 200
    print("   And if they are exactly equal in magnitude the method does not")
    print("   converge at all, because there is no single dominant direction to")
    print("   converge to.")
    print()

    # ---------------------------------------------------------------- 5
    print("5. Why normalise at all? Because of what happens if you do not.")
    print()
    v = start.copy()
    lengths: dict[int, float] = {}
    print("      k    length of A^k v0")
    print("   " + "-" * 34)
    with np.errstate(over="ignore"):
        for k in range(0, 401):
            if k in (0, 10, 50, 100, 200, 300, 400):
                lengths[k] = float(np.linalg.norm(v))
                print(f"     {k:3d}    {lengths[k]:.6e}")
            v = A @ v
    print()
    print("   The direction was right after twenty-five rounds. The LENGTH keeps")
    print("   multiplying by five, and float64 stops at about 1.8e308:")
    print()
    print(f"       largest float64:      {np.finfo(np.float64).max:.6e}")
    print(f"       length after 200:     {lengths[200]:.6e}  (still fine)")
    print(f"       length after 300:     {lengths[300]:.6e}")
    print()
    assert np.isfinite(lengths[200]) and not np.isfinite(lengths[300])
    overflow = start.copy()
    with np.errstate(over="ignore", invalid="ignore"):
        for _ in range(600):
            overflow = A @ overflow
    print(f"       after 600 un-normalised rounds:  {overflow}")
    assert not np.all(np.isfinite(overflow))

    with np.errstate(invalid="ignore"):
        recovered = overflow / np.linalg.norm(overflow)
    print(f"       and normalising it now:          {recovered}")
    assert np.all(np.isnan(recovered))
    print()
    print("       inf divided by inf is nan. The direction was correct at round")
    print("       twenty-five and is now unrecoverable, destroyed by a magnitude")
    print("       nobody asked for. Normalising each round changes no direction")
    print("       and costs one division.")
    print()

    # ---------------------------------------------------------------- 6
    print("6. Against numpy.linalg.eig, which solves the whole problem at once.")
    print()
    values, vectors = np.linalg.eig(A)
    real_values = values.real
    top = int(np.argmax(np.abs(real_values)))
    print(f"       numpy dominant eigenvalue   {real_values[top]:.12f}")
    print(f"       power method eigenvalue     {result['eigenvalue']:.12f}")
    print(f"       difference                  {abs(real_values[top] - result['eigenvalue']):.3e}")
    print()
    print(f"       numpy dominant eigenvector  [{vectors.real[0, top]: .12f}, {vectors.real[1, top]: .12f}]")
    print(f"       power method eigenvector    [{result['vector'][0]: .12f}, {result['vector'][1]: .12f}]")
    print(f"       abs_cosine between them     {abs_cosine(vectors.real[:, top], result['vector']):.15f}")
    print()
    assert abs(real_values[top] - result["eigenvalue"]) < 1e-9
    assert abs_cosine(vectors.real[:, top], result["vector"]) > 1.0 - 1e-12

    print("   Two honest points about that comparison.")
    print()
    print("   The power method found ONE eigenvector; eig found all of them, and")
    print("   for a 2x2 there is no reason at all to use anything else.")
    print()
    print("   But eig needs the matrix as an array and works on all of it. The")
    print("   power method needs only a function that computes A @ v. On a graph")
    print("   with a hundred million nodes the adjacency matrix does not fit in")
    print("   memory as an array, while multiplying by it is just a walk over the")
    print("   edges — which is why the method that looks naive here is the one")
    print("   that survives at scale.")
    print()

    print(f"{SCRIPT}: every assertion held.")


if __name__ == "__main__":
    main()
