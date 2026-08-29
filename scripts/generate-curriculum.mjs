#!/usr/bin/env node
/**
 * Compiles curriculum/curriculum.source.mjs into curriculum/curriculum.yml.
 * Deterministic: sequential day/week numbers, slugs derived from titles,
 * IDs of the form Course01 / Course01-SS01 / W01 / D001. Each top-level unit
 * is a standalone course; the nine together form "365 Days of AI Mastery".
 */
import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import yaml from 'js-yaml';
import { sections, slugify } from '../curriculum/curriculum.source.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

let dayNumber = 0;
let weekNumber = 0;

const compiled = sections.map((section, si) => {
  const sectionId = `Course${String(si + 1).padStart(2, '0')}`;
  return {
    id: sectionId,
    slug: section.slug,
    title: section.title,
    summary: section.summary,
    subsections: section.subsections.map((sub, bi) => {
      const subId = `${sectionId}-SS${String(bi + 1).padStart(2, '0')}`;
      return {
        id: subId,
        slug: sub.slug,
        title: sub.title,
        summary: sub.summary,
        weeks: sub.weeks.map((week) => {
          weekNumber += 1;
          const wn = weekNumber;
          return {
            id: `W${String(wn).padStart(2, '0')}`,
            number: wn,
            theme: week.theme,
            project: week.project,
            days: week.days.map((title) => {
              dayNumber += 1;
              return {
                id: `D${String(dayNumber).padStart(3, '0')}`,
                number: dayNumber,
                slug: slugify(title),
                title,
              };
            }),
          };
        }),
      };
    }),
  };
});

if (dayNumber !== 365) {
  console.error(`FATAL: curriculum compiles to ${dayNumber} days, expected 365.`);
  process.exit(1);
}
if (weekNumber !== 52) {
  console.error(`FATAL: curriculum compiles to ${weekNumber} weeks, expected 52.`);
  process.exit(1);
}

const slugs = new Set();
for (const s of compiled)
  for (const b of s.subsections)
    for (const w of b.weeks)
      for (const d of w.days) {
        if (slugs.has(d.slug)) {
          console.error(`FATAL: duplicate day slug "${d.slug}" (day ${d.number}).`);
          process.exit(1);
        }
        slugs.add(d.slug);
      }

const doc = {
  course: {
    title: '365 Days of AI Mastery',
    slug: 'ai-roadmap',
    days: dayNumber,
    weeks: weekNumber,
    sections: compiled.length,
    generated_by: 'scripts/generate-curriculum.mjs',
    source: 'curriculum/curriculum.source.mjs',
  },
  sections: compiled,
};

const out = path.join(root, 'curriculum', 'curriculum.yml');
writeFileSync(
  out,
  '# GENERATED FILE — edit curriculum/curriculum.source.mjs and run `npm run generate:curriculum`.\n' +
    yaml.dump(doc, { lineWidth: 100, noRefs: true }),
);
console.log(`Wrote ${out}: ${compiled.length} sections, ${weekNumber} weeks, ${dayNumber} days.`);
