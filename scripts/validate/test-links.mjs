#!/usr/bin/env node
/**
 * Link-mode tests (requirements §11): `npm run test:links -- --mode <m>`
 * exercises link generation for all 365 days in the requested mode and
 * asserts the mode's invariants. `--mode all` runs every mode.
 */
import { allDays, loadConfig, argValue, makeReporter } from '../lib/course.mjs';
import {
  getLessonUrl,
  getLocalLabUrl,
  getRepoLabUrl,
  getBlogUrl,
  PUBLIC_LINK_PLACEHOLDER,
} from '../lib/links.mjs';

const MODES = ['local', 'repo', 'public-preview', 'public'];
const requested = argValue(['--mode']) ?? 'all';
const modes = requested === 'all' ? MODES : [requested];
if (!modes.every((m) => MODES.includes(m))) {
  console.error(`Unknown mode "${requested}". Valid: ${MODES.join(', ')} or all.`);
  process.exit(1);
}

const r = makeReporter(`test:links (${modes.join(', ')})`);
const config = loadConfig();
const days = allDays();

for (const mode of modes) {
  for (const d of days) {
    const tag = `mode ${mode}, day ${d.number}`;
    switch (mode) {
      case 'local': {
        const url = getLessonUrl(config, d, 'local');
        if (!url.startsWith(config.website.local_base_url))
          r.fail(`${tag}: lesson URL not under local base`);
        if (!url.endsWith(d.dayId)) r.fail(`${tag}: lesson URL missing day id`);
        if (getLocalLabUrl(config, d) !== `${config.website.local_base_url}/labs/${d.dayId}`)
          r.fail(`${tag}: lab URL malformed`);
        break;
      }
      case 'repo': {
        const url = getLessonUrl(config, d, 'repo');
        if (!url.startsWith(`${config.repository.url}/tree/${config.repository.branch}/content/`))
          r.fail(`${tag}: repository lesson-source URL malformed`);
        if (!getRepoLabUrl(config, d).includes('/labs/sections/'))
          r.fail(`${tag}: repository lab URL malformed`);
        break;
      }
      case 'public-preview': {
        const lesson = getLessonUrl(config, d, 'public-preview');
        if (config.website.public_base_url) {
          if (!lesson.startsWith(config.website.public_base_url))
            r.fail(`${tag}: preview lesson URL malformed`);
        } else if (!lesson.startsWith(PUBLIC_LINK_PLACEHOLDER)) {
          r.fail(`${tag}: expected placeholder while public site unconfigured`);
        }
        break;
      }
      case 'public': {
        // The blog URL and the lab URL are the two links every day must have,
        // and they must point at each other's half of the same repository.
        const lab = getRepoLabUrl(config, d);
        if (!lab.startsWith(`${config.repository.url}/tree/`)) r.fail(`${tag}: lab URL malformed`);
        const blog = getBlogUrl(config, d);
        if (blog !== `${config.website.public_base_url}/${d.dayId}`)
          r.fail(`${tag}: blog URL malformed`);
        if (getLessonUrl(config, d, 'public') !== blog)
          r.fail(`${tag}: public lesson URL and blog URL disagree`);
        break;
      }
    }
  }
}

r.finish(`${modes.length} mode(s) × 365 days of link generation verified.`);
