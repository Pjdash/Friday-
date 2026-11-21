import { chatBodySchema } from "@/lib/schemas";
import { proxyPost } from "@/lib/server/proxy";

export function POST(request: Request) {
  return proxyPost(request, "chat", chatBodySchema, 20);
}
