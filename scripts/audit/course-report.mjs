#!/usr/bin/env node
/**
 * Per-course audit report: the machine-checkable half.
 *
 *   node scripts/audit/course-report.mjs --section computing-foundations
 *   node scripts/audit/course-report.mjs --section computing-foundations --md > report.md
 *
 * This measures what a script CAN measure honestly. It never scores teaching
 * quality -- that is the reviewer's job, and docs/course-audit/rubric.md is
 * what they use. Anything here reported as a warning is a candidate for human
 * judgement, not an automatic defect.
 */
import fs from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';
import { allDays, repoRoot } from '../lib/course.mjs';

const args = process.argv.slice(2);
const asMarkdown = args.includes('--md');

/**
 * Accept either the slug or the course's display name, so the caller can
 * write what they see on the site rather than looking up a slug:
 *   --section computing-foundations
 *   --course "Computing Foundations"
 */
const flagValue = (flag) => {
  const i = args.indexOf(flag);
  // indexOf returns -1 when the flag is absent, and args[-1 + 1] is args[0],
  // which is the NEXT flag rather than a missing value.
  return i === -1 ? null : (args[i + 1] ?? null);
};
const rawArg = flagValue('--section') ?? flagValue('--course');
if (!rawArg || rawArg.startsWith('--')) {
  console.error('usage: course-report.mjs (--section <slug> | --course "<Course Name>") [--md]');
  process.exit(2);
}

const norm = (s) =>
  String(s)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '');
const allTheDays = allDays();
const known = new Map();
for (const d of allTheDays) if (!known.has(d.section)) known.set(d.section, d.sectionTitle);

let sectionArg = null;
for (const [slug, title] of known) {
  if (norm(slug) === norm(rawArg) || norm(title) === norm(rawArg)) sectionArg = slug;
}
// Fall back to a unique prefix match, so "Deployment" finds the long one.
if (!sectionArg) {
  const hits = [...known].filter(
    ([slug, title]) => norm(title).startsWith(norm(rawArg)) || norm(slug).startsWith(norm(rawArg)),
  );
  if (hits.length === 1) sectionArg = hits[0][0];
}
if (!sectionArg) {
  console.error(`no course matches ${JSON.stringify(rawArg)}. Known courses:`);
  for (const [slug, title] of known) console.error(`  ${title}  (${slug})`);
  process.exit(2);
}

const read = (p) => (fs.existsSync(p) ? fs.readFileSync(p, 'utf8') : null);
const loadYaml = (p) => {
  const raw = read(p);
  if (raw === null) return null;
  try {
    return yaml.load(raw);
  } catch (e) {
    return { __error: e.message };
  }
};

