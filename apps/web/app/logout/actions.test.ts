import { beforeEach, describe, expect, it, vi } from "vitest";

const { signOut, mockCreateClient, mockRedirect } = vi.hoisted(() => {
  const signOut = vi.fn();
  return {
    signOut,
    mockCreateClient: vi.fn(async () => ({
      auth: { signOut },
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

import { logout } from "./actions";

describe("logout server action", () => {
  beforeEach(() => {
    signOut.mockReset();
    signOut.mockResolvedValue({ error: null });
    mockCreateClient.mockClear();
    mockRedirect.mockClear();
  });

  it("clears the session and redirects to /login", async () => {
    await expect(logout()).rejects.toThrow("REDIRECT:/login");

    expect(signOut).toHaveBeenCalledTimes(1);
  });
});
