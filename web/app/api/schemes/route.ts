import { proxyGet } from "@/lib/server/proxy";

export function GET() {
  // The scheme list changes only when the knowledge base is redeployed, so a short shared cache
  // is safe and saves a cold-start round trip to the backend.
  return proxyGet("schemes", "public, s-maxage=300, stale-while-revalidate=3600");
}
