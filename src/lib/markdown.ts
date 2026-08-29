/**
 * Typed wrapper around the canonical markdown pipeline shared with the
 * release/export scripts (scripts/lib/markdown.mjs) so the lab browser,
 * WordPress preview, and exports all render identically.
 */
// @ts-ignore -- plain ESM module shared with the release pipeline
import {
  renderMarkdown as render,
  stripFrontmatter as strip,
} from '../../scripts/lib/markdown.mjs';

export const renderMarkdown: (markdown: string) => Promise<string> = render;
export const stripFrontmatter: (source: string) => string = strip;
