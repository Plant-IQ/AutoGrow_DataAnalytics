export const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const fetcher = (url: string) => fetch(`${BASE}${url}`).then((r) => r.json());

export const postJson = (path: string, body: unknown) =>
  fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
