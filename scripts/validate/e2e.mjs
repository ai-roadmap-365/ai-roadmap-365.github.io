#!/usr/bin/env node
/**
 * End-to-end checks over the built site (dist/): the required pages exist,
 * parse, carry real content, and internal navigation resolves to files that
 * are actually in the build. Run after `npm run build`.
 */
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import * as cheerio from 'cheerio';
import { allDays, loadConfig, repoRoot, makeReporter } from '../lib/course.mjs';

const r = makeReporter('test:e2e');
const config = loadConfig();
const dist = path.join(repoRoot, 'dist');
const basePath = config.website.base_path; // e.g. /courses/ai-roadmap

if (!existsSync(dist)) {
  r.fail('dist/ does not exist — run npm run build first');
}

function pageFile(route) {
  // Astro emits the build at dist/ root; the base path exists only in URLs.
  const rel = route.replace(/^\//, '').replace(/\/$/, '');
  return path.join(dist, rel === '' ? 'index.html' : `${rel}/index.html`);
}

function loadPage(route, tag) {
  const file = pageFile(route);
  if (!existsSync(file)) {
    r.fail(`${tag}: page not built (${route})`);
    return null;
  }
  const $ = cheerio.load(readFileSync(file, 'utf8'));
  if ($('main').length !== 1) r.fail(`${tag}: no single <main> landmark`);
  if (!$('title').text()) r.fail(`${tag}: empty <title>`);
  return $;
}

if (existsSync(dist)) {
  const days = allDays();
  const authored = days.filter((d) => d.hasContent);

  const home = loadPage('', 'home');
  if (home && !home('body').text().includes('365 Days of AI')) r.fail('home: missing course title');

  loadPage('/sections', 'sections');
  loadPage('/search', 'search');
  loadPage('/glossary', 'glossary');
  loadPage('/progress', 'progress');
  loadPage('/admin/status', 'admin dashboard');
  for (const c of ['tools', 'frameworks', 'models', 'projects', 'free-open-source'])
    loadPage(`/catalog/${c}`, `catalog ${c}`);
  // Section pages group days under category headings (flat structure, A18/A19).
  for (const sectionSlug of new Set(days.map((d) => d.section))) {
    const $ = loadPage(`/sections/${sectionSlug}`, `section ${sectionSlug}`);
    if ($ && !/Days \d+-\d+ ·/.test($('body').text()))
      r.fail(`section ${sectionSlug}: page has no category headings`);
  }

  const searchIndex = path.join(dist, 'search-index.json');
  if (!existsSync(searchIndex)) r.fail('search index not built');
  else if (JSON.parse(readFileSync(searchIndex, 'utf8')).length !== authored.length)
    r.fail('search index entry count != authored lesson count');

  for (const d of authored) {
    const $ = loadPage(`/${d.dayId}`, `day ${d.number}`);
    if ($) {
      const text = $('body').text();
      if (!text.includes(d.title)) r.fail(`day ${d.number}: page missing lesson title`);
      if (!text.includes('Learning objectives'))
        r.fail(`day ${d.number}: page missing objectives section`);
      if (!text.includes('Quiz')) r.fail(`day ${d.number}: page missing quiz`);
      // Every internal link on the page must resolve to a built file.
      $('a[href]').each((_, el) => {
        const href = $(el).attr('href');
        if (!href.startsWith(basePath)) return;
        const clean = href.split('#')[0].slice(basePath.length) || '/';
        if (clean.endsWith('.json') || clean.endsWith('.svg') || /\.\w{2,4}$/.test(clean)) {
          if (!existsSync(path.join(dist, clean.replace(/^\//, ''))))
            r.fail(`day ${d.number}: dead asset link ${href}`);
        } else if (!existsSync(pageFile(clean))) {
          r.fail(`day ${d.number}: dead internal link ${href}`);
        }
      });
    }
    if (d.hasLab) {
      const lab = loadPage(`/labs/${d.dayId}`, `lab ${d.number}`);
      if (lab) {
        const text = lab('body').text();
        for (const marker of ['File tree', 'Expected output', 'Commands']) {
          if (!text.includes(marker)) r.fail(`lab ${d.number}: page missing "${marker}"`);
        }
      }
    }
  }
}

r.finish('built site passes end-to-end page, content, and internal-link checks.');
