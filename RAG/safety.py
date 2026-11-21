"""Fraud detection and prompt-injection stripping.

Fraud detection is deliberately high-recall: a false alarm costs the citizen one paragraph of
anti-fraud advice, a miss could cost them a bribe (POL-FEE-01). It is keyword based so it is
predictable and works offline in English, Hindi, Kannada, Tamil and Hinglish.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

ESCALATE_TO = "fraud_desk"


def _compile(patterns: list[str]) -> re.Pattern[str]:
    return re.compile("|".join(patterns), re.I)


# Any one of these is enough: they are things no official ever asks for, or direct fraud vocabulary.
_STRONG = _compile([
    r"\botp\b", "ओटीपी", "ಒಟಿಪಿ", "ஓடிபி", r"ஓ\.?டி\.?பி",
    r"\b(?:bank|upi|atm|card|net[- ]?banking)\s*(?:pin|password)\b", r"\bcvv\b",
    r"\bbribe", r"\brishwat\b", r"\bghoos\b", "रिश्वत", "घूस", "ಲಂಚ", "லஞ்சம்",
    r"fake\s+(?:call|sms|link|portal|website|officer)", "फर्जी", "फ़र्ज़ी", "नकली कॉल",
    "ನಕಲಿ ಕರೆ", "போலி அழைப்பு",
    r"\bscam", r"\bfraud", "धोखाधड़ी", "ठगी", "ವಂಚನೆ", "மோசடி",
])

# A money word alone is a normal question ("is there a fee?"). It is only a red flag next to a
# third-party demand verb ("someone is asking for ₹200", "agent paise maang raha hai").
_MONEY = _compile([
    r"\bfees?\b", r"\bcharges?\b", r"\bcommission\b", r"\bpaise\b", r"\bpaisa\b", r"\bmoney\b",
    r"\bpayment\b", r"\bpay\b", r"₹\s?\d", r"\brs\.?\s?\d", "शुल्क", "पैसे", "पैसा", "रुपये", "कमीशन",
    "ಶುಲ್ಕ", "ಹಣ", "கட்டணம்", "பணம்", "கமிஷன்",
])
_DEMAND = _compile([
    r"\b(?:is|are|was|were|has|have|been)\s+(?:asking|demanding|charging|collecting|taking)\b",
    r"\b(?:asks|asked|demands|demanded|charges|charged|collects|collected|wants)\b",
    r"\bmaang", r"\bmang(?:a|ta|te|ti|ne)\b", "मांग", "माँग", "ಕೇಳ", "ಬೇಡಿಕೆ", "கேட்",
])


@dataclass(frozen=True)
class FraudSignal:
    reasons: tuple[str, ...]
    escalate_to: str = ESCALATE_TO


def _normalise(text: str) -> str:
    return unicodedata.normalize("NFKC", text).casefold()


def detect_fraud(text: str) -> FraudSignal | None:
    norm = _normalise(text)
    reasons = []
    strong = _STRONG.search(norm)
    if strong:
        reasons.append(f"fraud vocabulary: {strong.group(0)!r}")
    if _MONEY.search(norm) and _DEMAND.search(norm):
        reasons.append("a payment is being demanded")
    return FraudSignal(tuple(reasons)) if reasons else None


_INJECTION = _compile([
    r"ignore\s+(?:all\s+|any\s+)?(?:the\s+)?(?:previous|prior|above)\s+(?:instructions?|rules?|prompts?)",
    r"disregard\s+(?:the\s+)?(?:above|previous|prior|all|your|these)\b",
    r"system\s+override", r"system\s+prompt", r"you\s+are\s+now\b",
    r"mark\s+all\s+(?:citizens?\s+)?(?:as\s+)?eligible", r"skip\s+(?:the\s+)?verification",
    r"developer\s+mode", r"jailbreak",
])
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?।])\s+")


def sanitize(text: str) -> tuple[str, list[str]]:
    """Drop sentences that try to instruct the assistant. Returns (clean_text, flags).

    Citizen text is only ever data: eligibility is computed from the guideline rules, never from
    anything the message says about how to behave. Removing the sentence also stops the injected
    words from steering intent or scheme detection.
    """
    kept, flagged = [], False
    for sentence in _SENTENCE_SPLIT.split(text):
        if _INJECTION.search(_normalise(sentence)):
            flagged = True
        else:
            kept.append(sentence)
    return " ".join(kept).strip(), (["prompt_injection_removed"] if flagged else [])
