#!/usr/bin/env node
/**
 * Regenerates every generated-link block in the repository from
 * config/course.config.yml (requirements §5.5, §9: README links are
 * generated, never hand-maintained). Idempotent; run after any URL change
 * (or use `npm run configure`, which runs this for you).
 *
 * A generated block is delimited by:
 *   <!-- generated-links:start ... -->  ...  <!-- generated-links:end -->
 */
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { allDays, loadConfig } from './lib/course.mjs';
import { getLessonUrl } from './lib/links.mjs';

const START =
  '<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->';
const END = '<!-- generated-links:end -->';

/**
 * Repository-neutral by design (amendment A10 to §5.5): the block contains
 * NO absolute repository URLs and never distinguishes private from public —
 * relative references work identically wherever the README lives, and
 * nothing reveals that any other repository exists.
 */
export function generatedLinkBlock(config, day) {
  const lines = [
    START,
    `- **Lesson title:** ${day.title}`,
    `- **Day number:** ${day.number} of 365`,
    config.website.public_base_url
      ? `- **Lesson article:** ${getLessonUrl(config, day, 'public')}`
      : `- **Lesson article:** published on the course blog (one lesson per day); the article for this day links back to this lab.`,
    `- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.`,
    `- **Browse the course locally:** from the repository root, this lab also appears in the course website at \`/labs/${day.dayId}\` when the site is running.`,
    END,
  ];
  return lines.join('\n');
}

export function updateLinks({ quiet = false } = {}) {
  const config = loadConfig();
  let updated = 0;
  let missing = 0;
  for (const day of allDays().filter((d) => d.hasLab)) {
    const readmePath = path.join(day.labDir, 'README.md');
    if (!existsSync(readmePath)) continue;
    const text = readFileSync(readmePath, 'utf8');
    const startIdx = text.indexOf(START);
    const endIdx = text.indexOf(END);
    if (startIdx === -1 || endIdx === -1) {
      missing += 1;
      if (!quiet)
        console.warn(`  warning: day ${day.number} lab README has no generated-links block`);
      continue;
    }
    const next =
      text.slice(0, startIdx) + generatedLinkBlock(config, day) + text.slice(endIdx + END.length);
    if (next !== text) {
      writeFileSync(readmePath, next);
      updated += 1;
    }
  }
  if (!quiet)
    console.log(`✓ update:links: ${updated} README(s) rewritten, ${missing} without a block.`);
  return { updated, missing };
}

import { pathToFileURL } from 'node:url';

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  updateLinks();
}
