"""Exercise 5 — principal component analysis is eigenvectors of a covariance matrix.

Run from inside examples/:

    ../.venv/bin/python3 05_pca_from_covariance.py

Everything so far has been about matrices that were handed to you. This is the
step that makes eigenvectors matter: build a matrix OUT OF DATA, take its
eigenvectors, and the top one is the direction the data is most spread along.

The dataset is invented, and it is stretched along a direction chosen in
advance — 30 degrees from the x-axis. Nothing in the array of coordinates
records that number. PCA has to find it, from 400 pairs of numbers, and the
whole of PCA is five lines long.
"""

from __future__ import annotations

import numpy as np

from dataset import (
    CENTRE,
    ELONGATION_DEG,
    N_POINTS,
    SPREAD_ACROSS,
    SPREAD_ALONG,
    elongation_direction,
    make_cloud,
)
from eigen import abs_cosine, covariance_matrix, direction_degrees, principal_components

SCRIPT = "05_pca_from_covariance.py"


def main() -> None:
    print(f"{SCRIPT}")
    print("=" * 72)
    print()

    cloud = make_cloud()
    truth = elongation_direction()

    # ---------------------------------------------------------------- 1
    print("1. The invented data. 400 points, deliberately cigar-shaped.")
    print()
    print(f"       shape                 {cloud.shape}")
    print(f"       first three points    {np.round(cloud[:3], 6).tolist()}")
    print(f"       column means          {np.round(cloud.mean(axis=0), 6).tolist()}")
    print(f"       built around centre   {CENTRE.tolist()}")
    print()
    print(f"   It was built by drawing a wide spread (sd {SPREAD_ALONG}) along the")
    print(f"   direction {ELONGATION_DEG} degrees, and a narrow spread (sd {SPREAD_ACROSS}) across it.")
    print("   That direction is the answer. It appears nowhere in the array.")
    print()
    print(f"       the answer, kept aside:  [{truth[0]:.6f}, {truth[1]:.6f}]  at {ELONGATION_DEG} degrees")
    print()
    assert cloud.shape == (N_POINTS, 2)

    # ---------------------------------------------------------------- 2
    print("2. Centre the data. This step is not optional and it is the one")
    print("   people skip.")
    print()
    centred = cloud - cloud.mean(axis=0)
    print(f"       means before centring  {np.round(cloud.mean(axis=0), 6).tolist()}")
    print(f"       means after centring   {np.round(centred.mean(axis=0), 12).tolist()}")
    print()
    print("   Covariance is about how the points vary AROUND THEIR OWN MEAN. Skip")
    print("   the subtraction and every product picks up the offset of the cloud")
    print("   from the origin, which here is (5, -2) and has nothing to do with")
    print("   the shape. Section 6 shows exactly how wrong the answer goes.")
    print()
    assert np.allclose(centred.mean(axis=0), 0.0, atol=1e-12)

    # ---------------------------------------------------------------- 3
    print("3. The covariance matrix, from scratch and then from NumPy.")
    print()
    print("       C = (Xc.T @ Xc) / (n - 1)")
    print()
    covariance = covariance_matrix(cloud)
    print("   from scratch:")
    for row in covariance:
        print(f"       [{row[0]: .8f}  {row[1]: .8f}]")
    print()
    print("   numpy.cov(cloud, rowvar=False):")
    reference = np.cov(cloud, rowvar=False)
    for row in reference:
        print(f"       [{row[0]: .8f}  {row[1]: .8f}]")
    print()
    print(f"   identical to 1e-12? {np.allclose(covariance, reference, atol=1e-12)}")
    print()
    assert np.allclose(covariance, reference, atol=1e-12)

    print("   Read the entries. C[0][0] is how much x varies, C[1][1] is how much")
    print("   y varies, and C[0][1] is how much they vary TOGETHER — positive")
    print("   here, meaning that points to the right also tend to be higher up,")
    print("   which is what a cloud tilted upwards at 30 degrees looks like.")
    print()
    print(f"       variance of x        {covariance[0, 0]:.6f}")
    print(f"       variance of y        {covariance[1, 1]:.6f}")
    print(f"       covariance of x, y   {covariance[0, 1]:.6f}")
    print(f"       symmetric?           {np.allclose(covariance, covariance.T, atol=1e-15)}")
    print()
    print("   The symmetry is not a coincidence: entry (0,1) and entry (1,0) are")
    print("   the same sum of products written in the other order. And symmetry")
    print("   is exactly what guarantees the eigenvalues are real and the")
    print("   eigenvectors at right angles, which is why PCA always works and")
    print("   never comes back with a complex answer you have to interpret.")
    print()
    assert np.allclose(covariance, covariance.T, atol=1e-15)

    # ---------------------------------------------------------------- 4
    print("4. Take the eigenvectors. That is PCA. There is no step five.")
    print()
    variances, directions = principal_components(cloud)
    print(f"       numpy.linalg.eigh eigenvalues, sorted large to small:")
    print(f"           {np.round(variances, 8).tolist()}")
    print(f"       eigenvectors, as columns:")
    for row in directions:
        print(f"           [{row[0]: .8f}  {row[1]: .8f}]")
    print()
    top = directions[:, 0]
    second = directions[:, 1]
    print(f"       top component      [{top[0]: .8f}, {top[1]: .8f}]")
    print(f"       its direction      {direction_degrees(top):.6f} degrees")
    print(f"       the truth          {ELONGATION_DEG} degrees")
    print(f"       error              {abs(direction_degrees(top) - ELONGATION_DEG):.6f} degrees")
    print()
    similarity = abs_cosine(top, truth)
    print(f"       abs_cosine(top component, true direction) = {similarity:.10f}")
    print()
    assert similarity > 0.999
    assert abs(direction_degrees(top) - ELONGATION_DEG) < 1.0

    print("   Found, from 400 pairs of coordinates and nothing else.")
    print()
    print("   And note the SIGN of what came back:")
    print(f"       top component  [{top[0]: .6f}, {top[1]: .6f}]")
    print(f"       true direction [{truth[0]: .6f}, {truth[1]: .6f}]")
    if float(np.dot(top, truth)) < 0:
        print("       They point OPPOSITE ways along the same line. numpy.allclose")
        print(f"       says {np.allclose(top, truth)}, and the answer is nonetheless exactly right.")
        print("       A principal component names an AXIS, not an arrow, and any")
        print("       code that cares which end is which has a bug waiting.")
    print()
    assert np.dot(top, truth) < 0  # observed: eigh returned the reversed sign here

    # ---------------------------------------------------------------- 5
    print("5. What the eigenVALUES mean here: variance along each axis.")
    print()
    print(f"       eigenvalue 1   {variances[0]:.6f}   sqrt = {np.sqrt(variances[0]):.6f}   (built with sd {SPREAD_ALONG})")
    print(f"       eigenvalue 2   {variances[1]:.6f}   sqrt = {np.sqrt(variances[1]):.6f}   (built with sd {SPREAD_ACROSS})")
    print()
    print("   The eigenvalue IS the variance along its own eigenvector, so its")
    print("   square root is the standard deviation — and both come back close")
    print("   to the numbers the cloud was built with. Not exactly equal: 400")
    print("   samples estimate a spread, they do not reproduce it.")
    print()
    proportion = variances / variances.sum()
    print(f"       proportion of variance explained: {np.round(proportion, 8).tolist()}")
    print(f"       the first component alone carries {100 * proportion[0]:.4f}% of it")
    print()
    print("   That is the sentence behind every 'we reduced 768 dimensions to 50'")
    print("   claim you will read: sort the eigenvalues, keep the ones that add")
    print("   up to enough of the total, and throw the rest away.")
    print()
    assert proportion[0] > 0.97
    assert abs(np.sqrt(variances[0]) - SPREAD_ALONG) < 0.2
    assert abs(np.sqrt(variances[1]) - SPREAD_ACROSS) < 0.1

    print("   Check it directly: project every point onto each component and")
    print("   measure the spread of what comes out.")
    print()
    projected = centred @ directions
    print(f"       spread along component 1  {projected[:, 0].std(ddof=1):.6f}")
    print(f"       spread along component 2  {projected[:, 1].std(ddof=1):.6f}")
    print(f"       correlation between them  {np.corrcoef(projected.T)[0, 1]:.3e}")
    print()
    print("   The two projections are uncorrelated to within rounding, which is")
    print("   the other half of what PCA buys you: not just the best directions,")
    print("   but directions along which the data carries no shared information.")
    print()
    assert abs(projected[:, 0].std(ddof=1) - np.sqrt(variances[0])) < 1e-9
    assert abs(float(np.corrcoef(projected.T)[0, 1])) < 1e-12

    # ---------------------------------------------------------------- 6
    print("6. What forgetting to centre actually costs.")
    print()
    uncentred = (cloud.T @ cloud) / (N_POINTS - 1)
    bad_variances, bad_directions = np.linalg.eigh(uncentred)
    order = np.argsort(bad_variances)[::-1]
    bad_top = bad_directions[:, order][:, 0]
    print("       Xc.T @ Xc / (n-1) with NO centring:")
    for row in uncentred:
        print(f"           [{row[0]: .8f}  {row[1]: .8f}]")
    print(f"       its top eigenvector points at {direction_degrees(bad_top):.6f} degrees")
    print(f"       the correct answer is         {ELONGATION_DEG} degrees")
    print(f"       error                         {abs(direction_degrees(bad_top) - ELONGATION_DEG):.6f} degrees")
    print()
    centre_angle = float(np.degrees(np.arctan2(CENTRE[1], CENTRE[0])) % 180.0)
    bad_angle = direction_degrees(bad_top)
    print(f"       the cloud's CENTRE lies at {centre_angle:.6f} degrees from the origin")
    print(f"       distance from the uncentred answer to that:  {abs(bad_angle - centre_angle):.6f} degrees")
    print(f"       distance from the uncentred answer to the truth: {abs(bad_angle - ELONGATION_DEG):.6f} degrees")
    print()
    print("       So the uncentred answer sits close to the direction of the")
    print("       cloud's OFFSET from the origin and nowhere near its shape. That")
    print("       is what the calculation measured, because without centring the")
    print("       squared offset (5^2 + 2^2 = 29) swamps the actual spread (8.4).")
    print("       No exception, no warning, a confident wrong answer.")
    print()
    assert abs(bad_angle - ELONGATION_DEG) > 5.0
    assert abs(bad_angle - centre_angle) < abs(bad_angle - ELONGATION_DEG)

    # ---------------------------------------------------------------- 7
    print("7. Against the two NumPy routines.")
    print()
    values_eig, vectors_eig = np.linalg.eig(covariance)
    print(f"       numpy.linalg.eig  values {values_eig}  dtype {values_eig.dtype}")
    values_eigh, vectors_eigh = np.linalg.eigh(covariance)
    print(f"       numpy.linalg.eigh values {values_eigh}  dtype {values_eigh.dtype}")
    print()
    print("   Same numbers, different packaging. eigh knows the input is")
    print("   symmetric, so it returns float64 in ascending order; eig does not")
    print("   assume it, so it returns complex128 unordered. For a covariance")
    print("   matrix — always symmetric, by construction — eigh is the right")
    print("   call every time.")
    print()
    eig_top = vectors_eig.real[:, int(np.argmax(values_eig.real))]
    print(f"       eig  top component, abs_cosine with the truth  {abs_cosine(eig_top, truth):.10f}")
    print(f"       eigh top component, abs_cosine with the truth  {abs_cosine(top, truth):.10f}")
    print()
    assert abs_cosine(eig_top, truth) > 0.999
    assert np.allclose(np.sort(values_eig.real), np.sort(values_eigh), atol=1e-12)

    print("   The AI connection, in one line: replace this 2-column cloud with a")
    print("   matrix of 768-dimensional sentence embeddings and nothing about")
    print("   the method changes. The covariance matrix becomes 768 by 768, its")
    print("   top eigenvectors are the directions those embeddings actually vary")
    print("   along, and the eigenvalues tell you how many of the 768 dimensions")
    print("   are carrying real information rather than noise.")
    print()

    print(f"{SCRIPT}: every assertion held.")


if __name__ == "__main__":
    main()
