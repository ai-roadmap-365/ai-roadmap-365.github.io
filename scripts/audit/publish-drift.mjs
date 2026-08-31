#!/usr/bin/env node
/**
 * Has anything been authored here that the public projections have not received?
 *
 * The private repository is the source; the two public repositories and the live
 * site are generated from it. Nothing enforces that they are current, so an
 * audit can land good work in `main` and leave every learner reading the old
 * lesson -- which is exactly what happened after the RAG-week rewrite.
 *
 * Compares git blob SHAs rather than file contents. A blob SHA is computed from
 * the bytes, so equal SHAs mean identical files, and the GitHub contents API
 * returns one per file for a whole directory in a single request. The first
 * version of this script fetched raw.githubusercontent per file and reported
 * "not published" for files that were in fact published, because that host
 * answers 400 for some perfectly valid paths. A check that cries wolf gets
 * ignored, so it now compares identifiers instead of downloading content.
 *
 * Read-only, needs a network, and deliberately not part of verify:all.
 */
import { execSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import yaml from 'js-yaml';

const cfg = yaml.load(readFileSync('config/course.config.yml', 'utf8'));
const repo = cfg?.repository?.public_canonical ?? 'ai-roadmap-365/ai-roadmap-365';
const API = `https://api.github.com/repos/${repo}/contents`;

const args = process.argv.slice(2);
const limit = Number(args[args.indexOf('--sample') + 1]) || 12;

const dirs = execSync("git ls-files 'content/sections/*/day-*/index.mdx'", { encoding: 'utf8' })
  .trim()
  .split('\n')
  .map((f) => f.replace(/\/index\.mdx$/, ''));
const step = Math.max(1, Math.floor(dirs.length / limit));
const sample = dirs.filter((_, i) => i % step === 0).slice(0, limit);

// Unauthenticated the API allows 60 requests an hour, which this exhausts in two
// runs. `gh` is already authenticated on any machine that can publish, so borrow
// its token rather than asking for another one to be configured.
let token = process.env.GITHUB_TOKEN ?? process.env.GH_TOKEN;
if (!token) {
  try {
    token = execSync('gh auth token', {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    }).trim();
  } catch {
    token = undefined;
  }
}
const headers = {
  Accept: 'application/vnd.github+json',
  ...(token ? { Authorization: `Bearer ${token}` } : {}),
};

console.log(`Comparing ${sample.length} lesson directories against ${repo}…`);
const drifted = [];
let compared = 0;

for (const dir of sample) {
  let remote;
  try {
    const res = await fetch(`${API}/${dir}?ref=main`, { headers });
    if (res.status === 404) {
      drifted.push({ dir, why: 'directory not published' });
      continue;
    }
    if (!res.ok) {
      console.error(
        `  cannot read ${dir}: HTTP ${res.status}` +
          (res.status === 403 ? ' (rate limited — set GITHUB_TOKEN for a higher limit)' : ''),
      );
      process.exit(2);
    }
    remote = new Map(
      (await res.json()).filter((e) => e.type === 'file').map((e) => [e.name, e.sha]),
    );
  } catch (err) {
    console.error(`  network error on ${dir}: ${err.message}`);
    process.exit(2);
  }

  const local = execSync(`git ls-files -s -- ${dir}`, { encoding: 'utf8' })
    .trim()
    .split('\n')
    .map((l) => l.split(/\s+/))
    .filter(([, , , p]) => p && !p.slice(dir.length + 1).includes('/'))
    .map(([, sha, , p]) => [p.slice(dir.length + 1), sha]);

  for (const [name, sha] of local) {
    // release:public rewrites READMEs on the way out -- it strips the instructor
    // pointers from 362 of them -- so the published bytes legitimately differ
    // and comparing them would report drift that is not drift.
    if (name === 'README.md') continue;
    compared += 1;
    const there = remote.get(name);
    if (!there) drifted.push({ dir, why: `${name} not published` });
    else if (there !== sha) drifted.push({ dir, why: `${name} out of date` });
  }
}

if (!drifted.length) {
  console.log(`No drift: ${compared} files match the published copy exactly.`);
  process.exit(0);
}
console.error(`\n${drifted.length} difference(s) across ${sample.length} sampled directories:`);
for (const d of drifted.slice(0, 20)) console.error(`  ${d.why.padEnd(24)} ${d.dir}`);
if (drifted.length > 20) console.error(`  … and ${drifted.length - 20} more`);
console.error('\nRun: npm run release:public && npm run release:site');
process.exit(1);
