#!/usr/bin/env node
/**
 * Offline build (requirements §8): produces a self-contained static copy of
 * the entire site under dist/offline/ plus a zero-dependency local server
 * script, so the whole course reads offline. Reuses the standard build when
 * present (verify:all runs `astro build` immediately before this).
 */
import { spawnSync } from 'node:child_process';
import { cpSync, existsSync, rmSync, mkdirSync, writeFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import { repoRoot } from './lib/course.mjs';

const dist = path.join(repoRoot, 'dist');
const offline = path.join(dist, 'offline');

const needsBuild = !existsSync(dist) || !readdirSync(dist).some((f) => f !== 'offline');
if (needsBuild || process.argv.includes('--fresh')) {
  const res = spawnSync('npx', ['astro', 'build'], { cwd: repoRoot, stdio: 'inherit' });
  if (res.status !== 0) process.exit(res.status ?? 1);
}

rmSync(offline, { recursive: true, force: true });
mkdirSync(offline, { recursive: true });

for (const entry of readdirSync(dist)) {
  if (entry === 'offline') continue;
  cpSync(path.join(dist, entry), path.join(offline, entry), { recursive: true });
}

// A dependency-free static server so the offline copy is fully self-contained.
writeFileSync(
  path.join(offline, 'serve.mjs'),
  `#!/usr/bin/env node
// Serves this offline build: node serve.mjs  → http://localhost:4321/courses/ai-roadmap
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { existsSync, statSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.txt': 'text/plain' };

createServer(async (req, res) => {
  let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  let file = path.join(root, p);
  if (existsSync(file) && statSync(file).isDirectory()) file = path.join(file, 'index.html');
  if (!existsSync(file)) file = path.join(root, 'courses/ai-roadmap/404/index.html');
  try {
    const body = await readFile(file);
    res.writeHead(200, { 'Content-Type': types[path.extname(file)] ?? 'application/octet-stream' });
    res.end(body);
  } catch {
    res.writeHead(404).end('not found');
  }
}).listen(4321, () => console.log('Offline course at http://localhost:4321/courses/ai-roadmap'));
`,
);

writeFileSync(
  path.join(offline, 'README.md'),
  `# Offline build — 365 Days of AI

Self-contained static copy of the complete private course website.

## Read it

\`\`\`bash
node serve.mjs
# then open http://localhost:4321/courses/ai-roadmap
\`\`\`

Only Node.js is required — no npm install, no network, no database, no API
key. Search, navigation, lessons, lab pages, glossary, and catalogs all work
offline. External resources (videos, third-party sites) are labelled in the
lessons and are the only things that need internet.
`,
);

console.log(
  `✓ build:offline: self-contained site written to ${path.relative(repoRoot, offline)} (serve with: node dist/offline/serve.mjs)`,
);
