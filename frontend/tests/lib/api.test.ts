import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

describe("lib/api", () => {
  beforeEach(() => {
    vi.resetModules();
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });

  it("realFetcher uses NEXT_PUBLIC_API_URL and returns json", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://api.test");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ ok: true }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const mod = await import("@/lib/api");
    const result = await mod.realFetcher("/health");

    expect(fetchMock).toHaveBeenCalledWith("http://api.test/health");
    expect(result).toEqual({ ok: true });
  });

  it("realFetcher throws on non-ok response", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://api.test");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: "Server Error",
      })
    );

    const mod = await import("@/lib/api");
    await expect(mod.realFetcher("/health")).rejects.toThrow("500 Server Error");
  });

  it("postJson sends JSON payload", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://api.test");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      statusText: "OK",
    });
    vi.stubGlobal("fetch", fetchMock);

    const mod = await import("@/lib/api");
    await mod.postJson("/plants/start", { name: "Lettuce" });

    expect(fetchMock).toHaveBeenCalledWith("http://api.test/plants/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "Lettuce" }),
    });
  });
});
