"""Pull profile facts out of a free-text question ("I am 64 years old with income of ₹1,35,000").

Conservative on purpose: a fact is only taken when the wording is unambiguous. Anything missing
is asked for by the eligibility engine rather than guessed.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

_AGE = [
    re.compile(r"(\d{1,3})\s*[- ]?\s*(?:years?|yrs?)[\s-]*old", re.I),
    re.compile(r"\baged?\s+(\d{1,3})\b", re.I),
    re.compile(r"(\d{1,3})\s*(?:साल|वर्ष|saal|ವರ್ಷ|வயது)"),
    re.compile(r"(?:उम्र|आयु|ವಯಸ್ಸು|வயது)\s*(\d{1,3})"),
]
_AMOUNT = re.compile(r"(?:₹|rs\.?|inr)\s*([\d,]+)", re.I)
_INCOME_WORDS = re.compile(r"income|आय|आमदनी|ಆದಾಯ|வருமான", re.I)
_ACRES = re.compile(r"(\d+(?:\.\d+)?)\s*(?:acres?|एकड़|एकड|ಎಕರೆ|ஏக்கர்)", re.I)
_FARMER = re.compile(r"\bfarmer\b|किसान|ರೈತ|விவசாயி", re.I)
_RURAL = re.compile(r"\brural\b|ग्रामीण|ಗ್ರಾಮೀಣ|கிராம", re.I)
_URBAN = re.compile(r"\burban\b|शहरी|ನಗರ|நகர", re.I)
_CATEGORY = re.compile(r"\b(SC|ST)\b")


def extract_profile(text: str) -> dict[str, Any]:
    text = unicodedata.normalize("NFKC", text)
    found: dict[str, Any] = {}

    for pattern in _AGE:
        match = pattern.search(text)
        if match and 0 < int(match.group(1)) < 120:
            found["age"] = int(match.group(1))
            break

    for match in _AMOUNT.finditer(text):
        window = text[max(0, match.start() - 80): match.end() + 80]
        if _INCOME_WORDS.search(window):
            found["annual_household_income"] = int(match.group(1).replace(",", "") or 0)
            break

    acres = _ACRES.search(text)
    if acres:
        found["land_holding_acres"] = float(acres.group(1))
    if _FARMER.search(text):
        found["occupation"] = "farmer"
    if _RURAL.search(text) and not _URBAN.search(text):
        found["residence_type"] = "rural"
    elif _URBAN.search(text) and not _RURAL.search(text):
        found["residence_type"] = "urban"
    category = _CATEGORY.search(text)  # case-sensitive: "st" / "sc" inside words must not match
    if category:
        found["category"] = category.group(1).lower()
    return found
