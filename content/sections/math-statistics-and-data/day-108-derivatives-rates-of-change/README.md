# Day 108 — Derivatives: Rates of Change

The third lesson of Week 16 ("Linear Algebra II and Calculus"), and **the first
calculus in the course**. Days 99 to 107 were linear algebra: vectors, matrices,
matrix multiplication, transformations, dot products, NumPy, images,
eigenvalues, norms and distances. Today the subject changes.

It is also the first of five days that build directly to a working training
loop: 108 derivatives, 109 partial derivatives and gradients, 110 the chain
rule, 111 gradient descent from scratch, 112 visualising optimization. The
lesson says where the reader is going once, in the opening section, and then
gets on with the day.

The organising sentence, returned to in every section:

> **A derivative is a rate of change, and the reason it matters for AI is that
> it tells you which way to move to make something smaller.**

## The audience decision this lesson is built around

The reader has 107 days of computing, eight days of linear algebra, and **no
calculus at all**. Many carry active anxiety about the word. So the lesson does
three things deliberately, and none of them should be undone by a later edit:

1. **It does not open with limits or epsilon-delta.** It opens with speed,
   because every reader already understands speed as a rate. A car covers 144
   metres in 6 seconds; a speedometer shows a number at an instant; the
   derivative is the machine that turns the first into the second. That sentence
   arrives before any notation.
2. **The limit is met as an observation, not as a definition.** The reader
   computes the slope over intervals of 1, 0.1, 0.01 and 0.001, sees 7, 6.1,
   6.01 and 6.001, and watches the sequence settle. Only afterwards is the word
   "limit" attached to what they just watched. The Historical background section
   points out that this is the order in which humanity actually understood it —
   calculus was used for about a century and a half before anyone could define
   it rigorously — so the reversal is defensible rather than a simplification.
3. **Every rule is checked against a number.** No rule in this lesson is stated
   without a measurement beside it, including the fact that `e` is special,
   which is shown by measuring the slope of `bˣ` at zero for five bases and
   observing 0.693, 0.916, 1.000, 1.099 and 2.303 — the natural logarithms of
   2, 2.5, e, 3 and 10.

## The two uncomfortable findings the lesson is built on

Both are measurements, both contradict the intuitive answer, and both are
load-bearing.

**Making `h` smaller eventually makes the answer worse.** Truncation error
shrinks with `h` and rounding error grows with it, so the total error is
U-shaped and its minimum is nowhere near zero. The lab measures it across 27
step sizes from 1e-1 to 1e-14. At `h = 1e-300` a forward difference returns
exactly `0.0`, silently, because `exp(1 + 1e-300)` and `exp(1)` are the same
float64.

**A numerical derivative answers questions that have no answer.** `|x|` has no
derivative at zero; the central difference returns `0.0` anyway, which is both
confident and plausible-looking. ReLU's returns `0.5`, which is neither of the
two values a framework could defensibly choose. That corner is inside every
neural network the reader will train.

## Four findings discovered while building the lab, all kept

1. **`numpy.gradient` gives two different answers to the same question.** With a
   scalar spacing it is bit-for-bit identical to the from-scratch central
   difference. With an array of the same evenly spaced coordinates it uses the
   general unevenly-spaced route and differs by 1.879e-11. Both are correct.
   Asserted in both directions.
2. **The error curve is not monotone near its minimum.** On the captured run
   `h = 1e-6` is worse than both `h = 3.162e-6` and `h = 3.162e-7`. This is why
   the lab's `is_u_shaped` test asks about the two ends against the middle
   rather than demanding a monotone descent — a test demanding smoothness here
   would demand something untrue.
3. **The second difference at a corner is exactly `2/h`.** It diverges as `h`
   shrinks, which makes it a far better corner detector than the first
   derivative's calm `0.0`.
4. **`x⁴` at 0 is a genuine minimum the second-derivative test cannot see.** It
   reads identically to `x³` at 0, which is not a minimum. The lab's classifier
   returns `"undecided"` for both and a test asserts it, because reporting
   `"minimum"` would be right by accident on one of the two.

## What this directory contains

| File | Purpose |
| --- | --- |
| `index.mdx` | The full lesson body (pure markdown after the frontmatter), with all sixteen standard sections |
| `lesson.yml` | Lesson metadata: id, slug, learning promise, fifteen objectives, prerequisites, timings, tags |
| `quiz.yml` | 8 multiple-choice questions with answers and teaching explanations, including one on why a smaller `h` eventually makes the answer worse and one on what a zero derivative does and does not tell you |
| `glossary.yml` | 19 precise definitions of the lesson's key terms |
| `sources.yml` | The six verified external sources this lesson draws on |
| `visuals.yml` | Registry of the lesson's two diagrams with titles, alt text and full descriptions |
| `assets/derivative-anatomy-architecture.svg` | Static architecture diagram: three panels showing the same secant construction at h = 2, 0.5 and 0.1, with rise, run and the computed slope labelled at each stage, the tangent overlaid on the third, and the whole sequence tabulated with its algebra across the foot |
| `assets/shrinking-interval-flow.svg` | Animated flow diagram (A30): four secants fanning from the fixed point, the second point sliding down the curve, and a readout whose rows light in step — width and slope updating at every stage, with the tangent slope marked |

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

