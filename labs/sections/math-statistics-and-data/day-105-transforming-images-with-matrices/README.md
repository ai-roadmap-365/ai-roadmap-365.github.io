# Day 105 lab — Rotate It Yourself

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Transforming Images with Matrices
- **Day number:** 105 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-105-transforming-images-with-matrices
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-105-transforming-images-with-matrices` when the site is running.
<!-- generated-links:end -->

## Purpose

An image is a matrix. Everything Week 15 taught applies to it directly — and
now you can see the result.

This lab has you write rotation, scaling, shear and flip yourself, as 3 by 3
matrices built from arithmetic you can check on paper, and apply them to a
picture. Then it hands the identical six numbers to Pillow and compares the two
outputs pixel by pixel.

The order of the work is the argument. First you implement **forward
mapping** — walk the input, send each pixel where it lands — and count the
damage: 22 of 81 output pixels never written on a 30 degree rotation, holes
punched through the middle of solid ink, and 243 of 324 missing when you
enlarge. Then you turn the loop inside out and do **inverse mapping**: walk the
output, send each pixel's centre backward through the inverse matrix, and take
the value it came from. The holes do not get patched. They stop existing,
because the loop is now over the array being filled.

Along the way the lab settles a question Day 102 raised and deliberately left
open. Pillow's affine coefficients express the **output-to-input** map, which
Day 102 confirmed; what it could not determine was where in each output pixel
the transformation is evaluated. This lab answers it by measurement: at the
pixel's **centre**, `(x + 0.5, y + 0.5)`. That half is why a shear coefficient
of 2.0 moves row 0 by a whole pixel even though the shear term is multiplied
by y and row 0 is supposedly at y = 0.

The comparison is the day's strongest artifact and it is reported honestly in
both directions. On 510 affine transformations, your implementation and
Pillow's produce byte-for-byte identical arrays. On the 360 whole-degree
rotations, 352 agree and 8 do not — by at most 2 pixels of 81, every one of
them a floating-point tie where a sample lands within one unit in the last
place of a pixel boundary. The eight are 30, 60, 120, 150, 210, 240, 300 and
330 degrees: the "nice" angles, which is the opposite of most people's
intuition and worth remembering.

Nothing is downloaded. The test image is generated in code — a capital F on a 9
by 9 grid, asymmetric under every operation in the lab, so a broken flip cannot
accidentally pass. Every pixel value in it is asserted.

## Learning objectives

By the end of this lab you can:

1. Explain why an image array is indexed `img[y, x]` while the mathematics
   writes `(x, y)`, and read the same pixel both ways without guessing.
2. Implement forward mapping, count the holes it leaves, and say why patching
   them is the wrong instinct.
3. Implement inverse mapping with nearest-neighbour sampling, and get a quarter
   turn that equals `numpy.rot90(img, -1)` exactly.
4. Build translation as a matrix using homogeneous coordinates, and say why no
   2 by 2 matrix can do it.
5. Compose several transformations into one matrix, and measure what you lose
   by resampling repeatedly instead.
6. Convert your matrix into Pillow's six coefficients — remembering the
   inverse — and confirm the two implementations agree.
7. State precisely where that agreement stops, and why.

## Prerequisites

- Day 099 (vectors), Day 100 (matrices), Day 101 (matrix multiplication and
  composition), Day 102 (linear transformations, determinants, inverses),
  Day 103 (dot products) and Day 104 (NumPy).
- Day 043 for `python3 -m venv`, and Days 071–074 for pytest.
- Comfort with `math.cos`, `math.sin` and radians. Day 102's rotation section
  derives both from the unit circle if you want the refresher.

No prior image-processing experience is assumed, and no mathematics beyond
Week 15.

## Supported operating systems

- **macOS** — captured here on macOS 26.5.2, Apple Silicon (arm64).
- **Linux** — every command is identical.
- **Windows** — use WSL2 and follow the Linux instructions. Native PowerShell
  works too, with `python -m venv .venv` and `.venv\Scripts\python.exe` in
  place of `.venv/bin/python3`, but `tests/run_tests.sh` is a bash script and
  needs Git Bash or WSL. This was not run on Windows and the lab does not claim
  it was.

## Hardware requirements

Anything that runs Python. The images in this lab are 9 by 9 pixels and the
entire test suite finishes in well under a second. Roughly 80 MB of disk for
the virtual environment, almost all of it NumPy and Pillow.

## Required software

| Software | Version used here | Notes |
| --- | --- | --- |
| Python | 3.14.0 | 3.11 or later is fine. |
| numpy | 2.5.2 | Holds the pixels and supplies the independent answers. |
| Pillow | 12.3.0 | The library your work is compared against. |
| pytest | 9.1.1 | The test runner from Days 071–074. |
| bash | 3.2.57 | For `tests/run_tests.sh`. |

`requirements/README.md` explains why each is pinned and what you would lose
without Pillow.

## Free and open-source options

All three packages are free and open source, need no account, no key and no
signup, and cost nothing for personal or commercial use. NumPy is BSD
3-Clause, Pillow is MIT-CMU, pytest is MIT.

There is no paid tier and nothing here is a trial. The one deliberate
non-dependency is worth naming: the test image is generated rather than
downloaded, so the lab needs no image file, no image licence and no network
after the install.

Three other libraries do this same work and are described in the lesson but
are **not installed here and produce no output in this lab**: OpenCV,
scikit-image and torchvision. Each is free and open source too. The lesson says
plainly which tools were run and which were not.

## Installation

From the lab directory:

```bash
cd labs/sections/math-statistics-and-data/day-105-transforming-images-with-matrices
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy, PIL; print(numpy.__version__, PIL.__version__)"
```

Expect `2.5.2 12.3.0`. This is the only step that needs the network.

## File structure

```
day-105-transforming-images-with-matrices/
├── README.md
├── metadata.yml
├── troubleshooting.md
├── security.md
├── requirements/
│   ├── README.md              why each package, and what you lose without it
│   └── requirements.txt       numpy, Pillow, pytest, all pinned
├── starter/                   YOUR WORK
│   ├── 00_brief.md            read this first
│   ├── warp.py                twelve functions to write
│   ├── answers.py             twenty-six predictions to make
│   ├── pattern.py             the test image, written for you
│   ├── test_starter.py        your running score
│   └── conftest.py            the import guard (see below)
├── examples/                  THE REFERENCE, read after you attempt
│   ├── warp.py                the complete implementation
│   ├── pattern.py             identical to the starter copy
│   ├── 01_an_image_is_a_matrix.py
│   ├── 02_forward_mapping_leaves_holes.py
│   ├── 03_inverse_mapping.py
│   ├── 04_scale_shear_flip.py
│   ├── 05_homogeneous_and_composition.py
│   ├── 06_against_pillow.py
│   ├── test_reference.py      64 tests over the reference implementation
│   └── conftest.py            the import guard
├── tests/
│   └── run_tests.sh           the harness: 79 checks
└── expected-output/           captured from real runs, never hand-written
    ├── 01-an-image-is-a-matrix.txt … 06-against-pillow.txt
    ├── reference-tests.txt
    ├── starter-progress.txt
    ├── test-run.txt
    └── FIELDS.md              what may legitimately differ on your machine
