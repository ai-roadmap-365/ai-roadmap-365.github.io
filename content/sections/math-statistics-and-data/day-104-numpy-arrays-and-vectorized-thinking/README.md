# Day 104 — NumPy: Arrays and Vectorized Thinking

The sixth lesson of Week 15 ("Linear Algebra I: Vectors and Matrices"), and the
day NumPy stops being the answer key beside a from-scratch implementation and
becomes the subject.

Days 99 to 103 used NumPy as a checking tool: vectors, matrices, matrix
multiplication, linear transformations, dot products and cosine similarity were
each built by hand and then verified against the library. Today the library
itself is what is being taught, and the thing being taught is not an API — it is
a change of mental habit, from *loop over the items and do the thing* to
*express the whole operation on the whole array and let the library do the loop
in C*.

The organising sentence, returned to in every section:

> **A vectorised expression is the SAME computation as the loop, not a
> different one — you have moved the loop, not removed it.**

The lesson opens by breaking something, in the pattern this course uses for its
strongest days, and what it breaks is its own claim. The first measurement shown
is `sys.getsizeof` on a list of a million integers against `nbytes` on the
equivalent array: 8,000,056 against 8,000,000, a ratio of 1.0000. The obvious
measurement says a list is exactly as compact as an array. That is a real
capture from a real run, and it is wrong in a way that is more instructive than
the right answer would have been alone — `getsizeof` measures the list object
and its pointers, never the 28-byte integer objects those pointers reach, and
the honest total is 36,000,056. That failure sets the tone for the whole day: a
measurement is only as good as the question it answers.

The rest is the mechanics, each landed against real captured output: the three
facts that make an ndarray (fixed dtype, contiguous block, shape with strides,
which are three faces of one decision); the eight array constructors with when
each is right; universal functions; dtypes as a promise you can break by
accident, with an int8 wrapping silently from 127 to -128 and a float32 unable
to distinguish 16,777,216 from its successor; boolean masking in full, including
both separate causes of the ambiguous-truth-value `ValueError`; the axis rule;
views versus copies; `argsort` turning Day 103's similarity scores into a
top-three search; and `nan`, which is not equal to itself.

The closing section is the one the day exists for, and it argues against the
rest of the lesson: three measured situations in which the loop is the better
code — a four-element array where the comprehension beat NumPy at 0.108
microseconds against 0.325, a running balance whose sequential dependence has no
one-line equivalent, and a pairwise table that would need 80 GB at a hundred
thousand points.

Three findings in this lesson were discovered while building it rather than
planned, and all three are kept:

1. `sys.getsizeof` on the list makes the memory comparison come out at 1.0000,
   which contradicts the received wisdom until you understand what it measured.
2. On numpy 2.5.2 the int8 overflow emits **no warning at all**. The reference
   suite asserts the *absence* of the warning, so a future NumPy that started
   emitting one would fail the suite rather than let this page go stale.
3. `x ** 0.5` disagrees with `numpy.sqrt` on 1,390 of the lab's million values,
   always by one unit in the last place, while `math.sqrt` agrees on all of
   them. IEEE-754 requires square root to be correctly rounded and `pow` makes
   no such promise. This is the sharpest available illustration of the day's
   organising sentence: "the same computation" is a claim about the operation,
   not about anything that would agree in exact arithmetic.

## What this directory contains

| File | Purpose |
| --- | --- |
| `index.mdx` | The full lesson body (pure markdown after the frontmatter), with all sixteen standard sections |
| `lesson.yml` | Lesson metadata: id, slug, learning promise, fourteen objectives, prerequisites, timings, tags |
| `quiz.yml` | 8 multiple-choice questions with answers and teaching explanations, including one on why `and` fails on arrays and one on views versus copies |
| `glossary.yml` | 17 precise definitions of the lesson's key terms |
| `sources.yml` | The six verified external sources this lesson draws on |
| `visuals.yml` | Registry of the lesson's two diagrams with titles, alt text and full descriptions |
| `assets/ndarray-memory-architecture.svg` | Static architecture diagram: a list's scattered pointer-and-object layout beside an ndarray's header and contiguous block, with both measured byte totals and the misleading `getsizeof` comparison across the foot |
| `assets/vectorized-vs-loop-flow.svg` | Animated flow diagram (A30): the loop visiting one element at a time against the whole block lighting at once, with the measured medians and a note that the vectorised loop still happens, just in C |

## How this lesson is rendered

`index.mdx` provides the lesson body, and the sidecar YAML files travel with it:
the site layout renders the body at the day route, injects the quiz from
`quiz.yml`, the glossary from `glossary.yml`, and the source list from
`sources.yml`, and uses `lesson.yml` for navigation, metadata and time
estimates. Images are referenced from `index.mdx` with relative paths into
`assets/`, and their alt text must stay identical to `visuals.yml`. All
cross-links — to the lab and to neighbouring days — are generated by the layout
from central configuration; never hard-code repository or site URLs inside
content files.

