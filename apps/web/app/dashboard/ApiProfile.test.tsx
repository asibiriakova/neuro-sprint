import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

const { mockApiFetch } = vi.hoisted(() => ({
  mockApiFetch: vi.fn(),
}));

vi.mock("@/lib/api", async (importActual) => {
  const actual = await importActual<typeof import("@/lib/api")>();
  return {
    ...actual,
    apiFetch: mockApiFetch,
  };
});

import ApiProfile from "./ApiProfile";
import { ApiError } from "@/lib/api";

describe("ApiProfile", () => {
  it("shows a loading state before the request resolves", () => {
    mockApiFetch.mockReturnValue(new Promise(() => {}));

    render(<ApiProfile />);

    expect(screen.getByText(/loading from api/i)).toBeInTheDocument();
  });

  it("renders the id and email once the request succeeds", async () => {
    mockApiFetch.mockResolvedValue({ id: "user-123", email: "me@example.com" });

    render(<ApiProfile />);

    expect(
      await screen.findByText("From API: user-123 / me@example.com")
    ).toBeInTheDocument();
  });

  it("shows a visible error state when the request fails", async () => {
    mockApiFetch.mockRejectedValue(
      new ApiError("http", "Request failed with status 500.", 500)
    );

    render(<ApiProfile />);

    expect(
      await screen.findByRole("alert")
    ).toHaveTextContent("Something went wrong talking to the server.");
  });
});
