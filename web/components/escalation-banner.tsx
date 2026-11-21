"use client";

import type { MessageKey } from "@/lib/i18n";
import { useLang } from "./lang-provider";
import { Alert } from "./ui";

const KNOWN: Record<string, { title: MessageKey; body: MessageKey; tone: "bad" | "warn" }> = {
  fraud_desk: { title: "escalate.fraud_desk.title", body: "escalate.fraud_desk.body", tone: "bad" },
  human_review: { title: "escalate.human_review.title", body: "escalate.human_review.body", tone: "warn" },
};

/**
 * `escalate_to` is a signal that the citizen should take a next step. The backend does not file a
 * report or ticket, so this banner tells them what to do themselves and never says it was done.
 */
export function EscalationBanner({ target }: { target: string }) {
  const { t } = useLang();
  const entry = KNOWN[target] ?? { title: "escalate.other.title", body: "escalate.other.body", tone: "warn" as const };
  return (
    <Alert tone={entry.tone} title={t(entry.title)} role={entry.tone === "bad" ? "alert" : "status"}>
      <p>{t(entry.body)}</p>
    </Alert>
  );
}
