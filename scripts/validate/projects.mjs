#!/usr/bin/env node
/**
 * Project validation: every week defines a real project in the curriculum;
 * weeks whose seven days are all complete must ship a project directory in
 * labs/ (README with expected output + validation) and an instructor
 * solution. Authored-but-incomplete weeks are tracked by audit:coverage.
 */
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { allDays, loadCurriculum, repoRoot, makeReporter } from '../lib/course.mjs';

const r = makeReporter('validate:projects');

// The instructor tree is PRIVATE (A31) and is not synced to the public
// repository, so its absence is a property of where this checkout is, not a
// defect. Where it exists it is checked as strictly as before; where it does
// not, the checks that depend on it are skipped and said to be skipped rather
// than silently passing.
const hasInstructorTree = existsSync(path.join(repoRoot, 'instructor'));
const curriculum = loadCurriculum();
const days = allDays();

for (const section of curriculum.sections) {
  for (const sub of section.subsections) {
    for (const week of sub.weeks) {
      if (!week.project?.title || (week.project.summary ?? '').length < 40)
        r.fail(`week ${week.number}: project missing or summary too thin to be real`);

      const weekDays = days.filter((d) => d.week === week.number);
      const allComplete = weekDays.every((d) => d.status === 'complete');
      if (!allComplete) continue;

      // Flat layout (A18): weekly projects live at
      // labs/sections/<section>/projects/week-NN/ and mirror in instructor/.
      const wk = `week-${String(week.number).padStart(2, '0')}`;
      const readme = path.join(
        repoRoot,
        'labs',
        'sections',
        section.slug,
        'projects',
        wk,
        'README.md',
      );
      if (!existsSync(readme)) {
        r.fail(
          `week ${week.number}: all days complete but no project at ${path.relative(repoRoot, readme)}`,
        );
        continue;
      }
      const text = readFileSync(readme, 'utf8');
      for (const h of ['## Expected output', '## Validation']) {
        if (!text.includes(h)) r.fail(`week ${week.number}: project README missing "${h}"`);
      }
      const solution = path.join(
        repoRoot,
        'instructor',
        'project-solutions',
        'sections',
        section.slug,
        'projects',
        wk,
      );
      if (hasInstructorTree && !existsSync(solution))
        r.fail(`week ${week.number}: no instructor solution directory for the project`);
    }
  }
}

// Instructor solutions must exist for every complete day — where the private
// instructor tree is present at all.
for (const d of hasInstructorTree ? days.filter((x) => x.status === 'complete') : []) {
  const dir = path.join(
    repoRoot,
    'instructor',
    'project-solutions',
    'sections',
    d.section,
    d.dayId,
  );
  if (!existsSync(dir))
    r.fail(`day ${d.number}: marked complete but has no instructor solution directory`);
}

r.finish(
  hasInstructorTree
    ? 'all 52 weekly projects are defined; completed weeks/days carry projects and instructor solutions.'
    : 'all 52 weekly projects are defined; instructor-solution checks skipped (private tree not in this checkout).',
);
