#!/usr/bin/env node
/**
 * Publish the rendered course site to the `site` branch.
 *
 * Model (A31): one repository. `main` carries the whole course - lessons,
 * labs, instructor material, site source and pipelines. The rendered site is
 * published to a dedicated `site` branch as generated output, never source,
 * and GitHub Pages serves that branch.
 *
 * The branch is force-pushed on every release because it holds only generated
 * output; its history carries no information `main` does not already
 * have.
 *
 * Usage:
 *   node scripts/release/site.mjs            # build, verify, push
 *   node scripts/release/site.mjs --dry-run  # build and verify only
 */

import { execFileSync } from 'node:child_process';
import {
  cpSync,
  existsSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
  readdirSync,
  statSync,
} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import yaml from 'js-yaml';

const repoRoot = process.cwd();
const dryRun = process.argv.includes('--dry-run');

const config = yaml.load(readFileSync(path.join(repoRoot, 'config', 'course.config.yml'), 'utf8'));
const dist = path.join(repoRoot, 'dist');

/** Routes that exist for local authoring and must never reach the public site. */
const INTERNAL_ROUTES = ['admin', 'wordpress-preview'];

function run(cmd, args, opts = {}) {
  return execFileSync(cmd, args, { stdio: 'pipe', encoding: 'utf8', maxBuffer: 100 * 1024 * 1024, ...opts });
}

function fail(message) {
  console.error(`✗ release:site: ${message}`);
  process.exit(1);
}

// -------------------------------------------------------------- preconditions

if (!config.website.public_base_url) fail('website.public_base_url is null; nothing to publish to');
if (!config.repository.public_url) fail('repository.public_url is null');

const siteBranch = config.repository.site_branch;
if (!siteBranch) fail('repository.site_branch is not set in course.config.yml');

// ------------------------------------------------------------------- build

console.log('· building');
run('npm', ['run', 'build'], { stdio: 'inherit' });
if (!existsSync(dist)) fail('dist/ was not produced');

// --------------------------------------------------------- strip internals

for (const route of INTERNAL_ROUTES) {
  const target = path.join(dist, route);
  if (existsSync(target)) {
    rmSync(target, { recursive: true, force: true });
    console.log(`· stripped internal route /${route}`);
  }
}

// Astro emits /_astro/**; GitHub Pages runs Jekyll on branch deploys and Jekyll
// skips any path beginning with an underscore. Without this file every stylesheet
// and script 404s.
writeFileSync(path.join(dist, '.nojekyll'), '');

// ------------------------------------------------------------------ verify

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = path.join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else out.push(full);
  }
  return out;
}

const textFiles = walk(dist).filter((f) => /\.(html|json|xml|txt|css|js)$/.test(f));

// There is one repository now (A31), so there is no private URL to leak. What
// must still never reach the published site is a localhost reference or a link
// into a route stripped from the build.
const localhostRe = /localhost:\d+/;

const leaks = [];
for (const file of textFiles) {
  const body = readFileSync(file, 'utf8');
  const rel = path.relative(dist, file);
  if (localhostRe.test(body)) leaks.push(`${rel}: references localhost`);
  for (const route of INTERNAL_ROUTES) {
    if (body.includes(`"${config.website.base_path}/${route}`)) {
      leaks.push(`${rel}: links to stripped internal route /${route}`);
    }
  }
}
if (leaks.length) {
  fail(`public output is not clean:\n  ${[...new Set(leaks)].slice(0, 20).join('\n  ')}`);
}

const pages = textFiles.filter((f) => f.endsWith('.html')).length;
console.log(`· verified ${pages} pages: no localhost, no internal routes`);

if (dryRun) {
  console.log('✓ release:site: dry run complete, nothing pushed');
  process.exit(0);
}

// -------------------------------------------------------------------- push

const remote = `git@github.com:${config.repository.owner}/${config.repository.public_name}.git`;
const staging = mkdtempSync(path.join(os.tmpdir(), 'site-publish-'));

try {
  cpSync(dist, staging, { recursive: true });

  run('git', ['init', '-q', '-b', siteBranch], { cwd: staging });
  // A fresh temp repo inherits the GLOBAL git identity, which is not
  // necessarily this project's. Set it explicitly (A24, A38).
  run('git', ['config', 'user.name', config.committer.name], { cwd: staging });
  run('git', ['config', 'user.email', config.committer.email], { cwd: staging });
  run('git', ['add', '-A'], { cwd: staging });

  const stamp = run('git', ['log', '-1', '--format=%h %s'], { cwd: repoRoot }).trim();
  run('git', ['commit', '-q', '-m', `Publish course site\n\nBuilt from main ${stamp}`], {
    cwd: staging,
  });

  console.log(`· force-pushing ${pages} pages to ${config.repository.public_name}:${siteBranch}`);
  run('git', ['push', '-q', '--force', remote, `${siteBranch}:${siteBranch}`], { cwd: staging });

  console.log(`✓ release:site: published to ${config.website.public_base_url}`);
} finally {
  rmSync(staging, { recursive: true, force: true });
}
