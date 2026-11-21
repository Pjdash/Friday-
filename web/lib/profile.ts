import type { MessageKey } from "./i18n";
import { CATEGORIES, OCCUPATIONS, RESIDENCES } from "./schemas";
import type { Profile, ProfileField } from "./types";
import { PROFILE_FIELDS } from "./types";

/** Form state is all strings, so a half-typed number never fights the input. */
export type FormValues = Record<ProfileField, string>;
export type FormErrors = Partial<Record<ProfileField, MessageKey>>;

export const emptyValues = (): FormValues => ({
  age: "",
  annual_household_income: "",
  occupation: "",
  land_holding_acres: "",
  residence_type: "",
  category: "",
});

export function valuesFromProfile(profile: Profile): FormValues {
  const values = emptyValues();
  for (const field of PROFILE_FIELDS) {
    const value = profile[field];
    if (value !== undefined) values[field] = String(value);
  }
  return values;
}

/**
 * Fields the citizen must fill in. Land is only asked of farmers: the schemes that use it start
 * with an occupation == farmer rule, and asking a retiree for acreage invites made-up answers.
 */
export function requiredFields(values: FormValues): ProfileField[] {
  const base: ProfileField[] = ["age", "annual_household_income", "occupation", "residence_type", "category"];
  return values.occupation === "farmer" ? [...base, "land_holding_acres"] : base;
}

function parseNumber(raw: string): number | null {
  const cleaned = raw.replace(/[,\s₹]/g, "");
  if (cleaned === "" || !/^\d+(\.\d+)?$/.test(cleaned)) return null;
  const value = Number(cleaned);
  return Number.isFinite(value) ? value : null;
}

const RANGES: Record<"age" | "annual_household_income" | "land_holding_acres", [number, number]> = {
  age: [0, 120],
  annual_household_income: [0, 100_000_000],
  land_holding_acres: [0, 10_000],
};

/**
 * Turn form strings into a Profile. `fields` are the ones that must be present; any other field
 * that has been filled in is still validated and included.
 */
export function validate(values: FormValues, fields: readonly ProfileField[]): { profile: Profile; errors: FormErrors } {
  const profile: Profile = {};
  const errors: FormErrors = {};

  for (const field of PROFILE_FIELDS) {
    const raw = values[field].trim();
    const required = fields.includes(field);
    if (raw === "") {
      if (required) errors[field] = "err.required";
      continue;
    }
    switch (field) {
      case "age":
      case "annual_household_income":
      case "land_holding_acres": {
        const n = parseNumber(raw);
        const [min, max] = RANGES[field];
        if (n === null || n < min || n > max || (field === "age" && !Number.isInteger(n))) {
          errors[field] = "err.number";
        } else {
          profile[field] = n;
        }
        break;
      }
      case "occupation":
        if ((OCCUPATIONS as readonly string[]).includes(raw)) profile.occupation = raw;
        else errors.occupation = "err.invalid";
        break;
      case "category":
        if ((CATEGORIES as readonly string[]).includes(raw)) profile.category = raw;
        else errors.category = "err.invalid";
        break;
      case "residence_type":
        if ((RESIDENCES as readonly string[]).includes(raw)) profile.residence_type = raw;
        else errors.residence_type = "err.invalid";
        break;
    }
  }
  return { profile, errors };
}
