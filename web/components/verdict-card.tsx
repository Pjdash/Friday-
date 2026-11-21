"use client";

import { OFFICIAL, isMessageKey, type MessageKey } from "@/lib/i18n";
import type { ConditionResult, Outcome, Verdict } from "@/lib/types";
import { useLang } from "./lang-provider";
import { SourceChips, TONE_BOX, TONE_TEXT, type Tone, buttonClass } from "./ui";

const OUTCOME_TONE: Record<Outcome, Tone> = {
  meets_criteria: "ok",
  does_not_meet: "bad",
  needs_info: "warn",
  not_open: "info",
};

function OutcomeIcon({ tone }: { tone: Tone }) {
  const paths: Record<Tone, string> = {
    ok: "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm-1.2 14.4-4-4 1.4-1.4 2.6 2.6 5-5 1.4 1.4-6.4 6.4Z",
    bad: "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm4.2 12.8-1.4 1.4-2.8-2.8-2.8 2.8-1.4-1.4 2.8-2.8-2.8-2.8 1.4-1.4 2.8 2.8 2.8-2.8 1.4 1.4-2.8 2.8 2.8 2.8Z",
    warn: "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm1 15h-2v-2h2v2Zm0-4h-2V7h2v6Z",
    info: "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm1 15h-2v-6h2v6Zm0-8h-2V7h2v2Z",
  };
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" aria-hidden="true" focusable="false" className={`shrink-0 ${TONE_TEXT[tone]}`}>
      <path d={paths[tone]} fill="currentColor" />
    </svg>
  );
}

function ConditionRow({ condition }: { condition: ConditionResult }) {
  const { t } = useLang();
  const state: { tone: Tone; label: MessageKey } =
    condition.passed === true
      ? { tone: "ok", label: "verdict.met" }
      : condition.passed === false
        ? { tone: "bad", label: "verdict.notMet" }
        : { tone: "warn", label: "verdict.unknown" };
  return (
    <li className="flex gap-3 rounded-xl border border-line p-3">
      <OutcomeIcon tone={state.tone} />
      <div className="min-w-0">
        <p className={`font-semibold ${TONE_TEXT[state.tone]}`}>{t(state.label)}</p>
        {/* Rule text is the official English wording until the backend localises it. */}
        <p lang="en">{condition.label}</p>
        {condition.detail && (
          <p lang="en" className="text-sm text-muted">
            {condition.detail}
          </p>
        )}
        {condition.notes.map((note) => (
          <p key={note} lang="en" className="mt-1 text-sm">
            {note}
          </p>
        ))}
        <div className="mt-2">
          <SourceChips ids={condition.sources} />
        </div>
      </div>
    </li>
  );
}

const REQUIREMENT_KEY: Record<string, MessageKey> = {
  mandatory: "verdict.mandatory",
  optional: "verdict.optional",
  conditional: "verdict.conditional",
};

