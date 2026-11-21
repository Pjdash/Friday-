import { proxyGet } from "@/lib/server/proxy";

// Readiness of the whole stack as seen from the UI: 200 only if the backend answers /ready.
// Used by the deploy smoke test.
export function GET() {
  return proxyGet("ready");
}
