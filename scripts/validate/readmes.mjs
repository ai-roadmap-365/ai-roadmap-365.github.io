#!/usr/bin/env node
/**
 * README validation (requirements §5, §15; amendments A18/A19): root README
 * headings; GENERATED section READMEs (content + labs) that group days under
 * category headings and list every authored day with a link; and daily
 * lesson/lab READMEs. Subsection and week READMEs no longer exist — the flat
 * per-section structure uses generated section navigation instead.
 */
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { allDays, loadCurriculum, repoRoot, makeReporter } from '../lib/course.mjs';
import { ROOT_README_HEADINGS } from '../lib/contracts.mjs';

const r = makeReporter('validate:readmes');
const curriculum = loadCurriculum();
const days = allDays();
const authored = days.filter((d) => d.hasContent);

function checkHeadings(file, headings, tag) {
  if (!existsSync(file)) {
    r.fail(`${tag}: missing README at ${path.relative(repoRoot, file)}`);
    return null;
  }
  const text = readFileSync(file, 'utf8');
  if (text.trim().length < 200) r.fail(`${tag}: README is effectively empty`);
  for (const h of headings) {
    if (!text.includes(`\n${h}`)) r.fail(`${tag}: missing required heading "${h}"`);
  }
  return text;
}

// Root README.
const root = checkHeadings(path.join(repoRoot, 'README.md'), ROOT_README_HEADINGS, 'root');
if (root) {
  for (const cmd of ['npm install', 'npm run dev', 'npm run build', 'npm run verify:all']) {
    if (!root.includes(cmd)) r.fail(`root: README does not document \`${cmd}\``);
  }
  if (!root.includes('corepack enable'))
    r.fail('root: README missing the corepack/Windows setup steps');
}

// Generated section READMEs: present for every section with authored days,
// grouping days under category headings with a link + status per day.
for (const section of curriculum.sections) {
  const sectionAuthored = authored.filter((d) => d.section === section.slug);
  if (sectionAuthored.length === 0) continue;
  for (const [tree, label] of [
    ['content', 'content'],
    ['labs', 'labs'],
  ]) {
    const file = path.join(repoRoot, tree, 'sections', section.slug, 'README.md');
    const text = checkHeadings(file, [], `${label} section ${section.slug}`);
    if (!text) continue;
    if (!text.includes('GENERATED'))
      r.fail(
        `${label} section ${section.slug}: README is not the generated file (run generate:section-nav)`,
      );
    // Every authored day must be linked; every category heading present.
    for (const d of sectionAuthored) {
      if (!text.includes(`./${d.dayId}/`))
        r.fail(
          `${label} section ${section.slug}: README does not link authored day ${d.number} (${d.dayId})`,
        );
    }
    // At least one "Days X-Y ·" collapsible category section.
    if (!/Days \d+-\d+ ·/.test(text))
      r.fail(`${label} section ${section.slug}: README has no category sections`);
    if (!text.includes('<details>'))
      r.fail(
        `${label} section ${section.slug}: README is not collapsible (run generate:section-nav)`,
      );
  }
}

// Master curriculum index with nested collapsible views.
{
  const file = path.join(repoRoot, 'CURRICULUM.md');
  const text = checkHeadings(file, [], 'CURRICULUM.md');
  if (text) {
    if (!text.includes('<details>'))
      r.fail('CURRICULUM.md: not collapsible (run generate:section-nav)');
    for (const s of curriculum.sections)
      if (!text.includes(`${s.id} · ${s.title}`)) r.fail(`CURRICULUM.md: missing section ${s.id}`);
  }
}

// Daily READMEs (lesson + lab) for every authored day — heading contracts
// are enforced by validate:lessons / validate:labs; here we enforce presence
// and cross-links.
for (const d of authored) {
  const lessonReadme = path.join(d.contentDir, 'README.md');
  const labReadme = path.join(d.labDir, 'README.md');
  if (!existsSync(lessonReadme)) r.fail(`day ${d.number}: missing lesson README`);
  if (!existsSync(labReadme)) {
    r.fail(`day ${d.number}: missing lab README`);
    continue;
  }
  const lab = readFileSync(labReadme, 'utf8');
  if (!lab.includes('generated-links:start'))
    r.fail(`day ${d.number}: lab README missing the generated-links block`);
}

r.finish('root README, generated section navigation, and daily READMEs present and correct.');
