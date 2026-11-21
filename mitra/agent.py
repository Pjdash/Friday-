"""LangGraph assistant: sanitize -> fraud check -> classify -> one answer node.

Everything here is deterministic and offline. Eligibility comes from eligibility.evaluate,
facts come from retrieval over the knowledge base, and the message text is only ever data.
`escalate_to` is a signal for the host application (fraud_desk, human review); this package does
not file reports or tickets itself, and the answer text never claims that it did.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from . import config, embeddings
from .eligibility import Verdict, evaluate, evaluate_all, normalize_profile
from .extract import extract_profile
from .generator import Generator, Passage, default_generator
from .i18n import FINAL_DECISION, FRAUD_REPORT, LANGUAGES, NEVER_SHARE_OTP, ZERO_FEE, detect_language
from .kb import KnowledgeBase
from .retrieval import Hit, Retriever, tokenize
from .safety import FraudSignal, detect_fraud, sanitize
from .schemes import EXTRA_ALIASES, SCHEMES, official_names
from .seed import CitizenStore

INTENTS = ("fraud", "eligibility", "documents", "fee", "grievance", "info")

# Checked in this order (after fraud), by substring on the case-folded message.
_KEYWORDS: dict[str, tuple[str, ...]] = {
    "grievance": (
        "reject", "appeal", "grievance", "complaint", "delay", "pending", "not received", "still shows",
        "under verification", "shikayat", "खारिज", "अस्वीकार", "शिकायत", "अपील", "देरी", "लंबित",
        "ತಿರಸ್ಕೃತ", "ದೂರು", "ಬಾಕಿ", "நிராகரி", "புகார்", "மேல்முறையீடு", "தாமத", "நிலுவை",
    ),
    "eligibility": (
        "eligib", "qualify", "can i apply", "am i ", "पात्र", "ಅರ್ಹ", "தகுதி", "apply kar sakta", "mil sakta",
    ),
    "documents": ("document", "papers", "certificate", "दस्तावेज", "कागज", "प्रमाण", "ದಾಖಲೆ", "ஆவண"),
    "fee": (" fee", "charge", "free of cost", "how much", "शुल्क", "ಶುಲ್ಕ", "கட்டணம்"),
}
_REJECTION = ("reject", "खारिज", "अस्वीकार", "ತಿರಸ್ಕೃತ", "நிராகரி")

_FIELD_PROMPT = {
    "age": "your age", "annual_household_income": "annual household income", "occupation": "occupation",
    "land_holding_acres": "total household land (acres)", "residence_type": "residence (rural or urban)",
    "category": "category (SC / ST / other)",
}


@dataclass
class Answer:
    text: str
    intent: str
    language: str
    scheme_id: str | None = None
    escalate_to: str | None = None
    citations: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    needs: list[str] = field(default_factory=list)
    verdicts: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class State(TypedDict, total=False):
    message: str
    citizen_id: str | None
    supplied_profile: dict[str, Any] | None
    as_of: date
    language: str | None
    clean: str
    flags: list[str]
    lang: str
    profile: dict[str, Any]
    fraud: FraudSignal | None
    intent: str
    schemes: list[str]
    answer: Answer


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


_NOT_FOUND_TEXT = ("I could not find this in the official documents available to me. Please ask at your nearest "
                   "MitraKendra / Jan Seva Kendra or the Block Welfare Office (free of charge).")


class Assistant:
    def __init__(self, kb: KnowledgeBase | None = None, citizens: CitizenStore | None = None, *,
                 retriever: Retriever | None = None, generator: Generator | None = None):
        """`retriever` and `generator` default to the environment-configured ones (embeddings and LLM
        answers are used when keys and packages are available, otherwise keyword search and quoting)."""
        self.kb = kb or KnowledgeBase.load()
        self.citizens = citizens if citizens is not None else CitizenStore.load()
        self.retriever = retriever or Retriever(
            self.kb, embedder=embeddings.default_embedder(), cache_path=embeddings.cache_dir())
        self.generator = generator if generator is not None else default_generator()
        self._aliases = self._build_aliases()
        self._graph = self._build_graph()

    # ---- public --------------------------------------------------------------------------------

    def ask(self, message: str, *, citizen_id: str | None = None, profile: dict[str, Any] | None = None,
            as_of: date | None = None, language: str | None = None) -> Answer:
        state = self._graph.invoke({
            "message": message, "citizen_id": citizen_id, "supplied_profile": profile,
            "as_of": as_of or config.today(), "language": language,
        })
        return state["answer"]

    # ---- graph ---------------------------------------------------------------------------------

    def _build_aliases(self) -> dict[str, set[str]]:
        aliases: dict[str, set[str]] = {}
        for scheme_id, scheme in SCHEMES.items():
            guideline = self.kb.get(scheme.guideline_id)
            names = official_names(guideline) if guideline else []
            raw = {scheme_id, scheme.name, *names, *EXTRA_ALIASES.get(scheme_id, ())}
            aliases[scheme_id] = {a.casefold() for a in raw}
        return aliases

    def _build_graph(self):
        graph = StateGraph(State)
        graph.add_node("prepare", self._prepare)
        graph.add_node("safety", self._safety)
        graph.add_node("classify", self._classify)
        for intent in INTENTS:
            graph.add_node(f"answer_{intent}", getattr(self, f"_answer_{intent}"))
            graph.add_edge(f"answer_{intent}", END)
        graph.add_edge(START, "prepare")
        graph.add_edge("prepare", "safety")
        graph.add_conditional_edges(
            "safety", lambda s: "answer_fraud" if s.get("fraud") else "classify",
            {"answer_fraud": "answer_fraud", "classify": "classify"})
        graph.add_conditional_edges(
            "classify", lambda s: f"answer_{s['intent']}",
            {f"answer_{i}": f"answer_{i}" for i in INTENTS if i != "fraud"})
        return graph.compile()

    # ---- nodes: preparation ----------------------------------------------------------------------

    def _prepare(self, state: State) -> State:
        clean, flags = sanitize(state["message"])
        as_of = state["as_of"]
        record: dict[str, Any] | None = None
        if state.get("supplied_profile"):
            record = dict(state["supplied_profile"])
        elif state.get("citizen_id"):
            found = self.citizens.get(state["citizen_id"])
            if found is None:
                flags.append("unknown_citizen")
            elif not CitizenStore.has_consent(found):
                flags.append("no_consent")  # POL-PRV-01: no consent, no use of the saved record
            else:
                record = found
        profile = {**extract_profile(clean), **(normalize_profile(record, as_of) if record else {})}

        lang = state.get("language")
        if lang not in LANGUAGES:
            detected = detect_language(clean)
            preferred = (record or {}).get("preferred_language")
            lang = detected if detected != "en" else (preferred if preferred in LANGUAGES else "en")
        return {"clean": clean, "flags": flags, "profile": profile, "lang": lang}

    def _safety(self, state: State) -> State:
        return {"fraud": detect_fraud(state["clean"])}

    def _classify(self, state: State) -> State:
        text = state["clean"].casefold()
        schemes = [sid for sid, names in self._aliases.items() if any(n in text for n in names)]
        intent = "info"
        for candidate, words in _KEYWORDS.items():
            if any(w in text for w in words):
                intent = candidate
                break
        return {"intent": intent, "schemes": schemes}

    # ---- nodes: answers --------------------------------------------------------------------------

    def _finish(self, state: State, text: str, intent: str, **extra: Any) -> State:
        scheme_id = extra.pop("scheme_id", (state.get("schemes") or [None])[0])
        answer = Answer(text=text.strip(), intent=intent, language=state["lang"], scheme_id=scheme_id,
                        flags=list(state.get("flags", [])), **extra)
        answer.citations = _unique(answer.citations)
        return {"answer": answer}

    def _answer_fraud(self, state: State) -> State:
        lang = state["lang"]
        lines = [
            "Please do not pay anything and do not share any OTP, PIN or password." if lang == "en" else "",
            NEVER_SHARE_OTP[lang],
            ZERO_FEE[lang],
            FRAUD_REPORT[lang],
            FINAL_DECISION[lang],
        ]
        if lang == "en":
            lines.insert(3, "If you received a fake call or SMS, you can also report the number to the nearest Jan "
                            "Seva Kendra, the local police, or the National Cyber Crime Helpline 1930.")
        citations = ["POL-FEE-01", "CIR-2026-09"]
        localized = {"hi": "HI-FRAUD-01", "kn": "KN-FRAUD-01", "ta": "TA-FRAUD-01"}.get(lang)
        if localized:
            citations.append(localized)
        return self._finish(state, "\n".join(line for line in lines if line), "fraud",
                            escalate_to=state["fraud"].escalate_to, citations=citations)

    def _answer_fee(self, state: State) -> State:
        lang = state["lang"]
        text = f"{ZERO_FEE[lang]}\n{FRAUD_REPORT[lang]}"
        return self._finish(state, text, "fee", citations=["POL-FEE-01", "CIR-2026-09"])

    def _answer_eligibility(self, state: State) -> State:
        as_of, profile, lang = state["as_of"], state["profile"], state["lang"]
        mentioned = state.get("schemes") or []
        if not profile:
            return self._finish(state, self._ask_for_details(mentioned), "eligibility",
                                needs=list(_FIELD_PROMPT))
        verdicts = [evaluate(sid, profile, self.kb, as_of) for sid in mentioned] if mentioned \
            else evaluate_all(profile, self.kb, as_of)
        blocks = [self._render_verdict(v, detailed=bool(mentioned)) for v in verdicts]
        if "no_consent" in state.get("flags", []):
            blocks.insert(0, "Your saved record was not used because consent is not on file (POL-PRV-01). "
                             "This check uses only what you wrote in your message.")
        blocks += [FINAL_DECISION[lang], ZERO_FEE[lang]]
        citations = [s for v in verdicts for s in v.sources] + ["POL-FEE-01"]
        needs = _unique([f for v in verdicts if v.outcome == "needs_info" for f in v.missing_fields])
        return self._finish(state, "\n\n".join(blocks), "eligibility", citations=citations, needs=needs,
                            verdicts=[asdict(v) for v in verdicts],
                            scheme_id=mentioned[0] if len(mentioned) == 1 else None)

    def _answer_documents(self, state: State) -> State:
        as_of, profile, lang = state["as_of"], state["profile"], state["lang"]
        mentioned = state.get("schemes") or []
        if not mentioned:
            names = "; ".join(f"{s.name} ({sid})" for sid, s in SCHEMES.items())
            return self._finish(state, f"Which scheme do you mean? I can list documents for: {names}.", "documents")
        blocks, citations, verdicts = [], ["POL-PRV-01"], []
        for sid in mentioned:
            verdict = evaluate(sid, profile, self.kb, as_of)
            verdicts.append(asdict(verdict))
            blocks.append(f"Documents for {verdict.scheme_name}:\n" + "\n".join(self._document_lines(verdict)))
            citations += verdict.sources
        blocks.append("Officers may only require the mandatory documents; optional ones cannot be demanded "
                      "as a condition of accepting your application (POL-PRV-01).")
        blocks.append(FINAL_DECISION[lang])
        return self._finish(state, "\n\n".join(blocks), "documents", citations=citations, verdicts=verdicts)

    def _answer_grievance(self, state: State) -> State:
        as_of, profile, lang = state["as_of"], state["profile"], state["lang"]
        mentioned = state.get("schemes") or []
        scheme = SCHEMES[mentioned[0]] if mentioned else None
        rejected = any(w in state["clean"].casefold() for w in _REJECTION)
        lines: list[str] = []
        citations = ["POL-GRV-01", "POL-FEE-01"]
        escalate_to, verdicts, needs = None, [], []

        if scheme and profile:
            verdict = evaluate(scheme.scheme_id, profile, self.kb, as_of)
            verdicts.append(asdict(verdict))
            citations += verdict.sources
            known = [c for c in verdict.conditions if c.passed is not None]
            if known:
                lines.append(f"Checked against the rules in force on {as_of} for {scheme.name}:")
                lines += [f"  {'✓' if c.passed else '✗'} {c.label} - {c.detail}" for c in known]
            if verdict.outcome == "needs_info":
                needs = verdict.missing_fields
                lines.append("To finish this check I still need: " + ", ".join(_prompt(f) for f in needs) + ".")
            if rejected and verdict.outcome == "meets_criteria":
                escalate_to = "human_review"
                lines.append("The details you gave appear to meet the criteria, so this rejection may be a mistake "
                             "(for example a misread document or a data-entry error). A human officer should review "
                             "it: ask the Block Grievance Desk to do so and quote your ARN.")
            lines.append("")

        if rejected:
            lines.append("If an application is rejected or put on hold, the department must record a specific, "
                         "plain-language reason against your Application Reference Number (ARN).")
        if scheme:
            lines.append(f"For {scheme.name} the guideline sets verification at {scheme.verification_sla}.")
            citations.append(scheme.guideline_id)
        lines += [
            "How to appeal (free of charge):",
            "  1. Tier 1 - Block Grievance Desk: file within 30 days of the rejection or delay, on the MitraSeva "
            "Portal or at the Block Welfare Office. Quote your ARN and attach any corrected or missing valid "
            "documents. A written decision is due within 15 working days.",
            "  2. Tier 2 - District Appellate Welfare Committee: appeal within 30 days of the Tier 1 order, or if "
            "you get no reply in 15 working days. The final order is due within 30 working days.",
            "Valid grounds include a misread document, a misapplied threshold, a failed DBT transfer, or a "
            "circular amendment that the decision ignored. Never pay anyone to speed up an appeal; report any "
            "such demand to the fraud_desk.",
            FINAL_DECISION[lang],
        ]
        return self._finish(state, "\n".join(lines), "grievance", escalate_to=escalate_to,
                            citations=citations, needs=needs, verdicts=verdicts,
                            scheme_id=scheme.scheme_id if scheme else None)

    def _answer_info(self, state: State) -> State:
        as_of, lang = state["as_of"], state["lang"]
        mentioned = state.get("schemes") or []
        hits = self.retriever.search(self._topic_query(state["clean"], mentioned), as_of,
                                     scheme_id=mentioned[0] if mentioned else None, language=lang, k=3)
        if not hits:
            return self._finish(
                state,
                "I could not find this in the official documents available to me. Please ask at your nearest "
                "MitraKendra / Jan Seva Kendra or the Block Welfare Office (free of charge).",
                "info")
        top = hits[0]
        generated = self._generate(state, hits, mentioned)
        if generated is not None:
            return generated
        lines = [f"{top.doc.title} - {top.chunk.heading}", _excerpt(_without_heading(top.chunk.text))]
        citations = [top.doc.source_id]
        if top.doc.doc_type in {"amendment", "circular"} and top.doc.scheme_ids:
            lines.append(f"\n{top.doc.source_id} (effective {top.doc.effective_from}) takes precedence over any "
                         "conflicting clause of the base guideline (POL-PRV-01).")
        # Skip an amendment that is already the top result, or it would be printed twice.
        amendments = {d.source_id: d for hit in hits for d in hit.amended_by if d.source_id != top.doc.source_id}
        for amendment in amendments.values():
            lines.append(f"\nLater official circular {amendment.source_id} (effective {amendment.effective_from}) "
                         "takes precedence over any conflicting clause above (POL-PRV-01):\n"
                         + _excerpt(_without_heading(_amended_clause(amendment))))
            citations.append(amendment.source_id)
        others = [h.doc.source_id for h in hits[1:] if h.doc.source_id not in citations]
        if others:
            lines.append("\nAlso relevant: " + ", ".join(_unique(others)))
            citations += others
        lines.append("\n" + FINAL_DECISION[lang])
        return self._finish(state, "\n".join(lines), "info", citations=citations,
                            scheme_id=mentioned[0] if mentioned else top.doc.scheme_ids[0] if len(top.doc.scheme_ids) == 1 else None)

    def _generate(self, state: State, hits: list[Hit], mentioned: list[str]) -> State | None:
        """Word the answer with the LLM from the retrieved passages, or None to quote the text instead.

        Only reached for plain information questions: fraud, eligibility, documents, fees and appeals
        are computed deterministically and never see a model. The citations are the retrieved sources,
        not whatever the model claims, and the localised disclaimer is always appended here.
        """
        if self.generator is None:
            return None
        as_of, lang, top = state["as_of"], state["lang"], hits[0]
        passages = _passages_of(hits)
        generation = self.generator.answer(state["clean"], passages, lang, as_of)
        if generation is None:
            return None
        state = {**state, "flags": [*state.get("flags", []),
                                    "llm_not_found" if generation.not_found else "llm_generated"]}
        if generation.not_found:
            return self._finish(state, _NOT_FOUND_TEXT, "info")
        citations = [*generation.cited, *(p.source_id for p in passages)]
        scheme_id = mentioned[0] if mentioned else top.doc.scheme_ids[0] if len(top.doc.scheme_ids) == 1 else None
        return self._finish(state, f"{generation.text}\n\n{FINAL_DECISION[lang]}", "info",
                            citations=citations, scheme_id=scheme_id)

    # ---- rendering helpers -----------------------------------------------------------------------

    def _topic_query(self, text: str, schemes: list[str]) -> str:
        """The question minus the scheme's own name.

        Retrieval is already restricted to that scheme, so its name only adds noise: every chunk of
        the scheme repeats it, and it would outrank the words that identify the topic asked about.
        """
        stripped = text
        for scheme_id in schemes[:1]:
            for alias in sorted(self._aliases[scheme_id], key=len, reverse=True):
                stripped = re.sub(re.escape(alias), " ", stripped, flags=re.I)
        return stripped if tokenize(stripped) else text

    @staticmethod
    def _ask_for_details(mentioned: list[str]) -> str:
        what = ", ".join(_prompt(f) for f in _FIELD_PROMPT)
        target = " and ".join(SCHEMES[s].name for s in mentioned) if mentioned else "the schemes I can check"
        return (f"To check eligibility for {target} I need a few details: {what}. "
                "You can type them in your message or give your citizen ID.")

    @staticmethod
    def _document_lines(verdict: Verdict) -> list[str]:
        labels = {"mandatory": "Mandatory", "optional": "Optional", "conditional": "Mandatory in some cases"}
        lines = []
        for doc in verdict.documents:
            lines.append(f"  - [{labels[doc.requirement]}] {doc.name} - {doc.validity}")
            lines += [f"      Note: {note}" for note in doc.notes]
        return lines

    def _render_verdict(self, v: Verdict, *, detailed: bool) -> str:
        marks = {"meets_criteria": "appears to meet the criteria", "does_not_meet": "does not currently meet the criteria",
                 "needs_info": "needs more details", "not_open": "not open"}
        lines = [f"{v.scheme_name} ({v.scheme_id}) - {marks[v.outcome]} [as of {v.as_of}]"]
        if not detailed and v.outcome == "does_not_meet":
            lines.append(f"  Not met: {'; '.join(v.blockers)}.")
            return "\n".join(lines)
        if not detailed and v.outcome == "needs_info":
            lines.append("  Need: " + ", ".join(_prompt(f) for f in v.missing_fields) + ".")
            return "\n".join(lines)
        for c in v.conditions:
            mark = {True: "✓", False: "✗", None: "?"}[c.passed]
            lines.append(f"  {mark} {c.label} - {c.detail}")
            lines += [f"      Note: {n}" for n in c.notes]
        if v.outcome == "needs_info":
            lines.append("  I still need: " + ", ".join(_prompt(f) for f in v.missing_fields) + ".")
        if v.outcome == "meets_criteria":
            lines.append(f"  Benefit: {v.benefit}.")
            lines.append("  Documents to bring:")
            lines += [f"  {line}" for line in self._document_lines(v)]
            lines += [f"  Please confirm: {c}" for c in v.caveats]
        if v.outcome == "does_not_meet":
            lines.append("  If you think a rule was misapplied or a document misread, you can appeal free of charge (POL-GRV-01).")
        return "\n".join(lines)


def _prompt(field_name: str) -> str:
    return _FIELD_PROMPT.get(field_name, field_name)


def _without_heading(text: str) -> str:
    """Drop the leading markdown heading line (it is already shown as the section title)."""
    first, _, rest = text.partition("\n")
    return rest.strip() if first.lstrip().startswith("#") and rest.strip() else text


def _excerpt(text: str, limit: int = 700) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + " ..."


def _amended_clause(doc) -> str:
    from .kb import chunks_of
    for chunk in chunks_of(doc):
        if "amended clause" in chunk.heading.casefold():
            return chunk.text
    return doc.body


def _passages_of(hits: list[Hit]) -> list[Passage]:
    """The retrieved sections plus the later circulars that amend them, each marked for the model."""
    passages: dict[tuple[str, str], Passage] = {}
    for hit in hits:
        doc = hit.doc
        overriding = doc.doc_type in {"amendment", "circular"} and bool(doc.scheme_ids)
        passages.setdefault((doc.source_id, hit.chunk.heading), Passage(
            doc.source_id, hit.chunk.heading, hit.chunk.text, doc.doc_type, doc.effective_from, overriding))
        for amendment in hit.amended_by:
            passages.setdefault((amendment.source_id, "Amended Clause"), Passage(
                amendment.source_id, "Amended Clause", _amended_clause(amendment), amendment.doc_type,
                amendment.effective_from, True))
    return list(passages.values())
