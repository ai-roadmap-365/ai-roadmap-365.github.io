/**
 * Typed wrapper over the canonical link-generation module shared with the
 * validation/release scripts (scripts/lib/links.mjs). Requirements §9, §11:
 * all lesson/lab/export URLs come from these helpers plus
 * config/course.config.yml — nothing else hard-codes repository URLs.
 */
import type { CourseConfig } from './config';
// @ts-ignore -- plain ESM module shared with the release pipeline
import * as impl from '../../scripts/lib/links.mjs';

export type LinkMode = 'local' | 'repo' | 'public-preview' | 'public';

export interface LessonRef {
  /** 1-based day number */
  number: number;
  /** slug portion, e.g. "how-a-computer-works-from-transistors" */
  slug: string;
  section: string;
  subsection: string;
  /** 1-based week number */
  week: number;
}

export const PUBLIC_LINK_PLACEHOLDER: string = impl.PUBLIC_LINK_PLACEHOLDER;

export const dayId: (lesson: LessonRef) => string = impl.dayId;
export const lessonId: (lesson: LessonRef) => string = impl.lessonId;
export const weekDir: (lesson: LessonRef) => string = impl.weekDir;
export const lessonContentPath: (lesson: LessonRef) => string = impl.lessonContentPath;
export const labPath: (lesson: LessonRef) => string = impl.labPath;
export const getLessonUrl: (config: CourseConfig, lesson: LessonRef, mode?: LinkMode) => string =
  impl.getLessonUrl;
export const getLocalLabUrl: (config: CourseConfig, lesson: LessonRef) => string =
  impl.getLocalLabUrl;
export const getRepoLabUrl: (config: CourseConfig, lesson: LessonRef) => string =
  impl.getRepoLabUrl;
/** Retained name: one repository now, so this is the same URL. */
export const getPublicRepoLabUrl: (config: CourseConfig, lesson: LessonRef) => string =
  impl.getPublicRepoLabUrl;
export const getBlogUrl: (config: CourseConfig, lesson: LessonRef) => string = impl.getBlogUrl;
export const publicPlaceholderAnchor: (lesson: LessonRef, kind: 'lesson' | 'lab') => string =
  impl.publicPlaceholderAnchor;
