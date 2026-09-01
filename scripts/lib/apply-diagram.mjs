#!/usr/bin/env node
/**
 * Wire generated diagrams into lessons: write the SVG, register it in
 * visuals.yml, and place the image reference in index.mdx -- replacing a named
 * paragraph where one is given, so a diagram takes prose's place rather than
 * being added on top of it.
 */
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import * as gen from './make-diagram.mjs';

const specs = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const SECTIONS = 'content/sections';

const dayDir = (day) => {
  for (const s of readdirSync(SECTIONS)) {
    const sp = path.join(SECTIONS, s);
    const hit = readdirSync(sp).find((d) => d.startsWith(`day-${String(day).padStart(3, '0')}-`));
    if (hit) return path.join(sp, hit);
  }
  throw new Error(`no directory for day ${day}`);
};

for (const spec of specs) {
  const dir = dayDir(spec.day);
  const file = `assets/${spec.id}.svg`;

  const vpath = path.join(dir, 'visuals.yml');
  const v = readFileSync(vpath, 'utf8').replace(/\s*$/, '');
  // Whole-id match. A substring test skips the append when an existing id
  // merely starts with this one — `rag-triad` inside `rag-triad-evaluation-
  // topology` — leaving the SVG written and embedded but undeclared.
  const declared = new RegExp(
    `^[ \\t]*-?[ \\t]*id:[ \\t]*${spec.id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[ \\t]*$`,
    'm',
  ).test(v);
  // A colliding id is a real hazard, and the check has to come before the SVG
  // is written: reusing an id silently overwrote a hand-authored diagram and
  // embedded a second copy of it under a different alt, which only
  // validate:lessons noticed. Refuse before anything on disk changes.
  if (declared && !v.includes(`alt: '${spec.alt.replace(/'/g, "''")}'`)) {
    throw new Error(
      `day ${spec.day}: id "${spec.id}" is already declared with a different alt - choose another id`,
    );
  }

  writeFileSync(path.join(dir, file), gen[spec.kind](spec));

  if (!declared) {
    // Match the file's existing sequence indentation. Sections differ: most
    // indent items two spaces under `visuals:`, and capstone puts them at
    // column zero. Both are valid YAML; mixing them in one file is not, and
    // the parse error names a line far from the append.
    const first = v.match(/^([ \t]*)- id:/m);
    const dash = first ? first[1] : '  ';
    const key = `${dash}  `;
    writeFileSync(
      vpath,
      `${v}
${dash}- id: ${spec.id}
${key}file: ${file}
${key}type: diagram
${key}title: '${spec.title.replace(/'/g, "''")}'
${key}alt: '${spec.alt.replace(/'/g, "''")}'
${key}description: '${spec.description.replace(/'/g, "''")}'
`,
    );
  }

  const mpath = path.join(dir, 'index.mdx');
  let mdx = readFileSync(mpath, 'utf8');
  const img = `![${spec.alt}](./${file})`;
  if (mdx.includes(img)) {
    console.log(`day ${spec.day}: ${spec.id} already placed`);
    continue;
  }

  if (spec.replace) {
    const paras = mdx.split('\n\n');
    const i = paras.findIndex((p) => p.trim().startsWith(spec.replace));
    if (i === -1) throw new Error(`day ${spec.day}: no paragraph starting "${spec.replace}"`);
    const before = paras[i].split(/\s+/).length;
    paras[i] = spec.lead ? `${spec.lead.trim()}\n\n${img}` : img;
    mdx = paras.join('\n\n');
    console.log(`day ${spec.day}: ${spec.id} replaced a ${before}-word paragraph`);
  } else {
    const anchor = `## ${spec.after}`;
    const at = mdx.indexOf(anchor);
    if (at === -1) throw new Error(`day ${spec.day}: no section "${spec.after}"`);
    const nl = mdx.indexOf('\n\n', at + anchor.length);
    mdx = `${mdx.slice(0, nl + 2)}${img}\n\n${mdx.slice(nl + 2)}`;
    console.log(`day ${spec.day}: ${spec.id} added under "${spec.after}"`);
  }
  writeFileSync(mpath, mdx);
}
