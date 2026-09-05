import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import Home from "./page";

describe("Home page", () => {
  it("renders the default landing content", () => {
    render(<Home />);
    expect(screen.getByText(/to get started, edit the/i)).toBeInTheDocument();
  });
});
