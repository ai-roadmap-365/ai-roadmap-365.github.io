#!/usr/bin/env node
/**
 * Accessibility checks over every built HTML page: lang attribute, single
 * h1, no skipped heading levels, alt text on all images, labelled inputs,
 * landmarks, and non-empty link text.
 */
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import * as cheerio from 'cheerio';
import { repoRoot, makeReporter } from '../lib/course.mjs';

const r = makeReporter('test:accessibility');
const dist = path.join(repoRoot, 'dist');

if (!existsSync(dist)) r.fail('dist/ does not exist — run npm run build first');

// offline/ is a byte copy of the site pages already scanned.
const SKIP = new Set(['offline']);

function* htmlFiles(dir, depth = 0) {
  for (const entry of readdirSync(dir)) {
    if (depth === 0 && SKIP.has(entry)) continue;
    const full = path.join(dir, entry);
    if (statSync(full).isDirectory()) yield* htmlFiles(full, depth + 1);
    else if (entry.endsWith('.html')) yield full;
  }
}

let pages = 0;
if (existsSync(dist)) {
  for (const file of htmlFiles(dist)) {
    pages += 1;
    const rel = path.relative(dist, file);
    const $ = cheerio.load(readFileSync(file, 'utf8'));

    if (!$('html').attr('lang')) r.fail(`${rel}: <html> missing lang`);
    if ($('h1').length !== 1) r.fail(`${rel}: expected exactly one h1, found ${$('h1').length}`);

    let prev = 1;
    $('h1, h2, h3, h4, h5, h6').each((_, el) => {
      const level = Number(el.tagName[1]);
      if (level > prev + 1) r.fail(`${rel}: heading level skips from h${prev} to h${level}`);
      prev = level;
    });

    $('img').each((_, el) => {
      if ($(el).attr('alt') === undefined)
        r.fail(`${rel}: <img src="${$(el).attr('src')}"> missing alt`);
    });

    $('a[href]').each((_, el) => {
      const text = $(el).text().trim() || $(el).attr('aria-label');
      if (!text) r.fail(`${rel}: link with empty accessible text (${$(el).attr('href')})`);
    });

    $('input:not([type=hidden]):not([type=checkbox][disabled]), select, textarea').each((_, el) => {
      const id = $(el).attr('id');
      const labelled =
        (id && $(`label[for="${id}"]`).length > 0) ||
        $(el).parents('label').length > 0 ||
        $(el).attr('aria-label');
      if (!labelled) r.fail(`${rel}: form control without label`);
    });

    for (const landmark of ['header', 'main', 'footer']) {
      if ($(landmark).length === 0) r.fail(`${rel}: missing <${landmark}> landmark`);
    }
  }
}

r.finish(`${pages} built pages pass structural accessibility checks.`);
