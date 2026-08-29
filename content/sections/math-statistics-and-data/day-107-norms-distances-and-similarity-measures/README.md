# Day 107 — Norms, Distances, and Similarity Measures

The second lesson of Week 16 ("Linear Algebra II and Calculus"), and the day
the reader stops picking a distance by habit.

The organising idea, stated in the first section and returned to in every
section after it:

> **"Distance" is not one thing. It is a family, and choosing a member is a
> modelling decision with consequences you can see.**

The lesson opens by breaking something, in the pattern this course uses for its
strongest days — except that here nothing is broken at all, which is the point.
One query, three candidate articles, four term counts each, and three standard
measures name three different winners. No randomness, nothing to tune, no bug
anywhere. That disagreement is the spine of the day, and everything after it is
an answer to "so how do I choose".

The rest is the family, each part landed against real captured output: the
general p-norm and what changes as `p` moves, with the unit balls drawn as a
diamond, a circle and a square; the four norm axioms and the four metric
axioms, checked numerically, including the one squared Euclidean distance
fails; cosine distance restated as a non-metric with a concrete triple and an
exhaustive sweep; Manhattan against Euclidean against Chebyshev on cases where
each is the only correct answer; Hamming for categorical data, with the
integer-encoding trap made explicit; Jaccard against cosine ranking the same
two sets in opposite orders; Mahalanobis distance tied directly to Day 106's
eigenvectors; and the scaling demonstration that the whole day builds towards.

## Continuity with Days 99, 103 and 106

Day 99 introduced the L1 and L2 norms and Euclidean distance, and found a case
where L1 and L2 rank two candidates in opposite orders. Day 103 covered dot
products, cosine similarity, cosine distance failing the triangle inequality,
and the curse of dimensionality. Day 106 built eigenvalues, eigenvectors and
the covariance matrix.

Today **consolidates and generalises** rather than re-teaching. The cosine
non-metric result is restated with concrete numbers and an exhaustive sweep,
and the proof is explicitly left where Day 103 gave it. The Mahalanobis section
does not re-derive eigenvectors; it uses them, decomposing both probe distances
along the two eigenvectors of `[[7.5, 7.0], [7.0, 7.5]]` and dividing each
component by the square root of its eigenvalue to recover 1.114172 and exactly
6.0.

## The numbers this day rests on

Every figure below came from a real run on the authoring machine on 2026-08-17
and is asserted in `tests/run_tests.sh`.

| Result | Value |
| --- | --- |
| L1, L2 and cosine winners on the same query | Aisle, Beacon, Cartogram — three different articles |
| p-norm of (3, 4) at p = 1, 2, ∞ | 7, 5, 4; and 4.000000001 at p = 64 |
| Grid cells inside the L1, L2 and L-infinity unit balls | 469, 723, 931 — recovering areas 2.036, 3.138, 4.041 |
| Cosine distance triangle-inequality violations | 326 of 3375 binary triples |
| Jaccard and Hamming violations on their own sweeps | 0 of 4096, each |
| Warehouse displacement under L1, L2, L-infinity | 14, 10, 8 |
| Jaccard against cosine on the same two recipes | 0.3636 / 0.4000 against 0.6030 / 0.5774 — opposite winners |
| Covariance of the sensor readings, and its eigenvalues | `[[7.5, 7.0], [7.0, 7.5]]`; 0.5 and 14.5 |
| Euclidean and Mahalanobis on the two probes | 4.242641 both; 1.114172 and 6.000000 |
| Bore column's share of every raw bearing distance | at most 0.0036 per cent |
| Raw and standardised bearing rankings | `R U P S T V` and `P U R S T V` |
| Seeded sweep: winner changed after standardising | 1090 of 2000 catalogues (54.5 per cent) |

## Two findings reported rather than smoothed over

**Mahalanobis does not reproduce the standardised ranking.** It was natural to
expect it to, since both are cures for the same disease. On this catalogue,
standardised Euclidean ranks P first and Mahalanobis on the raw numbers ranks U
first and P second. Both demote the unusable part R — from first to third and
from first to fifth — but they disagree at the top, because Mahalanobis also
removes the +0.7979 correlation between bore and mass while standardising only
rescales each column. The lesson states the measured result and explains the
cause rather than trimming the claim to fit.

**Two correct inverses give two different last bits.** The Mahalanobis distance
across the grain of the sensor data is exactly `6.0` through the lab's
hand-written Gauss-Jordan inverse and `5.999999999999999` through
`numpy.linalg.inv` — a difference of `8.882e-16`. Neither is more accurate;
IEEE 754 addition is not associative. Both are asserted against a tolerance of
1e-12, and the pair is printed in the lab output as the clearest available
argument for why every float comparison in the course states a tolerance.

## What this directory contains

