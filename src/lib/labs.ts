import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';
import { repoRoot } from './config';
import { labPath } from './links';
import type { DayContext } from './curriculum';

export interface LabFile {
  /** path relative to the lab directory */
  relPath: string;
  size: number;
}

export interface LabMetadata {
  lesson_id: string;
  kind: string;
  languages: string[];
  setup_commands: string[];
  run_commands: string[];
  test_commands: string[];
  cleanup_commands: string[];
  requires_network: boolean;
  requires_api_key: boolean;
  estimated_minutes: number;
}

export interface LabBundle {
  dir: string;
  readme: string;
  metadata: LabMetadata | null;
  files: LabFile[];
  expectedOutput: { name: string; content: string }[];
  troubleshooting: string | null;
  security: string | null;
}

/**
 * Directories that live inside a lab while you work but are not part of it.
 *
 * A lab that needs a third-party package creates a lab-local `.venv`, which
 * is gitignored — but this walk reads from DISK, not from git, so without
 * this list the whole installed dependency tree was rendered into the lab
 * page. Day 093's page reached 53 MB, and the site publish then refused it
 * because SQLAlchemy's own bundled files contain the string "localhost".
 */
const NOT_PART_OF_THE_LAB = new Set([
  '.venv',
  'venv',
  '.env',
  '__pycache__',
  '.pytest_cache',
  '.mypy_cache',
  '.ruff_cache',
  'node_modules',
  '.git',
  '.DS_Store',
  'out',
  'workspace',
]);

function walk(dir: string, base: string, out: LabFile[]): void {
  for (const entry of readdirSync(dir)) {
    if (NOT_PART_OF_THE_LAB.has(entry)) continue;
    const full = path.join(dir, entry);
    const st = statSync(full);
    if (st.isDirectory()) {
      walk(full, base, out);
    } else if (!entry.endsWith('.pyc')) {
      out.push({ relPath: path.relative(base, full), size: st.size });
    }
  }
}

/** Reads a day's lab directory straight from disk — works fully offline. */
export function loadLab(day: DayContext): LabBundle | null {
  const dir = path.join(repoRoot, labPath(day));
  const readmePath = path.join(dir, 'README.md');
  if (!existsSync(readmePath)) return null;

  const files: LabFile[] = [];
  walk(dir, dir, files);
  files.sort((a, b) => a.relPath.localeCompare(b.relPath));

  const metaPath = path.join(dir, 'metadata.yml');
  const expectedDir = path.join(dir, 'expected-output');
  const expectedOutput: { name: string; content: string }[] = [];
  if (existsSync(expectedDir)) {
    for (const name of readdirSync(expectedDir).sort()) {
      const p = path.join(expectedDir, name);
      if (statSync(p).isFile()) expectedOutput.push({ name, content: readFileSync(p, 'utf8') });
    }
  }

  const maybeRead = (p: string) => (existsSync(p) ? readFileSync(p, 'utf8') : null);

  return {
    dir,
    readme: readFileSync(readmePath, 'utf8'),
    metadata: existsSync(metaPath)
      ? (yaml.load(readFileSync(metaPath, 'utf8')) as LabMetadata)
      : null,
    files,
    expectedOutput,
    troubleshooting: maybeRead(path.join(dir, 'troubleshooting.md')),
    security: maybeRead(path.join(dir, 'security.md')),
  };
}

/** Reads a source file inside a lab directory (for the file viewer). */
export function readLabFile(day: DayContext, relPath: string): string | null {
  const dir = path.join(repoRoot, labPath(day));
  const full = path.resolve(dir, relPath);
  if (!full.startsWith(dir + path.sep)) return null; // no path traversal
  return existsSync(full) ? readFileSync(full, 'utf8') : null;
}
