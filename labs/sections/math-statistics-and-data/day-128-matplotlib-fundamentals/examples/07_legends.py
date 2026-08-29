"""Exercise 7 -- legends, the label-then-legend pattern.

Give every artist that should appear in the legend a label= at plot time,
then call ax.legend() once. The legend's entries come out in the order
the artists were plotted, matching the labels supplied.
"""

import matplotlib.pyplot as plt

import plotting as P

x = [0, 1, 2, 3]
measured = [2.1, 3.4, 3.9, 5.2]
predicted = [2.0, 3.2, 4.1, 5.0]

fig, ax = P.plot_two_series_with_legend(x, measured, "measured", predicted, "predicted")

legend = ax.get_legend()
texts = [t.get_text() for t in legend.get_texts()]
print(f"legend texts, in order: {texts}")

assert legend is not None, "expected ax.legend() to have created a Legend"
assert texts == ["measured", "predicted"], f"expected ['measured', 'predicted'], got {texts}"

plt.close(fig)
print("\n07_legends.py: every assertion held.")
