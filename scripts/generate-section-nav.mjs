#!/usr/bin/env node
/**
 * Generates collapsible, category-grouped navigation (amendments A19 + A20):
 *   - content/sections/<section>/README.md and labs/sections/<section>/README.md
 *     — each category is a collapsible <details> holding its day table.
 *   - CURRICULUM.md (repo root) — a master index: each section is a
 *     collapsible <details>, and inside it each category is a nested
 *     collapsible <details> holding the day table. Lets a reader drill from
 *     S01…S09 → "Days 1-7 · Inside the Machine" → day-by-day without a giant
 *     flat page.
 *
 * All links are relative and generated from the curriculum + progress
 * tracker, so nothing goes stale. GitHub renders <details>/<summary>
 * natively; blank lines around tables keep markdown rendering correct.
 */
import { writeFileSync, mkdirSync, readFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { loadCurriculum, allDays, repoRoot, loadConfig, loadYamlIfExists } from './lib/course.mjs';

function writeEnsured(file, contents) {
  mkdirSync(path.dirname(file), { recursive: true });
  writeFileSync(file, contents);
}

const curriculum = loadCurriculum();
const days = allDays();
const config = loadConfig();

function statusBadge(d) {
  return d.hasContent ? d.status : 'planned';
}

/**
 * The published blog URL for a day. It is derived from the configured site
 * base, never hand-maintained, so it cannot drift from where the page
 * actually is. A day with no lesson written yet has no blog post to link.
 */
function blogCell(d) {
  if (!d.hasContent) return '—';
  const base = config.website?.public_base_url;
  return base ? `[blog](${base}/${d.dayId})` : '_site not configured_';
}

/**
 * Every week is presented as one table with the same four columns, so a
 * reader always finds the same three destinations in the same places:
 * the lesson source, the hands-on lab, and the published blog post.
 *
 * `tree` decides how the relative links are written:
 *   'content' — the README lives in content/sections/<slug>/
 *   'labs'    — the README lives in labs/sections/<slug>/
 *   'root'    — the README lives at the repository root (CURRICULUM.md)
 *
 * Repository links are always RELATIVE. One repository holds both the lesson
 * and the lab (A31), so an absolute GitHub URL would be noise here - and
 * validate:links rejects absolute repository URLs under labs/ anyway. The
 * blog column is the one absolute URL, because it points off the repository
 * and onto the published site.
 */
function weekTable(sectionDays, sectionSlug, tree) {
  const prefix = {
    content: {
      lesson: (d) => `./${d.dayId}/`,
      lab: (d) => `../../../labs/sections/${sectionSlug}/${d.dayId}/`,
    },
    labs: {
      lesson: (d) => `../../../content/sections/${sectionSlug}/${d.dayId}/`,
      lab: (d) => `./${d.dayId}/`,
    },
    root: {
      lesson: (d) => `content/sections/${sectionSlug}/${d.dayId}/`,
      lab: (d) => `labs/sections/${sectionSlug}/${d.dayId}/`,
    },
  }[tree];
  const lines = ['| Day | Lesson | Lab | Blog | Status |', '| --- | --- | --- | --- | --- |'];
  for (const d of sectionDays) {
    const label = `Day ${String(d.number).padStart(3, '0')}`;
    if (!d.hasContent) {
      lines.push(`| ${label} | ${d.title} | — | — | planned |`);
      continue;
    }
    const lesson = `[${d.title}](${prefix.lesson(d)})`;
    const lab = `[lab](${prefix.lab(d)})`;
    const blog = blogCell(d);
    lines.push(`| ${label} | ${lesson} | ${lab} | ${blog} | ${statusBadge(d)} |`);
  }
  return lines.join('\n');
}

/** Group a section's days by week theme (the category), in order. */
function categories(sectionSlug) {
  const groups = [];
  const section = curriculum.sections.find((s) => s.slug === sectionSlug);
  for (const sub of section.subsections) {
    for (const wk of sub.weeks) {
      const ds = days.filter((d) => d.week === wk.number);
      if (ds.length === 0) continue;
      const done = ds.filter((d) => d.status === 'complete').length;
      groups.push({
        theme: wk.theme,
        first: ds[0].number,
        last: ds[ds.length - 1].number,
        days: ds,
        project: wk.project,
        done,
        total: ds.length,
      });
    }
  }
  return groups;
}

/** A collapsible <details> block. `open` expands it by default. */
function details(summary, body, open = false) {
  return `<details${open ? ' open' : ''}>\n<summary>${summary}</summary>\n\n${body}\n\n</details>`;
}

let count = 0;
for (const section of curriculum.sections) {
  const sectionDays = days.filter((d) => d.section === section.slug);
  const written = sectionDays.filter((d) => d.hasContent).length;
  const groups = categories(section.slug);

  // Expand the first category that still has unwritten days, so the "live"
  // part of the section is visible on open; completed-and-past stays collapsed.
  const firstOpenIdx = groups.findIndex((g) => g.done < g.total);

  const buildSectionReadme = (header, intro, tree) => {
    const lines = [
      header,
      '',
      '> GENERATED navigation — do not edit by hand. Run `npm run generate:section-nav`.',
      '',
      intro,
      '',
    ];
    groups.forEach((g, i) => {
      const summary = `<strong>Days ${g.first}-${g.last} · ${g.theme}</strong> — ${g.done}/${g.total} complete`;
      const body = [
        weekTable(g.days, section.slug, tree),
        '',
        `**Project:** ${g.project.title} — ${g.project.summary}`,
      ].join('\n');
      lines.push(details(summary, body, i === firstOpenIdx), '');
    });
    return lines.join('\n');
  };

  writeEnsured(
    path.join(repoRoot, 'content', 'sections', section.slug, 'README.md'),
    buildSectionReadme(
      `# ${section.id} · ${section.title}`,
      `${section.summary}\n\n**${written} of ${sectionDays.length} lessons written.** Expand a subsection below to see its days.`,
      'content',
    ) + '\n',
  );

  const labIntro =
    `Hands-on companions to this section's lessons. Each day directory is self-contained: open it, follow its README, finish with its tests passing.\n\n` +
    `**${written} of ${sectionDays.length} labs written.** Expand a subsection below to see its days.`;
  const labReadme =
    buildSectionReadme(`# ${section.id} · ${section.title} — hands-on labs`, labIntro, 'labs') +
    '\n## Conventions (all labs)\n\n' +
    '- `starter/` is yours to edit; `examples/` holds the completed reference.\n' +
    '- `tests/run_tests.sh` (or the lab’s declared test command) must exit 0 before a lab counts as done.\n' +
    '- `expected-output/` contains real captured runs, never fabricated text.\n' +
    '- Nothing needs sudo, accounts, or API keys unless `metadata.yml` says so — and a free alternative is always given.\n';
  writeEnsured(path.join(repoRoot, 'labs', 'sections', section.slug, 'README.md'), labReadme);
  count += 1;
}

// Master index: CURRICULUM.md at the repo root — nested collapsible views.
const totalDone = days.filter((d) => d.status === 'complete').length;
const master = [
  '# 365 Days of AI Mastery — curriculum index',
  '',
  '> GENERATED — do not edit by hand. Run `npm run generate:section-nav`.',
  '',
  `The complete map of all nine courses: **${totalDone} of 365 days complete.** Click a course to expand it, then a subsection, to drill down to individual days — nothing is shown all at once.`,
  '',
];
for (const section of curriculum.sections) {
  const sectionDays = days.filter((d) => d.section === section.slug);
  const done = sectionDays.filter((d) => d.status === 'complete').length;
  const groups = categories(section.slug);
  const inner = groups
    .map((g) => {
      const summary = `Days ${g.first}-${g.last} · ${g.theme} — ${g.done}/${g.total}`;
      return details(summary, weekTable(g.days, section.slug, 'root'));
    })
    .join('\n');
  const sectionSummary = `<h3>${section.id} · ${section.title} — ${done}/${sectionDays.length} complete</h3>`;
  // All sections collapsed by default; the reader expands what they want.
  master.push(details(sectionSummary, `${section.summary}\n\n${inner}`), '');
}
writeFileSync(path.join(repoRoot, 'CURRICULUM.md'), master.join('\n') + '\n');

// Private-README "Released labs" section (PRIVATE ONLY — mirrors the public
// repo's Released-labs view but adds a per-day Blog/Course lesson-URL column
// and per-course landing links, so the owner tracks where each day is
// published. URLs come from curriculum/published-urls.yml (filled in as days
// go live), else the configured deployment base, else an "add URL" prompt.
// Never emit a fabricated link. Injected between markers so the rest of the
// hand-written README is untouched.
const published = loadYamlIfExists(path.join(repoRoot, 'curriculum', 'published-urls.yml')) ?? {};
const dayUrls = published.days ?? {};
const courseUrls = published.courses ?? {};

function lessonUrlCell(d) {
  const explicit = dayUrls[d.number];
  if (explicit) return `[lesson](${explicit})`;
  if (config.website?.public_base_url)
    return `[lesson](${config.website.public_base_url}/${d.dayId})`;
  return '_add URL_';
}

function releasedLabsBlock() {
  const released = days.filter((d) => d.hasContent);
  const out = [
    `**${released.length} of 365 days released.** Expand a course, then a subsection, to reach its lab and its published blog/course lesson URL. Fill URLs in \`curriculum/published-urls.yml\` (or set the deployment base with \`npm run configure\`), then re-run \`npm run generate:section-nav\`.`,
    '',
  ];
  for (const section of curriculum.sections) {
    const secReleased = released.filter((d) => d.section === section.slug);
    if (secReleased.length === 0) continue;
    const courseUrl = courseUrls[section.id];
    const heading = courseUrl
      ? `<h3><a href="${courseUrl}">${section.id} · ${section.title}</a> — ${secReleased.length} lab(s)</h3>`
      : `<h3>${section.id} · ${section.title} — ${secReleased.length} lab(s)</h3>`;
    const catBlocks = [];
    for (const g of categories(section.slug)) {
      const gReleased = g.days.filter((d) => d.hasContent);
      if (gReleased.length === 0) continue;
      const rows = ['| Day | Lab | Blog / Course lesson |', '| --- | --- | --- |'];
      for (const d of gReleased) {
        rows.push(
          `| ${d.number} | [${d.title}](labs/sections/${d.section}/${d.dayId}/README.md) | ${lessonUrlCell(d)} |`,
        );
      }
      catBlocks.push(details(`Days ${g.first}-${g.last} · ${g.theme}`, rows.join('\n')));
    }
    out.push(details(heading, catBlocks.join('\n')), '');
  }
  return out.join('\n').trimEnd();
}

// Progress badges in the README hero. Generated for the same reason the
// navigation is (A19): a hand-typed count goes stale the day after it is
// typed, and a stale count on the landing page is the most visible kind of
// lie a repository can tell.
function statsBlock() {
  const written = days.filter((d) => d.hasContent).length;
  const complete = days.filter((d) => d.status === 'complete').length;
  const badge = (label, value, color) =>
    `  <img alt="${label}" src="https://img.shields.io/badge/${encodeURIComponent(label)}-${encodeURIComponent(value)}-${color}">`;
  return [
    '<p align="center">',
    badge('lessons', `${written} / 365`, '1d4ed8'),
    badge('labs', `${days.filter((d) => d.hasLab).length} / 365`, '4f46e5'),
    badge('days complete', `${complete} / 365`, '16a34a'),
    badge('courses', '9', '7c3aed'),
    badge('weekly projects', '52', '9333ea'),
    badge('cost', 'free & open source', '16a34a'),
    badge('prerequisites', 'none', '0891b2'),
    '</p>',
  ].join('\n');
}

const STATS_START =
  '<!-- STATS:START — generated by npm run generate:section-nav; do not edit by hand -->';
const STATS_END = '<!-- STATS:END -->';

const README_START = '<!-- RELEASED-LABS:START -->';
const README_END = '<!-- RELEASED-LABS:END -->';
const readmePath = path.join(repoRoot, 'README.md');
let injectedReleased = false;
let injectedStats = false;
if (existsSync(readmePath)) {
  let readme = readFileSync(readmePath, 'utf8');
  if (readme.includes(README_START) && readme.includes(README_END)) {
    const block = `${README_START}\n\n${releasedLabsBlock()}\n\n${README_END}`;
    readme = readme.replace(new RegExp(`${README_START}[\\s\\S]*?${README_END}`), block);
    injectedReleased = true;
  }
  if (readme.includes(STATS_START) && readme.includes(STATS_END)) {
    const block = `${STATS_START}\n${statsBlock()}\n${STATS_END}`;
    readme = readme.replace(
      new RegExp(`${STATS_START.replace(/[.*+?^${}()|[\]\\—]/g, '\\$&')}[\\s\\S]*?${STATS_END}`),
      block,
    );
    injectedStats = true;
  }
  writeFileSync(readmePath, readme);
}

console.log(
  `✓ generate:section-nav: wrote ${count} section README(s) + CURRICULUM.md${injectedReleased ? ' + README Released-labs' : ''}${injectedStats ? ' + README stats badges' : ''} with collapsible category navigation.`,
);