```

**About the two `conftest.py` files.** `examples/` and `starter/` both contain
modules called `warp` and `pattern`. pytest imports a test file by putting its
directory on `sys.path`, so running `pytest` across both at once would import
whichever `warp` it saw first and reuse it for the other suite — which would
let the starter tests pass against the reference solution and report unwritten
exercises as done. Each `conftest.py` prevents that, and section 4 of the
harness proves it still works by checking that the skip count is unchanged
whether you run `pytest starter` or bare `pytest`.

## How to run

Read `starter/00_brief.md`, then work through `starter/warp.py` and
`starter/answers.py`. Check yourself at any point:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `1 passed, 53 skipped`. Unattempted work
is **skipped**, not failed. When it says `54 passed`, you are finished.

To see the finished versions — after you have attempted the exercises:

```bash
cd examples
../.venv/bin/python3 01_an_image_is_a_matrix.py
../.venv/bin/python3 02_forward_mapping_leaves_holes.py
../.venv/bin/python3 03_inverse_mapping.py
../.venv/bin/python3 04_scale_shear_flip.py
../.venv/bin/python3 05_homogeneous_and_composition.py
../.venv/bin/python3 06_against_pillow.py
cd ..
```

And the whole thing at once:

```bash
bash tests/run_tests.sh
```

## What the commands do

| Command | What it does |
| --- | --- |
| `01_an_image_is_a_matrix.py` | Prints the test picture as characters and as numbers, measures the `(row, column)` versus `(x, y)` mismatch, and shows colour as three stacked planes. |
| `02_forward_mapping_leaves_holes.py` | Does it wrong on purpose. Counts 22 holes on a rotation, 243 when doubling, and shows that shrinking leaves no holes but overwrites 24 of 25 output pixels instead. |
| `03_inverse_mapping.py` | Turns the loop inside out. Quarter turns that equal `numpy.rot90` exactly, and the difference between one 360 degree matrix and twelve 30 degree passes. |
| `04_scale_shear_flip.py` | Flip against `numpy.fliplr`, doubling against `numpy.kron`, halving against a strided slice, and the shear that moves row 0. Ends with what affine transformations cannot do. |
| `05_homogeneous_and_composition.py` | Why translation needs a third coordinate, three matrices folded into one, order mattering, and the singular case that cannot be applied at all. |
| `06_against_pillow.py` | The comparison. Settles Pillow's sampling rule by measurement, agrees on 510 transformations, disagrees on 8 of 360 rotations, and states exactly where the bilinear agreement stops. |
| `pytest examples -q` | 64 tests over the reference implementation. |
| `pytest starter -q` | Your score. Skips what you have not written. |
| `bash tests/run_tests.sh` | 79 checks: versions, all six scripts, both suites, the import guard, every claim above re-measured, a deliberate self-failure, and a hygiene sweep. |

## Expected output

The final line of the harness on the authoring machine:

```
79 checks, 0 failure(s).
```

The comparison that the day is built around, from
`expected-output/06-against-pillow.txt`:

```
    transformations compared:            510
    transformations matching EXACTLY:    510
    worst case, pixels differing:        0
    stated tolerance for this comparison: 0 (exact equality)
