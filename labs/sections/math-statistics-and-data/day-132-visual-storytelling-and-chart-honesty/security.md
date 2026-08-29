# Security notes

## What this lab does

It draws charts in memory and measures them. That is the whole surface
area.

- **No network.** After the single `pip install` that creates the
  virtual environment, nothing in this lab opens a socket. The test
  harness greps every source file under `examples/` and `starter/` for
  `urlopen`, `requests.`, `socket.`, `http://` and `https://` and fails
  if any appears.
- **No files written.** This lab draws roughly fifty figures and saves
  none of them. Nothing calls `savefig`. The harness fails if any
  `.png`, `.svg` or `.pdf` is found anywhere under the lab directory
  after a run, and also fails on a leftover `__pycache__` or
  `.pytest_cache`.
- **No display server, no window.** `matplotlib.use("Agg")` is called
  before `pyplot` is imported in every file, and `plt.show()` is never
  called. The harness greps for a real `plt.show(` call at the start of a
  statement and fails if it finds one.
- **No credentials, no keys, no external services.** `requires_api_key`
  is `false` in `metadata.yml` and there is nothing to authenticate to.
- **No `sudo`, ever.** Every command in this lab runs as your normal
  user, and everything it creates lives inside the lab directory.

## The data

Every dataset here is generated from a seeded NumPy random generator
inside the lab. There is no input file, no download, and no personal or
proprietary data of any kind. The bar labels ("north", "south", …) and
the values attached to them are invented for the exercise and mean
nothing.

## Cleaning up

`.venv` is the only large thing this lab creates, and removing it is one
command:

```bash
rm -rf .venv
```

The `cleanup_commands` in `metadata.yml` list that alongside clearing
bytecode caches and resetting `starter/` to its blank skeleton.

## A note that belongs on this page more than most

This lab is a tutorial in making misleading charts. It is worth being
explicit that the intent runs the other way: the point of building the
distortions is to be able to *measure* them, and the exercise that
matters most is the last one, which is a review tool you can run on your
own work. Nothing in `examples/` should be lifted into a real report. The
one function that should be is `review_chart`.
