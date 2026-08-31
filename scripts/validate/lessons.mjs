#!/usr/bin/env node
/**
 * Validates every authored lesson directory against the completion contract:
 * required files, exact heading set, sidecar schemas, matching visuals,
 * no placeholder markers, no hard-coded repository/localhost URLs in content.
 */
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import { allDays, loadSidecars, makeReporter, repoRoot } from '../lib/course.mjs';
import { videoPath } from '../lib/links.mjs';
import {
  FORBIDDEN_STRINGS,
  findForbidden,
  LESSON_HEADINGS,
  LESSON_HANDS_ON_HEADINGS,
  LESSON_FIELDS,
  LESSON_README_HEADINGS,
} from '../lib/contracts.mjs';

const r = makeReporter('validate:lessons');
const authored = allDays().filter((d) => d.hasContent);
const complete = allDays().filter((d) => d.status === 'complete');

for (const d of complete) {
  if (!d.hasContent) r.fail(`day ${d.number} is marked complete but has no content directory`);
}

const REQUIRED_FILES = [
  'index.mdx',
  'lesson.yml',
  'quiz.yml',
  'glossary.yml',
  'sources.yml',
  'visuals.yml',
  'README.md',
];

for (const d of authored) {
  const tag = `day ${d.number}`;
  for (const f of REQUIRED_FILES) {
    if (!existsSync(path.join(d.contentDir, f))) r.fail(`${tag}: missing ${f}`);
  }
  const assetsDir = path.join(d.contentDir, 'assets');
  if (!existsSync(assetsDir) || readdirSync(assetsDir).length === 0)
    r.fail(`${tag}: assets/ missing or empty`);
  if (!existsSync(path.join(d.contentDir, 'index.mdx'))) continue;

  const mdx = readFileSync(path.join(d.contentDir, 'index.mdx'), 'utf8');

  // Frontmatter identity matches the curriculum.
  const fm = mdx.match(/^---\n([\s\S]*?)\n---\n/);
  if (!fm) r.fail(`${tag}: index.mdx has no frontmatter`);
  else {
    if (!new RegExp(`^day:\\s*${d.number}\\s*$`, 'm').test(fm[1]))
      r.fail(`${tag}: frontmatter day != ${d.number}`);
    if (!fm[1].includes(d.title))
      r.fail(`${tag}: frontmatter title does not match curriculum title "${d.title}"`);
  }

  // Exact required headings, in order.
  let cursor = 0;
  for (const h of LESSON_HEADINGS) {
    const idx = mdx.indexOf(`\n${h}\n`, cursor);
    if (idx === -1) {
      r.fail(`${tag}: missing or out-of-order heading "${h}"`);
    } else {
      cursor = idx;
    }
  }
  for (const h of LESSON_HANDS_ON_HEADINGS) {
    if (!mdx.includes(`\n${h}\n`)) r.fail(`${tag}: hands-on section missing "${h}"`);
  }

  // No fake-completion markers.
  for (const hit of findForbidden(mdx))
    r.fail(`${tag}: index.mdx contains forbidden marker "${hit}"`);

  // Content files never hard-code repo or site URLs (central config only).
  if (/github\.com|localhost:\d+/i.test(mdx))
    r.fail(`${tag}: index.mdx hard-codes a repository/site URL`);

  // Substance floor: a "complete lesson, not a summary" (≥2500 words).
  const words = mdx.split(/\s+/).length;
  if (words < 2500)
    r.fail(`${tag}: lesson body is only ${words} words — complete lessons are substantial (≥2500)`);

  const sc = loadSidecars(d);
  for (const field of LESSON_FIELDS) {
    if (sc.lesson[field] === undefined || sc.lesson[field] === null || sc.lesson[field] === '')
      r.fail(`${tag}: lesson.yml missing field "${field}"`);
  }
  if (sc.lesson.day !== d.number) r.fail(`${tag}: lesson.yml day mismatch`);
  if (sc.lesson.slug !== d.slug) r.fail(`${tag}: lesson.yml slug mismatch`);
  if ((sc.lesson.objectives ?? []).length < 4) r.fail(`${tag}: fewer than 4 learning objectives`);

  if (!sc.quiz || (sc.quiz.questions ?? []).length < 5)
    r.fail(`${tag}: quiz has fewer than 5 questions`);
  for (const [i, q] of (sc.quiz?.questions ?? []).entries()) {
    if (!q.question || !Array.isArray(q.options) || q.options.length < 3)
      r.fail(`${tag}: quiz Q${i + 1} malformed`);
    else if (
      !Number.isInteger(q.answer_index) ||
      q.answer_index < 0 ||
      q.answer_index >= q.options.length
    )
      r.fail(`${tag}: quiz Q${i + 1} answer_index out of range`);
    if (!q.explanation) r.fail(`${tag}: quiz Q${i + 1} has no explanation`);
  }

  if (!sc.glossary || (sc.glossary.terms ?? []).length < 8)
    r.fail(`${tag}: glossary has fewer than 8 terms`);

  // Visual declarations and embeds must agree; every asset must exist.
  const declared = sc.visuals?.visuals ?? [];
  if (declared.length < 1) r.fail(`${tag}: visuals.yml declares no visuals`);
  const embeddedAlts = [...mdx.matchAll(/!\[([^\]]*)\]\(\.\/([^)]+)\)/g)];
  // Two visuals sharing one alt string would let an unembedded one pass the
  // check below, because the match is by text. Reject the collision itself:
  // two diagrams described identically are also a content problem.
  const altOwners = new Map();
  for (const v of declared) {
    if (!v.alt) continue;
    if (altOwners.has(v.alt))
      r.fail(`${tag}: visuals ${altOwners.get(v.alt)} and ${v.id} share alt text "${v.alt}"`);
    else altOwners.set(v.alt, v.id);
  }
  for (const v of declared) {
    if (!existsSync(path.join(d.contentDir, v.file)))
      r.fail(`${tag}: visual file missing: ${v.file}`);
    if (!v.alt) r.fail(`${tag}: visual ${v.id} has no alt text`);
    else {
      // Match on the file, then check the alt: matching on alt alone cannot
      // tell an embedded visual from a different one that reads the same.
      const embeds = embeddedAlts.filter((m) => m[2] === v.file);
      if (embeds.length === 0)
        r.fail(`${tag}: visual ${v.id} (${v.file}) not embedded in index.mdx`);
      else if (embeds.length > 1)
        r.fail(`${tag}: visual ${v.id} embedded ${embeds.length} times in index.mdx`);
      else if (embeds[0][1] !== v.alt)
        r.fail(`${tag}: visual ${v.id} embedded with alt "${embeds[0][1]}", declared "${v.alt}"`);
    }
  }
  for (const m of embeddedAlts) {
    if (!existsSync(path.join(d.contentDir, m[2])))
      r.fail(`${tag}: index.mdx references missing image ${m[2]}`);
    if (!declared.some((v) => v.file === m[2]))
      r.fail(`${tag}: embedded image ${m[2]} not declared in visuals.yml`);
  }

  // Generated video prompt must exist (amendment A11); flat path (A18).
  const videoPrompt = path.join(repoRoot, videoPath(d), 'videoprompt.md');
  if (!existsSync(videoPrompt))
    r.fail(
      `${tag}: missing generated video prompt — run npm run generate:video-prompts -- --day ${d.number}`,
    );

  // Lesson README with required headings.
  const readmePath = path.join(d.contentDir, 'README.md');
  if (existsSync(readmePath)) {
    const readme = readFileSync(readmePath, 'utf8');
    for (const h of LESSON_README_HEADINGS) {
      if (!readme.includes(h)) r.fail(`${tag}: lesson README missing heading "${h}"`);
    }
  }
}

r.finish(
  `${authored.length} authored lesson(s) pass the content contract (${FORBIDDEN_STRINGS.length} forbidden markers scanned, headings, sidecars, visuals).`,
);
