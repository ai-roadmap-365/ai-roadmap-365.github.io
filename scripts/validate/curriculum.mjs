#!/usr/bin/env node
/** Validates curriculum.yml integrity and its sync with the source + site config. */
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { loadCurriculum, loadConfig, allDays, repoRoot, makeReporter } from '../lib/course.mjs';
import { sections as source, slugify } from '../../curriculum/curriculum.source.mjs';

const r = makeReporter('validate:curriculum');
const curriculum = loadCurriculum();
const config = loadConfig();
const days = allDays();

if (days.length !== 365) r.fail(`expected 365 days, curriculum has ${days.length}`);
const weekNumbers = new Set(days.map((d) => d.week));
if (weekNumbers.size !== 52) r.fail(`expected 52 weeks, found ${weekNumbers.size}`);
if (curriculum.course.days !== 365) r.fail('course.days is not 365');

// Sequential day numbering and unique slugs.
const slugs = new Set();
days.forEach((d, i) => {
  if (d.number !== i + 1) r.fail(`day numbering breaks at position ${i} (day ${d.number})`);
  if (slugs.has(d.slug)) r.fail(`duplicate day slug: ${d.slug}`);
  slugs.add(d.slug);
});

// Every week carries a project with title and summary.
for (const s of curriculum.sections)
  for (const b of s.subsections)
    for (const w of b.weeks) {
      if (!w.project?.title || !w.project?.summary)
        r.fail(`week ${w.number} has no project title/summary`);
      if (w.days.length !== 7 && !(w.number === 52 && w.days.length === 8))
        r.fail(`week ${w.number} has ${w.days.length} days (expected 7, or 8 for week 52)`);
    }

// The generated manifest matches the authored source (regenerate check).
let sourceDayCount = 0;
const sourceTitles = [];
for (const s of source)
  for (const b of s.subsections)
    for (const w of b.weeks)
      for (const t of w.days) {
        sourceDayCount += 1;
        sourceTitles.push({ title: t, slug: slugify(t) });
      }
if (sourceDayCount !== days.length) {
  r.fail(
    `curriculum.yml (${days.length} days) is out of date with curriculum.source.mjs (${sourceDayCount}) — run npm run generate:curriculum`,
  );
} else {
  days.forEach((d, i) => {
    if (d.title !== sourceTitles[i].title || d.slug !== sourceTitles[i].slug)
      r.fail(`day ${d.number} differs from source — run npm run generate:curriculum`);
  });
}

// Site config invariants duplicated in astro.config.mjs stay in sync.
const astroConfig = readFileSync(path.join(repoRoot, 'astro.config.mjs'), 'utf8');
if (!astroConfig.includes(`base: '${config.website.base_path}'`))
  r.fail(
    `astro.config.mjs base does not match course.config.yml base_path (${config.website.base_path})`,
  );
if (!astroConfig.includes(`port: ${config.website.port}`))
  r.fail(`astro.config.mjs port does not match course.config.yml port (${config.website.port})`);
if (!config.website.local_base_url.endsWith(config.website.base_path))
  r.fail('local_base_url does not end with base_path');

r.finish(
  `365 days, 52 weeks, ${curriculum.sections.length} sections; manifest in sync with source and site config.`,
);
