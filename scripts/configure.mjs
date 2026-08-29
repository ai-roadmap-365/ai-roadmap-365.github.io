#!/usr/bin/env node
/**
 * npm run configure — the ONE place to (re)point the course at its homes.
 *
 * Interactively asks for:
 *   1. the private (master) repository URL,
 *   2. the public (labs-only) repository URL,
 *   3. the blog/course deployment base URL (e.g. https://techhorizon.com/courses/ai-roadmap-365),
 *   4. the local development base URL (host/port),
 * writes them to config/course.config.yml, regenerates every generated link
 * in the repository (lab READMEs, README.html), regenerates any existing
 * WordPress/public-release exports so their links match, and finally offers
 * to commit the private repo and sync + commit + push a local clone of the
 * public repo. Nothing is pushed without an explicit yes.
 */
import { createInterface } from 'node:readline/promises';
import { writeFileSync, existsSync, readdirSync, cpSync, statSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import yaml from 'js-yaml';
import { repoRoot, loadConfig, allDays } from './lib/course.mjs';
import { updateLinks } from './update-links.mjs';

const rl = createInterface({ input: process.stdin, output: process.stdout });

function normalizeBase(url) {
  return url ? url.replace(/\/+$/, '') : null;
}

async function ask(question, current) {
  const answer = (await rl.question(`${question}\n  [current: ${current ?? 'not set'}] > `)).trim();
  if (answer === '') return current ?? null;
  if (answer === '-') return null; // explicit clear
  return answer;
}

async function yesNo(question) {
  const answer = (await rl.question(`${question} [y/N] > `)).trim().toLowerCase();
  return answer === 'y' || answer === 'yes';
}

function run(cmd, args, cwd) {
  console.log(`  $ ${cmd} ${args.join(' ')}`);
  return spawnSync(cmd, args, { cwd, stdio: 'inherit' }).status === 0;
}

const configPath = path.join(repoRoot, 'config', 'course.config.yml');
const config = loadConfig();

console.log('365 Days of AI — central configuration');
console.log('Press Enter to keep the current value, or type "-" to clear it.\n');

config.repository.private_url = normalizeBase(
  await ask('1) PRIVATE repository URL (the complete master repo)', config.repository.private_url),
);
config.repository.public_url = normalizeBase(
  await ask(
    '2) PUBLIC repository URL (labs-only companion, released day by day)',
    config.repository.public_url,
  ),
);
const deployment = normalizeBase(
  await ask(
    '3) Course/blog DEPLOYMENT base URL — the parent under which each day publishes,\n   e.g. https://techhorizon.com/courses/ai-roadmap-365',
    config.website.public_base_url,
  ),
);
config.website.public_base_url = deployment;
config.website.local_base_url = normalizeBase(
  await ask('4) LOCAL development base URL', config.website.local_base_url),
);

// Derive names/owner from the URLs so nothing else needs editing.
const parseRepo = (url) => url?.match(/github\.com\/([^/]+)\/([^/]+)/) ?? null;
const priv = parseRepo(config.repository.private_url);
const pub = parseRepo(config.repository.public_url);
if (priv) {
  config.repository.owner = priv[1];
  config.repository.private_name = priv[2];
}
if (pub) config.repository.public_name = pub[2];

writeFileSync(
  configPath,
  '# Central link and repository configuration — edit via `npm run configure`.\n' +
    '# Every lesson/lab/export link in the repository is generated from this file;\n' +
    '# after changing it, `npm run configure` (or `npm run update:links`) rewrites them all.\n' +
    yaml.dump(config, { lineWidth: 100, noRefs: true }),
);
console.log(`\n✓ wrote ${path.relative(repoRoot, configPath)}`);

// Regenerate everything derived from the config.
console.log('\nRegenerating generated links across the repository…');
updateLinks();
run('node', ['scripts/render-readme-html.mjs'], repoRoot);

const exportedDays = allDays().filter((d) =>
  existsSync(path.join(repoRoot, 'dist', 'wordpress', d.dayId, 'article.html')),
);
for (const d of exportedDays) {
  console.log(`Regenerating WordPress export for day ${d.number}…`);
  run('node', ['scripts/release/wordpress.mjs', '--day', String(d.number)], repoRoot);
  if (existsSync(path.join(repoRoot, 'dist', 'public-release', d.dayId))) {
    run('node', ['scripts/release/export.mjs', '--day', String(d.number)], repoRoot);
  }
}

// Sanity gate before offering to commit.
const linksOk =
  run('node', ['scripts/validate/links.mjs'], repoRoot) &&
  run('node', ['scripts/validate/private-links.mjs'], repoRoot);
if (!linksOk) {
  console.error('\n✗ Link validation failed after regeneration — fix before committing.');
  rl.close();
  process.exit(1);
}

// Offer to update the PRIVATE repository.
if (await yesNo('\nCommit these configuration/link updates to the PRIVATE repository?')) {
  run('git', ['add', '-A'], repoRoot);
  run(
    'git',
    ['commit', '-m', 'chore: update central configuration and regenerate links'],
    repoRoot,
  );
  if (await yesNo('Push the private repository to origin?'))
    run('git', ['push', 'origin', 'HEAD'], repoRoot);
}

// Offer to update a local clone of the PUBLIC repository.
if (config.repository.public_url) {
  const clonePath = normalizeBase(
    await ask(
      '\nLocal clone path of the PUBLIC repository to sync released days into (blank to skip)',
      null,
    ),
  );
  if (clonePath && existsSync(path.join(clonePath, '.git'))) {
    const releaseRoot = path.join(repoRoot, 'dist', 'public-release');
    const packages = existsSync(releaseRoot)
      ? readdirSync(releaseRoot).filter((n) => statSync(path.join(releaseRoot, n)).isDirectory())
      : [];
    if (packages.length === 0) {
      console.log('No release packages found — run `npm run release:export -- --day N` first.');
    } else {
      for (const pkg of packages) {
        const src = path.join(releaseRoot, pkg, 'repository-content');
        if (existsSync(src)) {
          cpSync(src, clonePath, { recursive: true });
          console.log(`  synced ${pkg} → ${clonePath}`);
        }
      }
      run('git', ['add', '-A'], clonePath);
      run(
        'git',
        ['commit', '-m', `chore: sync released days with updated links (${packages.join(', ')})`],
        clonePath,
      );
      if (await yesNo('Push the public repository to origin?'))
        run('git', ['push', 'origin', 'HEAD'], clonePath);
    }
  } else if (clonePath) {
    console.log(
      `  ${clonePath} is not a git clone — skipped. Clone it first: git clone ${config.repository.public_url}.git`,
    );
  }
}

rl.close();
console.log('\nDone. Current link surface:');
const sample = allDays()[0];
const { getLessonUrl, getPublicRepoLabUrl } = await import('./lib/links.mjs');
console.log(`  local lesson : ${getLessonUrl(config, sample, 'local')}`);
console.log(
  `  deployed blog: ${config.website.public_base_url ? getLessonUrl(config, sample, 'public') : '(not deployed yet)'}`,
);
console.log(`  public lab   : ${getPublicRepoLabUrl(config, sample)}`);
