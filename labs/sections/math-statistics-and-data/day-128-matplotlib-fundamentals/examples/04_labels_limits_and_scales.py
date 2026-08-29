"""Exercise 4 -- labels, limits, ticks and scales.

Two claims: configure_axes sets exactly the label and title it is given,
and an explicit set_ylim OVERRIDES autoscaling rather than being merged
with it or ignored. The data plotted below ranges from 0 to 100 -- if
autoscale were still in charge after configure_axes runs, the y-limits
would reflect that range, not the (-5, 5) window this script asks for.
"""

import matplotlib.pyplot as plt

import plotting as P

fig, ax = plt.subplots()
ax.plot([0, 1, 2, 3], [0, 100, 5, 80])
fig.canvas.draw()
autoscaled_ylim = ax.get_ylim()
print(f"autoscaled ylim before configure_axes: {autoscaled_ylim}")

P.configure_axes(ax, xlabel="trial number", title="Before the override", ylim=None)
assert ax.get_xlabel() == "trial number"
assert ax.get_title() == "Before the override"
print(f"xlabel = {ax.get_xlabel()!r}, title = {ax.get_title()!r}")

P.configure_axes(ax, xlabel="trial number", title="After the override", ylim=(-5, 5))
final_ylim = ax.get_ylim()
print(f"ylim after set_ylim(-5, 5): {final_ylim}")

assert final_ylim == (-5, 5), f"expected (-5, 5), got {final_ylim}"
assert final_ylim != autoscaled_ylim, "the explicit ylim should differ from the autoscaled one"
assert ax.get_title() == "After the override"

plt.close(fig)
print("\n04_labels_limits_and_scales.py: every assertion held.")
