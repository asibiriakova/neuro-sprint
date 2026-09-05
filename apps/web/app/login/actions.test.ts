import { beforeEach, describe, expect, it, vi } from "vitest";

const { signInWithPassword, mockCreateClient, mockRedirect } = vi.hoisted(
  () => {
    const signInWithPassword = vi.fn();
    return {
      signInWithPassword,
      mockCreateClient: vi.fn(async () => ({
        auth: { signInWithPassword },
      })),
      mockRedirect: vi.fn((path: string) => {
        throw new Error(`REDIRECT:${path}`);
      }),
    };
  }
);

vi.mock("@/lib/supabase/server", () => ({
  createClient: mockCreateClient,
}));
vi.mock("next/navigation", () => ({
  redirect: mockRedirect,
}));

import { login } from "./actions";

function formDataOf(fields: Record<string, string>) {
  const fd = new FormData();
  for (const [key, value] of Object.entries(fields)) {
    fd.set(key, value);
  }
  return fd;
}

describe("login server action", () => {
  beforeEach(() => {
    signInWithPassword.mockReset();
    mockCreateClient.mockClear();
    mockRedirect.mockClear();
  });

  it("returns an inline error for missing fields without calling Supabase", async () => {
    const state = await login(undefined, formDataOf({ email: "", password: "" }));

    expect(state).toEqual({ error: "Email and password are required." });
    expect(signInWithPassword).not.toHaveBeenCalled();
  });

  it("returns an inline error on wrong credentials instead of crashing", async () => {
    signInWithPassword.mockResolvedValue({
      data: { user: null, session: null },
      error: { message: "Invalid login credentials" },
    });

    const state = await login(
      undefined,
      formDataOf({ email: "user@example.com", password: "wrong-password" })
    );

    expect(state).toEqual({ error: "Invalid login credentials" });
    expect(mockRedirect).not.toHaveBeenCalled();
  });

  it("redirects to /dashboard on successful login", async () => {
    signInWithPassword.mockResolvedValue({
      data: { user: { id: "u1" }, session: {} },
      error: null,
    });

    await expect(
      login(
        undefined,
        formDataOf({ email: "user@example.com", password: "correct-password" })
      )
    ).rejects.toThrow("REDIRECT:/dashboard");

    expect(signInWithPassword).toHaveBeenCalledWith({
      email: "user@example.com",
      password: "correct-password",
    });
  });
});
