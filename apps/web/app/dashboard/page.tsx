import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { logout } from "@/app/logout/actions";

// `proxy.ts` already redirects logged-out visitors away from this route.
// This second check is defense-in-depth per the Next.js auth guide
// (layouts/proxy alone are not a sufficient security boundary — check
// close to the data/page too).
export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  return (
    <main className="mx-auto flex max-w-sm flex-col gap-6 p-8">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <p>Signed in as {user.email}</p>
      <form action={logout}>
        <button type="submit">Log out</button>
      </form>
    </main>
  );
}
