# Day 110 — The Chain Rule

The fifth lesson of Week 16 ("Linear Algebra II and Calculus"), and **the hinge
of the whole calculus arc**. Day 108 introduced derivatives to a reader with no
calculus. Day 109 introduced partial derivatives and the gradient. Today those
rates get connected end to end; Day 111 writes the loop that follows them
downhill, and Day 112 visualises it.

The organising sentence, returned to in every section:

> **When one thing depends on another which depends on another, the rates
> multiply — and when a thing reaches the output by more than one route, the
> contributions add.**

The day's purpose is to make backpropagation feel **inevitable rather than
magical**. The lesson never introduces it as a new algorithm. It builds the
chain rule from gears, extends it to graphs, explains reverse mode by cost, and
then observes — in one sentence, near the end — that backpropagation is what
you have just been doing. Do not let a later edit turn that into a reveal.

## The audience decision this lesson is built around

The reader has 109 days of computing and exactly two days of calculus. So:

1. **The opening is arithmetic, not notation.** Two gears, 2 × 3 = 6. The
   reader gets the whole rule before any symbol appears, and the lesson says
   explicitly that the notation is bookkeeping on top of that sentence.
2. **The cancelling mnemonic is taught AND undermined, in that order.** The
   `du` appearing to cancel is presented as a genuinely brilliant piece of
   notation design by Leibniz, then shown to be silent on the case that
   actually matters — two paths meeting, where the answer contains a `+` that
   no symbol-shuffling produces.
3. **Every claim is measured.** No rule in this lesson is stated without a
   number beside it, and the sum-over-paths fact is settled by putting four
   candidate answers to a central difference rather than by assertion.

## The three numbers this lesson is built on

**42 versus 12.** The chain rule at `x = 2` on `(3x + 1)²`, done correctly and
done with the outer derivative evaluated at `x`. The wrong answer is asserted
*as* wrong by a test, so no future edit can make it accidentally right.

**24 + 12 = 36.** The two-path example. Four candidates — 24, 12, 288 and 36 —
are put to a measurement of `36.000000001` and only the sum survives. This is
the day's central fact and it appears in the lesson, both diagrams, the lab,
the quiz and the harness's deliberate self-test.

**−9.375.** The gradient of the loss with respect to `x1` in the two-layer
network, as `−6.0 + −3.375`. A product-only chain rule reports `−6.0` here and
looks entirely reasonable doing it.

## Two findings discovered while building the lab, both kept

**1. A stack of tanh layers does not vanish geometrically — the standard
argument is wrong by ten orders of magnitude.** Forty stacked `tanh`
operations at `x = 0.9` give a measured gradient of `8.397332e-03`. The naive
prediction — take `tanh`'s slope at the input, `0.486917`, and raise it to the
fortieth — gives `3.149274e-13`. The cause is that each `tanh` pulls its input
closer to zero where `tanh`'s slope is 1, so the local rates climb back
towards 1 as the stack deepens and the product decays like a power of the
depth rather than exponentially; the measured ratio settles near 2.8 per
doubling.

This was **not planned**. A test written to confirm the textbook story failed,
and it was rewritten to assert what is true rather than what was expected. The
suite now asserts the monotonic fall, the nine-orders-of-magnitude gap against
the prediction, and the contrast case where a genuinely constant factor of
0.487 *does* collapse below `1e-12` in the same forty steps — but never the
measured value. Do not tighten that to the captured number, and do not soften
the lesson's statement that "tanh saturates, therefore gradients vanish" is a
claim requiring measurement.

**2. `0.5⁵⁰` does not vanish when added to 1.0.** It is `8.881784e-16`, which
is *exactly four times* float64 epsilon — four representable gaps, and four
gaps still move a weight of 1. It takes three more halvings, to `0.5⁵³ =` half
an epsilon, before the addition rounds away. Both halves are asserted. The
example that genuinely vanishes at fifty layers is `0.25⁵⁰ = 7.888609e-31`,
and `0.25` was chosen because it is the **largest** slope the sigmoid ever
has, measured earlier in the same lesson rather than recalled.

