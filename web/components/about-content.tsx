"use client";

import { OFFICIAL } from "@/lib/i18n";
import { useLang } from "./lang-provider";

export function AboutContent() {
  const { lang, t } = useLang();
  return (
    <article className="max-w-3xl space-y-8">
      <h1 className="text-3xl font-bold text-brand-strong">{t("about.title")}</h1>

      <section className="space-y-3">
        <p className="text-lg">{t("about.p1")}</p>
        <p className="text-lg">{t("about.p2")}</p>
      </section>

      <section aria-labelledby="official-h" className="space-y-2 rounded-2xl border border-line bg-surface p-5">
        <h2 id="official-h" className="text-xl font-bold">
          {t("about.official.title")}
        </h2>
        <p>{OFFICIAL.finalDecision[lang]}</p>
        <p>{OFFICIAL.zeroFee[lang]}</p>
        <p>{OFFICIAL.neverShareOtp[lang]}</p>
      </section>

      <section aria-labelledby="privacy-h" className="space-y-2 rounded-2xl border border-line bg-surface p-5">
        <h2 id="privacy-h" className="text-xl font-bold">
          {t("about.privacy.title")}
        </h2>
        <p>{t("about.privacy.body")}</p>
      </section>
    </article>
  );
}
