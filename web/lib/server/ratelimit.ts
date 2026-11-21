// Best-effort, in-memory fixed-window limiter.
//
// Honest limits: on serverless every instance has its own memory, so this slows a single client
// hammering one warm instance but is NOT a global quota. It is a courtesy guard, not a security
// boundary. The real protection against abuse of the backend is that it is only reachable through
// these route handlers and requires an API key. For a hard global limit, put Vercel's WAF rate
// limiting rules in front of /api/*.

interface Bucket {
  count: number;
  resetAt: number;
}

const buckets = new Map<string, Bucket>();
const MAX_BUCKETS = 5_000;

export function clientKey(request: Request): string {
  // On Vercel the platform sets x-forwarded-for, so the first entry is the client.
  const forwarded = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim();
  return forwarded || request.headers.get("x-real-ip") || "local";
}

/** Returns seconds to wait if the client is over the limit, otherwise null. */
export function rateLimit(key: string, limit: number, windowMs: number): number | null {
  const now = Date.now();
  if (buckets.size > MAX_BUCKETS) {
    for (const [k, b] of buckets) if (b.resetAt <= now) buckets.delete(k);
    if (buckets.size > MAX_BUCKETS) buckets.clear(); // under attack: reset rather than grow without bound
  }
  const bucket = buckets.get(key);
  if (!bucket || bucket.resetAt <= now) {
    buckets.set(key, { count: 1, resetAt: now + windowMs });
    return null;
  }
  bucket.count += 1;
  return bucket.count > limit ? Math.ceil((bucket.resetAt - now) / 1000) : null;
}
