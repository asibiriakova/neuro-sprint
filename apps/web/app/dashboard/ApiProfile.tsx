"use client";

import { useEffect, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";

interface Me {
  id: string;
  email: string | null;
}

type State =
  | { status: "loading" }
  | { status: "success"; data: Me }
  | { status: "error"; message: string };

/**
 * Calls the FastAPI backend's `GET /me` on mount and renders the result.
 * Exists to prove (for a reviewer, on screen) that this data actually
 * round-tripped through the backend, distinct from the "Signed in as
 * {email}" line the server-rendered dashboard page gets directly from
 * Supabase.
 */
export default function ApiProfile() {
  const [state, setState] = useState<State>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    apiFetch<Me>("/me")
      .then((data) => {
        if (!cancelled) setState({ status: "success", data });
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof ApiError) {
          setState({
            status: "error",
            message: "Something went wrong talking to the server.",
          });
          return;
        }
        // Not an ApiError — e.g. the redirect-to-/login thrown by
        // apiFetch on a 401. Re-throw so Next.js's router handles it
        // instead of it being swallowed as a plain error here.
        throw err;
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (state.status === "loading") {
    return <p className="text-sm text-gray-500">Loading from API…</p>;
  }

  if (state.status === "error") {
    return (
      <p role="alert" className="text-sm text-red-600">
        {state.message}
      </p>
    );
  }

  return (
    <p className="text-sm text-gray-700">
      From API: {state.data.id} / {state.data.email}
    </p>
  );
}
