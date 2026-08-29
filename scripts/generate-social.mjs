#!/usr/bin/env node
/**
 * Generates the daily social-media pack for the #365DaysOfAI challenge.
 *
 * Per authored day, into social-media/day-NNN-<slug>/:
 *   post.md    — the LinkedIn post, ready to copy and paste
 *   post.html  — the same post as a share-and-schedule page, carrying the
 *                Open Graph tags that decide what a shared link previews as
 *
 * Plus social-media/README.md — the whole schedule in one table, so a year of
 * posts can be queued in one sitting, and dist/social-manifest.json, which
 * scripts/generate_hero_images.py reads to draw each day's hero image.
 *
 * There is no separate share card. The image a shared link shows IS the
 * lesson page's own first image, so the two can never disagree.
 *
 * Every fact in a post comes from the day's own lesson.yml, quiz.yml and lab
 * metadata. Nothing is invented here: if a day has no lesson, it gets no post.
 *
 * Usage:
 *   node scripts/generate-social.mjs              # every authored day
 *   node scripts/generate-social.mjs --day 85     # one day
 */
import { writeFileSync, mkdirSync, existsSync } from 'node:fs';
import path from 'node:path';
import { allDays, loadConfig, loadCurriculum, argValue, loadYamlIfExists } from './lib/course.mjs';

const repoRoot = process.cwd();
const config = loadConfig();
const curriculum = loadCurriculum();
const site = config.website.public_base_url;
const repo = config.repository.url;
const social = config.social ?? {};
const challenge = social.challenge_name ?? '365 Days of AI';
const hashtags = social.hashtags ?? ['AI', '365DaysOfAI'];

const only = argValue(['--day']);
const days = allDays().filter((d) => d.hasContent && (!only || d.number === Number(only)));
if (days.length === 0) {
  console.error(only ? `Day ${only} has no lesson written yet.` : 'No authored days.');
  process.exit(1);
}

const esc = (s) =>
  String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

/** Each course gets its own colour, so a year of posts reads as a set. */
const COURSE_STYLE = {
  'computing-foundations': { a: '#38bdf8' },
  'programming-with-python': { a: '#818cf8' },
  'math-statistics-and-data': { a: '#f472b6' },
  'machine-learning': { a: '#4ade80' },
  'deep-learning': { a: '#fbbf24' },
  'llms-and-generative-ai': { a: '#a78bfa' },
  'ai-engineering': { a: '#22d3ee' },
  'deployment-mlops-and-security': { a: '#fb7185' },
  capstone: { a: '#facc15' },
};

/**
 * The share image is the day's OWN hero image - the first image on the lesson
 * page - not a separate card. Sharing the blog link is the normal case, and
 * a crawler picks up the page's og:image, so one file does both jobs and the
 * thumbnail can never disagree with the page it represents.
 */
const heroPath = (d) => `social/${d.dayId}.png`;
const heroUrl = (d) => `${site}/${heroPath(d)}`;

