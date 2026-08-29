import { describe, it, expect } from 'vitest';
// @ts-ignore -- canonical markdown pipeline shared with the release scripts
import { renderMarkdown, stripFrontmatter } from '../scripts/lib/markdown.mjs';

describe('markdown pipeline', () => {
  it('renders headings with stable slug ids', async () => {
    const html = await renderMarkdown('## Why this matters\n\ntext');
    expect(html).toContain('<h2 id="why-this-matters">Why this matters</h2>');
  });

  it('renders GFM tables', async () => {
    const html = await renderMarkdown('| a | b |\n| - | - |\n| 1 | 2 |');
    expect(html).toContain('<table>');
    expect(html).toContain('<td>1</td>');
  });

  it('renders fenced code blocks with language classes', async () => {
    const html = await renderMarkdown('```bash\necho hi\n```');
    expect(html).toContain('<code class="language-bash">');
  });

  it('strips YAML frontmatter exactly once', () => {
    const src = '---\nday: 1\ntitle: x\n---\n# Body\n\n---\n\nrule stays';
    const out = stripFrontmatter(src);
    expect(out.startsWith('# Body')).toBe(true);
    expect(out).toContain('rule stays');
  });
});
