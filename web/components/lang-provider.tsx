"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useSyncExternalStore } from "react";
import { t as translate, type MessageKey } from "@/lib/i18n";
import { LANGS, type Lang } from "@/lib/types";

// The chosen language is a harmless preference (not personal data), so it may live in
// localStorage. Profile details never do. A module-level fallback keeps the switcher working
// when storage is blocked (private mode, strict settings).
const KEY = "mitra.lang";
const listeners = new Set<() => void>();
let memory: Lang | null = null;

const isLang = (value: unknown): value is Lang => LANGS.includes(value as Lang);

function readStored(): Lang {
  if (memory) return memory;
  try {
    const stored = window.localStorage.getItem(KEY);
    if (isLang(stored)) return stored;
  } catch {
    /* storage unavailable */
  }
  return "en";
}

function subscribe(callback: () => void) {
  listeners.add(callback);
  const onStorage = (event: StorageEvent) => {
    if (event.key === KEY) {
      memory = null;
      callback();
    }
  };
  window.addEventListener("storage", onStorage);
  return () => {
    listeners.delete(callback);
    window.removeEventListener("storage", onStorage);
  };
}

function writeLang(lang: Lang) {
  memory = lang;
  try {
    window.localStorage.setItem(KEY, lang);
  } catch {
    /* storage unavailable: memory still holds it for this visit */
  }
  listeners.forEach((callback) => callback());
}

interface LangContextValue {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: (key: MessageKey, vars?: Record<string, string>) => string;
}

const LangContext = createContext<LangContextValue | null>(null);

export function LangProvider({ children }: { children: React.ReactNode }) {
  // Server and first client render use "en"; React then switches to the stored value without a
  // hydration mismatch.
  const lang = useSyncExternalStore(subscribe, readStored, () => "en" as Lang);

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const t = useCallback(
    (key: MessageKey, vars?: Record<string, string>) => translate(lang, key, vars),
    [lang],
  );
  const value = useMemo(() => ({ lang, setLang: writeLang, t }), [lang, t]);
  return <LangContext.Provider value={value}>{children}</LangContext.Provider>;
}

export function useLang(): LangContextValue {
  const value = useContext(LangContext);
  if (!value) throw new Error("useLang must be used inside <LangProvider>");
  return value;
}
