/**
 * The completion contracts (requirements §2, §5, §13): forbidden placeholder
 * markers and the required heading sets validators enforce. Content
 * generators and validators both read from here so they can never drift.
 */

/** Strings that mark fake completion. Checked case-insensitively. */
export const FORBIDDEN_STRINGS = [
  'content coming soon',
  'add explanation here',
  'todo',
  'example to be added',
  'diagram pending',
  'lab pending',
  'source required',
  'insert code here',
  'tbd',
  'fixme',
  'lorem ipsum',
  'coming soon',
];

/**
 * Words like "todo" may legitimately appear inside other words ("todos") or
 * in phrases like "a to-do CLI". The scanner matches whole words only.
 */
export function findForbidden(text) {
  const lower = text.toLowerCase();
  const hits = [];
  for (const marker of FORBIDDEN_STRINGS) {
    const re = new RegExp(
      `(^|[^a-z0-9-])${marker.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}($|[^a-z0-9-])`,
      'i',
    );
    if (re.test(lower)) hits.push(marker);
  }
  return hits;
}

/**
 * Raw C0 control characters, which no lesson legitimately contains. They get
 * in when authored text passes through a shell heredoc that interprets
 * backslash escapes: `\alpha` becomes BEL + "lpha", `\beta` becomes BS +
 * "eta", `\frac` becomes FF + "rac", `\text` becomes TAB + "ext". The
 * damage is invisible in a terminal and renders as a mangled formula on the
 * site, so it survived until a reader would have hit it.
 *
 * TAB is excluded here because tool-output tables use it legitimately; the
 * `\t` case is caught by the LaTeX-command check below instead.
 */
// Matching control characters is the entire purpose of this check.
// eslint-disable-next-line no-control-regex
const CONTROL_CHARS = /[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g;

/** A tab immediately followed by the tail of a LaTeX command is a mangled `\t`. */
const MANGLED_TAB = /\t(?=ext[A-Za-z{( ]|imes\b|heta\b|au\b|op\b)/g;

/**
 * Returns a list of human-readable findings, empty when the text is clean.
 * Reported per occurrence with the surrounding text so the fix is obvious.
 */
export function findControlChars(text) {
  const hits = [];
  for (const [re, label] of [
    [CONTROL_CHARS, 'control character'],
    [MANGLED_TAB, 'tab from a mangled LaTeX command'],
  ]) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(text)) !== null) {
      const line = text.slice(0, m.index).split('\n').length;
      const near = text.slice(Math.max(0, m.index - 20), m.index + 20).replace(/\s+/g, ' ');
      const code = `U+${text.charCodeAt(m.index).toString(16).toUpperCase().padStart(4, '0')}`;
      hits.push(`line ${line}: ${label} ${code} near "${near.trim()}"`);
      if (hits.length >= 10) return hits;
    }
  }
  return hits;
}

/**
 * An odd number of line-anchored code fences means a block was never closed on
 * its own line -- usually a closing ``` appended to the end of a content line.
 * Markdown may still render it, but every tool that pairs fences by line then
 * mispairs the rest of the file, and program output starts counting as prose.
 */
