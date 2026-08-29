"""Exercise 6 — eig or eigh, and what the choice is actually worth.

Run from inside examples/:

    ../.venv/bin/python3 06_eig_against_eigh.py

NumPy offers four routines for this job and they are not interchangeable.
This script runs all four on the same inputs and measures the one difference
that is usually quoted without a number attached: how much faster eigh is.

Timings are measured here, on one machine, on one day. They are printed rather
than asserted, because a test that asserts milliseconds fails on somebody
else's laptop for no good reason. The SHAPES and DTYPES are asserted, because
those are properties of the routines rather than of the hardware.
"""

from __future__ import annotations

import platform
import sys
import time

import numpy as np

from dataset import A, SYMMETRIC

SCRIPT = "06_eig_against_eigh.py"

SIZE = 400
REPEATS = 5


def best_of(function, matrix, repeats: int = REPEATS) -> float:
    """Fastest of several runs, in seconds.

    The fastest run rather than the mean, because everything that makes a run
    slower — another process waking up, a page fault, the CPU changing its
    clock speed — is noise added on top. There is no source of noise that
    makes a run faster than the machine can do it, so the minimum is the
    cleanest estimate of the real cost.
    """
    timings = []
    for _ in range(repeats):
        start = time.perf_counter()
        function(matrix)
        timings.append(time.perf_counter() - start)
    return min(timings)


