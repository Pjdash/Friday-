// Server-only: this file reads secrets (MITRA_API_KEY). Import it only from route handlers.
//
// The browser never talks to the Mitra API directly. Route handlers call it from here, so the API
// key stays on the server and the backend can stay private.
//
// Privacy rule (matches the backend's logging rule): never log request or response bodies, only
// metadata such as path, status and timing.

import type { ApiError } from "../types";

const TIMEOUT_MS = 25_000;

export interface BackendResult {
  status: number;
  /** Parsed JSON on success, an ApiError on failure. */
  body: unknown;
}

function failure(status: number, code: ApiError["code"], error: string): BackendResult {
  return { status, body: { error, code } satisfies ApiError };
}

function baseUrl(): URL | null {
  const raw = process.env.MITRA_API_URL?.trim();
  if (!raw) return null;
  try {
    // Trailing slash so a base that has a path (a service URL) is joined, not replaced.
    return new URL(raw.endsWith("/") ? raw : `${raw}/`);
  } catch {
    return null;
  }
}

function requestId(): string {
  return crypto.randomUUID().replaceAll("-", "");
}

export async function callBackend(
  path: "schemes" | "eligibility" | "chat" | "ready",
  init: { method: "GET" } | { method: "POST"; json: unknown },
): Promise<BackendResult> {
  const base = baseUrl();
  if (!base) {
    console.error("backend: MITRA_API_URL is not set or invalid");
    return failure(503, "unavailable", "The service is not configured.");
  }

  const headers: Record<string, string> = { "X-Request-ID": requestId(), Accept: "application/json" };
  const key = process.env.MITRA_API_KEY?.trim();
  if (key) headers["X-API-Key"] = key;
  if (init.method === "POST") headers["Content-Type"] = "application/json";

  const started = Date.now();
  let response: Response;
  try {
    response = await fetch(new URL(path, base), {
      method: init.method,
      headers,
      body: init.method === "POST" ? JSON.stringify(init.json) : undefined,
      cache: "no-store",
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch (error) {
    const timedOut = error instanceof DOMException && error.name === "TimeoutError";
    console.error("backend: request failed", { path, reason: timedOut ? "timeout" : "network" });
    return failure(503, "unavailable", "The service is not reachable.");
  }
  console.info("backend: response", { path, status: response.status, ms: Date.now() - started });

  if (response.ok) {
    try {
      return { status: 200, body: await response.json() };
    } catch {
      return failure(502, "upstream", "The service returned an unreadable response.");
    }
  }

  // Map upstream failures to our own small vocabulary. Raw upstream detail is not forwarded: it can
  // echo user input, and a 401/403 means *our* configuration is wrong, which a citizen cannot fix.
  if (response.status === 401 || response.status === 403) {
    console.error("backend: rejected our API key", { path, status: response.status });
    return failure(502, "upstream", "The service is temporarily unavailable.");
  }
  if (response.status === 404) return failure(404, "not_found", "Not found.");
  if (response.status === 422) return failure(422, "invalid", "Invalid input.");
  if (response.status === 503) return failure(503, "unavailable", "The service is not ready.");
  return failure(502, "upstream", "The service is temporarily unavailable.");
}
