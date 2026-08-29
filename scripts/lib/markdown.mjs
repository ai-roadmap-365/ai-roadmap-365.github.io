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

const processor = unified()
  .use(remarkParse)
  .use(remarkGfm)
  .use(remarkRehype)
  .use(rehypeSlug)
  .use(rehypeOpenInNewTab)
  .use(rehypeStringify);

/** Strips YAML frontmatter from an MDX/markdown source string. */
export function stripFrontmatter(source) {
  return source.replace(/^---\n[\s\S]*?\n---\n/, '');
}

export async function renderMarkdown(markdown) {
  const file = await processor.process(markdown);
  return String(file);
}
