# Dependencies for the Day 105 lab

Three packages, all free and open source, all installed from the Python Package
Index with `pip`, all running entirely on your own machine.

| Package | Pinned version | Why this lab needs it |
| --- | --- | --- |
| `numpy` | `2.5.2` | Holds the pixels. An image is a 2-D array of bytes and this is what NumPy exists for. Also supplies the independent answers the lab checks against: `numpy.rot90`, `numpy.fliplr`, `numpy.flipud`, `numpy.kron` and ordinary strided slicing. |
| `pillow` | `12.3.0` | The mature library your from-scratch code is compared against. `Image.transform` with `Image.Transform.AFFINE` is the whole of the comparison, plus one PNG round trip. |
| `pytest` | `9.1.1` | The test runner from Days 071–074. Nothing new here except what it is pointed at. |

## Why the from-scratch code deliberately does not use NumPy for the maths

`examples/warp.py` and `starter/warp.py` build and multiply their 3 by 3
matrices with plain lists and hand-written arithmetic. If `rotation` returned a
NumPy array built by a NumPy helper, then checking it against NumPy would be
checking NumPy against itself, and agreeing with Pillow would prove nothing
either — both sit on the same numerical machinery.

NumPy holds the **pixels**, because a 9 by 9 array of bytes is exactly what it
is for and writing that by hand would teach nothing. The **mathematics** is
ours. That split is what makes section 3 of `06_against_pillow.py` mean
something: 510 transformations, byte-for-byte identical output, from two
implementations that share no code.

## Why the versions are pinned

They are *checked* rather than assumed. Section 1 of `tests/run_tests.sh` reads
the installed versions and compares them against this file, so a mismatch is
reported at the top of the run rather than surfacing later as a confusing diff.

Two places the version could genuinely matter, both handled honestly rather
than pinned to a last digit:

1. **Pillow's sampling rule.** This lab establishes by measurement that Pillow
   evaluates an affine transform at each output pixel's *centre* and takes the
   input pixel whose square contains the result. That was measured on Pillow
   12.3.0 on the authoring machine. It is a long-standing behaviour rather than
   a documented guarantee, so the lab measures it every run instead of
   asserting it from memory — `test_pillow_samples_at_pixel_centres_not_at_integer_corners`
   will fail loudly if a future version changes it, which is the correct
   outcome.

2. **Floating-point tie-breaking.** Eight of the 360 whole-degree rotations
   produce output that differs between this lab's implementation and Pillow's,
   by at most 2 pixels out of 81, and every one of those disagreements is a
   sample landing within one ulp of a pixel boundary. That set of eight angles
   is specific to this machine's floating-point behaviour and this version of
   Pillow. The lab asserts the *count* and asserts that every disagreement is
   at a boundary; it does not claim the two implementations agree everywhere,
   because they do not.

The versions were read from the installed packages rather than guessed:

```bash
.venv/bin/python3 -c "from importlib.metadata import version; print(version('numpy'), version('pillow'), version('pytest'))"
```

On the authoring machine, on 17 August 2026, that printed
`2.5.2 12.3.0 9.1.1`.

## Licences

NumPy is distributed under the BSD 3-Clause licence, Pillow under the MIT-CMU
licence, and pytest under the MIT licence, each stated on that project's own
documentation site. All three are maintained in the open, cost nothing, and
need no account, no key and no signup — personally or commercially.

## One-time install

From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy, PIL; print(numpy.__version__, PIL.__version__)"
```

Expect `2.5.2 12.3.0`. Day 43 covered `python3 -m venv` in full; this is the
same pattern. The environment lives in `.venv/` inside the lab, is already
excluded from version control, and can be deleted at any time with
`rm -rf .venv`.

## Network

Installing needs the network, once. **Nothing else in this lab does.**

In particular, the test image is *generated in code*, not downloaded. That was
a deliberate choice: a lab that fetches a photograph is a lab that breaks on a
train, ships a file whose licence someone has to check, and hides its own test
data behind a URL. `pattern.py` builds a 9 by 9 capital F from arithmetic, and
every pixel value in it is asserted. Section 7 of `tests/run_tests.sh` greps
every file under `examples/` and `starter/` for the patterns that would
indicate a socket being opened.

## Running without a lab-local environment

If NumPy, Pillow and pytest are already available in an environment you have
activated, the harness will find `pytest` on your `PATH`. You can also point it
at a specific binary:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The harness uses the `python3` that sits beside that `pytest`, because that is
the interpreter the packages are installed into. If NumPy or Pillow is not
importable from it, the harness says so and stops rather than skipping checks
quietly.

## What you would give up without Pillow

Less than you might fear, and the part you would lose is the best part.

Exercise 1 — writing all twelve functions — needs `math` and NumPy only, and
every test of your rotation, scaling, shear, flip, composition and inverse
mapping still runs, because those are checked against `numpy.rot90`,
`numpy.fliplr`, `numpy.kron` and strided slices rather than against Pillow.

What you lose is the comparison: the 510-transformation agreement, the
measurement that settles where Pillow takes its sample, the shear that moves
row 0, and the bilinear border finding. Those are the day's strongest
artifacts and they cannot be faked. The lab does not pretend otherwise.
