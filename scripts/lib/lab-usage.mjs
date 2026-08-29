/**
 * Generates the detailed, student-facing "how to use this lab" content for a
 * day — from cloning the public repository to running that specific lab —
 * plus the lesson-duration string. Used by the lesson page, the WordPress/
 * MasterStudy export, and the "Lesson materials" export block, so every
 * surface shows identical, correct instructions.
 *
 * The lab link always points at the PUBLIC repository (config public_url)
 * when configured — never the private one — so students need no
 * authentication and the private repo is never revealed (amendment A10).
 */
import { getPublicRepoLabUrl, labPath } from './links.mjs';

/** "1h 10m" style duration from reading + practical minutes. */
export function lessonDuration(sidecars) {
  const total =
    Number(sidecars.lesson?.reading_time_minutes ?? 0) +
    Number(sidecars.lesson?.practical_time_minutes ?? 0);
  if (!total) return '';
  const h = Math.floor(total / 60);
  const m = total % 60;
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

/** The public GitHub URL for this day's lab (or null if unconfigured). */
export function labRepoUrl(config, day) {
  const url = getPublicRepoLabUrl(config, day);
  return url.startsWith('http') ? url : null;
}

/**
 * Ordered how-to-use steps as {title, body, code?} objects, so each surface
 * can render them in its own markup. Beginner-complete: clone once, then
 * open this specific lab, then run it.
 */
export function labUsageSteps(config, day) {
  const repoUrl = labRepoUrl(config, day);
  const rel = labPath(day);
  const steps = [];

  if (repoUrl) {
    steps.push({
      title: 'Get the hands-on files',
      body: 'Clone the labs repository once (you can reuse this clone for every lesson). This works on macOS, Linux, and Windows (PowerShell or WSL):',
      code: `git clone ${config.repository.public_url}.git\ncd ${config.repository.public_name}`,
    });
    steps.push({
      title: `Open this lesson's lab`,
      body: 'Move into the directory for this specific day. Every lab lives at the same predictable path — section / subsection / week / day:',
      code: `cd ${rel}`,
    });
  } else {
    steps.push({
      title: 'Get the hands-on files',
      body: `The lab for this lesson lives in the course labs repository at \`${rel}\`. Download or clone the repository, then open that directory.`,
      code: `cd ${rel}`,
    });
  }

  steps.push({
    title: 'Read the lab guide',
    body: `Open \`README.md\` in that directory. It lists the exact commands, what each does, the expected output, and how to check your work — read it before running anything.`,
  });
  steps.push({
    title: 'Run it and check your work',
    body: 'Follow the README\'s "How to run" section: run the example first to see the finished result, then complete the numbered exercises in `starter/`, then run the tests. The tests pass (exit 0) only when your work is correct.',
    code: 'bash tests/run_tests.sh   # or the test command named in the lab README',
  });

  return { repoUrl, rel, steps };
}

/** Renders the how-to-use steps as a self-contained HTML block (for exports). */
export function labUsageHtml(config, day) {
  const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const { repoUrl, steps } = labUsageSteps(config, day);
  const parts = ['<div class="lab-materials">'];
  parts.push('<h3>Hands-on lab for this lesson</h3>');
  if (repoUrl) {
    parts.push(
      `<p><strong>Lab files on GitHub:</strong> <a href="${esc(repoUrl)}">${esc(repoUrl)}</a></p>`,
    );
  }
  parts.push('<ol>');
  for (const s of steps) {
    parts.push(`<li><strong>${esc(s.title)}.</strong> ${esc(s.body)}`);
    if (s.code) parts.push(`<pre><code>${esc(s.code)}</code></pre>`);
    parts.push('</li>');
  }
  parts.push('</ol></div>');
  return parts.join('\n');
}

/** Renders the how-to-use steps as Markdown (for lesson bodies / READMEs). */
export function labUsageMarkdown(config, day) {
  const { repoUrl, steps } = labUsageSteps(config, day);
  const lines = ['### Hands-on lab for this lesson', ''];
  if (repoUrl) lines.push(`**Lab files on GitHub:** ${repoUrl}`, '');
  steps.forEach((s, i) => {
    lines.push(`${i + 1}. **${s.title}.** ${s.body}`);
    if (s.code) lines.push('', '   ```bash', ...s.code.split('\n').map((l) => `   ${l}`), '   ```');
    lines.push('');
  });
  return lines.join('\n');
}
