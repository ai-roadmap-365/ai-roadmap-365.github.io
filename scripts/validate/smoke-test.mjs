#!/usr/bin/env node
/**
 * Production-preview smoke test: serves the built site with `astro preview`
 * on a scratch port, fetches the key routes over real HTTP, and verifies
 * status 200 + expected content. Proves `npm run preview` actually works.
 */
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { allDays, loadConfig, repoRoot, makeReporter } from '../lib/course.mjs';

const r = makeReporter('preview:smoke-test');
const config = loadConfig();
const PORT = 43219; // scratch port so a running dev server is undisturbed
const base = `http://localhost:${PORT}${config.website.base_path}`;

if (!existsSync(path.join(repoRoot, 'dist'))) {
  r.fail('dist/ does not exist — run npm run build first');
  r.finish('');
}

const server = spawn('npx', ['astro', 'preview', '--port', String(PORT)], {
  cwd: repoRoot,
  stdio: 'ignore',
  detached: false,
});

async function fetchOk(url, marker, tag) {
  const res = await fetch(url);
  if (res.status !== 200) {
    r.fail(`${tag}: HTTP ${res.status} for ${url}`);
    return;
  }
  const text = await res.text();
  if (marker && !text.includes(marker))
    r.fail(`${tag}: response missing expected content "${marker}"`);
}

try {
  // Wait for the server to accept connections.
  let up = false;
  for (let i = 0; i < 40 && !up; i += 1) {
    try {
      await fetch(`${base}/`);
      up = true;
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 250));
    }
  }
  if (!up) {
    r.fail('preview server did not start within 10s');
  } else {
    await fetchOk(`${base}/`, '365 Days of AI Mastery', 'home');
    await fetchOk(`${base}/sections`, 'Courses', 'sections');
    await fetchOk(`${base}/search-index.json`, null, 'search index');
    const first = allDays().find((d) => d.hasContent);
    if (first) {
      await fetchOk(`${base}/${first.dayId}`, first.title, `day ${first.number}`);
      if (first.hasLab)
        await fetchOk(`${base}/labs/${first.dayId}`, 'File tree', `lab ${first.number}`);
    }
  }
} finally {
  server.kill('SIGTERM');
}

r.finish('production preview serves the site correctly over HTTP.');
