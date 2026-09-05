import { beforeEach, describe, expect, it, vi } from "vitest";

const { signUp, mockCreateClient, mockRedirect } = vi.hoisted(() => {
  const signUp = vi.fn();
  return {
    signUp,
    mockCreateClient: vi.fn(async () => ({
      auth: { signUp },
    })),
    mockRedirect: vi.fn((path: string) => {
      throw new Error(`REDIRECT:${path}`);
    }),
  };
});

vi.mock("@/lib/supabase/server", () => ({
  createClient: mockCreateClient,
}));
vi.mock("next/navigation", () => ({
  redirect: mockRedirect,
}));

import { signup } from "./actions";

function formDataOf(fields: Record<string, string>) {
  const fd = new FormData();
  for (const [key, value] of Object.entries(fields)) {
    fd.set(key, value);
  }
  return fd;
}

describe("signup server action", () => {
  beforeEach(() => {
    signUp.mockReset();
    mockCreateClient.mockClear();
    mockRedirect.mockClear();
  });

  it("returns an inline error for missing fields without calling Supabase", async () => {
    const state = await signup(undefined, formDataOf({ email: "", password: "" }));

    expect(state).toEqual({ error: "Email and password are required." });
    expect(signUp).not.toHaveBeenCalled();
  });

  it("returns an inline error for a too-short password", async () => {
    const state = await signup(
      undefined,
      formDataOf({ email: "user@example.com", password: "abc" })
    );

    expect(state).toEqual({
      error: "Password must be at least 6 characters.",
    });
    expect(signUp).not.toHaveBeenCalled();
  });

  it("returns an inline error when Supabase rejects the signup", async () => {
    signUp.mockResolvedValue({
      data: { user: null, session: null },
      error: { message: "User already registered" },
    });

    const state = await signup(
      undefined,
      formDataOf({ email: "user@example.com", password: "password123" })
    );

    expect(state).toEqual({ error: "User already registered" });
    expect(mockRedirect).not.toHaveBeenCalled();
  });

  it("redirects to /dashboard on successful signup", async () => {
    signUp.mockResolvedValue({
      data: { user: { id: "u1" }, session: {} },
      error: null,
    });

    await expect(
      signup(
        undefined,
        formDataOf({ email: "new@example.com", password: "password123" })
      )
    ).rejects.toThrow("REDIRECT:/dashboard");

    expect(signUp).toHaveBeenCalledWith({
      email: "new@example.com",
      password: "password123",
    });
  });
});
