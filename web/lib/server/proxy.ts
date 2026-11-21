import { NextResponse, connection } from "next/server";
import type { z } from "zod";
import type { ApiError } from "../types";
import { callBackend } from "./backend";
import { clientKey, rateLimit } from "./ratelimit";

const NO_STORE = { "Cache-Control": "no-store" };
const MAX_BODY_BYTES = 16 * 1024;

function error(status: number, code: ApiError["code"], message: string, extra?: HeadersInit) {
  return NextResponse.json({ error: message, code } satisfies ApiError, {
    status,
    headers: { ...NO_STORE, ...extra },
  });
}

/** Validate a JSON POST body, rate limit, forward to the backend, and return its answer. */
export async function proxyPost<S extends z.ZodType>(
  request: Request,
  path: "chat" | "eligibility",
  schema: S,
  limitPerMinute: number,
): Promise<NextResponse> {
  const wait = rateLimit(`${path}:${clientKey(request)}`, limitPerMinute, 60_000);
  if (wait !== null) return error(429, "rate_limited", "Too many requests.", { "Retry-After": String(wait) });

  const length = Number(request.headers.get("content-length") ?? 0);
  if (length > MAX_BODY_BYTES) return error(413, "invalid", "Request too large.");

  let raw: unknown;
  try {
    const text = await request.text();
    if (text.length > MAX_BODY_BYTES) return error(413, "invalid", "Request too large.");
    raw = JSON.parse(text);
  } catch {
    return error(400, "invalid", "Invalid JSON.");
  }

  const parsed = schema.safeParse(raw);
  if (!parsed.success) return error(422, "invalid", "Invalid input.");

  const result = await callBackend(path, { method: "POST", json: parsed.data });
  return NextResponse.json(result.body, { status: result.status, headers: NO_STORE });
}

export async function proxyGet(
  path: "schemes" | "ready",
  cacheControl: string = NO_STORE["Cache-Control"],
): Promise<NextResponse> {
  // With Cache Components, GET handlers are prerendered at build unless they read request-time
  // data. This must run at request time: the backend is not reachable (or meaningful) at build.
  await connection();
  const result = await callBackend(path, { method: "GET" });
  const ok = result.status === 200;
  return NextResponse.json(result.body, {
    status: result.status,
    // Only cache successes: a cached error would outlive the outage that caused it.
    headers: { "Cache-Control": ok ? cacheControl : "no-store" },
  });
}