function post(d, lesson, labMeta) {
  const url = `${site}/${d.dayId}`;
  const labUrl = `${repo}/tree/${config.repository.branch}/labs/sections/${d.section}/${d.dayId}`;
  const objectives = (lesson.objectives ?? []).slice(0, 3);
  const promise = String(lesson.learning_promise ?? '').replace(
    /^After this lesson you will be able to /i,
    '',
  );
  const first = promise.split(/[;.]/)[0].trim();
  const course = curriculum.sections.find((s) => s.slug === d.section);
  const minutes = (lesson.reading_time_minutes ?? 0) + (lesson.practical_time_minutes ?? 0);
  const tags = hashtags.map((h) => `#${h}`).join(' ');

  const lines = [
    `Day ${d.number} of ${challenge} — ${d.title}`,
    // The second line carries the context every post needs for a reader who
    // has never seen one before: what the series is and where it goes.
    `Part of my 365-day AI challenge — from foundations to production, one lesson and one hands-on lab every single day.`,
    '',
    `${first.charAt(0).toUpperCase()}${first.slice(1)}.`,
    '',
    'What today covers:',
    ...objectives.map((o) => `→ ${String(o).split(/[,—]/)[0].trim()}`),
    '',
  ];

  if (labMeta) {
    lines.push(
      `The lab is the point: ${labMeta.estimated_minutes ?? 30} minutes of hands-on work you run yourself, offline, with output you can check against a real captured run.`,
      '',
    );
  }

  // LINK ORDER MATTERS AND IS NOT COSMETIC. LinkedIn builds the preview card
  // from the LAST link in the post, so the lesson URL goes last — that is the
  // one with the branded Day N / 365 hero as its og:image. Putting the lab
  // link last would preview a GitHub directory listing instead.
  lines.push(
    `🧪 Lab: ${labUrl}`,
    `📖 Lesson (~${minutes} min): ${url}`,
    '',
    `Course ${course.id.replace('Course', '')} of 9 · ${course.title}`,
    '',
    'Free and no prerequisites beyond curiosity.',
    '',
    tags,
  );
  return lines.join('\n');
}

