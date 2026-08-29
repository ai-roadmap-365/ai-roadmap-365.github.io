# What is installed, why, and what it costs

Three packages, all free and open source, all installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `numpy` | 2.5.2 | BSD 3-Clause | `numpy.meshgrid` to build every grid, vectorised arithmetic for the colour ramp, and the gradient-descent loop itself. |
| `Pillow` | 12.3.0 | MIT-CMU (the "PIL Software License") | `Image`, `ImageDraw` and `Image.save(..., save_all=True)` — every pixel this lab draws, and the only GIF-writing code it needs. |
| `pytest` | 9.1.1 | MIT | The reference suite and your running score in `starter/`. |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially.

## The tool this lab deliberately does not install

**matplotlib is not installed here, and neither is scipy, pandas or plotly.**
That is not an oversight — it is the reason this lab exists in the form it
does. Every picture is built from a NumPy array and Pillow's `ImageDraw`
with nothing else in between, so nothing about how a contour plot or a loss
curve actually gets to the screen is hidden behind a library call. The
lesson's Tools section describes matplotlib, Plotly, TensorBoard and Weights
& Biases from their documentation and states plainly that no output from any
of them is reproduced here.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Section 6 of
`tests/run_tests.sh` greps every source file in `examples/` and `starter/` to
prove that nothing else does.

## If you cannot install anything at all

Almost none of this lab runs without Pillow, and that is worth saying
plainly rather than glossing over: `evaluate_grid` and `ascii_contour` need
only NumPy (and the ASCII renderer is genuinely useful on its own — it is how
this lab's first picture gets checked without an image viewer at all), but
every PNG and the GIF need `PIL.Image` and `PIL.ImageDraw` directly, and there
is no standard-library substitute for either.

## What is deliberately *not* installed, and why it is not a problem

matplotlib, Plotly, TensorBoard and Weights & Biases all do this job, usually
better and always faster to write. None of them is installed here, and **no
output from any of them is reproduced anywhere in this lab or its lesson.**
They are described from their documentation, and the lesson's Tools section
marks each one as not run.

That is not a limitation to apologise for. `heatmap_png` and
`draw_path_on_heatmap` in `examples/imaging.py` do, by hand, exactly what
`matplotlib.pyplot.contourf` and `plt.plot` do for you: evaluate a function
over a grid, map values to colours, and place pixels. Having built the
minimal version, the documentation of the real one reads as engineering on
top of an idea you already own, rather than as magic.
