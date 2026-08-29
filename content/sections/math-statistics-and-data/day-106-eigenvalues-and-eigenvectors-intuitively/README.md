# Day 106 — Eigenvalues and Eigenvectors, Intuitively

The first lesson of Week 16 ("Linear Algebra II and Calculus"), and the day the
course crosses the topic that loses more people than any other in linear
algebra.

The organising idea, stated in the second section and returned to in every
section after it:

> **Most vectors get knocked off their line when a matrix acts on them. A few do
> not — they only stretch or squash. Those are the eigenvectors, and how much
> they stretch is the eigenvalue.**

## What this directory contains

| File | What it is |
| --- | --- |
| `index.mdx` | The lesson. Frontmatter plus pure markdown, ~10,800 words, every `LESSON_HEADINGS` H2 in order and the four hands-on H3s. |
| `lesson.yml` | Metadata: id, day, slug, title, section, subsection, week, learning promise, 12 objectives, prerequisites, timings, `last_verified`, tags. |
| `quiz.yml` | Eight questions with `answer_index` spread across 0–3, including one on why a plane rotation has no real eigenvectors and one on the sign-and-scale ambiguity. Explanations teach rather than restate, and each says why the wrong options are wrong. |
| `glossary.yml` | Twelve terms, from eigenvector and eigenvalue through to spectral radius and multiplicity. |
| `sources.yml` | Six sources, all verified reachable on 2026-08-17. |
| `visuals.yml` | Both diagrams, with alt text identical to the markdown and descriptions full enough to stand in for the picture. |
| `assets/eigenvector-anatomy-architecture.svg` | Static architecture diagram: twelve directions around a circle, ten knocked off their line and two only stretched, beside the anatomy of `A v = λ v`. |
| `assets/power-method-flow.svg` | Animated flow diagram: a vector swinging from 20.17° onto the eigen-line at 45°, with the three-line loop and the real measured iteration table. |

## The pedagogical decision this day is built on

**The lesson does not open with the characteristic equation.** It opens by
showing that equation and saying plainly that as an opening line it has ended
more people's relationship with linear algebra than any other sentence in
mathematics — then putting it away.

What replaces it is a measurement. Apply `[[4, 1], [2, 3]]` to twenty-four unit
vectors spread around the circle, print the angle between each input and its
output, and watch one column dip to exactly zero. The concept arrives as
something observed before it is anything defined.

The characteristic equation then returns, on page four, **derived rather than
quoted**: `A v = λ v` becomes `(A − λI) v = 0`, which says a non-zero vector is
sent to the origin, and Day 102 already established that only a matrix with zero
determinant does that. By the time `det(A − λI) = 0` appears, every symbol in it
stands for something the reader has a picture of.

The sustained analogy is a **rubber sheet with a printed grid, pinned at the
centre and pulled**. It is carried through negative eigenvalues (a fold),
eigenvalue zero (crushed flat, and therefore not undoable — Day 102's
determinant), uniform scaling (every arrow keeps its line), rotation (no arrow
does), the sign ambiguity (a line through the pin, not an arrowhead) and
repeated application (the fastest-growing direction takes over). The lesson also
states where the analogy breaks, which is that rubber has physical limits and a
linear map does not.

## The measurements this lesson reports, and why they are stated the way they are

Every number in `index.mdx` came from a real run on the authoring machine on
2026-08-17 and is asserted in `tests/run_tests.sh`. Four are worth calling out
because each one records a place where measurement beat the received wisdom.

**`numpy.linalg.eig` returns `complex128` on a real matrix with two real
eigenvalues, contradicting its own docstring.** The docstring shipped with numpy
2.5.2 says the array "will be of complex type, unless the imaginary part is zero
in which case it will be cast to a real type". The imaginary part *is* zero and
the cast does *not* happen — for `A`, for `numpy.eye(2)`, for
`numpy.diag([1., 2., 3.])` and for an integer matrix. The lesson quotes the
docstring exactly, states what was observed, and says that if a future version
performs the cast, the lab test going red is the **correct** outcome and this
text needs updating. Quiz question 3 and starter exercise 3d both build on it.

**A shear has one eigen-line while `eig` returns two columns, and the
diagonalisation attempt fails silently.** Algebraic multiplicity 2, geometric
multiplicity 1, confirmed independently by algebra and by a 180,000-direction
brute-force sweep. `numpy.linalg.inv` on the singular eigenvector matrix does not
raise — determinant `2.2e-16`, entries around `4.5e15`, and a clean, plausible,
completely wrong identity matrix comes back. The lesson says the reliable check
is the condition number, not the absence of an exception.

