import type { ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost";

const BUTTON_BASE =
  "inline-flex min-h-12 items-center justify-center gap-2 rounded-xl px-5 text-base font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-60";
const BUTTON_VARIANTS: Record<ButtonVariant, string> = {
  primary: "bg-brand text-white hover:bg-brand-strong",
  secondary: "border-2 border-brand bg-surface text-brand-strong hover:bg-brand-soft",
  ghost: "text-brand-strong hover:bg-brand-soft",
};

/** Class string so the same look works on <button> and next/link <Link>. */
export const buttonClass = (variant: ButtonVariant = "primary") => `${BUTTON_BASE} ${BUTTON_VARIANTS[variant]}`;

export function Spinner() {
  return (
    <svg className="size-5 animate-spin" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="3" opacity="0.25" />
      <path d="M21 12a9 9 0 0 0-9-9" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

export type Tone = "info" | "ok" | "warn" | "bad";

export const TONE_BOX: Record<Tone, string> = {
  info: "border-info bg-info-soft",
  ok: "border-ok bg-ok-soft",
  warn: "border-warn bg-warn-soft",
  bad: "border-bad bg-bad-soft",
};

export const TONE_TEXT: Record<Tone, string> = {
  info: "text-info",
  ok: "text-ok",
  warn: "text-warn",
  bad: "text-bad",
};

/** A callout. The border colour is reinforced by the title text, so colour is never the only cue. */
export function Alert({
  tone,
  title,
  children,
  role,
}: {
  tone: Tone;
  title?: string;
  children?: ReactNode;
  role?: "alert" | "status";
}) {
  return (
    <div role={role} className={`rounded-xl border-l-8 p-4 ${TONE_BOX[tone]}`}>
      {title && <p className={`text-lg font-bold ${TONE_TEXT[tone]}`}>{title}</p>}
      {children && <div className={title ? "mt-1" : ""}>{children}</div>}
    </div>
  );
}

export function SourceChips({ ids }: { ids: string[] }) {
  if (ids.length === 0) return null;
  return (
    <ul className="flex flex-wrap gap-2">
      {ids.map((id) => (
        <li key={id} lang="en" className="rounded-md bg-brand-soft px-2 py-0.5 font-mono text-sm text-brand-strong">
          {id}
        </li>
      ))}
    </ul>
  );
}
