#!/usr/bin/env node
/**
 * Source/citation validation: every authored lesson cites ≥3 real sources
 * with complete fields, https URLs, no known-fake domains, and no duplicates.
 */
import { allDays, loadSidecars, makeReporter } from '../lib/course.mjs';

const r = makeReporter('validate:sources');
const FAKE_DOMAINS = ['example.com', 'example.org', 'test.com', 'yourdomain.com', 'site.com'];

for (const d of allDays().filter((x) => x.hasContent)) {
  const tag = `day ${d.number}`;
  const sources = loadSidecars(d).sources?.sources ?? [];
  if (sources.length < 3) r.fail(`${tag}: only ${sources.length} sources (≥3 required)`);
  const seen = new Set();
  for (const s of sources) {
    for (const field of ['title', 'url', 'publisher', 'accessed']) {
      if (!s[field]) r.fail(`${tag}: source "${s.title ?? s.url ?? '?'}" missing ${field}`);
    }
    if (s.url && !s.url.startsWith('https://')) r.fail(`${tag}: non-https source URL ${s.url}`);
    if (s.url && FAKE_DOMAINS.some((f) => s.url.includes(f)))
      r.fail(`${tag}: fake source domain in ${s.url}`);
    if (s.url) {
      if (seen.has(s.url)) r.fail(`${tag}: duplicate source URL ${s.url}`);
      seen.add(s.url);
    }
    if (s.accessed && !/^\d{4}-\d{2}-\d{2}$/.test(String(s.accessed)))
      r.fail(`${tag}: source accessed date malformed (${s.accessed})`);
  }
}

r.finish('all authored lessons cite ≥3 well-formed, deduplicated https sources.');
