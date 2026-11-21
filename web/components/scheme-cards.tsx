"use client";

import Link from "next/link";
import { errorKey } from "@/lib/client";
import { useSchemes, useSlow } from "@/lib/use-schemes";
import { useLang } from "./lang-provider";
import { Alert, buttonClass } from "./ui";

export function SchemeCards() {
  const { t } = useLang();
  const { state, retry } = useSchemes();
  const slow = useSlow(state.status === "loading");

  if (state.status === "loading") {
    return (
      <div aria-busy="true">
        <ul className="grid gap-4 md:grid-cols-3" aria-hidden="true">
          {[0, 1, 2].map((i) => (
            <li key={i} className="h-48 animate-pulse rounded-2xl border border-line bg-surface" />
          ))}
        </ul>
        <p role="status" className="mt-3 text-muted">
          {slow ? t("home.waking") : t("common.loading")}
        </p>
      </div>
    );
  }

  if (state.status === "error") {
    return (
      <Alert tone="bad" title={t("home.loadError")} role="alert">
        <p>{t(errorKey(state.code))}</p>
        <button type="button" onClick={retry} className={`${buttonClass("secondary")} mt-3`}>
          {t("common.retry")}
        </button>
      </Alert>
    );
  }

  return (
    <ul className="grid gap-4 md:grid-cols-3">
      {state.schemes.map((scheme) => (
        <li key={scheme.scheme_id} className="flex flex-col rounded-2xl border border-line bg-surface p-5">
          {/* Scheme text comes from the official guideline and is English-only for now. */}
          <h3 lang="en" className="text-xl font-bold text-brand-strong">
            {scheme.name}
          </h3>
          <p lang="en" className="mt-1 text-sm text-muted">
            {scheme.department}
          </p>
          <p className="mt-4 text-sm font-semibold uppercase tracking-wide text-muted">{t("home.benefit")}</p>
          <p lang="en" className="grow">
            {scheme.benefit}
          </p>
          <Link href={`/check?scheme=${encodeURIComponent(scheme.scheme_id)}`} className={`${buttonClass("secondary")} mt-5`}>
            {t("home.checkThis")}
          </Link>
        </li>
      ))}
    </ul>
  );
}
