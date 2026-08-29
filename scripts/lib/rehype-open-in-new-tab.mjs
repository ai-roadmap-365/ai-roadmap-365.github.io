/**
 * Open links inside written content in a new tab, so a reader following a
 * reference does not lose the lesson they were part-way through.
 *
 * This applies to links the AUTHOR wrote inside a lesson or a lab README — a
 * citation, a tool's documentation, a cross-reference to another day. It does
 * NOT apply to the site's own navigation: the previous/next lesson links, the
 * header, the breadcrumbs and the lab callout are Astro components rather
 * than markdown, so they never pass through this plugin and continue to
 * navigate in place, which is what you want when you are deliberately moving
 * on to the next lesson.
 *
 * `rel="noopener noreferrer"` is not optional with `target="_blank"`: without
 * `noopener` the opened page gets a handle on this one through `window.opener`
 * and can navigate it somewhere else.
 *
 * In-page anchors (`#section`) are deliberately left alone — opening a jump to
 * a heading in a new tab would be absurd.
 *
 * No dependency: this is a ten-line tree walk, and rehype-external-links would
 * be a package to install, audit and keep current for the same result.
 */

/** Walk every node in a hast tree, depth first. */
function walk(node, visit) {
  visit(node);
  for (const child of node.children ?? []) walk(child, visit);
}

export function rehypeOpenInNewTab() {
  return (tree) => {
    walk(tree, (node) => {
      if (node.type !== 'element' || node.tagName !== 'a') return;
      const href = node.properties?.href;
      if (typeof href !== 'string' || href.startsWith('#')) return;
      node.properties.target = '_blank';
      node.properties.rel = 'noopener noreferrer';
    });
  };
}

export default rehypeOpenInNewTab;
