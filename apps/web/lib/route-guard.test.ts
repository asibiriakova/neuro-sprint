import { describe, expect, it } from "vitest";
import { decideRedirect, isAuthRoute, isProtectedPath } from "./route-guard";

describe("isProtectedPath", () => {
  it("matches the dashboard root and nested paths", () => {
    expect(isProtectedPath("/dashboard")).toBe(true);
    expect(isProtectedPath("/dashboard/settings")).toBe(true);
  });

  it("does not match unrelated paths", () => {
    expect(isProtectedPath("/")).toBe(false);
    expect(isProtectedPath("/login")).toBe(false);
    expect(isProtectedPath("/dashboards")).toBe(false);
  });
});

describe("isAuthRoute", () => {
  it("matches login and signup", () => {
    expect(isAuthRoute("/login")).toBe(true);
    expect(isAuthRoute("/signup")).toBe(true);
  });

  it("does not match other paths", () => {
    expect(isAuthRoute("/dashboard")).toBe(false);
    expect(isAuthRoute("/")).toBe(false);
  });
});

describe("decideRedirect", () => {
  it("redirects logged-out users away from protected routes", () => {
    expect(decideRedirect("/dashboard", false)).toBe("/login");
    expect(decideRedirect("/dashboard/settings", false)).toBe("/login");
  });

  it("lets logged-in users reach protected routes", () => {
    expect(decideRedirect("/dashboard", true)).toBeNull();
  });

  it("redirects logged-in users away from login/signup", () => {
    expect(decideRedirect("/login", true)).toBe("/dashboard");
    expect(decideRedirect("/signup", true)).toBe("/dashboard");
  });

  it("lets logged-out users reach login/signup", () => {
    expect(decideRedirect("/login", false)).toBeNull();
    expect(decideRedirect("/signup", false)).toBeNull();
  });

  it("leaves public routes alone regardless of auth state", () => {
    expect(decideRedirect("/", false)).toBeNull();
    expect(decideRedirect("/", true)).toBeNull();
  });
});
