import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const { getSession, mockCreateClient, mockRedirect } = vi.hoisted(() => {
  const getSession = vi.fn();
  return {
    getSession,
    mockCreateClient: vi.fn(() => ({
      auth: { getSession },
    })),
    mockRedirect: vi.fn((path: string) => {
      throw new Error(`REDIRECT:${path}`);
    }),
  };
});

vi.mock("@/lib/supabase/client", () => ({
  createClient: mockCreateClient,
}));
vi.mock("next/navigation", () => ({
  redirect: mockRedirect,
}));

import { apiFetch, ApiError } from "./api";

function jsonResponse(body: unknown, init: { status?: number } = {}) {
  return {
    ok: (init.status ?? 200) >= 200 && (init.status ?? 200) < 300,
    status: init.status ?? 200,
    json: () => Promise.resolve(body),
  } as Response;
}

describe("apiFetch", () => {
  const originalEnv = process.env.NEXT_PUBLIC_API_BASE_URL;
  const originalFetch = global.fetch;

  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_BASE_URL = "http://api.example.test";
    getSession.mockResolvedValue({
      data: { session: { access_token: "test-token" } },
    });
  });

  afterEach(() => {
    process.env.NEXT_PUBLIC_API_BASE_URL = originalEnv;
    global.fetch = originalFetch;
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it("prefixes the path with the base URL and attaches the bearer token", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ id: "1" }));
    global.fetch = fetchMock as unknown as typeof fetch;

    const result = await apiFetch<{ id: string }>("/me");

    expect(result).toEqual({ id: "1" });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe("http://api.example.test/me");
    const headers = options.headers as Headers;
    expect(headers.get("Authorization")).toBe("Bearer test-token");
  });

  it("redirects to /login on a 401 response", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse({}, { status: 401 }));
    global.fetch = fetchMock as unknown as typeof fetch;

    await expect(apiFetch("/me")).rejects.toThrow("REDIRECT:/login");
    expect(mockRedirect).toHaveBeenCalledWith("/login");
  });

  it("rejects with an ApiError for a non-401 error response", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse({ detail: "nope" }, { status: 500 }));
    global.fetch = fetchMock as unknown as typeof fetch;

    const error = await apiFetch("/me").catch((err) => err);

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).kind).toBe("http");
    expect((error as ApiError).status).toBe(500);
  });

  it("rejects with an ApiError when the backend is unreachable", async () => {
    const fetchMock = vi
      .fn()
      .mockRejectedValue(new TypeError("Failed to fetch"));
    global.fetch = fetchMock as unknown as typeof fetch;

    const error = await apiFetch("/me").catch((err) => err);

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).kind).toBe("network");
  });

  it("rejects with an ApiError when the request exceeds the 10s timeout", async () => {
    vi.useFakeTimers();
    const fetchMock = vi.fn(
      (_url: string, options: RequestInit) =>
        new Promise((_resolve, reject) => {
          options.signal?.addEventListener("abort", () => {
            reject(
              new DOMException("The operation was aborted.", "AbortError"),
            );
          });
        }),
    );
    global.fetch = fetchMock as unknown as typeof fetch;

    const pending = apiFetch("/me").catch((err) => err);
    await vi.advanceTimersByTimeAsync(10_000);
    const error = await pending;

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).kind).toBe("timeout");
  });

  it("rejects with an ApiError when the response body isn't valid JSON", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () =>
        Promise.reject(new SyntaxError("Unexpected end of JSON input")),
    } as unknown as Response);
    global.fetch = fetchMock as unknown as typeof fetch;

    const error = await apiFetch("/me").catch((err) => err);

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).kind).toBe("invalid-json");
  });

  it("sends the request without a usable token when there is no session", async () => {
    getSession.mockResolvedValue({ data: { session: null } });
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ id: "1" }));
    global.fetch = fetchMock as unknown as typeof fetch;

    await apiFetch("/me");

    const [, options] = fetchMock.mock.calls[0];
    const headers = options.headers as Headers;
    expect(headers.has("Authorization")).toBe(false);
  });
});
