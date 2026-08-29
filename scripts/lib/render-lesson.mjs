/**
 * Renders a lesson (MDX source + sidecar YAML) into export HTML.
 * Used by scripts/release/wordpress-export logic and by the site's
 * /wordpress-preview route, so the preview is exactly what ships.
 *
 * In private mode, public links are emitted as data-attributed placeholder
 * anchors (requirements §12) that the public release pipeline resolves;
 * fake public URLs are never generated.
 */
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { renderMarkdown, stripFrontmatter } from './markdown.mjs';
import { getLessonUrl, dayId, lessonId } from './links.mjs';
import { labUsageHtml, lessonDuration } from './lab-usage.mjs';

function esc(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

const LETTERS = ['A', 'B', 'C', 'D', 'E', 'F'];

export function renderQuizHtml(quiz) {
  if (!quiz?.questions?.length) return '';
  const items = quiz.questions
    .map((q, i) => {
      const options = q.options.map((o) => `<li>${esc(o)}</li>`).join('');
      return (
        `<div class="quiz-question"><p><strong>Q${i + 1}. ${esc(q.question)}</strong></p>` +
        `<ol type="A">${options}</ol>` +
        `<details><summary>Show answer</summary>` +
        `<p><strong>Answer: ${LETTERS[q.answer_index]}.</strong> ${esc(q.options[q.answer_index])}</p>` +
        `<p>${esc(q.explanation)}</p></details></div>`
      );
    })
    .join('\n');
  return `<h2 id="quiz">Quiz</h2>\n${items}`;
}

export function renderGlossaryHtml(glossary) {
  if (!glossary?.terms?.length) return '';
  const items = glossary.terms
    .map((t) => `<dt><strong>${esc(t.term)}</strong></dt><dd>${esc(t.definition)}</dd>`)
    .join('\n');
  return `<h2 id="glossary">Glossary</h2>\n<dl>${items}</dl>`;
}

export function renderSourcesHtml(sources) {
  if (!sources?.sources?.length) return '';
  const items = sources.sources
    .map(
      (s) =>
        `<li><a href="${esc(s.url)}">${esc(s.title)}</a> — ${esc(s.publisher)} (accessed ${esc(s.accessed)})${s.note ? ` — ${esc(s.note)}` : ''}</li>`,
    )
    .join('\n');
  return `<h2 id="sources">Sources and further reading</h2>\n<ul>${items}</ul>`;
}

function navAnchor(config, day, label) {
  if (!day) return '';
  if (config.website.public_base_url) {
    return `<a href="${esc(getLessonUrl(config, day, 'public'))}">${esc(label)}</a>`;
  }
  return `<a data-link-type="public-lesson" data-lesson-id="${lessonId(day)}">${esc(label)} (link resolved during public release)</a>`;
}

/**
 * @param {object} args
 * @param {object} args.config course.config.yml contents
 * @param {object} args.day flattened day (scripts/lib/course.mjs shape)
 * @param {object} args.sidecars loadSidecars(day)
 * @param {object} [args.prev] previous day
 * @param {object} [args.next] next day
 */
export async function renderLessonArticle({ config, day, sidecars, prev, next }) {
  const mdx = readFileSync(path.join(day.contentDir, 'index.mdx'), 'utf8');
  const bodyHtml = await renderMarkdown(stripFrontmatter(mdx));
  const lesson = sidecars.lesson;

  const objectives = (lesson.objectives ?? []).map((o) => `<li>${esc(o)}</li>`).join('');
  const prerequisites = (lesson.prerequisites ?? []).map((p) => `<li>${esc(p)}</li>`).join('');

  // Full "how to use this lab" block (clone → open this lab → run), pointing
  // at the public labs repository. This is also emitted as a standalone
  // Lesson-materials file for the MasterStudy "Lesson materials" field.
  const labMaterialsHtml = labUsageHtml(config, day);

  const header = [
    `<p><em>${esc(lesson.learning_promise ?? '')}</em></p>`,
    `<table class="lesson-meta"><tbody>`,
    `<tr><th>Day</th><td>${day.number} of 365</td></tr>`,
    `<tr><th>Section</th><td>${esc(day.sectionTitle)}</td></tr>`,
    `<tr><th>Subsection</th><td>${esc(day.subsectionTitle)}</td></tr>`,
    `<tr><th>Week</th><td>Week ${day.week}: ${esc(day.weekTheme)}</td></tr>`,
    `<tr><th>Reading time</th><td>≈ ${esc(lesson.reading_time_minutes)} min</td></tr>`,
    `<tr><th>Practical time</th><td>≈ ${esc(lesson.practical_time_minutes)} min</td></tr>`,
    `<tr><th>Last verified</th><td>${esc(lesson.last_verified)}</td></tr>`,
    `</tbody></table>`,
    lesson.video_url
      ? `<p><strong><a href="${esc(lesson.video_url)}">▶ Watch the video for this lesson</a></strong></p>`
      : '',
    `<h2 id="learning-objectives">Learning objectives</h2><ul>${objectives}</ul>`,
    `<h2 id="prerequisites">Prerequisites</h2><ul>${prerequisites}</ul>`,
    labMaterialsHtml,
  ].join('\n');

  const footer = [
    renderQuizHtml(sidecars.quiz),
    renderGlossaryHtml(sidecars.glossary),
    renderSourcesHtml(sidecars.sources),
    `<nav class="prev-next"><span>${navAnchor(config, prev, prev ? `← Day ${prev.number}: ${prev.title}` : '')}</span>` +
      `<span>${navAnchor(config, next, next ? `Day ${next.number}: ${next.title} →` : '')}</span></nav>`,
  ].join('\n');

  const articleHtml = [
    `<article data-lesson-id="${lessonId(day)}">`,
    `<h1>Day ${day.number}: ${esc(day.title)}</h1>`,
    header,
    bodyHtml,
    footer,
    `</article>`,
  ].join('\n');

  // MasterStudy lesson body: content + lab materials + quiz (the LMS supplies
  // its own title, navigation, and metadata chrome). The lab how-to is
  // included so the lesson is self-contained even if the separate
  // Lesson-materials field is left empty.
  const masterstudyHtml = [
    bodyHtml,
    labMaterialsHtml,
    renderQuizHtml(sidecars.quiz),
    renderGlossaryHtml(sidecars.glossary),
  ].join('\n');

  // Discrete fields for the MasterStudy lesson form.
  const shortDescription = String(lesson.learning_promise ?? day.title);
  const duration = lessonDuration(sidecars);
  const masterstudy = {
    lesson_title: `${String(day.number).padStart(3, '0')} — ${day.title}`,
    lesson_duration: duration,
    short_description_html: `<p>${esc(shortDescription)}</p>`,
    lesson_materials_html: labMaterialsHtml,
  };

  const metadata = {
    lesson_id: lessonId(day),
    day: day.number,
    day_id: dayId(day),
    title: day.title,
    section: day.sectionTitle,
    section_slug: day.section,
    subsection: day.subsectionTitle,
    subsection_slug: day.subsection,
    week: day.week,
    week_theme: day.weekTheme,
    reading_time_minutes: lesson.reading_time_minutes ?? null,
    practical_time_minutes: lesson.practical_time_minutes ?? null,
    lesson_duration: duration,
    video_url: lesson.video_url ?? null,
    last_verified: lesson.last_verified ?? null,
    status: day.status,
    repository_mode: config.repository.mode,
  };

  const seo = {
    title: `Day ${day.number}: ${day.title} — 365 Days of AI`,
    description: String(lesson.learning_promise ?? day.title).slice(0, 155),
    keywords: lesson.tags ?? [],
    slug: dayId(day),
  };

  return {
    articleHtml,
    articleMd: stripFrontmatter(mdx),
    masterstudyHtml,
    masterstudy,
    metadata,
    seo,
  };
}
