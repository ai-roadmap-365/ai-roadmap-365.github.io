import { describe, it, expect } from 'vitest';

// @ts-expect-error - plain .mjs helper, no type declarations
import { isExternalLink, internalPath } from '../scripts/lib/internal-links.mjs';

/**
 * These tests exist because of a real defect, not for coverage.
 *
 * The e2e validator decided "is this link mine to resolve?" with
 * `href.startsWith(basePath)`. When the site moved from /ai-roadmap-365 to the
 * root, basePath became '' — and every string starts with the empty string, so
 * the guard passed every external link through to a filesystem lookup and
 * reported 1,946 reachable URLs as dead.
 *
 * The root-site cases below are the ones that would have caught it.
 */
describe('deciding which links this project is responsible for', () => {
  const external = [
    'https://github.com/ai-roadmap-365/ai-roadmap-365.github.io',
    'http://example.com/page',
    '//cdn.example.com/asset.js',
    'mailto:someone@example.com',
    'tel:+10000000000',
  ];

  it('treats external links as external at EVERY base, empty included', () => {
    for (const href of external) {
      expect(isExternalLink(href), href).toBe(true);
      // The regression: with an empty base these all used to look internal.
      expect(internalPath(href, ''), href).toBeNull();
      expect(internalPath(href, '/ai-roadmap-365'), href).toBeNull();
    }
  });

  it('resolves internal links against a root base', () => {
    expect(internalPath('/sections', '')).toBe('/sections');
    expect(internalPath('/day-001-a-day', '')).toBe('/day-001-a-day');
    expect(internalPath('/', '')).toBe('/');
    expect(internalPath('/page#anchor', '')).toBe('/page');
  });

  it('resolves internal links against a sub-path base', () => {
    expect(internalPath('/prefix/sections', '/prefix')).toBe('/sections');
    expect(internalPath('/prefix', '/prefix')).toBe('/');
    // Outside the configured base is not ours to resolve.
    expect(internalPath('/elsewhere/page', '/prefix')).toBeNull();
  });

  it('never treats a bare in-page anchor as a path', () => {
    expect(internalPath('#main', '')).toBeNull();
    expect(internalPath('#main', '/prefix')).toBeNull();
  });

  it('refuses malformed input rather than guessing', () => {
    expect(isExternalLink(undefined)).toBe(true);
    expect(isExternalLink('')).toBe(true);
    expect(internalPath('   ', '')).toBeNull();
  });
});