export function findUnbalancedFences(text) {
  const fences = text.match(/^```/gm) ?? [];
  return fences.length % 2 === 0
    ? []
    : [
        `${fences.length} line-anchored code fences -- one block is unclosed, or a closing fence shares a line with content`,
      ];
}

/** Exact H2 headings every lesson index.mdx must contain, in order. */
export const LESSON_HEADINGS = [
  '## Why this matters',
  '## The idea in plain language',
  '## Historical background',
  '## What it is — and what it is not',
  '## Why it was created and what problems it solves',
  '## How it works',
  '## An everyday analogy',
  '## Examples in practice',
  '## Implications: security, privacy, performance, scalability, and cost',
  '## Alternatives: free, open source, and commercial',
  '## Comparison with related concepts',
  '## When to use it — and when not to',
  '## Knowledge check',
  '## Hands-on exercise',
  '## Practice assignment',
  '## Extension challenge',
];

/** H3 headings required inside the hands-on exercise section. */
export const LESSON_HANDS_ON_HEADINGS = [
  '### Expected output',
  '### Validate your work',
  '### Troubleshooting',
  '### Common mistakes',
];

/** Required fields in lesson.yml. */
export const LESSON_FIELDS = [
  'id',
  'day',
  'slug',
  'title',
  'section',
  'subsection',
  'week',
  'learning_promise',
  'objectives',
  'prerequisites',
  'reading_time_minutes',
  'practical_time_minutes',
  'last_verified',
  'tags',
];

/** Required headings in every daily lab README. */
export const LAB_README_HEADINGS = [
  '## Lesson',
  '## Purpose',
  '## Learning objectives',
  '## Prerequisites',
  '## Supported operating systems',
  '## Hardware requirements',
  '## Required software',
  '## Free and open-source options',
  '## Installation',
  '## File structure',
  '## How to run',
  '## What the commands do',
  '## Expected output',
  '## Validation steps',
  '## Tests',
  '## Cleanup',
  '## Troubleshooting',
  '## Security notes',
  '## Extension exercises',
  '## Navigation',
];

/** Required entries in every daily lab directory. */
export const LAB_REQUIRED_PATHS = [
  'README.md',
  'metadata.yml',
  'starter',
  'examples',
  'tests',
  'expected-output',
  'requirements',
  'troubleshooting.md',
  'security.md',
];

export const LAB_METADATA_FIELDS = [
  'lesson_id',
  'day',
  'kind',
  'languages',
  'setup_commands',
  'run_commands',
  'test_commands',
  'cleanup_commands',
  'requires_network',
  'requires_api_key',
  'estimated_minutes',
];

/** Required headings in the root README. */
export const ROOT_README_HEADINGS = [
  '## Vision and audience',
  '## The nine courses (365-day structure)',
  '## Released labs',
  '## Repository hierarchy',
  '## Getting started',
  '## Development server',
  '## Production build and preview',
  '## Offline build',
  '## Tests and validation',
  '## Content structure',
  '## Lab structure',
  '## Instructor content',
  '## Repository and link strategy',
  '## Publishing one daily lesson',
  '## Security controls',
  '## Contribution process',
  '## Troubleshooting',
  '## Current implementation status',
  '## Resuming content development',
];

export const SECTION_README_HEADINGS = [
  '## Purpose',
  '## Skills covered',
  '## Why this section is included',
  '## Prerequisites',
  '## Subsections and weeks',
  '## Projects',
  '## Expected completion time',
  '## Learning outcomes',
  '## Where this fits in the course',
  '## Navigation',
];

export const SUBSECTION_README_HEADINGS = [
  '## Purpose',
  '## Topics',
  '## Prerequisites',
  '## Weeks',
  '## Learning progression',
  '## Hands-on work',
  '## Assessment',
  '## Navigation',
];

export const WEEK_README_HEADINGS = [
  '## Theme and objectives',
  '## Prerequisites',
  '## Daily lessons',
  '## Daily expectations',
  '## Required tools and free alternatives',
  '## Weekly project',
  '## Weekly quiz',
  '## Deliverables',
  '## Troubleshooting',
  '## Navigation',
];

/** Required headings in every daily lesson-content README. */
export const LESSON_README_HEADINGS = [
  '## What this directory contains',
  '## How this lesson is rendered',
  '## Related directories',
  '## Editing rules',
];

/** The 13 completion flags — a lesson is complete only when all are true. */
export const COMPLETION_FLAGS = [
  'lesson_content',
  'lesson_rendered',
  'lab_created',
  'lab_executed',
  'tests_passed',
  'visuals_complete',
  'sources_verified',
  'readme_complete',
  'local_links_passed',
  'lab_links_generated',
  'blog_published',
  'privacy_scan_passed',
  'editorial_review_passed',
];