/** Prose without code fences, tables, headings, images or list markers. */
function proseParagraphs(mdx) {
  const body = mdx
    .replace(/^---\n[\s\S]*?\n---\n/, '')
    .replace(/```[\s\S]*?```/g, '')
    .replace(/^\|.*$/gm, '')
    .replace(/^#{1,6} .*$/gm, '')
    .replace(/^!\[.*$/gm, '');
  return body
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter((p) => p && !/^[-*>\d]/.test(p))
    .map((p) => ({ words: p.split(/\s+/).length, text: p }));
}

function analyseDay(day) {
  const c = day.contentDir;
  const l = day.labDir;
  const mdx = read(path.join(c, 'index.mdx')) ?? '';
  const paras = proseParagraphs(mdx);
  const words = mdx.split(/\s+/).length;
  // Prose only: code blocks are not what "too much essay" means.
  const proseWords = mdx
    .replace(/^---\n[\s\S]*?\n---\n/, '')
    .replace(/```[\s\S]*?```/g, '')
    .split(/\s+/)
    .filter(Boolean).length;
  const readingMinutes = Math.round(proseWords / 240);
  const quiz = loadYaml(path.join(c, 'quiz.yml'));
  const glossary = loadYaml(path.join(c, 'glossary.yml'));
  const sources = loadYaml(path.join(c, 'sources.yml'));
  const visuals = loadYaml(path.join(c, 'visuals.yml'));
  const lessonYml = loadYaml(path.join(c, 'lesson.yml'));
  const meta = loadYaml(path.join(l, 'metadata.yml'));

  const imagesInProse = (mdx.match(/^!\[/gm) || []).length;
  const codeBlocks = (mdx.match(/```/g) || []).length / 2;
  const tables = (mdx.match(/^\|/gm) || []).length;
  const svgFiles = fs.existsSync(path.join(c, 'assets'))
    ? fs.readdirSync(path.join(c, 'assets')).filter((f) => f.endsWith('.svg'))
    : [];

  const longest = paras.reduce((m, p) => Math.max(m, p.words), 0);
  const heavy = paras.filter((p) => p.words > 120).length;

  const starterFiles = fs.existsSync(path.join(l, 'starter'))
    ? fs.readdirSync(path.join(l, 'starter'))
    : [];
  const identicalStarter = starterFiles.some((f) => {
    const a = path.join(l, 'starter', f);
    const b = path.join(l, 'examples', f);
    return fs.existsSync(b) && fs.readFileSync(a, 'utf8') === fs.readFileSync(b, 'utf8');
  });

  const socialDir = path.join(repoRoot, 'social-media', day.dayId);
  const videoDir = path.join(repoRoot, 'videos', 'sections', day.section, day.dayId);
  const solution = path.join(
    repoRoot,
    'instructor',
    'project-solutions',
    'sections',
    day.section,
    day.dayId,
    'SOLUTION.md',
  );
  const hero = path.join(repoRoot, 'public', 'social', `${day.dayId}.png`);

  return {
    day: day.number,
    dayId: day.dayId,
    title: day.title,
    words,
    proseWords,
    readingMinutes,
    longestParagraph: longest,
    heavyParagraphs: heavy,
    visuals: svgFiles.length,
    imagesInProse,
    codeBlocks,
    tableRows: tables,
    // Denominator is TOTAL words, not the proseWords column beside it in the
    // report table. Keep the two distinct: reading time is about prose, while
    // diagram density is about the whole page a learner scrolls through.
    visualsPer1kWords: +(svgFiles.length / (words / 1000) || 0).toFixed(2),
    quiz: Array.isArray(quiz?.questions) ? quiz.questions.length : 0,
    glossary: Array.isArray(glossary?.terms) ? glossary.terms.length : 0,
    sources: Array.isArray(sources?.sources) ? sources.sources.length : 0,
    visualsDeclared: Array.isArray(visuals?.visuals) ? visuals.visuals.length : 0,
    hasLessonYml: !!lessonYml && !lessonYml.__error,
    hasLabMeta: !!meta && !meta.__error,
    labKind: meta?.kind ?? null,
    requiresNetwork: meta?.requires_network ?? null,
    hasTests: fs.existsSync(path.join(l, 'tests', 'run_tests.sh')),
    hasStarter: starterFiles.length > 0,
    starterIdenticalToSolution: identicalStarter,
    hasExpectedOutput: fs.existsSync(path.join(l, 'expected-output')),
    hasSecurityMd: fs.existsSync(path.join(l, 'security.md')),
    hasTroubleshooting: fs.existsSync(path.join(l, 'troubleshooting.md')),
    hasSocialPost: fs.existsSync(path.join(socialDir, 'post.html')),
    hasVideoPrompt:
      fs.existsSync(videoDir) && fs.readdirSync(videoDir).some((f) => f.endsWith('.md')),
    hasInstructorSolution: fs.existsSync(solution),
    hasHeroImage: fs.existsSync(hero),
  };
}

const days = allTheDays.filter((d) => d.section === sectionArg);
if (!days.length) {
  console.error(`no days found for section '${sectionArg}'`);
  process.exit(2);
}
const rows = days.map(analyseDay);

/** Thresholds are advisory. They mark a day for a human to look at. */
const FLAGS = [
  [
    'proseWords',
    (r) => r.proseWords > 3500,
    'over 3,500 words of prose (more than ~15 minutes of reading)',
  ],
  ['longestParagraph', (r) => r.longestParagraph > 150, 'a paragraph over 150 words'],
  ['heavyParagraphs', (r) => r.heavyParagraphs >= 4, 'four or more paragraphs over 120 words'],
  ['visuals', (r) => r.visuals < 2, 'fewer than two diagrams'],
  ['quiz', (r) => r.quiz < 5, 'fewer than five quiz questions'],
  ['glossary', (r) => r.glossary < 8, 'fewer than eight glossary terms'],
  ['sources', (r) => r.sources < 3, 'fewer than three sources'],
  ['starter', (r) => r.starterIdenticalToSolution, 'starter identical to the solution'],
  ['tests', (r) => !r.hasTests, 'no runnable test suite'],
  [
    'artifacts',
    (r) => !r.hasSocialPost || !r.hasVideoPrompt || !r.hasHeroImage || !r.hasInstructorSolution,
    'a missing social post, video prompt, hero image or instructor solution',
  ],
];

const flagged = rows.map((r) => ({
  r,
  hits: FLAGS.filter(([, f]) => f(r)).map(([, , msg]) => msg),
}));
const withFlags = flagged.filter((f) => f.hits.length);

const avg = (k) => +(rows.reduce((s, r) => s + r[k], 0) / rows.length).toFixed(1);

if (!asMarkdown) {
  console.log(`\n${known.get(sectionArg)}  (${sectionArg}, ${rows.length} days)\n`);
  console.log(
    `  mean prose words        ${avg('proseWords')}   (~${avg('readingMinutes')} min to read)`,
  );
  console.log(`  mean longest paragraph  ${avg('longestParagraph')} words`);
  console.log(`  mean diagrams per day   ${avg('visuals')}`);
  console.log(`  mean diagrams / 1k total words ${avg('visualsPer1kWords')}`);
  console.log(`\n  days with at least one flag: ${withFlags.length} of ${rows.length}\n`);
  for (const { r, hits } of withFlags) {
    console.log(`  day ${r.day} — ${r.title}`);
    for (const h of hits) console.log(`      · ${h}`);
  }
  console.log('');
  process.exit(0);
}

const esc = (s) => String(s).replace(/\|/g, '\\|');
const lines = [];
lines.push(`# Course audit — ${known.get(sectionArg)}`, '');
lines.push(`\`${sectionArg}\``, '');
lines.push(`${rows.length} days. Generated by \`scripts/audit/course-report.mjs\`.`, '');
lines.push('## Density and structure', '');
lines.push(
  '| Day | Title | Prose words | Read | Longest ¶ | Heavy ¶ | Diagrams | /1k total | Quiz | Gloss | Sources |',
);
lines.push('| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |');
for (const r of rows) {
  lines.push(
    `| ${r.day} | ${esc(r.title)} | ${r.proseWords} | ${r.readingMinutes}m | ${r.longestParagraph} | ${r.heavyParagraphs} | ${r.visuals} | ${r.visualsPer1kWords} | ${r.quiz} | ${r.glossary} | ${r.sources} |`,
  );
}
lines.push('', '## Lab and artefacts', '');
lines.push(
  '| Day | Tests | Starter | Stubbed | Expected out | security.md | trouble | Social | Video | Hero | Solution |',
);
lines.push('| ---: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |');
const t = (b) => (b ? '✓' : '✗');
for (const r of rows) {
  lines.push(
    `| ${r.day} | ${t(r.hasTests)} | ${t(r.hasStarter)} | ${t(!r.starterIdenticalToSolution)} | ${t(r.hasExpectedOutput)} | ${t(r.hasSecurityMd)} | ${t(r.hasTroubleshooting)} | ${t(r.hasSocialPost)} | ${t(r.hasVideoPrompt)} | ${t(r.hasHeroImage)} | ${t(r.hasInstructorSolution)} |`,
  );
}
lines.push('', '## Flagged for human review', '');
if (!withFlags.length) lines.push('None.');
for (const { r, hits } of withFlags) {
  lines.push(`- **Day ${r.day} — ${r.title}**`);
  for (const h of hits) lines.push(`  - ${h}`);
}
console.log(lines.join('\n'));
