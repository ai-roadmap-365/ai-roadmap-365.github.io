#!/usr/bin/env node
/**
 * Aggregated verification (requirements §14): runs every quality gate in
 * order and fails if any fails. Pass --full to also require 365/365
 * completed days (the final-delivery gate).
 */
import { spawnSync } from 'node:child_process';

const full = process.argv.includes('--full');

const STEPS = [
  ['install:verify', ['node', 'scripts/validate/install-verify.mjs']],
  ['lint', ['npx', 'eslint', '.']],
  ['format:check', ['npx', 'prettier', '--check', '.']],
  ['typecheck', ['npx', 'astro', 'check']],
  ['validate:curriculum', ['node', 'scripts/validate/curriculum.mjs']],
  ['validate:readmes', ['node', 'scripts/validate/readmes.mjs']],
  ['validate:bootstrap', ['node', 'scripts/validate/bootstrap.mjs']],
  ['validate:lessons', ['node', 'scripts/validate/lessons.mjs']],
  ['validate:labs', ['node', 'scripts/validate/labs.mjs']],
  ['validate:projects', ['node', 'scripts/validate/projects.mjs']],
  ['validate:sources', ['node', 'scripts/validate/sources.mjs']],
  ['validate:visuals', ['node', 'scripts/validate/visuals.mjs']],
  ['validate:animation', ['node', 'scripts/validate/animation.mjs']],
  ['validate:quiz-balance', ['node', 'scripts/validate/quiz-balance.mjs']],
  ['validate:links', ['node', 'scripts/validate/links.mjs']],
  ['validate:privacy', ['node', 'scripts/validate/privacy.mjs']],
  ['validate:secrets', ['node', 'scripts/validate/secrets.mjs']],
  ['audit:licenses', ['node', 'scripts/validate/licenses.mjs']],
  ['audit:currency', ['node', 'scripts/validate/currency.mjs']],
  ['test', ['npx', 'vitest', 'run']],
  ['test:links', ['node', 'scripts/validate/test-links.mjs', '--mode', 'all']],
  ['build', ['npx', 'astro', 'build']],
  // astro build clears dist/, so exports are regenerated after it.
  ['test:e2e', ['node', 'scripts/validate/e2e.mjs']],
  ['test:accessibility', ['node', 'scripts/validate/accessibility.mjs']],
  ['build:offline', ['node', 'scripts/build-offline.mjs']],
  ['preview:smoke-test', ['node', 'scripts/validate/smoke-test.mjs']],
  [
    full ? 'audit:coverage --require-full' : 'audit:coverage',
    ['node', 'scripts/validate/coverage.mjs', ...(full ? ['--require-full'] : [])],
  ],
];

const results = [];
for (const [name, [cmd, ...args]] of STEPS) {
  process.stdout.write(`\n▶ ${name}\n`);
  const started = Date.now();
  const res = spawnSync(cmd, args, { stdio: 'inherit' });
  results.push({ name, ok: res.status === 0, seconds: ((Date.now() - started) / 1000).toFixed(1) });
}

console.log('\n================ verify:all summary ================');
let failed = 0;
for (const { name, ok, seconds } of results) {
  if (!ok) failed += 1;
  console.log(`${ok ? '✓' : '✗'} ${name.padEnd(36)} ${seconds}s`);
}
console.log('====================================================');
if (failed > 0) {
  console.error(`${failed} step(s) failed.`);
  process.exit(1);
}
console.log(`All ${results.length} steps passed${full ? ' (FULL completion gate)' : ''}.`);
