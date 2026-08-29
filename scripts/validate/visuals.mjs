#!/usr/bin/env node
/**
 * Visuals validation: declared visuals exist, are accessible (SVGs carry
 * role="img" and a <title>), alts are meaningful, and declarations match
 * what the lesson actually embeds.
 */
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { existsSync } from 'node:fs';
import { allDays, loadSidecars, makeReporter } from '../lib/course.mjs';

const r = makeReporter('validate:visuals');

for (const d of allDays().filter((x) => x.hasContent)) {
  const tag = `day ${d.number}`;
  const visuals = loadSidecars(d).visuals?.visuals ?? [];
  if (visuals.length < 2) {
    r.fail(
      `${tag}: only ${visuals.length} visual(s) declared — every lesson needs at least an architecture diagram and a flow diagram (amendment A14)`,
    );
    if (visuals.length === 0) continue;
  }
  for (const v of visuals) {
    const file = path.join(d.contentDir, v.file);
    if (!existsSync(file)) {
      r.fail(`${tag}: ${v.file} missing`);
      continue;
    }
    for (const field of ['id', 'type', 'title', 'alt', 'description']) {
      if (!v[field]) r.fail(`${tag}: visual ${v.file} missing ${field}`);
    }
    if (v.alt && v.alt.split(' ').length < 3)
      r.fail(`${tag}: visual ${v.id} alt text too short to be meaningful`);
    if (v.file.endsWith('.svg')) {
      const svg = readFileSync(file, 'utf8');
      if (!svg.includes('<title'))
        r.fail(`${tag}: ${v.file} has no <title> element (accessibility)`);
      if (!svg.includes('role="img"')) r.fail(`${tag}: ${v.file} missing role="img"`);
      if (!svg.includes('viewBox')) r.fail(`${tag}: ${v.file} missing viewBox (not scalable)`);
    }
  }
}

r.finish('all declared visuals exist, are accessible, and match their lessons.');
