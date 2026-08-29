"""Exercise 7 — perspective breaks the comparison the chart exists for.

Two 3D bars, heights 1 and 2, a data ratio of 2. Every corner is pushed
through the Axes' own projection matrix and the drawn front-face areas
are compared. The flat 2D control gives exactly 2.000. The 3D versions do
not -- and how wrong they are depends on where the taller bar happens to
be standing, which is a fact about the camera, not about the data.
"""

import matplotlib.pyplot as plt

import honesty as H

HEIGHTS = (1.0, 2.0)
TOLERANCE = 0.10


def main():
    data_ratio = HEIGHTS[1] / HEIGHTS[0]

    fig, ax = H.bar_pair(HEIGHTS)
    try:
        fig.canvas.draw()
        flat = H.drawn_bar_heights(ax)
    finally:
        plt.close(fig)
    flat_ratio = flat[1] / flat[0]

    far = H.bar3d_projected_areas(list(HEIGHTS), [0.0, 3.0])
    near = H.bar3d_projected_areas(list(HEIGHTS), [3.0, 0.0])
    far_ratio = far[1] / far[0]
    near_ratio = near[1] / near[0]

    print(f"Heights {HEIGHTS[0]:.0f} and {HEIGHTS[1]:.0f}. Data ratio = {data_ratio:.3f}.")
    print()
    print("  rendering                          drawn ratio   departure")
    print(f"  flat 2D bars                          {flat_ratio:.3f}        {abs(flat_ratio / data_ratio - 1) * 100:5.1f}%")
    print(f"  3D, taller bar at the far depth       {far_ratio:.3f}        {abs(far_ratio / data_ratio - 1) * 100:5.1f}%")
    print(f"  3D, taller bar at the near depth      {near_ratio:.3f}        {abs(near_ratio / data_ratio - 1) * 100:5.1f}%")
    print()

    assert abs(flat_ratio - data_ratio) < 1e-9, flat_ratio
    assert abs(far_ratio / data_ratio - 1.0) > TOLERANCE, far_ratio
    assert abs(near_ratio / data_ratio - 1.0) > TOLERANCE, near_ratio
    assert near_ratio > far_ratio, (near_ratio, far_ratio)

    print("  The flat chart is exact. Both 3D renderings overstate the taller")
    print(f"  bar, and moving it from the far depth to the near one takes the")
    print(f"  drawn ratio from {far_ratio:.2f} to {near_ratio:.2f} -- from a {abs(far_ratio / data_ratio - 1) * 100:.0f}% overstatement to")
    print(f"  a {abs(near_ratio / data_ratio - 1) * 100:.0f}% one -- without touching a single number.")
    print()
    print("  These figures depend on the camera: this run uses matplotlib's")
    print("  perspective projection at focal_length=0.2 and the default view")
    print("  angle. A different camera gives different numbers. What does not")
    print("  change is the shape of the result: under perspective, the drawn")
    print("  size of a bar depends on where it stands, so the one comparison")
    print("  the chart exists to support is the one the third dimension")
    print("  breaks.")
    print()
    print("07_three_d_distortion.py: every assertion held.")


if __name__ == "__main__":
    main()
