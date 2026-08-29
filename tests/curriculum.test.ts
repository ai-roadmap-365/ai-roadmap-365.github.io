import { describe, it, expect } from 'vitest';
// @ts-ignore -- plain-ESM course access shared with scripts
import { allDays, loadCurriculum, loadConfig } from '../scripts/lib/course.mjs';

describe('curriculum manifest', () => {
  const days = allDays() as { number: number; slug: string; week: number; dayId: string }[];

  it('contains exactly 365 sequentially numbered days across 52 weeks', () => {
    expect(days).toHaveLength(365);
    days.forEach((d, i) => expect(d.number).toBe(i + 1));
    expect(new Set(days.map((d) => d.week)).size).toBe(52);
  });

  it('has globally unique day slugs and dayIds', () => {
    expect(new Set(days.map((d) => d.slug)).size).toBe(365);
    expect(new Set(days.map((d) => d.dayId)).size).toBe(365);
  });

  it('gives every week 7 days except week 52 which absorbs day 365', () => {
    const byWeek = new Map<number, number>();
    for (const d of days) byWeek.set(d.week, (byWeek.get(d.week) ?? 0) + 1);
    for (const [week, count] of byWeek) {
      expect(count, `week ${week}`).toBe(week === 52 ? 8 : 7);
    }
  });

  it('defines a titled project with a real summary for every week', () => {
    const curriculum = loadCurriculum() as {
      sections: {
        subsections: { weeks: { number: number; project: { title: string; summary: string } }[] }[];
      }[];
    };
    const weeks = curriculum.sections.flatMap((s) => s.subsections.flatMap((b) => b.weeks));
    expect(weeks).toHaveLength(52);
    for (const w of weeks) {
      expect(w.project.title.length).toBeGreaterThan(3);
      expect(w.project.summary.length).toBeGreaterThan(40);
    }
  });

  it('keeps course config and curriculum in agreement', () => {
    const config = loadConfig() as { course: { days: number; weeks: number } };
    expect(config.course.days).toBe(365);
    expect(config.course.weeks).toBe(52);
  });
});
