// SPDX-FileCopyrightText: 2026 Sandeep Bazar
// SPDX-License-Identifier: Apache-2.0
//
// Animated hero art and star button, one dark file and one light.
//
// The progress figure is read from CURRICULUM.md rather than written here, because a hero that
// hard-codes a day count keeps advertising a number the course passed months ago.
//
// A README renders these through GitHub's image proxy, which is a closed context: no font loads,
// no script runs, no <foreignObject> lays anything out. So the motion is CSS keyframes inside the
// file, the type is generic families only, and every coordinate is computed here.
//
// Usage:  node scripts/build-hero.mjs
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const THEMES = {
  dark: { bg: '#0b1020', panel: '#121a30', edge: '#243154', ink: '#e8ecf8', dim: '#93a4c8' },
  light: { bg: '#fbfcff', panel: '#ffffff', edge: '#dfe6f5', ink: '#0f1729', dim: '#5a6b8c' },
};
const BLUE = '#1d4ed8',
  SKY = '#38bdf8',
  GREEN = '#22c55e',
  AMBER = '#f59e0b';
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function progress() {
  const md = readFileSync(join(ROOT, 'CURRICULUM.md'), 'utf8');
  const total = md.match(/\*\*(\d+) of (\d+) days complete\.\*\*/);
  const courses = [
    ...md.matchAll(/<h3>(Course\d+)\s*·\s*([^—]+)—\s*(\d+)\/(\d+) complete<\/h3>/g),
  ].map((m) => ({ id: m[1], name: m[2].trim(), done: +m[3], of: +m[4] }));
  return { done: total ? +total[1] : 0, of: total ? +total[2] : 365, courses };
}

