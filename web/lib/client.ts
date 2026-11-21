import type { MessageKey } from "./i18n";
import type { Answer, ApiError, Lang, Profile, SchemeSummary, Verdict } from "./types";

export type Failure = ApiError["code"] | "network";
export type Result<T> = { ok: true; data: T } | { ok: false; code: Failure };

async function request<T>(path: string, init?: RequestInit): Promise<Result<T>> {
  try {
    const response = await fetch(path, {
      ...init,
      headers: { Accept: "application/json", ...(init?.body ? { "Content-Type": "application/json" } : {}) },
      cache: "no-store",
    });
    const body: unknown = await response.json().catch(() => null);
    if (response.ok) return { ok: true, data: body as T };
    const code = (body as Partial<ApiError> | null)?.code;
    return { ok: false, code: code ?? "upstream" };
  } catch {
    return { ok: false, code: "network" };
  }
}

export const getSchemes = () => request<SchemeSummary[]>("/api/schemes");

export const postEligibility = (body: { scheme_id: string; profile: Profile; as_of?: string }) =>
  request<Verdict>("/api/eligibility", { method: "POST", body: JSON.stringify(body) });

export const postChat = (body: { message: string; language: Lang; profile?: Profile; as_of?: string }) =>
  request<Answer>("/api/chat", { method: "POST", body: JSON.stringify(body) });

/** The message a citizen should see for a failed call. */
export function errorKey(code: Failure): MessageKey {
  switch (code) {
    case "rate_limited":
      return "err.rate";
    case "unavailable":
    case "network":
      return "err.unavailable";
    case "invalid":
      return "err.invalid";
    default:
      return "err.generic";
  }
}
