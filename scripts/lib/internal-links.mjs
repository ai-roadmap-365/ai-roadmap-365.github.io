/**
 * Deciding whether a link is this project's to resolve.
 *
 * This exists because of a real bug. The e2e validator used to decide with
 * `href.startsWith(basePath)` alone. That works while the site is served from
 * a sub-path, and stops working the moment it is served from the root: the
 * base becomes the empty string, EVERY string starts with the empty string,
 * and the guard silently passes every external link through to a filesystem
 * lookup. It reported 1,946 reachable URLs as dead.
 *
 * The lesson generalises: a prefix test against a configurable base is
 * vacuously true when that base can be empty. Decide externality on its own
 * terms first, and never let it depend on the base.
 */

/** Protocol-relative, http(s), and the non-navigational schemes. */
const EXTERNAL = /^(?:[a-z][a-z0-9+.-]*:)?\/\//i;
const NON_NAVIGATIONAL = /^(?:mailto|tel|sms|javascript|data):/i;

/** True when the href points somewhere this repository does not build. */
export function isExternalLink(href) {
  if (typeof href !== 'string') return true;
  const trimmed = href.trim();
  if (!trimmed) return true;
  return EXTERNAL.test(trimmed) || NON_NAVIGATIONAL.test(trimmed);
}

/**
 * The site-relative path an internal href points at, or null when the link is
 * external or outside the configured base.
 *
 * `basePath` may be '' (root site) or '/prefix'. Both are handled, and an
 * empty base never widens what counts as internal.
 */
export function internalPath(href, basePath = '') {
  if (isExternalLink(href)) return null;
  const withoutHash = href.split('#')[0];
  if (withoutHash === '') return null;
  if (basePath && !withoutHash.startsWith(basePath)) return null;
  // An in-page anchor ('#x') resolves to the page itself, not to a path.
  return withoutHash.slice(basePath.length) || '/';
}
