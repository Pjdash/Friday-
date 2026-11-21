"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { errorKey, postEligibility, type Failure } from "@/lib/client";
import { emptyValues, requiredFields, valuesFromProfile, validate, type FormErrors, type FormValues } from "@/lib/profile";
import { SAMPLES } from "@/lib/samples";
import { useSchemes, useSlow } from "@/lib/use-schemes";
import type { ProfileField, Verdict } from "@/lib/types";
import { useLang } from "./lang-provider";
import { ProfileForm } from "./profile-form";
import { Alert, Spinner, buttonClass } from "./ui";
import { VerdictCard } from "./verdict-card";

type Status =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "done"; verdicts: Verdict[]; failed: Failure | null }
  | { kind: "error"; code: Failure };

const ALL = "ALL";

export function EligibilityChecker() {
  const { lang, t } = useLang();
  const params = useSearchParams();
  const { state: schemesState, retry: retrySchemes } = useSchemes();
  const slowSchemes = useSlow(schemesState.status === "loading");

  const [requested, setRequested] = useState(params.get("scheme") ?? ALL);
  const [values, setValues] = useState<FormValues>(emptyValues);
  const [errors, setErrors] = useState<FormErrors>({});
  const [consent, setConsent] = useState(false);
  const [consentError, setConsentError] = useState(false);
  const [asOf, setAsOf] = useState("");
  const [status, setStatus] = useState<Status>({ kind: "idle" });
  const resultsRef = useRef<HTMLHeadingElement>(null);
  const formRef = useRef<HTMLFormElement>(null);

  const schemes = schemesState.status === "ready" ? schemesState.schemes : [];
  // Ignore an unknown ?scheme= value instead of failing on it.
  const selected = schemes.some((s) => s.scheme_id === requested) ? requested : ALL;
  const fields = requiredFields(values);

  useEffect(() => {
    if (status.kind === "done" || status.kind === "error") resultsRef.current?.focus();
  }, [status]);

  function change(field: ProfileField, value: string) {
    setValues((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => (prev[field] ? { ...prev, [field]: undefined } : prev));
  }

  function applySample(index: number) {
    setValues(valuesFromProfile(SAMPLES[index].profile));
    setErrors({});
    setStatus({ kind: "idle" });
  }

  function reset() {
    setValues(emptyValues());
    setErrors({});
    setConsent(false);
    setConsentError(false);
    setAsOf("");
    setStatus({ kind: "idle" });
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (status.kind === "loading" || schemesState.status !== "ready") return;

    const { profile, errors: found } = validate(values, fields);
    setErrors(found);
    setConsentError(!consent);
    if (Object.keys(found).length > 0 || !consent) {
      // Move focus to the first problem so keyboard and screen reader users land on it.
      requestAnimationFrame(() => {
        formRef.current?.querySelector<HTMLElement>("[aria-invalid='true']")?.focus();
      });
      return;
    }

    setStatus({ kind: "loading" });
    const ids = selected === ALL ? schemes.map((s) => s.scheme_id) : [selected];
    const results = await Promise.all(
      ids.map((scheme_id) => postEligibility({ scheme_id, profile, ...(asOf ? { as_of: asOf } : {}) })),
    );
    const verdicts = results.flatMap((r) => (r.ok ? [r.data] : []));
    const firstFailure = results.find((r) => !r.ok);
    if (verdicts.length === 0 && firstFailure && !firstFailure.ok) {
      setStatus({ kind: "error", code: firstFailure.code });
    } else {
      setStatus({ kind: "done", verdicts, failed: firstFailure && !firstFailure.ok ? firstFailure.code : null });
    }
  }

  const loading = status.kind === "loading";

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-brand-strong">{t("check.title")}</h1>
        <p className="mt-2 max-w-2xl text-lg">{t("check.lead")}</p>
      </header>

      <form ref={formRef} onSubmit={submit} noValidate className="no-print space-y-6 rounded-2xl border border-line bg-surface p-5">
        <div>
          <label htmlFor="scheme" className="mb-1 block font-semibold">
            {t("check.scheme")}
          </label>
          <select
            id="scheme"
            value={selected}
            onChange={(e) => setRequested(e.target.value)}
            disabled={schemesState.status !== "ready"}
            className="min-h-12 w-full rounded-xl border-2 border-line bg-surface px-3 text-base focus:border-brand sm:max-w-md"
          >
            <option value={ALL}>{t("check.allSchemes")}</option>
            {schemes.map((s) => (
              <option key={s.scheme_id} value={s.scheme_id} lang="en">
                {s.name}
              </option>
            ))}
          </select>
          {schemesState.status === "loading" && (
            <p role="status" className="mt-1 text-sm text-muted">
              {slowSchemes ? t("home.waking") : t("common.loading")}
            </p>
          )}
          {schemesState.status === "error" && (
            <div className="mt-2">
              <Alert tone="bad" role="alert" title={t("home.loadError")}>
                <button type="button" onClick={retrySchemes} className={`${buttonClass("secondary")} mt-2`}>
                  {t("common.retry")}
                </button>
              </Alert>
            </div>
          )}
        </div>

        <div>
          <p className="font-semibold">{t("check.sample")}</p>
          <p className="text-sm text-muted">{t("check.sampleHint")}</p>
          <ul className="mt-2 flex flex-wrap gap-2">
            {SAMPLES.map((sample, index) => (
              <li key={sample.id}>
                <button type="button" onClick={() => applySample(index)} className="min-h-11 rounded-full border-2 border-line bg-surface px-4 text-base hover:bg-brand-soft">
                  {sample.label[lang]}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <ProfileForm values={values} errors={errors} fields={fields} onChange={change} idPrefix="chk" />

        <details className="rounded-xl border border-line p-3">
          <summary className="cursor-pointer font-semibold">{t("check.advanced")}</summary>
          <div className="mt-3">
            <label htmlFor="as-of" className="mb-1 block font-semibold">
              {t("check.asOf")} <span className="font-normal text-muted">({t("common.optional")})</span>
            </label>
            <input
              id="as-of"
              type="date"
              min="2020-01-01"
              max="2100-12-31"
              value={asOf}
              onChange={(e) => setAsOf(e.target.value)}
              aria-describedby="as-of-help"
              className="min-h-12 rounded-xl border-2 border-line bg-surface px-3 text-base focus:border-brand"
            />
            <p id="as-of-help" className="mt-1 text-sm text-muted">
              {t("check.asOfHint")}
            </p>
          </div>
        </details>

        <div>
          <label className="flex cursor-pointer items-start gap-3">
            <input
              type="checkbox"
              checked={consent}
              onChange={(e) => {
                setConsent(e.target.checked);
                if (e.target.checked) setConsentError(false);
              }}
              aria-invalid={consentError ? true : undefined}
              aria-describedby={consentError ? "consent-error" : undefined}
              className="mt-1.5 size-6 shrink-0 accent-brand"
            />
            <span>{t("check.consent")}</span>
          </label>
          {consentError && (
            <p id="consent-error" className="mt-1 text-sm font-semibold text-bad">
              {t("err.consent")}
            </p>
          )}
        </div>

        {Object.keys(errors).some((k) => errors[k as ProfileField]) && (
          <Alert tone="bad" role="alert" title={t("check.fixErrors")} />
        )}

        <div className="flex flex-wrap gap-3">
          <button type="submit" disabled={loading || schemesState.status !== "ready"} className={buttonClass("primary")}>
            {loading && <Spinner />}
            {loading ? t("check.checking") : t("check.submit")}
          </button>
          <button type="button" onClick={reset} className={buttonClass("ghost")}>
            {t("check.reset")}
          </button>
        </div>
      </form>

      <section aria-live="polite" className="space-y-4">
        {(status.kind === "done" || status.kind === "error") && (
          <h2 ref={resultsRef} tabIndex={-1} className="text-2xl font-bold outline-none">
            {t("check.results")}
          </h2>
        )}
        {status.kind === "error" && (
          <Alert tone="bad" role="alert" title={t(errorKey(status.code))}>
            <button type="button" onClick={() => formRef.current?.requestSubmit()} className={`${buttonClass("secondary")} mt-2`}>
              {t("common.retry")}
            </button>
          </Alert>
        )}
        {status.kind === "done" && (
          <>
            {status.failed && <Alert tone="warn" role="alert" title={t(errorKey(status.failed))} />}
            <div className="space-y-5">
              {status.verdicts.map((verdict) => (
                <VerdictCard key={verdict.scheme_id} verdict={verdict} />
              ))}
            </div>
          </>
        )}
      </section>
    </div>
  );
}
