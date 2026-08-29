# Day 132 — Visual Storytelling and Chart Honesty

The sixth lesson of Week 19 ("Data Visualization"), after Day 127's chart
choice, Day 128's matplotlib object model, Day 129's seaborn estimators,
Day 130's distributions and Day 131's time series. Day 133 assembles the
week's EDA report; this day supplies the review pass that report has to
survive.

The organising sentence, returned to throughout:

> **Most misleading charts are made by honest people.**

Nothing here is a trick a villain reaches for. Every distortion is a
default, a convenience or a reasonable-looking choice that happens to
change the conclusion — which is why the deliverable is an instrument for
checking your own work rather than a gallery of villainy.

## The opening failure

Two numbers, 100 and 102. Drawn as bars from a zero baseline they look
like what they are. Set `ylim=(99, 103)` and the second bar is
**exactly three times the height of the first** — measured off the
rendered geometry, a drawn height ratio of `3.0000` against a data ratio
of `1.0200`, for a lie factor of `2.9412`. No data changed. One line of
code.

## What the lesson covers, each with a measured number

- **Tufte's lie factor**, defined precisely and computed from rendered
  geometry rather than from the plotted values — `1.0000` for the honest
  chart, `2.9412` for the truncated one.
- **Truncation, with the nuance most versions omit.** The same two
  numbers on the same truncated axis, drawn as a line, have a lie factor
  of exactly `1.0000` on every baseline tried. A bar encodes value as
  length from the baseline; a line encodes change as displacement. Hence
  the two-clause rule rather than the slogan.
- **Dual y-axes, and the correction to the standard warning.** Scaling
  cannot change the drawn traces' correlation at all — measured invariant
  to `3.12e-15` across 500 random pairs of axis limits. What it does
  control is the sign (inverting one axis takes `+0.913234` to
  `-0.913234`, exactly) and the visual impression (the tracking gap moves
  from `0.4938` to `0.0147` on unchanged data). And the control that
  settles it: the same widening drives a genuinely correlated pair to a
  gap of `0.0046` and an uncorrelated pair to `0.0147`, so overlapping
  curves carry no information about correlation.
- **Cherry-picked windows**: one series whose fitted slope runs
  `-0.7305` per week over its first half, `+0.7045` over its second, and
  `-0.0131` over the whole.
- **Binning as an editorial choice**: Sturges' rule draws one hump and
  the Freedman-Diaconis rule draws two from the same 400 values. The
  dataset was deliberately selected for that disagreement, and the lesson
  and the lab both say so.
- **Radius and 3D**: a radius-encoded pair whose shown area ratio is
  `16.00` for a data ratio of 4 — so the lie factor is the data ratio
  itself, `4.00` — and two 3D bars drawn at `2.341` and `4.204` for a
  data ratio a flat chart reproduces as exactly `2.000`.
- **The legitimate craft**: ordering, retrievable claim text, emphasis
  through contrast, and removal — with the argument that an unlabelled
  chart is unhelpful rather than neutral.
- **Accessibility as honesty**: the classic red/green pair separates by
  only `0.0996` in relative luminance, against `0.1970` for seaborn's
  `colorblind` palette and `0.5505` for deliberate emphasis.
- **The caption contract**: four checks that pass an honest chart, fail a
  truncated one, and pass a line on a non-zero baseline whose caption
  discloses it.

## What this directory contains

| File | Purpose |
| --- | --- |
| `index.mdx` | The full lesson body (pure markdown after the frontmatter), all sixteen standard sections plus a closing AI thread |
| `lesson.yml` | Lesson metadata: id, slug, learning promise, ten objectives, prerequisites, timings, tags |
| `quiz.yml` | 8 multiple-choice questions with teaching explanations, answer index spread across 0-3 |
| `glossary.yml` | 15 precise definitions of the lesson's key terms |
| `sources.yml` | The five verified sources this lesson draws on |
| `visuals.yml` | Registry of the lesson's two diagrams with titles, alt text and full descriptions |
| `assets/distortion-anatomy-architecture.svg` | Static architecture diagram: one dataset drawn honestly at the centre, five distortions arrayed around it with their measured lie factors |
| `assets/baseline-flow.svg` | Animated flow diagram: the baseline sliding up from zero while the data ratio caption stays fixed and the lie factor climbs |

## How this lesson is rendered

`index.mdx` provides the lesson body, and the sidecar YAML files travel
with it: the site layout renders the body at the day route, injects the
quiz from `quiz.yml`, the glossary from `glossary.yml`, and the source
list from `sources.yml`, and uses `lesson.yml` for navigation, metadata
and time estimates. Images are referenced from `index.mdx` with relative
paths into `assets/`, and their alt text stays identical to `visuals.yml`.
All cross-links — to the lab and to neighbouring days — are generated by
the layout from central configuration; never hard-code repository or site
URLs inside content files.

`baseline-flow.svg` is animated with CSS `@keyframes` inside the file, so
it animates wherever it is rendered as an image and prints as a still. It
carries a `@media (prefers-reduced-motion: reduce)` block that disables
every animation and restores the resting state, and the still frame
carries the whole meaning on its own — all four stages, all twelve
numbers and the lie-factor scale are present without motion. Both SVGs
prefix every class, id and keyframes name — `d132a-` in the architecture
diagram, `d132f-` in the flow diagram — because an inlined SVG's
`<style>` block is not scoped to that SVG and `url(#name)` resolves
document-wide, so two diagrams on one page would otherwise restyle each
other.

