#!/usr/bin/env node
/**
 * Fail the gate if any vendor bootstrap file has drifted from its source.
 *
 * A stale CLAUDE.md / GEMINI.md / AGENTS.md is actively harmful: it is the
 * first thing a new assistant reads, so wrong content there propagates into
 * everything that follows.
 */

import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const { TARGETS, render, coreText } = await import('../generate-bootstrap.mjs');

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
const core = coreText();
const problems = [];

for (const target of TARGETS) {
  let actual;
  try {
    actual = readFileSync(join(ROOT, target.file), 'utf8');
  } catch {
    problems.push(`${target.file} is missing — run npm run generate:bootstrap`);
    continue;
  }
  if (actual !== render(target, core)) {
    problems.push(
      `${target.file} has drifted from context/bootstrap-core.md — run npm run generate:bootstrap`,
    );
  }
}

if (problems.length) {
  console.error(`✗ validate:bootstrap: ${problems.length} problem(s)`);
  for (const p of problems) console.error(`  - ${p}`);
  process.exit(1);
}

console.log(
  `✓ validate:bootstrap: ${TARGETS.length} vendor bootstrap file(s) match context/bootstrap-core.md.`,
);
