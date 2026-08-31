/**
 * Emit a lesson diagram as a self-contained SVG.
 *
 * Hand-authoring one SVG per conversion produced inconsistent spacing and, more
 * than once, invalid XML -- XML predefines only five entities, so a bare `&` or
 * a stray `&rarr;` breaks the file. This builds them from a small spec instead,
 * escaping text centrally and applying the motion rules from A41 the same way
 * every time: the static frame is the complete diagram, motion is guarded behind
 * `no-preference`, and `reduce` degrades to a non-motion cue rather than to
 * nothing.
 *
 * Kinds:
 *   sequence   ordered stages, left to right, with a travelling token
 *   compare    two columns set against each other
 *   states     labelled boxes joined by captioned arrows
 */
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif';
const MONO = 'ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace';

function head(id, w, h, title, aria) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" role="img"
     aria-label="${esc(aria)}">
  <title>${esc(title)}</title>`;
}

function baseStyle(id) {
  return `    .${id}-bg   { fill: #f8fafc; }
    .${id}-h1   { fill: #1a202c; font-size: 21px; font-weight: 700; font-family: ${FONT}; }
    .${id}-sub  { fill: #475569; font-size: 14px; font-family: ${FONT}; }
    .${id}-name { fill: #1a202c; font-size: 15px; font-weight: 700; font-family: ${FONT}; }
    .${id}-desc { fill: #475569; font-size: 12.5px; font-family: ${FONT}; }
    .${id}-edge { fill: #1d4ed8; font-size: 12.5px; font-weight: 600; font-family: ${FONT}; }
    .${id}-mono { fill: #1a202c; font-size: 13px; font-family: ${MONO}; }
    .${id}-box  { fill: #ffffff; stroke: #94a3b8; stroke-width: 1.75; }
    .${id}-hi   { fill: #eff6ff; stroke: #1d4ed8; stroke-width: 2.25; }
    .${id}-warn { fill: #fef3c7; stroke: #b45309; stroke-width: 2; }
    .${id}-good { fill: #dcfce7; stroke: #047857; stroke-width: 2; }
    .${id}-line { stroke: #1d4ed8; stroke-width: 2.5; fill: none; }
    .${id}-step { fill: #1d4ed8; font-size: 12px; font-weight: 700; font-family: ${MONO}; }`;
}

/**
 * Motion, modelled on the trace technique: each connector draws itself along the
 * flow and each stage brightens as the flow reaches it, then everything rests in
 * the finished state.
 *
 * The base rules ARE the finished state, so a reader with motion disabled sees
 * the complete diagram rather than a half-drawn one -- the animation only adds
 * the order in which it assembles. Under `reduce` the stages still brighten in
 * sequence, because opacity carries the order without the movement that causes
 * harm; the flow is still communicated, it simply stops sliding.
 */
function motion(id, count) {
  if (!count) return '';
  const dur = Math.max(6, count * 1.6);
  let per = '';
  for (let i = 0; i < count; i += 1) {
    const delay = ((i * dur) / (count + 1)).toFixed(2);
    per += `
    .${id}-s${i} { animation-delay: ${delay}s; }
    .${id}-e${i} { animation-delay: ${delay}s; }`;
  }
  return `
    /* Finished state first: this is what a reader with motion off sees. */
    .${id}-conn { stroke-dasharray: 10 8; stroke-dashoffset: 0; opacity: 1; }
    .${id}-stage { opacity: 1; }
${per}
    @media (prefers-reduced-motion: no-preference) {
      .${id}-conn  { animation: ${id}-trace ${dur}s ease-in-out infinite; }
      .${id}-stage { animation: ${id}-arrive ${dur}s ease-in-out infinite; }
    }
    @keyframes ${id}-trace {
      0%        { stroke-dashoffset: 54; opacity: 0.35; }
      14%, 100% { stroke-dashoffset: 0;  opacity: 1; }
    }
    @keyframes ${id}-arrive {
      0%        { opacity: 0.55; }
      10%, 22%  { opacity: 1; }
      34%, 100% { opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      /* No movement, but the order is still shown: each stage brightens in turn
         and stays bright. Opacity and colour are vestibular-safe. */
      .${id}-conn  { animation: none; stroke-dashoffset: 0; opacity: 1; }
      .${id}-stage { animation: ${id}-settle ${dur}s ease-in-out infinite; opacity: 1; }
    }
    @keyframes ${id}-settle {
      0%        { opacity: 0.62; }
      12%, 100% { opacity: 1; }
    }`;
}

function wrap(text, max) {
  const words = String(text).split(/\s+/);
  const lines = [];
  let cur = '';
  for (const w of words) {
    if ((cur + ' ' + w).trim().length > max) {
      lines.push(cur.trim());
      cur = w;
    } else cur += ' ' + w;
  }
  if (cur.trim()) lines.push(cur.trim());
  return lines;
}

export function sequence({ id, title, subtitle, stages, note }) {
  const W = 980,
    boxW = Math.floor((W - 60 - (stages.length - 1) * 26) / stages.length);
  const H = 292 + (note ? 30 : 0);
  const y = 118;
  let body = '';
  stages.forEach((s, i) => {
    const x = 30 + i * (boxW + 26);
    const cls =
      s.emphasis === 'good'
        ? `${id}-good`
        : s.emphasis === 'warn'
          ? `${id}-warn`
          : s.emphasis
            ? `${id}-hi`
            : `${id}-box`;
    body += `\n  <g class="${id}-stage ${id}-s${i}">`;
    body += `\n    <rect class="${cls}" x="${x}" y="${y}" width="${boxW}" height="104" rx="10"/>`;
    body += `\n    <text class="${id}-step" x="${x + 14}" y="${y + 24}">${String(i + 1).padStart(2, '0')}</text>`;
    body += `\n    <text class="${id}-name" x="${x + 40}" y="${y + 24}">${esc(s.name)}</text>`;
    wrap(s.detail ?? '', Math.floor(boxW / 6.4))
      .slice(0, 3)
      .forEach((l, n) => {
        body += `\n    <text class="${id}-desc" x="${x + 14}" y="${y + 48 + n * 16}">${esc(l)}</text>`;
      });
    if (s.cost)
      body += `\n    <text class="${id}-edge" x="${x + 14}" y="${y + 124}">${esc(s.cost)}</text>`;
    body += `\n  </g>`;
    if (i < stages.length - 1) {
      const ax = x + boxW + 2,
        bx = x + boxW + 24;
      body += `\n  <line class="${id}-line ${id}-conn ${id}-e${i}" x1="${ax}" y1="${y + 52}" x2="${bx}" y2="${y + 52}" marker-end="url(#${id}-tip)"/>`;
    }
  });
  if (note) body += `\n  <text class="${id}-sub" x="30" y="${H - 18}">${esc(note)}</text>`;
  return `${head(id, W, H, title, subtitle ?? title)}
  <style>
${baseStyle(id)}${motion(id, stages.length)}
  </style>
  <defs>
    <marker id="${id}-tip" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">
      <path d="M0,0 L9,4.5 L0,9 z" fill="#1d4ed8"/>
    </marker>
  </defs>
  <rect class="${id}-bg" width="${W}" height="${H}"/>
  <text class="${id}-h1"  x="30" y="40">${esc(title)}</text>
  <text class="${id}-sub" x="30" y="64">${esc(subtitle ?? '')}</text>${body}
</svg>
`;
}

function revealCss(id, rows) {
  let per = '';
  for (let i = 0; i < rows; i += 1) {
    per += `\n    .${id}-r${i} { animation-delay: ${(i * 0.45).toFixed(2)}s; }`;
  }
  // The base state is fully visible, so a still frame is the complete table.
  // The reveal is opacity only -- identical under `reduce`, because nothing
  // moves. That is what lets it run for every reader on every device.
  return `
    .${id}-row { opacity: 1; }${per}
    .${id}-row { animation: ${id}-reveal ${(rows * 0.45 + 5).toFixed(1)}s ease-in-out infinite; }
    @keyframes ${id}-reveal {
      0%       { opacity: 0.5; }
      9%, 100% { opacity: 1; }
    }`;
}

export function compare({ id, title, subtitle, left, right, note }) {
  const W = 980,
    colW = 440,
    H = 180 + Math.max(left.rows.length, right.rows.length) * 34 + (note ? 40 : 0);
  const col = (side, x) => {
    let out = `\n  <rect class="${side.emphasis === 'good' ? `${id}-good` : side.emphasis === 'warn' ? `${id}-warn` : `${id}-hi`}" x="${x}" y="96" width="${colW}" height="56" rx="9"/>`;
    out += `\n  <text class="${id}-name" x="${x + 16}" y="${122}">${esc(side.heading)}</text>`;
    out += `\n  <text class="${id}-desc" x="${x + 16}" y="${142}">${esc(side.summary ?? '')}</text>`;
    side.rows.forEach((r, i) => {
      out += `\n  <text class="${id}-desc ${id}-row ${id}-r${i}" x="${x + 16}" y="${182 + i * 34}">${esc(r)}</text>`;
    });
    return out;
  };
  return `${head(id, W, H, title, subtitle ?? title)}
  <style>
${baseStyle(id)}${revealCss(id, Math.max(left.rows.length, right.rows.length))}
  </style>
  <rect class="${id}-bg" width="${W}" height="${H}"/>
  <text class="${id}-h1"  x="30" y="40">${esc(title)}</text>
  <text class="${id}-sub" x="30" y="64">${esc(subtitle ?? '')}</text>${col(left, 30)}${col(right, 510)}${
    note ? `\n  <text class="${id}-sub" x="30" y="${H - 18}">${esc(note)}</text>` : ''
  }
</svg>
`;
}
