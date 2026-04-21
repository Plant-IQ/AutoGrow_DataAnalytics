const REAL_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function fetchJson(path: string, base: string) {
  const res = await fetch(`${base}${path}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export const realFetcher = async (path: string) => fetchJson(path, REAL_BASE);
export const fetcher = realFetcher;

export const postJson = async (path: string, body: unknown) => {
  const res = await fetch(`${REAL_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res;
};

// Kept for compatibility in case other code imports BASE directly
export const BASE = REAL_BASE;
export const DEFAULT_LAT = process.env.NEXT_PUBLIC_DEFAULT_LAT ?? "13.7563";
export const DEFAULT_LON = process.env.NEXT_PUBLIC_DEFAULT_LON ?? "100.5018";
