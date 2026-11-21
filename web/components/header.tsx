"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { MessageKey } from "@/lib/i18n";
import { LangSwitcher } from "./lang-switcher";
import { useLang } from "./lang-provider";

const NAV: { href: string; key: MessageKey }[] = [
  { href: "/", key: "nav.home" },
  { href: "/check", key: "nav.check" },
  { href: "/chat", key: "nav.chat" },
  { href: "/about", key: "nav.about" },
];

function Logo() {
  return (
    <svg width="40" height="40" viewBox="0 0 40 40" aria-hidden="true" focusable="false">
      <rect width="40" height="40" rx="10" className="fill-brand" />
      <path d="M10 28V13l10 9 10-9v15" fill="none" stroke="#fff" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="30" cy="9" r="3" className="fill-accent" />
    </svg>
  );
}

export function Header() {
  const { t } = useLang();
  const pathname = usePathname();

  return (
    <header className="no-print border-b border-line bg-surface">
      <a href="#main" className="skip-link">
        {t("skip")}
      </a>
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-x-6 gap-y-3 px-4 py-3">
        <Link href="/" className="flex items-center gap-3 rounded-lg">
          <Logo />
          <span>
            <span className="block text-lg font-bold leading-tight text-brand-strong">{t("app.name")}</span>
            <span className="block text-sm leading-tight text-muted">{t("app.tagline")}</span>
          </span>
        </Link>
        <LangSwitcher />
      </div>
      <nav aria-label={t("nav.menu")} className="border-t border-line">
        {/* Wraps instead of scrolling: a hidden horizontal scroll hides the last item on a phone. */}
        <ul className="mx-auto flex max-w-5xl flex-wrap px-2">
          {NAV.map(({ href, key }) => {
            const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
            return (
              <li key={href} className="shrink-0">
                <Link
                  href={href}
                  aria-current={active ? "page" : undefined}
                  className={
                    "flex min-h-12 items-center border-b-4 px-3 text-base font-medium " +
                    (active
                      ? "border-brand text-brand-strong"
                      : "border-transparent text-foreground hover:bg-brand-soft")
                  }
                >
                  {t(key)}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </header>
  );
}
