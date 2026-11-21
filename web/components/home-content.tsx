"use client";

import Link from "next/link";
import { useLang } from "./lang-provider";
import { SafetyPanel } from "./safety-banner";
import { SchemeCards } from "./scheme-cards";
import { buttonClass } from "./ui";

export function HomeContent() {
  const { t } = useLang();
  return (
    <div className="space-y-10">
      <section aria-labelledby="home-title">
        <h1 id="home-title" className="max-w-3xl text-3xl font-bold leading-snug text-brand-strong md:text-4xl">
          {t("home.title")}
        </h1>
        <p className="mt-3 max-w-2xl text-lg">{t("home.lead")}</p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/check" className={buttonClass("primary")}>
            {t("home.ctaCheck")}
          </Link>
          <Link href="/chat" className={buttonClass("secondary")}>
            {t("home.ctaChat")}
          </Link>
        </div>
      </section>

      <SafetyPanel />

      <section aria-labelledby="schemes-title">
        <h2 id="schemes-title" className="mb-4 text-2xl font-bold">
          {t("home.schemes")}
        </h2>
        <SchemeCards />
      </section>
    </div>
  );
}
