// Shapes mirror the backend (mitra/agent.py Answer, mitra/eligibility.py Verdict, mitra/api.py).
// If the backend changes, change these first: the UI renders exactly what the API returns.

export const LANGS = ["en", "hi", "kn", "ta"] as const;
export type Lang = (typeof LANGS)[number];

export type Outcome = "meets_criteria" | "does_not_meet" | "needs_info" | "not_open";

export interface ConditionResult {
  id: string;
  label: string;
  /** null = the profile did not say */
  passed: boolean | null;
  detail: string;
  sources: string[];
  notes: string[];
}

export interface DocumentItem {
  name: string;
  requirement: "mandatory" | "optional" | "conditional";
  validity: string;
  notes: string[];
}

export interface Verdict {
  scheme_id: string;
  scheme_name: string;
  as_of: string;
  outcome: Outcome;
  summary: string;
  conditions: ConditionResult[];
  blockers: string[];
  missing_fields: string[];
  documents: DocumentItem[];
  caveats: string[];
  benefit: string;
  department: string;
  sources: string[];
  disclaimer: string;
}

export type Intent = "fraud" | "eligibility" | "documents" | "fee" | "grievance" | "info";

export interface Answer {
  text: string;
  intent: Intent;
  language: Lang;
  scheme_id: string | null;
  /** A signal for the host application. The service does NOT file a report or ticket itself. */
  escalate_to: string | null;
  citations: string[];
  flags: string[];
  needs: string[];
  verdicts: Verdict[];
}

export interface SchemeSummary {
  scheme_id: string;
  name: string;
  department: string;
  benefit: string;
}

/** The fields the eligibility rules read. All optional: missing ones come back as `needs_info`. */
export interface Profile {
  age?: number;
  annual_household_income?: number;
  occupation?: string;
  land_holding_acres?: number;
  residence_type?: string;
  category?: string;
}

export type ProfileField = keyof Profile;

export const PROFILE_FIELDS: readonly ProfileField[] = [
  "age",
  "annual_household_income",
  "occupation",
  "land_holding_acres",
  "residence_type",
  "category",
];

export interface ApiError {
  error: string;
  /** machine-readable: unavailable | rate_limited | invalid | upstream */
  code: "unavailable" | "rate_limited" | "invalid" | "upstream" | "not_found";
}
