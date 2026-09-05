/**
 * Pure route-protection rules, kept separate from `proxy.ts` so they can
 * be unit tested without a real Next.js request/response or a Supabase
 * client.
 */

const PROTECTED_PREFIXES = ["/dashboard"];
const AUTH_ROUTES = ["/login", "/signup"];

export function isProtectedPath(pathname: string): boolean {
  return PROTECTED_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`),
  );
}

export function isAuthRoute(pathname: string): boolean {
  return AUTH_ROUTES.includes(pathname);
}

/**
 * Decide whether a request should be redirected, given its path and
 * whether the caller is logged in.
 *
 * - Logged-out user hitting a protected route -> redirect to /login.
 * - Logged-in user hitting /login or /signup -> redirect to /dashboard.
 * - Otherwise -> no redirect (returns null).
 */
export function decideRedirect(
  pathname: string,
  isLoggedIn: boolean,
): string | null {
  if (isProtectedPath(pathname) && !isLoggedIn) {
    return "/login";
  }
  if (isAuthRoute(pathname) && isLoggedIn) {
    return "/dashboard";
  }
  return null;
}
