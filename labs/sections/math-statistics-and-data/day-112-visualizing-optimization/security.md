# Security notes

## What this lab does

It computes and draws pictures into a temporary directory, then deletes that
directory. It writes no permanent files, opens no network connection after
the one-time `pip install`, needs no credentials, no `sudo` and no elevated
permissions, and touches nothing outside its own directory (or a temporary
one it creates and removes itself). Every number it works with is invented
and is stated to be invented: the two bowl functions, the starting point, the
learning rate and the step counts are all written out in
`examples/dataset.py`.

Section 6 of `tests/run_tests.sh` greps every source file in `examples/` and
`starter/` for `urlopen`, `requests.`, `socket.`, `http://` and `https://` and
fails if any of them appears.

## The virtual environment

`python3 -m venv .venv` creates the environment inside the lab directory, so
nothing installed here can affect the rest of your machine, and `rm -rf .venv`
is a complete undo. The three packages are pinned to exact versions in
`requirements/requirements.txt`, and section 1 of the harness reads the
installed versions back and compares them against that file rather than
trusting that the install did what it said.

## Two things worth carrying away from this particular day

**A picture that looks plausible can still encode the wrong axis.** The
single most common bug this lab is built to catch is a flipped or transposed
grid: `world_to_pixel`'s y-axis flip (data y grows up, pixel rows grow down)
is the one piece of arithmetic every drawing function in `imaging.py` shares,
and getting it backwards produces a heatmap that still looks like a
symmetric bowl — a symmetric bowl looks the same either way — while the path
drawn on top of it walks toward the wrong wall. The lesson's honesty note
about never encoding the only copy of information in a picture applies here
too: a visualization that only an author who already knows the answer can
verify as correct is not a diagnostic instrument, it is decoration. That is
why exercise 4's test checks a *specific* pixel distance rather than "the
image exists".

**Silent numeric failure is worse than a crash.** The learning-rate sweep
runs learning rates that are known in advance to diverge. `descent.py`
catches the resulting overflow deliberately with `numpy.errstate(over=
"ignore")` and reports it as `float('inf')`, rather than letting a
`RuntimeWarning` escape unnoticed or letting an unguarded `x ** 2` on a huge
`float` raise `OverflowError` and crash the sweep. A training script that
does not check its own loss for finiteness will spend GPU-hours computing
usefully-shaped `nan`.

## What this lab deliberately does not claim

matplotlib, Plotly, TensorBoard and Weights & Biases are none of them
installed here, and **no output from any of them is reproduced anywhere in
this lab or its lesson.** They are described from their documentation and
marked as not run. "Here is how the real tool is called" is a claim about an
API; "here is what it printed" is a claim about a measurement, and this lab
only makes the first one for those four tools.
