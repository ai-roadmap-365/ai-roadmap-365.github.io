#!/usr/bin/env node
/**
 * Secret scan over all git-tracked files (and dist/ exports if present):
 * API keys, tokens, private keys, and .env files must never be committed
 * or shipped in an export.
 */
import { execSync } from 'node:child_process';
import { readFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import { repoRoot, makeReporter } from '../lib/course.mjs';

const r = makeReporter('validate:secrets');

const PATTERNS = [
  [/sk-ant-[a-zA-Z0-9-_]{20,}/, 'Anthropic API key'],
  [/sk-[a-zA-Z0-9]{40,}/, 'OpenAI-style API key'],
  [/ghp_[a-zA-Z0-9]{30,}/, 'GitHub personal access token'],
  [/github_pat_[a-zA-Z0-9_]{30,}/, 'GitHub fine-grained token'],
  [/AKIA[0-9A-Z]{16}/, 'AWS access key ID'],
  [/AIza[0-9A-Za-z\-_]{30,}/, 'Google API key'],
  [/-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----/, 'private key material'],
  [/xox[bpors]-[0-9a-zA-Z-]{10,}/, 'Slack token'],
];

const tracked = execSync('git ls-files', { cwd: repoRoot, encoding: 'utf8' }).trim().split('\n');

for (const rel of tracked) {
  if (/\.(png|jpg|jpeg|gif|ico|woff2?|lock)$/.test(rel)) continue;
  if (/^\.env(\..+)?$/.test(path.basename(rel)) && !rel.endsWith('.env.example'))
    r.fail(`environment file is tracked by git: ${rel}`);
  const full = path.join(repoRoot, rel);
  if (!existsSync(full)) continue;
  const text = readFileSync(full, 'utf8');
  for (const [re, label] of PATTERNS) {
    if (re.test(text)) r.fail(`${rel}: contains what looks like a ${label}`);
  }
}

// Exports must be secret-free too (requirements §8).
function* walk(dir) {
  for (const entry of readdirSync(dir)) {
    const full = path.join(dir, entry);
    if (statSync(full).isDirectory()) yield* walk(full);
    else if (/\.(html|md|json|js|css|txt|xml)$/.test(entry)) yield full;
  }
}
for (const distDir of ['dist/wordpress', 'dist/public-release', 'dist/offline']) {
  const full = path.join(repoRoot, distDir);
  if (!existsSync(full)) continue;
  for (const file of walk(full)) {
    const text = readFileSync(file, 'utf8');
    for (const [re, label] of PATTERNS) {
      if (re.test(text)) r.fail(`${path.relative(repoRoot, file)}: export contains a ${label}`);
    }
  }
}

r.finish(`${tracked.length} tracked files scanned; no secrets, no tracked .env files.`);