## Why the network's numbers look contrived

They are contrived, deliberately and openly. The bias of hidden unit B is half
the natural logarithm of 3, because `math.tanh(0.5 * math.log(3.0))` returns
**exactly** `0.5` in float64 and `1 - tanh²` is then **exactly** `0.75`. Unit A
sits at a pre-activation of exactly 0, where `tanh` is 0 and its slope is 1.

The result is that every one of the sixteen gradients in the backward pass is
exact, the reader can check the whole thing with a pen, and the hand
computation and the from-scratch engine agree **bit for bit** — which lets the
lab compare them with `==` rather than a tolerance.

Both exactness claims are asserted by the reference suite rather than assumed,
and `dataset.py` states plainly that the choice is a convenience for the reader
and that nothing about the chain rule depends on it. Keep that declaration.

## What this directory contains

| File | Purpose |
| --- | --- |
| `index.mdx` | The full lesson body (pure markdown after the frontmatter), ~11,500 words, with all sixteen standard sections |
| `lesson.yml` | Lesson metadata: id, slug, learning promise, seventeen objectives, prerequisites, timings, tags |
| `quiz.yml` | 8 multiple-choice questions with teaching explanations, including one on why contributions sum over paths and one on why reverse mode wins with many parameters |
| `glossary.yml` | 19 precise definitions of the lesson's key terms |
| `sources.yml` | The six verified external sources this lesson draws on |
| `visuals.yml` | Registry of the lesson's two diagrams with titles, alt text and full descriptions |
| `assets/computation-graph-architecture.svg` | Static architecture diagram: the expression `f = u × v` with `u = x²` and `v = 3x` at `x = 2`, drawn as a graph with forward values on the nodes and a local derivative boxed on every edge, the two paths from `x` to `f` highlighted in different colours, their products 24 and 12 written out, and the sum 36 with an independent check |
| `assets/backward-pass-flow.svg` | Animated flow diagram (A30): the five-stage chain computing 1, 2, 5, 25, 5 and ln 5 left to right, the local derivative of each stage beneath, then the gradient carried right to left from a seed of 1.0 through 0.2, 0.02, 0.2 and 0.2 to the answer 0.4 |

## How this lesson is rendered

`index.mdx` provides the lesson body, and the sidecar YAML files travel with
it: the site layout renders the body at the day route, injects the quiz from
`quiz.yml`, the glossary from `glossary.yml`, and the source list from
`sources.yml`, and uses `lesson.yml` for navigation, metadata and time
estimates. Images are referenced from `index.mdx` with relative paths into
`assets/`, and their alt text must stay identical to `visuals.yml`. All
cross-links — to the lab and to neighbouring days — are generated by the layout
from central configuration; never hard-code repository or site URLs inside
content files.

`backward-pass-flow.svg` is animated with CSS `@keyframes` inside the file, so
it animates wherever it is rendered as an image and prints as a still. It
carries a `@media (prefers-reduced-motion: reduce)` block that disables every
animation and restores the resting state, and the still frame carries the whole
meaning on its own — all six forward values, all five local derivatives, all
six running gradients and every caption are present without motion. Both SVGs
prefix every class, id and keyframes name — `d110a-` in the architecture
diagram, `d110f-` in the flow diagram — because an inlined SVG's `<style>`
block is not scoped to that SVG and `url(#name)` resolves document-wide, so two
diagrams on one page would otherwise restyle each other.

## Related directories

- Matching hands-on lab:
  `labs/sections/math-statistics-and-data/day-110-the-chain-rule/` — "Rates
  Multiply". The learner writes fourteen functions in `starter/chainrule.py`,
  a complete reverse-mode autodiff engine and a forward-mode dual-number class
  in `starter/autodiff.py`, the hand-worked backward pass in
  `starter/network.py`, and forty-two predictions in `starter/answers.py`,
  checking themselves against a suite that skips unattempted work rather than
  failing it. The reference implementation, seven annotated demonstration
  scripts and 235 reference tests live in `examples/`, and every captured
  output in `expected-output/` came from a real run through a real lab-local
  virtual environment.
