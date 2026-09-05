"use client";

import Link from "next/link";
import { useActionState } from "react";
import { login, type AuthFormState } from "./actions";

const initialState: AuthFormState = undefined;

export default function LoginPage() {
  const [state, formAction, pending] = useActionState(login, initialState);

  return (
    <main className="mx-auto flex max-w-sm flex-col gap-6 p-8">
      <h1 className="text-2xl font-semibold">Log in</h1>
      <form action={formAction} className="flex flex-col gap-4" noValidate>
        <div className="flex flex-col gap-1">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            required
            autoComplete="email"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            required
            autoComplete="current-password"
          />
        </div>
        {state?.error && (
          <p role="alert" className="text-red-600">
            {state.error}
          </p>
        )}
        <button type="submit" disabled={pending}>
          {pending ? "Logging in…" : "Log in"}
        </button>
      </form>
      <p>
        Don&apos;t have an account? <Link href="/signup">Sign up</Link>
      </p>
    </main>
  );
}
