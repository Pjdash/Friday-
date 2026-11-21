"use client";

import { OFFICIAL } from "@/lib/i18n";
import { useLang } from "./lang-provider";

function ShieldIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" focusable="false" className="shrink-0">
      <path
        d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5l-8-3Zm-1 14-4-4 1.4-1.4L11 13.2l4.6-4.6L17 10l-6 6Z"
        fill="currentColor"
      />
    </svg>
  );
}

/** One-line reminder shown on every page: applying is free, never share an OTP. */
export function SafetyStrip() {
  const { t } = useLang();
  return (
    <div className="no-print bg-brand-soft text-brand-strong">
      <p className="mx-auto flex max-w-5xl items-center gap-2 px-4 py-2 text-base font-medium">
        <ShieldIcon />
        {t("safety.title")}
      </p>
    </div>
  );
}

/** The official fee and OTP sentences, verbatim from the knowledge base, in the chosen language. */
export function SafetyPanel() {
  const { lang, t } = useLang();
  return (
    <section aria-labelledby="safety-heading" className="rounded-2xl border border-brand/30 bg-brand-soft p-5">
      <h2 id="safety-heading" className="flex items-center gap-2 text-lg font-bold text-brand-strong">
        <ShieldIcon />
        {t("safety.title")}
      </h2>
      <p className="mt-2">{OFFICIAL.zeroFee[lang]}</p>
      <p className="mt-2">{OFFICIAL.neverShareOtp[lang]}</p>
    </section>
  );
}
