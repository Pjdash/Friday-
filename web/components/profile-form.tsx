"use client";

import type { ReactNode } from "react";
import type { MessageKey } from "@/lib/i18n";
import type { FormErrors, FormValues } from "@/lib/profile";
import { CATEGORIES, OCCUPATIONS, RESIDENCES } from "@/lib/schemas";
import type { ProfileField } from "@/lib/types";
import { useLang } from "./lang-provider";

const INPUT =
  "min-h-12 w-full rounded-xl border-2 bg-surface px-3 text-base focus:border-brand disabled:opacity-60";

function Field({
  id,
  label,
  help,
  error,
  children,
}: {
  id: string;
  label: string;
  help?: string;
  error?: string;
  children: ReactNode;
}) {
  return (
    <div>
      <label htmlFor={id} className="mb-1 block font-semibold">
        {label}
      </label>
      {children}
      {help && (
        <p id={`${id}-help`} className="mt-1 text-sm text-muted">
          {help}
        </p>
      )}
      {error && (
        <p id={`${id}-error`} className="mt-1 text-sm font-semibold text-bad">
          {error}
        </p>
      )}
    </div>
  );
}

interface Props {
  values: FormValues;
  errors: FormErrors;
  /** Which fields to show, in the standard order. */
  fields: readonly ProfileField[];
  onChange: (field: ProfileField, value: string) => void;
  idPrefix?: string;
}

export function ProfileForm({ values, errors, fields, onChange, idPrefix = "pf" }: Props) {
  const { t } = useLang();
  const show = (field: ProfileField) => fields.includes(field);
  const idOf = (field: ProfileField) => `${idPrefix}-${field}`;

  /** aria wiring shared by the text inputs and selects */
  const aria = (field: ProfileField, hasHelp = false) => {
    const id = idOf(field);
    const describedBy = [hasHelp ? `${id}-help` : null, errors[field] ? `${id}-error` : null]
      .filter(Boolean)
      .join(" ");
    return {
      id,
      "aria-invalid": errors[field] ? true : undefined,
      "aria-describedby": describedBy || undefined,
      className: `${INPUT} ${errors[field] ? "border-bad" : "border-line"}`,
    } as const;
  };
  const err = (field: ProfileField) => (errors[field] ? t(errors[field] as MessageKey) : undefined);

  return (
    <div className="grid gap-5 sm:grid-cols-2">
      {show("age") && (
        <Field id={idOf("age")} label={t("f.age")} error={err("age")}>
          <input
            {...aria("age")}
            type="text"
            inputMode="numeric"
            autoComplete="off"
            value={values.age}
            onChange={(e) => onChange("age", e.target.value)}
          />
        </Field>
      )}

      {show("annual_household_income") && (
        <Field id={idOf("annual_household_income")} label={t("f.annual_household_income")} error={err("annual_household_income")}>
          <input
            {...aria("annual_household_income")}
            type="text"
            inputMode="numeric"
            autoComplete="off"
            value={values.annual_household_income}
            onChange={(e) => onChange("annual_household_income", e.target.value)}
          />
        </Field>
      )}

      {show("occupation") && (
        <Field id={idOf("occupation")} label={t("f.occupation")} error={err("occupation")}>
          <select {...aria("occupation")} value={values.occupation} onChange={(e) => onChange("occupation", e.target.value)}>
            <option value="">{t("f.select")}</option>
            {OCCUPATIONS.map((value) => (
              <option key={value} value={value}>
                {t(`occ.${value}`)}
              </option>
            ))}
          </select>
        </Field>
      )}

      {show("category") && (
        <Field id={idOf("category")} label={t("f.category")} error={err("category")}>
          <select {...aria("category")} value={values.category} onChange={(e) => onChange("category", e.target.value)}>
            <option value="">{t("f.select")}</option>
            {CATEGORIES.map((value) => (
              <option key={value} value={value}>
                {t(`cat.${value}`)}
              </option>
            ))}
          </select>
        </Field>
      )}

      {show("land_holding_acres") && (
        <Field
          id={idOf("land_holding_acres")}
          label={t("f.land_holding_acres")}
          help={t("f.land.help")}
          error={err("land_holding_acres")}
        >
          <input
            {...aria("land_holding_acres", true)}
            type="text"
            inputMode="decimal"
            autoComplete="off"
            value={values.land_holding_acres}
            onChange={(e) => onChange("land_holding_acres", e.target.value)}
          />
        </Field>
      )}

      {show("residence_type") && (
        <fieldset
          aria-invalid={errors.residence_type ? true : undefined}
          aria-describedby={errors.residence_type ? `${idOf("residence_type")}-error` : undefined}
        >
          <legend className="mb-1 font-semibold">{t("f.residence_type")}</legend>
          <div className="flex gap-3">
            {RESIDENCES.map((value) => (
              <label
                key={value}
                className="flex min-h-12 flex-1 cursor-pointer items-center justify-center rounded-xl border-2 border-line bg-surface px-3 font-medium has-[:checked]:border-brand has-[:checked]:bg-brand has-[:checked]:text-white has-[:focus-visible]:outline-3 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-info"
              >
                <input
                  type="radio"
                  name={idOf("residence_type")}
                  value={value}
                  checked={values.residence_type === value}
                  onChange={() => onChange("residence_type", value)}
                  className="sr-only"
                />
                {t(`res.${value}`)}
              </label>
            ))}
          </div>
          {errors.residence_type && (
            <p id={`${idOf("residence_type")}-error`} className="mt-1 text-sm font-semibold text-bad">
              {t(errors.residence_type)}
            </p>
          )}
        </fieldset>
      )}
    </div>
  );
}
