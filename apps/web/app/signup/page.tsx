"use client";

import Link from "next/link";
import { useActionState } from "react";
import { signup, type AuthFormState } from "./actions";

const initialState: AuthFormState = undefined;

export default function SignupPage() {
  const [state, formAction, pending] = useActionState(signup, initialState);

  return (
    <main className="mx-auto flex max-w-sm flex-col gap-6 p-8">
      <h1 className="text-2xl font-semibold">Sign up</h1>
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
            autoComplete="new-password"
          />
        </div>
        {state?.error && (
          <p role="alert" className="text-red-600">
            {state.error}
          </p>
        )}
        <button type="submit" disabled={pending}>
          {pending ? "Signing up…" : "Sign up"}
        </button>
      </form>
      <p>
        Already have an account? <Link href="/login">Log in</Link>
      </p>
    </main>
  );
}