**The Rayleigh quotient's quadratic convergence is conditional, and the
condition is usually dropped.** Measured, the quotient error over the squared
angle locks onto `2.0000` for the symmetric matrix and runs away for this
lesson's non-symmetric `A`, where it converges merely linearly. The condition is
orthogonal eigenvectors, which symmetry guarantees; `A`'s eigen-lines meet at
`71.5651` degrees rather than 90. The lesson reports the measurement first and
then restores the textbook claim with its condition attached.

**The sign ambiguity is treated as the day's central practical lesson rather
than a footnote.** PCA recovers `30.101134` degrees from a cloud built along
`30.0` and returns the component pointing the *opposite* way along that line, so
`numpy.allclose` returns `False` on an answer that is exactly right (absolute
cosine `0.9999984422`). Every comparison in the lab goes through absolute cosine,
`expected-output/FIELDS.md` states that a flipped sign in a reader's output is
not a difference at all, and quiz question 4 is built on it.

## How this lesson is rendered

`index.mdx` is rendered by the Astro site from `src/`. The frontmatter supplies
`day` and `title`; everything below it is plain markdown, with no HTML and no
JSX.

The presentation is inherited and is not written into this day (A34): the
centred reading column, centred images, self-scrolling code blocks, the
previous/next cards, the star ask, external links opening in a new tab, and the
branded `DAY 106 / 365` hero image. The two SVGs are referenced as ordinary
markdown images, which means the browser renders them as image documents — so
the flow diagram's animation is CSS `@keyframes` rather than script or SMIL, and
it carries a `prefers-reduced-motion` block that parks the swinging arrow at its
converged position and turns the marching dashes into a solid line.

Both diagrams namespace every class, id and `@keyframes` with `d106a-` and
`d106f-`, because the WordPress/MasterStudy exporter inlines both SVGs into one
HTML document where a `<style>` block is not scoped and `url(#name)` resolves to
the first match on the page.

The LinkedIn post is generated from `lesson.yml` and the lab metadata by
`npm run generate:social`, not written here.

## Related directories

- **Lab:** `labs/sections/math-statistics-and-data/day-106-eigenvalues-and-eigenvectors-intuitively/`
  — "The Vectors That Keep Their Direction". Six functions and twenty-six
  predictions to write, six reference scripts, 94 reference tests, and a
  110-check bash harness that re-measures every claim in the lesson and
  demonstrates its own ability to fail.
  — the answer key from real runs, the common mistakes with what each reveals,
  and a 100-point grading rubric.
- **Week 15:** days 099 (vectors), 100 (matrices), 101 (matrix multiplication),
  102 (linear transformations), 103 (dot products), 104 (NumPy) and 105
  (transforming images). This day depends on all seven and re-teaches none of
  them. **Day 102 is the load-bearing one**: the derivation of the characteristic
  equation, the meaning of eigenvalue zero, and the table of standard
  transformations all rest on it directly.

## Editing rules

- **Never change a captured number without re-running the lab.** Every figure in
  the lesson — the 24-direction table, 116.565051, 5 and 2, 25 iterations, 962
  iterations, 0.399999, 30.101134, 0.9999984422, 136.583965, 2.902251, 0.9794,
  10.46x, 1.990e-13 — came from a real run on 2026-08-17 and is asserted in
  `tests/run_tests.sh`. If a number here and a number there disagree, the lab is
  right and this file is wrong.
- **The machine-dependent claims are marked and must stay marked.** The
  `eig`/`eigh` timing ratio is one machine on one day and is asserted nowhere;
  what the lab asserts beside it is that the two routines' 400 eigenvalues agree
  to `1.990e-13`. The `complex128` observation is a measurement of one NumPy
  version, quoted against its own docstring, and must not be promoted into a
  guarantee. `expected-output/FIELDS.md` explains the distinction.
- **The sign of any eigenvector may differ on another machine, and the lesson
  must keep saying so.** Do not "correct" a sign anywhere in this day.
- **Alt text must match `visuals.yml` exactly**, and must never contain a `]`,
  which would end the markdown image syntax early and break the image.
- **Only the six sources in `sources.yml`.** SciPy, PyTorch and scikit-learn are
  described from their documentation, and the Alternatives section states
  plainly that only `numpy.linalg.eig` and `numpy.linalg.eigh` were actually run
  and that no output is reproduced for the others. Do not add a quoted output
  for a tool that was not run.
- Only NumPy 2.5.2 and pytest 9.1.1 were run. That must stay true.
- No AI references anywhere, in any file. No `github.com` or `localhost` URLs;
  all URLs come from `config/course.config.yml` via `scripts/lib/links.mjs`.
- The `## Lesson` section of the lab README is generated by
  `npm run update:links` and must not be edited by hand.
