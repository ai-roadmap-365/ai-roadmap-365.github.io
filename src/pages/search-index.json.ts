/**
 * Build-time search index consumed by /search. Plain JSON + client-side
 * scoring so search works fully offline with no external service.
 */
import { readFileSync } from 'node:fs';
import path from 'node:path';
import type { APIRoute } from 'astro';
import { authoredDays, loadSidecars } from '../lib/curriculum';
import { lessonContentPath } from '../lib/links';
import { stripFrontmatter } from '../lib/markdown';
import { repoRoot } from '../lib/config';

function plainText(markdown: string): string {
  return stripFrontmatter(markdown)
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/[#>*_`|[\]()-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

export const GET: APIRoute = () => {
  const index = authoredDays().map((day) => {
    const mdx = readFileSync(path.join(repoRoot, lessonContentPath(day), 'index.mdx'), 'utf8');
    const sidecars = loadSidecars(day);
    const terms = sidecars.glossary?.terms.map((t) => t.term).join(' ') ?? '';
    return {
      day: day.number,
      dayId: day.dayId,
      title: day.title,
      section: day.sectionTitle,
      week: day.week,
      text: `${terms} ${plainText(mdx)}`.slice(0, 4000).toLowerCase(),
    };
  });
  return new Response(JSON.stringify(index), {
    headers: { 'Content-Type': 'application/json' },
  });
};
