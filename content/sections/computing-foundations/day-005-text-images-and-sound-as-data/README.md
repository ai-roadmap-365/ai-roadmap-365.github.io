# Day 005 — Text, Images, and Sound as Data

## What this directory contains

| File | Purpose |
| ---- | ------- |
| `index.mdx` | The full lesson body (pure markdown after the frontmatter), all sixteen standard sections |
| `lesson.yml` | Lesson metadata: id, slug, learning promise, objectives, prerequisites, timings, tags |
| `quiz.yml` | 8 multiple-choice questions with answers and explanations |
| `glossary.yml` | 15 plain-language definitions of the lesson's key terms |
| `sources.yml` | The verified external sources this lesson draws on |
| `visuals.yml` | Registry of the lesson's diagrams with titles, alt text, and descriptions |
| `assets/text-encoding-layers.svg` | Diagram: character → code point → UTF-8 bytes → bits |
| `assets/pixel-grid.svg` | Diagram: a 2×2 image as a grid of RGB numbers |

## How this lesson is rendered

The site renders `index.mdx` at the day's route, injecting the quiz,
glossary, and sources from their sidecar YAML files and the lab how-to from
central configuration. The same sources produce the WordPress/MasterStudy
exports, so every surface matches.

## Related directories

- Matching lab: `labs/sections/computing-foundations/day-005-text-images-and-sound-as-data/`

## Editing rules

No placeholder text; update `last_verified` when revising; keep the
`visuals.yml` alt text character-identical to the image alts in
`index.mdx`; regenerate exports and the video prompt after edits.
