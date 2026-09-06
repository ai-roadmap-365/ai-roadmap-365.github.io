#!/usr/bin/env node
// SPDX-FileCopyrightText: 2026 Sandeep Bazar
// SPDX-License-Identifier: Apache-2.0
//
// Give a static lesson diagram the same sense of direction the animated ones have.
//
// The rule this obeys is A44's: motion may draw attention to an order that is ALREADY VISIBLE,
// and nothing more. So this script NEVER edits an existing element. It reads the diagram, works
// out which lines are flow connectors, and adds a layer of travelling pulses ON TOP of arrows
// that are already drawn. Delete the layer and the diagram is byte-for-byte what it was.
//
// A line counts as a connector only if an arrowhead sits at one of its ends: a polygon whose
// points cluster within ARROW_NEAR of the endpoint. Rules, dividers and box outlines have no
// arrowhead, so they stay still — which is the point. A pulse on a divider would be motion that
// means nothing, and this file exists to add meaning, not movement.
//
// Pulses are staggered in reading order (left to right, then top to bottom) so a four-step
// diagram animates as four steps rather than four simultaneous twitches.
//
// Idempotent: a file already carrying MARK is left alone, so re-running is safe.
//
// Usage:
//   node scripts/animate-diagrams.mjs --section computing-foundations
//   node scripts/animate-diagrams.mjs --section computing-foundations --dry-run
//   node scripts/animate-diagrams.mjs --file path/to/one.svg
import { readFileSync, writeFileSync } from 'node:fs';
import { globSync } from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const argv = process.argv.slice(2);
const arg = (name) => {
  const i = argv.indexOf(`--${name}`);
  return i === -1 ? null : argv[i + 1];
};
const dryRun = argv.includes('--dry-run');

const MARK = 'dx-flow'; // presence of this class means the file is already done
const ARROW_NEAR = 20; // px from a line end within which a polygon counts as its arrowhead
const MIN_LEN = 26; // ignore hairlines; a pulse on a 10px stub is noise

const num = (v) => (v === undefined || v === null ? NaN : Number.parseFloat(v));

