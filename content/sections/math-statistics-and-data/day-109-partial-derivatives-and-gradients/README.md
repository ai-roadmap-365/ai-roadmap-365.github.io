# Day 109 — Partial Derivatives and Gradients

The second lesson of Week 16 ("Linear Algebra II and Calculus"), and the day the
derivative stops being a number and becomes a vector.

Day 108 taught the derivative of a curve: one input, one slope, measured by
nudging and dividing, with the U-shaped error curve that punishes a step size
chosen too small. Today the ground has two directions to walk in, and "how steep
is it" stops having a single answer. The fix has two halves — freeze all but one
input to get a **partial derivative**, then collect them into a vector to get a
**gradient** — and the second half earns a new name because the resulting object
does something the individual partials do not.

The organising sentence, returned to in every section:

> **A partial derivative asks "if I change only this one input and hold
> everything else still, how does the output respond?" — and collecting all of
> them into a vector gives you the gradient, which points in the direction of
> steepest increase.**

That last clause is what Days 110, 111 and 112 are built on, so this lesson
treats it as a claim requiring evidence rather than a definition to be accepted.
Two facts are **demonstrated rather than asserted**, and the care taken over the
second one is the day's methodological point:

1. **The gradient is the steepest way up.** The lab measures the rate of change
   along 360 bearings, one per degree, each with its own direct central
   difference that never forms a gradient. The winner lands on the gradient's
   bearing every time, within the half-degree the sampling grid allows — and the
   sharper form holds too: the winning rate divided by the gradient's length
   equals the cosine of the sampling gap to nine decimal places.

2. **The gradient is perpendicular to the contour.** The lazy demonstration is
   circular: rotate the gradient ninety degrees, call it the contour direction,
   marvel at the right angle you built. So every contour here is an exact
   algebraic curve derived on paper from the function alone, checked to hold `f`
   constant before it is used (measured drift `1.332e-15`), and the evidence is
   not one small dot product but a dot product that divides by ten each time the
   contour step divides by ten.

Around that spine: directional derivatives as Day 103's dot product doing real
work; the constant gradient of a plane and the outward-pointing gradient of a
bowl, which does *not* point at the minimum on an ellipse and is 26.565° off at
`(1, 1)`; a zero gradient at a minimum, a maximum and a saddle, all three
identical; and the honest statement that distinguishing them needs second
derivatives, which is the Hessian, which is named and not developed.

Three findings in this lesson were discovered while building it rather than
planned, and all three are kept:

1. **A plane's constant gradient becomes unmeasurable when `f` is large.** An
   assertion failed at `(1000, −1000)`. The gradient of `3x − 2y + 5` is exactly
   `(3, −2)` everywhere, and the numerical estimate is out by `5e-8` there and
   has lost its fourth decimal place by `(1e7, −1e7)`. The roundoff bound
   `ε|f| / 2h` tracks the measured error across seven orders of magnitude. The
   lab **asserts the failure** rather than widening the tolerance, so the working
   range of the method is documented by the suite.

2. **A finer sweep does not always give a smaller gap.** At `(1, 1)` on the bowl,
   a 60-direction sweep and a 360-direction sweep leave *exactly* the same
   0.4349° gap, because both grids contain 72 and the gradient's bearing is
   71.5651. The plausible-sounding test was wrong; the reference suite asserts
   the real law instead — that the gap can never exceed half the sampling step.

3. **`numpy.gradient` defaults to first-order accuracy at the boundary.** On an
   exactly sampled quadratic every interior value is exact and the corner comes
   out `(0.5, 1.5)` where `(0, 0)` is correct. `edge_order=2` fixes it exactly.
   Both behaviours are asserted so a future release changing either would fail
   the suite rather than let this page go stale.

The closing AI thread is the one the whole day exists to reach: every parameter
of a model gets a partial derivative, and the gradient is that entire collection.
A three-parameter loss makes it concrete with whole numbers — loss 22.5, gradient
`(−17, −18, −8)`, six evaluations — and the arithmetic that follows is the reason
automatic differentiation exists: two evaluations of the whole function per
parameter means two million forward passes to take one training step on a
million-parameter model.

