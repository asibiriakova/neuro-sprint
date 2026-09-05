import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

const { getUser, mockCreateClient, mockRedirect } = vi.hoisted(() => {
  const getUser = vi.fn();
  return {
    getUser,
    mockCreateClient: vi.fn(async () => ({
      auth: { getUser },
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
vi.mock("@/app/logout/actions", () => ({
  logout: vi.fn(),
}));

import DashboardPage from "./page";

describe("DashboardPage", () => {
  it("renders the signed-in user's email when logged in", async () => {
    getUser.mockResolvedValue({ data: { user: { email: "me@example.com" } } });

    render(await DashboardPage());

    expect(screen.getByText(/me@example.com/)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /log out/i })
    ).toBeInTheDocument();
  });

  it("redirects to /login instead of rendering when logged out", async () => {
    getUser.mockResolvedValue({ data: { user: null } });

    await expect(DashboardPage()).rejects.toThrow("REDIRECT:/login");
  });
});