/** Attributes of one tag, as a plain object. */
function attrs(tag) {
  const out = {};
  // The name class must allow digits: x1, y2 and stroke-width are all attributes
  // this needs, and [a-zA-Z-]+ silently matches "x" and drops the "1".
  for (const m of tag.matchAll(/([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*"([^"]*)"/g)) out[m[1]] = m[2];
  return out;
}

/** Centroid of a `points` list, used to place an arrowhead. */
function centroid(points) {
  const nums = (points.match(/-?\d+(?:\.\d+)?/g) ?? []).map(Number);
  let sx = 0,
    sy = 0,
    n = 0;
  for (let i = 0; i + 1 < nums.length; i += 2) {
    sx += nums[i];
    sy += nums[i + 1];
    n += 1;
  }
  return n ? { x: sx / n, y: sy / n } : null;
}

const dist = (ax, ay, bx, by) => Math.hypot(ax - bx, ay - by);

/**
 * Every coordinate pair in a path's `d`, used only to locate its two ends.
 * Returns null when the path uses H/V or relative commands, where a pair-wise
 * read would be wrong — those fall back to marker evidence, which needs no
 * geometry at all.
 */
function pathEnds(d) {
  if (
    /[hvHV]/.test(d) ||
    /[a-z]/.test(d.replace(/[a-zA-Z]/g, (c) => (c === c.toUpperCase() ? c : 'r')))
  )
    return null;
  const nums = (d.match(/-?\d+(?:\.\d+)?/g) ?? []).map(Number);
  if (nums.length < 4) return null;
  return {
    sx: nums[0],
    sy: nums[1],
    ex: nums[nums.length - 2],
    ey: nums[nums.length - 1],
  };
}

/**
 * Flow connectors in the file, each with the direction its arrow points.
 * Direction matters: a pulse travelling backwards up an arrow teaches the
 * reader the opposite of what the diagram says.
 *
 * Two ways a diagram in this course says "arrow", and both are honoured:
 * a `<polygon>` head drawn at the end of a `<line>`, and a `marker-end` on a
 * `<line>` or `<path>`. Markers need no geometry — the marker IS the evidence
 * and the path's own drawn direction is the flow — which is what lets curved
 * and multi-segment connectors work without parsing their shape.
 *
 * `reverse` is returned rather than flipped coordinates: the overlay reuses
 * the original geometry verbatim and simply runs its dash the other way, so a
 * curve never has to be reversed by hand.
 */
/**
 * Class name -> its declarations, read from the file's own <style> blocks.
 *
 * The later diagrams in this course style their connectors through a class
 * rather than attributes — `<path class="d290f-flow"/>` with
 * `.d290f-flow { stroke: #64748b; fill: none; }` in <style>. An attribute-only
 * reader sees a path with no stroke and skips it, which is why 68 files that
 * plainly draw flows looked like they had none.
 */
function classStyles(svg) {
  const map = new Map();
  for (const block of svg.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)) {
    const css = block[1].replace(/\/\*[\s\S]*?\*\//g, '');
    for (const rule of css.matchAll(/\.([A-Za-z0-9_-]+)\s*\{([^}]*)\}/g)) {
      map.set(rule[1], (map.get(rule[1]) ?? '') + ';' + rule[2]);
    }
  }
  return map;
}

/** A class the author named as a connector: flow, arrow, edge, link, conn. */
const CONNECTOR_NAME = /(flow|arrow|edge|link|conn)/i;

function connectors(svg) {
  const styles = classStyles(svg);
  const decl = (names, prop) => {
    for (const n of names) {
      const css = styles.get(n);
      if (!css) continue;
      const m = css.match(new RegExp(`(?:^|[;{\\s])${prop}\\s*:\\s*([^;}]+)`, 'i'));
      if (m) return m[1].trim();
    }
    return null;
  };
  /**
   * Resolve a connector from its classes alone. Requires the author to have
   * NAMED it a connector and to have given it a stroke with no fill — a
   * "flow-label" text class must not become a moving line.
   */
  const fromClass = (a) => {
    const names = (a.class ?? '').trim().split(/\s+/).filter(Boolean);
    if (!names.some((n) => CONNECTOR_NAME.test(n))) return null;
    const stroke = a.stroke ?? decl(names, 'stroke');
    if (!stroke || stroke === 'none') return null;
    const fill = a.fill ?? decl(names, 'fill');
    if (fill && fill !== 'none') return null;
    return {
      stroke,
      width: Number.parseFloat(a['stroke-width'] ?? decl(names, 'stroke-width')) || 2,
    };
  };

  const heads = [];
  for (const m of svg.matchAll(/<polygon\b[^>]*>/g)) {
    const c = centroid(attrs(m[0]).points ?? '');
    if (c) heads.push(c);
  }
  const near = (x, y) => heads.some((h) => dist(h.x, h.y, x, y) <= ARROW_NEAR);
  const found = [];

  for (const m of svg.matchAll(/<line\b[^>]*>/g)) {
    const a = attrs(m[0]);
    const x1 = num(a.x1),
      y1 = num(a.y1),
      x2 = num(a.x2),
      y2 = num(a.y2);
    if ([x1, y1, x2, y2].some(Number.isNaN)) continue;
    if (dist(x1, y1, x2, y2) < MIN_LEN) continue;
    const cls = fromClass(a);
    const stroke = a.stroke && a.stroke !== 'none' ? a.stroke : cls?.stroke;
    if (!stroke) continue;

    const atEnd = Boolean(a['marker-end']) || near(x2, y2);
    const atStart = Boolean(a['marker-start']) || near(x1, y1);
    if (!atEnd && !atStart && !cls) continue;
    found.push({
      d: `M ${x1} ${y1} L ${x2} ${y2}`,
      reverse: atStart && !atEnd,
      sortX: x1,
      sortY: y1,
      stroke,
      width: num(a['stroke-width']) || cls?.width || 2,
    });
  }

  for (const m of svg.matchAll(/<path\b[^>]*>/g)) {
    const a = attrs(m[0]);
    if (!a.d) continue;
    // A filled path is a shape, not a connector; overlaying it would trace an
    // outline around something the diagram never drew as a line.
    if (a.fill && a.fill !== 'none') continue;
    if (/[zZ]/.test(a.d)) continue; // closed: a shape

    const cls = fromClass(a);
    const stroke = a.stroke && a.stroke !== 'none' ? a.stroke : cls?.stroke;
    if (!stroke) continue;

    const ends = pathEnds(a.d);
    const atEnd = Boolean(a['marker-end']) || (ends ? near(ends.ex, ends.ey) : false);
    const atStart = Boolean(a['marker-start']) || (ends ? near(ends.sx, ends.sy) : false);
    if (!atEnd && !atStart && !cls) continue;
    if (ends && dist(ends.sx, ends.sy, ends.ex, ends.ey) < MIN_LEN) continue;

    found.push({
      d: a.d,
      reverse: atStart && !atEnd,
      sortX: ends ? ends.sx : 0,
      sortY: ends ? ends.sy : 0,
      stroke,
      width: num(a['stroke-width']) || cls?.width || 2,
    });
  }
  return found;
}

function animate(svg) {
  if (svg.includes(MARK)) return { svg, added: 0, skipped: 'already animated' };
  if (svg.includes('@keyframes')) return { svg, added: 0, skipped: 'already has motion' };
  const close = svg.lastIndexOf('</svg>');
  if (close === -1) return { svg, added: 0, skipped: 'no closing tag' };

  const lines = connectors(svg);
  if (lines.length === 0) return { svg, added: 0, skipped: 'no flow connectors' };

  // Reading order: down the page in bands, left to right within a band. Sorting
  // by raw y alone scrambles a row of boxes whose arrows differ by a pixel.
  lines.sort((a, b) => Math.round(a.sortY / 40) - Math.round(b.sortY / 40) || a.sortX - b.sortX);

  const CYCLE = 3.6;
  const step = lines.length > 1 ? Math.min(0.42, CYCLE / (lines.length + 2)) : 0;

  // pathLength="100" normalises every connector, so a 40px arrow and a 400px
  // one carry a pulse of the same visual proportion at the same speed. Without
  // it the dash lengths would have to be recomputed per line and long arrows
  // would appear to move faster than short ones.
  const paths = lines
    .map(
      (l, i) =>
        `    <path class="dx-flow${l.reverse ? ' dx-rev' : ''} dx-f${i}" d="${l.d}" ` +
        `stroke="${l.stroke}" stroke-width="${(l.width + 1.6).toFixed(1)}" fill="none" ` +
        `stroke-linecap="round" pathLength="100" stroke-dasharray="18 100" ` +
        `stroke-dashoffset="18"/>`,
    )
    .join('\n');

  const delays = lines
    .map((_, i) => `.dx-f${i}{animation-delay:${(i * step).toFixed(2)}s}`)
    .join('');

  const layer = `
  <style>
    /* Travelling highlights on arrows that are already drawn. Added by
       scripts/animate-diagrams.mjs; no original element was modified, so
       removing this block restores the diagram exactly.

       reduce-ok: .dx-flow is a highlight sliding along an arrow the reader can
       already see, complete with its head and its direction. With the motion
       off there is no second arrow to miss — only the moving glint is gone. */
    @keyframes dxflow{from{stroke-dashoffset:18}to{stroke-dashoffset:-100}}
    @keyframes dxflowr{from{stroke-dashoffset:-100}to{stroke-dashoffset:18}}
    .dx-flow{animation:dxflow ${CYCLE}s cubic-bezier(.5,0,.5,1) infinite;opacity:.9}
    /* An arrow whose head is at the START of the drawn path flows the other
       way. Running the dash backwards is exact and geometry-free; reversing a
       curve's control points by hand is neither. */
    .dx-rev{animation-name:dxflowr}
    ${delays}
    @media (prefers-reduced-motion:reduce){
      .dx-flow{animation:none;opacity:0}
      .dx-rev{animation:none}
    }
  </style>
  <g aria-hidden="true">
${paths}
  </g>
`;
  return { svg: svg.slice(0, close) + layer + svg.slice(close), added: lines.length };
}

// ------------------------------------------------------------------ run

const one = arg('file');
const section = arg('section');
const files = one
  ? [one]
  : globSync(`content/sections/${section ?? '*'}/**/assets/*.svg`, { cwd: ROOT })
      .map((f) => path.join(ROOT, f))
      .sort();

let changed = 0,
  pulses = 0;
const skips = new Map();
for (const f of files) {
  const before = readFileSync(f, 'utf8');
  const { svg, added, skipped } = animate(before);
  if (skipped) {
    skips.set(skipped, (skips.get(skipped) ?? 0) + 1);
    continue;
  }
  changed += 1;
  pulses += added;
  if (!dryRun) writeFileSync(f, svg);
}
console.log(
  `${dryRun ? '[dry run] ' : ''}animated ${changed} diagram(s) with ${pulses} flow pulse(s)` +
    ` across ${files.length} file(s)`,
);
for (const [why, n] of [...skips].sort((a, b) => b[1] - a[1]))
  console.log(`  skipped ${n}: ${why}`);