`shrinking-interval-flow.svg` is animated with CSS `@keyframes` inside the file,
so it animates wherever it is rendered as an image and prints as a still. It
carries a `@media (prefers-reduced-motion: reduce)` block that disables every
animation and restores the resting state, and the still frame carries the whole
meaning on its own — all four secants, both tables, every width and every slope
are present without motion. Both SVGs prefix every class, id and keyframes name
— `d108a-` in the architecture diagram, `d108f-` in the flow diagram — because
an inlined SVG's `<style>` block is not scoped to that SVG and `url(#name)`
resolves document-wide, so two diagrams on one page would otherwise restyle each
other.

## Related directories

- Matching hands-on lab:
  `labs/sections/math-statistics-and-data/day-108-derivatives-rates-of-change/`
  — "Watch the Slope Settle". The learner writes ten functions in
  `starter/derivatives.py` and makes forty-two predictions in `starter/answers.py`,
  checking themselves against a suite that skips unattempted work rather than
  failing it. The reference implementation, seven annotated demonstration
  scripts and 178 reference tests live in `examples/`, and every captured output
  in `expected-output/` came from a real run through a real lab-local virtual
  environment.
- Instructor solution:
- Day 109 takes the same definition into more than one input variable and calls
  the result a gradient. Day 111 writes the loop that follows it downhill.

## Editing rules

- Every file must ship complete: no stub text, no unfinished sections, no filler
  — if a fact or figure is not verified, leave it out rather than approximating
  it.
- **Every block of output shown in this lesson was captured from a real run on
  the authoring machine on 2026-08-17**, with Python 3.14.0, numpy 2.5.2 and
  pytest 9.1.1 on macOS 26.5.2 (Apple Silicon, arm64), through a real lab-local
  `.venv` created by the lab's documented setup commands. The captures live in
  the lab's `expected-output/` directory. If you change a number here, re-run
  the lab and change it there too, and keep the indentation identical — these
  are quotes, not paraphrases.
- **The position of the bottom of the U is reported, never asserted.** The
  measured optima — `h = 1.000e-08` for the forward rule and `h = 3.162e-06` for
  the central one — are one machine on one day. The lab asserts only the shape:
  an interior minimum, both ends more than a hundredfold worse, each optimum
  inside a documented band, and each within a factor of ten of the balance
  prediction. Do not tighten those to the measured values;
  `expected-output/FIELDS.md` in the lab records exactly which figures may move
  and why.
- **Every tolerance in the lab is derived, not tuned.** `examples/dataset.py`
  writes out the truncation and rounding arithmetic beside each one, and a
  reference test asserts that none of them is loose enough to be meaningless. If
  a future change makes a test fail, do not widen the tolerance — find out which
  of the two error terms moved.
- **The Historical background section deliberately carries few dates.** It names
  Fermat, Newton and Leibniz, places the invention in the seventeenth century
  and the rigorous limit definition in the nineteenth, and otherwise shows the
  history that is still visible in the notation. Do not add years, places or
  attributions that are not checkable against `sources.yml`.
- **SymPy, JAX and PyTorch are not installed and no output from any of them is
  reproduced anywhere.** They are described from their documentation and are
  explicitly marked as not run here. Keep that marking; it is the difference
  between a description and a claim.
- **No claim is made about which value any particular framework uses for ReLU's
  derivative at zero.** The lesson says the choice is a convention between 0 and
  1, says which value the central difference produces (0.5), and tells the
  reader to check their own framework's documentation. Do not replace that with
  a remembered answer.
- No prices, tier limits or free-tier allowances for any product may be written
  here. Licences are stated qualitatively (BSD 3-Clause for NumPy, MIT for
  pytest, BSD for SymPy) and no others are asserted.
- All data is invented and is stated to be invented — the seven car readings are
  `4t²`, and every function differentiated is written out in the lab's
  `dataset.py`. Keep any replacement equally checkable by hand.
- Cite only sources listed in `sources.yml`; do not add URLs elsewhere in the
  content.
- When you revise any file in this directory, update `last_verified` in
  `lesson.yml` to the revision date.
- Keep image alt text in `index.mdx` and `visuals.yml` identical, and keep the
  exact H2 heading strings intact — the lesson validator checks them. Alt text
  must contain no square brackets: a closing bracket ends markdown image syntax
  and the alt renders broken.
- If you edit either SVG, keep every class, id and keyframes name behind its
  file's prefix (`d108a-` or `d108f-`), keep the `prefers-reduced-motion` block,
  and re-check with `xmllint --noout`.
