import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

/**
 * Typed request helper for calling the FastAPI backend from Client
 * Components. Every future client-side feature should go through this
 * (rather than a raw `fetch`) so auth, errors, and timeouts are handled
 * in one place.
 *
 * Not for Server Components / Server Actions — those need a different
 * way of attaching the auth token server-side (tracked in issue #38).
 */

const REQUEST_TIMEOUT_MS = 10_000;

export type ApiErrorKind =
  /** Non-2xx, non-401 response (403/404/500/etc.). */
  | "http"
  /** `fetch` itself threw — the backend is unreachable (connection
   * refused, DNS failure, offline, ...). */
  | "network"
  /** The request didn't complete within `REQUEST_TIMEOUT_MS`. */
  | "timeout"
  /** The response body did not parse as JSON. */
  | "invalid-json";

/**
 * Every failure mode `apiFetch` can produce that ISN'T the 401 -> /login
 * redirect (that case navigates away instead of rejecting in a way
 * callers observe). Call sites should catch this specific type to render
 * a visible error state — see the dashboard's `ApiProfile` component for
 * the expected pattern:
 *
 * ```ts
 * try {
 *   const data = await apiFetch<T>("/some-path");
 *   // ... use data
 * } catch (err) {
 *   if (err instanceof ApiError) {
 *     // render a visible error state from err.message
 *     return;
 *   }
 *   // Not an ApiError — e.g. the `redirect()` this module throws on a
 *   // 401 to send the browser to /login. Re-throw so Next.js's router
 *   // can catch it; swallowing it here would silently break the
 *   // redirect.
 *   throw err;
 * }
 * ```
 */
export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status?: number;

  constructor(kind: ApiErrorKind, message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.kind = kind;
    this.status = status;
  }
}

function apiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
}

/**
 * Call the backend at `path` (relative to `NEXT_PUBLIC_API_BASE_URL`),
 * attaching the current Supabase session's access token as a Bearer
 * token. Callers never read, store, or pass the token themselves.
 *
 * - A 401 response redirects the browser to /login and does not resolve
 *   or reject in a way callers can observe (see `ApiError` doc above).
 * - Every other failure (non-2xx/non-401 response, network failure,
 *   10s timeout, unparseable JSON body) rejects with an `ApiError`.
 */
export async function apiFetch<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  const headers = new Headers(init.headers);
  if (session?.access_token) {
    headers.set("Authorization", `Bearer ${session.access_token}`);
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}${path}`, {
      ...init,
      headers,
      signal: controller.signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiError("timeout", "The request took too long to respond.");
    }
    throw new ApiError("network", "Could not reach the server.");
  } finally {
    clearTimeout(timeoutId);
  }

  if (response.status === 401) {
    // Deliberately not caught by our own try/catch above, and not
    // wrapped in an ApiError: this needs to propagate to Next.js's
    // router (see the `ApiError` doc comment for how callers must
    // avoid swallowing it).
    redirect("/login");
  }

  if (!response.ok) {
    throw new ApiError(
      "http",
      `Request failed with status ${response.status}.`,
      response.status
    );
  }

  try {
    return (await response.json()) as T;
  } catch {
    throw new ApiError(
      "invalid-json",
      "The server response could not be parsed."
    );
  }
}
