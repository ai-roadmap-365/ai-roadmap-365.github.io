#!/usr/bin/env node
/** Convenience wrapper: serve the offline build produced by build:offline. */
import { existsSync } from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { repoRoot } from './lib/course.mjs';

const server = path.join(repoRoot, 'dist', 'offline', 'serve.mjs');
if (!existsSync(server)) {
  console.error('No offline build found — run: npm run build:offline');
  process.exit(1);
}
spawn('node', [server], { stdio: 'inherit' });