```

and, immediately afterwards, the half that makes it honest:

```
    rotations compared:                 360
    identical, pixel for pixel:         352
    disagreeing in at least one pixel:  8
    worst case, pixels differing:       2 of 81
    the angles: [30, 60, 120, 150, 210, 240, 300, 330]
```

Forward mapping against inverse mapping, from
`expected-output/02-forward-mapping-leaves-holes.txt` — the `~` are pixels that
were never written:

```
  forward mapping (holes show as ~)      inverse mapping
    ~~.###~~~                          ~~.####~~
    ~.##~..#~                          ~.##..##~
    ~.##....#                          ..##....#
    .##~.....                          .###.....
    #~#.#..~.                          #####....
    ##.~.....                          ##.......
    ##......~                          ##.......
    ~...~...~                          ~.......~
    ~~~....~~                          ~~.....~~
```

Everything in `expected-output/` was captured from real runs. `FIELDS.md` lists
what may legitimately differ on your machine and what must not.

## Validation steps

1. The install printed `2.5.2 12.3.0`.
2. `.venv/bin/pytest examples -q` prints `64 passed`.
3. `.venv/bin/pytest starter -q` prints `1 passed, 53 skipped` before you start
   and `54 passed` when you finish.
4. Each of the six reference scripts exits 0 and ends with
   `NN_name.py: every assertion held.`
5. `bash tests/run_tests.sh` prints `79 checks, 0 failure(s).` and exits 0.
   Check the exit status directly, not through a pipe:

   ```bash
   bash tests/run_tests.sh; echo "exit=$?"
   ```

6. Your own output matches `expected-output/`, allowing for the machine-
   dependent fields named in `FIELDS.md`.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints `N checks, M
failure(s)`, exits 0 only when `M` is 0, and reads **real values** rather than
reading source — every claim in this README is re-measured there.

Section 6 is the one worth reading. A green test suite proves nothing until you
have watched it go red, so the harness re-runs itself with one expectation
deliberately swapped for the naive belief that Pillow samples at integer pixel
corners, and asserts that the re-run names the failing check and exits
non-zero with exactly one failure. If section 6 passes, section 5 is not
decorative.

Every float comparison in the lab states a tolerance. Pixel comparisons state
whether they are exact — most of them are, and say `==` on purpose, because
that is the stronger claim.

## Cleanup

The lab writes nothing outside its own directory. The one file it does create,
a PNG for the round-trip demonstration, lives in the operating system's
temporary directory and is removed by the `tempfile.TemporaryDirectory` context
that made it. Section 7 of the harness asserts that no image file exists
anywhere under the lab.

```bash
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the virtual environment
git checkout -- starter/   # optional: resets your work
```

## Troubleshooting

`troubleshooting.md` covers the failures people actually hit. The three
shortest answers:

- **Everything is half a pixel out, or `halving is exactly a strided slice`
  fails** — you left `SAMPLE_OFFSET` out of `warp_nearest_with_inverse`.
- **The picture moves the wrong way through Pillow** — you passed your matrix
  instead of its inverse. Use `to_pillow_coefficients`.
- **`pytest starter` reports failures rather than skips** — you deleted a
  `raise NotImplementedError` without writing the body, or you ran it from
  inside `starter/` instead of from the lab directory.

## Security notes

`security.md` has the detail. In short: the lab needs the network exactly once,
to install three packages from PyPI. Nothing else opens a socket, reads a URL
or contacts a service — including the test image, which is generated in code
precisely so that it does not need to be fetched. Nothing needs `sudo`, nothing
needs a key, nothing binds a port, and nothing writes outside the lab
directory or a temporary directory it cleans up.

## Extension exercises

1. **Bilinear from scratch.** `warp_bilinear_with_inverse` is written for you
   in `examples/warp.py`. Write your own, then find the border cases where it
   disagrees with Pillow and decide what *you* think should happen outside the
   image: fill, clamp to the edge pixel, or refuse.
2. **Rotate without clipping.** A rotated square does not fit in a square. Work
   out the bounding box of the four transformed corners, size the output to
   fit, and add the translation that keeps the picture centred — all in one
   composed matrix.
3. **Find your own tie.** The eight disagreeing angles were whole degrees.
   Sweep half-degrees, or sweep translations in steps of 0.1, and see whether
   the pattern of "nice numbers are dangerous" holds.
4. **A projective transform.** Change the bottom row from `(0, 0, 1)` to
   something else, divide the result by the third coordinate, and watch
   parallel lines converge. That is the perspective transform this lab says
   affine cannot do — implemented in about five extra lines.
5. **Colour properly.** `warp_colour` transforms three planes separately.
   Confirm that this is genuinely the same as transforming the coordinates
   once, by checking that a colour rotation equals stacking three greyscale
   rotations, then time both and see whether the loop order matters.

## Navigation

- Previous: Day 104 — NumPy and vectorised thinking
- Next: the Week 15 project
- Section: `labs/sections/math-statistics-and-data/`
