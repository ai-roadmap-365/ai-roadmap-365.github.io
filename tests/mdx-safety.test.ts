import { describe, it, expect } from 'vitest';
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

/**
 * MDX treats `{` as the start of a JavaScript expression and `<` as the start
 * of a JSX tag. In a lesson body those characters usually arrive as ordinary
 * prose — set notation like {B, C, D}, or a comparison like x <= y — and the
 * result is a build failure a long way from the cause, or worse, a page that
 * renders an evaluated expression.
 *
 * Three real incidents motivated this file: a `$$...$$` block on Day 109 that
 * killed the whole 240-page build, `{B, C, D}` on Day 124 ("B is not defined"),
 * and `P(Z <= z)` on Day 118. None of the per-day validators catch any of them
 * — only the site build does, which is far too late and far too slow.
 *
 * Inline code spans and fenced blocks are exempt: MDX leaves both alone, and
 * wrapping the offending text in backticks is the correct fix.
 */

const CONTENT = new URL('../content/sections/', import.meta.url).pathname;

function lessonFiles(dir: string, found: string[] = []): string[] {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) lessonFiles(full, found);
    else if (entry === 'index.mdx') found.push(full);
  }
  return found;
}

/**
 * Body lines with fenced blocks removed and inline code spans blanked out.
 *
 * The blanking runs over the whole document rather than line by line: a first
 * attempt stripped spans per line and reported two false positives on Day 122,
 * where two adjacent spans on one line confused the match. MDX itself does not
 * care about line boundaries, so neither should this.
 */
function proseLines(src: string): { n: number; text: string }[] {
  // CommonMark fence rules, which a naive open/close toggle gets wrong. An
  // opening fence may carry an info string; a CLOSING fence may not, and must be
  // at least as long as the one it closes. So inside a ```markdown block, a
  // nested ```python line is content, not a close — and a toggle desynchronises
  // from there on, reporting the rest of the file as code.
  //
  // Day 139 shipped exactly that: a ```python fence inside a ```markdown fence.
  // This checker passed it and the site build failed on a dict literal 50 lines
  // later, because MDX had correctly decided that region was prose.
  let fence = 0; // 0 = outside, else the backtick count that opened the block
  const withoutFences = src.split('\n').map((raw) => {
    const m = raw.match(/^\s*(`{3,})(.*)$/);
    if (m) {
      const ticks = m[1].length;
      const info = m[2].trim();
      if (fence === 0) {
        fence = ticks;
        return '';
      }
      // Only a bare fence at least as long as the opener closes the block.
      if (info === '' && ticks >= fence) {
        fence = 0;
        return '';
      }
      return ''; // a nested opener: content, but never scanned as prose
    }
    return fence === 0 ? raw : '';
  });

  // Blank inline code spans across the whole document, preserving line count so
  // reported line numbers still point at the real source line.
  const blanked = withoutFences
    .join('\n')
    .replace(/`+[^`]*`+/g, (m) => m.replace(/[^\n]/g, ' '))
    .split('\n');

  return blanked.map((text, i) => ({ n: i + 1, text }));
}

describe('MDX safety in lesson bodies', () => {
  const files = lessonFiles(CONTENT);

  it('finds the lesson bodies', () => {
    expect(files.length).toBeGreaterThan(100);
  });

  it.each(files.map((f) => [f.slice(CONTENT.length), f]))(
    '%s has no unescaped MDX expression braces in prose',
    (_name, path) => {
      const offenders = proseLines(readFileSync(path as string, 'utf8'))
        .filter((l) => l.text.includes('{'))
        .map((l) => `line ${l.n}: ${l.text.trim().slice(0, 80)}`);
      expect(offenders, 'wrap these in backticks — MDX evaluates { } as JavaScript').toEqual([]);
    },
  );

  it.each(files.map((f) => [f.slice(CONTENT.length), f]))(
    '%s has no bare JSX-like angle brackets in prose',
    (_name, path) => {
      // `<` followed by whitespace or a digit is plain text to MDX ("p < 0.05").
      // `<=`, `<foo` and `</foo` are what start a tag and break the build.
      const offenders = proseLines(readFileSync(path as string, 'utf8'))
        .filter((l) => /<[=/A-Za-z]/.test(l.text))
        .map((l) => `line ${l.n}: ${l.text.trim().slice(0, 80)}`);
      expect(offenders, 'wrap these in backticks — MDX reads < as a JSX tag').toEqual([]);
    },
  );
});
