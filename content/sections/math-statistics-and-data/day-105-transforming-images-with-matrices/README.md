# Day 105 — Transforming Images with Matrices

The seventh and final lesson of Week 15 ("Linear Algebra I: Vectors and
Matrices"), and the week's payoff: the day the mathematics acts on something
the reader can *see*.

The organising idea, stated in the second section and returned to in every
section after it:

> **An image is a matrix, so everything Week 15 taught applies to it directly —
> and you transform the COORDINATES, not the pixels.**

The lesson opens by breaking something, in the pattern this course uses for its
strongest days. The reader writes the obvious five-line rotation — walk the
input, send each pixel where it goes — and gets back a picture with twenty-two
of its eighty-one pixels missing, including holes punched straight through
solid ink. That failure is the spine of the day. It is not a rounding error and
it is not fixable by patching the gaps; it is a property of which array the
loop iterates over, and inverting the loop removes it entirely at no cost.

The rest is the mechanics, each landed against real captured output: an image
as an array, with the `(row, column)` versus `(x, y)` trap stated explicitly and
asserted; forward mapping's three distinct failure modes (holes when rotating,
holes as a counting argument when enlarging, silent overwriting when shrinking);
inverse mapping and why it cannot leave holes; the difference between a hole and
clipping, proved rather than described; homogeneous coordinates introduced for
the reason they exist, which is that translation moves the origin and Day 102
proved a linear map cannot; composition, and the measurement that repeated
resampling costs eleven per cent of the picture; interpolation, with the honest
statement of which kinds of image each rule is wrong for; and the closing
section on what affine transformations cannot do — perspective, lens distortion,
dense warps — with what each of those needs instead.

## The question Day 102 deferred, now settled

Day 102 verified by experiment that Pillow's affine coefficients express the
**output-to-input** map, and it explicitly deferred one thing to Day 105: a
half-pixel sampling offset that appeared to make a shear coefficient act on row
0, which the mathematics says is impossible because the shear term is multiplied
by `y`.

It is settled here, by measurement rather than by assertion. **Pillow evaluates
the affine at each output pixel's CENTRE, `(x + 0.5, y + 0.5)`, and floors.**
Row 0 is not at `y = 0`; its centre is at `y = 0.5`, so a shear coefficient of
2.0 contributes exactly one whole pixel even in the top row. The lab separates
the two candidate rules with a single scale experiment that a translation
experiment could never have separated, which is precisely why Day 102 could not
settle it and said so instead of guessing.

## The comparison, and the honesty in it

The day's strongest artifact is the reader's own twenty-odd lines agreeing with
a mature library, and it is reported in both directions:

- **510 of 510** affine transformations produce byte-for-byte identical output.
  Zero differing pixels, exact equality, no tolerance.
- **352 of 360** whole-degree rotations agree. The other **8** — at 30, 60, 120,
  150, 210, 240, 300 and 330 degrees — differ by at most **2 pixels of 81**, and
  every disagreeing sample lands within `2.220e-15` of a pixel boundary, where
  the order of the floating-point additions decides which side of the tie you
  get. The lesson names the failing pixel, quotes its source coordinate
  (`4.999999999999999` where the exact answer is 5), and explains the cause.

The observation worth keeping from that: the eight failing angles are all the
"nice" ones, whose sines and cosines are exactly a half or half the root of
three. The angles nobody would think to test — 37 degrees, 113 degrees — all
agreed. Round numbers are where floating-point ties live.

The bilinear comparison splits just as cleanly and is stated rather than
smoothed: within **1 grey level** of Pillow wherever all four contributing
pixels are inside the image, and up to **118 levels** apart at the border, where
the two extrapolate differently. Naming the boundary of what agrees was
preferred to widening a tolerance until a test went green.

## What this directory contains

