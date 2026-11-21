"use client";

import { useEffect, useRef, useState } from "react";
import { errorKey, postChat, type Failure } from "@/lib/client";
import { isMessageKey, type MessageKey } from "@/lib/i18n";
import { emptyValues, validate, type FormErrors, type FormValues } from "@/lib/profile";
import { PROFILE_FIELDS, type Answer, type Profile, type ProfileField } from "@/lib/types";
import { EscalationBanner } from "./escalation-banner";
import { useLang } from "./lang-provider";
import { ProfileForm } from "./profile-form";
import { Alert, SourceChips, Spinner, buttonClass } from "./ui";
import { VerdictCard } from "./verdict-card";

type Msg =
  | { id: number; role: "user"; text: string }
  | { id: number; role: "assistant"; answer: Answer }
  | { id: number; role: "error"; code: Failure; retryText: string };

// Omit<> on a union collapses it to the shared keys; this keeps each member's own shape.
type DistributiveOmit<T, K extends PropertyKey> = T extends unknown ? Omit<T, K> : never;

const isProfileField = (value: string): value is ProfileField => (PROFILE_FIELDS as readonly string[]).includes(value);

/** Asks only for the details the assistant said it needs, then replays the question with them. */
function NeedsForm({ needs, onSubmit }: { needs: ProfileField[]; onSubmit: (profile: Profile) => void }) {
  const { t } = useLang();
  const [values, setValues] = useState<FormValues>(emptyValues);
  const [errors, setErrors] = useState<FormErrors>({});
  const [consent, setConsent] = useState(false);
  const [consentError, setConsentError] = useState(false);

  // As in the eligibility form, only farmers are asked for land.
  const visible = needs.filter(
    (f) => f !== "land_holding_acres" || !needs.includes("occupation") || values.occupation === "farmer",
  );

  function submit(event: React.FormEvent) {
    event.preventDefault();
    const { profile, errors: found } = validate(values, visible);
    setErrors(found);
    setConsentError(!consent);
    if (Object.keys(found).length === 0 && consent) onSubmit(profile);
  }

  return (
    <form onSubmit={submit} noValidate className="space-y-4 rounded-xl border border-line bg-background p-4">
      <p className="text-lg font-bold">{t("chat.needsTitle")}</p>
      <ProfileForm
        values={values}
        errors={errors}
        fields={visible}
        idPrefix="needs"
        onChange={(field, value) => setValues((prev) => ({ ...prev, [field]: value }))}
      />
      <label className="flex cursor-pointer items-start gap-3">
        <input
          type="checkbox"
          checked={consent}
          onChange={(e) => {
            setConsent(e.target.checked);
            if (e.target.checked) setConsentError(false);
          }}
          aria-invalid={consentError ? true : undefined}
          className="mt-1.5 size-6 shrink-0 accent-brand"
        />
        <span>{t("check.consent")}</span>
      </label>
      {consentError && <p className="text-sm font-semibold text-bad">{t("err.consent")}</p>}
      <button type="submit" className={buttonClass("primary")}>
        {t("chat.needsSubmit")}
      </button>
    </form>
  );
}

function AssistantMessage({
  answer,
  askForDetails,
  onProfile,
}: {
  answer: Answer;
  askForDetails: boolean;
  onProfile: (profile: Profile) => void;
}) {
  const { t } = useLang();
  const needs = answer.needs.filter(isProfileField);
  return (
    <div className="space-y-3 rounded-2xl border border-line bg-surface p-4">
      {answer.escalate_to && <EscalationBanner target={answer.escalate_to} />}
      {/* The answer is plain text with line breaks and indented lists, so keep its whitespace. */}
      <p lang={answer.language} className="whitespace-pre-wrap break-words">
        {answer.text}
      </p>
      {answer.flags.map((flag) => {
        const key = `flag.${flag}`;
        return isMessageKey(key) ? (
          <Alert key={flag} tone="info" role="status">
            {t(key)}
          </Alert>
        ) : null;
      })}
      {answer.citations.length > 0 && (
        <div>
          <p className="mb-1 text-sm font-semibold uppercase tracking-wide text-muted">{t("chat.sources")}</p>
          <SourceChips ids={answer.citations} />
        </div>
      )}
      {answer.verdicts.length > 0 && (
        <details className="rounded-xl border border-line p-3">
          <summary className="cursor-pointer font-semibold">{t("check.results")}</summary>
          <div className="mt-3 space-y-4">
            {answer.verdicts.map((verdict) => (
              <VerdictCard key={verdict.scheme_id} verdict={verdict} />
            ))}
          </div>
        </details>
      )}
      {askForDetails && needs.length > 0 && <NeedsForm needs={needs} onSubmit={onProfile} />}
    </div>
  );
}

