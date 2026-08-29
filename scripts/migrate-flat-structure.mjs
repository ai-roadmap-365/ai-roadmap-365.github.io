#!/usr/bin/env node
/**
 * ONE-TIME migration (amendment A18): flatten the content/labs/instructor/
 * videos trees so each section directly holds its day directories, dropping
 * the `<subsection>/week-NN/` path levels. Weekly projects move to
 * `sections/<section>/projects/week-NN/`.
 *
 *   before: content/sections/<sec>/<sub>/week-NN/day-NNN-slug/
 *   after:  content/sections/<sec>/day-NNN-slug/
 *
 * Uses `git mv` to preserve history. Idempotent: skips anything already
 * flat. Run ONLY when no authoring agents are active. Curriculum data keeps
 * subsection/week as grouping metadata; only directory paths change (the
 * path helpers in links.mjs are updated separately to match).
 */
import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, statSync, rmdirSync } from 'node:fs';
import path from 'node:path';
import { repoRoot } from './lib/course.mjs';

const TREES = [
  'content/sections',
  'labs/sections',
  'instructor/project-solutions/sections',
  'videos/sections',
];

function git(args) {
  execFileSync('git', args, { cwd: repoRoot, stdio: 'pipe' });
}

let moved = 0;
let projectsMoved = 0;

function isDayDir(name) {
  return /^day-\d{3}-/.test(name);
}
function isWeekDir(name) {
  return /^week-\d{2}$/.test(name);
}

for (const tree of TREES) {
  const root = path.join(repoRoot, tree);
  if (!existsSync(root)) continue;
  for (const section of readdirSync(root)) {
    const secDir = path.join(root, section);
    if (!statSync(secDir).isDirectory()) continue;
    for (const sub of readdirSync(secDir)) {
      const subDir = path.join(secDir, sub);
      if (!statSync(subDir).isDirectory()) continue;
      // Already-flat day dirs and the projects dir stay put.
      if (isDayDir(sub) || sub === 'projects') continue;
      // subDir is a subsection; descend into its week dirs.
      for (const wk of readdirSync(subDir)) {
        const wkDir = path.join(subDir, wk);
        if (!statSync(wkDir).isDirectory()) continue;
        if (!isWeekDir(wk)) continue;
        for (const entry of readdirSync(wkDir)) {
          const src = path.join(wkDir, entry);
          if (!statSync(src).isDirectory()) continue;
          if (isDayDir(entry)) {
            const dest = path.join(secDir, entry);
            if (existsSync(dest)) {
              console.warn(`skip (exists): ${path.relative(repoRoot, dest)}`);
              continue;
            }
            git(['mv', path.relative(repoRoot, src), path.relative(repoRoot, dest)]);
            moved += 1;
          } else if (entry === 'project') {
            const destParent = path.join(secDir, 'projects');
            const dest = path.join(destParent, wk); // projects/week-NN
            if (!existsSync(destParent)) execFileSync('mkdir', ['-p', destParent]);
            if (existsSync(dest)) {
              console.warn(`skip (exists): ${path.relative(repoRoot, dest)}`);
              continue;
            }
            git(['mv', path.relative(repoRoot, src), path.relative(repoRoot, dest)]);
            projectsMoved += 1;
          }
        }
        // Remove the now-empty week dir (README etc. removed below).
      }
    }
  }
}

// Remove leftover subsection/week README files and empty dirs.
function pruneEmpty(dir) {
  if (!existsSync(dir)) return;
  for (const name of readdirSync(dir)) {
    const p = path.join(dir, name);
    if (statSync(p).isDirectory()) pruneEmpty(p);
  }
  const remaining = readdirSync(dir);
  // Delete a lone README.md left behind in a subsection/week dir.
  if (remaining.length === 1 && remaining[0] === 'README.md') {
    const readme = path.join(dir, 'README.md');
    try {
      git(['rm', '-q', path.relative(repoRoot, readme)]);
    } catch {
      /* not tracked */
    }
  }
  if (readdirSync(dir).length === 0) {
    try {
      rmdirSync(dir);
    } catch {
      /* ignore */
    }
  }
}

for (const tree of TREES) {
  const root = path.join(repoRoot, tree);
  if (!existsSync(root)) continue;
  for (const section of readdirSync(root)) {
    const secDir = path.join(root, section);
    if (!statSync(secDir).isDirectory()) continue;
    for (const sub of readdirSync(secDir)) {
      const subDir = path.join(secDir, sub);
      if (!statSync(subDir).isDirectory()) continue;
      if (isDayDir(sub) || sub === 'projects') continue;
      pruneEmpty(subDir);
    }
  }
}

console.log(
  `✓ migrate-flat-structure: moved ${moved} day dir(s), ${projectsMoved} project dir(s).`,
);
