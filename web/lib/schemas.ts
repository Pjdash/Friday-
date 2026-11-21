import { z } from "zod";
import { LANGS } from "./types";

// Request validation for the proxy. Limits mirror mitra/api.py (message <= 2000 chars, profile values
// short) but are stricter on purpose: the UI only ever sends the six fields the rules read, so
// anything else is rejected here before it reaches the backend.

export const OCCUPATIONS = ["farmer", "student", "retired", "shopkeeper", "daily_wage", "other"] as const;
export const CATEGORIES = ["general", "obc", "sc", "st"] as const;
export const RESIDENCES = ["rural", "urban"] as const;

export const profileSchema = z
  .object({
    age: z.number().int().min(0).max(120),
    annual_household_income: z.number().min(0).max(100_000_000),
    occupation: z.enum(OCCUPATIONS),
    land_holding_acres: z.number().min(0).max(10_000),
    residence_type: z.enum(RESIDENCES),
    category: z.enum(CATEGORIES),
  })
  .partial()
  .strict();

const isoDate = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}$/)
  .refine((s) => {
    const d = new Date(`${s}T00:00:00Z`);
    return !Number.isNaN(d.getTime()) && d.getUTCFullYear() >= 2020 && d.getUTCFullYear() <= 2100;
  });

export const chatBodySchema = z
  .object({
    // NFC so that Devanagari/Kannada/Tamil typed on different keyboards compare equal to the
    // backend's keyword lists.
    message: z
      .string()
      .transform((s) => s.normalize("NFC").trim())
      .pipe(z.string().min(1).max(2000)),
    language: z.enum(LANGS).optional(),
    profile: profileSchema.optional(),
    as_of: isoDate.optional(),
  })
  .strict();

export const eligibilityBodySchema = z
  .object({
    scheme_id: z.string().regex(/^[A-Z0-9-]{1,32}$/),
    profile: profileSchema.refine((p) => Object.keys(p).length > 0, "profile must not be empty"),
    as_of: isoDate.optional(),
  })
  .strict();

export type ChatBody = z.infer<typeof chatBodySchema>;
export type EligibilityBody = z.infer<typeof eligibilityBodySchema>;
