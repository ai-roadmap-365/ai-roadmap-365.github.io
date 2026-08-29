#!/usr/bin/env node
/**
 * Generate the per-vendor bootstrap files from ONE source.
 *
 * CLAUDE.md, GEMINI.md and AGENTS.md all say the same thing: read
 * `context/` first, and here are the non-negotiables. Maintaining three
 * copies by hand guarantees they drift, and a drifted bootstrap file is
 * worse than none — it tells a new assistant something that is no longer
 * true.
 *
 * The shared body lives in `context/bootstrap-core.md`. This script wraps
 * it in the right heading per vendor. `scripts/validate/bootstrap.mjs`
 * regenerates in memory and fails `verify:all` if any file has drifted.
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

function repoRoot(start = process.cwd()) {
  let dir = start;
  for (;;) {
    try {
      readFileSync(join(dir, 'package.json'));
      return dir;
    } catch {
      const parent = join(dir, '..');
      if (parent === dir) throw new Error('repo root not found');
      dir = parent;
    }
  }
}

const ROOT = repoRoot();

export const TARGETS = [
  {
    file: 'CLAUDE.md',
    heading: '# AI session bootstrap',
    intro: 'Read the `context/` directory first. This file is a pointer, not the contract.',
  },
  {
    file: 'GEMINI.md',
    heading: '# AI session bootstrap (Gemini / Antigravity)',
    intro:
      'This file exists so that Gemini-based tools bootstrap the same way every other assistant does. **It is a pointer, not the contract.**',
  },
  {
    file: 'AGENTS.md',
    heading: '# AI session bootstrap (Codex / AGENTS.md-aware tools)',
    intro:
      'This file exists so that Codex and other AGENTS.md-aware tools bootstrap the same way every other assistant does. **It is a pointer, not the contract.**',
  },
];

export function render(target, core) {
  return [
    target.heading,
    '',
    '<!-- GENERATED FILE — do not edit by hand.',
    '     Source: context/bootstrap-core.md',
    '     Regenerate: npm run generate:bootstrap',
    '     Drift fails verify:all via scripts/validate/bootstrap.mjs -->',
    '',
    target.intro,
    '',
    core.trimEnd(),
    '',
  ].join('\n');
}

export function coreText() {
  return readFileSync(join(ROOT, 'context', 'bootstrap-core.md'), 'utf8');
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const core = coreText();
  for (const target of TARGETS) {
    writeFileSync(join(ROOT, target.file), render(target, core));
  }
  console.log(
    `✓ generate:bootstrap: wrote ${TARGETS.map((t) => t.file).join(', ')} from context/bootstrap-core.md`,
  );
}
