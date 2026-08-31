#!/usr/bin/env node
/**
 * Commit identity: every commit must be authored as sandeepbazar with the
 * GitHub noreply address, and must carry no AI attribution.
 *
 * This exists because the rule was followed by memory and memory failed: 23
 * commits in one session were authored with a real personal email address,
 * because each `git commit` passed an explicit `-c user.email=...` that
 * overrode the repository's already-correct configuration. Nothing caught it
 * until the owner read a commit command over my shoulder.
 *
 * Checks the commits that are still local, because those are the ones that can
 * still be corrected before they are published.
 */
import { execFileSync } from 'node:child_process';
import { makeReporter } from '../lib/course.mjs';

const r = makeReporter('validate:commit-identity');

const EXPECTED_EMAIL = '5602033+sandeepbazar@users.noreply.github.com';
const EXPECTED_NAME = 'sandeepbazar';
// Target ATTRIBUTION, not mentions. This repository legitimately contains
// CLAUDE.md, GEMINI.md and AGENTS.md as vendor bootstrap files, and commits
// about them name them — "CLAUDE.md gains a routing section" is a normal
// message, not a credit. A bare-name regex flags those, and a gate that cries
// wolf gets switched off, which is worse than no gate.
const AI_NAMES = String.raw`claude|codex|gemini|copilot|chatgpt|anthropic|openai|an? ai`;
const AI_MARKERS = new RegExp(
  [
    String.raw`co-authored-by\s*:`,
    String.raw`\bai[-\s]generated\b`,
    String.raw`\b(generated|authored|written|created|produced)\s+(with|by)\s+(${AI_NAMES})\b`,
    String.raw`\bassisted\s+by\s+(${AI_NAMES})\b`,
    '\u{1F916}', // robot emoji, used by some tools as a trailer
  ].join('|'),
  'iu',
);

/** Run git with an argument array, so nothing is interpreted by a shell. */
const git = (...args) => {
  try {
    return execFileSync('git', args, {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    }).trim();
  } catch {
    return '';
  }
};

// The configured identity, which is what an unqualified `git commit` will use.
const cfgEmail = git('config', 'user.email');
const cfgName = git('config', 'user.name');
if (cfgEmail !== EXPECTED_EMAIL)
  r.fail(`git config user.email is "${cfgEmail}" - expected "${EXPECTED_EMAIL}"`);
if (cfgName !== EXPECTED_NAME)
  r.fail(`git config user.name is "${cfgName}" - expected "${EXPECTED_NAME}"`);

// Unpushed commits are still correctable, so that is where it is worth failing.
// A fresh clone in CI has no upstream; then only the identity config is checked.
const hasUpstream = Boolean(git('rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'));

// Field and record separators unlikely to occur in a commit message.
const FS = '<<|F|>>';
const RS = '<<|R|>>';

let checked = 0;
if (hasUpstream) {
  const raw = git('log', '@{u}..HEAD', `--format=%H${FS}%an${FS}%ae${FS}%s${FS}%b${RS}`);
  for (const entry of raw.split(RS)) {
    const parts = entry.split(FS);
    if (parts.length < 5) continue;
    const [hash, name, email, subject, body] = parts.map((s) => s.trim());
    if (!hash) continue;
    checked++;
    const short = hash.slice(0, 8);
    if (email !== EXPECTED_EMAIL)
      r.fail(`${short}: authored as "${email}" - expected "${EXPECTED_EMAIL}"`);
    if (name !== EXPECTED_NAME)
      r.fail(`${short}: author name "${name}" - expected "${EXPECTED_NAME}"`);
    const marker = `${subject}\n${body}`.match(AI_MARKERS);
    if (marker) r.fail(`${short}: commit message contains AI attribution ("${marker[0]}")`);
  }
}

r.finish(
  `${checked} unpushed commit(s) authored correctly, with no AI attribution` +
    (hasUpstream ? '' : ' (no upstream; identity config checked only)'),
);
