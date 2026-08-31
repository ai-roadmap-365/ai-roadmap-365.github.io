/**
 * Rewrite relative links in rendered markdown to absolute repository URLs.
 *
 * A lab's README says `see security.md` and `expected-output/FIELDS.md`. Those
 * are correct relative to the file on disk and meaningless once the markdown is
 * rendered at /labs/day-330-docker-fundamentals — the browser resolves them
 * against the PAGE, producing /labs/security.md, which does not exist.
 *
 * A site-wide crawl found 90 links of this shape. Rather than strip them, point
 * them at the file in the repository, where the reader can actually open it.
 */
import { visit } from 'unist-util-visit';

const ABSOLUTE = /^(?:[a-z][a-z0-9+.-]*:|\/\/|\/|#)/i;

export function rehypeResolveRelativeLinks(options = {}) {
  const base = (options.base || '').replace(/\/$/, '');
  return (tree) => {
    if (!base) return;
    visit(tree, 'element', (node) => {
      for (const attr of ['href', 'src']) {
        const value = node.properties?.[attr];
        if (typeof value !== 'string' || !value || ABSOLUTE.test(value)) continue;
        const [pathPart, hash] = value.split('#');
        const cleaned = pathPart.replace(/^\.\//, '');
        // A bare "./" is the lab README's "everything you need is in this
        // directory" link. It means the lab folder, so point at the folder --
        // left alone it resolves against the page and yields /labs/.
        const suffix = cleaned ? `/${cleaned}` : '';
        node.properties[attr] = `${base}${suffix}${hash ? `#${hash}` : ''}`;
      }
    });
  };
}