function postHtml(d, lesson, body, style) {
  const url = `${site}/${d.dayId}`;
  const cardUrl = heroUrl(d);
  const desc = String(lesson.learning_promise ?? d.title).slice(0, 300);
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Day ${d.number} / 365 — ${esc(d.title)}</title>
<meta name="description" content="${esc(desc)}">

<!-- These tags decide what LinkedIn shows when the link is shared. -->
<meta property="og:type" content="article">
<meta property="og:title" content="Day ${d.number} / 365 — ${esc(d.title)}">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${url}">
<meta property="og:image" content="${cardUrl}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="${esc(config.course.title)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Day ${d.number} / 365 — ${esc(d.title)}">
<meta name="twitter:description" content="${esc(desc)}">
<meta name="twitter:image" content="${cardUrl}">

<style>
  :root { color-scheme: dark; }
  body { margin:0; background:#0b1220; color:#e2e8f0;
         font-family: system-ui, -apple-system, "Segoe UI", sans-serif; line-height:1.6; }
  .wrap { max-width: 780px; margin: 0 auto; padding: 40px 20px 80px; }
  .badge { display:inline-block; padding:6px 16px; border-radius:999px;
           background:${style.a}22; color:${style.a}; font-weight:800; letter-spacing:1px; font-size:14px; }
  h1 { font-size: clamp(28px, 5vw, 44px); line-height:1.15; margin:18px 0 6px; color:#f8fafc; }
  .sub { color:#94a3b8; margin:0 0 28px; }
  img.card { width:100%; border-radius:14px; border:1px solid #1e293b; display:block; margin:24px 0; }
  .actions a { display:inline-block; margin:0 10px 10px 0; padding:11px 20px; border-radius:10px;
               text-decoration:none; font-weight:700; }
  .primary { background:${style.a}; color:#0b1220; }
  .ghost { border:1px solid #334155; color:#cbd5e1; }
  h2 { font-size:15px; text-transform:uppercase; letter-spacing:2px; color:#64748b;
       margin:40px 0 10px; }
  pre { background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:20px;
        white-space:pre-wrap; word-wrap:break-word; font-size:15px; color:#e2e8f0;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  button { background:${style.a}; color:#0b1220; border:0; border-radius:10px; padding:11px 20px;
           font-weight:700; font-size:15px; cursor:pointer; }
  footer { margin-top:48px; color:#475569; font-size:14px; border-top:1px solid #1e293b; padding-top:20px; }
  a { color:${style.a}; }
</style>
</head>
<body>
<div class="wrap">
  <span class="badge">DAY ${d.number} / 365</span>
  <h1>${esc(d.title)}</h1>
  <p class="sub">${esc(String(lesson.learning_promise ?? '').slice(0, 240))}</p>

  <img class="card" src="${cardUrl}" alt="Day ${d.number} of 365: ${esc(d.title)} — the lesson's hero image, which is also what a shared link shows">

  <div class="actions">
    <a class="primary" href="${url}">Read the lesson</a>
    <a class="ghost" href="${repo}/tree/${config.repository.branch}/labs/sections/${d.section}/${d.dayId}">Open the lab</a>
  </div>

  <h2>The post — copy and paste</h2>
  <pre id="post">${esc(body)}</pre>
  <button onclick="navigator.clipboard.writeText(document.getElementById('post').innerText).then(()=>{this.textContent='Copied';setTimeout(()=>this.textContent='Copy post',1600)})">Copy post</button>

  <footer>
    ${esc(challenge)} · ${esc(config.course.title)} ·
    <a href="${site}">${esc(site.replace('https://', ''))}</a>
  </footer>
</div>
</body>
</html>
`;
}

let written = 0;
const index = [];
for (const d of days) {
  const lesson = loadYamlIfExists(path.join(d.contentDir, 'lesson.yml')) ?? {};
  const labMeta = existsSync(path.join(d.labDir, 'metadata.yml'))
    ? loadYamlIfExists(path.join(d.labDir, 'metadata.yml'))
    : null;
  const style = COURSE_STYLE[d.section] ?? COURSE_STYLE['computing-foundations'];
  const dir = path.join(repoRoot, 'social-media', d.dayId);
  mkdirSync(dir, { recursive: true });

  const body = post(d, lesson, labMeta);
  writeFileSync(path.join(dir, 'post.md'), `${body}\n`);
  writeFileSync(path.join(dir, 'post.html'), postHtml(d, lesson, body, style));
  index.push({ d, lesson });
  written += 1;
}

// The schedule: one row per day, so a year of posts can be queued in a sitting.
const rows = index
  .map(
    ({ d }) =>
      `| ${d.number} | [${d.title}](${d.dayId}/post.md) | [image](../public/${heroPath(d)}) | [page](${d.dayId}/post.html) | [blog](${site}/${d.dayId}) |`,
  )
  .join('\n');

writeFileSync(
  path.join(repoRoot, 'social-media', 'README.md'),
  `# ${challenge} — the daily posts

> GENERATED — do not edit by hand. Run \`npm run generate:social\`.

One ready-to-paste post per published day. Everything here is built from the
day's own \`lesson.yml\` and lab metadata, so a post cannot claim something the
lesson does not teach.

## How to use it

1. Open the day's \`post.html\` (or \`post.md\`) and copy the text.
2. Paste it into LinkedIn **with the blog link**. You do not need to attach an
   image: the lesson page's first image is its branded hero — carrying
   \`Day N / 365\` and the challenge name — and it is declared as the page's
   \`og:image\`, so LinkedIn picks it up automatically from the link.
3. Schedule it for that calendar day.

The post already contains the lesson link and the lab link, so a reader can go
straight from the feed to the material.

If you ever want the image as a file — for a carousel, or a platform that does
not read \`og:image\` — it is \`public/social/day-NNN-<slug>.png\` at
1200×630.

**${written} of 365 days ready.**

| Day | Post | Image | Page | Blog |
| --- | --- | --- | --- | --- |
${rows}
`,
);

// The manifest the hero-image drawer reads. Kept as generated output rather
// than a committed file: it is derived entirely from the lessons.
const manifest = {
  challenge,
  site,
  days: index.map(({ d, lesson }) => ({
    number: d.number,
    dayId: d.dayId,
    title: d.title,
    section: d.section,
    course_title: curriculum.sections.find((s) => s.slug === d.section).title,
    promise: String(lesson.learning_promise ?? ''),
  })),
};
mkdirSync(path.join(repoRoot, 'dist'), { recursive: true });
writeFileSync(
  path.join(repoRoot, 'dist', 'social-manifest.json'),
  `${JSON.stringify(manifest, null, 2)}\n`,
);

console.log(
  `✓ generate:social: ${written} day pack(s) under social-media/ + dist/social-manifest.json` +
    ` (draw the hero images with: python3 scripts/generate_hero_images.py)`,
);
