"""Exercise 8 -- the figure lifecycle, and the leak that follows from
ignoring it.

Every figure opened through pyplot lives in a global registry until
plt.close() (or plt.close('all')) removes it. A function that plots in a
loop and returns without closing leaks one figure per call -- harmless for
five iterations, expensive for five thousand in a long-running report
job. matplotlib's own defence is a RuntimeWarning once more than 20
figures are open at once; this script triggers it for real and captures
the message, then proves plt.close() on each figure empties the registry
completely.
"""

import warnings

import matplotlib.pyplot as plt

import plotting as P

plt.close("all")

# --- five unclosed figures: a small, silent leak ---
five_figs = P.open_figures_without_closing(5)
print(f"after opening 5 figures without closing any: plt.get_fignums() has {len(plt.get_fignums())} entries")
assert len(plt.get_fignums()) == 5

for fig in five_figs:
    plt.close(fig)
assert plt.get_fignums() == [], "closing each figure individually should empty the registry"
print(f"after closing each of the 5: plt.get_fignums() = {plt.get_fignums()}")

# --- the real warning, triggered for real ---
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    many_figs = P.open_figures_without_closing(22)

messages = [str(w.message) for w in caught if issubclass(w.category, RuntimeWarning)]
print(f"\nopening 22 figures without closing triggered {len(messages)} RuntimeWarning(s):")
for m in messages:
    print(f"  {m}")

assert len(plt.get_fignums()) == 22
assert any("More than 20 figures" in m for m in messages), (
    "expected matplotlib's own too-many-open-figures warning to fire"
)

plt.close("all")
assert plt.get_fignums() == []
print(f"\nafter plt.close('all'): plt.get_fignums() = {plt.get_fignums()}")

print("\n08_figure_leak.py: every assertion held.")
