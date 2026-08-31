/**
 * The single canonical markdown → HTML pipeline. Used by the Astro site
 * (via src/lib/markdown.ts) and by the WordPress/release export scripts,
 * so lab pages, previews, and exports render identically.
 */
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import remarkRehype from 'remark-rehype';
import rehypeSlug from 'rehype-slug';
import rehypeStringify from 'rehype-stringify';
import { rehypeOpenInNewTab } from './rehype-open-in-new-tab.mjs';
import { rehypeResolveRelativeLinks } from './rehype-resolve-relative-links.mjs';

const processor = unified()
  .use(remarkParse)
  .use(remarkGfm)
  .use(remarkRehype)
  .use(rehypeSlug)
  .use(rehypeOpenInNewTab)
  .use(rehypeStringify);

/**
 * A second pipeline that also resolves relative file links against a base URL.
 * Built per call because the base differs per page; the plain `processor`
 * above is kept so existing single-argument callers are unaffected.
 */
function processorWithBase(base) {
  return unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkRehype)
    .use(rehypeSlug)
    .use(rehypeResolveRelativeLinks, { base })
    .use(rehypeOpenInNewTab)
    .use(rehypeStringify);
}

/** Strips YAML frontmatter from an MDX/markdown source string. */
export function stripFrontmatter(source) {
  return source.replace(/^---\n[\s\S]*?\n---\n/, '');
}

export async function renderMarkdown(markdown, options = {}) {
  const engine = options.relativeBase ? processorWithBase(options.relativeBase) : processor;
  const file = await engine.process(markdown);
  return String(file);
}