const SUGGESTIONS: MessageKey[] = ["chat.suggest1", "chat.suggest2", "chat.suggest3", "chat.suggest4"];

export function ChatPanel() {
  const { lang, t } = useLang();
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  // Held in memory only, never persisted: gone on reload, on "clear chat" and on "forget".
  const [profile, setProfile] = useState<Profile | null>(null);
  const nextId = useRef(1);
  const lastQuestion = useRef("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messages.length > 0) endRef.current?.scrollIntoView({ block: "end" });
  }, [messages, pending]);

  const add = (message: DistributiveOmit<Msg, "id">) =>
    setMessages((prev) => [...prev, { ...message, id: nextId.current++ } as Msg]);

  async function ask(text: string, withProfile: Profile | null, echo: boolean) {
    if (pending) return;
    lastQuestion.current = text;
    if (echo) add({ role: "user", text });
    setPending(true);
    const result = await postChat({ message: text, language: lang, ...(withProfile ? { profile: withProfile } : {}) });
    setPending(false);
    if (result.ok) add({ role: "assistant", answer: result.data });
    else add({ role: "error", code: result.code, retryText: text });
  }

  function submit(event: React.FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text || pending) return;
    setInput("");
    void ask(text, profile, true);
  }

  function applyDetails(details: Profile) {
    setProfile(details);
    void ask(lastQuestion.current, details, false);
  }

  function clear() {
    setMessages([]);
    setProfile(null);
    lastQuestion.current = "";
  }

  const lastAssistantId = [...messages].reverse().find((m) => m.role === "assistant")?.id;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-brand-strong">{t("chat.title")}</h1>
        <p className="mt-2 max-w-2xl text-lg">{t("chat.lead")}</p>
        <p className="mt-1 text-sm text-muted">{t("chat.langNote")}</p>
      </header>

      {messages.length === 0 && (
        <section aria-label={t("chat.empty")}>
          <p className="mb-2 font-semibold">{t("chat.empty")}</p>
          <ul className="flex flex-wrap gap-2">
            {SUGGESTIONS.map((key) => (
              <li key={key}>
                <button
                  type="button"
                  onClick={() => void ask(t(key), profile, true)}
                  disabled={pending}
                  className="min-h-11 rounded-full border-2 border-line bg-surface px-4 text-left text-base hover:bg-brand-soft disabled:opacity-60"
                >
                  {t(key)}
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      <div role="log" aria-live="polite" aria-relevant="additions" className="space-y-4">
        {messages.map((message) => {
          if (message.role === "user") {
            return (
              <div key={message.id} className="flex justify-end">
                <div className="max-w-[85%] rounded-2xl bg-brand px-4 py-3 text-white">
                  <p className="sr-only">{t("chat.you")}</p>
                  <p className="whitespace-pre-wrap break-words">{message.text}</p>
                </div>
              </div>
            );
          }
          if (message.role === "error") {
            return (
              <Alert key={message.id} tone="bad" role="alert" title={t(errorKey(message.code))}>
                <button
                  type="button"
                  onClick={() => void ask(message.retryText, profile, false)}
                  disabled={pending}
                  className={`${buttonClass("secondary")} mt-2`}
                >
                  {t("common.retry")}
                </button>
              </Alert>
            );
          }
          return (
            <div key={message.id}>
              <p className="sr-only">{t("chat.assistant")}</p>
              <AssistantMessage
                answer={message.answer}
                askForDetails={message.id === lastAssistantId && !pending && profile === null}
                onProfile={applyDetails}
              />
            </div>
          );
        })}
        {pending && (
          <p role="status" className="flex items-center gap-2 text-muted">
            <Spinner />
            {t("chat.thinking")}
          </p>
        )}
        <div ref={endRef} />
      </div>

      <form onSubmit={submit} className="no-print space-y-3">
        <label htmlFor="chat-input" className="sr-only">
          {t("chat.placeholder")}
        </label>
        <textarea
          id="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            // Enter sends, Shift+Enter adds a line. Never send while an IME composition is open:
            // Hindi, Kannada and Tamil keyboards use Enter to confirm a word.
            if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
              e.preventDefault();
              e.currentTarget.form?.requestSubmit();
            }
          }}
          rows={3}
          maxLength={2000}
          placeholder={t("chat.placeholder")}
          className="w-full rounded-xl border-2 border-line bg-surface p-3 text-base focus:border-brand"
        />
        {input.length > 1800 && (
          <p className="text-sm text-muted" aria-live="polite">
            {input.length}/2000
          </p>
        )}
        <div className="flex flex-wrap gap-3">
          <button type="submit" disabled={pending || input.trim() === ""} className={buttonClass("primary")}>
            {t("chat.send")}
          </button>
          {messages.length > 0 && (
            <button type="button" onClick={clear} className={buttonClass("ghost")}>
              {t("chat.clear")}
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
