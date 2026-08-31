#!/usr/bin/env node
/**
 * Gate: motion must never carry the meaning.
 *
 * A diagram that only makes sense while it is moving is broken for every reader
 * who has Reduce motion switched on -- which on macOS is a large share of them,
 * and which the browser honours whether we like it or not. Overriding the
 * setting is not an option: it is an accessibility control, and ignoring it can
 * make people ill. So the rule is inverted: animation may draw attention to an
 * order that is ALREADY VISIBLE, and nothing more.
 *
 * The failures this catches are the ones that survive review, because the
 * author has motion switched on and the diagram looks perfect to them.
 *
 * It resolves the cascade PER ELEMENT rather than per selector. That matters:
 * `.token { animation: none }` in the reduce block legitimately stops
 * `.t1 { animation-name: move1 }` when every element carries both classes, and
 * a selector-matching checker reports that as a fault. A gate that cries wolf
 * gets switched off, which is worse than not having one.
 */
import { readFileSync, globSync } from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const decomment = (css) => css.replace(/\/\*[\s\S]*?\*\//g, '');

/** Bodies of every top-level at-rule of one kind, plus everything else. */
function splitAtRules(css, kind) {
  const blocks = [];
  let rest = '';
  for (let i = 0; i < css.length;) {
    const at = css.indexOf(`@${kind}`, i);
    if (at === -1) {
      rest += css.slice(i);
      break;
    }
    rest += css.slice(i, at);
    const open = css.indexOf('{', at);
    if (open === -1) break;
    let depth = 0,
      end = open;
    for (; end < css.length; end += 1) {
      if (css[end] === '{') depth += 1;
      else if (css[end] === '}' && (depth -= 1) === 0) break;
    }
    blocks.push({ prelude: css.slice(at, open), body: css.slice(open + 1, end) });
    i = end + 1;
  }
  return { blocks, rest };
}

/**
 * Class-only rules, in source order. Anything using a tag, id, attribute or
 * combinator is skipped: ignoring a rule can only make us miss a fault, never
 * invent one, and a false alarm is the more expensive mistake here.
 */
function parseRules(css) {
  const rules = [];
  for (const m of css.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
    for (const sel of m[1].split(',')) {
      const s = sel.trim();
      if (!s || !/^(?:\.[A-Za-z0-9_-]+)+$/.test(s)) continue;
      rules.push({
        classes: s.slice(1).split('.'),
        decls: m[2],
        specificity: (s.match(/\./g) || []).length, // .a.b beats .a
        order: rules.length,
      });
    }
  }
  return rules;
}

const declValue = (decls, prop) => {
  const hits = [...decls.matchAll(new RegExp(`(?:^|[;{\\s])${prop}\\s*:\\s*([^;}]+)`, 'gi'))];
  return hits.length ? hits[hits.length - 1][1].trim() : null;
};

/** Merge every rule matching this element's class set, in cascade order. */
function computed(rules, classSet) {
  return rules
    .filter((r) => r.classes.every((c) => classSet.has(c)))
    .sort((a, b) => a.specificity - b.specificity || a.order - b.order)
    .map((r) => r.decls)
    .join(';');
}

/** The animation-name in force, accounting for the `animation` shorthand. */
function animationName(decls, keyframeNames) {
  const shorthand = declValue(decls, 'animation');
  const longhand = declValue(decls, 'animation-name');
  // Whichever was declared last wins; the shorthand resets animation-name.
  const iSh = decls.lastIndexOf('animation:');
  const iLh = decls.lastIndexOf('animation-name:');
  const winner = iLh > iSh ? longhand : (shorthand ?? longhand);
  if (!winner || /^none\b/.test(winner.trim())) return null;
  return keyframeNames.find((n) => new RegExp(`\\b${n}\\b`).test(winner)) ?? null;
}

const problems = [];
const stats = { scanned: 0, animated: 0 };

for (const rel of globSync('{content,public,src}/**/*.svg', { cwd: ROOT }).sort()) {
  const svg = readFileSync(path.join(ROOT, rel), 'utf8');
  stats.scanned += 1;
  const fail = (rule, detail) => problems.push({ rel, rule, detail });

  // --- Techniques the reader cannot switch off -----------------------------
  // SMIL is not CSS and no browser applies prefers-reduced-motion to it.
  const smil = svg.match(/<(animate|animateTransform|animateMotion|set)\b/);
  if (smil)
    fail('smil', `<${smil[1]}> ignores prefers-reduced-motion entirely; use CSS @keyframes`);

  // --- Dependencies that fail outside a live browser -----------------------
  // These load through <img>, which runs no script and fetches no external CSS,
  // and they must survive the offline build and PDF export.
  if (/<script\b/.test(svg)) fail('external', '<script> does not execute in <img>');
  if (/@import\b/.test(svg)) fail('external', '@import does not resolve in <img>');
  if (/@font-face\b/.test(svg)) fail('external', '@font-face pulls a font that may never arrive');
  const remote =
    svg.match(/(?:href|src)\s*=\s*"(https?:[^"]+)"/i) ||
    svg.match(/url\(\s*['"]?(https?:[^)'"]+)/i);
  if (remote) fail('external', `remote reference ${remote[1]}`);

  const rawStyles = [...svg.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)]
    .map((m) => m[1])
    .join('\n');
  if (!rawStyles.trim()) continue;
  const styles = decomment(rawStyles);

  const { blocks: kfBlocks, rest: afterKf } = splitAtRules(styles, 'keyframes');
  const { blocks: mediaBlocks, rest: topLevel } = splitAtRules(afterKf, 'media');
  const keyframes = new Map(
    kfBlocks.map((b) => [b.prelude.replace('@keyframes', '').trim(), b.body]).filter(([n]) => n),
  );
  const keyframeNames = [...keyframes.keys()];

  /** Highest opacity the element reaches while it IS animating. */
  const peakOpacity = (name, fallback) => {
    const stops = [...(keyframes.get(name) ?? '').matchAll(/\{([^{}]*)\}/g)]
      .map((m) => declValue(m[1], 'opacity'))
      .filter((o) => o !== null)
      .map(Number.parseFloat);
    return stops.length ? Math.max(...stops) : fallback;
  };

  const pick = (re) =>
    mediaBlocks
      .filter((b) => re.test(b.prelude))
      .map((b) => b.body)
      .join('\n');
  const reduceCss = pick(/prefers-reduced-motion\s*:\s*reduce/);
  const noPrefCss = pick(/prefers-reduced-motion\s*:\s*no-preference/);

  const motionRules = parseRules(topLevel + '\n' + noPrefCss);
  const reduceRules = parseRules(topLevel + '\n' + reduceCss);

  let fileAnimates = false;
  const reported = new Set();

  for (const m of svg.matchAll(/class\s*=\s*"([^"]+)"/g)) {
    const classSet = new Set(m[1].trim().split(/\s+/));
    const key = [...classSet].sort().join('.');
    if (reported.has(key)) continue;

    const moving = animationName(computed(motionRules, classSet), keyframeNames);
    if (!moving) continue;
    fileAnimates = true;
    reported.add(key);

    const underReduce = computed(reduceRules, classSet);

    // --- The motion must actually stop -----------------------------------
    if (animationName(underReduce, keyframeNames)) {
      fail('unstoppable', `.${key} keeps animating under prefers-reduced-motion: reduce`);
      continue;
    }

    // --- What is left must still be the whole diagram ---------------------
    // Base and reduce cannot be judged separately: a base `opacity: 0` is fine
    // when the reduce block restores it, and a reduce block is not fine merely
    // because it exists. Only the combination says what is on screen.
    // "Invisible" has to mean invisible, not merely faint. A band drawn at
    // opacity 0.14 that is parked rather than sliding has lost nothing: it looks
    // the same in both states. What matters is content that is visible while
    // moving and gone once it stops, so compare the two.
    const opacity = declValue(underReduce, 'opacity');
    const still = opacity === null ? 1 : Number.parseFloat(opacity);
    const moved = peakOpacity(
      moving,
      Number.parseFloat(declValue(computed(motionRules, classSet), 'opacity') ?? '1'),
    );
    const invisible =
      (still < 0.05 && moved >= 0.05) ||
      /visibility\s*:\s*hidden/i.test(underReduce) ||
      /display\s*:\s*none/i.test(underReduce);

    // Hiding something deliberately is legitimate -- one half of a before/after
    // pair has to be the half not shown. It just has to be DECLARED, so the
    // next author reads an intention instead of guessing at an oversight.
    const excused = [...classSet].some((c) =>
      new RegExp(`reduce-ok:[^*]*\\.${c}\\b`).test(rawStyles),
    );
    if (invisible && !excused) {
      fail(
        'lost-in-reduce',
        `.${key} reaches opacity ${moved} while animating but ${still} once motion ` +
          'is off — that content reaches the reader only as movement',
      );
    }
  }
  if (fileAnimates) stats.animated += 1;
}

const EXPLAIN = {
  smil: 'motion the reader cannot switch off',
  external: 'resources that do not load in <img>',
  unstoppable: "motion that ignores the reader's setting",
  'lost-in-reduce': 'content the Reduce-motion reader never sees',
};

console.log(`Animation accessibility: ${stats.scanned} SVGs scanned, ${stats.animated} animated.`);
if (!problems.length) {
  console.log('Every animated diagram is complete and readable with motion disabled.');
  process.exit(0);
}
const byRule = new Map();
for (const p of problems) byRule.set(p.rule, [...(byRule.get(p.rule) ?? []), p]);
for (const [rule, list] of byRule) {
  console.error(`\n${rule} — ${EXPLAIN[rule] ?? ''} (${list.length})`);
  for (const p of list.slice(0, 15)) console.error(`  ${p.rel}\n    ${p.detail}`);
  if (list.length > 15) console.error(`  ... and ${list.length - 15} more`);
}
console.error(`\n${problems.length} problems. Motion must never carry the meaning.`);
process.exit(1);
