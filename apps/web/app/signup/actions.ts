"use server";

import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";

export type AuthFormState = { error: string } | undefined;

export async function signup(
  _prevState: AuthFormState,
  formData: FormData,
): Promise<AuthFormState> {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");

  if (!email || !password) {
    return { error: "Email and password are required." };
  }
  if (password.length < 6) {
    return { error: "Password must be at least 6 characters." };
  }

  const supabase = await createClient();
  const { error } = await supabase.auth.signUp({ email, password });

  if (error) {
    return { error: error.message };
  }

  // Note: if the Supabase project has "Confirm email" enabled (the
  // default), signUp() does not return an active session until the user
  // clicks the confirmation link, so this redirect will land on a
  // /dashboard the proxy immediately bounces back to /login. Email
  // verification is explicitly out of scope for this issue; disable
  // "Confirm email" in the Supabase Auth settings for the MVP flow
  // described here (signup -> immediately logged in).
  redirect("/dashboard");
}