| File | What it is |
| --- | --- |
| `index.mdx` | The lesson. Frontmatter plus pure markdown, ~9,900 words, every `LESSON_HEADINGS` H2 in order and the four hands-on H3s. |
| `lesson.yml` | Metadata: id, day, slug, title, section, subsection, week, learning promise, 14 objectives, prerequisites, timings, `last_verified`, tags. |
| `quiz.yml` | Eight questions with `answer_index` spread across 0–3, including one on why cosine distance is not a metric and one on what standardising changes. Explanations teach rather than restate, and each says why the wrong options are wrong. |
| `glossary.yml` | Twenty terms, from norm and p-norm through to squared Euclidean distance. |
| `sources.yml` | Six sources, all verified reachable on 2026-08-17. |
| `visuals.yml` | Both diagrams, with alt text identical to the markdown and descriptions full enough to stand in for the picture. |
| `assets/norm-family-architecture.svg` | Static architecture diagram: the three unit balls on one set of axes, one point measured three ways, the p sweep, and what each norm is for. |
| `assets/scaling-changes-the-answer-flow.svg` | Animated flow diagram: the same nearest-neighbour search in raw units and after standardising, with both winners named in the still frame. |

## How this lesson is rendered

`index.mdx` is rendered by the Astro site from `src/`. The frontmatter supplies
`day` and `title`; everything below it is plain markdown, with no HTML and no
JSX.

The presentation is inherited and is not written into this day (A34): the
centred reading column, centred images, self-scrolling code blocks, the
previous/next cards, the star ask, external links opening in a new tab, and the
branded `DAY 107 / 365` hero image. The two SVGs are referenced as ordinary
markdown images, which means the browser renders them as image documents — so
the flow diagram's animation is CSS `@keyframes` rather than script or SMIL,
and it carries a `prefers-reduced-motion` block that restores a fully legible
still frame in which both winners, both rankings and every number are present.

Both diagrams namespace every class, id and `@keyframes` with `d107a-` and
`d107f-`, because the WordPress/MasterStudy exporter inlines both SVGs into one
HTML document where a `<style>` block is not scoped and `url(#name)` resolves to
the first match on the page.

The LinkedIn post is generated from `lesson.yml` and the lab metadata by
`npm run generate:social`, not written here.

## Related directories

- **Lab:** `labs/sections/math-statistics-and-data/day-107-norms-distances-and-similarity-measures/`
  — "Choose Your Distance on Purpose". Seventeen functions and twenty-five
  predictions to write, six reference scripts, 105 reference tests, and a
  98-check bash harness that re-measures every claim in the lesson and
  demonstrates its own ability to fail.
  — the answer key from real runs, the common mistakes with what each reveals,
  and a 100-point grading rubric.
- **Week 16:** the preceding day is 106 (eigenvalues and eigenvectors) and the
  next is 108 (derivatives). This day depends on Days 99, 100, 101, 103, 104
  and 106 and re-teaches none of them.

## Editing rules

- **Never change a captured number without re-running the lab.** Every figure
  in the lesson — 5, 6 and 20; 7, 5 and 4; 469, 723 and 931; 326 of 3375;
  14, 10 and 8; 4/11 and 2/5; `[[7.5, 7.0], [7.0, 7.5]]`; 0.5 and 14.5;
  1.114172 and 6.0; 0.0036 per cent; 1090 of 2000 — came from a real run on the
  authoring machine on 2026-08-17 and is asserted in `tests/run_tests.sh`. If a
  number here and a number there disagree, the lab is right and this file is
  wrong.
- **The machine-dependent claims are marked and must stay marked.** The exact
  count of 1090 depends on NumPy's random stream, which NumPy does not
  guarantee across versions; the claim the code asserts is a range of 35 to 75
  per cent. The `5.999999999999999` depends on this LAPACK build; the claim
  asserted is that both routes land within 1e-12 of 6.
  `expected-output/FIELDS.md` explains both. Do not promote either observation
  into a guarantee.
- **Alt text must match `visuals.yml` exactly**, and must never contain a `]`,
  which would end the markdown image syntax early and break the image.
- **Only the six sources in `sources.yml`.** SciPy, scikit-learn, FAISS,
  pgvector, Qdrant, Weaviate, Milvus and Chroma are described from their
  documentation, and the lesson states plainly that they are not installed here
  and that no output is reproduced for them. Do not add a quoted output for a
  tool that was not run.
- Only NumPy 2.5.2 was run. That sentence appears in the Alternatives section
  and must stay true.
- No AI references anywhere, in any file. No `github.com` or `localhost` URLs;
  all URLs come from `config/course.config.yml` via `scripts/lib/links.mjs`.
- The `## Lesson` section of the lab README is generated by
  `npm run update:links` and must not be edited by hand.
