#!/usr/bin/env node
/**
 * License audit: catalog entries all declare a license; lab requirement
 * files exist for labs that install dependencies; repository license
 * posture is explicit (a LICENSE file plus a package.json license field).
 */
import { readFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';
import { allDays, loadYamlIfExists, repoRoot, makeReporter } from '../lib/course.mjs';

const r = makeReporter('audit:licenses');

const pkg = JSON.parse(readFileSync(path.join(repoRoot, 'package.json'), 'utf8'));
if (!pkg.license) r.fail('package.json has no license field');
if (!existsSync(path.join(repoRoot, 'LICENSE')))
  r.fail(
    'no LICENSE file at the repository root — a public course repository must say how it may be used',
  );
// The package is deliberately NOT marked private: this is a public course
// repository, and `private: true` would be a leftover from the two-repo model.
// What must hold instead is that it names where it lives and what it is.
if (pkg.private) r.fail('package.json is marked private, but this repository is public (A31)');
if (!pkg.repository?.url?.includes('ai-roadmap-365'))
  r.fail('package.json repository.url does not point at the course repository');
if (!pkg.homepage) r.fail('package.json has no homepage (the published course site)');

for (const name of ['tools', 'frameworks', 'models', 'free-open-source', 'projects']) {
  const file = path.join(repoRoot, 'catalog', `${name}.yml`);
  if (!existsSync(file)) {
    r.fail(`catalog/${name}.yml missing`);
    continue;
  }
  const doc = yaml.load(readFileSync(file, 'utf8'));
  for (const e of doc.entries ?? []) {
    if (!e.license) r.fail(`catalog/${name}.yml: "${e.name}" has no license field`);
    if (!e.last_verified) r.fail(`catalog/${name}.yml: "${e.name}" has no last_verified date`);
    if (/\$\d/.test(`${e.pricing}`))
      r.fail(
        `catalog/${name}.yml: "${e.name}" pricing contains a dollar amount — keep pricing qualitative`,
      );
  }
}

// Labs that declare dependencies must document them under requirements/.
for (const d of allDays().filter((x) => x.hasLab)) {
  const metadata = loadYamlIfExists(path.join(d.labDir, 'metadata.yml'));
  if (!metadata) continue;
  if (!existsSync(path.join(d.labDir, 'requirements')))
    r.fail(`day ${d.number} lab: no requirements/ directory`);
}

r.finish(
  'license posture explicit; catalogs fully licensed and dated; labs document requirements.',
);
