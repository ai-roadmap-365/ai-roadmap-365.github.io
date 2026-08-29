import { describe, it, expect } from 'vitest';
// @ts-ignore -- canonical plain-ESM implementation under test
import * as links from '../scripts/lib/links.mjs';
import * as wrapper from '../src/lib/links';

const lesson = {
  number: 1,
  slug: 'how-a-computer-works-from-transistors',
  section: 'computing-foundations',
  subsection: 'how-computers-work',
  week: 1,
};

// One repository, everything public (A31). `public_*` are retained aliases of
// the canonical name/url/branch and must resolve to the same single repo.
const baseConfig = {
  repository: {
    mode: 'public',
    owner: 'sandeepbazar',
    name: 'ai-roadmap-365',
    url: 'https://github.com/sandeepbazar/ai-roadmap-365',
    branch: 'main',
    public_name: 'ai-roadmap-365',
    public_url: 'https://github.com/sandeepbazar/ai-roadmap-365',
    public_branch: 'main',
    site_branch: 'site',
  },
  website: {
    local_base_url: 'http://localhost:4321/ai-roadmap-365',
    public_base_url: 'https://sandeepbazar.github.io/ai-roadmap-365',
    base_path: '/ai-roadmap-365',
    port: 4321,
  },
} as never;

const noSiteConfig = {
  ...(baseConfig as object),
  website: { ...(baseConfig as { website: object }).website, public_base_url: null },
} as never;

describe('link mode: local', () => {
  it('builds lesson and lab URLs under the local base', () => {
    expect(links.getLessonUrl(baseConfig, lesson, 'local')).toBe(
      'http://localhost:4321/ai-roadmap-365/day-001-how-a-computer-works-from-transistors',
    );
    expect(links.getLocalLabUrl(baseConfig, lesson)).toBe(
      'http://localhost:4321/ai-roadmap-365/labs/day-001-how-a-computer-works-from-transistors',
    );
  });
});

describe('link mode: repo', () => {
  it('builds GitHub tree URLs into the one repository', () => {
    expect(links.getRepoLabUrl(baseConfig, lesson)).toBe(
      'https://github.com/sandeepbazar/ai-roadmap-365/tree/main/labs/sections/computing-foundations/day-001-how-a-computer-works-from-transistors',
    );
    expect(links.getLessonUrl(baseConfig, lesson, 'repo')).toContain(
      '/tree/main/content/sections/',
    );
  });

  it('keeps getPublicRepoLabUrl as an alias of the same URL', () => {
    expect(links.getPublicRepoLabUrl(baseConfig, lesson)).toBe(
      links.getRepoLabUrl(baseConfig, lesson),
    );
  });
});

describe('the two links every day must have', () => {
  it('points the blog URL at the site and the lab URL at the repository', () => {
    expect(links.getBlogUrl(baseConfig, lesson)).toBe(
      'https://sandeepbazar.github.io/ai-roadmap-365/day-001-how-a-computer-works-from-transistors',
    );
    expect(links.getLessonUrl(baseConfig, lesson, 'public')).toBe(
      links.getBlogUrl(baseConfig, lesson),
    );
    expect(links.getRepoLabUrl(baseConfig, lesson)).toContain('/labs/sections/');
  });

  it('refuses a public lesson URL rather than inventing one when the site is unconfigured', () => {
    expect(() => links.getLessonUrl(noSiteConfig, lesson, 'public')).toThrow(/not configured/);
  });

  it('emits a structured placeholder — never a fake URL — for an unconfigured preview', () => {
    expect(links.getLessonUrl(noSiteConfig, lesson, 'public-preview')).toBe(
      'PUBLIC_LINK_PENDING:lesson:D001',
    );
  });
});

describe('placeholder anchors', () => {
  it('carries the sanctioned data attributes for later resolution', () => {
    const anchor = links.publicPlaceholderAnchor(lesson, 'lab');
    expect(anchor).toContain('data-link-type="public-repository"');
    expect(anchor).toContain('data-lesson-id="D001"');
    expect(anchor).not.toContain('href=');
  });
});

describe('TS wrapper and canonical implementation agree', () => {
  it('produces identical URLs through both entry points', () => {
    expect(wrapper.getLessonUrl(baseConfig, lesson, 'local')).toBe(
      links.getLessonUrl(baseConfig, lesson, 'local'),
    );
    expect(wrapper.getRepoLabUrl(baseConfig, lesson)).toBe(links.getRepoLabUrl(baseConfig, lesson));
    expect(wrapper.getBlogUrl(baseConfig, lesson)).toBe(links.getBlogUrl(baseConfig, lesson));
    expect(wrapper.labPath(lesson)).toBe(links.labPath(lesson));
  });
});