function hero(themeName, p) {
  const t = THEMES[themeName],
    W = 880,
    H = 284;
  const frac = p.of ? p.done / p.of : 0;
  const R = 62,
    C = 2 * Math.PI * R;

  const rows = p.courses
    .slice(0, 4)
    .map((c, i) => {
      const y = 66 + i * 44,
        full = c.done === c.of,
        col = full ? GREEN : SKY;
      const w = Math.max(4, Math.round(212 * (c.of ? c.done / c.of : 0)));
      return `
    <g class="row">
      <rect x="24" y="${y}" width="248" height="34" rx="9" fill="${t.panel}" stroke="${t.edge}"/>
      <text x="38" y="${y + 15}" class="mono b" fill="${t.ink}">${esc(c.name.slice(0, 26))}</text>
      <rect x="38" y="${y + 22}" width="212" height="4" rx="2" fill="${t.edge}"/>
      <rect class="fill f${i}" x="38" y="${y + 22}" width="${w}" height="4" rx="2" fill="${col}"/>
      <text x="256" y="${y + 15}" text-anchor="end" class="mono xs" fill="${col}">${c.done}/${c.of}</text>
    </g>`;
    })
    .join('');

  const right = [
    ['one lesson', 'written to be read once', SKY],
    ['one lab', 'that actually runs', GREEN],
    ['one output', 'captured from a real run', AMBER],
  ]
    .map(([k, v, col], i) => {
      const y = 84 + i * 44;
      return `
    <g class="vrow v${i}">
      <rect x="600" y="${y}" width="248" height="34" rx="9" fill="${t.panel}" stroke="${t.edge}"/>
      <circle cx="618" cy="${y + 17}" r="4.5" fill="${col}"/>
      <text x="632" y="${y + 14}" class="mono b" fill="${col}">${esc(k)}</text>
      <text x="632" y="${y + 27}" class="mono xs" fill="${t.dim}">${esc(v)}</text>
    </g>`;
    })
    .join('');

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="365 Days of AI Mastery: nine standalone courses, ${p.done} of ${p.of} days complete, one lesson and one runnable lab every day.">
  <style>
    .mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
    .sans{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
    .b{font-size:11.5px;font-weight:700}.xs{font-size:9.5px;letter-spacing:.06em}
    .cap{font-size:10px;font-weight:700;letter-spacing:.18em}
    @keyframes arc{from{stroke-dashoffset:${C.toFixed(1)}}to{stroke-dashoffset:${(C * (1 - frac)).toFixed(1)}}}
    @keyframes spin{to{transform:rotate(360deg)}}
    @keyframes pulse{0%,100%{opacity:.4}50%{opacity:1}}
    @keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
    @keyframes glow{0%,100%{opacity:.18}50%{opacity:.4}}
    .arc{animation:arc 2.4s cubic-bezier(.22,.9,.3,1) both}
    .ticks{animation:spin 60s linear infinite;transform-origin:0 0}
    .vrow{animation:pulse 4.2s ease-in-out infinite}.v1{animation-delay:1.4s}.v2{animation-delay:2.8s}
    .fill{animation:grow 1.6s ease-out both;transform-origin:left center}
    .f1{animation-delay:.2s}.f2{animation-delay:.4s}.f3{animation-delay:.6s}
    .glow{animation:glow 4.4s ease-in-out infinite}
    @media (prefers-reduced-motion:reduce){*{animation:none!important}
      .arc{stroke-dashoffset:${(C * (1 - frac)).toFixed(1)}}.fill{transform:none}}
  </style>
  <defs><radialGradient id="g-${themeName}">
    <stop offset="0%" stop-color="${SKY}" stop-opacity=".34"/>
    <stop offset="60%" stop-color="${SKY}" stop-opacity=".10"/>
    <stop offset="100%" stop-color="${SKY}" stop-opacity="0"/></radialGradient></defs>
  <rect width="${W}" height="${H}" rx="18" fill="${t.bg}"/>
  <circle class="glow" cx="440" cy="142" r="120" fill="url(#g-${themeName})"/>
  <text x="24"  y="36" class="mono cap" fill="${t.dim}">NINE COURSES</text>
  <text x="386" y="36" class="mono cap" fill="${SKY}">ONE YEAR</text>
  <text x="600" y="36" class="mono cap" fill="${GREEN}">EVERY DAY</text>
  ${rows}
  <g transform="translate(440 146)">
    <g class="ticks" opacity=".5">
      <circle r="${R + 13}" fill="none" stroke="${t.edge}" stroke-width="6" stroke-dasharray="1 7.28"/>
    </g>
    <circle r="${R}" fill="none" stroke="${t.edge}" stroke-width="9"/>
    <circle class="arc" r="${R}" fill="none" stroke="${BLUE}" stroke-width="9" stroke-linecap="round"
            stroke-dasharray="${C.toFixed(1)}" transform="rotate(-90)"/>
    <text y="-2" text-anchor="middle" class="sans" font-size="30" font-weight="800" fill="${t.ink}">${p.done}</text>
    <text y="20" text-anchor="middle" class="mono xs" fill="${t.dim}">OF ${p.of} DAYS</text>
  </g>
  <text x="440" y="248" text-anchor="middle" class="sans" font-size="14" font-weight="700" fill="${t.ink}">365 Days of AI Mastery</text>
  <text x="440" y="264" text-anchor="middle" class="mono xs" fill="${t.dim}">HOW A COMPUTER WORKS · TO SHIPPING PRODUCTION AI</text>
  ${right}
</svg>`;
}

function starButton(themeName) {
  const t = THEMES[themeName],
    W = 132,
    H = 34;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="Star this repository on GitHub">
  <style>
    .mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11.5px;font-weight:700}
    @keyframes cur{0%{transform:translate(34px,26px);opacity:0}12%{opacity:1}30%,38%{transform:translate(12px,13px)}
      44%{transform:translate(12px,15px)}58%{transform:translate(12px,13px)}80%{transform:translate(12px,13px);opacity:1}
      92%,100%{transform:translate(34px,26px);opacity:0}}
    @keyframes press{0%,38%,58%,100%{transform:scale(1)}46%{transform:scale(.94)}}
    @keyframes fill{0%,44%{fill:none;stroke-width:1.6}52%,88%{fill:#f5b301;stroke-width:0}96%,100%{fill:none;stroke-width:1.6}}
    @keyframes pop{0%,44%{transform:scale(1)}54%{transform:scale(1.28)}64%,100%{transform:scale(1)}}
    @keyframes tick{0%,52%{opacity:0}62%,86%{opacity:1}94%,100%{opacity:0}}
    .btn{animation:press 5s ease-in-out infinite;transform-origin:50% 50%}
    .star{animation:fill 5s ease-in-out infinite,pop 5s ease-in-out infinite;transform-origin:center;transform-box:fill-box}
    .cur{animation:cur 5s ease-in-out infinite}.n{animation:tick 5s ease-in-out infinite}
    @media (prefers-reduced-motion:reduce){*{animation:none!important}.star{fill:#f5b301;stroke-width:0}.n{opacity:1}}
  </style>
  <g class="btn">
    <rect x=".8" y=".8" width="${W - 1.6}" height="${H - 1.6}" rx="9" fill="${t.panel}" stroke="${t.edge}"/>
    <path class="star" d="M20 8.2 l3.3 6.7 7.4 1.1 -5.35 5.2 1.26 7.35 -6.61-3.47 -6.61 3.47 1.26-7.35 -5.35-5.2 7.4-1.1 z"
          fill="none" stroke="#f5b301" stroke-width="1.6" stroke-linejoin="round"/>
    <text x="42" y="22" class="mono" fill="${t.ink}">Star</text>
    <g class="n"><rect x="${W - 42}" y="9" width="32" height="16" rx="5" fill="#f5b301" opacity=".16"/>
      <text x="${W - 26}" y="21" text-anchor="middle" class="mono" fill="#d69a00">+1</text></g>
  </g>
  <g class="cur"><path d="M0 0 L0 13.5 L3.6 10.4 L6.1 15.6 L8.4 14.5 L5.9 9.4 L10.6 9.1 Z"
     fill="${t.ink}" stroke="${t.bg}" stroke-width="1.1"/></g>
</svg>`;
}

const p = progress();
const out = join(ROOT, 'assets', 'readme');
mkdirSync(out, { recursive: true });
for (const th of Object.keys(THEMES)) {
  writeFileSync(join(out, `hero-${th}.svg`), hero(th, p));
  writeFileSync(join(out, `star-${th}.svg`), starButton(th));
}
console.log(
  `wrote 4 animated files -> assets/readme (${p.done}/${p.of} days, ${p.courses.length} courses read from CURRICULUM.md)`,
);
