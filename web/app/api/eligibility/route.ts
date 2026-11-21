import { eligibilityBodySchema } from "@/lib/schemas";
import { proxyPost } from "@/lib/server/proxy";

export function POST(request: Request) {
  // A full "all schemes" check is one request per scheme, so the limit is higher than chat's.
  return proxyPost(request, "eligibility", eligibilityBodySchema, 40);
}
