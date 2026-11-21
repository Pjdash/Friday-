"use client";

import { OFFICIAL } from "@/lib/i18n";
import { useLang } from "./lang-provider";

export function Footer() {
  const { lang, t } = useLang();
  return (
    <footer className="no-print mt-12 border-t border-line bg-surface">
      <div className="mx-auto max-w-5xl space-y-1 px-4 py-6 text-sm text-muted">
        <p className="font-medium text-foreground">{t("footer.note")}</p>
        <p>{OFFICIAL.finalDecision[lang]}</p>
      </div>
    </footer>
  );
}
