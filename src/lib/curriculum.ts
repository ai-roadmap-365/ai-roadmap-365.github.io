import { readFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';
import { repoRoot } from './config';
import { lessonContentPath, labPath, dayId, type LessonRef } from './links';

export interface CurriculumDay {
  id: string;
  number: number;
  slug: string;
  title: string;
}

export interface CurriculumWeek {
  id: string;
  number: number;
  theme: string;
  project: { title: string; summary: string };
  days: CurriculumDay[];
}

export interface CurriculumSubsection {
  id: string;
  slug: string;
  title: string;
  summary: string;
  weeks: CurriculumWeek[];
}

export interface CurriculumSection {
  id: string;
  slug: string;
  title: string;
  summary: string;
  subsections: CurriculumSubsection[];
}

export interface Curriculum {
  course: {
    title: string;
    slug: string;
    days: number;
    weeks: number;
    sections: number;
  };
  sections: CurriculumSection[];
}

/** A day flattened with its full hierarchy context. */
export interface DayContext extends LessonRef {
  id: string;
  title: string;
  sectionTitle: string;
  subsectionTitle: string;
  weekTheme: string;
  /** e.g. day-001-how-a-computer-works-from-transistors */
  dayId: string;
  hasContent: boolean;
  hasLab: boolean;
  status: DayStatus;
}

export type DayStatus = 'planned' | 'draft' | 'in-review' | 'complete';

export interface ProgressEntry {
  status: DayStatus;
  completion?: Record<string, boolean>;
}

let cachedCurriculum: Curriculum | null = null;
let cachedDays: DayContext[] | null = null;
let cachedProgress: Record<number, ProgressEntry> | null = null;

export function loadCurriculum(): Curriculum {
  if (!cachedCurriculum) {
    const raw = readFileSync(path.join(repoRoot, 'curriculum', 'curriculum.yml'), 'utf8');
    cachedCurriculum = yaml.load(raw) as Curriculum;
  }
  return cachedCurriculum;
}

export function loadProgress(): Record<number, ProgressEntry> {
  if (!cachedProgress) {
    const file = path.join(repoRoot, 'curriculum', 'progress.yml');
    const doc = (existsSync(file) ? yaml.load(readFileSync(file, 'utf8')) : {}) as {
      days?: Record<number, ProgressEntry>;
    };
    cachedProgress = doc?.days ?? {};
  }
  return cachedProgress;
}

/** All 365 days flattened, each with hierarchy context and on-disk state. */
export function allDays(): DayContext[] {
  if (cachedDays) return cachedDays;
  const curriculum = loadCurriculum();
  const progress = loadProgress();
  const days: DayContext[] = [];
  for (const section of curriculum.sections) {
    for (const sub of section.subsections) {
      for (const week of sub.weeks) {
        for (const day of week.days) {
          const ref: LessonRef = {
            number: day.number,
            slug: day.slug,
            section: section.slug,
            subsection: sub.slug,
            week: week.number,
          };
          const contentDir = path.join(repoRoot, lessonContentPath(ref));
          const labDir = path.join(repoRoot, labPath(ref));
          days.push({
            ...ref,
            id: day.id,
            title: day.title,
            sectionTitle: section.title,
            subsectionTitle: sub.title,
            weekTheme: week.theme,
            dayId: dayId(ref),
            hasContent: existsSync(path.join(contentDir, 'index.mdx')),
            hasLab: existsSync(path.join(labDir, 'README.md')),
            status: progress[day.number]?.status ?? 'planned',
          });
        }
      }
    }
  }
  cachedDays = days;
  return days;
}

export function getDay(number: number): DayContext | undefined {
  return allDays().find((d) => d.number === number);
}

/** Days that have authored content on disk (routable). */
export function authoredDays(): DayContext[] {
  return allDays().filter((d) => d.hasContent);
}

export function prevNext(number: number): { prev?: DayContext; next?: DayContext } {
  const days = allDays();
  return {
    prev: days.find((d) => d.number === number - 1),
    next: days.find((d) => d.number === number + 1),
  };
}

export interface LessonSidecars {
  lesson: Record<string, unknown>;
  quiz: { questions: QuizQuestion[] } | null;
  glossary: { terms: { term: string; definition: string }[] } | null;
  sources: { sources: SourceEntry[] } | null;
  visuals: { visuals: VisualEntry[] } | null;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  answer_index: number;
  explanation: string;
}

export interface SourceEntry {
  title: string;
  url: string;
  publisher: string;
  accessed: string;
  note?: string;
}

export interface VisualEntry {
  id: string;
  file: string;
  type: string;
  title: string;
  alt: string;
  description: string;
}

function loadYamlIfExists<T>(file: string): T | null {
  return existsSync(file) ? (yaml.load(readFileSync(file, 'utf8')) as T) : null;
}

/** Loads the sidecar YAML files for an authored day. */
export function loadSidecars(day: DayContext): LessonSidecars {
  const dir = path.join(repoRoot, lessonContentPath(day));
  return {
    lesson: loadYamlIfExists<Record<string, unknown>>(path.join(dir, 'lesson.yml')) ?? {},
    quiz: loadYamlIfExists(path.join(dir, 'quiz.yml')),
    glossary: loadYamlIfExists(path.join(dir, 'glossary.yml')),
    sources: loadYamlIfExists(path.join(dir, 'sources.yml')),
    visuals: loadYamlIfExists(path.join(dir, 'visuals.yml')),
  };
}