## What this directory contains

| File | Purpose |
| --- | --- |
| `index.mdx` | The full lesson body (pure markdown after the frontmatter), with all sixteen standard sections |
| `lesson.yml` | Lesson metadata: id, slug, learning promise, fifteen objectives, prerequisites, timings, tags |
| `quiz.yml` | 8 multiple-choice questions with answers and teaching explanations, including one on why the gradient is perpendicular to the contour and one on what a zero gradient does not tell you |
| `glossary.yml` | 15 precise definitions of the lesson's key terms |
| `sources.yml` | The six verified external sources this lesson draws on |
| `visuals.yml` | Registry of the lesson's two diagrams with titles, alt text and full descriptions |
| `assets/gradient-anatomy-architecture.svg` | Static architecture diagram: a contour map with the two partial derivatives drawn as arrows, composing into the gradient, meeting the contour tangent at a right angle, with the two frozen-variable slices shown beside it |
| `assets/steepest-ascent-flow.svg` | Animated flow diagram (A30): eight bearings tried in turn with the measured rate for each, the gradient's bearing winning at 6.3246 against a next-best 6.1962 |

## How this lesson is rendered

`index.mdx` provides the lesson body, and the sidecar YAML files travel with it:
the site layout renders the body at the day route, injects the quiz from
`quiz.yml`, the glossary from `glossary.yml`, and the source list from
`sources.yml`, and uses `lesson.yml` for navigation, metadata and time estimates.
Images are referenced from `index.mdx` with relative paths into `assets/`, and
their alt text must stay identical to `visuals.yml`. All cross-links — to the lab
and to neighbouring days — are generated by the layout from central
configuration; never hard-code repository or site URLs inside content files.

`steepest-ascent-flow.svg` is animated with CSS `@keyframes` inside the file, so
it animates wherever it is rendered as an image and prints as a still. It carries
a `@media (prefers-reduced-motion: reduce)` block that disables every animation
and restores the resting state, and the still frame carries the whole meaning on
its own — all eight arrows are drawn and labelled, all eight bars are filled with
their measured values printed, and the winner is permanently heavier and blue.
Both SVGs prefix every class, id and keyframes name — `d109a-` in the
architecture diagram, `d109f-` in the flow diagram — because an inlined SVG's
`<style>` block is not scoped to that SVG and `url(#name)` resolves
document-wide, so two diagrams on one page would otherwise restyle each other.

One implementation note for anyone editing the flow diagram: the "settle" pulse
animates `stroke-width` only. An earlier version animated the `r` attribute of a
circle, which is not reliably CSS-animatable across browsers. Do not reintroduce
it.

## Related directories

- Matching hands-on lab:
  `labs/sections/math-statistics-and-data/day-109-partial-derivatives-and-gradients/`
  — "Which Way Is Uphill?". The learner writes eight functions in
  `starter/gradients.py` and fifty-one predictions in `starter/answers.py`,
  checking themselves against a suite that skips unattempted work rather than
  failing it. The reference implementation, seven annotated demonstration scripts
  and 271 reference tests live in `examples/`, and every captured output in
  `expected-output/` came from a real run through a real lab-local virtual
  environment.
- Instructor solution:
- Day 110 introduces the chain rule, which is how a gradient is computed through
  composed functions — and the reason automatic differentiation is possible.
- Day 111 turns "step against the gradient" into gradient descent from scratch.
  This lesson takes a single such step, at eight step sizes, and shows the loss
  falling and then overshooting.

## Editing rules

- Every file must ship complete: no stub text, no unfinished sections, no filler
  — if a fact or figure is not verified, leave it out rather than approximating
  it.
