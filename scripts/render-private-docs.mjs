#!/usr/bin/env node
/**
 * Renders the PRIVATE authoring documents to HTML alongside their markdown,
 * so they can be read in a browser without an editor.
 *
 * These documents are the project's memory — the binding requirements, the
 * operating manual, the current state, the quality bar and the architecture.
 * They live ONLY in the private repository (A31, `authoring.private_only`)
 * and are never synced to the public one: they carry authoring instructions,
 * session history and pointers to the instructor answer keys, none of which
 * belong in front of a learner.
 *
 * `scripts/release/public-sync.mjs` refuses to publish anything under
 * `context/` or `docs/`, so both the .md and the .html generated here stay
 * private by construction rather than by remembering.
 *
 * Usage:  npm run docs:html
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import { repoRoot } from './lib/course.mjs';
import { renderMarkdown } from './lib/markdown.mjs';

/** Every private document that earns an HTML rendering, and why it exists. */
const DOCUMENTS = [
  ['context/prompt.md', 'The binding requirements and every amendment, in order'],
  ['context/state.md', 'Where the work actually stands, and what to do next'],
  ['context/skills.md', 'The operating manual: how to produce a day'],
  ['context/quality-bar.md', 'The model-independent definition of "good enough"'],
  ['context/authoring-brief-shared.md', 'The contract every authoring agent reads first'],
  ['context/animated-diagram-reference.md', 'The animated flow-diagram standard'],
  ['context/optimization-playbook.md', 'Token and session-limit discipline'],
  ['context/day-brief-template.md', 'The per-day brief template'],
  ['docs/architecture.md', 'How the whole system fits together'],
];

const css = `
  :root { color-scheme: light dark; }
  body { margin: 0 auto; max-width: 54rem; padding: 2rem 1.2rem 5rem;
         font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
         line-height: 1.65; color: #1a202c; }
  @media (prefers-color-scheme: dark) {
    body { background: #0f1420; color: #e8edf4; }
    a { color: #7ca6ff; }
    pre, code { background: #1b2333 !important; }
    th { background: #171e2e !important; }
    td, th { border-color: #2a3548 !important; }
    .banner { background: #2a1c1c !important; border-color: #7f1d1d !important; color: #fca5a5 !important; }
  }
  .banner { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b;
            padding: 0.75rem 1rem; border-radius: 8px; font-weight: 600; margin-bottom: 1.5rem; }
  .nav { font-size: 0.92rem; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #cbd5e1; }
  .nav a { margin-right: 0.9rem; white-space: nowrap; }
  pre { background: #f1f5f9; padding: 1rem; border-radius: 8px; overflow-x: auto; }
  code { background: #f1f5f9; padding: 0.1em 0.3em; border-radius: 4px; font-size: 0.92em; }
  pre code { background: none; padding: 0; }
  table { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid #cbd5e1; padding: 0.4rem 0.6rem; text-align: left; }
  th { background: #f6f7f9; }
  h1, h2 { line-height: 1.25; }
  h2 { border-bottom: 1px solid #cbd5e1; padding-bottom: 0.25rem; margin-top: 2.2rem; }
  img { max-width: 100%; height: auto; display: block; margin-inline: auto; }
`;

const outDir = path.join(repoRoot, 'docs', 'html');
mkdirSync(outDir, { recursive: true });

const present = DOCUMENTS.filter(([rel]) => existsSync(path.join(repoRoot, rel)));
const navLinks = present
  .map(([rel]) => `<a href="./${path.basename(rel, '.md')}.html">${path.basename(rel, '.md')}</a>`)
  .join('');

let written = 0;
for (const [rel, summary] of present) {
  const md = readFileSync(path.join(repoRoot, rel), 'utf8');
  const body = await renderMarkdown(md);
  const name = path.basename(rel, '.md');
  writeFileSync(
    path.join(outDir, `${name}.html`),
    `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>${name} — private authoring document</title>
<style>${css}</style></head><body>
<p class="banner">PRIVATE — authoring material. This document lives only in the private repository and is never published with the course.</p>
<nav class="nav"><strong>Private docs:</strong> ${navLinks}</nav>
<p><em>${summary}. Generated from <code>${rel}</code> — edit the markdown, then run <code>npm run docs:html</code>.</em></p>
${body}
</body></html>
`,
  );
  written += 1;
}

// One index so the set is navigable.
const rows = present
  .map(
    ([rel, summary]) =>
      `<tr><td><a href="./${path.basename(rel, '.md')}.html">${path.basename(rel, '.md')}</a></td><td>${summary}</td><td><code>${rel}</code></td></tr>`,
  )
  .join('\n');
writeFileSync(
  path.join(outDir, 'index.html'),
  `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Private authoring documents</title>
<style>${css}</style></head><body>
<p class="banner">PRIVATE — authoring material. None of this is published with the course.</p>
<h1>Private authoring documents</h1>
<p>The project's memory: the binding requirements, the operating manual, the current state and the architecture. Each page is generated from its markdown source; edit the markdown and run <code>npm run docs:html</code>.</p>
<table><thead><tr><th>Document</th><th>What it is for</th><th>Source</th></tr></thead>
<tbody>
${rows}
</tbody></table>
</body></html>
`,
);

console.log(`✓ docs:html: ${written} private document(s) + index written to docs/html/`);
