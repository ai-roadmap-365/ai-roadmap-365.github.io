// SPDX-FileCopyrightText: 2026 Sandeep Bazar
// SPDX-License-Identifier: Apache-2.0
//
// Animated art: the README hero, the star button, and the map of the year.
//
// Every figure is read from CURRICULUM.md rather than written here, because art that hard-codes a
// day count keeps advertising a number the course passed months ago. The nine day RANGES are
// derived the same way — a running total of each course's length — so adding or resizing a course
// moves every label without anyone editing a coordinate.
//
// A README renders these through GitHub's image proxy, which is a closed context: no font loads,
// no script runs, no <foreignObject> lays anything out. So the motion is CSS keyframes inside the
// file, the type is generic families only, and every coordinate is computed here.
//
// Motion rules, enforced by `npm run validate:animation` (A44):
//   - nothing MOVES under prefers-reduced-motion: reduce, and
//   - nothing that carries meaning DISAPPEARS when the motion stops.
// So each reduce rule names its classes explicitly. A blanket `*{animation:none}` works in a
// browser but is invisible to a checker that resolves the cascade per class, and a rule nothing
// can check is a rule that is already broken.
//
// Usage:  node scripts/build-hero.mjs
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const THEMES = {
  dark: {
    bg: '#0b1020',
    panel: '#121a30',
    edge: '#243154',
    ink: '#e8ecf8',
    dim: '#93a4c8',
    rail: '#1b2440',
  },
  light: {
    bg: '#fbfcff',
    panel: '#ffffff',
    edge: '#dfe6f5',
    ink: '#0f1729',
    dim: '#5a6b8c',
    rail: '#e6ecf8',
  },
};
const BLUE = '#1d4ed8',
  SKY = '#38bdf8',
  GREEN = '#22c55e',
  AMBER = '#f59e0b';
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// ---------------------------------------------------------------- curriculum

function progress() {
  const md = readFileSync(join(ROOT, 'CURRICULUM.md'), 'utf8');
  const total = md.match(/\*\*(\d+) of (\d+) days complete\.\*\*/);
  const courses = [
    ...md.matchAll(/<h3>(Course\d+)\s*·\s*([^—]+)—\s*(\d+)\/(\d+) complete<\/h3>/g),
  ].map((m) => ({ id: m[1], name: m[2].trim(), done: +m[3], of: +m[4] }));

  // Day ranges are a running total, never written down. The first course starts
  // on day 1 and each one begins where the last ended.
  let cursor = 1;
  for (const c of courses) {
    c.from = cursor;
    c.to = cursor + c.of - 1;
    cursor = c.to + 1;
  }
  return { done: total ? +total[1] : 0, of: total ? +total[2] : 365, courses };
}

/**
 * Editorial copy for the map, keyed by course id so it survives a rename.
 * `short` is the name that fits on a signpost; `gain` is what you can do by the
 * end of that course. A course with no entry falls back to its own first word,
 * so a tenth course renders as something rather than nothing.
 */
const STOPS = {
  Course01: { short: 'Foundations', gain: 'the machine', colour: '#38bdf8' },
  Course02: { short: 'Python', gain: 'you can build', colour: '#818cf8' },
  Course03: { short: 'Maths', gain: 'no longer magic', colour: '#f472b6' },
  Course04: { short: 'Machine Learning', gain: 'models that hold up', colour: '#4ade80' },
  Course05: { short: 'Deep Learning', gain: 'nets from scratch', colour: '#fbbf24' },
  Course06: { short: 'LLMs', gain: 'prompt, ground, tune', colour: '#a78bfa' },
  Course07: { short: 'AI Engineering', gain: 'agents and MCP', colour: '#22d3ee' },
  Course08: { short: 'Deploy', gain: 'it survives users', colour: '#fb7185' },
  Course09: { short: 'Capstone', gain: 'you ship it', colour: '#facc15' },
};
const FALLBACK = '#7dd3fc';

// ------------------------------------------------------------------ layout

/**
 * Approximate rendered width. There is no text engine here and no font to
 * measure — the README renders with whatever generic family the viewer has —
 * so this is a deliberate over-estimate. Wrapping a label that would have just
 * fitted costs a line; not wrapping one that does not fit collides with its
 * neighbour, which is the defect this exists to prevent.
 */
