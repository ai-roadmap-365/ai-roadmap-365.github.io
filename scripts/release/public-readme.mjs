#!/usr/bin/env node
/**
 * Generates the PUBLIC repository's homepage README (labs-only, generic —
 * amendment A6). Released days are shown as nested collapsible views
 * (section → category → days, amendment A20) so the page stays compact as
 * the course grows. Regenerate on every release. Writes to stdout or
 * --out <path>. Links are relative (repository-neutral, A10).
 */
import { writeFileSync } from 'node:fs';
import { allDays, loadConfig, loadCurriculum, argValue } from '../lib/course.mjs';

const config = loadConfig();
const curriculum = loadCurriculum();
const days = allDays();
const released = days.filter((d) => d.status === 'complete');
const blogBase = config.website.public_base_url;

function details(summary, body, open = false) {
  return `<details${open ? ' open' : ''}>\n<summary>${summary}</summary>\n\n${body}\n\n</details>`;
}

const lines = [];
lines.push('# 365 Days of AI Mastery — hands-on labs');
lines.push('');
lines.push(
  'One practical, self-contained lab for every day of **365 Days of AI Mastery** — a year-long path, delivered as nine standalone courses, from computing foundations to building and shipping production AI systems. This repository holds the hands-on exercises; each daily lesson article is published on the course blog and links to its lab here.',
);
lines.push('');
lines.push('## How to use a lab');
lines.push('');
lines.push('```bash');
lines.push(`git clone ${config.repository.public_url ?? '<this repository>'}.git`);
lines.push(
  `cd ${config.repository.public_name ?? 'ai-roadmap-365'}/labs/sections/<section>/day-<nnn>-<slug>`,
);
lines.push('```');
lines.push('');
lines.push("Then follow that day's `README.md`. Every lab is independently usable and includes:");
lines.push('');
lines.push('- `starter/` — the files you work in, with clearly numbered exercises');
lines.push('- `examples/` — a completed reference implementation');
lines.push('- `tests/` — automated checks (run them; they exit 0 when you are done)');
lines.push('- `expected-output/` — genuinely captured runs to compare against');
lines.push('- `requirements/`, `troubleshooting.md`, `security.md`');
lines.push('');
lines.push(
  "Labs use free and open-source tools wherever possible; any exception (for example an API key) is declared in the lab's `metadata.yml` and README, always with a free alternative.",
);
lines.push('');
lines.push('## Released labs');
lines.push('');
lines.push(
  `**${released.length} of 365 days released.** Expand a course, then a subsection, to find a lab.`,
);
lines.push('');

// Nested collapsible: only sections/categories that have released days.
for (const section of curriculum.sections) {
  const sectionReleased = released.filter((d) => d.section === section.slug);
  if (sectionReleased.length === 0) continue;
  const categoryBlocks = [];
  for (const sub of section.subsections) {
    for (const wk of sub.weeks) {
      const catDays = sectionReleased.filter((d) => d.week === wk.number);
      if (catDays.length === 0) continue;
      const first = catDays[0].number;
      const last = catDays[catDays.length - 1].number;
      const table = ['| Day | Lab |', '| --- | --- |'];
      for (const d of catDays) {
        table.push(
          `| ${d.number} | [${d.title}](labs/sections/${d.section}/${d.dayId}/README.md) |`,
        );
      }
      categoryBlocks.push(details(`Days ${first}-${last} · ${wk.theme}`, table.join('\n')));
    }
  }
  lines.push(
    details(
      `<h3>${section.id} · ${section.title} — ${sectionReleased.length} lab(s)</h3>`,
      categoryBlocks.join('\n'),
    ),
    '',
  );
}

lines.push(
  released.length <= 14
    ? 'New labs are released as the course rolls out — a new day with each blog post.'
    : `${released.length} days released so far; a new day is released with each blog post.`,
);
lines.push('');
lines.push('## The course');
lines.push('');
lines.push(
  blogBase
    ? `Read the daily lessons at ${blogBase} — each post explains the concepts behind that day's lab and links back here.`
    : 'Each daily lesson is published on the course blog (link coming with the first public post); every post links to its matching lab directory here.',
);
lines.push('');
lines.push('## License and contributions');
lines.push('');
lines.push(
  '© Sandeep Bazar. Lab content is provided for personal learning alongside the course; issues and corrections are welcome via GitHub issues.',
);
lines.push('');

const out = argValue(['--out']);
const text = lines.join('\n');
if (out) {
  writeFileSync(out, text);
  console.log(
    `✓ public README written to ${out} (${released.length} released day(s), collapsible)`,
  );
} else {
  console.log(text);
}
