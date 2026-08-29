# What in the captured output may legitimately differ on your machine

Every file in this directory was captured from a real run on the authoring
machine on 17 August 2026:

```
python   3.14.0
numpy    2.5.2
pillow   12.3.0
pytest   9.1.1
platform macOS-26.5.2-arm64-arm-64bit-Mach-O
```

Most of what you see is arithmetic and will be identical everywhere. This file
names the parts that will not be, so you can tell a real difference from a
harmless one.

## Will differ, and does not matter

| Field | Where | Why |
| --- | --- | --- |
| `platform macOS-26.5.2-arm64-arm-64bit-Mach-O` | `test-run.txt`, section 1 | Your operating system, version and processor. |
| `python 3.14.0` | `test-run.txt`, section 1 | Whichever Python you installed the lab into. Anything from 3.11 up will work; the type-hint syntax in `warp.py` needs 3.9 or later. |
| `... in 0.14s` | `reference-tests.txt`, `starter-progress.txt`, `test-run.txt` | Timing. Nothing in this lab asserts a duration; the whole suite is well under a second because the images are 9 by 9. |
| `written, 89 bytes on disk for 81 pixels` | `06-against-pillow.txt`, section 7 | The exact byte count of the PNG depends on the zlib build and its default compression level. The lab asserts only that the file is non-empty and that the array survives the round trip. |

## Must NOT differ

If any of these changes, something real has changed and the harness will say
so rather than passing quietly.

| Value | Where |
| --- | --- |
| `79 checks, 0 failure(s).` | `test-run.txt`, last line |
| `64 passed` | `reference-tests.txt` |
| `1 passed, 53 skipped` | `starter-progress.txt` (an untouched checkout) |
| 22 forward-mapping holes on a 30 degree rotation | `02-*.txt`, `test-run.txt` |
| 243 of 324 holes when doubling by forward mapping | `02-*.txt`, `test-run.txt` |
| A quarter turn equalling `numpy.rot90(img, -1)` exactly | `03-*.txt`, `test-run.txt` |
| 16 pixels lost by twelve separate 30 degree passes | `03-*.txt`, `06-*.txt` |
| 0 pixels lost by the same full turn as one matrix | `03-*.txt`, `06-*.txt` |
| 28 pixels lost by an integer shear round trip in two passes | `04-*.txt` |
| 510 of 510 affine transformations matching Pillow exactly | `06-*.txt`, `test-run.txt` |

## The three that are genuinely machine-dependent, and are asserted anyway

These are the interesting ones. All three are floating-point results, all three
were measured rather than assumed, and the lab states what it is claiming about
each.

**1. `math.cos(math.pi / 2)` is `6.123233995736766e-17`, not `0.0`.**
This is the Day 102 result and it follows from IEEE 754 double precision, which
is specified rather than platform-dependent, so it will be the same on your
machine. The lab uses it to justify stating a tolerance on every float
comparison. Note what the lab then *measures*: the float noise does **not**
change a single pixel of a quarter turn, because nearest-neighbour rounds to a
whole pixel and an error of 1e-17 never reaches a rounding boundary.

**2. The eight whole-degree rotations where this lab and Pillow disagree:
30, 60, 120, 150, 210, 240, 300 and 330.**
This is the one to watch. At those angles a sample lands within one unit in the
last place of a pixel boundary, and which side of the boundary you get is
decided by the *order* the floating-point additions happen in — Pillow's C loop
accumulates the source coordinate along each output row, this lab evaluates the
whole expression per pixel. The list of eight was measured on this machine with
Pillow 12.3.0.

A different compiler, a different Pillow build, or a machine that evaluates
intermediates at extended precision could produce a different list. If yours
differs, the lab has not broken and neither has Pillow — the check that
actually matters is the one beside it, which asserts that **every** disagreeing
sample sits within 1e-9 of a pixel boundary. That is the claim; the specific
angles are the evidence for it on one machine on one day.

**3. Pillow's bilinear border behaviour.**
Where all four contributing pixels are inside the image, this lab's bilinear
and Pillow's agree to within 1.0 grey level — that is the rounding of a float
average back into a byte and cannot be improved on. Where a contributor lies
outside the image, they differ by up to 118 grey levels, because they
extrapolate differently: this lab averages the fill value in, Pillow does not.
The lab asserts both halves. The exact border figure of 118 depends on the pixel
values in the test pattern, so the assertion is `> 100`, not `== 118`.

## Reproducing the capture

```bash
cd labs/sections/math-statistics-and-data/day-105-transforming-images-with-matrices
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
bash tests/run_tests.sh
```

Nothing in this directory was written by hand or edited after capture.
