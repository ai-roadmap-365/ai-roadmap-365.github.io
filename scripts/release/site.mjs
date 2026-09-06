#!/usr/bin/env node
/**
 * Build and verify the publishable course site into `dist/`.
 *
 * This script does NOT deploy. GitHub Pages is fed by
 * `.github/workflows/pages.yml`, which runs this and then hands `dist/` to
 * actions/deploy-pages (A49). One branch, `main`, is both the source and the
 * thing that triggers a publish.
 *
 * It used to force-push the built HTML to a dedicated `site` branch. That
 * branch existed only because Pages could not otherwise be pointed at a
 * subdirectory of a build, and it cost a second branch, a force-push over
 * generated history on every release, and an SSH remote that only the owner's
 * machine had. Deploying the artifact directly removes all three.
 *
 * What remains here is everything that has to be true before anything is
 * served: the build succeeds, the authoring-only routes are stripped, Jekyll
 * is disabled so Astro's /_astro assets resolve, and no page references
 * localhost or links into a route that was stripped.
 *
 * Usage:
 *   node scripts/release/site.mjs     # build, strip, verify; leaves dist/
 */

import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, rmSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';

const repoRoot = process.cwd();

const config = yaml.load(readFileSync(path.join(repoRoot, 'config', 'course.config.yml'), 'utf8'));
const dist = path.join(repoRoot, 'dist');

/** Routes that exist for local authoring and must never reach the public site. */
const INTERNAL_ROUTES = ['admin', 'wordpress-preview'];

function run(cmd, args, opts = {}) {
  return execFileSync(cmd, args, {
    stdio: 'pipe',
    encoding: 'utf8',
    maxBuffer: 100 * 1024 * 1024,
    ...opts,
  });
}

function fail(message) {
  console.error(`✗ build:site: ${message}`);
  process.exit(1);
}

// -------------------------------------------------------------- preconditions

if (!config.website.public_base_url) fail('website.public_base_url is null; nothing to publish to');
if (!config.repository.public_url) fail('repository.public_url is null');

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

console.log(
  `\u2713 build:site: ${pages} pages built and verified in dist/. ` +
    'Deployment is .github/workflows/pages.yml, not this script.',
);
