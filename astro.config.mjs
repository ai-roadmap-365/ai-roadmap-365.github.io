// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import { rehypeOpenInNewTab } from './scripts/lib/rehype-open-in-new-tab.mjs';

// Base path and port are fixed by config/course.config.yml (website section).
// They are duplicated here as literals because Astro needs them before any
// app code runs; scripts/validate/curriculum.mjs asserts they stay in sync.
export default defineConfig({
  site: 'https://ai-roadmap-365.github.io',
  base: '',
  trailingSlash: 'ignore',
  integrations: [mdx()],
  // Links an author wrote inside a lesson open in a new tab so the reader
  // keeps their place; the site's own prev/next navigation is a component,
  // not markdown, so it still navigates in place.
  markdown: { rehypePlugins: [rehypeOpenInNewTab] },
  server: { port: 4321 },
  build: { format: 'directory' },
});
