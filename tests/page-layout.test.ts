import { describe, it, expect } from 'vitest';
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

/**
 * Every page must sit on the shared page axis (`--page-w` in global.css), which
 * leaves roughly 10% of the viewport free on each side and lines the content up
 * with the header and the footer.
 *
 * A page opts in one of three ways:
 *   - `<article>`      a lesson (`main > article` is styled)
 *   - `.readable`      any ordinary page body
 *   - `.wrap`          the landing page's full-bleed bands
 *
 * Seven pages were shipped without any of them and rendered flush against the
 * left edge of the window while lesson pages were correctly inset. The symptom
 * is invisible in every per-day validator — it only shows up in a browser — so
 * it is asserted here instead.
 */

const PAGES_DIR = new URL('../src/pages/', import.meta.url).pathname;

function astroPages(dir: string, found: string[] = []): string[] {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) astroPages(full, found);
    else if (entry.endsWith('.astro')) found.push(full);
  }
  return found;
}

describe('page layout', () => {
  const pages = astroPages(PAGES_DIR);

  it('finds the site pages', () => {
    expect(pages.length).toBeGreaterThan(5);
  });

  it.each(pages.map((p) => [p.slice(PAGES_DIR.length), p]))(
    '%s puts its body on the shared page axis',
    (_name, path) => {
      const src = readFileSync(path as string, 'utf8');
      const optsIn =
        /<article[\s>]/.test(src) ||
        /class="[^"]*\breadable\b/.test(src) ||
        /class="[^"]*\bwrap\b/.test(src);
      expect(optsIn).toBe(true);
    },
  );

  it('defines the page axis exactly once, so overriding it moves everything together', () => {
    const css = readFileSync(new URL('../src/styles/global.css', import.meta.url).pathname, 'utf8');
    const definitions = css.match(/--page-w:/g) ?? [];
    // One base definition plus the narrow-screen override.
    expect(definitions.length).toBe(2);
    expect(css).toMatch(/main > article,\s*\nmain > \.readable \{\s*\n\s*width: var\(--page-w\)/);
  });

  it('keeps the header and footer on the same axis as the page body', () => {
    const css = readFileSync(new URL('../src/styles/global.css', import.meta.url).pathname, 'utf8');
    expect(css).toContain('padding-inline: max(16px, calc((100% - var(--page-w)) / 2));');
    expect(css).toMatch(/\.site-footer \.inner \{\s*\n\s*width: var\(--page-w\)/);
  });
});