def main() -> None:
    print(f"{SCRIPT}")
    print("=" * 72)
    print()
    print(f"   python   {platform.python_version()}")
    print(f"   numpy    {np.__version__}")
    print(f"   platform {platform.platform()}")
    print(f"   exe      {sys.executable.rsplit('/', 3)[-1]}")
    print()

    # ---------------------------------------------------------------- 1
    print("1. The four routines, and what each one is for.")
    print()
    print("   numpy.linalg.eig      any square matrix; values AND vectors")
    print("   numpy.linalg.eigvals  any square matrix; values only")
    print("   numpy.linalg.eigh     symmetric input only; values AND vectors")
    print("   numpy.linalg.eigvalsh symmetric input only; values only")
    print()
    print("   On the symmetric matrix [[2, 1], [1, 2]]:")
    print()
    for name, function in (
        ("eig", np.linalg.eig),
        ("eigh", np.linalg.eigh),
    ):
        values, vectors = function(SYMMETRIC)
        print(f"       {name:<6} values {values}  dtype {values.dtype}")
        print(f"       {'':<6} sorted ascending? {bool(np.all(np.diff(values.real) >= 0))}")
    for name, function in (
        ("eigvals", np.linalg.eigvals),
        ("eigvalsh", np.linalg.eigvalsh),
    ):
        values = function(SYMMETRIC)
        print(f"       {name:<8} values {values}  dtype {values.dtype}")
    print()
    assert np.linalg.eig(SYMMETRIC)[0].dtype == np.complex128
    assert np.linalg.eigh(SYMMETRIC)[0].dtype == np.float64
    assert np.linalg.eigvalsh(SYMMETRIC).dtype == np.float64
    assert np.all(np.diff(np.linalg.eigh(SYMMETRIC)[0]) >= 0)

    print("   Three differences that matter in practice:")
    print()
    print("     * eigh returns float64; eig returns complex128 even when every")
    print("       eigenvalue is real. Exercise 2 covers that at length.")
    print("     * eigh returns its values sorted ascending. eig makes no")
    print("       ordering promise at all, so 'the largest eigenvalue' needs an")
    print("       argmax rather than an index.")
    print("     * eigh reads only ONE triangle of the input and assumes the")
    print("       other matches. Feed it a non-symmetric matrix and it does not")
    print("       complain — it answers a question about a different matrix.")
    print()

    # ---------------------------------------------------------------- 2
    print("2. eigh on non-symmetric input: silently the wrong answer.")
    print()
    print("   A = [[4, 1], [2, 3]] is NOT symmetric. Its real eigenvalues are 5 and 2.")
    print()
    honest = np.sort(np.linalg.eig(A)[0].real)
    wrong = np.linalg.eigh(A)[0]
    print(f"       eig  on A -> {honest}   (correct)")
    print(f"       eigh on A -> {wrong}   (no error, no warning)")
    print()
    print("   eigh took the lower triangle, [[4, ...], [2, 3]], assumed the")
    print("   upper matched it, and solved [[4, 2], [2, 3]] instead — a")
    print("   different matrix with different eigenvalues.")
    print()
    substitute = np.array([[4.0, 2.0], [2.0, 3.0]])
    print(f"       eigvalsh([[4, 2], [2, 3]]) -> {np.linalg.eigvalsh(substitute)}")
    print(f"       matches what eigh returned for A? {np.allclose(wrong, np.linalg.eigvalsh(substitute))}")
    print()
    print("   So check symmetry before reaching for eigh, or know for structural")
    print("   reasons that it holds — as it does for every covariance matrix.")
    print()
    assert not np.allclose(np.sort(wrong), honest)
    assert np.allclose(wrong, np.linalg.eigvalsh(substitute))

    # ---------------------------------------------------------------- 3
    print(f"3. What eigh is worth, measured on a {SIZE} by {SIZE} symmetric float64 matrix.")
    print()
    rng = np.random.default_rng(7)
    noise = rng.normal(size=(SIZE, SIZE))
    symmetric = (noise + noise.T) / 2.0
    assert np.allclose(symmetric, symmetric.T)

    print(f"       shape {symmetric.shape}, dtype {symmetric.dtype}, symmetric: True")
    print(f"       best of {REPEATS} runs each:")
    print()
    results = {}
    for name, function in (
        ("numpy.linalg.eig", np.linalg.eig),
        ("numpy.linalg.eigh", np.linalg.eigh),
        ("numpy.linalg.eigvals", np.linalg.eigvals),
        ("numpy.linalg.eigvalsh", np.linalg.eigvalsh),
    ):
        seconds = best_of(function, symmetric)
        results[name] = seconds
        print(f"         {name:<24} {seconds * 1000:8.2f} ms")
    print()
    ratio = results["numpy.linalg.eig"] / results["numpy.linalg.eigh"]
    print(f"       eig / eigh = {ratio:.2f}x on this run, on this machine.")
    print()
    print("   float64 on purpose. A float32 or an integer array would be a")
    print("   different measurement, and mixing them would make the number")
    print("   meaningless. Nothing here is asserted — the ratio is real but it")
    print("   is one machine on one day, and your number will differ.")
    print()
    print("   Both answers agree, which IS asserted:")
    values_eig = np.sort(np.linalg.eig(symmetric)[0].real)
    values_eigh = np.linalg.eigh(symmetric)[0]
    difference = float(np.abs(values_eig - values_eigh).max())
    print(f"       largest disagreement across all {SIZE} eigenvalues: {difference:.3e}")
    print()
    assert difference < 1e-10

    # ---------------------------------------------------------------- 4
    print("4. Everything else in this area, described honestly and NOT run here.")
    print()
    print("   None of the following is installed in this lab, and no output from")
    print("   any of them is reproduced anywhere in this day. They are described")
    print("   from their own documentation, and that is all.")
    print()
    for name, note in (
        (
            "scipy.linalg.eig / eigh",
            "the same jobs with more knobs — a generalized problem A v = lambda B v, "
            "the option to ask for only a range of eigenvalues, and a choice of "
            "LAPACK driver. Reach for it when NumPy's version does not take the "
            "argument you need. Free and open source, BSD 3-Clause.",
        ),
        (
            "scipy.sparse.linalg.eigs / eigsh",
            "for matrices too large to hold densely. Asks for the k largest or "
            "smallest eigenvalues rather than all of them, and needs only the "
            "ability to multiply by the matrix — the same requirement the power "
            "method has, which is not a coincidence: this is an industrial-grade "
            "relative of it. Free and open source, BSD 3-Clause.",
        ),
        (
            "torch.linalg.eig / eigh",
            "the same interface on tensors, so it runs on a GPU and takes part in "
            "automatic differentiation. Choose it when the eigendecomposition sits "
            "inside a model rather than beside it. Free and open source, BSD-style.",
        ),
        (
            "sklearn.decomposition.PCA",
            "PCA as a fitted object, with the centring, the sorting, the "
            "variance ratios and the transform handled for you — and with a "
            "singular value decomposition underneath rather than an explicit "
            "covariance matrix, which is more accurate on ill-conditioned data. "
            "Use it for real work; the five lines in exercise 5 are for "
            "understanding what it does. Free and open source, BSD 3-Clause.",
        ),
    ):
        print(f"     {name}")
        for line in _wrap(note, 66):
            print(f"         {line}")
        print()

    print(f"{SCRIPT}: every assertion held.")


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


if __name__ == "__main__":
    main()