- Instructor solution:
- Day 111 takes the gradients this day produces and writes the loop that
  follows them downhill. Day 112 visualises that loop.

## Editing rules

- Every file must ship complete: no stub text, no unfinished sections, no
  filler — if a fact or figure is not verified, leave it out rather than
  approximating it.
- **Every block of output shown in this lesson was captured from a real run on
  the authoring machine on 2026-08-17**, with Python 3.14.0, numpy 2.5.2 and
  pytest 9.1.1 on macOS 26.5.2 (Apple Silicon, arm64), through a real lab-local
  `.venv` created by the lab's documented setup commands. The captures live in
  the lab's `expected-output/` directory. If you change a number here, re-run
  the lab and change it there too, and keep the indentation identical — these
  are quotes, not paraphrases.
- **The stacked-tanh measurement is reported, never asserted to a value.** The
  suite asserts the shape — monotonic decline, a gap of more than nine orders
  of magnitude against the constant-factor prediction, and the contrast case —
  and `expected-output/FIELDS.md` records exactly which figures may move. Do
  not tighten them to the captured numbers.
- **Every tolerance in the lab is derived, not tuned.** `examples/dataset.py`
  writes out the truncation and rounding arithmetic beside each one, and a
  reference test asserts that none is loose enough to be meaningless and that
  `ANALYTIC_TOL` is at least a thousand times tighter than `NUMERIC_TOL`. If a
  future change makes a test fail, do not widen the tolerance — find out which
  error term moved.
- **The hand computation and the engine are compared with `==`, on purpose.**
  That is only legitimate because the network's values are exact in float64.
  If anyone changes the network's parameters, that comparison must be revisited
  rather than quietly relaxed.
- **The Historical background section deliberately carries few dates.** It
  names Leibniz, Newton and Berkeley, places the invention in the seventeenth
  century, the rigorous limit definition in the nineteenth, Berkeley's "ghosts
  of departed quantities" in 1734, reverse accumulation in the 1960s and 1970s,
  and the popularisation of backpropagation in the mid-1980s. It deliberately
  does not attribute backpropagation to specific individuals, because the
  priority question is genuinely contested and `sources.yml` does not settle
  it. Do not add years, places or attributions that are not checkable against
  the listed sources.
- **PyTorch, JAX, TensorFlow and SymPy are not installed and no output from
  any of them is reproduced anywhere.** They are described from their
  documentation and are explicitly marked as not run here, in a standalone
  honesty note before the tool list. Keep that marking; it is the difference
  between a description and a claim.
- No prices, tier limits or free-tier allowances for any product may be written
  here. Licences are stated qualitatively (BSD 3-Clause for NumPy, MIT for
  pytest) and no others are asserted.
- All data is invented and is stated to be invented — the gear ratios, the
  three currency rates (explicitly not quoted from any market), the five chain
  stages, the two-path graph and all nine network parameters are written out in
  the lab's `dataset.py`. Keep any replacement equally checkable by hand.
- Cite only sources listed in `sources.yml`; do not add URLs elsewhere in the
  content.
- When you revise any file in this directory, update `last_verified` in
  `lesson.yml` to the revision date.
- Keep image alt text in `index.mdx` and `visuals.yml` identical, and keep the
  exact H2 heading strings intact — the lesson validator checks them. Alt text
  must contain no square brackets: a closing bracket ends markdown image syntax
  and the alt renders broken.
- If you edit either SVG, keep every class, id and keyframes name behind its
  file's prefix (`d110a-` or `d110f-`), keep the `prefers-reduced-motion`
  block, and re-check with `xmllint --noout`.
