"""Exercise 1 -- two-sample z-test from scratch, checked against a hand
computation done with the standard library only.

Two fixed, non-random samples so the "hand" side of the comparison is
exact arithmetic anyone can redo with a calculator, not a random draw.
"""
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from inference import phi, two_sample_z_test  # noqa: E402


def hand_two_sample_z(a: list[float], b: list[float]) -> tuple[float, float]:
    mean_a, var_a = statistics.mean(a), statistics.variance(a)
    mean_b, var_b = statistics.mean(b), statistics.variance(b)
    se = math.sqrt(var_a / len(a) + var_b / len(b))
    z = (mean_a - mean_b) / se
    p = 2.0 * (1.0 - phi(abs(z)))
    return z, p


def main() -> None:
    # Case 1: a clear, large separation.
    a = [50, 52, 49, 51, 53, 48, 50, 52, 51, 49]
    b = [54, 55, 53, 56, 54, 52, 55, 53, 54, 56]
    z_lib, p_lib = two_sample_z_test(a, b)
    z_hand, p_hand = hand_two_sample_z(a, b)
    print(f"Case 1 (clear separation): z_library={z_lib:.6f}  p_library={p_lib:.10e}")
    print(f"Case 1 (clear separation): z_hand={z_hand:.6f}  p_hand={p_hand:.10e}")
    assert abs(z_lib - z_hand) < 1e-9, "z from the library must match the hand computation"
    assert abs(p_lib - p_hand) < 1e-9, "p from the library must match the hand computation"
    assert p_lib < 0.001, "these two samples are obviously different -- p should be tiny"

    # Case 2: nearly identical samples -- p should be large (not significant).
    c = [50, 52, 49, 51, 53, 48, 50, 52, 51, 49]
    d = [51, 51, 50, 52, 52, 49, 51, 51, 52, 48]
    z_lib2, p_lib2 = two_sample_z_test(c, d)
    z_hand2, p_hand2 = hand_two_sample_z(c, d)
    print(f"Case 2 (near-identical): z_library={z_lib2:.6f}  p_library={p_lib2:.6f}")
    print(f"Case 2 (near-identical): z_hand={z_hand2:.6f}  p_hand={p_hand2:.6f}")
    assert abs(z_lib2 - z_hand2) < 1e-9
    assert abs(p_lib2 - p_hand2) < 1e-9
    assert p_lib2 > 0.30, "these two samples overlap heavily -- p should not be small"

    print("OK: two_sample_z_test agrees with an independent hand computation on both cases.")


if __name__ == "__main__":
    main()
