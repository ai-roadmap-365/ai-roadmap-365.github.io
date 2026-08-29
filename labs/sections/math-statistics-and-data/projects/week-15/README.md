# Week 15 project — Image Transformer

This week was about **vectors and matrices**: vectors and distance, matrices
and their three meanings, matrix multiplication as composition, linear
transformations and what the columns tell you, dot products and similarity,
NumPy and vectorised thinking, and finally transforming images with matrices.

Day 105 walked you through rotating one generated test pattern. This project
is the same mathematics applied to **an image you chose**, assembled into a
small tool you would actually use — and the difference is that a real image
has edges, corners and colour, all of which the tutorial version could ignore.

## What you are building

A command-line **image transformer**: it takes an image, applies a sequence of
transformations you name, and writes the result. Every transformation is a
matrix you built, applied by inverse mapping you wrote. Pillow may load and
save the file; it may not do the geometry.

```
python transform.py in.png out.png --rotate 30 --scale 1.5 --shear-x 0.2
```

The point is not the tool. It is that by the end you can look at a rotated
photograph and say exactly which matrix produced it, why the corners are
where they are, and why the edges look the way they do.

## Requirements

- **Your own transformations** (Days 102, 105): scale, rotate, shear, flip and
  translate, each built as a matrix. Translation must go through homogeneous
  coordinates — it is not linear, and Day 102 proved why.
- **Composition, not repetition** (Day 101): a sequence of three
  transformations must be composed into **one** matrix and applied once. Prove
  it: assert the composed result matches applying them one after another, and
  say which is cheaper and why.
- **Inverse mapping** (Day 105): walk each output pixel back through the
  inverse to find where it came from. Forward mapping leaves holes; if you are
  unsure, implement it once and count them.
- **Interpolation you can defend**: nearest-neighbour at minimum. Add bilinear
  and show the difference on a diagonal edge, where it is visible.
- **Vectorised** (Day 104): no Python loop over pixels. Build the coordinate
  grid with NumPy and transform it in one operation. Measure the loop version
  once so you know what you bought, and report the shape of the gap rather
  than a millisecond.
- **Correct output geometry**: decide what happens to the corners of a rotated
  image — crop, or expand the canvas to fit — and implement your choice
  deliberately. Say in `NOTES.md` which you chose and what it costs.
- **Colour handled properly**: a colour image is `(height, width, 3)`. Your
  transformation applies to coordinates, so it should not care about the
  channel axis. If you special-cased it, that is a sign the coordinate grid is
  not doing the work.
- **Determinant reported** (Day 102): print the determinant of the composed
  matrix and say what it predicts about area. Verify it against the actual
  non-empty pixel count within a tolerance you state.

## Steps

1. Start with a small generated pattern, not a photograph. A 9×9 asymmetric
   grid makes a wrong flip obvious; a photograph hides it.
2. Get one 90-degree rotation exactly right, asserted pixel by pixel, before
   anything else. Exact angles first, arbitrary angles after.
3. Add the inverse mapping and confirm your 90-degree case still passes.
4. Move to arbitrary angles and watch the edges. This is where interpolation
   stops being theoretical.
5. Compose two transformations and assert the single matrix matches the
   sequence.
6. Only now load a real image, and expect to be surprised by the corners.
7. Vectorise the coordinate grid and re-run every assertion — they must all
   still pass, because it is the same computation.
8. Add the CLI last, with `--dry-run` printing the composed matrix and the
   predicted output size without writing a file.

## Expected output

- `python transform.py in.png out.png --rotate 90` on a square image → output
  identical to Pillow's own 90-degree rotation, asserted within a tolerance.
- `--rotate 360` → an image equal to the input within a stated tolerance, and
  you can say why it is not exactly equal.
- `--rotate 30 --scale 1.5 --shear-x 0.2 --dry-run` → the composed 3×3 matrix,
  its determinant, and the predicted output dimensions, no file written.
- A run on a colour image → correct output with no channel-specific code path.
- Your timing note → the vectorised grid against the pixel loop, with the
  image size stated and the numbers labelled as one machine.
- The interpolation comparison → nearest-neighbour and bilinear on the same
  diagonal edge, saved side by side.
- `pytest` → every geometric assertion passing, with no network access.

## Validation

- [ ] Every transformation is a matrix you built; Pillow does no geometry.
- [ ] Translation goes through homogeneous coordinates, and you can say why it
      cannot be done without them.
- [ ] Three transformations compose into one matrix, asserted equal to the
      sequence, and you can say which is cheaper.
- [ ] Inverse mapping is used, and you have seen the holes forward mapping
      leaves — counted, not assumed.
- [ ] A 90-degree rotation is asserted pixel-exact.
- [ ] A 360-degree rotation returns the original within a stated tolerance,
      and you can explain the residue.
- [ ] The determinant is reported and checked against the observed area change.
- [ ] No Python loop iterates over pixels; the grid is transformed in one
      NumPy operation.
- [ ] Colour images work with no channel-specific branch.
- [ ] Float comparisons use a stated tolerance, never `==`.
- [ ] `NOTES.md` records your corner decision, your interpolation choice, and
      one thing about a real image that the generated pattern did not prepare
      you for.

## Troubleshooting

- Output is mirrored or transposed? Rows are y and columns are x, and the
  image origin is top-left while the graphs on Day 102 used bottom-left. Use
  an asymmetric test pattern and the error becomes obvious immediately.
- Black holes scattered through the output? Forward mapping. Walk output
  pixels back through the inverse instead.
- Rotation works at 90 degrees and breaks at 30? Your indices are truncating.
  The inverse-mapped position lands between pixels, which is what
  interpolation is for.
- Corners cut off? Expected, unless you expanded the canvas. Decide
  deliberately and write down the choice.
- Colour image comes out wrong? Something indexed the channel axis. The
  transformation should touch coordinates only.
- A 360-degree rotation is not exactly the original? Correct, and worth
  understanding rather than fixing. Every intermediate step resampled.
- Vectorising changed the result? It should not — same computation. Compare
  against your loop version on a small image and find the first differing
  pixel.
