import { createBrowserClient } from "@supabase/ssr";

/**
 * Supabase client for use in Client Components. Session (access/refresh
 * tokens) is persisted via cookies, not a custom store, so the server
 * (Server Components, Server Actions, `proxy.ts`) can read the same
 * session on the next request.
 */
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  );
}
