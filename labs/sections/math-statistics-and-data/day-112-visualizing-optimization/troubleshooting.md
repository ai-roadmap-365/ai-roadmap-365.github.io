# Troubleshooting

Every entry below was hit while building this lab, or is named by a test that
exists because of it.

## `ModuleNotFoundError: No module named 'dataset'`

You ran a numbered script from the lab directory instead of from inside
`examples/`. The scripts import `dataset`, `gridviz`, `descent` and `imaging`
from beside themselves.

```bash
cd examples
../.venv/bin/python3 01_grid_and_ascii.py
cd ..
```

## `ModuleNotFoundError: No module named 'PIL'`

You are running the system `python3` rather than the lab's, or you installed
`numpy` and `pytest` but not `Pillow`. Everything in this lab goes through
`.venv/bin/python3`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

## My heatmap looks like a bowl, but the descent path walks toward the wrong wall

This is `world_to_pixel`'s y-flip, backwards. Data y grows upward; pixel rows
grow downward (row 0 is the top of the image). The formula is
`py = (ylim[1] - y) / (ylim[1] - ylim[0]) * (height - 1)`, not
`py = (y - ylim[0]) / (ylim[1] - ylim[0]) * (height - 1)`.

The reason this bug is dangerous rather than merely wrong: for a bowl
centred at the origin, `heatmap_array` on its own is vertically symmetric,
so the heatmap PNG looks completely correct by itself. The bug only shows up
once something is drawn ON TOP of it — which is exactly why exercise 4 checks
a specific pixel distance for the drawn path rather than checking the
heatmap image alone.

## My ASCII contour has the wrong character at a corner

Check the direction of your band mapping. `ascii_contour` rescales
`(Z - Z.min()) / (Z.max() - Z.min())` to `[0, len(chars))` and floors it — the
**lowest** value must map to `chars[0]` (the lightest character, a space in
the default ramp) and the **highest** value to `chars[-1]` (the densest). A
reversed ramp puts a dense character at the minimum, which is very easy to
miss by eye on a genuinely symmetric grid but fails the exact-character test
immediately.

## `Image.open(path).n_frames` raises `AttributeError`, or is always 1

Two separate causes:

- You saved a single `Image.save(path)` instead of
  `frames[0].save(path, save_all=True, append_images=frames[1:], ...)`. A
  plain `save` writes only the first frame, silently.
- You forgot `format="GIF"`. Pillow infers format from the file extension in
  most cases, but passing it explicitly is one fewer thing to get wrong when
  writing to a path Python built rather than one you typed.

## My GIF frame colours look banded or wrong

Each frame is converted to `"P"` (palette) mode with
`img.convert("P", palette=Image.ADAPTIVE)` before being appended. GIF is a
palette format — at most 256 colours per frame — so this conversion is not
optional decoration; skipping it produces a `TypeError` or a frame Pillow
silently re-quantizes with its own default palette, which looks noticeably
worse than `ADAPTIVE`.

## The log-axis collinearity test fails, but the linear one passes

You are almost certainly plotting `losses` on the log axis instead of
`numpy.log10(losses)`. `loss_curve_points`'s `log` argument controls which
values become the y-DATA before the same linear pixel mapping is applied to
both axes — the log transform has to happen before the pixel math, not
instead of it or after it.

If you did transform correctly and it still fails, check which run you fed
it: only the well-conditioned bowl (`a = b = 1`) produces an EXACTLY
geometric loss sequence with this lab's update rule. The ill-conditioned
bowl's loss is a sum of two different geometric sequences (one per axis) and
is not a single straight line on a log axis — which is itself worth noticing,
not a bug to chase.

## My learning-rate sweep raises `OverflowError` or prints a `RuntimeWarning`

`sweep_final_loss` must wrap both the update step and the final `f(x)`
evaluation in `numpy.errstate(over="ignore", invalid="ignore")`, and must
check `np.isfinite(x)` after every step rather than only at the end — a value
that has already overflowed to `inf` on step 50 of 300 will otherwise keep
being multiplied for 250 more steps, which is wasted work at best and `nan`
from `inf * 0` at worst if the coefficient array is ever exactly zero
somewhere.

Using a plain Python `float` instead of `numpy.float64` for `x` changes which
exception a genuine overflow raises (`OverflowError` from Python's own
`float.__pow__` rather than a NumPy `RuntimeWarning`) and `numpy.errstate`
does not catch it. Keep `x` as `numpy.float64` throughout.

## The starter tests all skip and I have written code

A skip means the function still returns `None`. Look for a leftover
`return None` below the code you added — the skeletons put `return None`
after a long docstring, and it is easy to write the body above it and leave
the `return None` in place, in which case your work is computed and then
discarded.

Downstream exercises also skip cleanly if an earlier one is unattempted:
`get_grid()` in `starter/test_starter.py` skips exercise 3 onward if
`evaluate_grid` itself is still `None`, rather than crashing on an unpack of
`None`. If exercise 4 is skipping and you are sure you wrote
`draw_path_on_heatmap`, check exercise 1 and exercise 3 first.

## `__pycache__` or `.pytest_cache` appears and the cleanup check fails

Run:

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

`tests/run_tests.sh` clears both at the **start** of its own run (pruning
`.venv`) for the same reason Day 110's harness does: the README's own
documented `pytest starter -q` legitimately writes `starter/__pycache__`, and
an earlier version of a harness like this one would then report that as
litter at the end — failing you for following the instructions. `.venv`
itself is the documented setup and is never treated as a stray file, and
nothing inside it is ever deleted.

## Running `pytest` with no arguments gives a different skip count than `pytest starter`

It should not, and there is a check for exactly that. Both `examples/` and
`starter/` define modules called `dataset`, `gridviz`, `descent` and
`imaging`. Without the `conftest.py` in each directory, collecting both
suites in one run would import whichever copy of, say, `gridviz` Python saw
first and reuse it for the other suite — so an unattempted starter exercise
could silently import the REFERENCE implementation and report as passing.
That is a wrong answer with a green tick on it, which is the worst kind, and
it is exactly the failure mode this lab's own authoring process ran into and
had to catch: two independent copies of this exact lab, sharing this exact
directory, defined the same module names and began overwriting each other's
files until the collision was noticed and one copy was deleted outright.
Nothing short of separate, careful ownership of a directory — which
`conftest.py`'s `sys.path` and `sys.modules` surgery enforces for the code,
and a single author enforces for everything else — actually prevents it.

## Windows

Not run here, and this file will not pretend otherwise. Use the Windows
Subsystem for Linux and follow the Linux instructions, or use Git Bash with
`.venv\Scripts\python.exe` in place of `.venv/bin/python3`. Everything in the
lab is NumPy, Pillow and standard-library Python, so nothing in it is
platform-specific — but "should work" and "was run" are different claims and
only the second one is worth making.