`vectorized-vs-loop-flow.svg` is animated with CSS `@keyframes` inside the file,
so it animates wherever it is rendered as an image and prints as a still. It
carries a `@media (prefers-reduced-motion: reduce)` block that disables every
animation and restores the resting state, and the still frame carries the whole
meaning on its own — every figure, label and caption is present without motion.
Both SVGs prefix every class, id and keyframes name — `d104a-` in the
architecture diagram, `d104f-` in the flow diagram — because an inlined SVG's
`<style>` block is not scoped to that SVG and `url(#name)` resolves
document-wide, so two diagrams on one page would otherwise restyle each other.

## Related directories

- Matching hands-on lab:
  `labs/sections/math-statistics-and-data/day-104-numpy-arrays-and-vectorized-thinking/`
  — "Stop Writing the Loop". The learner writes ten functions in
  `starter/vectorize.py`, three of them twice (once as a loop, once vectorised),
  and makes forty-two predictions in `starter/answers.py`, checking themselves
  against a suite that skips unattempted work rather than failing it. The
  reference implementation, seven annotated demonstration scripts and 107
  reference tests live in `examples/`, and every captured output in
  `expected-output/` came from a real run through a real lab-local virtual
  environment.
- Instructor solution:
- Day 105 applies these arrays to a real image, where a shear and a rotation
  stop being abstractions and a dtype choice becomes visible in pixels.

## Editing rules

- Every file must ship complete: no stub text, no unfinished sections, no filler
  — if a fact or figure is not verified, leave it out rather than approximating
  it.
- **Every block of output shown in this lesson was captured from a real run on
  the authoring machine on 2026-08-17**, with Python 3.14.0, numpy 2.5.2 and
  pytest 9.1.1 on macOS 26.5.2 (Apple Silicon, arm64). The captures live in the
  lab's `expected-output/` directory. If you change a number here, re-run the
  lab and change it there too, and keep the indentation identical — these are
  quotes, not paraphrases.
- **Every timing in this lesson is labelled as one machine on one day, and no
  test anywhere asserts a duration.** The lab's tests assert only that the
  vectorised version is at least twenty times faster, which is a claim about the
  shape of the gap. Do not tighten that number to match the measured 106x–134x;
  a test that asserted the measured figure would fail on a slower machine and
  teach the reader that the suite is unreliable rather than that their hardware
  is different. `expected-output/FIELDS.md` in the lab records exactly which
  figures may move.
- **This lesson deliberately writes no dated history of NumPy**, and the
  Historical background section says so in as many words. Neither of the two
  NumPy documentation pages in `sources.yml` carries a dated account of who
  built what and when, so rather than reach for a half-remembered version number
  and a founder's name, the section shows the history still visible in the
  software: the legacy `numpy.random.seed` docstring, the promotion rule that
  changed at NumPy 2, and the version number itself. Do not add names or dates
  that are not in a cited source.
- The four quoted passages from NumPy's documentation — the ndarray definition
  with its homogeneity and fixed-size constraints, the statement about
  homogeneous data on the CPU, the view-versus-copy contrast with lists, and the
  broadcasting definition with "looping occurs in C instead of Python" — are
  verbatim from the pages listed in `sources.yml`, verified on 2026-08-17. The
  `numpy.random.seed` docstring quoted in the Historical background section was
  printed from the installed numpy 2.5.2 rather than from a web page. Keep all
  five verbatim or drop the quotation marks.
- The three unplanned findings listed at the top of this file are load-bearing
  and must not be tidied away. The `getsizeof` ratio of 1.0000 is the lesson's
  opening and the reason the memory section is structured as a wrong
  measurement followed by a right one. The absence of an overflow warning is
  asserted by a reference test precisely so that it cannot silently stop being
  true. And the 1,390 disagreements between `x ** 0.5` and `numpy.sqrt` are the
  sharpest illustration in the day of what "the same computation" does and does
  not mean — note that the count itself depends on the maths library Python was
  built against, so the lab asserts the direction rather than the number.
- NumPy 2.5.2 is the only library anything was run on. PyTorch, JAX, CuPy, Dask
  and pandas are described from their documentation and are explicitly marked as
  not installed, with no output reproduced. Keep that marking; it is the
  difference between a description and a claim.
- No prices, tier limits or free-tier allowances for any product may be written
  here. Licences are stated qualitatively (BSD 3-Clause for NumPy, MIT for
  pytest) and no others are asserted.
- All data is invented and is stated to be invented — the twenty readings from a
  seeded generator, the six articles carried unchanged from Days 99 and 103, and
  the eight sample values in the architecture diagram. Keep any replacement
  equally checkable by hand.
- Cite only sources listed in `sources.yml`; do not add URLs elsewhere in the
  content.
- When you revise any file in this directory, update `last_verified` in
  `lesson.yml` to the revision date.
- Keep image alt text in `index.mdx` and `visuals.yml` identical, and keep the
  exact H2 heading strings intact — the lesson validator checks them. Alt text
  must contain no square brackets: a closing bracket ends markdown image syntax
  and the alt renders broken.
- If you edit either SVG, keep every class, id and keyframes name behind its
  file's prefix (`d104a-` or `d104f-`), keep the `prefers-reduced-motion` block,
  and re-check with `xmllint --noout`.
