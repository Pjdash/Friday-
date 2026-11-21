"use client";

import { LANGS, type Lang } from "@/lib/types";
import { useLang } from "./lang-provider";

// Each language is named in its own script so a reader can find theirs without reading English.
const NAMES: Record<Lang, string> = { en: "English", hi: "हिन्दी", kn: "ಕನ್ನಡ", ta: "தமிழ்" };

export function LangSwitcher() {
  const { lang, setLang, t } = useLang();
  return (
    <div role="group" aria-label={t("lang.label")} className="flex rounded-xl border border-line bg-surface p-1">
      {LANGS.map((code) => (
        <button
          key={code}
          type="button"
          lang={code}
          aria-pressed={code === lang}
          onClick={() => setLang(code)}
          className={
            "min-h-11 min-w-11 rounded-lg px-3 text-base font-medium transition-colors " +
            (code === lang ? "bg-brand text-white" : "text-foreground hover:bg-brand-soft")
          }
        >
          {NAMES[code]}
        </button>
      ))}
    </div>
  );
}
