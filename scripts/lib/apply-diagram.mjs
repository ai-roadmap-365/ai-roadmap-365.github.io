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
  const svg = gen[spec.kind](spec);
  const file = `assets/${spec.id}.svg`;
  writeFileSync(path.join(dir, file), svg);

  const vpath = path.join(dir, 'visuals.yml');
  const v = readFileSync(vpath, 'utf8').replace(/\s*$/, '');
  if (!v.includes(`id: ${spec.id}`)) {
    writeFileSync(
      vpath,
      `${v}
  - id: ${spec.id}
    file: ${file}
    type: diagram
    title: '${spec.title.replace(/'/g, "''")}'
    alt: '${spec.alt.replace(/'/g, "''")}'
    description: '${spec.description.replace(/'/g, "''")}'
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
