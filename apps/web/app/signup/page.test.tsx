import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";

const mockSignup = vi.fn();

vi.mock("./actions", () => ({
  signup: (...args: unknown[]) => mockSignup(...args),
}));

import SignupPage from "./page";

describe("SignupPage", () => {
  it("renders email and password fields and a submit button", () => {
    render(<SignupPage />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /sign up/i })
    ).toBeInTheDocument();
  });

  it("shows an inline error instead of crashing when signup fails", async () => {
    mockSignup.mockResolvedValue({ error: "User already registered" });

    render(<SignupPage />);

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "taken@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: /sign up/i }));

    expect(
      await screen.findByText("User already registered")
    ).toBeInTheDocument();
  });

  it("links to the login page", () => {
    render(<SignupPage />);

    const link = screen.getByRole("link", { name: /log in/i });
    expect(link).toHaveAttribute("href", "/login");
  });
});
