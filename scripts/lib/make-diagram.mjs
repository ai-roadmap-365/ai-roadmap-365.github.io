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
    .${id}-line { stroke: #64748b; stroke-width: 2; fill: none; }`;
}

/** Motion is opt-in, guarded, and always degrades to a visible resting state. */
function motion(id, kind) {
  if (kind !== 'sequence') return '';
  return `
    /* The token rests visible at the first stage; the static frame already shows
       every stage and label, so motion only draws attention to the order. */
    .${id}-tok { fill: #1d4ed8; opacity: 1; }
    @media (prefers-reduced-motion: no-preference) {
      .${id}-tok { animation: ${id}-travel 7s ease-in-out infinite; }
    }
    @keyframes ${id}-travel {
      0%, 6%    { transform: translateX(0);    opacity: 1; }
      94%, 100% { transform: translateX(var(--${id}-run, 600px)); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .${id}-tok { animation: none; transform: translateX(0); opacity: 1; }
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
    boxW = Math.floor((W - 60 - (stages.length - 1) * 22) / stages.length);
  const H = 300 + (note ? 34 : 0);
  const y = 132,
    run = (boxW + 22) * (stages.length - 1);
  let body = '';
  stages.forEach((s, i) => {
    const x = 30 + i * (boxW + 22);
    const cls =
      s.emphasis === 'good'
        ? `${id}-good`
        : s.emphasis === 'warn'
          ? `${id}-warn`
          : s.emphasis
            ? `${id}-hi`
            : `${id}-box`;
    body += `\n  <rect class="${cls}" x="${x}" y="${y}" width="${boxW}" height="96" rx="9"/>`;
    body += `\n  <text class="${id}-name" x="${x + 14}" y="${y + 28}">${esc(s.name)}</text>`;
    wrap(s.detail ?? '', Math.floor(boxW / 6.6))
      .slice(0, 3)
      .forEach((l, n) => {
        body += `\n  <text class="${id}-desc" x="${x + 14}" y="${y + 50 + n * 16}">${esc(l)}</text>`;
      });
    if (s.cost)
      body += `\n  <text class="${id}-edge" x="${x + 14}" y="${y + 116}">${esc(s.cost)}</text>`;
    if (i < stages.length - 1) {
      const ax = x + boxW + 3;
      body += `\n  <line class="${id}-line" x1="${ax}" y1="${y + 48}" x2="${ax + 16}" y2="${y + 48}"/>`;
    }
  });
  body += `\n  <rect class="${id}-tok" x="34" y="${y - 26}" width="${Math.min(58, boxW - 8)}" height="14" rx="3" style="--${id}-run: ${run}px"/>`;
  if (note) body += `\n  <text class="${id}-sub" x="30" y="${H - 20}">${esc(note)}</text>`;
  return `${head(id, W, H, title, subtitle ?? title)}
  <style>
${baseStyle(id)}${motion(id, 'sequence')}
  </style>
  <rect class="${id}-bg" width="${W}" height="${H}"/>
  <text class="${id}-h1"  x="30" y="40">${esc(title)}</text>
  <text class="${id}-sub" x="30" y="64">${esc(subtitle ?? '')}</text>${body}
</svg>
`;
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
      out += `\n  <text class="${id}-desc" x="${x + 16}" y="${182 + i * 34}">${esc(r)}</text>`;
    });
    return out;
  };
  return `${head(id, W, H, title, subtitle ?? title)}
  <style>
${baseStyle(id)}
  </style>
  <rect class="${id}-bg" width="${W}" height="${H}"/>
  <text class="${id}-h1"  x="30" y="40">${esc(title)}</text>
  <text class="${id}-sub" x="30" y="64">${esc(subtitle ?? '')}</text>${col(left, 30)}${col(right, 510)}${
    note ? `\n  <text class="${id}-sub" x="30" y="${H - 18}">${esc(note)}</text>` : ''
  }
</svg>
`;
}
