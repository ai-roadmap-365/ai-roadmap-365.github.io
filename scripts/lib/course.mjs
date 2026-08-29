/**
 * Course data access for Node scripts (validators, release pipeline).
 * Mirrors src/lib/{config,curriculum}.ts for plain-ESM consumers; the vitest
 * suite asserts both stay in agreement.
 */
import { readFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';
import { lessonContentPath, labPath, dayId } from './links.mjs';

/**
 * Repo root found by walking up from cwd to the directory holding
 * curriculum/curriculum.yml. import.meta.url is NOT usable here: when the
 * site bundles this module, the URL points into dist/.
 */
function findRepoRoot() {
  let dir = process.cwd();
  for (let i = 0; i < 10; i += 1) {
    if (existsSync(path.join(dir, 'curriculum', 'curriculum.yml'))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return process.cwd();
}

export const repoRoot = findRepoRoot();

export function loadConfig() {
  return yaml.load(readFileSync(path.join(repoRoot, 'config', 'course.config.yml'), 'utf8'));
}

export function loadCurriculum() {
  return yaml.load(readFileSync(path.join(repoRoot, 'curriculum', 'curriculum.yml'), 'utf8'));
}

export function loadProgress() {
  const file = path.join(repoRoot, 'curriculum', 'progress.yml');
  if (!existsSync(file)) return {};
  const doc = yaml.load(readFileSync(file, 'utf8'));
  return doc?.days ?? {};
}

/** All 365 days flattened with hierarchy context and on-disk state. */
export function allDays() {
  const curriculum = loadCurriculum();
  const progress = loadProgress();
  const days = [];
  for (const section of curriculum.sections) {
    for (const sub of section.subsections) {
      for (const week of sub.weeks) {
        for (const day of week.days) {
          const ref = {
            number: day.number,
            slug: day.slug,
            section: section.slug,
            subsection: sub.slug,
            week: week.number,
          };
          days.push({
            ...ref,
            id: day.id,
            title: day.title,
            sectionTitle: section.title,
            subsectionTitle: sub.title,
            weekTheme: week.theme,
            weekProject: week.project,
            dayId: dayId(ref),
            contentDir: path.join(repoRoot, lessonContentPath(ref)),
            labDir: path.join(repoRoot, labPath(ref)),
            hasContent: existsSync(path.join(repoRoot, lessonContentPath(ref), 'index.mdx')),
            hasLab: existsSync(path.join(repoRoot, labPath(ref), 'README.md')),
            status: progress[day.number]?.status ?? 'planned',
            completion: progress[day.number]?.completion ?? {},
          });
        }
      }
    }
  }
  return days;
}

export function loadYamlIfExists(file) {
  return existsSync(file) ? yaml.load(readFileSync(file, 'utf8')) : null;
}

/** Sidecar YAML files for an authored day. */
export function loadSidecars(day) {
  return {
    lesson: loadYamlIfExists(path.join(day.contentDir, 'lesson.yml')) ?? {},
    quiz: loadYamlIfExists(path.join(day.contentDir, 'quiz.yml')),
    glossary: loadYamlIfExists(path.join(day.contentDir, 'glossary.yml')),
    sources: loadYamlIfExists(path.join(day.contentDir, 'sources.yml')),
    visuals: loadYamlIfExists(path.join(day.contentDir, 'visuals.yml')),
  };
}

/** Simple CLI arg lookup: argValue(['--day']) → '1'. */
export function argValue(names, argv = process.argv) {
  for (let i = 0; i < argv.length; i += 1) {
    if (names.includes(argv[i])) return argv[i + 1];
    for (const n of names) {
      if (argv[i].startsWith(`${n}=`)) return argv[i].slice(n.length + 1);
    }
  }
  return undefined;
}

/** Shared reporter for validators: collects failures, exits non-zero. */
export function makeReporter(name) {
  const failures = [];
  return {
    fail(message) {
      failures.push(message);
    },
    finish(okMessage) {
      if (failures.length > 0) {
        console.error(`✗ ${name}: ${failures.length} problem(s)`);
        for (const f of failures) console.error(`  - ${f}`);
        process.exit(1);
      }
      console.log(`✓ ${name}: ${okMessage}`);
    },
    get failures() {
      return failures;
    },
  };
}
