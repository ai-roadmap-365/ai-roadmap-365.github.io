"""Exercise 1 -- the two APIs, and the failure that motivates the whole day.

draw_line_pyplot_style routes every instruction through plt.* -- the state
machine that always draws into whichever figure is "current". Called twice
in a row, with nothing in between asking for a new figure, both calls land
on the SAME figure. draw_line_object_style instead names a figure and axes
explicitly with fig, ax = plt.subplots() and calls methods on that specific
ax -- called twice, it is structurally impossible for the two calls to
collide, because each call created its own figure.
"""

import matplotlib.pyplot as plt

import plotting as P

plt.close("all")

# --- the pyplot state machine, called twice ---
P.draw_line_pyplot_style([0, 1, 2, 3], [0, 1, 4, 9], "run A")
P.draw_line_pyplot_style([0, 1, 2, 3], [9, 4, 1, 0], "run B")

pyplot_fignums = plt.get_fignums()
pyplot_fig = plt.figure(pyplot_fignums[0])
pyplot_lines = len(pyplot_fig.axes[0].lines)
print(f"pyplot-style: plt.get_fignums() = {pyplot_fignums}")
print(f"pyplot-style: lines on that one figure = {pyplot_lines}")
print(
    "pyplot-style: BOTH calls landed on the same current figure -- this is"
    " the bug. Two experiments' curves, overlaid, with nobody asking for that."
)

assert pyplot_fignums == [1] or len(pyplot_fignums) == 1, (
    f"expected exactly one figure from two plt.* calls, got {pyplot_fignums}"
)
assert pyplot_lines == 2, f"expected 2 lines on the one figure, got {pyplot_lines}"

plt.close("all")

# --- the object API, called twice ---
fig_a, ax_a = P.draw_line_object_style([0, 1, 2, 3], [0, 1, 4, 9], "run A")
fig_b, ax_b = P.draw_line_object_style([0, 1, 2, 3], [9, 4, 1, 0], "run B")

object_fignums = plt.get_fignums()
print(f"\nobject-style: plt.get_fignums() = {object_fignums}")
print(f"object-style: lines on figure A = {len(ax_a.lines)}, on figure B = {len(ax_b.lines)}")
print("object-style: two figures, one line each -- each call named exactly where it drew.")

assert len(object_fignums) == 2, f"expected two figures, got {object_fignums}"
assert len(ax_a.lines) == 1 and len(ax_b.lines) == 1

plt.close("all")

print("\n01_the_two_apis.py: every assertion held.")