const estWidth = (text, fs, { mono = false, bold = false } = {}) =>
  text.length * fs * (mono ? 0.6 : bold ? 0.58 : 0.545);

/**
 * Wrap onto two BALANCED lines, not greedy ones.
 *
 * Greedy filling packs the first line and leaves whatever is left over on the
 * second, which is how "models that hold up" becomes "models that hold" above a
 * lone "up". Choosing the split that minimises the WIDER of the two lines gives
 * "models that" / "hold up" instead: the same information, centred, with no
 * orphan. Single words, and text that already fits, are returned untouched.
 */
function wrap(text, maxW, fs, opts = {}) {
  if (estWidth(text, fs, opts) <= maxW) return [text];
  const words = text.split(' ');
  if (words.length < 2) return [text];
  let best = null;
  for (let i = 1; i < words.length; i += 1) {
    const a = words.slice(0, i).join(' '),
      b = words.slice(i).join(' ');
    const widest = Math.max(estWidth(a, fs, opts), estWidth(b, fs, opts));
    if (!best || widest < best.widest) best = { lines: [a, b], widest };
  }
  return best.lines;
}

// -------------------------------------------------------------------- hero

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

  // Sparks sit on the ring at the arc's leading edge once it has drawn.
  const dashOff = (C * (1 - frac)).toFixed(1);

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="365 Days of AI Mastery: nine standalone courses, ${p.done} of ${p.of} days complete, one lesson and one runnable lab every day.">
  <style>
    .mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
    .sans{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
    .b{font-size:11.5px;font-weight:700}.xs{font-size:9.5px;letter-spacing:.06em}
    .cap{font-size:10px;font-weight:700;letter-spacing:.18em}
    @keyframes arc{from{stroke-dashoffset:${C.toFixed(1)}}to{stroke-dashoffset:${dashOff}}}
    @keyframes spin{to{transform:rotate(360deg)}}
    @keyframes pulse{0%,100%{opacity:.45}50%{opacity:1}}
    @keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
    @keyframes glow{0%,100%{opacity:.16}50%{opacity:.42}}
    @keyframes sheen{0%{opacity:0}8%{opacity:.5}22%{opacity:0}100%{opacity:0}}
    @keyframes countIn{0%{opacity:0}30%{opacity:1}100%{opacity:1}}
    .arc{animation:arc 2.6s cubic-bezier(.22,.9,.3,1) both}
    .ticks{animation:spin 60s linear infinite;transform-origin:0 0}
    .vrow{animation:pulse 4.2s ease-in-out infinite}.v1{animation-delay:1.4s}.v2{animation-delay:2.8s}
    .fill{animation:grow 1.7s cubic-bezier(.22,.9,.3,1) both;transform-origin:left center}
    .f1{animation-delay:.18s}.f2{animation-delay:.36s}.f3{animation-delay:.54s}
    .glow{animation:glow 4.4s ease-in-out infinite}
    /* One slow sweep of light across the ring, long after the arc has settled. */
    .sheen{animation:sheen 9s ease-in-out 3s infinite}
    .count{animation:countIn 2.6s ease-out both}
    @media (prefers-reduced-motion:reduce){
      /* Every class named, so a cascade-resolving checker can see the stop.
         The arc keeps its finished length, the bars keep their finished width:
         the picture is the same one, just already arrived. */
      .arc{animation:none;stroke-dashoffset:${dashOff}}
      .ticks{animation:none}
      .fill{animation:none;transform:none}
      .glow{animation:none;opacity:.28}
      /* reduce-ok: .sheen is a highlight sweeping a ring that is already fully
         drawn at its finished length, with the day count written inside it.
         Nothing is said by the sweep that the ring has not already said. */
      .sheen{animation:none;opacity:0}
      .count{animation:none;opacity:1}
      /* Opacity-only, vestibular-safe: the three promises still take turns. */
      .vrow{animation:pulse 6s ease-in-out infinite}
    }
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
    <circle class="sheen" r="${R}" fill="none" stroke="${SKY}" stroke-width="9" stroke-linecap="round"
            stroke-dasharray="34 ${(C - 34).toFixed(1)}" transform="rotate(-90)"/>
    <g class="count">
      <text y="-2" text-anchor="middle" class="sans" font-size="30" font-weight="800" fill="${t.ink}">${p.done}</text>
      <text y="20" text-anchor="middle" class="mono xs" fill="${t.dim}">OF ${p.of} DAYS</text>
    </g>
  </g>
  <text x="440" y="248" text-anchor="middle" class="sans" font-size="14" font-weight="700" fill="${t.ink}">365 Days of AI Mastery</text>
  <text x="440" y="264" text-anchor="middle" class="mono xs" fill="${t.dim}">HOW A COMPUTER WORKS · TO SHIPPING PRODUCTION AI</text>
  ${right}
</svg>`;
}

// ------------------------------------------------------------------- star

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
    @keyframes ray{0%,48%{opacity:0;transform:scale(.6)}58%{opacity:.9;transform:scale(1)}72%,100%{opacity:0;transform:scale(1.25)}}
    .btn{animation:press 5s ease-in-out infinite;transform-origin:50% 50%}
    .star{animation:fill 5s ease-in-out infinite,pop 5s ease-in-out infinite;transform-origin:center;transform-box:fill-box}
    .cur{animation:cur 5s ease-in-out infinite}.n{animation:tick 5s ease-in-out infinite}
    .rays{animation:ray 5s ease-in-out infinite;transform-origin:center;transform-box:fill-box}
    @media (prefers-reduced-motion:reduce){
      /* The button's resting state is the one worth showing: starred. */
      .btn{animation:none;transform:none}
      .star{animation:none;fill:#f5b301;stroke-width:0}
      /* reduce-ok: .cur and .rays act out a click that the still frame has
         already finished — the star is shown filled and the +1 counted. A
         pointer mid-gesture and a burst of sparks would only describe how the
         button got there. */
      .cur{animation:none;opacity:0}
      .rays{animation:none;opacity:0}
      .n{animation:none;opacity:1}
    }
  </style>
  <g class="btn">
    <rect x=".8" y=".8" width="${W - 1.6}" height="${H - 1.6}" rx="9" fill="${t.panel}" stroke="${t.edge}"/>
    <g class="rays" stroke="#f5b301" stroke-width="1.5" stroke-linecap="round" opacity="0">
      <path d="M20 1.6 V5"/><path d="M20 29 v3.4"/><path d="M6.6 17 H3.2"/><path d="M36.8 17 h3.4"/>
      <path d="M10.5 7.5 8.1 5.1"/><path d="M29.5 26.5 31.9 28.9"/>
      <path d="M29.5 7.5 31.9 5.1"/><path d="M10.5 26.5 8.1 28.9"/>
    </g>
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

// ---------------------------------------------------------------- journey

/**
 * The map of the year: nine stops on one path, each with its day range and what
 * you can do by the end of it.
 *
 * Every label is wrapped against the ACTUAL stop spacing rather than trusted to
 * fit. The hand-drawn version this replaces centred "Machine Learning" and
 * "Deep Learning" on 126px centres and they collided on the live site — the
 * kind of defect that only appears once the text is real.
 *
 * The traveller walks stop to stop and rests at each one, and the stop it has
 * reached brightens as it arrives. Both run on the same 22s cycle, so the two
 * stay in step for as long as the page is open: each stop's delay is exactly
 * the time the traveller takes to reach it.
 */
function journey(themeName, p, { W = 1200, H = 300, opaqueBg = true } = {}) {
  const t = THEMES[themeName];
  const stops = p.courses.map((c, i) => {
    const s = STOPS[c.id] ?? {};
    return {
      short: s.short ?? c.name.split(/[\s,:]+/)[0],
      gain: s.gain ?? `${c.of} days`,
      colour: s.colour ?? FALLBACK,
      days: `${c.from}–${c.to}`,
      i,
    };
  });
  const n = stops.length;
  const scale = W / 1200;
  const margin = Math.round(W * 0.079);
  const span = W - 2 * margin;
  const gap = n > 1 ? span / (n - 1) : 0;

  const fsLabel = +(15 * scale).toFixed(1);
  const fsDays = +(12 * scale).toFixed(1);
  const fsGain = +(12.5 * scale).toFixed(1);
  const fsHead = +(17 * scale).toFixed(1);
  const fsSub = +(13 * scale).toFixed(1);
  const fsFoot = +(12 * scale).toFixed(1);

  const yPath = 154;
  const rStop = +(9 * Math.min(1, scale + 0.25)).toFixed(1);

  // Per-stop cycle: dwell at the stop, then travel to the next one.
  const CYCLE = 22;
  const slot = 100 / n; // 9 stops -> 11.111% each
  const dwell = slot * 0.34;

  const travelKf = stops
    .map((s, i) => {
      const a = (i * slot).toFixed(2),
        b = (i * slot + dwell).toFixed(2);
      return `${a}%,${b}%{transform:translateX(${(i * gap).toFixed(1)}px)}`;
    })
    .join('');

  const marks = stops
    .map((s) => {
      const x = +(margin + s.i * gap).toFixed(1);
      const labelLines = wrap(s.short, gap * 0.94, fsLabel, { bold: true });
      const gainLines = wrap(s.gain, gap * 0.98, fsGain);
      // Labels grow upward from the path so the day range below never shifts.
      const labelTop = yPath - 30 - (labelLines.length - 1) * (fsLabel + 3);
      const label = labelLines
        .map(
          (ln, k) =>
            `<text class="jlabel" x="${x}" y="${(labelTop + k * (fsLabel + 3)).toFixed(1)}" text-anchor="middle" fill="${t.ink}">${esc(ln)}</text>`,
        )
        .join('');
      const gain = gainLines
        .map(
          (ln, k) =>
            `<text class="jgain" x="${x}" y="${(yPath + 62 + k * (fsGain + 3)).toFixed(1)}" text-anchor="middle" fill="${t.dim}">${esc(ln)}</text>`,
        )
        .join('');
      return `
    <g>
      ${label}
      <circle class="jstop s${s.i}" cx="${x}" cy="${yPath}" r="${rStop}" fill="${t.bg}" stroke="${s.colour}" stroke-width="3.5"/>
      <text class="jdays" x="${x}" y="${yPath + 42}" text-anchor="middle" fill="${t.dim}">${esc(s.days)}</text>
      ${gain}
    </g>`;
    })
    .join('');

  const delays = stops
    .map((s) => `.s${s.i}{animation-delay:${((s.i * slot * CYCLE) / 100).toFixed(2)}s}`)
    .join('');

  const x0 = margin,
    x1 = margin + (n - 1) * gap;
  const pathLen = x1 - x0;

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-labelledby="jt-${themeName} jd-${themeName}" preserveAspectRatio="xMidYMid meet">
  <title id="jt-${themeName}">The ${p.of}-day journey: from a transistor on day 1 to a shipped AI system on day ${p.of}</title>
  <desc id="jd-${themeName}">${n} courses laid out as one continuous path. ${stops
    .map((s) => `${s.short}, days ${s.days.replace('–', ' to ')}, ${s.gain}`)
    .join('. ')}. Every stop carries one lesson and one runnable lab.</desc>
  <defs>
    <!-- userSpaceOnUse, not the default objectBoundingBox: the path this fills
         is a perfectly horizontal line, so its bounding box has zero height and
         a proportional gradient degenerates against it. The hand-drawn map this
         replaces carried that bug and drew the year as a grey rail. -->
    <linearGradient id="jp-${themeName}" gradientUnits="userSpaceOnUse"
                    x1="${margin}" y1="${yPath}" x2="${margin + (n - 1) * gap}" y2="${yPath}">
      ${stops.map((s, i) => `<stop offset="${((i / (n - 1)) * 100).toFixed(1)}%" stop-color="${s.colour}"/>`).join('\n      ')}
    </linearGradient>
    <filter id="jg-${themeName}" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <style>
    .jlabel{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;font-size:${fsLabel}px;font-weight:700}
    .jdays{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:${fsDays}px;letter-spacing:.5px}
    .jgain{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;font-size:${fsGain}px}
    .jhead{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;font-size:${fsHead}px;font-weight:800}
    .jsub{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;font-size:${fsSub}px}
    .jfoot{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;font-size:${fsFoot}px}

    /* A light runs the length of the path, in the direction of travel. The path
       itself is always fully drawn: the route is the meaning, so it is never
       something the reader has to wait for. */
    @keyframes jcomet{from{stroke-dashoffset:${pathLen.toFixed(0)}}to{stroke-dashoffset:${(-pathLen).toFixed(0)}}}
    @keyframes jwalk{${travelKf}}
    @keyframes jarrive{0%,3%{opacity:1;stroke-width:6}14%,100%{opacity:1;stroke-width:3.5}}
    @keyframes jhalo{0%,3%{opacity:.55;transform:scale(1.5)}16%,100%{opacity:0;transform:scale(1)}}
    @keyframes jbreathe{0%,100%{opacity:.5}50%{opacity:1}}

    .jcomet{animation:jcomet 6s linear infinite}
    .jstop{animation:jarrive ${CYCLE}s ease-out infinite}
    .jhalo{animation:jhalo ${CYCLE}s ease-out infinite;transform-origin:center;transform-box:fill-box}
    .jtok{animation:jwalk ${CYCLE}s cubic-bezier(.65,0,.35,1) infinite}
    .jtokglow{animation:jbreathe 3.2s ease-in-out infinite}
    ${delays}

    @media (prefers-reduced-motion:reduce){
      /* Nothing moves. Every stop, its day range and its label were already on
         screen; what stops is the light travelling between them. */
      .jcomet{animation:none;stroke-dasharray:none;opacity:.2}
      .jstop{animation:none}
      /* reduce-ok: .jhalo is the ripple that marks the traveller arriving at a
         stop. With the traveller parked, there is no arrival to mark, and every
         stop keeps its ring, its name, its day range and its outcome. */
      .jhalo{animation:none;opacity:0}
      .jtok{animation:none;transform:none}
      .jtokglow{animation:jbreathe 5s ease-in-out infinite}
    }
  </style>

  ${opaqueBg ? `<rect width="${W}" height="${H}" rx="14" fill="${t.bg}"/>` : ''}

  <text class="jhead" x="${W / 2}" y="${46 * Math.min(1, scale + 0.2)}" text-anchor="middle" fill="${t.ink}">Day 1 you meet a transistor. Day ${p.of} you ship an AI system you built.</text>
  <text class="jsub" x="${W / 2}" y="${72 * Math.min(1, scale + 0.2)}" text-anchor="middle" fill="${SKY}">One lesson and one runnable lab, every single day — free, no prerequisites.</text>

  <path d="M ${x0} ${yPath} H ${x1}" fill="none" stroke="${t.rail}" stroke-width="7" stroke-linecap="round"/>
  <path d="M ${x0} ${yPath} H ${x1}" fill="none" stroke="url(#jp-${themeName})" stroke-width="5" stroke-linecap="round"/>
  <path class="jcomet" d="M ${x0} ${yPath} H ${x1}" fill="none" stroke="${t.ink}" stroke-width="2.5"
        stroke-linecap="round" stroke-dasharray="26 ${pathLen.toFixed(0)}" opacity=".7"/>

  ${marks}

  <g class="jtok" transform="translate(0 0)">
    <circle class="jhalo" cx="${x0}" cy="${yPath}" r="${rStop}" fill="none" stroke="${t.ink}" stroke-width="2" opacity="0"/>
    <circle class="jtokglow" cx="${x0}" cy="${yPath}" r="${(rStop * 1.7).toFixed(1)}" fill="${SKY}" opacity=".55" filter="url(#jg-${themeName})"/>
    <circle cx="${x0}" cy="${yPath}" r="${(rStop * 0.78).toFixed(1)}" fill="${t.ink}"/>
  </g>

  <text class="jfoot" x="${W / 2}" y="${H - 22}" text-anchor="middle" fill="${t.dim}">Start anywhere. Every course stands on its own, and every lab runs offline on a normal laptop.</text>
</svg>`;
}

// ------------------------------------------------------------------- write

const p = progress();
if (p.courses.length === 0) {
  console.error('✗ build-hero: no courses parsed from CURRICULUM.md — refusing to write art');
  process.exit(1);
}

const out = join(ROOT, 'assets', 'readme');
mkdirSync(out, { recursive: true });
for (const th of Object.keys(THEMES)) {
  writeFileSync(join(out, `hero-${th}.svg`), hero(th, p));
  writeFileSync(join(out, `star-${th}.svg`), starButton(th));
  writeFileSync(join(out, `journey-${th}.svg`), journey(th, p, { W: 880 }));
}

// The site's map. It sits on a deliberately dark card in both themes (see
// `.journey` in src/pages/index.astro), so it is the dark art at full width —
// generated from the same function, so the site and the README can never
// disagree about where the year goes.
writeFileSync(join(ROOT, 'public', 'journey.svg'), journey('dark', p, { W: 1200 }));

console.log(
  `wrote 6 README file(s) -> assets/readme and public/journey.svg ` +
    `(${p.done}/${p.of} days, ${p.courses.length} courses, day ranges derived from CURRICULUM.md)`,
);