No LaTeX appears anywhere in `index.mdx`. Every formula and every
matplotlib call in prose is written in inline backticks or a fenced code
block, because MDX parses `{` and `}` as JSX and a `$$…$$` block broke
the site build on an earlier day.

## Related directories

- Matching hands-on lab:
  `labs/sections/math-statistics-and-data/day-132-visual-storytelling-and-chart-honesty/`
  — "Charts That Cannot Lie To You." The learner writes fourteen
  functions across nine exercises in `starter/honesty.py`, checking
  themselves against a suite that skips unattempted work rather than
  failing it. The reference implementation, nine annotated demonstration
  scripts and a 42-test reference suite live in `examples/`, and every
  captured output in `expected-output/` came from a real run through a
  real lab-local virtual environment.
- Instructor solution:
- Day 127 supplied the perceptual ranking this lesson quantifies, and
  named both radius encoding and the red/green collapse. Day 128 supplied
  the technique every measurement here uses — read the artists, never the
  pixels. Day 130 established bin width as a choice; this day supplies
  the consequences. Day 131 established what a window does to a trend.
  Day 116's Simpson's paradox is referenced, not re-derived. Day 133
  assembles the EDA report that this day's review contract is meant to be
  run over.

## Editing rules

- Every file must ship complete: no stub text, no unfinished sections, no
  filler — if a fact or figure is not verified, leave it out rather than
  approximating it.
- **Every block of output shown in this lesson was captured from a real
  run on the authoring machine on 2026-08-20**, with Python 3.14.0,
  matplotlib 3.11.1, seaborn 0.13.2, pandas 3.0.5, NumPy 2.5.2 and
  pytest 9.1.1 on macOS 26.5.2 (Apple Silicon, arm64), through a real
  lab-local `.venv` created by the lab's documented setup commands. If
  you change a number here, re-run the lab and change it there too.
- **The dual-axis section states the opposite of the folk warning, and
  that is deliberate.** Scaling cannot change the drawn correlation;
  correlation is invariant under affine transforms and a linear axis
  rescaling is one. Do not "fix" that section back to the usual claim. If
  you revise it, keep the three measured parts together: the invariance
  (`3.12e-15` over 500 scalings), the exact sign flip under inversion,
  and — the load-bearing one — the control showing the same widening
  produces overlapping curves for both an uncorrelated and a strongly
  correlated pair.
- **Keep the radius/area statement the right way round.** The shown AREA
  RATIO is the square of the data ratio (`16.00` for a data ratio of 4);
  the LIE FACTOR equals the data ratio itself (`4.00`). It is easy to
  invert this into "the lie factor is the square", which the measurement
  does not support.
- **Two of the lab's datasets were deliberately selected**, and both
  disclosures must stay: the dual-axis seed was chosen by scanning seeds
  1-599 for the smallest absolute correlation, and the bimodal sample's
  parameters were chosen by scanning a grid for a case where Sturges' and
  Freedman-Diaconis genuinely disagree — which most parameter settings do
  not. Exercise 5's claim is that the disagreement is possible with two
  citable rules, not that it is typical. Removing those disclosures would
  commit the exact failure the lesson is about.
- **The 3D numbers are camera-dependent** (`focal_length=0.2`, default
  view angle) and the lesson says so. Keep that caveat attached to the
  figures; the portable claim is the shape of the finding, not the value.
- **The luminance claim has a stated limit.** Luminance is one component
  of colour distinguishability, not the whole of it; no colour-deficiency
  simulation is implemented anywhere in this day. Do not strengthen that
  wording.
- **No BI tool was run.** Tableau and Power BI are described from their
  published documentation only. Two specifics must not drift: Tableau's
  help documents an "Include zero" check box and describes *clearing* it
  as the action that narrows the axis, so this lesson does **not** claim
  Tableau defaults to a truncated axis; and Power BI's axis documentation
  does confirm that adding a line value to a combo chart creates a
  secondary Y-axis automatically, along with an "Invert range" slider and
  a "Round range" toggle. State only what the documentation states.
- No prices, tier limits or free-tier allowances for any product may be
  written here. The Alternatives section names the free entry tiers by
  name and explicitly declines to state pricing.
- All data plotted in the lab is invented and is stated to be invented.
  Keep any replacement equally checkable by reading the chart back.
- Cite only sources listed in `sources.yml`; do not add URLs elsewhere in
  the content.
- When you revise any file in this directory, update `last_verified` in
  `lesson.yml` to the revision date.
- Keep image alt text in `index.mdx` and `visuals.yml` identical, and keep
  the exact H2 heading strings intact — the lesson validator checks them.
  Alt text must contain no square brackets: a closing bracket ends
  markdown image syntax and the alt renders broken.
- If you edit either SVG, keep every class, id and keyframes name behind
  its file's prefix (`d132a-` or `d132f-`), keep the
  `prefers-reduced-motion` block, and re-check with `xmllint --noout`.