- **Every block of output shown in this lesson was captured from a real run on
  the authoring machine on 2026-08-17**, with Python 3.14.0, numpy 2.5.2 and
  pytest 9.1.1 on macOS 26.5.2 (Apple Silicon, arm64). The captures live in the
  lab's `expected-output/` directory. If you change a number here, re-run the lab
  and change it there too, and keep the indentation identical — these are quotes,
  not paraphrases.
- **Every exact gradient in this lesson was differentiated by hand**, and the
  numerical ones are checked against it rather than the other way round. The
  values `(2, 6)`, `(3, −2)`, `(13, 4)` and `(−17, −18, −8)` are algebra and are
  re-derivable with a pencil in under a minute each. Do not replace any of them
  with a computed figure.
- **Every tolerance in this lesson and its lab is derived rather than tuned.**
  `starter/surfaces.py` explains where each one came from, and one reference test
  asserts that `GRADIENT_TOL` has at least tenfold headroom over the worst
  measured error rather than merely scraping past. Do not widen a tolerance to
  make something pass; the lesson's own security section explains why that
  particular fix is worse than the failure it hides.
- **The three unplanned findings listed at the top of this file are load-bearing
  and must not be tidied away.** The roundoff limit at large `|f|` is the reason
  the implications section has a scalability paragraph and the reason one test
  asserts a failure. The 60-versus-360 sweep coincidence is the reason the
  reference suite asserts a bound rather than a monotone improvement, and it is
  documented in `expected-output/FIELDS.md`. The `numpy.gradient` `edge_order`
  default is asserted in two places precisely so it cannot silently stop being
  true.
- The historical facts in this lesson come only from the Wikipedia article listed
  in `sources.yml`: Condorcet's use of `∂` in 1770 for partial differences,
  Legendre creating the modern notation in 1786 and later abandoning it, and
  Jacobi reintroducing it in 1841. **Do not add names or dates that are not in a
  cited source.** In particular this lesson deliberately writes no dated history
  of the nabla symbol, because the cited pages state what it is and not who
  introduced it when.
- The quoted passages from Wikipedia — the definition of a partial derivative
  with "the others held constant", the gradient's direction-and-magnitude
  statement, the "unique vector field whose dot product with any unit vector"
  definition, the orthogonality-to-level-sets sentence, the non-differentiable
  counterexample that "fails to point towards the steepest ascent in some
  orientations", the naming of a stationary point, the description of `∇` as an
  upside-down triangle pronounced "del", the tangent-line description of partial
  differentiation, and the 40%-slope road example — are verbatim from the pages
  listed in `sources.yml`, verified on 2026-08-17. Keep them verbatim or drop the
  quotation marks.
- **JAX, PyTorch and SymPy are not installed and no output from them is
  reproduced anywhere.** They are described from their documentation and are
  explicitly marked as not run here. Keep that marking; it is the difference
  between a description and a claim.
- No prices, tier limits or free-tier allowances for any product may be written
  here. Licences are stated qualitatively (BSD 3-Clause for NumPy, MIT for
  pytest) and no others are asserted.
- No parameter count for any named real model appears here. The scaling table
  uses round illustrative numbers — 3, 1,000, 1,000,000, 1,000,000,000 — and
  attributes them to nothing.
- All data is invented and is stated to be invented: the six surfaces, the five
  probe points, and the four samples of the three-parameter model, which were
  chosen so every step can be checked by hand. Keep any replacement equally
  checkable.
- Cite only sources listed in `sources.yml`; do not add URLs elsewhere in the
  content.
- When you revise any file in this directory, update `last_verified` in
  `lesson.yml` to the revision date.
- Keep image alt text in `index.mdx` and `visuals.yml` identical, and keep the
  exact H2 heading strings intact — the lesson validator checks them. Alt text
  must contain no square brackets: a closing bracket ends markdown image syntax
  and the alt renders broken.
- If you edit either SVG, keep every class, id and keyframes name behind its
  file's prefix (`d109a-` or `d109f-`), keep the `prefers-reduced-motion` block,
  and re-check with `xmllint --noout`.
