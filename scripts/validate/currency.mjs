#!/usr/bin/env node
/**
 * Currency audit: last_verified dates on authored lessons and catalog
 * entries must be recent (≤180 days). AI moves fast; stale "current
 * product" claims are treated as failures for complete lessons and
 * warnings otherwise.
 */
import { readFileSync } from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';
import { allDays, loadSidecars, repoRoot, makeReporter } from '../lib/course.mjs';

const r = makeReporter('audit:currency');
const MAX_AGE_DAYS = 180;
const now = Date.now();

function ageDays(date) {
  return (now - Date.parse(date)) / 86400000;
}

for (const d of allDays().filter((x) => x.hasContent)) {
  const verified = loadSidecars(d).lesson.last_verified;
  if (!verified) {
    r.fail(`day ${d.number}: no last_verified date`);
    continue;
  }
  const age = ageDays(String(verified));
  if (Number.isNaN(age)) r.fail(`day ${d.number}: last_verified unparseable (${verified})`);
  else if (age > MAX_AGE_DAYS) {
    if (d.status === 'complete')
      r.fail(`day ${d.number}: complete lesson stale (verified ${Math.round(age)} days ago)`);
    else console.log(`  warning: day ${d.number} verified ${Math.round(age)} days ago`);
  }
}

for (const name of ['tools', 'frameworks', 'models', 'free-open-source']) {
  const doc = yaml.load(readFileSync(path.join(repoRoot, 'catalog', `${name}.yml`), 'utf8'));
  for (const e of doc.entries ?? []) {
    const age = ageDays(String(e.last_verified));
    if (Number.isNaN(age) || age > MAX_AGE_DAYS)
      r.fail(`catalog/${name}.yml: "${e.name}" stale or undated`);
  }
}

r.finish(`all complete lessons and catalogs verified within ${MAX_AGE_DAYS} days.`);