export function VerdictCard({ verdict }: { verdict: Verdict }) {
  const { lang, t } = useLang();
  const tone = OUTCOME_TONE[verdict.outcome] ?? "info";
  const outcomeKey = (prefix: "outcome" | "outcome.help") =>
    `${prefix}.${verdict.outcome}` as MessageKey;
  const fieldLabel = (field: string) => {
    const key = `f.${field}`;
    return isMessageKey(key) ? t(key) : field;
  };

  return (
    <article className="rounded-2xl border border-line bg-surface p-5 print:break-inside-avoid">
      <h3 lang="en" className="text-xl font-bold text-brand-strong">
        {verdict.scheme_name}
      </h3>
      <p className="text-sm text-muted">{t("verdict.asOf", { date: verdict.as_of })}</p>

      <div className={`mt-4 flex gap-3 rounded-xl border-l-8 p-4 ${TONE_BOX[tone]}`}>
        <OutcomeIcon tone={tone} />
        <div>
          <p className={`text-lg font-bold ${TONE_TEXT[tone]}`}>{t(outcomeKey("outcome"))}</p>
          <p>{t(outcomeKey("outcome.help"))}</p>
        </div>
      </div>

      {/* The outcome box already says this for the other outcomes; "not open" needs the reason. */}
      {verdict.summary && verdict.outcome === "not_open" && (
        <p lang="en" className="mt-3 text-muted">
          {verdict.summary}
        </p>
      )}
      {lang !== "en" && <p className="mt-1 text-sm text-muted">{t("verdict.englishNote")}</p>}

      {verdict.conditions.length > 0 && (
        <section className="mt-6" aria-label={t("verdict.how")}>
          <h4 className="mb-2 text-lg font-bold">{t("verdict.how")}</h4>
          {/* Rules can be "A or B". A red item inside a "meets" result is then expected, so say so. */}
          {verdict.outcome === "meets_criteria" && verdict.conditions.some((c) => c.passed === false) && (
            <p className="mb-3 rounded-xl bg-info-soft p-3">{t("verdict.alternativesNote")}</p>
          )}
          <ul className="space-y-2">
            {verdict.conditions.map((condition) => (
              <ConditionRow key={condition.id} condition={condition} />
            ))}
          </ul>
        </section>
      )}

      {verdict.blockers.length > 0 && (
        <section className="mt-6">
          <h4 className="mb-2 text-lg font-bold">{t("verdict.blockers")}</h4>
          <ul className="list-disc space-y-1 pl-6" lang="en">
            {verdict.blockers.map((blocker) => (
              <li key={blocker}>{blocker}</li>
            ))}
          </ul>
        </section>
      )}

      {verdict.missing_fields.length > 0 && (
        <section className="mt-6">
          <h4 className="mb-2 text-lg font-bold">{t("verdict.missing")}</h4>
          <ul className="list-disc space-y-1 pl-6">
            {verdict.missing_fields.map((field) => (
              <li key={field}>{fieldLabel(field)}</li>
            ))}
          </ul>
        </section>
      )}

      {verdict.documents.length > 0 && (
        <section className="mt-6">
          <h4 className="mb-2 text-lg font-bold">{t("verdict.documents")}</h4>
          <ul className="space-y-2">
            {verdict.documents.map((doc) => (
              <li key={doc.name} className="rounded-xl border border-line p-3">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <p lang="en" className="font-semibold">
                    {doc.name}
                  </p>
                  <span
                    className={
                      "rounded-full px-3 py-0.5 text-sm font-semibold " +
                      (doc.requirement === "mandatory"
                        ? "bg-brand text-white"
                        : doc.requirement === "conditional"
                          ? "bg-warn-soft text-warn"
                          : "bg-brand-soft text-brand-strong")
                    }
                  >
                    {t(REQUIREMENT_KEY[doc.requirement] ?? "verdict.optional")}
                  </span>
                </div>
                {doc.validity && (
                  <p className="text-sm text-muted">
                    {t("verdict.validity")}: <span lang="en">{doc.validity}</span>
                  </p>
                )}
                {doc.notes.map((note) => (
                  <p key={note} lang="en" className="mt-1 text-sm">
                    {note}
                  </p>
                ))}
              </li>
            ))}
          </ul>
        </section>
      )}

      {verdict.caveats.length > 0 && (
        <section className="mt-6">
          <h4 className="mb-2 text-lg font-bold">{t("verdict.caveats")}</h4>
          <ul className="list-disc space-y-1 pl-6" lang="en">
            {verdict.caveats.map((caveat) => (
              <li key={caveat}>{caveat}</li>
            ))}
          </ul>
        </section>
      )}

      <dl className="mt-6 grid gap-3 sm:grid-cols-2">
        <div>
          <dt className="text-sm font-semibold uppercase tracking-wide text-muted">{t("verdict.benefit")}</dt>
          <dd lang="en">{verdict.benefit}</dd>
        </div>
        <div>
          <dt className="text-sm font-semibold uppercase tracking-wide text-muted">{t("verdict.department")}</dt>
          <dd lang="en">{verdict.department}</dd>
        </div>
      </dl>

      {verdict.sources.length > 0 && (
        <div className="mt-4">
          <p className="mb-1 text-sm font-semibold uppercase tracking-wide text-muted">{t("verdict.sources")}</p>
          <SourceChips ids={verdict.sources} />
        </div>
      )}

      {/* Always show the official sentences, in the reader's language. Never hide the disclaimer. */}
      <div className="mt-6 space-y-1 rounded-xl bg-background p-3 text-sm">
        <p>{OFFICIAL.finalDecision[lang]}</p>
        <p>{OFFICIAL.zeroFee[lang]}</p>
      </div>

      <button type="button" onClick={() => window.print()} className={`${buttonClass("secondary")} no-print mt-5`}>
        {t("verdict.print")}
      </button>
    </article>
  );
}
