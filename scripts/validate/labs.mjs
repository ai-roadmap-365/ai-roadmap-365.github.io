#!/usr/bin/env node
/**
 * Validates every lab directory: required structure, metadata schema,
 * non-empty expected output, README heading contract, and — for lessons
 * marked complete — evidence of execution.
 */
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import { allDays, loadYamlIfExists, makeReporter } from '../lib/course.mjs';
import {
  LAB_REQUIRED_PATHS,
  LAB_README_HEADINGS,
  LAB_METADATA_FIELDS,
  findForbidden,
} from '../lib/contracts.mjs';

const r = makeReporter('validate:labs');
const days = allDays();

for (const d of days.filter((x) => x.status === 'complete' || x.hasContent)) {
  if (!d.hasLab)
    r.fail(
      `day ${d.number} is ${d.status === 'complete' ? 'complete' : 'authored'} but has no lab`,
    );
}

for (const d of days.filter((x) => x.hasLab)) {
  const tag = `day ${d.number} lab`;
  for (const p of LAB_REQUIRED_PATHS) {
    const full = path.join(d.labDir, p);
    if (!existsSync(full)) {
      r.fail(`${tag}: missing ${p}`);
      continue;
    }
    if (statSync(full).isDirectory() && readdirSync(full).length === 0)
      r.fail(`${tag}: ${p}/ is empty`);
    if (statSync(full).isFile() && readFileSync(full, 'utf8').trim().length < 40)
      r.fail(`${tag}: ${p} is effectively empty`);
  }

  const metadata = loadYamlIfExists(path.join(d.labDir, 'metadata.yml'));
  if (!metadata) {
    r.fail(`${tag}: metadata.yml missing or unparseable`);
    continue;
  }
  for (const f of LAB_METADATA_FIELDS) {
    if (metadata[f] === undefined) r.fail(`${tag}: metadata.yml missing field "${f}"`);
  }
  if (metadata.day !== d.number) r.fail(`${tag}: metadata day mismatch`);
  if (metadata.lesson_id !== d.id)
    r.fail(`${tag}: metadata lesson_id mismatch (${metadata.lesson_id} != ${d.id})`);

  const readmePath = path.join(d.labDir, 'README.md');
  if (existsSync(readmePath)) {
    const readme = readFileSync(readmePath, 'utf8');
    for (const h of LAB_README_HEADINGS) {
      if (!readme.includes(`\n${h}`)) r.fail(`${tag}: README missing heading "${h}"`);
    }
    for (const hit of findForbidden(readme))
      r.fail(`${tag}: README contains forbidden marker "${hit}"`);
    if (!/Day number:\*?\*? ?\d+/.test(readme) && !readme.includes(`Day ${d.number}`))
      r.fail(`${tag}: README does not state the day number`);
  }

  // Completion requires recorded execution evidence.
  if (d.status === 'complete') {
    if (!metadata.last_executed)
      r.fail(`${tag}: lesson marked complete but metadata has no last_executed date`);
    if (!metadata.executed_on)
      r.fail(`${tag}: lesson marked complete but metadata has no executed_on record`);
    const expected = path.join(d.labDir, 'expected-output');
    const files = existsSync(expected) ? readdirSync(expected) : [];
    if (files.length === 0) r.fail(`${tag}: complete lesson has no captured expected output`);
  }
}

const labCount = days.filter((x) => x.hasLab).length;
r.finish(`${labCount} lab(s) pass structure, metadata, README, and execution-evidence checks.`);
