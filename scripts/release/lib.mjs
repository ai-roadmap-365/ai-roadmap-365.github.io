/** Shared logic for the daily release pipeline (requirements §10). */
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { allDays, argValue, repoRoot } from '../lib/course.mjs';

export function requireDay() {
  const dayArg = Number(argValue(['--day', '-d']));
  if (!Number.isInteger(dayArg) || dayArg < 1 || dayArg > 365) {
    console.error('Usage: <command> -- --day <1-365>');
    process.exit(1);
  }
  const day = allDays().find((d) => d.number === dayArg);
  if (!day) {
    console.error(`Day ${dayArg} not found in the curriculum.`);
    process.exit(1);
  }
  return day;
}

export function releaseDir(day) {
  return path.join(repoRoot, 'dist', 'public-release', day.dayId);
}

export function run(label, cmd, args) {
  process.stdout.write(`▶ ${label}\n`);
  const res = spawnSync(cmd, args, { cwd: repoRoot, stdio: 'inherit' });
  return res.status === 0;
}

/** Validation gate shared by release:validate and release:export. */
export function validateDayForRelease(day) {
  const steps = [
    ['validate:curriculum', ['node', 'scripts/validate/curriculum.mjs']],
    ['validate:lessons', ['node', 'scripts/validate/lessons.mjs']],
    ['validate:labs', ['node', 'scripts/validate/labs.mjs']],
    ['validate:sources', ['node', 'scripts/validate/sources.mjs']],
    ['validate:visuals', ['node', 'scripts/validate/visuals.mjs']],
    ['validate:links', ['node', 'scripts/validate/links.mjs']],
    ['validate:private-links', ['node', 'scripts/validate/private-links.mjs']],
    ['validate:secrets', ['node', 'scripts/validate/secrets.mjs']],
    ['audit:licenses', ['node', 'scripts/validate/licenses.mjs']],
  ];
  let ok = true;
  for (const [label, [cmd, ...args]] of steps) ok = run(label, cmd, args) && ok;
  if (!day.hasContent) {
    console.error(`✗ day ${day.number} has no authored lesson content`);
    ok = false;
  }
  if (!day.hasLab) {
    console.error(`✗ day ${day.number} has no lab`);
    ok = false;
  }
  return ok;
}
