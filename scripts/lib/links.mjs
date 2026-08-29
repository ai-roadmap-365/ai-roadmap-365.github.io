/**
 * Central link generation (requirements §9, §11) — the single canonical
 * implementation, used by the Astro site via src/lib/links.ts and by every
 * validation/release script directly.
 *
 * Link modes: local | repo | public-preview | public.
 * Public URLs that are not configured yet are emitted as structured
 * placeholders — never fake links.
 */

export const PUBLIC_LINK_PLACEHOLDER = 'PUBLIC_LINK_PENDING';

export function dayId(lesson) {
  return `day-${String(lesson.number).padStart(3, '0')}-${lesson.slug}`;
}

export function lessonId(lesson) {
  return `D${String(lesson.number).padStart(3, '0')}`;
}

export function weekDir(lesson) {
  return `week-${String(lesson.week).padStart(2, '0')}`;
}

// Flat per-section layout (amendment A18): each section directly holds its
// day directories; subsection and week are grouping metadata only, never
// path segments.
export function lessonContentPath(lesson) {
  return `content/sections/${lesson.section}/${dayId(lesson)}`;
}

export function labPath(lesson) {
  return `labs/sections/${lesson.section}/${dayId(lesson)}`;
}

export function videoPath(lesson) {
  return `videos/sections/${lesson.section}/${dayId(lesson)}`;
}

export function projectPath(section, week) {
  return `labs/sections/${section}/projects/week-${String(week).padStart(2, '0')}`;
}

function requirePublic(config, what) {
  const url = what === 'site' ? config.website.public_base_url : config.repository.public_url;
  if (!url) {
    throw new Error(
      `Public ${what} URL is not configured in config/course.config.yml; ` +
        `public link mode is unavailable until the public release is set up.`,
    );
  }
  return url;
}

export function getLessonUrl(config, lesson, mode = 'local') {
  switch (mode) {
    case 'local':
      return `${config.website.local_base_url}/${dayId(lesson)}`;
    case 'repo':
      return `${config.repository.url}/tree/${config.repository.branch}/${lessonContentPath(lesson)}`;
    case 'public':
      return `${requirePublic(config, 'site')}/${dayId(lesson)}`;
    case 'public-preview':
      return config.website.public_base_url
        ? `${config.website.public_base_url}/${dayId(lesson)}`
        : `${PUBLIC_LINK_PLACEHOLDER}:lesson:${lessonId(lesson)}`;
    default:
      throw new Error(`Unknown link mode: ${mode}`);
  }
}

export function getLocalLabUrl(config, lesson) {
  return `${config.website.local_base_url}/labs/${dayId(lesson)}`;
}

export function getRepoLabUrl(config, lesson) {
  return `${config.repository.url}/tree/${config.repository.branch}/${labPath(lesson)}`;
}

/** Retained name: one repository now, so this is the same URL. */
export const getPublicRepoLabUrl = getRepoLabUrl;

/** The published blog URL for a day — the single place a lesson is read. */
export function getBlogUrl(config, lesson) {
  return `${config.website.public_base_url}/${dayId(lesson)}`;
}

export function publicPlaceholderAnchor(lesson, kind) {
  const label =
    kind === 'lab'
      ? 'Hands-on repository link will be resolved during public release'
      : 'Public lesson link will be resolved during public release';
  return `<a data-link-type="public-repository" data-link-kind="${kind}" data-lesson-id="${lessonId(lesson)}">${label}</a>`;
}
