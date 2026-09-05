import { NextResponse, type NextRequest } from "next/server";
import { updateSession } from "@/lib/supabase/middleware";
import { decideRedirect } from "@/lib/route-guard";

// `middleware.ts` was renamed to `proxy.ts` in Next.js 16; behavior is
// unchanged. See node_modules/next/dist/docs/.../proxy.md.
export async function proxy(request: NextRequest) {
  const { supabaseResponse, user } = await updateSession(request);

  const pathname = request.nextUrl.pathname;
  const redirectTarget = decideRedirect(pathname, user !== null);

  if (redirectTarget) {
    const url = request.nextUrl.clone();
    url.pathname = redirectTarget;
    url.search = "";
    if (redirectTarget === "/login") {
      url.searchParams.set("redirectTo", pathname);
    }
    return NextResponse.redirect(url);
  }

  return supabaseResponse;
}

export const config = {
  matcher: [
    // Run on everything except static assets and image optimization,
    // so auth cookies stay in sync on real navigations without blocking
    // CSS/JS/image loads.
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
