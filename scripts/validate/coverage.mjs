#!/usr/bin/env node
/**
 * Coverage audit: honest progress report of authored/complete days, labs,
 * projects and published days against the 365-day target. Exits 0 as a report;
 * with --require-full it becomes the full-completion gate and fails unless
 * every day is validated complete (requirements §13, §19).
 */
import { allDays, makeReporter } from '../lib/course.mjs';
import { COMPLETION_FLAGS } from '../lib/contracts.mjs';

const requireFull = process.argv.includes('--require-full');
const r = makeReporter('audit:coverage');
const days = allDays();

const authored = days.filter((d) => d.hasContent);
const withLabs = days.filter((d) => d.hasLab);
const complete = days.filter((d) => d.status === 'complete');

// A day may be marked complete only when all 13 flags are true.
for (const d of complete) {
  const missing = COMPLETION_FLAGS.filter((f) => d.completion[f] !== true);
  if (missing.length > 0)
    r.fail(`day ${d.number} is marked complete but flags are not all true: ${missing.join(', ')}`);
}
// And no day with all flags true may be left unmarked (tracker honesty both ways).
for (const d of days) {
  if (d.status !== 'complete' && COMPLETION_FLAGS.every((f) => d.completion[f] === true))
    r.fail(`day ${d.number} has all completion flags true but status is "${d.status}"`);
}

console.log('Coverage report:');
console.log(`  days authored:            ${authored.length} / 365`);
console.log(`  days with labs:           ${withLabs.length} / 365`);
console.log(`  days validated complete:  ${complete.length} / 365`);
const nextIncomplete = days.find((d) => d.status !== 'complete');
if (nextIncomplete)
  console.log(`  next incomplete day:      ${nextIncomplete.number} — ${nextIncomplete.title}`);

if (requireFull && complete.length < 365)
  r.fail(`full completion requires 365/365 complete days; currently ${complete.length}`);

r.finish(
  requireFull
    ? 'full-completion gate passed: 365/365 days complete.'
    : `progress tracker is consistent (${complete.length}/365 complete — report mode, use --require-full for the completion gate).`,
);