| File | What it is |
| --- | --- |
| `index.mdx` | The lesson. Frontmatter plus pure markdown, ~10,800 words, every `LESSON_HEADINGS` H2 in order and the four hands-on H3s. |
| `lesson.yml` | Metadata: id, day, slug, title, section, subsection, week, learning promise, 14 objectives, prerequisites, timings, `last_verified`, tags. |
| `quiz.yml` | Eight questions with `answer_index` spread across 0–3, including one on why inverse mapping is used and one on why translation needs homogeneous coordinates. Explanations teach rather than restate, and each says why the wrong options are wrong. |
| `glossary.yml` | Sixteen terms, from raster image and pixel through to projective transformation. |
| `sources.yml` | Six sources, all verified reachable on 2026-08-17. |
| `visuals.yml` | Both diagrams, with alt text identical to the markdown and descriptions full enough to stand in for the picture. |
| `assets/image-as-matrix-architecture.svg` | Static architecture diagram: a five by five patch drawn as squares beside the same patch as numbers, the row-versus-column trap, and colour as three stacked planes. |
| `assets/inverse-mapping-flow.svg` | Animated flow diagram: forward mapping with its 22 holes, then inverse mapping tracing one output pixel back to a position between input pixels, then the two interpolation answers. |

## How this lesson is rendered

`index.mdx` is rendered by the Astro site from `src/`. The frontmatter supplies
`day` and `title`; everything below it is plain markdown, with no HTML and no
JSX.

The presentation is inherited and is not written into this day (A34): the
centred reading column, centred images, self-scrolling code blocks, the
previous/next cards, the star ask, external links opening in a new tab, and the
branded `DAY 105 / 365` hero image. The two SVGs are referenced as ordinary
markdown images, which means the browser renders them as image documents — so
the flow diagram's animation is CSS `@keyframes` rather than script or SMIL, and
it carries a `prefers-reduced-motion` block that restores a fully legible still
frame.

Both diagrams namespace every class, id and `@keyframes` with `d105a-` and
`d105f-`, because the WordPress/MasterStudy exporter inlines both SVGs into one
HTML document where a `<style>` block is not scoped and `url(#name)` resolves to
the first match on the page.

The LinkedIn post is generated from `lesson.yml` and the lab metadata by
`npm run generate:social`, not written here.

## Related directories

- **Lab:** `labs/sections/math-statistics-and-data/day-105-transforming-images-with-matrices/`
  — "Rotate It Yourself". Twelve functions and twenty-six predictions to write,
  six reference scripts, 64 reference tests, and a 79-check bash harness that
  re-measures every claim in the lesson and demonstrates its own ability to fail.
  — the answer key from real runs, the common mistakes with what each reveals,
  and a 100-point grading rubric.
- **Week 15:** the preceding days are 099 (vectors), 100 (matrices), 101 (matrix
  multiplication), 102 (linear transformations), 103 (dot products) and 104
  (NumPy). This day depends on all six and re-teaches none of them.

## Editing rules

- **Never change a captured number without re-running the lab.** Every figure in
  the lesson — 22 holes, 243, 12 clipped, 16 of 81, 510 of 510, 352 of 360, the
  eight angles, 4.999999999999999, 195.83, 118 grey levels — came from a real
  run on the authoring machine on 2026-08-17 and is asserted in
  `tests/run_tests.sh`. If a number here and a number there disagree, the lab
  is right and this file is wrong.
- **The machine-dependent claims are marked and must stay marked.** The list of
  eight disagreeing angles is specific to this Pillow build and this machine;
  the claim the lab actually asserts is that *every* disagreement sits within
  `1e-9` of a pixel boundary. `expected-output/FIELDS.md` explains the
  distinction. Do not promote the angle list into a guarantee.
- **Alt text must match `visuals.yml` exactly**, and must never contain a `]`,
  which would end the markdown image syntax early and break the image.
- **Only the six sources in `sources.yml`.** OpenCV, scikit-image and
  torchvision are described from their documentation and the lesson states
  plainly that no output is reproduced for them, because they are not installed
  on the authoring machine. Do not add a quoted output for a tool that was not
  run.
- Only NumPy 2.5.2 and Pillow 12.3.0 were run. That sentence appears in the
  Alternatives section and must stay true.
- No AI references anywhere, in any file. No `github.com` or `localhost` URLs;
  all URLs come from `config/course.config.yml` via `scripts/lib/links.mjs`.
- The `## Lesson` section of the lab README is generated by
  `npm run update:links` and must not be edited by hand.
