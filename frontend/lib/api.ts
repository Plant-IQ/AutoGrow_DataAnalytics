const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const fetcher = (url: string) =>
  fetch(`${BASE}${url}`).then((r) => r.json());