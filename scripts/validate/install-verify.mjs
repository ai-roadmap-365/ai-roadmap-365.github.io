#!/usr/bin/env node
/**
 * Environment verification: Node version, installed dependencies, parseable
 * configuration — the first thing to run on a fresh clone.
 */
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import yaml from 'js-yaml';
import { repoRoot, makeReporter } from '../lib/course.mjs';

const r = makeReporter('install:verify');
const require = createRequire(import.meta.url);

const major = Number(process.versions.node.split('.')[0]);
if (major < 20) r.fail(`Node ${process.versions.node} too old — install Node 20 or newer`);

if (!existsSync(path.join(repoRoot, 'node_modules')))
  r.fail('node_modules missing — run npm install');

for (const dep of ['astro', '@astrojs/mdx', 'js-yaml', 'unified', 'cheerio', 'vitest']) {
  try {
    require.resolve(dep, { paths: [repoRoot] });
  } catch {
    r.fail(`dependency not installed: ${dep} — run npm install`);
  }
}

for (const file of [
  'config/course.config.yml',
  'curriculum/curriculum.yml',
  'curriculum/progress.yml',
]) {
  try {
    yaml.load(readFileSync(path.join(repoRoot, file), 'utf8'));
  } catch (err) {
    r.fail(`${file} unreadable or invalid YAML: ${err.message}`);
  }
}

r.finish(`Node ${process.versions.node}, dependencies installed, configuration parses.`);
