import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";

const mockLogin = vi.fn();

vi.mock("./actions", () => ({
  login: (...args: unknown[]) => mockLogin(...args),
}));

import LoginPage from "./page";

describe("LoginPage", () => {
  it("renders email and password fields and a submit button", () => {
    render(<LoginPage />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /log in/i })).toBeInTheDocument();
  });

  it("shows an inline error instead of crashing on wrong credentials", async () => {
    mockLogin.mockResolvedValue({ error: "Invalid login credentials" });

    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "user@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "wrong-password" },
    });
    fireEvent.click(screen.getByRole("button", { name: /log in/i }));

    expect(
      await screen.findByText("Invalid login credentials"),
    ).toBeInTheDocument();
  });

  it("links to the signup page", () => {
    render(<LoginPage />);

    const link = screen.getByRole("link", { name: /sign up/i });
    expect(link).toHaveAttribute("href", "/signup");
  });

  it("does not render an error before any submission", async () => {
    render(<LoginPage />);

    await waitFor(() => {
      expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    });
  });
});
